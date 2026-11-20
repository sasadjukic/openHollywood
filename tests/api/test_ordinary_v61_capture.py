"""Single-use dispatch regressions with independent processes and a local fake endpoint."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts import ordinary_v61_capture as capture

APPROVAL = "a" * 64
BODY = b'{"model":"fixture"}'


def test_only_one_process_claim_and_no_ledger_reissue(tmp_path: Path) -> None:
    capture.initialize_ledger(tmp_path, APPROVAL)

    def claim() -> str:
        try:
            return capture.ledger_state(tmp_path, APPROVAL, ("ready", "claimed"))
        except EvidenceError:
            return "refused"

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sorted(pool.map(lambda _: claim(), range(4))) == ["claimed", *["refused"] * 3]
    with pytest.raises(FileExistsError):
        capture.initialize_ledger(tmp_path, APPROVAL)
    with pytest.raises(EvidenceError):
        capture.ledger_state(tmp_path, APPROVAL, ("claimed", "ready"))


async def _child(root: Path, drift: str) -> None:
    capture.WIRE_SHA = hashlib.sha256(BODY).hexdigest()

    def receive(request: httpx.Request) -> httpx.Response:
        assert capture.ledger_state(root, APPROVAL) == "dispatched"
        with (root / "received").open("ab") as stream:
            stream.write(b"POST\n")
            stream.flush()
            os.fsync(stream.fileno())
        os._exit(86)  # Abrupt death after receipt, before any response or finally block.

    capture.ledger_state(root, APPROVAL, ("ready", "claimed"))
    gate = capture.SinglePost(root, APPROVAL, httpx.MockTransport(receive))
    async with httpx.AsyncClient(transport=gate) as client:
        url = capture.URL + ("/wrong" if drift == "endpoint" else "")
        await client.post(url, content=b"different" if drift == "body" else BODY)


def _process(root: Path, drift: str) -> int:
    return subprocess.run(
        [sys.executable, "-m", "tests.api.test_ordinary_v61_capture", str(root), drift],
        cwd=capture.REPO,
        capture_output=True,
        timeout=45,
        check=False,
    ).returncode


def test_interruption_after_post_refuses_new_process(tmp_path: Path) -> None:
    capture.initialize_ledger(tmp_path, APPROVAL)
    assert _process(tmp_path, "none") == 86
    assert capture.ledger_state(tmp_path, APPROVAL) == "dispatched"
    assert _process(tmp_path, "none") == 21
    assert (tmp_path / "received").read_bytes() == b"POST\n"


@pytest.mark.parametrize("drift", ["body", "endpoint"])
def test_drift_refused_before_dispatch(tmp_path: Path, drift: str) -> None:
    capture.initialize_ledger(tmp_path, APPROVAL)
    assert _process(tmp_path, drift) == 21
    assert capture.ledger_state(tmp_path, APPROVAL) == "claimed"
    assert not (tmp_path / "received").exists()


def test_unknown_usage_and_error_chain_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(capture, "WIRE_SHA", hashlib.sha256(BODY).hexdigest())
    capture.initialize_ledger(tmp_path, APPROVAL)
    capture.ledger_state(tmp_path, APPROVAL, ("ready", "claimed"))
    (tmp_path / "output").mkdir()
    payload = {"error": "daemon returned upstream HTTP 500"}

    async def check() -> None:
        inner = httpx.MockTransport(lambda _: httpx.Response(500, json=payload))
        async with httpx.AsyncClient(
            transport=capture.SinglePost(tmp_path, APPROVAL, inner)
        ) as client:
            assert (await client.post(capture.URL, content=BODY)).status_code == 500
            with pytest.raises(EvidenceError):
                await client.post(capture.URL, content=BODY)

    asyncio.run(check())
    receipt = json.loads((tmp_path / "output/http.json").read_bytes())
    assert receipt["response"] == payload
    assert receipt["input_tokens"] is receipt["output_tokens"] is None


if __name__ == "__main__":
    try:
        asyncio.run(_child(Path(sys.argv[1]), sys.argv[2]))
    except EvidenceError:
        raise SystemExit(21) from None

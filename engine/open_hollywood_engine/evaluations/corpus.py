"""Frozen benchmark-corpus loading and integrity checks."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from open_hollywood_engine.evaluations.contracts import BenchmarkCorpus

V01_CORPUS_ID = "open-hollywood-short-prose-v0.1"
V01_PROMPT_COUNT = 12


class BenchmarkCorpusError(ValueError):
    """Raised when a corpus file is unreadable, malformed, or incomplete."""


def load_benchmark_corpus(path: Path) -> BenchmarkCorpus:
    """Read and strictly validate one UTF-8 benchmark corpus."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:
        raise BenchmarkCorpusError(f"benchmark corpus could not be read: {path}") from error
    try:
        corpus = BenchmarkCorpus.model_validate_json(raw)
    except ValidationError as error:
        raise BenchmarkCorpusError("benchmark corpus failed schema validation") from error
    if corpus.corpus_id == V01_CORPUS_ID and len(corpus.prompts) != V01_PROMPT_COUNT:
        raise BenchmarkCorpusError(f"{V01_CORPUS_ID} requires exactly {V01_PROMPT_COUNT} prompts")
    return corpus

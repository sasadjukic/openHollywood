"""Strict structured-output normalization tests."""

from __future__ import annotations

import pytest
from open_hollywood_api.services.structured_output import normalize_json_document


def test_plain_json_is_preserved_after_outer_whitespace() -> None:
    assert normalize_json_document(' \n{"value": 1}\n ') == '{"value": 1}'


def test_single_json_fence_is_normalized() -> None:
    assert normalize_json_document('```json\n{"value": 1}\n```') == '{"value": 1}'


@pytest.mark.parametrize(
    "content",
    (
        'Commentary\n```json\n{"value": 1}\n```',
        '```python\n{"value": 1}\n```',
        '```json\n{"value": 1}',
        "```json\n\n```",
    ),
)
def test_commentary_or_malformed_fences_are_rejected(content: str) -> None:
    with pytest.raises(ValueError):
        normalize_json_document(content)

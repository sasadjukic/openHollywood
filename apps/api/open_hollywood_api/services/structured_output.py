"""Strict normalization for provider-returned structured JSON."""

from __future__ import annotations


def normalize_json_document(content: str) -> str:
    """Remove only one provenance-free JSON fence and reject mixed commentary."""
    stripped = content.strip()
    if not stripped.startswith("```"):
        if "```" in stripped:
            raise ValueError("structured output mixes commentary and Markdown fencing")
        return stripped
    lines = stripped.splitlines()
    if len(lines) < 3 or lines[0].casefold() not in {"```", "```json"}:
        raise ValueError("structured output has an unsupported Markdown fence")
    if lines[-1].strip() != "```":
        raise ValueError("structured output has an unterminated Markdown fence")
    document = "\n".join(lines[1:-1]).strip()
    if not document:
        raise ValueError("structured output fence is empty")
    return document

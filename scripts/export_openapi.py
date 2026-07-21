"""Export the canonical OpenAPI document used for TypeScript code generation."""

import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = WORKSPACE_ROOT / "packages" / "contracts" / "openapi.json"
sys.path.insert(0, str(WORKSPACE_ROOT / "apps" / "api"))

from open_hollywood_api.app import app  # noqa: E402


def main() -> None:
    """Write a deterministic OpenAPI document from the application schema."""
    output = json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"
    OUTPUT_PATH.write_text(output, encoding="utf-8", newline="\n")
    print(f"Exported OpenAPI schema to {OUTPUT_PATH.relative_to(WORKSPACE_ROOT)}")


if __name__ == "__main__":
    main()

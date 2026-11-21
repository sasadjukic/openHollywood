"""Verify or spend the single registered ordinary critic attempt for The Impossible Card."""

from scripts import ordinary_v61_capture as capture

ROOT = capture.REPO / "data/diagnostics/second-family-v61-capture-2026-11-21"
WIRE_SHA = "03249a0141224241dadaf5998df2d09da75fa177097cff9c05a9edda233afb01"
MESSAGE_SHA = "4c0c951627a82067d907985a5d4f0529c30632f678593d5301896823f9556030"

if __name__ == "__main__":
    # Apply the three case-specific pins only in this CLI's dedicated process.
    # Both registrations use the same source campaign, parser and single-use transport.
    capture.ROOT = ROOT
    capture.WIRE_SHA = WIRE_SHA
    capture.MESSAGE_SHA = MESSAGE_SHA
    raise SystemExit(capture.main())

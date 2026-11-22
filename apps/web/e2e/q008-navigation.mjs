import { verifyNavigation } from "./saved-assessment-navigation.mjs";

await verifyNavigation(
  {
    claimId: "Q008",
    directory: "../../data/diagnostics/q008-browser-2026-11-21",
    usage: {
      input_tokens: 58894,
      output_tokens: 345,
      reasoning_tokens: 165,
      cached_input_tokens: 0,
    },
    phase: "complete",
  },
  ...process.argv.slice(2),
);

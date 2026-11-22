import assert from "node:assert/strict";
import { verifyNavigation } from "./saved-assessment-navigation.mjs";

const [phase, registered, copy, scratch] = process.argv.slice(2);
assert.ok(["archive", "damage"].includes(phase));
await verifyNavigation(
  {
    claimId: "Q013",
    directory: "../../data/diagnostics/q013-browser-2026-11-22",
    usage: {
      input_tokens: 62835,
      output_tokens: 427,
      reasoning_tokens: 255,
      cached_input_tokens: 0,
    },
    phase,
  },
  registered,
  copy,
  scratch,
);

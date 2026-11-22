# Tracked read-only lookup for Q008 and Q013

Operators can open the saved Q008 and Q013 assessments together with `python -m scripts.lookup_saved_review_completion`. Pass one `--selection` file per lookup. The output preserves the requested order and repetitions. In the two private archives, eight interleaved selections refer to two assessments and two generation usage records. [Command example](../../README.md#saved-review-lookup) · [Shared lookup](../../scripts/lookup_saved_review_completion.py)

| Available deliveries in the inventory | Usage records | Generation input | Generation output | Reasoning included in output |
| --- | ---: | ---: | ---: | ---: |
| Q008 and Q013 | 2 | 121,729 | 772 | 420 |
| Q008 only | 1 | 58,894 | 345 | 165 |
| Q013 only | 1 | 62,835 | 427 | 255 |
| Neither | 0 | Unknown | Unknown | Unknown |

The JSON contract is `saved-review-consumer-lookup-1`. With both deliveries available, the assessment and accounting lists return Q008 followed by Q013 in either selection order. Each available row references an assessment by delivery ID and claim ID. Generation accounting uses the delivery ID and attributes the request to its original critique. Input-count measurements remain on their individual records. The generation totals include each delivery once. The operator score retains its three Q008 judgments or its separate Q013 claim-correctness and evidence-coverage judgments. [Q008 publication](q008-observed-publication-2026-11-21.md) · [Q013 publication](q013-observed-publication-2026-11-22.md)

## What happens on refresh

The lookup uses fixed digests of the complete selectors to find the requested registrations even when a publication is missing. The five selector fields are project, role, artifact ID, version ID and content digest. On every lookup, the consumer reads each matching publication once, verifies its pinned manifest, asks the publisher to reauthenticate the observed delivery, and checks the complete member set and member bytes. It returns a result only for a selection listed in the authenticated manifest.

Adjacent Q013 versions get an unavailable row with empty claim and delivery references. If another exact Q013 selection is present, its assessment and usage stay in the inventory. If the last exact Q013 selection is replaced, only Q008 contributes. Damage to Q013 with both exact selections open clears all Q013 rows' references and drops its score and usage. The next lookup after restoration reauthenticates Q013 and recovers the original records. [Local rehearsal](q008-q013-consumer-rehearsal-2026-11-22.md)

## Q008 compatibility

The existing `python -m scripts.lookup_q008_completion` command continues to return `q008-consumer-lookup-1`. It accepts the same selection files and retains its Q008-only score projection, failure reasons and accounting. The artifact inspector continues to use this command's lookup function. [Q008 command](../../README.md#q008-lookup)

The previous and current Q008 entry points produced identical output and exit status in four comparisons covering mixed exact selections, Q013-only input, a missing Q008 publication and malformed selector JSON. Separate process invocations checked both commands on the same mixed batch and the shared command on malformed input.

## Local verification

Nine portable regressions exercise both command lines, reversed and repeated mixed selections, same-text adjacent versions for both Q013 roles, and refresh followed by recovery. The six fault cases cover altered usage, altered score, a recomputed member hash under a changed manifest, missing closure, an absent directory and an upstream source that fails reauthentication. The tests compare the surviving Q008 assessment and usage record with their healthy values and check that reads preserve the damaged directory as found. [Regression tests](../../tests/api/test_saved_review_lookup.py)

The private archive verifier runs the original 29-scenario rehearsal against the tracked lookup. It compares the resulting inventories with the retained evidence and exercises the commands as an operator would invoke them. With the saved archives present, run these checks from the project root.

```powershell
.venv/Scripts/python.exe -m pytest -q tests/api/test_saved_review_lookup.py tests/api/test_q008_consumer_lookup.py
.venv/Scripts/python.exe data/diagnostics/q008-q013-tracked-lookup-2026-11-22/verify.py
```

All 29 scenarios passed. After accounting for the new contract name, the saved mixed, adjacent and damaged inventories and the scenario verification record matched the rehearsal byte for byte. All 86 original files checked retained their hashes and modification times. A separate reverse control withdrew Q008 and recovered Q013 alone with 62,835 input and 427 output tokens. With both directories absent, the lookup returned empty records and null totals and created neither directory.

Private evidence is in `data/diagnostics/q008-q013-tracked-lookup-2026-11-22/`. Open `mixed-inventory.json` and `legacy-mixed-inventory.json` for the two commands' outputs on the same eight selections, `verification.json` for the archive and compatibility checks, and `reverse-isolation.json` for the missing-directory control.

All 2,671 distinct Python tests passed with zero skips. Ruff lint, formatting and strict mypy passed across 353 Python files. Frontend formatting, lint, type checks, all 44 web tests and both production builds passed. Verification used zero provider calls. Step 19 remains in progress and the full workflow canary stays on hold.

## Next step

Qualify a read-only Q013 adapter for the API and artifact inspector in its exact registered workspace. Use critique v3 and draft v1 as the positive controls. Exercise a copied workspace with identical IDs, an adjacent version, a selection switch during an outstanding request, and a refresh after damaging a previously valid publication. Verify that the inspector clears stale assessment and usage and exposes only the intended display fields. Replay Q008 alongside these controls before enabling Q013 in artifact navigation.

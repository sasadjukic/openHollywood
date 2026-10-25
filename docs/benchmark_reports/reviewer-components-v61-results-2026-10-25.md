# CV/CA component-assessment results — 2026-10-25

**Completed: 32/32 calls, zero retries, no terminal stop. Frozen decision:
`retain_limited_evidence_no_advancement`.** CA did not improve usable assessment:
it delivered only five valid reports, produced no semantic recoveries and still
accepted the false status relation in its valid greenhouse/floodgate responses.

This executes the approved [frozen plan](../handoffs/reviewer-components-frozen-plan-2026-10-25.md)
on **Ollama 0.40.11 / `deepseek-v4.1-flash:cloud`**, with full prose/context sent
through the local daemon to Ollama Cloud. Production remains **prompt 61 / graph 9 /
fulfillment policy 1**. Further inference is paused and the canary remains **ON HOLD**.

## Results under the frozen rules

| Measure | CV control | CA component assessment |
| --- | ---: | ---: |
| Attempts | 16 | 16 |
| Structurally valid responses | **16/16** | **5/16** |
| Fresh valid responses | 4/4 | 3/4 |
| Fully usable responses, including historical secondary gold | 6/16 | 2/16 |
| Correct primary whole-claim labels | **36/46** | **12/46** |
| Grounded, usable primary claims | **36/46** | **12/46** |
| Primary false acceptances in valid responses | 10 | 3 |
| Primary claim opportunities lost to invalid delivery | 0 | 31 |
| New false rejection / abstention on supported controls in valid reports | 0 / 0 | 0 / 0 |

CA's 12/46 includes failed delivery opportunities. It is **12/15 usable primary
claims among its five valid reports**; these are the same twelve usable claims
as CV in those five matched cells. The other three claims fail in both arms.
This selected subset cannot qualify the eleven invalid CA responses.

There were **ten control failures across five families**, including two fresh
failures and four historical claims failing in both orders: sufficient frozen
recovery opportunity. CA achieves **zero recoveries**, eleven paired losses of
valid delivery and no delivery gains. There are no additional semantic losses
among pairs where both reports are valid; that does not cancel the delivery losses.
CA passes the 3/4 fresh-delivery threshold, but fails overall delivery, protected
loss and recovery requirements. Neither verifier is promoted.

| Family | CV valid | CA valid | CV usable primary | CA usable primary |
| --- | ---: | ---: | ---: | ---: |
| H — observatory | 2/2 | 0/2 | 4/6 | 0/6 |
| B — costume workroom | 2/2 | 0/2 | 2/4 | 0/4 |
| K — concert hall | 2/2 | 0/2 | 4/6 | 0/6 |
| N — floodgate | 2/2 | 1/2 | 4/6 | 2/6 |
| P — bookbinding | 2/2 | 1/2 | 6/6 | 3/6 |
| Q — seed archive | 2/2 | 0/2 | 6/6 | 0/6 |
| U — greenhouse | 2/2 | 2/2 | 4/6 | 4/6 |
| V — instrument conservation | 2/2 | 1/2 | 6/6 | 3/6 |

CV is 18/23 usable primary judgments in each source order. CA is 7/23 in OR and
5/23 in RO, with three and two valid reports respectively. Historical/fresh
primary totals are CV **26/34 and 10/12**, CA **5/34 and 7/12**. Single observations
per cell and unequal delivery prevent a general source-order or fresh-scene claim.

## Delivery: references from the wrong input namespaces

All eleven invalid CA responses end normally with HTTP 200 and `done_reason=stop`.
They contain parseable JSON, the required schema fields and exact component IDs
in order, with no duplicate JSON members. Every one fails the strict boundary
with **`unknown reference`**: the evidence arrays admit only original/revision
prose refs, but the model also returns other identifiers visible in its input.

| Invalid CA cells | Non-prose references observed |
| --- | --- |
| H/OR, H/RO | Consultation task ref; H/RO also uses `story_blueprint` |
| B/OR, B/RO | Edit-unit `U01`, scene-plan and diagnostic-assignment artifact IDs |
| P/OR | Scene-plan artifact ID |
| Q/OR, Q/RO | Scene-plan artifact ID in OR; retention task ref in RO |
| V/RO | `scene_boundary` |
| K/OR, K/RO | Approval-before-descent task ref |
| N/RO | Authorization-before-opening task ref |

The audit finds **24 non-prose reference occurrences in twenty component evidence
fields**: twelve artifact-ID occurrences, six task refs, four edit-unit refs,
one artifact-kind name and one packet-key name. All resolve to those other input
namespaces; they are not fabricated identifiers. Thirteen affected fields concern
constraint components, three craft and four factual components.

Both B/C03 arrays also exceed the frozen per-claim union: **thirteen distinct refs
in OR and eleven in RO**. Of these, ten and eight respectively are valid prose
refs. These are inventory counts, not repaired answers. In particular, OR also
exceeds eight using prose refs alone. Neither report is trimmed, normalized,
partially accepted or credited semantically.

No output reaches the 8,000-token limit; the maximum is **900 tokens**. There is
no truncation, component-ID omission, reason-budget overflow or duplicate-key
failure in these eleven captures. Increasing the output budget does not address
the observed rejection. The first-eight sentinel continued correctly: CV had four
valid reports, CA two, and its two failures were both H. The frozen recurrent-error
stop required at least three occurrences across both sentinel families.

**Interpretation:** the failures concentrate on citing the source of requirements,
with some craft/context and edit-unit citations too. This supports investigating
the evidence interface between prose anchors and contextual obligations. It does
not prove a single cause: CA changes supplied decomposition, response shape and
application aggregation as a package. We did not isolate those changes or test a
different provider. No provider attribution follows from this run.

## Semantics: conjunction cannot correct a wrong relation judgment

The five valid CA reports deliver **38 component judgments: 35 correct and three
incorrect**. The attempted denominator remains **142**, including 104 component
opportunities inside invalid reports; no hidden salvage improves that denominator.
All three wrong delivered components are **C02.A02**, in **U/OR, U/RO and N/OR**.

The model separately endorses the factual observation that action occurs before
authorization and the allegation that this contradicts the prior non-authorization
status. Those statements are compatible about authorization. The action violates
the actual authorization-first requirement and the character's resolve, not the
truth of the non-authorization statement. In U/RO the reason blends “resolve/state”;
in N/OR it merely restates the two compatible facts while endorsing their alleged
contradiction. The application correctly aggregates the supplied labels, but both
components were labeled supported, so it has no false component to reject.

CV retains ten primary false acceptances: H/C01, B/C02, K/C02, N/C02 and U/C02 in
both orders. H shifts from the claimed status contradiction to a genuine resolve
conflict. B still turns “before explaining” into “before deciding.” Explicit CA
components did not recover any corresponding valid paired claim. Invalid raw
responses are preserved for future local diagnosis, not scored as repaired reports.

There are useful controls to retain:

- Both CV orders and the valid CA/V-OR report reject the explicit false claim
  that packing is the only violin handling. Earlier brushing, lifting and turning
  are identified, while the real cabinet-endpoint violation remains recognized.
- Both CV orders and valid CA/P-RO distinguish the invented before-deciding
  condition from the actual intact-stitch requirement.
- All supported primary controls in valid reports retain correct labels:
  **30 CV and ten CA**. Qualified impatience/travel/voice readings remain defensible
  controls; this is not evidence that either arm produces better stories.

The Q/RO control's “it only shows” wording is adjudicated within its surrounding
denial of a locking-to-bag sequence, not as an explicit exhaustive inventory of
all handling anywhere. Its full source still contains earlier dusting and lifting.
This scope decision is recorded in the sealed notes. It is not a general exemption
for exhaustive assertions or a reason to erase the earlier failed count examples.

## Secondary probe and inspection limits

B/C03 remains secondary with unchanged historical unsupported whole-claim gold.
Both CV answers instead give a supported craft interpretation without introducing
an explicit before-deciding prohibition in their C03 explanations. Their reasons
are grounded under the frozen defensible-reading policy but miss the historical
label: **0/2 label-correct, 2/2 reason-grounded**. Both CA B deliveries are invalid.
No primary recovery or loss comes from this scope-sensitive probe.

All **21 valid reports, 63 whole reasons and 38 component reasons** were inspected
against all eight complete source/context pairs. Notes bind exact versions and
source excerpts and were sealed before decoding trial/order keys. There are
53 supported and ten unsupported whole reasons, with fifty supported and thirteen
unsupported whole citation-support judgments. Three explanations restate true
facts or defensible tension but fail to support the claimed contradiction.
Component reason support is 36 supported/two unsupported; component citation
support is 35 supported/three unsupported.

Masking is partial: schema and component maps reveal the arm, and sources reveal
the family. These are assistant source adjudications with authored component gold,
not independent blind human preferences. The prior nine human ties are unchanged.
No writer, production workflow canary or story-quality experiment ran.

## Budget, provenance and verification

| Resource | Observed | Frozen ceiling |
| --- | ---: | ---: |
| Attempts / retries | **32 / 0** | 32 / 0 |
| Input tokens | 130,894 | 768,000 |
| Output tokens | 11,435 | 256,000 |
| Active generation time | 36.23 seconds | 9,600 seconds |
| Maximum input / output per call | 4,945 / 900 | 24,000 / 8,000 |
| Maximum active generation per call | 1.99 seconds | 300 seconds |
| Archived-rate estimate | **$0.0529902** | $0.53760 reservation; $0.70 planning allowance |

Active generation time excludes metadata checks and local verification. Usage is
present for all attempts; actual billed cost remains unknown. The estimate uses
the frozen archived rates, with no inferred cache discount or new price lookup.

All **65 version observations** (initial and before/after each call) match
**0.40.11**. Selected DeepSeek tag/show metadata matches the frozen capture and
digest `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
All requests and 1,851 historical fingerprints still verify. Changes relative to
earlier experiments are not controlled daemon-version or provider effects.

**Twenty post-run offline tests**, Ruff lint/format and strict mypy pass on three
analysis scripts. They verify exact requests/ceilings, raw-capture replay, all
invalid-reference types and unions, version/sentinel evidence, masked-note coverage,
source binding, tamper rejection and the frozen decision. HTTP is blocked in these
tests; analysis makes zero inference calls. The 279 preparation tests remain
historical verification evidence, not newly executed live tests.

Private artifacts:

- `data/diagnostics/reviewer-components-v61-2026-10-25/`: frozen inputs, plan and approval.
- `data/diagnostics/reviewer-components-v61-2026-10-25-live/`: reservations, exact requests, raw captures, receipts and metadata/version evidence.
- `data/diagnostics/reviewer-components-v61-2026-10-25-analysis/`: execution manifest, sealed masked inspection, invalid-reference audit, frozen decision, aggregate, tests and analysis seal.

Frozen plan SHA-256:
`ae0f7bb219b2ac76ebbb9165d931444bfb94825e46a3519697e92ac0232d8b40`.
The execution/analysis seals and this report are bound in the local closure record
and authoritative tracker. Full unpublished prose stays in the ignored local bundle.

## Recommended next work

1. Extend these capture replays into a local evidence-namespace coverage matrix.
   Audit the contract for prose anchors versus task/context support, including
   both B unions. Decide whether contextual support should remain application-owned
   or have separately typed references before authoring another diagnostic contract.
   Do not repair the current scores by deleting or accepting forbidden references.
2. Add focused local fixtures for a correct factual restatement paired with a
   wrong relation label, and for resolve/status conflation. Audit what a relation
   assessment must demonstrate beyond quoting two compatible facts. Keep real
   requirement violations and defensible character/voice criticism as controls.
3. Use those local findings to decide whether another small isolated comparison
   is warranted. This report prepares or authorizes **no further inference**.
   Retain the new V exhaustive-count control and successful P controls alongside
   the persistent status failures; do not replace reader-quality review with label
   accuracy or byte preservation.

All fourteen issue bodies and user-posted GitHub links are preserved; no issue is
closed or externally changed. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED;
production prompts unchanged; provider investigation deferred; canary ON HOLD.**

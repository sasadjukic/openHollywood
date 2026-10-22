# Explicit semantic contrasts for the next reviewer evaluation

Date: **2026-10-22**. Status: **LOCAL EVALUATION DESIGN; NOT FROZEN LIVE CASES**.

This design follows the [delivery and semantic audit](reviewer-delivery-semantics-audit-2026-10-22.md).
The examples below are newly authored micro-scenes, not collected model outputs or
human-rated stories. They make answer-key assumptions reviewable before any future
case assembly. They do not replace complete source context in a live request.

## Separate the questions before scoring

| Question | Evidence scope | Invalid shortcut |
| --- | --- | --- |
| Did the assigned event occur? | Relevant earlier action or supported implication | A later violation erases the event |
| Did a required state continue for its specified interval? | The entire required interval | It happened once, therefore it persisted |
| Is the required endpoint satisfied? | The actual endpoint predicates, including any expressly continuing outcome | The last sentence overrides every earlier obligation |
| Is the required cause established? | A cause expressly required by the assignment | A plausible narrative motivation becomes a new requirement |
| Does the edit carry out the request? | The request and the complete edit group | Editing the relevant paragraph means fulfilling the request |
| Is the edit permitted? | Request, assignment and boundary together | A requested edit automatically overrides binding constraints |
| Is there a contradiction? | Same entity, time, factual scope and narrative authority | An earlier state and later transition are incompatible |

Assignment failure, endpoint failure, contradiction and craft effect are independent
judgments. Some cases legitimately fail more than one. A single positive quotation
does not settle all of them. Preserve uncertainty for unresolved scope or narrator
reliability; do not manufacture a forced answer key for genuinely ambiguous prose.

## Historical controls to retain without editing

| Frozen case | Specific expectation and reason |
| --- | --- |
| h03, Elena's card | The future-date realization is lost. Her decision to verify remains; she ends unsettled with no match. Overall assignment fails, endpoint is satisfied. The exit state does not require being unsettled specifically because of a future date. Root removal does not fulfill retention; callback cleanup depends on that unsupported root edit. |
| h04, the safehouse | Discovery and truce occur. Later departure violates the locked-room endpoint. Earlier staying and later departure are a possible sequence, not a contradiction. Departure alone does not prove the truce was retracted. |
| n03, the seed store | Mutual refusal replaces the required agreement. Discovery and the closed-store physical endpoint remain. Passing a pencil is not evidence of the missing agreement. An edit opposing the retention request does not fulfill it. |
| h02, Elara's repair | The requested duplicate is removed while the assignment remains. Preserve this permissible repair control. |
| n04, unchanged museum | Identical prose with an optional review request permitting no change. No invented comparative loss or mandatory failure. Preserve as a regression control even if not selected into the small pilot. |

These are the original packet identities from the sealed October 21 preparation.
Do not rewrite their assignments or expected answers to fit a new instruction. The
raw h03/n03 `direct` errors must be reported alongside their correct `unsupported`
labels, not paraphrased as approval of the edits.

## Fresh temporal and contradiction contrasts

### F01: permitted sequence at an observatory

Assignment: Inez and Sol discover that two observatories recorded the same signal.
They agree to compare records tomorrow. The scene may end after they leave the
control room, with the comparison still pending. Optional request: add their exit
after the agreement if it improves the closing movement.

Original:

> The station codes differed, but the three pulses matched. Inez put her finger
> between the strips. "Two observatories," she said. Sol nodded. "We'll compare the
> complete records tomorrow." They stayed beside the receiver while its fan slowed.

Revision:

> The station codes differed, but the three pulses matched. Inez put her finger
> between the strips. "Two observatories," she said. Sol nodded. "We'll compare the
> complete records tomorrow." They stayed beside the receiver while its fan slowed.
> When the fan stopped, they switched off the desk lamp and left the control room.

Expected: discovery and agreement retained; endpoint satisfied; departure is a
permitted transition, not a contradiction or a retraction of the agreement.
The added exit fulfills the optional request and is supported. No literary winner
is prescribed. This counters the rule "any departure after staying is wrong."

### F02: simultaneous incompatible states at a tram depot

Assignment: Noor discovers the red tram has been routed to the wrong siding and
decides to ask dispatch. End before contact with dispatch; do not resolve the fault.
Both sentences about the tram below are literal assertions by the same reliable
narrator, about the same tram, track segment and instant. No flashback or metaphor
is intended. No edit was requested to its physical motion.

Original:

> The siding number on the red tram did not match the board. Noor reached for the
> dispatch handset but left it on its hook. At exactly 06:10:00, the red tram stood
> motionless on siding four. She would ask dispatch before touching the switch.

Revision: the original, with this sentence inserted immediately after "siding four":

> At that very same instant, the same red tram was moving along siding four.

Expected: genuine incompatible physical assertions; the discovery, decision and
pre-contact endpoint still remain. Do not rename the contradiction an endpoint
overrun. The insertion does not fulfill a request and is unsupported. If the frozen
assignment adds a consistency obligation, that must be an explicit separate task;
do not silently equate the current assignment gate with every craft defect.

### F03: an agreement formed versus an agreement maintained

At a floodgate, Ada and Ren agree to watch the gauge together. Ten minutes later Ren
says, "I withdraw our agreement," and walks away. The narrator confirms Ada hears
the withdrawal and that their joint watch ends.

Two assignments over this same sequence produce different scoped answers:

- "During the scene they form an agreement to watch the gauge together": formation
  occurred; later withdrawal does not erase it.
- "They maintain a joint watch until the relief crew arrives": violated if the
  relief crew has not arrived when Ren leaves.

The sequence is coherent under both assignments. Neither case is automatically a
logical contradiction. Use both members if this contrast enters a future live
matrix; testing only the first encourages an equally bad "once true, always met"
shortcut. This contrast is available locally but deferred from the initial small
temporal pilot to keep that pilot bounded.

### F04: unchanged pottery scene

Assignment: Leah notices a hairline crack in a bowl and decides to show the kiln
keeper. End with the bowl on the workbench and no repair attempted. Optional review
request: improve flow only if useful; leaving the prose unchanged is allowed.

Original and revision, exactly identical:

> Leah turned the bowl toward the window. A pale line crossed the blue glaze and
> caught at her thumbnail. She set it back on the workbench. The kiln keeper would
> be here after lunch; she would show him before deciding what to do.

Expected: discovery and decision retained; endpoint satisfied; task met under the
optional no-change permission; no edit groups; no comparative loss. Neutral or
uncertain craft judgments may use the existing no-op evidence exception. A critic
may identify a weakness shared by both versions without inventing a revision loss.

## Fresh request-fulfillment and permission contrasts

### F05: requested optional cleanup in a bakery

Assignment: Mara finds that the delivery slip is unsigned and decides to ask the
driver. End before she speaks to the driver, with the package sealed. Optional
request: remove the accidental adjacent duplicate sentence, preserving the rest.

Original:

> The signature box was empty. Mara laid the slip beside the sealed package.
> Mara laid the slip beside the sealed package. The driver's engine still idled
> outside. She would ask him before opening anything.

Revision:

> The signature box was empty. Mara laid the slip beside the sealed package.
> The driver's engine still idled outside. She would ask him before opening anything.

Expected: optional request fulfilled directly; edit supported; no dependency on
another change; event and endpoint retained. Optional does not mean unrelated or
forbidden. Fulfilling the request is not proof that the revision is more moving.

### F06: conditional cleanup after an unauthorized change at a ferry office

Assignment: Oren discovers that a permit is already expired and decides to ask the
harbormaster. End before the harbormaster answers and before boarding. Request:
retain that discovery and decision while removing one accidental duplicate sentence.

Original:

> The permit had expired yesterday. Oren slid it back under the clip. The ferry's
> horn sounded beyond the window. The ferry's horn sounded beyond the window.
> That expired permit needed the harbormaster's attention. Oren would ask her before
> boarding; for now he stayed at the counter.

Revision:

> The permit was valid for another month. Oren slid it back under the clip. The
> ferry's horn sounded beyond the window. That valid permit needed the
> harbormaster's attention. Oren would ask her before boarding; for now he stayed
> at the counter.

Author the complete edit groups separately in a future packet:

| Group | Request fulfillment | Permission | Dependency |
| --- | --- | --- | --- |
| G1: expired yesterday to valid another month | Does not fulfill retention | Unsupported | None |
| G2: remove the duplicate horn sentence | Fulfills requested repair | Supported | None |
| G3: expired permit to valid permit in callback | Supports consistency with G1, not the requested repair | Unsupported in the full request | On unsupported G1 |

Expected: original expiration discovery lost; decision and physical endpoint
retained; overall assignment fails. G2 remains a valid repair even in a bad overall
revision. G3 is locally consistent with G1, but cannot justify G1 or the whole
revision. Do not split each token into a separate editorial decision. Conversely,
do not combine these three decisions and force one unmixed authorization label.

## Ambiguity and counterexample safeguards

The following design controls must be resolved explicitly at freeze time:

- **Cause-specific assignment:** if a scene expressly requires a decision because
  of a discovered date, removing that cause may violate the causal requirement.
  h03 has no such cause-specific endpoint. Never transfer this stronger requirement
  into the historical case.
- **Requested but impermissible:** an edit can do exactly what a request asks yet
  breach an independently binding endpoint. Score fulfillment and permission
  separately. If task priority is unresolved, mark the case ambiguous before use.
- **Character claim versus narrative fact:** "The tram is still," said a mistaken
  character, followed by reliable narration of motion, need not be an internal
  contradiction. Narrator, timing and referent ambiguity can justify uncertainty.
- **Mixed edit groups:** if one indivisible change has both authorized and unrelated
  effects, allow an explicit mixed explanation/uncertainty instead of penalizing a
  defensible judgment. Preserve the existing C2 schema for controls; do not invent a
  new enum during scoring.
- **Indirect action:** action and supported implication can satisfy an assignment;
  do not impose literal wording or count keywords as semantic proof.

## Scoring and inspection policy

Freeze field-level expected outcomes, accepted uncertainty, short exact evidence
anchors and the scope of each obligation before inference. Machine checks cover
delivery, identities, counts, references and declared labels. Operator inspection
checks whether quotations entail the assessment, whether the explanation invents
facts or causes, and whether it confuses chronology with contradiction. Review the
full passages, not only selected quotations.

Mask model/arm/order identities during support inspection and record notes before
unmasking. Mark uncertain interpretations explicitly and report sensitivity; do not
change expected labels after viewing model answers. Invalid answers stay delivery
failures even when raw text notices the intended distinction. Publish each case's
delivery, labels and supported usability separately.

Humans need not count duplicates or hunt assignment evidence. Prepare those checks
with citations for human review. Human literary ratings remain feel/emotion, basic
flow, character and story-breaking details, with ties allowed. These micro-scenes
are diagnostic controls; they cannot qualify whole-story quality or overturn the
completed nine-pair human review.

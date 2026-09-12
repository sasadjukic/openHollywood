# v29 follow-up: exact revisions in 007 and the failed critic reviews in 009

This addendum corrects the interpretation of OH-V01-008/009 in the
[consolidated report](step-19-cloud-v29-consolidated-2026-09-12.md).
The recorded totals do not change. The original report and three evidence
archives remain intact, including their hash manifests.

## OH-V01-007: the versions are almost identical, but not word-for-word identical

The partial-story JSON was compared directly against the immutable snapshot.
Scene 2 changes one phrase; scene 5 changes one sentence across its revisions.
Keeping surrounding prose unchanged is consistent with a targeted repair.
The material issue is the validity and consistency of the review, rather than
an absence of any writer edit.

### Scene 2 — The Narrow Corridor

The only prose change:

- Initial: **In the dim afternoon light**, he was once again a silhouette of erasure…
- Revision: **In the soft morning light**, he was once again a silhouette of erasure…

The first critic passed the scene with no issues. The continuity supervisor
blocked it with this allegation:

> Timeline contradiction: Scene 2 occurs in the afternoon, but follows Scene 1 which is established as morning.

Its recommended resolution was to correct the time or establish a time jump.
The writer changed afternoon to morning.

The approved scene plan itself specifies **Afternoon**. On the revised version,
the critic noted the new mismatch as **minor**, recommended changing it back to
afternoon, and still returned **pass**. Continuity likewise acknowledged the
mismatch, but issued only a **non-blocking warning** and said no repair was
needed because it prioritized the prior scene's morning timeline.

That is the recorded reason for acceptance: critic pass and no blocking
continuity finding. The graph did not accept the same previously rejected
prose. It accepted a slightly changed scene after a blocking allegation became
an advisory mismatch with the plan.

Assessment: morning followed by afternoon is not inherently contradictory.
The visible evidence supports concern that continuity unnecessarily changed
the planned time and that the two reviewers offered opposing guidance.
Acceptance is evidence of the review gates clearing, not proof of a sound edit.

### Scene 5 — The Confrontation

All three versions were unaccepted. The story stopped at the two-revision limit.

**Initial sentence**

> He seemed to be fighting an internal battle, a struggle between the urge to protect me from the truth and the agony of being invisible.

**After revision 1**

> He seemed to be fighting an internal battle, as if he were caught between the impulse to remain hidden and an overwhelming need to be known.

**After revision 2**

> It looked as if he were fighting an internal battle, as if he were caught between the impulse to remain hidden and an overwhelming need to be known.

The assigned POV is **Elara**. All three critiques claimed access to **Julian's**
private internal conflict. The first recommended making the sentence Elara's
inference, giving "He seemed to be fighting an internal battle..." as an example,
although that construction was already present. The second suggested forms
including "It looked as if"; the writer used that. The third still blocked the
sentence and suggested "He seemed caught between...".

The immediately preceding prose observes Julian's shoulder tension and uneven
breathing. The v29 instructions allow contextually attributable inference and
say it needs no special label. Whether the specificity of the inferred motives
overreaches is a literary judgment, but repeating nearly the same recommended
qualifiers while continuing to reject them is inconsistent repair guidance.
The writer did make localized edits. The hard critic finding remained, so no
version of this scene was accepted.

The structured evidence accompanying this note retains the full three
critiques, recommendations, exact diffs and independent prose SHA-256 values.

## OH-V01-009: what is known about the critic, and what was not retained

The story generated scene 1, **The Void in the Record**, and scene 2,
**The Fragile Welcome**. Scene 1 passed critique with no issues and all three
craft scores at 5. Scene 2 received two failed critic-response attempts, then
the story stopped. Scene 2 was not sent to the writer for revision.

### Important correction: no POV was assigned

All six approved scene plans contain:

    point_of_view_character_id: null

The actual scene-2 critic input also contained:

    assigned_character_id: null
    assignment_origin: unassigned

The critic's instructions explicitly say to return aligned when no viewpoint
is assigned, and not to invent an assignment or stricter narrative mode.
The style guide requested clinical, restrained, observational prose, but the
application contract did not convert that into a named single-character POV.

My earlier consolidated report interpreted the error as the critic blocking
the assigned character's own interiority. That was too specific and incorrect
for this case. The error message covers two different conditions:

    if not assigned or check["subject_character_id"] == assigned:
        raise ... viewpoint_subject_not_other_character

For 009, the first condition is already true: **there is no assigned character**.
The same is true for the recovered error in **008 scene 6**. Its retry explicitly
returned an aligned audit with assigned_character_id null. This corrects the
008/009 narrative in the consolidated report, while preserving its numerical
results and validation-error identifiers.

### What can be established about the two attempts

Both responses reached the typed POV-violation branch and failed the guard
above. The error happened before evidence handles were resolved into passages.
The retry was explicitly a repair of the review JSON, not a prose revision;
it failed the same guard.

The durable record does **not** preserve either failed response's:

- subject character or violation kind;
- selected evidence handles;
- assessment or proposed repair.

It retains the full request, response hash and length, and structured validation
error. Detailed viewpoint audits are recorded on successful critique completion.
The failure path deliberately retains bounded diagnostics without the failed
response body. Neither the retry prompt nor the runner logs recover those
missing findings.

Consequently, I cannot honestly identify the exact sentence the critic selected
or say whether it targeted Elias or Clara. The error establishes a review
contract failure, not a validated manuscript POV defect.

### Perspective shifts visible in the prose — my reading, not recovered critic findings

The draft is largely centered on Elias's analysis and manipulation, but also
states Clara's private beliefs and desires:

> She wanted to believe in the possibility of reconciliation.

> She believed he was offering her a hand to pull her out of the darkness.

> She did not realize that he was merely mapping the terrain of that darkness to ensure his own archive was complete.

Under an explicitly Elias-limited POV, those passages would warrant close
review. Under an unassigned or omniscient perspective, such movement is not
automatically a hard violation. They may explain the impression of shifting
perspective, but identifying them as the critic's actual citations would be
inventing evidence.

## Diagnostic implications

1. **007/2:** a continuity allegation overrode an explicit afternoon scene plan;
   the resulting disagreement was accepted as non-blocking.
2. **007/5:** the writer performed tiny targeted edits, but the critic's advice
   did not provide a stable route to an acceptable inference.
3. **008/009:** the model returned a hard POV finding despite an unassigned
   viewpoint. A shared validator message obscured this distinction in my first
   report.
4. **Observability:** failed review outputs do not retain enough structured
   detail to answer which passage was accused. A future diagnostic change
   should distinguish missing assignment from same-subject allegations and
   preserve a redacted, bounded attempted finding before validation rejects it.

These are investigation findings and possible follow-up work. No prompt,
validator, runtime behavior or model run was changed by this investigation.

## Source references

- Batch 2 partial evidence: OH-V01-007 scene-2 versions
  455cd1cefdf440498911a44519d11903 and ff9bd832260b477f8ade6a11a79ddaaa.
- Batch 2 scene-5 versions: 3a3a697fba0b49be8dadd3f56ec04281,
  f7e71d74165b436e86a5e4f4755cf799, a54fdeb950044e499bc050f2ec573d7a.
- Failed 009 critic invocations: c79d2999842a4710a101fc57ade60b7e,
  51a35916873f4d53b5e9fafa001c1402.
- [POV validator](../../apps/api/open_hollywood_api/services/production_model_executor.py)
  at line 3030: missing-assignment and same-subject guard, before evidence resolution.
- The same file at lines 1270–1289 records successful viewpoint audits;
  lines 1414–1429 record response metadata; line 1498 documents bounded failure
  diagnostics without retaining response content.
- Local extracted evidence:
  data/diagnostics/v29-cloud-cycle-follow-up-2026-09-12/evidence.json.

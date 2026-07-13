# What “fully agentic” should mean

Open Hollywood should operate at three levels.

## Level 1: Autonomous planning

From even a very small idea, the orchestrator should infer a provisional creative brief:

- Form: short story, novel, screenplay, TV pilot, stage play, etc.
- Genre and subgenre
- Intended audience and maturity
- Tone and stylistic constraints
- Target length
- Central dramatic question
- Themes
- Required and forbidden elements
- Ambiguities the system is authorized to resolve itself

The user should not be forced through a questionnaire. Missing information should be inferred and clearly labeled as an assumption in the resulting blueprint.

## Level 2: Autonomous production

Specialists create structured artifacts:

- Premise and thematic thesis
- World and locations
- Character dossiers and relationships
- Narrative architecture
- Beat sheet
- Scene or chapter plan
- Drafts
- Dialogue passes
- Continuity reports
- Critiques and revisions
- Final formatted work

## Level 3: Sparse human governance

The workflow pauses only at major checkpoints:

1. Story blueprint approval
2. Optional treatment or sample approval
3. Final review

At an approval point, the user can:

- Approve and continue
- Request changes through chat
- Reject a specific artifact
- Fork a new story direction
- Compare alternatives
- Change model assignments or budget
- Resume from an earlier checkpoint

LangGraph is particularly well aligned with this requirement because its interrupts persist graph state and wait until a workflow is resumed. Its persistence supports recovery, human review, replay, and branching. [LangGraph persistence documentation](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupt documentation](https://docs.langchain.com/oss/python/langgraph/interrupts).

## Important design principle: bounded agency

The orchestrator should select agents from a registered catalog. It should not recursively invent and spawn arbitrary agents.

For example, it may decide that a story needs a Historical Researcher or Dialogue Specialist, but each is a known capability with:

- Input schema
- Output schema
- Allowed tools
- Model assignment
- Token budget
- Maximum attempts
- Quality rubric
- Completion condition

This preserves creative flexibility without inviting infinite delegation, runaway costs, or impossible-to-debug behavior.
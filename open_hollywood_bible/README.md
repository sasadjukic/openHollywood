# Open Hollywood project bible

This directory is the durable product and architecture reference for the Open Hollywood rewrite. Read the smallest relevant document before making a product, workflow, model, memory, or UI decision.

## Authority and status

The focused documents below are canonical. The complete rewrite report is an
archive of the original analysis and may contain older or broader wording. When documents conflict, use this priority:

1. `product_contract_and_benchmarks.md`
2. `important_decisions.md`
3. Accepted records in `docs/adr/`
4. Focused topic documents in this directory
5. `open_hollywood_rewrite_report.md`

## Index

| Document | Purpose | Status |
|---|---|---|
| `product_contract_and_benchmarks.md` | v0.1 scope, approvals, evaluation, hardware, cost, prompts, failures | Accepted |
| `important_decisions.md` | Short list of non-negotiable product decisions | Accepted |
| `recommended_creative_workflow.md` | Target agent workflow and specialist catalog | Accepted direction |
| `recommended_tech_stack.md` | Technical stack and architectural rationale | Accepted direction |
| `memory_and_context_architecture.md` | Story memory, artifacts, and context policy | Accepted direction |
| `model_configuration.md` | Local/cloud/hybrid profiles and experiments | Accepted direction |
| `guardrails.md` | Run limits, completion controls, and mature fiction | Accepted direction |
| `formatting_strategy.md` | Canonical formats and deterministic export | Accepted direction |
| `ui_ux.md` | Workspace interaction and visual direction | Accepted direction |
| `what_fully_agentic_should_mean.md` | Product definition of bounded agency | Accepted direction |
| `step_by_step_implementation.md` | Authoritative implementation progress | Active tracker |
| `open_hollywood_rewrite_report.md` | Complete initial analysis | Archived reference |

## Maintenance rules

- Update focused documents when a decision changes.
- Record durable architecture changes as new ADRs instead of silently rewriting an accepted decision.
- Update `step_by_step_implementation.md` in the same change that completes a step.
- Use ISO dates (`YYYY-MM-DD`) for status updates.
- Keep all documents UTF-8.

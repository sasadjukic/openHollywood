# UI/UX concept

The primary workspace should be a three-panel application.

```text
┌──────────────────┬──────────────────────────────────┬─────────────────────┐
│ Projects         │ Chat and workflow timeline       │ Artifact inspector  │
│                  │                                  │                     │
│ Story A          │ User premise                     │ Story Bible         │
│  • Blueprint     │ Orchestrator response            │ Characters          │
│  • Characters    │ Agent activity cards             │ Locations           │
│  • Outline       │ Approval request                 │ Outline             │
│  • Draft         │ User revision instruction        │ Version history     │
│                  │                                  │ Diff / evaluation   │
└──────────────────┴──────────────────────────────────┴─────────────────────┘
```

## Central interaction

The center is chat plus an event timeline:

- “Character Architect completed”
- “World Builder completed”
- “Continuity Integrator found two conflicts”
- “Revision 2 accepted”
- “Waiting for blueprint approval”
- “Scene 8 drafting—local model”
- “Budget is 62% consumed”

Agent internals should be collapsible. Users need transparency without being
forced to watch raw chain-of-thought or every intermediate token.

## Artifact viewer

There is no general-purpose text editor. The right panel provides:

- Rendered artifact
- Version selector
- Side-by-side diff
- Comments anchored to sections
- “Ask orchestrator to revise this” action
- Approve, reject, and fork actions
- Provenance and evaluation summary
- Export

## Model settings

Use visual presets and capability warnings:

- Model unavailable
- Context too small for assigned task
- Structured output unsupported
- API key missing
- Estimated run cost
- Local model currently loading
- Fallback used

API keys must never appear in logs, workflow state, or frontend persistence.

## Branding

Keep:

- `#262626` base background
- `#e9a5a5`, `#81c1d9`, `#b8c1c0`, `#65c0e0`, and `#aea2db` accents
- Existing logo and icon
- Character-specific accent colors

Use the palette semantically. Human input, orchestrator activity, creative
agents, evaluators, warnings, and approved artifacts should have consistent
roles.

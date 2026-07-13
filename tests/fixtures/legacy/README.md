# Legacy behavior fixtures

These fixtures preserve the useful creative and orchestration contract of the
legacy prototype without restoring its implementation to the rewrite.

- Source branch: `openHollywood-legacy`
- Immutable source tag: `legacy-v2-final`
- Source commit: `b6c39b3034fc505f81145a07d4d9942a0a211854`

The character and director prompts are preserved verbatim from
`sample_prompts/` at the tag. `confession_scene.json` captures the reusable scene
configuration. `director_flow.json` captures the tested orchestration and
termination contract.

These are regression references, not automatically approved prompts for the
new product. Port behavior deliberately and compare it through tests.

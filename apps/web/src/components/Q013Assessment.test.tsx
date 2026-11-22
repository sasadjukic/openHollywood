import { readFileSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import type {
  ArtifactSelection,
  ArtifactVersionDetail,
  Q013InspectorView,
} from "@open-hollywood/contracts";
import { client } from "@open-hollywood/contracts/client";
import { act, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it } from "vitest";
import { fetchQ013Assessment } from "../api";
import { mountInspector } from "../test/mountAssessmentInspector";
import { inspectorCases } from "../test/q008InspectorCases";
import { Q013Assessment, type Q013Lookup } from "./SavedAssessment";
import { sameSelection, selectionForReview } from "./artifactSelection";

interface Cases {
  project: string;
  details: Record<"review" | "draft" | "adjacent", ArtifactVersionDetail>;
  expected: Q013InspectorView;
}

const scratchName = process.env.OH_Q013_INSPECTOR_SCRATCH;
if (scratchName !== undefined && !/^replay-[a-zA-Z0-9_-]+$/.test(scratchName))
  throw new Error("Invalid disposable inspector directory");
const scratch =
  scratchName &&
  resolve("../../data/diagnostics/q013-inspector-api-2026-11-22", scratchName);
function cases(): Cases {
  if (scratch)
    return JSON.parse(
      readFileSync(join(scratch, "cases.json"), "utf8"),
    ) as Cases;
  const { project, details, views } = inspectorCases();
  const original = views.review;
  return {
    project,
    details,
    expected: {
      ...original,
      contract: "q013-inspector-view-1",
      lookups: original.lookups.map((r) => ({ ...r, claim_id: "Q013" })),
      assessments: original.assessments.map((a) => ({
        ...a,
        claim_id: "Q013",
        operator_score: {
          claim_correctness: "pass",
          evidence_coverage: "fail",
        },
      })),
    },
  };
}
const { project, details, expected } = cases();
const [assessment] = expected.assessments;
const [account] = expected.accounting_records;
if (!assessment || !account) throw new Error("Missing assessment fixture");
const claim = assessment;
const receipt = account;
const usage = `${account.generation_usage.input_tokens.toLocaleString("en-US")} input · ${account.generation_usage.output_tokens.toLocaleString("en-US")} output`;
const longWait = { timeout: 60000 };
const panel = () =>
  within(screen.getByRole("region", { name: "Q013 assessment" }));
function unavailable(
  selection: ArtifactSelection,
  reason: NonNullable<Q013InspectorView["lookups"][number]["reason"]>,
): Q013InspectorView {
  return {
    contract: "q013-inspector-view-1",
    lookups: [
      {
        selection,
        status: "unavailable",
        reason,
        claim_id: null,
        delivery_id: null,
      },
    ],
    assessments: [],
    accounting_records: [],
    generation_totals: null,
  };
}
const read: Q013Lookup = scratch
  ? fetchQ013Assessment
  : (selection) => {
      const positive = [details.review, details.draft].some((detail) =>
        sameSelection(
          selection,
          selectionForReview({ projectId: project, detail }),
        ),
      );
      if (!positive)
        return Promise.resolve(
          unavailable(selection, "exact_selection_unavailable"),
        );
      return Promise.resolve({
        ...expected,
        lookups: expected.lookups.map((row) => ({ ...row, selection })),
      });
    };
function mount(initial: ArtifactVersionDetail, lookup: Q013Lookup = read) {
  return mountInspector(
    (props) => <Q013Assessment {...props} lookup={lookup} />,
    project,
    details,
    initial,
  );
}
function cleared() {
  expect(panel().queryByText(claim.claim)).not.toBeInTheDocument();
  expect(
    panel().queryByText(claim.model_assessment.reason),
  ).not.toBeInTheDocument();
  expect(panel().queryByText(receipt.delivery_id)).not.toBeInTheDocument();
  expect(
    panel().queryAllByText(
      /model judgment|operator scores|claim correctness|evidence coverage|shared generation usage|preflight input count|reasoning tokens|citations ·|delivery and request/i,
    ),
  ).toHaveLength(0);
  expect(panel().queryByText(usage)).not.toBeInTheDocument();
}
async function shown() {
  await panel().findByText(usage, {}, longWait);
  expect(panel().getAllByText(usage)).toHaveLength(1);
  expect(panel().getByText(claim.claim)).toBeVisible();
  expect(
    panel().getByText(`${claim.model} · ${claim.model_assessment.support}`),
  ).toBeVisible();
  expect(
    panel().getByText(
      `Citations · ${claim.model_assessment.evidence.join(", ")}`,
    ),
  ).toBeVisible();
  expect(
    panel().getByText(
      `Claim correctness · ${claim.operator_score.claim_correctness}`,
    ),
  ).toBeVisible();
  expect(
    panel().getByText(
      `Evidence coverage · ${claim.operator_score.evidence_coverage}`,
    ),
  ).toBeVisible();
  expect(panel().getAllByText(receipt.delivery_id)).toHaveLength(1);
  expect(
    panel().getByText(details.review.selected_version.id),
  ).toBeInTheDocument();
}
const refresh = () =>
  userEvent.click(panel().getByRole("button", { name: "Refresh assessment" }));

it("opens both exact versions and returns to the same shared receipt", async () => {
  const open = mount(details.review);
  for (const item of [details.review, details.draft, details.review]) {
    open(item);
    await shown();
  }
}, 180000);

it("rejects the workspace copy with identical IDs for either selection", async () => {
  const previous = client.getConfig().baseUrl;
  try {
    if (scratch) {
      if (!process.env.OH_Q013_COPY_URL)
        throw new Error("Missing copied workspace");
      client.setConfig({ baseUrl: process.env.OH_Q013_COPY_URL });
    }
    const copy: Q013Lookup = scratch
      ? fetchQ013Assessment
      : (s) => Promise.resolve(unavailable(s, "unregistered_workspace"));
    const open = mount(details.review, copy);
    for (const item of [details.review, details.draft]) {
      open(item);
      await panel().findByText(
        "Assessment unavailable in this workspace.",
        {},
        longWait,
      );
      cleared();
    }
  } finally {
    client.setConfig({ baseUrl: previous });
  }
}, 150000);

it("clears a pending refresh and ignores its late success after switching to the adjacent version", async () => {
  const captured = Promise.withResolvers<{
    signal: AbortSignal;
    response: Q013InspectorView;
  }>();
  const release = Promise.withResolvers<undefined>();
  let reads = 0;
  mount(details.draft, async (s, signal) => {
    const hold = ++reads === 2;
    const response = await read(s, signal);
    if (hold) {
      captured.resolve({ signal, response });
      await release.promise;
    }
    return response;
  });
  try {
    await shown();
    await refresh();
    await panel().findByText(/Checking this version/);
    cleared();
    const prior = await captured.promise;
    expect(prior.response.assessments).toEqual(expected.assessments);
    await userEvent.selectOptions(
      screen.getByLabelText("Artifact version"),
      details.adjacent.selected_version.id,
    );
    await panel().findByText(
      "Assessment unavailable for this version.",
      {},
      longWait,
    );
    expect(prior.signal.aborted).toBe(true);
    cleared();
    await act(async () => {
      release.resolve(undefined);
      await release.promise;
    });
    expect(
      panel().getByText("Assessment unavailable for this version."),
    ).toBeVisible();
    cleared();
  } finally {
    release.resolve(undefined);
  }
}, 170000);

it("clears the prior result on a damaged refresh and recovers after the copied member is restored", async () => {
  const member = scratch
    ? join(scratch, "publication", "delivery.json")
    : undefined;
  const original = member ? await readFile(member) : undefined;
  let damaged = false;
  const release = Promise.withResolvers<undefined>();
  const captured = Promise.withResolvers<Q013InspectorView>();
  mount(details.draft, async (s, signal) => {
    if (!damaged) return read(s, signal);
    const reply = scratch
      ? await read(s, signal)
      : unavailable(s, "publication_member_changed");
    captured.resolve(reply);
    await release.promise;
    return reply;
  });
  await shown();
  try {
    if (original && member) {
      const edited = JSON.parse(original.toString("utf8")) as {
        usage: { input_tokens: number };
      };
      expect(edited.usage.input_tokens).toBe(
        receipt.generation_usage.input_tokens,
      );
      edited.usage.input_tokens += 1;
      await writeFile(member, JSON.stringify(edited));
    }
    damaged = true;
    await refresh();
    await panel().findByText(/Checking this version/);
    cleared();
    const reply = await captured.promise;
    expect(reply).toEqual(
      unavailable(
        selectionForReview({ projectId: project, detail: details.draft }),
        "publication_member_changed",
      ),
    );
    await act(async () => {
      release.resolve(undefined);
      await release.promise;
    });
    await panel().findByText(/publication could not be verified/, {}, longWait);
    cleared();
  } finally {
    release.resolve(undefined);
    if (original && member) await writeFile(member, original);
    damaged = false;
  }
  await refresh();
  await shown();
}, 180000);

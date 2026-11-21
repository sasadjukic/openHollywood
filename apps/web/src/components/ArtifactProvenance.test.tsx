import type {
  ArtifactProvenance,
  ArtifactSelection,
  ArtifactVersionDetail,
} from "@open-hollywood/contracts";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { fetchArtifactProvenance, fetchQ008Assessment } from "../api";
import { ArtifactInspector } from "./ArtifactInspector";

vi.mock("../api", () => ({
  fetchArtifactProvenance: vi.fn(),
  fetchQ008Assessment: vi.fn(),
}));
const fetchProvenance = vi.mocked(fetchArtifactProvenance);
const fetchAssessment = vi.mocked(fetchQ008Assessment);
const project = "11111111-1111-1111-1111-111111111111";
const logical = "22222222-2222-2222-2222-222222222222";
const oldVersion = "33333333-3333-3333-3333-333333333333";
const newVersion = "44444444-4444-4444-4444-444444444444";
const draftVersion = "55555555-5555-5555-5555-555555555555";

function present<T>(value: T | null | undefined): T {
  if (value === undefined || value === null) throw new Error("Missing fixture");
  return value;
}

function detail(version = oldVersion): ArtifactVersionDetail {
  const versions = [newVersion, oldVersion].map((id, index) => ({
    id,
    version_number: 2 - index,
    schema_version: "1",
    created_at: "2026-11-19T12:00:00Z",
    parent_version_id: index === 0 ? oldVersion : null,
    change_summary: "Saved critique",
    specialist_role: "scene_critic",
    provider: "fixture",
    model_identifier: "fixture",
  }));
  return {
    artifact: {
      id: logical,
      artifact_key: "scene-review",
      artifact_type: "critique",
      title: "Scene review",
      status: "draft",
      active_version_id: newVersion,
      versions,
    },
    selected_version: present(versions.find((item) => item.id === version)),
    content: {
      summary: version === oldVersion ? "Original review" : "Revised review",
    },
    content_sha256: (version === oldVersion ? "a" : "b").repeat(64),
    evaluations: [],
  };
}

function view(selection: ArtifactSelection): ArtifactProvenance {
  return {
    contract: "artifact-provenance-view-1",
    selection,
    status: "identity_verified",
    reason: "exact_registered_identity",
    relationship: {
      review_artifact_id: selection.artifact_id,
      review_version_id: selection.version_id,
      review_content_sha256: selection.content_sha256,
      draft_artifact_id: logical,
      draft_version_id: draftVersion,
      draft_content_sha256: "c".repeat(64),
      review_invocation_id: newVersion,
      workflow_run_id: project,
      source_registration: "registered-local-source",
      selected_is_latest_at_lookup: selection.version_id === newVersion,
      review_is_latest_at_lookup: selection.version_id === newVersion,
      draft_is_latest_at_lookup: false,
      assessment_source: "unsupported_contract",
      captured_assessment_delivery: "missing",
      semantic_support: "unassessed",
      evidence_adequacy: "unassessed",
      editorial_effect: "unassessed",
      edit_necessity: "unassessed",
      craft: "unassessed",
    },
    assessment_attachment_eligible: false,
    writer_dispatch_authorized: false,
    live_calls: 0,
  };
}

function setup(initial = detail(), projectId = project) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const node = (
    value: ArtifactVersionDetail,
    selected = value.selected_version.id,
    p = projectId,
  ) => (
    <QueryClientProvider client={client}>
      <ArtifactInspector
        artifact={value.artifact}
        detail={value}
        selectedVersionId={selected}
        projectId={p}
        isLoading={false}
        isOpen
        onClose={vi.fn()}
        onSelectVersion={vi.fn()}
      />
    </QueryClientProvider>
  );
  const result = render(node(initial));
  return {
    client,
    ...result,
    update: (value: ArtifactVersionDetail, selected?: string, p?: string) => {
      result.rerender(node(value, selected, p));
    },
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

beforeEach(() => {
  fetchProvenance.mockReset();
  fetchAssessment.mockReset();
});

describe("exact-version provenance in the inspector", () => {
  it("returns to fresh provenance while a saved assessment request is still pending", async () => {
    const assessment =
      deferred<Awaited<ReturnType<typeof fetchQ008Assessment>>>();
    fetchAssessment.mockReturnValue(assessment.promise);
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve(view(selection)),
    );
    setup();
    await screen.findByText("Version relationship verified");
    expect(fetchAssessment).not.toHaveBeenCalled();
    await userEvent.click(
      screen.getByRole("button", { name: "View saved assessment" }),
    );
    await screen.findByText(/Checking this version’s assessment/);
    const [selection, signal] = present(fetchAssessment.mock.calls[0]);
    await userEvent.click(
      screen.getByRole("button", { name: "Return to provenance" }),
    );
    await screen.findByText("Version relationship verified");
    expect(signal.aborted).toBe(true);
    expect(fetchProvenance).toHaveBeenCalledTimes(2);
    await act(async () => {
      assessment.resolve({
        contract: "q008-inspector-view-1",
        lookups: [
          {
            selection,
            status: "unavailable",
            reason: "unregistered_workspace",
            delivery_id: null,
            claim_id: null,
          },
        ],
        assessments: [],
        accounting_records: [],
        generation_totals: null,
      });
      await assessment.promise;
    });
    expect(
      screen.queryByRole("region", { name: "Q008 assessment" }),
    ).not.toBeInTheDocument();
    expect(screen.getByText("Version relationship verified")).toBeVisible();
  });

  it("binds the reviewed-draft role to its own version and hash", async () => {
    fetchProvenance.mockImplementation((selection) => {
      const result = view(selection);
      Object.assign(present(result.relationship), {
        review_version_id: draftVersion,
        draft_version_id: selection.version_id,
        draft_content_sha256: selection.content_sha256,
      });
      return Promise.resolve(result);
    });
    const value = detail();
    setup({
      ...value,
      artifact: { ...value.artifact, artifact_type: "scene_draft" },
    });
    await screen.findByText("Version relationship verified");
    expect(fetchProvenance.mock.calls[0]?.[0].role).toBe("reviewed_draft");
    expect(screen.getByText(oldVersion)).toBeInTheDocument();
    expect(screen.getByText(draftVersion)).toBeInTheDocument();
  });

  it.each(["relationship", "permission"])(
    "rejects an invalid %s even with a matching selection",
    async (fault) => {
      fetchProvenance.mockImplementation((selection) => {
        const result = view(selection);
        if (fault === "relationship") {
          present(result.relationship).review_content_sha256 = "f".repeat(64);
        } else {
          Object.assign(result, { writer_dispatch_authorized: true });
        }
        return Promise.resolve(result);
      });
      setup();
      await screen.findByText("The relationship could not be verified.");
      expect(
        screen.queryByText("Version relationship verified"),
      ).not.toBeInTheDocument();
      expect(screen.queryByText(draftVersion)).not.toBeInTheDocument();
    },
  );

  it("keeps verified identity separate from missing assessment and quality", async () => {
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve(view(selection)),
    );
    setup();
    expect(
      await screen.findByText("Version relationship verified"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/You are viewing an older version/),
    ).toBeInTheDocument();
    expect(screen.getByText("Assessment unavailable")).toBeInTheDocument();
    expect(
      screen.getByText(
        /does not establish accuracy, edit necessity or story quality/,
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(oldVersion)).toBeInTheDocument();
    expect(screen.getByText(draftVersion)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /approve|revise|write|attach/i }),
    ).not.toBeInTheDocument();
    expect(fetchProvenance.mock.calls[0]?.[0]).toEqual({
      role: "original_review",
      project_id: project,
      artifact_id: logical,
      version_id: oldVersion,
      content_sha256: "a".repeat(64),
    });
  });

  it.each([
    ["unregistered_workspace", /no registered provenance source/],
    ["no_registered_association", /No registered review relationship/],
    ["ambiguous_association", /More than one review relationship/],
    ["selection_mismatch", /selection does not match/],
    ["current_source_missing", /record needed.*is missing/],
    ["current_source_mismatch", /Current source records do not match/],
    ["source_changed", /could not be revalidated/],
    ["source_unavailable", /registered source is unavailable/],
  ] as const)("shows %s without a relationship", async (reason, message) => {
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve({
        ...view(selection),
        status: "unavailable",
        reason,
        relationship: null,
      }),
    );
    setup();
    expect(await screen.findByText(message)).toBeInTheDocument();
    expect(
      screen.queryByText("Version relationship verified"),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(draftVersion)).not.toBeInTheDocument();
  });

  it.each([
    "project_id",
    "artifact_id",
    "version_id",
    "content_sha256",
    "role",
  ] as const)("rejects a response with wrong %s", async (field) => {
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve({
        ...view(selection),
        selection: {
          ...selection,
          [field]: field === "role" ? "reviewed_draft" : "wrong",
        },
      }),
    );
    setup();
    expect(
      await screen.findByText(/response does not match this selection/),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Version relationship verified"),
    ).not.toBeInTheDocument();
  });

  it("does not reuse a late response after switching versions", async () => {
    const first = deferred<ArtifactProvenance>();
    fetchProvenance.mockImplementation((selection) =>
      selection.version_id === oldVersion
        ? first.promise
        : Promise.resolve(view(selection)),
    );
    const page = setup();
    await waitFor(() => {
      expect(fetchProvenance).toHaveBeenCalledTimes(1);
    });
    const [initialSelection, initialSignal] = present(
      fetchProvenance.mock.calls[0],
    );
    page.update(detail(newVersion));
    expect(
      await screen.findByText("Version relationship verified"),
    ).toBeInTheDocument();
    expect(initialSignal.aborted).toBe(true);
    await act(async () => {
      first.resolve(view(initialSelection));
      await first.promise;
    });
    expect(screen.queryByText(oldVersion)).not.toBeInTheDocument();
    expect(
      screen.queryByText(/You are viewing an older version/),
    ).not.toBeInTheDocument();
    expect(screen.getByText("Revised review")).toBeInTheDocument();
  });

  it("hides cached success during revalidation and after a failed check", async () => {
    const next = deferred<ArtifactProvenance>();
    fetchProvenance
      .mockImplementationOnce((selection) => Promise.resolve(view(selection)))
      .mockImplementationOnce(() => next.promise);
    const page = setup();
    await screen.findByText("Version relationship verified");
    void page.client.invalidateQueries({ queryKey: ["artifact-provenance"] });
    expect(
      await screen.findByText(/Checking this exact version/),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Version relationship verified"),
    ).not.toBeInTheDocument();
    const [selected] = present(fetchProvenance.mock.calls[0]);
    await act(async () => {
      next.resolve({
        ...view(selected),
        status: "unavailable",
        reason: "source_changed",
        relationship: null,
      });
      await next.promise;
    });
    expect(
      await screen.findByText(/could not be revalidated/),
    ).toBeInTheDocument();
    fetchProvenance.mockRejectedValue(new Error("private raw server failure"));
    await userEvent.click(screen.getByRole("button", { name: "Check again" }));
    expect(
      await screen.findByText("Review provenance could not be checked."),
    ).toBeInTheDocument();
    expect(screen.queryByText(/private raw/)).not.toBeInTheDocument();
  });

  it("suppresses a cached identity after an HTTP refetch error", async () => {
    fetchProvenance
      .mockImplementationOnce((selection) => Promise.resolve(view(selection)))
      .mockRejectedValue(new Error("failed"));
    const page = setup();
    await screen.findByText("Version relationship verified");
    await act(async () => {
      await page.client.invalidateQueries({
        queryKey: ["artifact-provenance"],
      });
    });
    expect(
      await screen.findByText("Review provenance could not be checked."),
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Version relationship verified"),
    ).not.toBeInTheDocument();
  });

  it("does not load provenance for stale artifact detail or unrelated artifact kinds", () => {
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve(view(selection)),
    );
    const value = detail();
    const page = setup({
      ...value,
      artifact: { ...value.artifact, artifact_type: "story_blueprint" },
    });
    expect(
      screen.queryByRole("region", { name: "Review provenance" }),
    ).not.toBeInTheDocument();
    expect(fetchProvenance).not.toHaveBeenCalled();
    page.update(value, newVersion);
    expect(
      screen.getByText(/loaded artifact does not match/),
    ).toBeInTheDocument();
    expect(screen.queryByText("Original review")).not.toBeInTheDocument();
    expect(fetchProvenance).not.toHaveBeenCalled();
  });

  it("rebinds the request when project or content hash changes", async () => {
    fetchProvenance.mockImplementation((selection) =>
      Promise.resolve(view(selection)),
    );
    const page = setup();
    await screen.findByText("Version relationship verified");
    page.update(
      { ...detail(), content_sha256: "d".repeat(64) },
      oldVersion,
      newVersion,
    );
    await waitFor(() => {
      expect(fetchProvenance).toHaveBeenCalledTimes(2);
    });
    expect(fetchProvenance.mock.calls[1]?.[0]).toMatchObject({
      project_id: newVersion,
      content_sha256: "d".repeat(64),
    });
  });

  it("renders source strings literally and rejects an incomplete response", async () => {
    fetchProvenance.mockImplementation((selection) => {
      const result = view(selection);
      present(result.relationship).source_registration =
        "<script>unsafe()</script> [link](https://example.invalid)";
      return Promise.resolve(result);
    });
    const page = setup();
    await screen.findByText("Version relationship verified");
    await userEvent.click(screen.getByText("Source details"));
    expect(screen.getByText(/<script>unsafe/)).toBeInTheDocument();
    expect(page.container.querySelector("script")).toBeNull();
    expect(page.container.querySelector("a")).toBeNull();
    fetchProvenance.mockResolvedValue({} as ArtifactProvenance);
    page.update(detail(newVersion));
    expect(
      await screen.findByText(/response does not match/),
    ).toBeInTheDocument();
  });
});

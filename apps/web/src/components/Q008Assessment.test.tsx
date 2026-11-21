import type {
  ArtifactSelection,
  ArtifactVersionDetail,
} from "@open-hollywood/contracts";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  inspectorCases,
  savedReplay,
  withPublicationCopy,
} from "../test/q008InspectorCases";
import { ArtifactInspector } from "./ArtifactInspector";
import {
  Q008Assessment,
  type Q008Inventory,
  type Q008Lookup,
} from "./Q008Assessment";
import {
  sameSelection,
  selectionForReview,
  type ReviewPanelProps,
} from "./artifactSelection";

const { project, details, views } = inspectorCases();
const [claim] = views.draft.assessments;
const [account] = views.draft.accounting_records;
if (!claim || !account)
  throw new Error("Missing saved assessment or accounting");
const assessment = claim;
const receipt = account;
const expectedUsage = `${receipt.generation_usage.input_tokens.toLocaleString("en-US")} input · ${receipt.generation_usage.output_tokens.toLocaleString("en-US")} output`;

function read(selection: ArtifactSelection) {
  for (const key of ["review", "draft", "adjacent"] as const) {
    if (
      sameSelection(
        selection,
        selectionForReview({ projectId: project, detail: details[key] }),
      )
    )
      return views[key];
  }
  throw new Error("Unknown fixture selection");
}

function mount(lookup: Q008Lookup, initial: ArtifactVersionDetail) {
  const client = new QueryClient();
  function Panel(props: ReviewPanelProps) {
    return <Q008Assessment {...props} lookup={lookup} />;
  }
  function tree(
    detail: ArtifactVersionDetail,
    selected = detail.selected_version.id,
  ) {
    return (
      <QueryClientProvider client={client}>
        <ArtifactInspector
          ReviewPanel={Panel}
          projectId={project}
          artifact={detail.artifact}
          detail={detail}
          selectedVersionId={selected}
          isLoading={false}
          isOpen
          onClose={() => undefined}
          onSelectVersion={(id) => {
            const next = Object.values(details).find(
              (d) => d.selected_version.id === id,
            );
            if (!next) throw new Error("Unknown version");
            page.rerender(tree(next));
          }}
        />
      </QueryClientProvider>
    );
  }
  const page = render(tree(initial));
  return (detail: ArtifactVersionDetail, selected?: string) => {
    page.rerender(tree(detail, selected));
  };
}

const panel = () =>
  within(screen.getByRole("region", { name: "Q008 assessment" }));
function expectCleared() {
  expect(panel().queryByText(assessment.claim)).not.toBeInTheDocument();
  expect(
    panel().queryByText(assessment.model_assessment.reason),
  ).not.toBeInTheDocument();
  expect(
    panel().queryByText(
      /model judgment|operator score|shared generation usage|preflight input count|reasoning tokens|citations ·|delivery and request/i,
    ),
  ).not.toBeInTheDocument();
  expect(panel().queryByText(expectedUsage)).not.toBeInTheDocument();
  expect(panel().queryByText(receipt.delivery_id)).not.toBeInTheDocument();
}

describe("Q008 in an isolated artifact inspector", () => {
  if (savedReplay) {
    it("reads the saved delivery on each open and detects damage made while it is displayed", async () => {
      await withPublicationCopy(async (lookup, damage) => {
        const readOnDemand = vi.fn(lookup);
        const open = mount(readOnDemand, details.review);
        for (const key of ["review", "draft"] as const) {
          open(details[key]);
          await panel().findByText(
            "58,894 input · 345 output",
            {},
            { timeout: 60000 },
          );
          expect(panel().getByText(assessment.claim)).toBeVisible();
          expect(panel().getByText(receipt.delivery_id)).toBeInTheDocument();
        }
        await damage();
        await userEvent.click(
          panel().getByRole("button", { name: "Refresh assessment" }),
        );
        await panel().findByText(/Checking this version/);
        expectCleared();
        await panel().findByText(
          /publication could not be verified/,
          {},
          { timeout: 60000 },
        );
        expectCleared();
        expect(readOnDemand).toHaveBeenCalledTimes(3);
        const [review, draft, damaged] = await Promise.all(
          readOnDemand.mock.results.map(
            (r) => r.value as Promise<Q008Inventory>,
          ),
        );
        expect(review?.accounting_records).toEqual(draft?.accounting_records);
        expect(draft?.assessments).toEqual(review?.assessments);
        expect(damaged?.lookups[0]?.reason).toBe("publication_member_changed");
        expect(damaged?.generation_totals).toBeNull();
      });
    }, 200000);
  }
  it.each([
    ["review", "draft"],
    ["draft", "review"],
  ] as const)(
    "opens %s then %s with the same generation and original request",
    async (first, second) => {
      const lookup = vi.fn<Q008Lookup>((s) => Promise.resolve(read(s)));
      const open = mount(lookup, details[first]);
      for (const key of [first, second, first]) {
        open(details[key]);
        expect(await panel().findByText(assessment.claim)).toBeVisible();
        expect(
          panel().getByText(
            `${assessment.model} · ${assessment.model_assessment.support}`,
          ),
        ).toBeVisible();
        expect(panel().getAllByText(expectedUsage)).toHaveLength(1);
        expect(
          panel().getByText(assessment.model_assessment.reason),
        ).toBeVisible();
        expect(
          panel().getByText(
            `Citations · ${assessment.model_assessment.evidence.join(", ")}`,
          ),
        ).toBeVisible();
        expect(panel().getByText(/Operator score · 3\/3/)).toBeVisible();
        expect(panel().getByText(/craft are unassessed/)).toBeVisible();
        await userEvent.click(panel().getByText("Delivery and request"));
        expect(panel().getByText(receipt.delivery_id)).toBeVisible();
        expect(
          panel().getByText(details.review.selected_version.id),
        ).toBeVisible();
      }
      expect(views.review.assessments).toEqual(views.draft.assessments);
      expect(views.review.accounting_records).toEqual(
        views.draft.accounting_records,
      );
      expect(lookup.mock.calls.map(([s]) => s.version_id)).toEqual(
        [first, second, first].map((k) => details[k].selected_version.id),
      );
    },
  );

  it("drops the old draft during a refresh and ignores its success after switching versions", async () => {
    const old = Promise.withResolvers<Q008Inventory>();
    const child = Promise.withResolvers<Q008Inventory>();
    const lookup = vi
      .fn<Q008Lookup>()
      .mockResolvedValueOnce(views.draft)
      .mockReturnValueOnce(old.promise)
      .mockReturnValueOnce(child.promise);
    mount(lookup, details.draft);
    await panel().findByText(expectedUsage);
    await userEvent.click(
      panel().getByRole("button", { name: "Refresh assessment" }),
    );
    await panel().findByText(/Checking this version/);
    expectCleared();
    await userEvent.selectOptions(
      screen.getByLabelText("Artifact version"),
      details.adjacent.selected_version.id,
    );
    await waitFor(() => {
      expect(lookup).toHaveBeenCalledTimes(3);
    });
    expect(lookup.mock.calls[1]?.[1].aborted).toBe(true);
    expect(lookup.mock.calls[2]?.[0].version_id).toBe(
      details.adjacent.selected_version.id,
    );
    expect(details.draft.content_sha256).toBe(details.adjacent.content_sha256);
    expectCleared();
    await act(async () => {
      child.resolve(views.adjacent);
      await child.promise;
    });
    await panel().findByText("Assessment unavailable for this version.");
    await act(async () => {
      old.resolve(views.draft);
      await old.promise;
    });
    expect(
      panel().getByText("Assessment unavailable for this version."),
    ).toBeVisible();
    expectCleared();
  });

  it.each(["damage", "error"] as const)(
    "clears a successful display during refresh and after %s",
    async (fault) => {
      const delayed = Promise.withResolvers<Q008Inventory>();
      const lookup = vi
        .fn<Q008Lookup>()
        .mockResolvedValueOnce(views.draft)
        .mockReturnValueOnce(delayed.promise);
      mount(lookup, details.draft);
      await panel().findByText(expectedUsage);
      await userEvent.click(
        panel().getByRole("button", { name: "Refresh assessment" }),
      );
      await panel().findByText(/Checking this version/);
      expectCleared();
      await act(async () => {
        if (fault === "damage") delayed.resolve(views.damaged);
        else delayed.reject(new Error("private transport detail"));
        await delayed.promise.catch(() => undefined);
      });
      await panel().findByText(/publication could not be verified/);
      expectCleared();
      expect(
        screen.queryByText(/private transport detail/),
      ).not.toBeInTheDocument();
    },
  );

  it("rejects a success for the other selection and hides stale workspace detail", async () => {
    const lookup = vi.fn<Q008Lookup>().mockResolvedValue(views.review);
    const open = mount(lookup, details.draft);
    await panel().findByText(/publication could not be verified/);
    expectCleared();
    open(details.draft, details.adjacent.selected_version.id);
    expect(
      screen.queryByRole("region", { name: "Q008 assessment" }),
    ).not.toBeInTheDocument();
    expect(lookup).toHaveBeenCalledTimes(1);
  });

  it.each(["other delivery", "duplicate accounting", "changed totals"])(
    "suppresses the judgment and usage for %s",
    async (fault) => {
      const invalid = structuredClone(views.draft);
      const [record] = invalid.accounting_records;
      if (!record || !invalid.generation_totals)
        throw new Error("Missing fixture accounting");
      if (fault === "other delivery") record.delivery_id = "other-delivery";
      else if (fault === "duplicate accounting")
        invalid.accounting_records.push(record);
      else
        invalid.generation_totals = {
          ...invalid.generation_totals,
          input_tokens: record.generation_usage.input_tokens + 1,
        };
      mount(vi.fn<Q008Lookup>().mockResolvedValue(invalid), details.draft);
      await panel().findByText(/publication could not be verified/);
      expectCleared();
    },
  );
});

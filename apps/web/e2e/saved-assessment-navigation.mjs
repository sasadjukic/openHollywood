import assert from "node:assert/strict";
import { readFile, realpath, writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright-core";

export async function verifyNavigation(
  { claimId, directory, usage, phase },
  registered,
  copied,
  scratch,
) {
  const root = await realpath(directory);
  assert.equal(path.dirname(await realpath(scratch)), root);
  assert.match(path.basename(scratch), /^replay-[\w-]+$/);
  const cases = JSON.parse(
    await readFile(path.join(scratch, "cases.json"), "utf8"),
  );
  const { review, draft, adjacent, adjacentReview } = cases.selections;
  const endpoint = claimId.toLowerCase() + "-assessment";
  const usageText =
    usage.input_tokens.toLocaleString("en-US") +
    " input · " +
    usage.output_tokens.toLocaleString("en-US") +
    " output";
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const observations = [];

  async function assertInViewport(locator) {
    const visible = await locator.evaluate(
      (el) =>
        new Promise((resolve) => {
          const observer = new IntersectionObserver(([entry]) => {
            observer.disconnect();
            resolve(entry.intersectionRatio > 0.5);
          });
          observer.observe(el);
        }),
    );
    assert.ok(visible, "The selected review panel must be on screen");
  }

  async function exercise(origin, registeredWorkspace) {
    assert.equal(new URL(origin).hostname, "127.0.0.1");
    const context = await browser.newContext({
      viewport: { width: 1500, height: 960 },
      serviceWorkers: "block",
    });
    const page = await context.newPage();
    page.setDefaultTimeout(45000);
    const errors = [];
    const assessmentRequests = [];
    page.on("pageerror", (e) => errors.push(e.message));
    let hold;
    await context.route("**/*", async (route) => {
      const req = route.request();
      const url = new URL(req.url());
      if (url.origin !== origin || req.method() !== "GET") {
        errors.push("Unexpected browser origin or method");
        return route.abort();
      }
      if (url.pathname.endsWith("-assessment")) {
        assessmentRequests.push(url.pathname);
        if (hold) await hold.promise;
      }
      await route.continue();
    });
    const nav = page.getByRole("navigation", {
      name: "Story projects and artifacts",
    });
    const inspector = page.getByRole("complementary", {
      name: "Artifact inspector",
    });
    const select = inspector.getByRole("combobox", {
      name: "Artifact version",
    });
    const assessment = inspector.getByRole("region", {
      name: claimId + " assessment",
    });
    const provenance = inspector.getByRole("region", {
      name: "Review provenance",
    });
    const open = () =>
      inspector.getByRole("button", { name: "View saved assessment" }).click();

    async function navigate(key) {
      const name = cases.titles[key];
      const kind = key === "draft" ? "Scene Draft" : "Critique";
      await nav
        .getByRole("button")
        .filter({ has: page.getByText(name, { exact: true }) })
        .filter({ hasText: kind })
        .click();
      await select.selectOption(cases.selections[key].version_id);
      await provenance
        .getByText("This workspace has no registered provenance source.")
        .waitFor();
      assert.equal(await assessment.count(), 0);
      assert.equal(await select.inputValue(), cases.selections[key].version_id);
    }

    async function request(selection, suffix, act, pending = false) {
      const pathname = `/api/v1/artifact-versions/${selection.version_id}/${suffix}`;
      const matches = (r) => new URL(r.url()).pathname === pathname;
      if (pending) hold = Promise.withResolvers();
      try {
        const [response] = await Promise.all([
          page.waitForResponse(matches),
          (async () => {
            if (!pending) return act();
            await Promise.all([page.waitForRequest(matches), act()]);
            await assessment.getByText(/Checking this version/).waitFor();
            await assertCleared();
            hold.resolve();
          })(),
        ]);
        assert.equal(response.status(), 200);
        assert.equal(await response.headerValue("cache-control"), "no-store");
        const { version_id, ...query } = selection;
        assert.deepEqual(
          Object.fromEntries(new URL(response.url()).searchParams),
          query,
        );
        return await response.json();
      } finally {
        hold?.resolve();
        hold = undefined;
      }
    }

    async function assertCleared() {
      for (const text of [
        cases.claim,
        cases.delivery,
        "Model judgment",
        "Shared generation usage",
        usageText,
        /Operator score|Claim correctness ·|Evidence coverage ·|Preflight input count ·|Citations ·|Reasoning tokens included/,
      ]) {
        assert.equal(
          await assessment.getByText(text, { exact: true }).count(),
          0,
        );
      }
    }

    async function lookup(selection, act, reason = null, pending = false) {
      const view = await request(selection, endpoint, act, pending);
      assert.equal(view.contract, claimId.toLowerCase() + "-inspector-view-1");
      assert.equal(view.lookups.length, 1);
      const [row] = view.lookups;
      assert.deepEqual(row.selection, selection);
      assert.equal(row.reason, reason);
      if (reason) {
        assert.equal(row.status, "unavailable");
        assert.equal(row.delivery_id, null);
        assert.equal(row.claim_id, null);
        assert.deepEqual(view.assessments, []);
        assert.deepEqual(view.accounting_records, []);
        assert.equal(view.generation_totals, null);
        const messages = {
          exact_selection_unavailable:
            "Assessment unavailable for this version.",
          unregistered_workspace: "Assessment unavailable in this workspace.",
          publication_member_changed:
            "Assessment unavailable. The publication could not be verified.",
        };
        await assessment.getByText(messages[reason], { exact: true }).waitFor();
        await assertInViewport(
          assessment.getByText(messages[reason], { exact: true }),
        );
        await assertCleared();
      } else {
        assert.equal(row.status, "available");
        assert.equal(row.claim_id, claimId);
        assert.equal(row.delivery_id, cases.delivery);
        assert.equal(view.assessments.length, 1);
        assert.equal(view.accounting_records.length, 1);
        assert.equal(view.accounting_records[0].delivery_id, cases.delivery);
        assert.deepEqual(view.accounting_records[0].request_selection, review);
        assert.deepEqual(view.accounting_records[0].generation_usage, usage);
        assert.deepEqual(view.generation_totals, usage);
        await assessment.getByText(cases.claim, { exact: true }).waitFor();
        await assertInViewport(
          assessment.getByRole("heading", { name: claimId + " assessment" }),
        );
        await assessment.getByText(usageText, { exact: true }).waitFor();
        if (claimId === "Q013") {
          assert.equal(
            view.assessments[0].model_assessment.support,
            "supported",
          );
          assert.deepEqual(view.assessments[0].model_assessment.evidence, [
            "E0920",
          ]);
          assert.deepEqual(view.assessments[0].operator_score, {
            claim_correctness: "pass",
            evidence_coverage: "pass",
          });
          for (const text of [
            "Citations · E0920",
            "Claim correctness · pass",
            "Evidence coverage · pass",
          ]) {
            await assessment.getByText(text, { exact: true }).waitFor();
          }
        }
        const details = assessment.locator("details");
        if (!(await details.evaluate((el) => el.open)))
          await details.locator("summary").click();
        await details.getByText(cases.delivery, { exact: true }).waitFor();
        await details.getByText(review.version_id, { exact: true }).waitFor();
      }
      observations.push({
        workspace: registeredWorkspace ? "registered" : "copy",
        version: selection.version_id,
        result: reason ?? "available",
        pending_cleared: pending,
      });
      return view;
    }

    async function back(selection) {
      const count = assessmentRequests.length;
      const result = await request(selection, "provenance", () =>
        inspector.getByRole("button", { name: "Return to provenance" }).click(),
      );
      assert.deepEqual(result.selection, selection);
      assert.equal(result.status, "unavailable");
      assert.equal(result.reason, "unregistered_workspace");
      assert.equal(result.relationship, null);
      await provenance
        .getByText("This workspace has no registered provenance source.")
        .waitFor();
      await assertInViewport(
        provenance.getByRole("heading", { name: "Review provenance" }),
      );
      assert.equal(await assessment.count(), 0);
      assert.equal(
        await inspector.getByText(cases.delivery, { exact: true }).count(),
        0,
      );
      assert.equal(assessmentRequests.length, count);
      observations.push({
        workspace: registeredWorkspace ? "registered" : "copy",
        version: selection.version_id,
        result: "returned_to_provenance",
        ...(claimId === "Q013" ? { provenance_reason: result.reason } : {}),
      });
    }
    try {
      await page.goto(origin);
      await nav
        .getByRole("button")
        .filter({ has: page.getByText(cases.project, { exact: true }) })
        .click();
      if (phase === "damage") {
        await navigate("draft");
        assert.equal(assessmentRequests.length, 0);
        const healthy = await lookup(draft, open);
        await damage(draft, true);
        const recovered = await lookup(draft, refresh);
        assert.deepEqual(recovered, healthy);
        await back(draft);
        checkRequests([draft, draft, draft, draft]);
        return;
      }
      await navigate("review");
      assert.equal(assessmentRequests.length, 0);
      const reason = registeredWorkspace ? null : "unregistered_workspace";
      const first = await lookup(review, open, reason);
      if (registeredWorkspace && adjacentReview) {
        await lookup(
          adjacentReview,
          () => select.selectOption(adjacentReview.version_id),
          "exact_selection_unavailable",
          true,
        );
        const reopened = await lookup(review, () =>
          select.selectOption(review.version_id),
        );
        assert.deepEqual(reopened, first);
      }
      await back(review);
      await navigate("draft");
      const second = await lookup(draft, open, reason);
      assert.deepEqual(first.assessments, second.assessments);
      assert.deepEqual(first.accounting_records, second.accounting_records);
      if (registeredWorkspace) {
        await lookup(
          adjacent,
          () => select.selectOption(adjacent.version_id),
          "exact_selection_unavailable",
          true,
        );
        const reopened = await lookup(draft, () =>
          select.selectOption(draft.version_id),
        );
        assert.deepEqual(reopened, second);
        if (phase === "complete") await damage(draft, false);
      }
      await back(draft);
      const requested = registeredWorkspace
        ? [
            review,
            ...(adjacentReview ? [adjacentReview, review] : []),
            draft,
            adjacent,
            draft,
            ...(phase === "complete" ? [draft] : []),
          ]
        : [review, draft];
      checkRequests(requested);
    } finally {
      await context.close();
    }

    function refresh() {
      return assessment
        .getByRole("button", { name: "Refresh assessment" })
        .click();
    }
    async function damage(selection, restore) {
      const target = path.join(scratch, "publication", "delivery.json");
      assert.equal(await realpath(target), target);
      const bytes = await readFile(target, "utf8");
      const input = usage.input_tokens;
      const changed = bytes.replace(
        new RegExp('("input_tokens"\\s*:\\s*)' + input + "\\b"),
        (_, prefix) => prefix + (input + 1),
      );
      assert.notEqual(bytes, changed);
      assert.equal(JSON.parse(changed).usage.input_tokens, input + 1);
      try {
        await writeFile(target, changed);
        await lookup(selection, refresh, "publication_member_changed", true);
        if (restore) {
          await back(selection);
          await lookup(selection, open, "publication_member_changed");
        }
      } finally {
        if (restore) await writeFile(target, bytes);
      }
    }
    function checkRequests(requested) {
      assert.deepEqual(
        assessmentRequests,
        requested.map(
          (s) => `/api/v1/artifact-versions/${s.version_id}/${endpoint}`,
        ),
      );
      assert.deepEqual(errors, []);
    }
  }

  try {
    if (phase !== "damage") await exercise(copied, false);
    await exercise(registered, true);
    await writeFile(
      path.join(
        scratch,
        phase === "complete" ? "browser-result.json" : phase + "-result.json",
      ),
      JSON.stringify({
        browser: "Google Chrome",
        version: browser.version(),
        delivery_id: cases.delivery,
        usage,
        observations,
        provider_calls: 0,
      }),
    );
  } finally {
    await browser.close();
  }
}

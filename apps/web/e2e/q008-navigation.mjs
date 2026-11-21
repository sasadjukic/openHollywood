import assert from "node:assert/strict";
import { readFile, realpath, writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright-core";

const [registered, copied, scratch] = process.argv.slice(2);
const root = await realpath("../../data/diagnostics/q008-browser-2026-11-21");
assert.equal(path.dirname(await realpath(scratch)), root);
assert.match(path.basename(scratch), /^replay-[\w-]+$/);
const cases = JSON.parse(
  await readFile(path.join(scratch, "cases.json"), "utf8"),
);
const { review, draft, adjacent } = cases.selections;
const usage = {
  input_tokens: 58894,
  output_tokens: 345,
  reasoning_tokens: 165,
  cached_input_tokens: 0,
};
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
    if (url.pathname.endsWith("/q008-assessment")) {
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
  const select = inspector.getByRole("combobox", { name: "Artifact version" });
  const assessment = inspector.getByRole("region", { name: "Q008 assessment" });
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
      "58,894 input · 345 output",
      /Operator score ·|Preflight input count ·|Citations ·/,
    ]) {
      assert.equal(
        await assessment.getByText(text, { exact: true }).count(),
        0,
      );
    }
  }

  async function lookup(selection, act, reason = null, pending = false) {
    const view = await request(selection, "q008-assessment", act, pending);
    assert.equal(view.lookups.length, 1);
    const [row] = view.lookups;
    assert.deepEqual(row.selection, selection);
    assert.equal(row.reason, reason);
    if (reason) {
      assert.equal(row.status, "unavailable");
      assert.equal(row.delivery_id, null);
      assert.deepEqual(view.assessments, []);
      assert.deepEqual(view.accounting_records, []);
      assert.equal(view.generation_totals, null);
      const messages = {
        exact_selection_unavailable: "Assessment unavailable for this version.",
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
      assert.equal(row.delivery_id, cases.delivery);
      assert.equal(view.assessments.length, 1);
      assert.equal(view.accounting_records.length, 1);
      assert.equal(view.accounting_records[0].delivery_id, cases.delivery);
      assert.deepEqual(view.accounting_records[0].request_selection, review);
      assert.deepEqual(view.accounting_records[0].generation_usage, usage);
      assert.deepEqual(view.generation_totals, usage);
      await assessment.getByText(cases.claim, { exact: true }).waitFor();
      await assertInViewport(
        assessment.getByRole("heading", { name: "Q008 assessment" }),
      );
      await assessment
        .getByText("58,894 input · 345 output", { exact: true })
        .waitFor();
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
    assert.equal(result.reason, "unregistered_workspace");
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
    });
  }
  try {
    await page.goto(origin);
    await nav
      .getByRole("button")
      .filter({ has: page.getByText(cases.project, { exact: true }) })
      .click();
    await navigate("review");
    assert.equal(assessmentRequests.length, 0);
    const reason = registeredWorkspace ? null : "unregistered_workspace";
    const first = await lookup(review, open, reason);
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
      await lookup(draft, () => select.selectOption(draft.version_id));
      const target = path.join(scratch, "publication", "delivery.json");
      assert.equal(await realpath(target), target);
      const bytes = await readFile(target, "utf8");
      const changed = bytes.replace(
        /("input_tokens"\s*:\s*)58894\b/,
        (_, prefix) => prefix + "58895",
      );
      assert.notEqual(bytes, changed);
      assert.equal(JSON.parse(changed).usage.input_tokens, 58895);
      await writeFile(target, changed);
      await lookup(
        draft,
        () =>
          assessment
            .getByRole("button", { name: "Refresh assessment" })
            .click(),
        "publication_member_changed",
        true,
      );
    }
    await back(draft);
    const requested = registeredWorkspace
      ? [review, draft, adjacent, draft, draft]
      : [review, draft];
    assert.deepEqual(
      assessmentRequests,
      requested.map(
        (s) => `/api/v1/artifact-versions/${s.version_id}/q008-assessment`,
      ),
    );
    assert.deepEqual(errors, []);
  } finally {
    await context.close();
  }
}

try {
  await exercise(copied, false);
  await exercise(registered, true);
  await writeFile(
    path.join(scratch, "browser-result.json"),
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

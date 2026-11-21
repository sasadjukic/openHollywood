import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { chromium } from "playwright-core";

const [mode, origin] = process.argv.slice(2);
assert.ok(["q008", "ordinary"].includes(mode));
assert.equal(new URL(origin).hostname, "127.0.0.1");
const archive = mode === "q008";
const diagnostics = "../../data/diagnostics";
const saved = JSON.parse(
  await readFile(
    `${diagnostics}/assessment-provenance-inspector-2026-11-19/selection-01.json`,
    "utf8",
  ),
);
const q008 = async (name) =>
  JSON.parse(
    await readFile(
      `${diagnostics}/q008-downstream-2026-11-20/${name}.json`,
      "utf8",
    ),
  );
const browser = await chromium.launch({ channel: "chrome", headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1500, height: 960 },
    serviceWorkers: "block",
  });
  page.setDefaultTimeout(45000);
  const problems = [];
  const requests = [];
  page.on("pageerror", (e) => problems.push(e.message));
  await page.route("**/*", async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    if (url.origin !== origin || req.method() !== "GET") {
      problems.push("Unexpected method or origin");
      return route.abort();
    }
    if (url.pathname.endsWith("/q008-assessment")) requests.push(url.pathname);
    return route.continue();
  });
  const nav = page.getByRole("navigation", {
    name: "Story projects and artifacts",
  });
  const inspector = page.getByRole("complementary", {
    name: "Artifact inspector",
  });
  const provenance = inspector.getByRole("region", {
    name: "Review provenance",
  });
  const assessment = inspector.getByRole("region", { name: "Q008 assessment" });
  const select = inspector.getByRole("combobox", { name: "Artifact version" });
  const results = [];

  async function readResult(selection, endpoint, click) {
    const [resp] = await Promise.all([
      page.waitForResponse(
        (r) =>
          new URL(r.url()).pathname ===
          `/api/v1/artifact-versions/${selection.version_id}/${endpoint}`,
      ),
      click(),
    ]);
    assert.equal(resp.status(), 200);
    assert.equal(await resp.headerValue("cache-control"), "no-store");
    const { version_id, ...query } = selection;
    assert.deepEqual(
      Object.fromEntries(new URL(resp.url()).searchParams),
      query,
    );
    return resp.json();
  }
  async function selectArtifact(title, type, selection) {
    await nav
      .getByRole("button")
      .filter({ has: page.getByText(title, { exact: true }) })
      .filter({ hasText: type })
      .click();
    await select.selectOption(selection.version_id);
    assert.equal(await select.inputValue(), selection.version_id);
    await provenance
      .getByText(
        archive ? "Provenance unavailable" : "Version relationship verified",
        { exact: true },
      )
      .waitFor();
  }
  async function expectVerified() {
    await provenance
      .getByText("Version relationship verified", { exact: true })
      .waitFor();
    await provenance
      .getByText(saved.relationship.review_version_id, { exact: true })
      .waitFor();
    await provenance
      .getByText(saved.relationship.draft_version_id, { exact: true })
      .waitFor();
  }
  await page.goto(origin);
  await page.getByText("Read-only archive", { exact: true }).waitFor();
  const project = archive
    ? "Benchmark OH-V01-001 — cloud"
    : "The Bone Labyrinth";
  await nav
    .getByRole("button")
    .filter({ has: page.getByText(project, { exact: true }) })
    .click();
  assert.equal(
    await page
      .getByRole("button", { name: /New story|Delete story|Model setup/ })
      .count(),
    0,
  );
  if (archive) {
    const review = await q008("original_review");
    const draft = await q008("reviewed_draft");
    const receipts = [];
    for (const [selection, title, type] of [
      [review, "Critique — scene_1", "Critique"],
      [draft, "The Pristine Lure", "Scene Draft"],
    ]) {
      await selectArtifact(title, type, selection);
      if (selection === draft)
        assert.deepEqual(
          await select
            .locator("option")
            .evaluateAll((options) => options.map((o) => o.value)),
          [draft.version_id],
        );
      const view = await readResult(selection, "q008-assessment", () =>
        inspector
          .getByRole("button", { name: "View saved assessment" })
          .click(),
      );
      assert.deepEqual(view.lookups[0].selection, selection);
      assert.equal(view.lookups[0].status, "available");
      assert.equal(view.assessments.length, 1);
      assert.equal(view.accounting_records.length, 1);
      assert.deepEqual(view.accounting_records[0].request_selection, review);
      await assessment
        .getByText("58,894 input · 345 output", { exact: true })
        .waitFor();
      receipts.push(view.accounting_records[0]);
      results.push({
        version: selection.version_id,
        status: "available",
        delivery_id: view.lookups[0].delivery_id,
      });
    }
    assert.deepEqual(receipts[0], receipts[1]);
  } else {
    const { selection } = saved;
    await selectArtifact("Critique — s1", "Critique", selection);
    await expectVerified();
    const view = await readResult(selection, "q008-assessment", () =>
      inspector.getByRole("button", { name: "View saved assessment" }).click(),
    );
    assert.deepEqual(view.lookups[0].selection, selection);
    assert.equal(view.lookups[0].reason, "unregistered_workspace");
    assert.deepEqual(view.assessments, []);
    assert.deepEqual(view.accounting_records, []);
    assert.equal(view.generation_totals, null);
    await assessment
      .getByText("Assessment unavailable in this workspace.", { exact: true })
      .waitFor();
    assert.equal(await provenance.count(), 0);
    const restored = await readResult(selection, "provenance", () =>
      inspector.getByRole("button", { name: "Return to provenance" }).click(),
    );
    assert.deepEqual(restored.selection, selection);
    assert.equal(restored.status, "identity_verified");
    assert.equal(restored.reason, "exact_registered_identity");
    for (const key of [
      "review_version_id",
      "draft_version_id",
      "review_invocation_id",
      "source_registration",
    ])
      assert.equal(restored.relationship[key], saved.relationship[key]);
    await expectVerified();
    assert.equal(await assessment.count(), 0);
    assert.equal(
      await inspector
        .getByText("Shared generation usage", { exact: true })
        .count(),
      0,
    );
    results.push({
      version: selection.version_id,
      assessment: view.lookups[0].reason,
      restored: restored.reason,
      draft_version: restored.relationship.draft_version_id,
    });
  }
  assert.equal(requests.length, archive ? 2 : 1);
  assert.deepEqual(problems, []);
  console.log(
    JSON.stringify({ browser: browser.version(), workspace: mode, results }),
  );
} finally {
  await browser.close();
}

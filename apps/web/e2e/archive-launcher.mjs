import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { chromium } from "playwright-core";

const [mode, origin, claimId = mode === "q013" ? "Q013" : "Q008"] =
  process.argv.slice(2);
const archives = {
  q008: {
    directory: "q008-downstream-2026-11-20",
    project: "Benchmark OH-V01-001 — cloud",
    draftTitle: "The Pristine Lure",
    critiqueVersion: 2,
    usage: {
      input_tokens: 58894,
      output_tokens: 345,
      reasoning_tokens: 165,
      cached_input_tokens: 0,
    },
  },
  q013: {
    directory: "q013-downstream-2026-11-21",
    project: "Benchmark OH-V01-002 — cloud",
    draftTitle: "The Impossible Card",
    critiqueVersion: 3,
    usage: {
      input_tokens: 62835,
      output_tokens: 427,
      reasoning_tokens: 255,
      cached_input_tokens: 0,
    },
  },
};
assert.ok(["q008", "q013", "ordinary"].includes(mode));
assert.ok(
  ["Q008", "Q013"].includes(claimId) &&
    (mode === "ordinary" || mode === claimId.toLowerCase()),
);
const endpoint = claimId.toLowerCase() + "-assessment";
assert.equal(new URL(origin).hostname, "127.0.0.1");
const archive = archives[mode];
const diagnostics = "../../data/diagnostics";
const fixture = async (file) =>
  JSON.parse(await readFile(`${diagnostics}/${file}.json`, "utf8"));
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
    if (url.pathname.endsWith("-assessment")) requests.push(url.pathname);
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
  const assessment = inspector.getByRole("region", {
    name: claimId + " assessment",
  });
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
  async function expectVerified(saved) {
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
  const project = archive?.project ?? "The Bone Labyrinth";
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
    const review = await fixture(archive.directory + "/original_review");
    const draft = await fixture(archive.directory + "/reviewed_draft");
    const receipts = [];
    const assessments = [];
    for (const [selection, title, type, number] of [
      [review, "Critique — scene_1", "Critique", archive.critiqueVersion],
      [draft, archive.draftTitle, "Scene Draft", 1],
    ]) {
      await selectArtifact(title, type, selection);
      const label = await select.locator("option:checked").textContent();
      assert.equal(label.split(" · ")[0], "v" + number);
      if (mode === "q008" && selection === draft)
        assert.deepEqual(
          await select
            .locator("option")
            .evaluateAll((options) => options.map((o) => o.value)),
          [draft.version_id],
        );
      const view = await readResult(selection, endpoint, () =>
        inspector
          .getByRole("button", { name: "View saved assessment" })
          .click(),
      );
      assert.deepEqual(view.lookups[0].selection, selection);
      assert.equal(view.contract, mode + "-inspector-view-1");
      assert.equal(view.lookups.length, 1);
      assert.equal(view.lookups[0].status, "available");
      assert.equal(view.lookups[0].claim_id, claimId);
      assert.equal(view.assessments.length, 1);
      assert.equal(view.accounting_records.length, 1);
      const [record] = view.accounting_records;
      const [assessmentRow] = view.assessments;
      assert.ok(record.delivery_id.startsWith(mode + "-"));
      assert.equal(record.delivery_id, view.lookups[0].delivery_id);
      assert.equal(record.delivery_id, assessmentRow.delivery_id);
      assert.deepEqual(record.request_selection, review);
      assert.deepEqual(record.generation_usage, archive.usage);
      assert.deepEqual(view.generation_totals, archive.usage);
      await assessment
        .getByText(assessmentRow.claim, { exact: true })
        .waitFor();
      const usageText =
        archive.usage.input_tokens.toLocaleString("en-US") +
        " input · " +
        archive.usage.output_tokens +
        " output";
      await assessment.getByText(usageText, { exact: true }).waitFor();
      if (mode === "q013") {
        assert.equal(assessmentRow.model_assessment.support, "supported");
        assert.deepEqual(assessmentRow.model_assessment.evidence, ["E0920"]);
        assert.deepEqual(assessmentRow.operator_score, {
          claim_correctness: "pass",
          evidence_coverage: "pass",
        });
        for (const text of [
          "Citations · E0920",
          "Claim correctness · pass",
          "Evidence coverage · pass",
        ])
          await assessment.getByText(text, { exact: true }).waitFor();
      }
      receipts.push(record);
      assessments.push(assessmentRow);
      results.push({
        version: selection.version_id,
        version_number: number,
        status: "available",
        delivery_id: view.lookups[0].delivery_id,
      });
    }
    assert.deepEqual(receipts[0], receipts[1]);
    assert.deepEqual(assessments[0], assessments[1]);
  } else {
    const saved = await fixture(
      "assessment-provenance-inspector-2026-11-19/selection-01",
    );
    const { selection } = saved;
    await selectArtifact("Critique — s1", "Critique", selection);
    await expectVerified(saved);
    const view = await readResult(selection, endpoint, () =>
      inspector.getByRole("button", { name: "View saved assessment" }).click(),
    );
    assert.deepEqual(view.lookups[0].selection, selection);
    assert.equal(view.lookups[0].reason, "unregistered_workspace");
    assert.equal(view.contract, claimId.toLowerCase() + "-inspector-view-1");
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
    await expectVerified(saved);
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
    JSON.stringify({
      browser: browser.version(),
      workspace: mode,
      results,
      generation_usage: archive?.usage,
    }),
  );
} finally {
  await browser.close();
}

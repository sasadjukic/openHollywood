/// <reference types="node" />
import { execFile } from "node:child_process";
import { readFileSync } from "node:fs";
import { cp, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { promisify } from "node:util";
import type {
  ArtifactSelection,
  ArtifactVersionDetail,
} from "@open-hollywood/contracts";

import type { Q008Inventory } from "../components/Q008Assessment";
import { selectionForReview } from "../components/artifactSelection";

type Version = "review" | "draft" | "adjacent";
export interface InspectorCases {
  project: string;
  details: Record<Version, ArtifactVersionDetail>;
  views: Record<Version | "damaged", Q008Inventory>;
}

function portableCases(): InspectorCases {
  const project = "fixture-project";
  function detail(key: Version): ArtifactVersionDetail {
    const isReview = key === "review";
    const versions = (isReview ? ["review"] : ["adjacent", "draft"]).map(
      (id) => ({
        id,
        parent_version_id: id === "adjacent" ? "draft" : null,
        version_number: id === "adjacent" ? 2 : 1,
        schema_version: "1",
        created_at: "2026-11-21T12:00:00Z",
        change_summary: null,
        specialist_role: null,
        provider: null,
        model_identifier: null,
      }),
    );
    const selected = versions.find((v) => v.id === key);
    if (!selected) throw new Error("Missing fixture version");
    return {
      artifact: {
        id: isReview ? "fixture-critique" : "fixture-draft",
        title: key,
        artifact_key: isReview ? "review" : "scene",
        artifact_type: isReview ? "critique" : "scene_draft",
        active_version_id: isReview ? "review" : "draft",
        status: "draft",
        versions,
      },
      selected_version: selected,
      content_sha256: (isReview ? "a" : "b").repeat(64),
      content: {
        text: isReview ? "A factual review." : "She opened the gate.",
      },
      evaluations: [],
    };
  }
  const details = {
    review: detail("review"),
    draft: detail("draft"),
    adjacent: detail("adjacent"),
  };
  const selection = (key: Version) =>
    selectionForReview({ projectId: project, detail: details[key] });
  const delivery = "fixture-delivery";
  const usage = {
    input_tokens: 120,
    output_tokens: 23,
    reasoning_tokens: 7,
    cached_input_tokens: 0,
  };
  function available(selected: ArtifactSelection): Q008Inventory {
    return {
      contract: "q008-consumer-lookup-1",
      lookups: [
        {
          selection: selected,
          status: "available",
          reason: null,
          delivery_id: delivery,
          claim_id: "Q008",
        },
      ],
      assessments: [
        {
          delivery_id: delivery,
          claim_id: "Q008",
          claim: "The gate opens.",
          model: "fixture-assessor",
          model_assessment: {
            support: "supported",
            evidence: ["E01", "E02"],
            reason: "The ending shows the action.",
          },
          operator_score: { passed_judgments: 3, possible_judgments: 3 },
          application_status: {
            semantic_support: "unassessed",
            evidence_adequacy: "unassessed",
            edit_necessity: "unassessed",
            craft: "unassessed",
            production_attachment_eligible: false,
            writer_dispatch_authorized: false,
          },
        },
      ],
      accounting_records: [
        {
          delivery_id: delivery,
          request_selection: selection("review"),
          generation_usage: usage,
          preflight_input_count: 120,
          actual_billed_cost: null,
        },
      ],
      generation_totals: usage,
    };
  }
  function unavailable(
    selected: ArtifactSelection,
    reason: string,
  ): Q008Inventory {
    return {
      contract: "q008-consumer-lookup-1",
      lookups: [
        {
          selection: selected,
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
  return {
    project,
    details,
    views: {
      review: available(selection("review")),
      draft: available(selection("draft")),
      adjacent: unavailable(
        selection("adjacent"),
        "exact_selection_unavailable",
      ),
      damaged: unavailable(selection("draft"), "publication_member_changed"),
    },
  };
}

export function inspectorCases(): InspectorCases {
  if (!savedReplay) return portableCases();
  const path = resolve(
    process.cwd(),
    "../../data/diagnostics/q008-inspector-2026-11-21/inspector-replay.json",
  );
  return JSON.parse(readFileSync(path, "utf8")) as InspectorCases;
}
export const savedReplay = process.env.OH_Q008_INSPECTOR_REPLAY === "1";

// The path override exists only in the test subprocess, for its disposable copy.
const readCopy = `
import sys
from pathlib import Path
from unittest.mock import patch
from scripts import lookup_q008_completion as consumer
from open_hollywood_api.services.production_association_records import ArtifactSelection
with patch.object(consumer, "PUBLICATION", Path(sys.argv[1])):
    selection = ArtifactSelection.model_validate_json(sys.argv[2])
    print(consumer.lookup((selection,)).model_dump_json())
`;

export async function withPublicationCopy(
  exercise: (
    lookup: (s: ArtifactSelection) => Promise<Q008Inventory>,
    damage: () => Promise<void>,
  ) => Promise<void>,
) {
  const root = resolve(process.cwd(), "../..");
  const python = join(
    root,
    ".venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );
  const scratch = await mkdtemp(join(tmpdir(), "oh-q008-inspector-"));
  const copy = join(scratch, "publication");
  try {
    await cp(
      join(root, "data/diagnostics/q008-publication-2026-11-21/critique-first"),
      copy,
      { recursive: true },
    );
    await exercise(
      async (selection) => {
        const { stdout } = await promisify(execFile)(
          python,
          ["-X", "utf8", "-c", readCopy, copy, JSON.stringify(selection)],
          { cwd: root, timeout: 60000 },
        );
        return JSON.parse(stdout) as Q008Inventory;
      },
      async () => {
        const path = join(copy, "delivery.json");
        const before = await readFile(path, "utf8");
        const changed = before.replace(
          /("input_tokens"\s*:\s*)58894\b/,
          (_, prefix: string) => prefix + "58895",
        );
        const after = JSON.parse(changed) as {
          usage: { input_tokens: number };
        };
        if (changed === before || after.usage.input_tokens !== 58895)
          throw new Error("Failed to alter the copied usage");
        await writeFile(path, changed, "utf8");
      },
    );
  } finally {
    await rm(scratch, { recursive: true, force: true });
  }
}

import type {
  ArtifactSelection,
  Q008InspectorView,
} from "@open-hollywood/contracts";
import { fetchQ008Assessment } from "../api";
import type { ReviewPanelProps } from "./artifactSelection";
import { SavedAssessment } from "./SavedAssessment";

export type Q008Inventory = Q008InspectorView;
export type Q008Lookup = (
  selection: ArtifactSelection,
  signal: AbortSignal,
) => Promise<Q008Inventory>;

export function Q008Assessment({
  lookup = fetchQ008Assessment,
  ...props
}: ReviewPanelProps & { lookup?: Q008Lookup }) {
  return <SavedAssessment {...props} claimId="Q008" lookup={lookup} />;
}

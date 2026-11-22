import type { ArtifactVersionDetail } from "@open-hollywood/contracts";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ComponentType } from "react";
import { ArtifactInspector } from "../components/ArtifactInspector";
import type { ReviewPanelProps } from "../components/artifactSelection";

export function mountInspector(
  Panel: ComponentType<ReviewPanelProps>,
  project: string,
  details: Record<string, ArtifactVersionDetail>,
  initial: ArtifactVersionDetail,
) {
  const client = new QueryClient();
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

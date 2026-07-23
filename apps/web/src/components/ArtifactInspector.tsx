import type {
  ArtifactVersionDetail,
  WorkspaceArtifact,
} from "@open-hollywood/contracts";

interface ArtifactInspectorProps {
  artifact: WorkspaceArtifact | null;
  detail: ArtifactVersionDetail | undefined;
  isLoading: boolean;
  isOpen: boolean;
  onClose: () => void;
  onSelectVersion: (versionId: string) => void;
  selectedVersionId: string | null;
}

export function ArtifactInspector({
  artifact,
  detail,
  isLoading,
  isOpen,
  onClose,
  onSelectVersion,
  selectedVersionId,
}: ArtifactInspectorProps) {
  return (
    <aside
      className={`artifact-inspector ${isOpen ? "artifact-inspector--open" : ""}`}
      aria-label="Artifact inspector"
    >
      <header className="inspector-header">
        <div>
          <p className="panel-label">Artifact inspector</p>
          <h2>{artifact?.title ?? "Select an artifact"}</h2>
        </div>
        <button
          className="icon-button inspector-close"
          type="button"
          onClick={onClose}
          aria-label="Close artifact inspector"
        >
          ×
        </button>
      </header>

      {!artifact && (
        <div className="inspector-empty">
          <span aria-hidden="true">◫</span>
          <p>Choose an artifact to inspect its active version and lineage.</p>
        </div>
      )}

      {artifact && (
        <>
          <div className="artifact-toolbar">
            <span
              className={`artifact-status artifact-status--${artifact.status}`}
            >
              {artifact.status}
            </span>
            <label>
              <span>Version</span>
              <select
                value={selectedVersionId ?? ""}
                onChange={(event) => {
                  onSelectVersion(event.target.value);
                }}
              >
                {artifact.versions.map((version) => (
                  <option key={version.id} value={version.id}>
                    v{version.version_number}
                    {version.id === artifact.active_version_id
                      ? " · active"
                      : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="inspector-scroll">
            {isLoading && <ArtifactSkeleton />}
            {!isLoading && detail && (
              <>
                <ArtifactContent
                  artifactType={artifact.artifact_type}
                  content={detail.content}
                />
                <VersionContext detail={detail} />
              </>
            )}
          </div>
        </>
      )}
    </aside>
  );
}

function ArtifactSkeleton() {
  return (
    <div className="artifact-skeleton" aria-label="Loading artifact">
      <span />
      <span />
      <span />
      <span />
    </div>
  );
}

function ArtifactContent({
  artifactType,
  content,
}: {
  artifactType: string;
  content: Record<string, unknown>;
}) {
  if (artifactType === "story_blueprint") {
    return <BlueprintContent content={content} />;
  }

  return (
    <article className="structured-artifact">
      {Object.entries(content).map(([key, value]) => (
        <StructuredSection key={key} label={key} value={value} />
      ))}
    </article>
  );
}

function BlueprintContent({ content }: { content: Record<string, unknown> }) {
  const brief = asRecord(content.creative_brief);
  const characters = asRecordArray(content.characters);
  const scenes = asRecordArray(content.scene_plans);
  const risks = asStringArray(content.potential_risks);
  const unresolved = asStringArray(content.unresolved_decisions);
  const maturity = readString(brief.maturity);

  return (
    <article className="blueprint">
      <section className="blueprint-lead">
        <p className="eyebrow">Logline</p>
        <h3>{readString(content.logline, "Untitled story direction")}</h3>
        <div className="chip-row">
          {asStringArray(brief.genres).map((genre) => (
            <span key={genre}>{genre}</span>
          ))}
          {asStringArray(brief.tone).map((tone) => (
            <span key={tone}>{tone}</span>
          ))}
          {maturity && <span>{humanize(maturity)}</span>}
        </div>
      </section>

      <BlueprintSection
        label="Thematic thesis"
        value={readString(content.thematic_thesis)}
      />
      <BlueprintSection
        label="World"
        value={readString(content.world_summary)}
      />
      <BlueprintSection
        label="Central conflict"
        value={readString(content.central_conflict)}
      />
      <BlueprintSection
        label="Story arc"
        value={readString(content.story_arc)}
      />

      {characters.length > 0 && (
        <section className="blueprint-section">
          <div className="section-heading">
            <p className="eyebrow">Characters</p>
            <span>{characters.length}</span>
          </div>
          <div className="character-list">
            {characters.map((character, index) => {
              const arc = readString(character.arc);
              return (
                <article key={readString(character.id, String(index))}>
                  <h4>{readString(character.name, "Unnamed character")}</h4>
                  <p className="character-role">
                    {readString(character.story_role)}
                  </p>
                  <p>{readString(character.description)}</p>
                  {arc && (
                    <dl>
                      <dt>Arc</dt>
                      <dd>{arc}</dd>
                    </dl>
                  )}
                </article>
              );
            })}
          </div>
        </section>
      )}

      {scenes.length > 0 && (
        <section className="blueprint-section">
          <div className="section-heading">
            <p className="eyebrow">Scene plan</p>
            <span>{scenes.length} scenes</span>
          </div>
          <ol className="scene-list">
            {scenes.map((scene, index) => (
              <li key={readString(scene.id, String(index))}>
                <span>{readNumber(scene.scene_number, index + 1)}</span>
                <div>
                  <h4>
                    {readString(scene.title, `Scene ${String(index + 1)}`)}
                  </h4>
                  <p>
                    {readString(
                      scene.summary ?? scene.scene_goal,
                      "Scene details are being integrated.",
                    )}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      )}

      <BlueprintSection
        label="Proposed ending"
        value={readString(content.proposed_ending)}
        featured
      />
      <BlueprintSection
        label="Voice & style"
        value={readString(content.voice_and_style_guide)}
      />

      {(risks.length > 0 || unresolved.length > 0) && (
        <section className="blueprint-section risk-section">
          <p className="eyebrow">Review notes</p>
          <ul>
            {[...risks, ...unresolved].map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </section>
      )}
    </article>
  );
}

function BlueprintSection({
  featured = false,
  label,
  value,
}: {
  featured?: boolean;
  label: string;
  value: string;
}) {
  if (!value) {
    return null;
  }
  return (
    <section
      className={`blueprint-section ${featured ? "blueprint-section--featured" : ""}`}
    >
      <p className="eyebrow">{label}</p>
      <p>{value}</p>
    </section>
  );
}

function StructuredSection({
  label,
  value,
}: {
  label: string;
  value: unknown;
}) {
  if (value === null || value === undefined) {
    return null;
  }
  return (
    <section className="blueprint-section">
      <p className="eyebrow">{humanize(label)}</p>
      {Array.isArray(value) ? (
        <ul>
          {value.map((item, index) => (
            <li key={`${label}-${String(index)}`}>
              {displayValue(item, true)}
            </li>
          ))}
        </ul>
      ) : typeof value === "object" ? (
        <dl className="structured-fields">
          {Object.entries(value as Record<string, unknown>).map(
            ([field, fieldValue]) => (
              <div key={field}>
                <dt>{humanize(field)}</dt>
                <dd>{displayValue(fieldValue)}</dd>
              </div>
            ),
          )}
        </dl>
      ) : (
        <p>{displayValue(value)}</p>
      )}
    </section>
  );
}

function VersionContext({ detail }: { detail: ArtifactVersionDetail }) {
  const version = detail.selected_version;
  const evaluation = detail.evaluations[0];
  return (
    <section className="version-context">
      <div className="section-heading">
        <p className="eyebrow">Version history</p>
        <span>v{String(version.version_number)}</span>
      </div>
      <p className="change-summary">
        {version.change_summary ?? "Immutable artifact version"}
      </p>
      <dl className="provenance-grid">
        <div>
          <dt>Created by</dt>
          <dd>{humanize(version.specialist_role ?? "workflow")}</dd>
        </div>
        <div>
          <dt>Model</dt>
          <dd>{version.model_identifier ?? "Deterministic step"}</dd>
        </div>
        <div>
          <dt>Created</dt>
          <dd>{formatDate(version.created_at)}</dd>
        </div>
        <div>
          <dt>Parent</dt>
          <dd>{version.parent_version_id ? "Linked version" : "Original"}</dd>
        </div>
      </dl>

      {evaluation && (
        <div className="evaluation-card">
          <div>
            <p className="eyebrow">Evaluation</p>
            <strong>
              {evaluation.weighted_score
                ? `${evaluation.weighted_score}/100`
                : "Scored"}
            </strong>
          </div>
          <p>{evaluation.summary ?? humanize(evaluation.rubric_name)}</p>
        </div>
      )}
    </section>
  );
}

function asRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.map(asRecord) : [];
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string")
    : [];
}

function readString(value: unknown, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function readNumber(value: unknown, fallback: number) {
  return typeof value === "number" ? value : fallback;
}

function displayValue(value: unknown, pretty = false): string {
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  if (value === null || value === undefined) {
    return "";
  }
  return JSON.stringify(value, null, pretty ? 2 : 0);
}

function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

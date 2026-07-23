import type {
  CatalogModel,
  ModelCatalog,
  ModelDeployment,
  ModelProfileSummary,
  ModelSelectionInput,
} from "@open-hollywood/contracts";
import { useState } from "react";

interface ModelSettingsProps {
  catalog: ModelCatalog | undefined;
  error: string | null;
  isCatalogLoading: boolean;
  isOpen: boolean;
  isProfilesLoading: boolean;
  isSaving: boolean;
  onClose: () => void;
  onSaveAndActivate: (
    profile: ModelProfileSummary,
    localModel: ModelSelectionInput | null,
    cloudModel: ModelSelectionInput | null,
  ) => void;
  profiles: ModelProfileSummary[];
}

export function ModelSettings({
  catalog,
  error,
  isCatalogLoading,
  isOpen,
  isProfilesLoading,
  isSaving,
  onClose,
  onSaveAndActivate,
  profiles,
}: ModelSettingsProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="settings-layer">
      <button
        className="settings-backdrop"
        type="button"
        aria-label="Close model settings"
        onClick={onClose}
      />
      <section
        className="model-settings"
        role="dialog"
        aria-modal="true"
        aria-labelledby="model-settings-title"
      >
        <header className="settings-header">
          <div>
            <p className="eyebrow">Inference profile</p>
            <h2 id="model-settings-title">Choose how the studio thinks.</h2>
            <p>
              Presets route registered specialists to exact models without
              storing provider credentials.
            </p>
          </div>
          <button
            className="icon-button"
            type="button"
            onClick={onClose}
            aria-label="Close model settings"
          >
            ×
          </button>
        </header>

        <div className="catalog-strip">
          <div>
            <span
              className={`catalog-indicator ${
                catalog?.models.length ? "catalog-indicator--ready" : ""
              }`}
              aria-hidden="true"
            />
            <span>
              {isCatalogLoading
                ? "Discovering Ollama models…"
                : `${String(catalog?.models.length ?? 0)} models discovered`}
            </span>
          </div>
          <div className="catalog-sources">
            {catalog?.sources.map((source) => (
              <span
                className={`catalog-source catalog-source--${source.status}`}
                key={source.key}
                title={source.detail ?? source.label}
              >
                {source.label}
              </span>
            ))}
          </div>
        </div>

        {isProfilesLoading ? (
          <div className="preset-loading" aria-label="Loading model presets">
            <span />
            <span />
            <span />
          </div>
        ) : (
          <div className="preset-grid">
            {profiles.map((profile) => (
              <ProfileCard
                catalogModels={catalog?.models ?? []}
                isSaving={isSaving}
                key={`${profile.id}-${profile.updated_at}`}
                onSaveAndActivate={onSaveAndActivate}
                profile={profile}
              />
            ))}
          </div>
        )}

        {error && <p className="settings-error">{error}</p>}
        <footer className="settings-footer">
          <span>Cloud calls remain opt-in.</span>
          <span>Credentials resolve only at runtime.</span>
        </footer>
      </section>
    </div>
  );
}

function ProfileCard({
  catalogModels,
  isSaving,
  onSaveAndActivate,
  profile,
}: {
  catalogModels: CatalogModel[];
  isSaving: boolean;
  onSaveAndActivate: ModelSettingsProps["onSaveAndActivate"];
  profile: ModelProfileSummary;
}) {
  const models = mergeSelectedModels(catalogModels, profile);
  const [localKey, setLocalKey] = useState(
    profile.local_model ? modelKey(profile.local_model) : "",
  );
  const [cloudKey, setCloudKey] = useState(
    profile.cloud_model ? modelKey(profile.cloud_model) : "",
  );
  const localModel = findSelection(models, localKey);
  const cloudModel = findSelection(models, cloudKey);
  const canActivate = profile.required_deployments.every((deployment) =>
    deployment === "local" ? localModel !== null : cloudModel !== null,
  );
  const localRoles = rolesFor(profile, "local");
  const cloudRoles = rolesFor(profile, "cloud");

  return (
    <article
      className={`preset-card preset-card--${profile.mode} ${
        profile.is_default ? "preset-card--active" : ""
      }`}
    >
      <header>
        <span className="preset-glyph" aria-hidden="true">
          {profileGlyph(profile.mode)}
        </span>
        <div>
          <div className="preset-title">
            <h3>{profile.name}</h3>
            {profile.is_default && <span>Active</span>}
          </div>
          <p>{profile.description}</p>
        </div>
      </header>

      <div className="role-routing">
        {localRoles.length > 0 && (
          <RoleGroup deployment="local" roles={localRoles} />
        )}
        {cloudRoles.length > 0 && (
          <RoleGroup deployment="cloud" roles={cloudRoles} />
        )}
      </div>

      <div className="model-slots">
        {profile.required_deployments.includes("local") && (
          <ModelSelect
            deployment="local"
            models={models}
            onChange={setLocalKey}
            value={localKey}
          />
        )}
        {profile.required_deployments.includes("cloud") && (
          <ModelSelect
            deployment="cloud"
            models={models}
            onChange={setCloudKey}
            value={cloudKey}
          />
        )}
      </div>

      <button
        className="preset-action"
        type="button"
        disabled={!canActivate || isSaving}
        onClick={() => {
          onSaveAndActivate(profile, localModel, cloudModel);
        }}
      >
        {isSaving
          ? "Saving…"
          : profile.is_default
            ? "Save active preset"
            : `Use ${profile.name}`}
      </button>
      {!canActivate && (
        <small>Select every required model before using this preset.</small>
      )}
    </article>
  );
}

function ModelSelect({
  deployment,
  models,
  onChange,
  value,
}: {
  deployment: ModelDeployment;
  models: CatalogModel[];
  onChange: (value: string) => void;
  value: string;
}) {
  const options = models.filter((model) => model.deployment === deployment);
  return (
    <label className="model-select">
      <span>{deployment === "local" ? "Local model" : "Cloud model"}</span>
      <select
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
        }}
      >
        <option value="">Select a discovered model</option>
        {options.map((model) => (
          <option key={modelKey(model)} value={modelKey(model)}>
            {model.model_identifier}
            {model.parameter_size ? ` · ${model.parameter_size}` : ""}
          </option>
        ))}
      </select>
    </label>
  );
}

function RoleGroup({
  deployment,
  roles,
}: {
  deployment: ModelDeployment;
  roles: string[];
}) {
  return (
    <div>
      <span>{deployment}</span>
      <p>{roles.map(shortRole).join(" · ")}</p>
    </div>
  );
}

function rolesFor(profile: ModelProfileSummary, deployment: ModelDeployment) {
  return Object.entries(profile.role_assignments)
    .filter(([, assigned]) => assigned === deployment)
    .map(([role]) => role);
}

function mergeSelectedModels(
  catalogModels: CatalogModel[],
  profile: ModelProfileSummary,
): CatalogModel[] {
  const models = [...catalogModels];
  for (const selection of [profile.local_model, profile.cloud_model]) {
    if (
      selection &&
      !models.some((model) => modelKey(model) === modelKey(selection))
    ) {
      models.push({
        ...selection,
        digest: null,
        parameter_size: null,
        quantization_level: null,
        size_bytes: null,
      });
    }
  }
  return models;
}

function findSelection(
  models: CatalogModel[],
  key: string,
): ModelSelectionInput | null {
  const model = models.find((candidate) => modelKey(candidate) === key);
  return model
    ? {
        deployment: model.deployment,
        model_identifier: model.model_identifier,
        provider: model.provider,
      }
    : null;
}

function modelKey(model: ModelSelectionInput) {
  return `${model.provider}:${model.deployment}:${model.model_identifier}`;
}

function shortRole(role: string) {
  return role
    .replace("_architect", "")
    .replace("blueprint_", "")
    .replaceAll("_", " ");
}

function profileGlyph(mode: ModelProfileSummary["mode"]) {
  const glyphs = {
    cloud: "☁",
    hybrid: "◒",
    local: "⌂",
  };
  return glyphs[mode];
}

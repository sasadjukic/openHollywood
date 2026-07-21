import { useQuery } from "@tanstack/react-query";

import { fetchServiceStatus } from "./api";

const connectionQueryKey = ["service-status"] as const;

export function App() {
  const serviceStatus = useQuery({
    queryFn: fetchServiceStatus,
    queryKey: connectionQueryKey,
    retry: 1,
  });

  const connectionState = serviceStatus.isPending
    ? "connecting"
    : serviceStatus.isError
      ? "unavailable"
      : "connected";

  return (
    <div className="app-shell">
      <header className="topbar">
        <img
          className="brand-logo"
          src="/open_hollywood_logo_no_bg.png"
          alt="Open Hollywood"
        />
        <span className="version-label">v0.1 foundation</span>
      </header>

      <main className="welcome-layout">
        <section className="welcome-copy" aria-labelledby="welcome-heading">
          <p className="eyebrow">Local-first creative studio</p>
          <h1 id="welcome-heading">Every story starts with a spark.</h1>
          <p className="introduction">
            Open Hollywood is preparing a bounded team of creative specialists
            to turn one premise into an approved blueprint and a finished short
            story.
          </p>

          <div
            className="workflow-preview"
            aria-label="Open Hollywood workflow"
          >
            <span>Premise</span>
            <span aria-hidden="true">→</span>
            <span>Blueprint approval</span>
            <span aria-hidden="true">→</span>
            <span>Autonomous draft</span>
          </div>
        </section>

        <aside className="status-card" aria-live="polite">
          <div className="status-heading">
            <span
              className={`status-dot status-dot--${connectionState}`}
              aria-hidden="true"
            />
            <div>
              <p className="status-label">Local service</p>
              <h2>
                {connectionState === "connecting" && "Connecting…"}
                {connectionState === "unavailable" && "API unavailable"}
                {connectionState === "connected" && "API connected"}
              </h2>
            </div>
          </div>

          {serviceStatus.data && (
            <dl className="service-details">
              <div>
                <dt>Service</dt>
                <dd>{serviceStatus.data.service}</dd>
              </div>
              <div>
                <dt>Contract</dt>
                <dd>v{serviceStatus.data.api_version}</dd>
              </div>
            </dl>
          )}

          {serviceStatus.isError && (
            <div className="connection-help">
              <p>Start the FastAPI service, then try the connection again.</p>
              <button
                type="button"
                onClick={() => void serviceStatus.refetch()}
              >
                Retry connection
              </button>
            </div>
          )}
        </aside>
      </main>

      <footer className="footer-note">
        <span>Short prose fiction</span>
        <span aria-hidden="true">•</span>
        <span>Private local storage</span>
        <span aria-hidden="true">•</span>
        <span>Local, cloud, or hybrid models</span>
      </footer>
    </div>
  );
}

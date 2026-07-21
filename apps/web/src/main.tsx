import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { AppProviders } from "./providers";
import "./styles.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Open Hollywood could not find its application root.");
}

createRoot(rootElement).render(
  <StrictMode>
    <AppProviders />
  </StrictMode>,
);

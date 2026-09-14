import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";

import App from "./App.jsx";
import EdgeLab from "./EdgeLab.jsx";


const params =
  new URLSearchParams(
    window.location.search
  );

const edgeLabPreview =
  params.get(
    "edge-lab"
  ) === "1";


createRoot(
  document.getElementById(
    "root"
  )
).render(
  <StrictMode>
    {edgeLabPreview ? (
      <main
        style={{
          minHeight: "100vh",
          padding: "24px",
          background:
            "#031018",
        }}
      >
        <EdgeLab language="tr" />
      </main>
    ) : (
      <App />
    )}
  </StrictMode>
);


// Auto-detects API base URL. When the FastAPI server serves the frontend
// itself (production / Render), API and frontend share the same origin.
// When opened standalone (e.g. via Live Server on a different port during
// development), point this at your local backend.
const CONFIG = {
  API_BASE: (() => {
    const { protocol, hostname, port } = window.location;
    // If served from the FastAPI app itself (port 8000 typically), same origin.
    if (port === "8000" || port === "" || port === "80" || port === "443") {
      return `${protocol}//${hostname}${port ? ":" + port : ""}`;
    }
    // Otherwise assume local dev backend on 8000.
    return `${protocol}//${hostname}:8000`;
  })(),
};

# BHID React/Vite Dedicated Frontend Package

Dedicated localhost web dashboard for BHID v1.0 built with React, Vite, TypeScript, and TailwindCSS.

---

## Architecture

- **Dashboard (`/`)**: Real-time spatiotemporal telemetry, crowd density chart, risk level indicator, active hazard events.
- **Sessions (`/sessions`)**: Recorded operational session registry table.
- **Replay (`/replay`)**: Deterministic historical playback controls and timeline navigation.
- **Reports (`/reports`)**: Operational KPI summaries, density/flow trends, Markdown report renderer.
- **Validation (`/validation`)**: Read-only system readiness audit and component status.

---

## Development Workflow

```bash
# Install frontend dependencies
npm install

# Launch Vite dev server
npm run dev
```

- **Localhost UI**: `http://localhost:5173`
- **FastAPI Proxy**: Proxy configured in `vite.config.ts` to `http://127.0.0.1:8000`.

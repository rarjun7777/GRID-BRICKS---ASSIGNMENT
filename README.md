# Winddesk

A React and Python pilot for a UK utility’s day-ahead purchasing team. Inspect the wind forecasts available at a January 2026 decision cutoff, then compare them with actual generation and quantify error.

**Deployed application:** https://q7m4x9p2.vercel.app/ (public reviewer access enabled).

**Status:** deployed to Vercel and published in the public GitHub repository at https://github.com/rarjun7777/GRID-BRICKS---ASSIGNMENT. The unlisted demo video still needs to be recorded and uploaded. Docker configuration is included; container execution awaits CI because Docker is unavailable in the build environment.

## Start with Docker

Requires Docker with Compose:

```bash
docker compose up --build
```

Open http://localhost:8000. API documentation: http://localhost:8000/docs.
The image builds React, installs Python dependencies, and serves both from one origin as a non-root user. The bundled snapshot means startup does not depend on Elexon availability.

## Start without Docker

Requires Python 3.12+ and Node 22+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
npm ci --prefix frontend
npm run build --prefix frontend
uvicorn app:app --host 0.0.0.0 --port 8000
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.
For frontend development, run `npm run dev --prefix frontend` in a second terminal; Vite proxies `/api` to port 8000.

## Product

- Decision overview: date and cutoff controls, forecast versus actual chart, daily error chart, signed bias, MAE, and coverage.
- Forecast accuracy: 31-day retrospective ledger, MAE chart, RMSE, bias, and drill-down to individual days.
- Data and methodology: source links, publication selection, hourly alignment, explicit limitations, source counts, and integrity hash.
- CSV export includes forecast publication time and lead time for every next-day hour.
- Responsive layout, accessible control labels, keyboard focus states, loading/error feedback, and retry.

No synthetic data is used. Elexon is the only generation data source. Fonts are optional Google Fonts with local sans-serif fallbacks.

## Interpretation and assumptions

1. **January means decision dates.** Decisions 1–31 January 2026 map to deliveries 2 January–1 February. All times are UTC (UK GMT in this period).
2. **09:00 UTC is an assumption.** The brief does not specify a purchase deadline. Users can change it to any minute of the decision day. This is not a claim about an exchange’s gate closure.
3. **No forecast look-ahead.** For each delivery hour, use the latest forecast publication at or before the decision cutoff. No future fallback. Publication-time equality is allowed.
4. **Alignment:** downloaded WINDFOR records are hourly; FUELHH is half-hourly. Compare each forecast to the arithmetic mean of actuals at `HH:00` and `HH:30`. The hourly forecast is treated as representative of that hour; this is an explicit approximation. Do not interpolate, duplicate hourly forecasts into two independent observations, or fill missing observations with zero.
5. **Outturn revisions:** use latest published actuals in the retrieved snapshot. This is retrospective evaluation, not a reconstruction of the actual-data revision state available on each historical date.
6. **Missing data:** unmatched hours are excluded from error metrics and remain in the coverage denominator. Zero actual generation is valid. Empty metrics return null, displayed as a dash.
7. **Scope:** national operational wind data does not represent the client’s contracted generation or electricity demand. This app does not calculate optimal trades, purchase volumes, costs, savings, or calibrated risk reserves.
8. **Retrospective statistics:** full-month results use outcomes unavailable earlier in January. They are labelled accordingly and never presented as an as-of trading signal.
9. **Snapshot window:** forecast publications 31 December–31 January; actuals 2 January–1 February. Earlier publications are not loaded. The tested default cutoff has complete coverage; missing eligible data at other cutoffs is surfaced.

## Metrics

For matched hour i, `error_i = forecast_i - actual_i`, in MW:

- MAE = mean(abs(error)).
- RMSE = sqrt(mean(error²)).
- Bias = mean(error); positive means forecast overestimation.
- Coverage = matched hours / expected hours × 100.

Energy would require integrating power over time; this dashboard reports MW, not MWh. MAPE is deliberately omitted because small/zero actuals make it unstable.

At 09:00 UTC, the bundled snapshot produces 744/744 matched hours, MAE 2,038.91 MW, RMSE 2,504.76 MW, and bias +1,747.89 MW. These are dataset-level pilot findings under the stated hourly-alignment assumption, not a universal accuracy rating.

## Data and reproducibility

```bash
python scripts/fetch_data.py
```

The standard-library downloader makes daily requests with bounded concurrency, timeouts, and retries. It collects all requests before replacing the snapshot, removes exact duplicates, and stores request URLs, retrieval timestamp, counts, and the SHA-256 of decompressed JSON in `data/provenance.json`. Conflicting records with identical target/publication keys cause analysis to fail explicitly. Restart the API after refreshing data to clear process caches.

Sources:
- https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream
- https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream

## Architecture

```text
React + SVG charts → same-origin FastAPI → pure Python analysis → compressed Elexon snapshot
                                               ↑
                                    offline download script
```

No database is needed for this fixed, small historical pilot. Parsed data is cached per Python process; dashboard responses are bounded to 256 cached date/cutoff combinations. API workers are stateless. Raw source data and provenance are versioned together. A production extension would add ingestion jobs, durable indexed storage, monitoring, and an agreed decision-time/forecast-resolution contract.

## API

| Route | Purpose |
| --- | --- |
| `GET /api/health` | Checks snapshot availability and returns status |
| `GET /api/dashboard?decision=2026-01-14&cutoff=09:00` | Selected day, full-month metrics, provenance, methodology |
| `GET /api/export?decision=2026-01-14&cutoff=09:00` | CSV for selected delivery day |
| `GET /docs` | Interactive OpenAPI documentation |

Invalid dates or times return HTTP 422. Missing or invalid snapshots return HTTP 503. There are no write endpoints or secrets.

## Files

| Path | Responsibility |
| --- | --- |
| `app.py` | FastAPI routes, input validation, cache, static serving, CSV |
| `backend/analysis.py` | Forecast revision selection, alignment, error metrics |
| `frontend/src/main.jsx` | React views and charts |
| `frontend/src/style.css` | Responsive visual design |
| `frontend/vite.config.js` | Build to `public/`, local API proxy |
| `frontend/package-lock.json` | Locked frontend dependency graph |
| `public/` | Prebuilt frontend, also rebuilt during deployment |
| `data/snapshot.json.gz` | Actual Elexon records |
| `data/provenance.json` | Source requests, counts, retrieval timestamp, hash |
| `scripts/fetch_data.py` | Reproducible offline ingestion |
| `tests/` | Analysis unit tests and real-snapshot/API checks |
| `.github/workflows/ci.yml` | Python tests, frontend build, Docker build and smoke test |
| `Dockerfile`, `compose.yaml` | Single-container local deployment |
| `pyproject.toml`, `vercel.json` | Python entrypoint and React build for Vercel |
| `docs/DEMO_SCRIPT.md` | Timed customer and technical video walkthrough |
| `docs/SUBMISSION.md` | Publishing and submission checklist |
| `docs/VALIDATION.md` | Executed checks and remaining verification |

## Tests

```bash
python -m pytest -q
npm run build --prefix frontend
```

Tests verify cutoff boundaries, future-publication exclusion, actual revision selection, duplicate conflicts, missing half hours, zero values, metric arithmetic, January/February boundaries, source integrity, API validation, CSV, and real-data coverage. Integration tests intentionally pin the default snapshot’s complete coverage so changed upstream data cannot silently reduce the pilot’s completeness.

## Deploy on Vercel

1. Push this folder as the root of a public GitHub repository. Do not commit virtual environments or `node_modules`.
2. The repository is linked to Vercel project `q7m4x9p2`; pushes to the production branch deploy automatically.
3. The configured build command runs `npm ci --prefix frontend && npm run build --prefix frontend`. React output is placed in root `public/`, which Vercel serves as static files. Python handles `/api/*` and `/docs`.
4. Verify `/`, `/api/health`, `/api/dashboard`, CSV, and `/docs` after deployment.
5. Check all submitted URLs in an incognito browser. Production reviewer access is public.

Vercel configuration follows https://vercel.com/docs/frameworks/backend/fastapi. The app is deployed to Vercel. The root route rewrites to `/index.html` so the CDN serves the React entry page while Python handles the API.

## AI disclosure

This project was created with OpenAI ChatGPT/Codex assistance for requirements interpretation, source code, styling, data retrieval, tests, and documentation. Review and understand the implementation before presenting it as your submission. No generated or fabricated generation data was substituted for Elexon records.

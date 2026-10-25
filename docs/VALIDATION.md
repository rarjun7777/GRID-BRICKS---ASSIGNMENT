# Validation record

Validated 25 October 2026 (Asia/Calcutta user date).

## Passed

- Downloaded real Elexon WINDFOR and FUELHH data: 18,688 forecast records and 1,488 WIND actuals.
- `npm run build --prefix frontend` builds the production React bundle.
- `python -m pytest -q`: 14 tests pass. A third-party Starlette/AnyIO deprecation warning is non-fatal.
- Default-cutoff coverage: 744/744 delivery hours matched.
- At 09:00 UTC: monthly MAE 2,038.9126 MW; RMSE 2,504.7587 MW; bias +1,747.8871 MW.
- Default day (14 January decision / 15 January delivery): 24/24 matched; MAE 1,041.8333 MW.
- FastAPI TestClient verifies HTTP routes, static index, CSV content, date/time validation, and snapshot integrity.
- Tests also exercise every January date at 00:00, 09:00, 12:30, and 23:59 to ensure selected publications do not exceed the decision cutoff.
- Public Vercel checks after SSO was disabled: `/`, `/api/health`, and `/api/dashboard?decision=2026-01-14&cutoff=09:00` returned HTTP 200.
- Public GitHub repository contains the project source and bundled data on `main` (commit `79026575c350b07fa88be71ed0cd166108087583`).

## Verification limits

- Docker binary/daemon is unavailable. Docker build/runtime validation is defined in CI but has not executed here.
- Browser inspection confirmed the deployed dashboard, charts, metrics, and hourly table. Mobile visual QA, chart-tooltip interaction, and a real-browser CSV download test remain unverified.
- The source is public on GitHub. The existing Vercel project is not connected to that repository for automatic deploys; connect it in Vercel Git settings if push-triggered deploys are required.
- A demo script is included; no finished video or YouTube upload exists.

## Remaining verification before submission

Run the Docker/CI checks, perform mobile visual QA and a browser CSV download, record and upload the video, and open all three submission URLs in incognito.

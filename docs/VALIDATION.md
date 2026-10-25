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

## Verification limits

- Docker binary/daemon is unavailable. Docker build/runtime validation is defined in CI but has not executed here.
- Browser extension context is unavailable. Managed preview startup fails because the preview daemon mailbox is absent. No browser rendering, mobile visual QA, chart-tooltip interaction, or real-browser download test was completed. The build and HTTP tests do not substitute for these checks.
- GitHub repository creation and code publication remain pending; the GitHub account connector has no repository-creation action. The public anonymous repo does not yet exist.
- A demo script is included; no finished video or YouTube upload exists.
- The Vite build reports a JavaScript bundle over 500 kB before gzip (about 169 kB gzipped); code splitting is a potential optimization, not a correctness failure.

## Remaining verification before submission

Run the Docker/CI checks, perform desktop and mobile browser QA, verify the deployed API/static routing, record and upload the video, and open all three submission URLs in incognito.

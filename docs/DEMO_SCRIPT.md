# Winddesk video walkthrough

Target: 8 minutes 30 seconds. Record an actual screen walkthrough after deployment and browser verification. This file is a script, not a finished or uploaded video. Use an unlisted YouTube upload. Keep total runtime below 10 minutes.

## Part 1 Customer demonstration 0:00–4:15

### 0:00–0:35 Why this product exists

Show Decision overview, 14 January, cutoff 09:00.

“Winddesk helps a day-ahead purchasing team see the wind forecast that was actually available when they had to make a decision. It puts the eventual outcome beside that forecast, so the team can understand the size and direction of historical error. This pilot uses only Elexon national wind data, for January 2026 decision dates.”

### 0:35–1:30 Make the decision context explicit

Point to the decision date, delivery day, and cutoff.

“The selected decision is 14 January for delivery on 15 January. The cutoff defaults to 09:00 UTC; it is an adjustable pilot assumption. For every delivery hour, we select the latest forecast issued by that cutoff. A later forecast cannot influence this historical decision.”

Change cutoff to 12:00, observe updated values, then restore 09:00. Avoid claiming earlier or later forecasts always improve accuracy.

### 1:30–2:25 Compare expectations with outcomes

Point to the forecast-versus-actual chart and error bars. Hover over one hour.

“The solid green line is the day-ahead forecast. The dashed line is actual generation, shown after the event. The error chart is forecast minus actual: positive values mean less wind arrived than forecast. For this selected day, mean absolute error is about 1,042 MW. That is a national-level forecast discrepancy, not automatically the client’s purchase shortfall.”

Scroll to the trace table and point to publication time and lead time. Export CSV.

### 2:25–3:25 Evaluate the month

Open Forecast accuracy.

“Across all 31 January decisions at the same cutoff, we have 744 matched delivery hours. The mean absolute miss is about 2,039 MW, RMSE about 2,505 MW, and average bias about positive 1,748 MW. The positive bias indicates overestimation in this sample. The daily ledger helps investigate which days drive the result. These are retrospective January outcomes; we do not pretend a buyer knew the full month’s results at the start of January.”

Select a day from the ledger and inspect it.

### 3:25–4:15 Explain value and boundaries

Open Data & methodology.

“Winddesk makes the evidence inspectable. It records publication times, missing-data coverage, source provenance, and the alignment method. Forecasts are hourly, so we compare each with the average of two half-hour actuals. This is an explicit approximation. The client would still need its own demand and contracted generation to translate this national view into a purchase volume. The pilot’s value is a transparent basis for discussing wind forecast uncertainty.”

## Part 2 Technical review 4:15–8:30

### 4:15–5:05 Architecture

Show the repository root and README architecture explanation.

“The frontend is React with custom SVG charts and Vite. A Python FastAPI backend selects forecast revisions, aligns actuals, calculates metrics, and exports CSV. Both are served from one origin. Docker builds the frontend in a Node stage and serves the complete app from a non-root Python stage. The fixed historical scope is small enough for a versioned compressed snapshot rather than a database.”

### 5:05–6:05 Data ingestion and integrity

Open `scripts/fetch_data.py`, `data/provenance.json`, and `backend/analysis.py`.

“The downloader requests daily Elexon windows, with bounded concurrency, timeouts, and retries. It keeps source request URLs, retrieval time, record counts, and a hash. There are 18,688 forecast records and 1,488 half-hour actuals. Exact duplicates are removed; conflicting versions fail explicitly. Actual outturn uses the latest available revision in the retrieved snapshot.”

### 6:05–7:10 Critical algorithm

Show `Analysis.day` in `backend/analysis.py`.

“The key rule is publication time less than or equal to cutoff. We then choose the latest eligible publication for each next-day hour. Actuals require both half-hour records; incomplete pairs are excluded, not filled with zero. Missing forecasts have no future fallback. Error equals forecast minus actual. MAE, RMSE, bias, and coverage are calculated only from matched hours.”

Mention that 31 January decisions target 1 February, and that full-month metrics are explicitly retrospective.

### 7:10–8:00 Validation and developer experience

Run `python -m pytest -q`. Show API docs `/docs`, the CSV endpoint, and CI workflow.

“The tests cover cutoff equality, exclusion of future revisions, zero actuals, missing half hours, duplicate conflicts, actual revisions, formula arithmetic, source hash, API inputs, CSV, and January’s boundary. The frontend production build passes. CI additionally builds Docker and smoke-tests the running container.”

Only claim Docker or browser verification if those steps have actually been completed by recording time. The initial build environment lacked both Docker and a working managed preview service.

### 8:00–8:30 Tradeoffs and handover

“09:00 is an assumption, and hourly alignment is documented. This is a reproducible pilot, not a live trading system. For production I would agree the market cutoff and forecast interval semantics, add scheduled ingestion and monitoring, and connect the client’s portfolio and demand only if scope expands. The README includes startup, data refresh, testing, AI disclosure, and deployment instructions.”

## Before uploading

- Verify the visible deployed app, mobile layout, chart tooltips, date/cutoff changes, and CSV download.
- Record both the customer and technical sections; do not substitute this script for the video.
- Use the actual current findings if the data or algorithm changes.
- Ensure no credentials, personal account details, or private files appear in the recording.
- Upload as unlisted and verify the watch URL in a signed-out/incognito browser.

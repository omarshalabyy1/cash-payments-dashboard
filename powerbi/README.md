# Building the Power BI report

The report answers three questions for the owner: how much cash came in (by day, payment method and region), how much is still due on card instalments, and which payments came late.

## Pages

1. **Daily cash:** cash in by day, by payment method and by region, with the payments confirmed and the late rate for any date range.
2. **Due and late:** the card instalments still due by month, the money never paid, and every late payment listed.

## Before you start

1. The warehouse is running and loaded: from the repo folder, `docker compose up -d` then `python load.py` (it ends with "check passed").
2. Power BI Desktop is installed.
3. In Power BI Desktop: File > Options and settings > Options > Current file > Data load: untick **Auto date/time** (the model has its own date table).

## Follow the files in order

The step-by-step path is [08-build-checklist.md](08-build-checklist.md): 32 numbered steps that call each file below at the right moment and stop at checks C1 to C8.

| Step | File | What you do |
|---|---|---|
| 1 | [01-power-query.md](01-power-query.md) | Connect to PostgreSQL and paste the five queries |
| 2 | [02-model.md](02-model.md) | Create the relationships, mark the date table, hide and sort columns |
| 3 | [03-measures.dax](03-measures.dax) | Paste the 12 measures into the `_Measures` table |
| 4 | [05-theme.json](05-theme.json) | View > Themes > Browse for themes, pick this file |
| 5 | [04-pages.md](04-pages.md) | Build the two pages, 22 visuals, in order |
| 6 | [07-interactions.md](07-interactions.md) | Set the edit-interactions matrix and the one visual-level filter |
| 7 | [06-checks.md](06-checks.md) | Compare every card with the expected numbers (C1 to C8) |
| 8 | `screenshots/` | Save one image per page: `daily-cash.png` and `due-and-late.png` |

Save the report as `powerbi/cash-payments-dashboard.pbix` and commit it with the screenshots.

If Power BI says the PostgreSQL connector needs a provider, install Npgsql (the recent Power BI Desktop builds already include it).

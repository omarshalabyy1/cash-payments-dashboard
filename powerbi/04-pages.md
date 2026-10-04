# 04 · Pages

Canvas: 16:9, 1280 × 720 (Format page > Canvas settings). Position and size are set in Format visual > General > Properties: X, Y, width, height.
Every amount is in BRL. Cards show display units **Millions** with 2 decimals, except where a row says otherwise.
Rename a field inside a visual by double-clicking it in the Build pane; the names to use are in quotes.
Build the visuals in the order of the # column. No visual uses the Legend well: each chart has one series.
Interactions, filters, drill-through and bookmarks are in [07-interactions.md](07-interactions.md).

## Page 1 · Daily cash

What came in, by day, payment method and region.

| # | Visual | X, Y, W, H | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 600, 48 | "Daily cash" | Segoe UI Semibold 20, navy `#0E1630` |
| 2 | Card | 1040, 12, 216, 56 | `[Report Date]` as "Report date" | Display units None; category label on |
| 3 | Slicer | 24, 76, 400, 56 | `dim_date[date]` as "Date" | Style: Between (a date range); format `d mmm yyyy`; not synced |
| 4 | Slicer | 440, 76, 260, 56 | `dim_payment_method[payment_method]` as "Payment method" | Style: Dropdown; Selection: Single select off (multi-select with Ctrl), Select all on; synced |
| 5 | Slicer | 716, 76, 260, 56 | `dim_state[region]` as "Region" | Style: Dropdown; Selection: Single select off (multi-select with Ctrl), Select all on; synced |
| 6 | Card | 24, 148, 296, 100 | `[Cash In]` as "Cash in" | Millions, 2 decimals |
| 7 | Card | 336, 148, 296, 100 | `[Payments Confirmed]` as "Payments confirmed" | Display units None |
| 8 | Card | 648, 148, 296, 100 | `[Late Payments]` as "Late payments" | Display units None |
| 9 | Card | 960, 148, 296, 100 | `[Late Rate %]` as "Late rate" | 1 decimal |
| 10 | Line chart | 24, 264, 760, 440 | X-axis `dim_date[date]`; Y-axis `[Cash In]`; Tooltips `[Payments Confirmed]` | Title "Cash in by day"; X-axis type Continuous; Y-axis display units Millions; data labels off; line colour royal blue `#2563EB` |
| 11 | Clustered bar chart | 800, 264, 456, 212 | Y-axis `dim_payment_method[payment_method]`; X-axis `[Cash In]`; Tooltips `[Share of Cash In %]` | Title "Cash in by payment method"; sort by Cash in, descending; X-axis and data labels display units Millions, 2 decimals |
| 12 | Clustered bar chart | 800, 492, 456, 212 | Y-axis `dim_state[region]`; X-axis `[Cash In]`; Tooltips `[Share of Cash In %]` | Title "Cash in by region"; sort by Cash in, descending; X-axis and data labels display units Millions, 2 decimals |


## Page 2 · Due and late

What is still to come on card instalments, what was never paid, and which payments came late. There is no date slicer on this page: it always shows everything up to the report date and every instalment after it.

| # | Visual | X, Y, W, H | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 600, 48 | "Due and late" | Segoe UI Semibold 20, navy `#0E1630` |
| 2 | Card | 1040, 12, 216, 56 | `[Report Date]` as "Report date" | Same as page 1 |
| 3 | Slicer | 24, 76, 260, 56 | `dim_payment_method[payment_method]` as "Payment method" | Same as page 1 #4; synced |
| 4 | Slicer | 300, 76, 260, 56 | `dim_state[region]` as "Region" | Same as page 1 #5; synced |
| 5 | Card | 24, 148, 400, 100 | `[Still Due]` as "Still due on instalments" | Millions, 2 decimals |
| 6 | Card | 440, 148, 400, 100 | `[Never Paid]` as "Never paid" | Thousands, 1 decimal |
| 7 | Card | 856, 148, 400, 100 | `[Late Amount]` as "Money in late payments" | Thousands, 1 decimal |
| 8 | Clustered column chart | 24, 264, 616, 210 | X-axis `dim_date[year_month]` as "Month"; Y-axis `[Still Due]` | Title "Still due by month"; X-axis type Categorical, sorted by Month ascending; Y-axis and data labels display units Thousands, 1 decimal; colour royal blue `#2563EB` |
| 9 | Matrix | 656, 264, 600, 210 | Rows `dim_payment_method[payment_method]`; Values `[Payments Confirmed]`, `[Late Payments]`, `[Late Rate %]`, `[Late Amount]` | Title "Late payments by method"; conditional formatting on Late rate: Background colour, gradient lowest `#FFFFFF` → highest `#2563EB`; row subtotals on; number formats from the measures |
| 10 | Table | 24, 490, 1232, 214 | `fact_instalment[payment_id]` as "Payment", `fact_instalment[order_date]` as "Ordered", `[Confirmed Date]` as "Confirmed", `dim_payment_method[payment_method]` as "Method", `dim_state[state]` as "State", `dim_state[region]` as "Region", `fact_instalment[instalments]` as "Instalments", `[Total Paid]` as "Amount" | Title "Late payments"; visual-level filter `fact_instalment[is_late]` is True; sort by Amount descending; totals on |


## Slicer sync

View > Sync slicers. Select the Payment method slicer: tick Sync and Visible on both pages. Do the same for the Region slicer.
The Date slicer stays on page 1 only (untick page 2), because page 2 shows the instalments still to come.

## Page names

Right-click each page tab > Rename: "Daily cash" and "Due and late".

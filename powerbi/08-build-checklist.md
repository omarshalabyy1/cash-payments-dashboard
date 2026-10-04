# 08 · Build checklist

From opening Power BI Desktop to the last screenshot. Tick each step; stop at a check (C1 to C8, in [06-checks.md](06-checks.md)) and fix the build before going on if a number differs.

## Start

1. In the repo folder: `docker compose up -d`, then `python load.py`. It must end with `check passed`.
2. Open Power BI Desktop > Blank report. File > Save as `powerbi/cash-payments-dashboard.pbix`.
3. File > Options and settings > Options > Current file > Data load: untick **Auto date/time**. In the same window, Relationships: untick **Autodetect new relationships after data is loaded**. OK.

## Power Query ([01-power-query.md](01-power-query.md))

4. Home > Get data > Blank query > Advanced Editor: paste `Warehouse`, Done, rename it `Warehouse`. Credentials: Database, user `cash`, password `cash`. Right-click > untick **Enable load**.
5. Repeat with `fact_instalment`, `dim_date`, `dim_payment_method`, `dim_state` (Blank query, paste, rename).
6. Home > Close & Apply.
7. **Check C1:** row counts 296,425 / 1,338 / 5 / 27.
8. Home > Enter data: name `_Measures`, Load.

## Model ([02-model.md](02-model.md))

9. Model view: create the three relationships (dim_date[date] → cash_date, dim_payment_method[payment_type] → payment_type, dim_state[customer_state] → customer_state), one to many, single, active.
10. `dim_date` > Mark as date table > `date`.
11. Hide the columns in the Hide table.
12. Sort by column: `weekday` by `weekday_no`, `payment_method` by `sort_order`.
13. Column formats: the dates `d mmm yyyy`, `instalments` Don't summarize.

## Measures ([03-measures.dax](03-measures.dax))

14. Select `_Measures` > New measure, paste the first measure (`Payments`), set its format and display folder. Repeat for all 12, top to bottom.
15. Delete `Column1` from `_Measures`. The table icon turns into a calculator.

## Theme ([05-theme.json](05-theme.json))

16. View > Themes > **Browse for themes** > pick `powerbi/05-theme.json`. The page turns soft grey, visuals white with a thin border.

## Page 1 · Daily cash ([04-pages.md](04-pages.md))

17. Format page > Canvas settings: 16:9, 1280 × 720. Rename the page tab "Daily cash".
18. Build visuals #1 to #12 in order, with the position, size, fields and settings in the table.
19. **Check C2:** the four cards and the report date with no slicer selected.
20. **Check C4** (hover the method bars) and **C5** (hover the region bars).
21. Set the Date slicer to 1 May 2018 to 31 May 2018. **Check C3**. Then clear the slicer (eraser icon).
22. Set the interactions for page 1 ([07-interactions.md](07-interactions.md)).

## Page 2 · Due and late

23. New page, Canvas settings 1280 × 720, rename the tab "Due and late".
24. Build visuals #1 to #10 in order; on #10 add the visual-level filter `is_late` is True.
25. **Check C6** (cards and the table's Amount total), **C7** (first four months), **C8** (matrix, with its Total row).
26. Set the interactions for page 2 ([07-interactions.md](07-interactions.md)).
27. View > Sync slicers: Payment method and Region synced and visible on both pages; Date on page 1 only.
28. On page 2, pick "Boleto (bank slip)" in the Payment method slicer: page 1's slicer shows the same choice. Clear it.

## Finish

29. Every slicer cleared; page 1 selected. File > Save.
30. View > Page view > **Fit to page**. On each page take a screenshot of the canvas (Windows + Shift + S) and save it as `powerbi/screenshots/daily-cash.png` and `powerbi/screenshots/due-and-late.png`.
31. In the repo `README.md`, under "The Power BI report", add:

    ```markdown
    ![Daily cash page](powerbi/screenshots/daily-cash.png)

    ![Due and late page](powerbi/screenshots/due-and-late.png)
    ```

32. Commit `powerbi/cash-payments-dashboard.pbix`, the two screenshots and `README.md`, and push.

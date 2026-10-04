# 07 · Interactions, filters and drill-through

Visual numbers (#) are the ones in [04-pages.md](04-pages.md).
To set one: select the source visual, Format ribbon > **Edit interactions**, then on each target visual click the funnel (**Filter**) or the circle with a line (**None**). Turn Edit interactions off when the page is done.

**Filter**, never Highlight: the selected numbers show outright on every card and chart, so they can be checked.

## Page 1 · Daily cash

| Source ↓ / Target → | #2 Report date | #3 Date slicer | #4 Method slicer | #5 Region slicer | #6 to #9 Cards | #10 Line | #11 Method bars | #12 Region bars |
|---|---|---|---|---|---|---|---|---|
| #3 Date slicer | None | | Filter | Filter | Filter | Filter | Filter | Filter |
| #4 Method slicer | None | Filter | | Filter | Filter | Filter | Filter | Filter |
| #5 Region slicer | None | Filter | Filter | | Filter | Filter | Filter | Filter |
| #10 Line (click a day) | None | None | None | None | Filter | | Filter | Filter |
| #11 Method bars | None | None | None | None | Filter | Filter | | Filter |
| #12 Region bars | None | None | None | None | Filter | Filter | Filter | |

Why #2 is None everywhere: the report date is the same whatever is selected.

## Page 2 · Due and late

| Source ↓ / Target → | #2 Report date | #3 Method slicer | #4 Region slicer | #5 to #7 Cards | #8 Still due by month | #9 Late matrix | #10 Late table |
|---|---|---|---|---|---|---|---|
| #3 Method slicer | None | | Filter | Filter | Filter | Filter | Filter |
| #4 Region slicer | None | Filter | | Filter | Filter | Filter | Filter |
| #8 Still due by month | None | None | None | None | | None | None |
| #9 Late matrix (click a method) | None | None | None | Filter | Filter | | Filter |
| #10 Late table | None | None | None | None | None | None | |

Why #8 is None: a month of instalments still to come says nothing about which payments were late.
Why #10 is None: the table is a list to read, not a filter.

## Filters

| Level | Filter |
|---|---|
| Report level | None |
| Page level, both pages | None |
| Visual level | Page 2 #10 Late table: `fact_instalment[is_late]` is True |

## Slicer sync

Payment method and Region are synced and visible on both pages; Date is on page 1 only. Steps in [04-pages.md](04-pages.md), Slicer sync.

## Drill-through, bookmarks, buttons, tooltip pages

None. The two pages are reached by their tabs, and tooltips come from each visual's Tooltips well.

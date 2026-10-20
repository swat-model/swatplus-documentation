---
title: Recall outputs
description: The recall and basin_psc files. Daily water, sediment and nutrient loads released by recall objects (point sources, inlets and diversions), per object and summed over the basin.
status: review
verified_against:
  - src/header_write.f90
  - src/hydrograph_module.f90
  - src/recall_output.f90
  - src/basin_recall_output.f90
  - src/recall_read.f90
  - src/recall_nut.f90
  - src/command.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A recall object adds a measured or externally simulated time series of water and loads to the model: a point source such as a treatment plant, an inlet from an area outside the model, or, with negative flows, a diversion. The recall output files show what each recall object released into the model.

| [`print.prt`](../input-reference/print-prt.md) row | Files | One row per |
|-----------------|-------|-------------|
| `recall` | `recall_day.txt`, `recall_mon.txt`, `recall_yr.txt`, `recall_aa.txt` | recall object |
| `basin_psc` | `basin_psc_day.txt`, `basin_psc_mon.txt`, `basin_psc_yr.txt`, `basin_psc_aa.txt` | basin (sum of all recall objects) |

Each `y` in the `daily`, `monthly`, `yearly` or `avann` column of [`print.prt`](../input-reference/print-prt.md) opens the matching file. With `csvout` set to `y`, a `.csv` copy of each file is written as well. The `basin_psc` files are written only when the project has at least one recall object.

## Format

- Line 1: the project name from [`file.cio`](../input-reference/file-cio.md) and the SWAT+ version banner.
- Line 2: column headers.
- Line 3: units.
- Lines 4 and on: data rows.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `jday` | - | Day of the year of the last day in the print step. |
| 2 | `mon` | - | Month. |
| 3 | `day` | - | Day of the month. |
| 4 | `yr` | - | Calendar year. |
| 5 | `name` | - | Name of the recall object. In `basin_psc` files, the project name. |
| 6 | `type` | - | Object type, always `recall`. `basin_psc` files have no `type` column; the header has a blank name in its place. |
| 7 | `flo` | m³ | Water released. |
| 8 | `sed` | tons | Sediment. |
| 9 | `orgn` | kg N | Organic nitrogen. |
| 10 | `sedp` | kg P | Organic (sediment-attached) phosphorus. |
| 11 | `no3` | kg N | Nitrate. |
| 12 | `solp` | kg P | Soluble mineral phosphorus. |
| 13 | `chla` | kg | Chlorophyll a. |
| 14 | `nh3` | kg N | Ammonium. |
| 15 | `no2` | kg N | Nitrite. |
| 16 | `cbod` | kg | Carbonaceous biochemical oxygen demand. |
| 17 | `dox` | kg | Dissolved oxygen. |
| 18 | `san` | tons | Sand. |
| 19 | `sil` | tons | Silt. |
| 20 | `cla` | tons | Clay. |
| 21 | `sag` | tons | Small aggregates. |
| 22 | `lag` | tons | Large aggregates. |
| 23 | `grv` | tons | Gravel. |
| 24 | `null` | °C | Water temperature. |

The values are the recall record used on the day, unchanged: SWAT+ does not convert the numbers read from the recall time series. The model passes `flo` on to the receiving object as a daily volume in m³, so that is how the column should be read, although the units row gives m³/s. The `.csv` copies of the `recall` files use a different units row, which gives `flo` as m³.

## Values by recall time step

The time step of each recall object is set in its [recall file](../input-reference/recall.md):

- Daily: each day uses the record for that day. Outside the years covered by the time series, the values are zero.
- Monthly: the record for the month is used on every day of that month. A monthly row of `recall_mon.txt` is therefore the monthly record multiplied by the number of days in the month. Outside the covered years, the values are zero.
- Yearly: the record for the year is used on every day of that year, so a row of `recall_yr.txt` is 365 or 366 times the yearly record.
- Sub-daily: the daily row is the sum of the records for that day's time steps.

A negative `flo` in a daily recall time series is a withdrawal. The row shows the negative value as read. In addition, SWAT+ removes nitrate, ammonium, nitrite, organic nitrogen, soluble phosphorus and dissolved oxygen from the receiving channel's storage at the channel's current concentration. Those removed amounts are not in the recall files.

## Aggregation

Monthly and yearly rows are totals over the step for all columns except `null`, which is a flow-weighted average. The average annual row is the average yearly total. Rows start after the `nyskip` warm-up years, and daily rows follow the daily print window and `interval` in [`print.prt`](../input-reference/print-prt.md).

`basin_psc` rows are sums over all recall objects, so withdrawals (negative flows) offset releases.

## Example

The column names of `recall_day.txt`:

```
jday  mon  day  yr  name  type
flo  sed  orgn  sedp  no3  solp  chla  nh3  no2  cbod  dox  san  sil  cla  sag  lag  grv  null
```

A treatment plant entered as a monthly recall object with `flo` = 1,200 for March shows 1,200 on every March row of `recall_day.txt` and 37,200 in the March row of `recall_mon.txt`.

## Related files

- [Recall inputs](../input-reference/recall.md): the recall objects and their time series.
- [`print.prt`](../input-reference/print-prt.md): the `recall` and `basin_psc` switches.
- [Hydrograph outputs](hydrographs.md): the same column layout for water passed between objects; the `hydout` rows of a recall object show where its water goes.
- [Output naming convention](naming-convention.md): all output files.

??? quote "Sources"

    - File opening and headers: [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90)
    - Header types: `hyd_header`, `hyd_header_time`, `rec_header_time`, `hyd_header_units`, `hyd_header_units3` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Writers: [`recall_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_output.f90), [`basin_recall_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_recall_output.f90)
    - Daily record selection: `case ("recall")` in [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)
    - Reading the time series: [`recall_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read.f90)
    - Nutrient removal for withdrawals: [`recall_nut.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_nut.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | hydrograph (`recall`) | `rec_d(irec) = ob(icmd)%hd(1)`, summed into `rec_m`, `rec_y`, `rec_a` |
    | hydrograph (`basin_psc`) | `brec_d` (sum of `rec_d`), `brec_m`, `brec_y`, `brec_a` |
    | `null` | `hyd_output%temp` |

---
title: "*.pcp (precipitation data)"
description: Measured precipitation for one gauge, daily or sub-daily, listed in pcp.cli and used by weather stations in weather-sta.cli.
status: review
verified_against:
  - src/cli_pmeas.f90
  - src/cli_precip_control.f90
  - src/cli_bounds_check.f90
  - src/cli_staread.f90
  - src/search.f90
  - src/climate_module.f90
  - src/cli_pgen.f90
  - src/cli_pgenhr.f90
  - src/cli_lapse.f90
  - src/hru_control.f90
  - src/sd_channel_control3.f90
  - src/res_control.f90
  - src/time_read.f90
  - src/time_control.f90
  - src/readcio_read.f90
  - src/input_file_module.f90
  - src/cal_conditions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A precipitation data file contains the measured precipitation of one gauge, as daily totals or as values for each sub-daily time step. Each file is named on one line of [`pcp.cli`](cli.md#observed-data-lists), and a weather station uses it when the `pcp` column of [`weather-sta.cli`](cli.md#weather-stacli) gives the same name. Days without a usable value are filled by the weather generator station named in the `wgn` column of the same weather station.

SWAT+ does not check the file extension. `.pcp` is the usual one. If `pcp_path` in [`file.cio`](file-cio.md) is not `null`, its value is put in front of every file name in [`pcp.cli`](../input-reference/cli.md#observed-data-lists) (see [path prefixes](cli.md#path-prefixes)).

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is a column header; both are skipped. Line 3 describes the gauge and every later line is one record.

### Gauge line

SWAT+ Editor writes the header `nbyr tstep lat lon elev` above this line.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `nbyr` | years | Number of years of record. SWAT+ uses it to size the store for the data, so it must be at least the number of calendar years the record spans. |
| 2 | `tstep` | values per day | `0` for daily data. For sub-daily data, the number of values per day, which must equal `step` in [`time.sim`](time-sim.md) (24 for hourly data). |
| 3 | `lat` | decimal degrees | Latitude of the gauge. Not used by SWAT+. |
| 4 | `lon` | decimal degrees | Longitude of the gauge. Not used by SWAT+. |
| 5 | `elev` | m | Elevation of the gauge. Used only for the [elevation adjustment](#elevation-adjustment). |

### Daily records

With `tstep` = 0, each record has three values:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | year | - | Calendar year. |
| 2 | day | - | Day of the year, 1 to 366. Called `jday` in earlier documentation. |
| 3 | pcp | mm | Precipitation for the day. A value of -97 or less marks the day as missing. |

### Sub-daily records

With `tstep` greater than 0, each record has six values:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | year | - | Calendar year. |
| 2 | day | - | Day of the year, 1 to 366. Called `jday` in earlier documentation. |
| 3 | month | - | Month, called `mon` in earlier documentation. Not used by SWAT+. |
| 4 | day of month | - | Not used by SWAT+. |
| 5 | step | - | Time step within the day, called `hr` in earlier documentation. Not used by SWAT+. |
| 6 | pcp | mm | Precipitation for the time step. |

SWAT+ places the values of each day in the order they appear, so every day needs `step` records in time order. The month, day of month and step columns do not position the value.

### Record order

Records must be continuous and in date order. SWAT+ counts years by watching for day 365 or 366 followed by a record from a new year, so a gap at the end of a year shifts every later year of the record. A file that starts or ends part way through a year is fine.

## Reading and storage

Records before the start of the simulation are skipped when the file is read. Storage starts with the first record whose year is at or after `yrc_start` and whose day is at or after `day_start` in [`time.sim`](../input-reference/time-sim.md).

When the record starts in a year after the simulation start year and `day_start` is later than the first day in the file, the records of that first year before `day_start` are also skipped. Those days then read as 0 mm instead of being filled by the weather generator.

## Missing days

In a daily run, SWAT+ fills a day from the weather generator when

- the value is -97 or less (SWAT+ Editor and most tools write -99), or
- the day is before the first record or after the last record of the file.

Generated precipitation uses the monthly statistics of the station's [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) entry and the wet or dry state of the previous day. The method is described in [Climate and weather](../model-theory/climate-weather.md#weather-generator).

## Sub-daily runs

A sub-daily file is read when `tstep` is greater than 0. `step` in [`time.sim`](../input-reference/time-sim.md) sets the number of steps per day of the run, and SWAT+ stores that many values per day. If the two numbers differ, the values are assigned to the wrong steps: with `step` = 0 or 1 and an hourly file, only the last hour of each day is kept.

Missing and out-of-range values are handled differently from daily data in 62.0.1:

- When a step has a value of -97 or less, SWAT+ calls the generator, but the day's total is still the sum of the file values for that day, missing-value flags included.
- Days outside the record are not generated. Inside the stored years they read as 0 mm.
- Values are looked up by simulation year counted from the simulation start, so the record must start on or before the simulation start date.
- From the second simulation year on, the values used for 1 January come from 1 January of the previous simulation year.

Sub-daily files should therefore be complete, without missing values, and cover the whole simulation period.

## Elevation adjustment

When `lapse` = 1 in [`codes.bsn`](codes-bsn.md), the precipitation of each HRU is changed for the difference between the HRU elevation and the gauge elevation:

$$P_{hru} = \max\left(0,\; P + \mathrm{plaps}\,\frac{z_{hru} - z_{gauge}}{1000}\right)$$

where $P$ is the station precipitation (mm), `plaps` is the precipitation lapse rate in [`parameters.bsn`](parameters-bsn.md) (mm per km, default 0), $z_{hru}$ is the `elev` column of [`hru.con`](con.md) and $z_{gauge}$ is `elev` from this file (m). When the station's `pcp` column is `sim`, the elevation of the weather generator station is used for $z_{gauge}$.

The adjustment is added every day, dry days included, so a positive `plaps` gives HRUs above the gauge a small amount of precipitation on every day. The adjustment values are calculated during channel and reservoir routing, so in a model without channels or reservoirs they remain zero.

## Calibration

The calibration parameter `precip` (object type `cli`) changes the stored daily values of listed precipitation records over a window of days and years. See [Climate changes](../calibration/hard-calibration.md#climate-changes).

## Example

First lines of `refdata/Ames_sub1/ames.pcp` in the SWAT+ repository, and part of 2012:

```
AME.pcp
 NBYR    TSTEP      LAT     LONG     ELEV
   121        0    42.04   -93.89   316
1900 1 -99
1900 2 -99
1900 3 -99
...
2012 55 12.4
2012 56 0
2012 57 -99
2012 58 0
```

A daily record (`tstep` = 0) of 121 years, 1900 to 2020, at 316 m. The Ames run starts in 1975, so the records from 1900 to 1974 are skipped when the file is read. Of the days from 1975 on, 31 are marked missing (`-99`), such as day 57 of 2012, and the weather generator fills them during the run.

## Related files

- [`pcp.cli`](cli.md#observed-data-lists): lists the precipitation files.
- [`weather-sta.cli`](cli.md#weather-stacli): assigns a precipitation file to each weather station in its `pcp` column.
- [`weather-wgn.cli`](cli.md#weather-wgncli): weather generator statistics that fill missing days.
- [`time.sim`](time-sim.md): simulation period and number of steps per day.
- [`file.cio`](file-cio.md): names [`pcp.cli`](../input-reference/cli.md#observed-data-lists) and the `pcp_path` prefix.
- [`codes.bsn`](codes-bsn.md) and [`parameters.bsn`](parameters-bsn.md): `lapse` switch and `plaps` rate.

??? quote "Sources"

    - Reader: [`cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pmeas.f90)
    - Type definition: `type climate_measured_data` in [`climate_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_module.f90)
    - Gauge name lookup from `weather-sta.cli`: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90), [`search.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/search.f90)
    - Daily use, missing values and range check: [`cli_precip_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_precip_control.f90), [`cli_bounds_check.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_bounds_check.f90), called from [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Weather generator: [`cli_pgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pgen.f90), [`cli_pgenhr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pgenhr.f90)
    - Elevation adjustment: [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90), called from [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90) and [`res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), applied in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Time step: [`time_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_read.f90)
    - Path prefix: `in_path_pcp` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Calibration change `precip`: [`cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `nbyr` | `pcp(i)%nbyr` |
    | `tstep` | `pcp(i)%tstep` |
    | `lat` | `pcp(i)%lat` |
    | `lon` | `pcp(i)%long` |
    | `elev` | `pcp(i)%elev` |
    | daily pcp | `pcp(i)%ts(day, iyr)` |
    | sub-daily pcp | `pcp(i)%tss(step, day, iyr)` |

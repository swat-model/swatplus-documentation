---
title: time.sim
description: Simulation period and the number of time steps per day.
status: review
verified_against:
  - src/time_read.f90
  - src/time_module.f90
  - src/time_control.f90
  - src/proc_bsn.f90
  - src/cli_pmeas.f90
  - src/cli_precip_control.f90
  - src/basin_print_codes_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`time.sim` sets the first and last day of the simulation and the number of time steps per day. Weather input, routing and every output file follow this period. The file is named in slot 1 of the `simulation` line of [`file.cio`](file-cio.md) (default `time.sim`).

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Line 3 contains five integers in the order below. The reader does not match columns by header name.

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `day_start` | day of year | 1 | Day of the year on which the simulation starts, 1 to 366. A value of 0 or less is set to 1 (1 January). |
| 2 | `yrc_start` | year | - | Calendar year in which the simulation starts. |
| 3 | `day_end` | day of year | 0 | Day of the year on which the simulation ends in `yrc_end`. A value of 0 or less means the last day of that year (31 December). |
| 4 | `yrc_end` | year | - | Calendar year in which the simulation ends. |
| 5 | `step` | time steps per day | 1 | Number of time steps per day for precipitation, surface runoff and routing. A value of 0 or less is set to 1 (daily). |

## Simulation period

The simulation runs over the calendar years `yrc_start` to `yrc_end`, which is

$$N_{yr} = \mathrm{yrc\_end} - \mathrm{yrc\_start} + 1$$

years. The first year starts on `day_start`, and every later year starts on 1 January. Every year but the last runs to 31 December. The last year ends on `day_end`, or on 31 December if `day_end` is 0. A `day_end` of 366 in a year that is not a leap year is treated as day 365. Leap years follow the Gregorian rule: years divisible by 4 are leap years, except century years that are not divisible by 400.

`day_start` and `day_end` make it possible to simulate water years or other periods that do not follow the calendar year. For example, `day_start = 274`, `yrc_start = 1999`, `day_end = 273` and `yrc_end = 2019` runs from 1 October 1999 to 30 September 2019. Neither year is a leap year, so day 274 is 1 October and day 273 is 30 September; in a leap year the same dates are days 275 and 274.

The warm-up years and the print window for daily output are set in [`print.prt`](print-prt.md). A zero `yrc_start` or `yrc_end` in [`print.prt`](../input-reference/print-prt.md) is filled from this file.

## Time step

`step` is the number of time steps in a day:

| `step` | Time step |
|--------|-----------|
| 0 or 1 | 1 day |
| 2 | 12 hours |
| 24 | 1 hour |
| 96 | 15 minutes |
| 1440 | 1 minute |

Any positive whole number works. The length of one time step in minutes is

$$\Delta t = \frac{1440}{\mathrm{step}}$$

With `step` greater than 1, the day is split into sub-daily steps for precipitation, infiltration and surface runoff, hydrograph routing through channels and reservoirs, and sub-daily channel output. The Green and Ampt infiltration method (`gampt = 1` in [`codes.bsn`](codes-bsn.md)) uses the sub-daily rainfall. Other processes, such as plant growth, soil water and nutrient cycling, still run once a day.

Sub-daily precipitation records ([`*.pcp`](pcp.md) files with a time step above 0) must have the same number of values per day as `step`. SWAT+ stores `step` values per day and does not check the record against it.

When `step` is greater than 1 and precipitation is generated, the weather generator also distributes each day's rainfall over the time steps. For a station with measured daily records, 62.0.1 does not fill the sub-daily values: the daily total is read, but the rainfall in each time step stays at zero. A sub-daily run therefore needs sub-daily precipitation records or generated precipitation.

## Weather outside the observed record

When the simulation starts before, or ends after, the measured daily weather records listed in the climate index files, SWAT+ generates the weather for the days outside the record with the weather generator ([`weather-wgn.cli`](cli.md)). The same applies to days that are flagged as missing in a record.

## Example

`refdata/Ames_sub1/time.sim` in the SWAT+ repository:

```
time.sim:
day_start  yrc_start   day_end   yrc_end      step
       0      1975         0      2020         0
```

The simulation runs from 1 January 1975 to 31 December 2020, 46 years. `day_start` and `day_end` are 0, so the first and last days of the year are used. `step` is 0, which SWAT+ sets to 1, so the simulation is daily.

## Related files

- [`file.cio`](file-cio.md): names this file.
- [`print.prt`](print-prt.md): warm-up years and print window for the outputs inside this period.
- [`pcp.cli` and the precipitation data files](pcp.md): their time step must match `step` for sub-daily records.
- [`codes.bsn`](codes-bsn.md): selects Green and Ampt infiltration, which uses sub-daily rainfall.

??? quote "Sources"

    - Reader: [`time_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_read.f90)
    - Type definition: `type time_current` in [`time_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_module.f90)
    - Time step length: [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Year and day loop, leap years, end day: [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Measured and generated precipitation: [`cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pmeas.f90), [`cli_precip_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_precip_control.f90)
    - File name slot: `in_sim%time` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `day_start` | `time%day_start` |
    | `yrc_start` | `time%yrc_start` |
    | `day_end` | `time%day_end` |
    | `yrc_end` | `time%yrc_end` |
    | `step` | `time%step` |

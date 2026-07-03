---
title: "*.pcp (precipitation data)"
description: Per-gauge time-series file holding daily or subdaily precipitation depths read by SWAT+.
status: review
verified_against:
  - src/cli_pmeas.f90
  - src/climate_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

A `*.pcp` file holds the measured precipitation time series for a single gauge. One file per station. The filename is listed in [`pcp.cli`](../input-reference/cli.md#pcpcli) and the same filename string is matched as the gauge key referenced from `pgage` in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). The reader supports either daily values or subdaily values at a fixed time step.

## Source

- Reader: [`src/cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_pmeas.f90)
- Type definition: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (the `pcp` array)

## Format

The reader uses list-directed reads (free format, whitespace-separated). The first two lines are skipped. The third line is the station header. From line four to end of file are the time-step records.

### Line 1: title

Single string, skipped.

### Line 2: column header

Skipped. SWAT+ Editor writes `NBYR    TSTEP      LAT     LONG     ELEV`.

### Line 3: station header

Read by `read (108,*,iostat=eof) pcp(i)%nbyr, pcp(i)%tstep, pcp(i)%lat, pcp(i)%long, pcp(i)%elev`.

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | nbyr  | int  | years | Number of years of record in the file. Used to size the in-memory time-series array. |
| 2 | tstep | int  | minutes | Time step. `0` means daily. A positive value is the subdaily interval in minutes and must match `time%step` from [`time.sim`](../input-reference/time-sim.md). |
| 3 | lat   | real | degrees | Latitude of the gauge. |
| 4 | long  | real | degrees | Longitude of the gauge. |
| 5 | elev  | real | m | Elevation of the gauge. |

### Records (line 4 onward)

The record layout depends on `tstep`.

For daily records (`tstep = 0`):

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | year  | int  | calendar year | Calendar year of the record. |
| 2 | jday  | int  | day-of-year | Julian day (1 to 365 or 366). |
| 3 | pcp   | real | mm | Daily precipitation depth. Use a value at or below `-97` to flag missing data; the reader replaces it with a generated value. |

For subdaily records (`tstep > 0`):

| # | Field   | Type | Units | Description |
|---|---------|------|-------|-------------|
| 1 | year    | int  | calendar year | Calendar year. |
| 2 | jday    | int  | day-of-year | Julian day. |
| 3 | mo      | int  | month | Month number. |
| 4 | day_mo  | int  | day | Day of the month. |
| 5 | ihr     | int  | step index | Sub-day step index (1 to `1440 / tstep`). |
| 6 | pcp     | real | mm | Precipitation depth for the time step. |

Records are read in order. The reader advances year-by-year using the change in `jday` (it expects the year to change after `jday = 365` or `366`).

### Missing data

The daily reader treats any value at or below `-97` as missing. Downstream in `cli_precip_control.f90`, when `precip_next <= -97.` the value is replaced by the weather generator. The classic flag written by SWAT+ Editor and the legacy tools is `-99`.

## Example

First lines of `refdata/Ames_sub1/ames.pcp`:

```
AME.pcp
 NBYR    TSTEP      LAT     LONG     ELEV
   121        0    42.04   -93.89   316
1900 1 -99
1900 2 -99
1900 3 -99
...
1983 184 0
1983 185 15.5
1983 186 0
```

Station header: 121 years, daily time step (`0`), latitude 42.04, longitude -93.89, elevation 316 m. Early years are missing (`-99`) and will be filled by the weather generator.

## Related files

- [`pcp.cli`](../input-reference/cli.md#pcpcli). Lists each `*.pcp` filename.
- [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). Binds a precipitation gauge to a weather station via `pgage`.
- [`file.cio`](../input-reference/file-cio.md). Names the `pcp.cli` index and the optional path prefix `in_path_pcp%pcp` applied to every `*.pcp` filename.
- [`time.sim`](../input-reference/time-sim.md). For subdaily files, `time%step` must equal the file's `tstep`.

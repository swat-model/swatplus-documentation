---
title: "*.tmp (temperature data)"
description: Per-gauge time-series file holding daily minimum and maximum air temperature read by SWAT+.
status: review
verified_against:
  - src/cli_tmeas.f90
  - src/climate_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

A `*.tmp` file holds the measured daily temperature time series for a single gauge. One file per station. The filename is listed in [`tmp.cli`](../input-reference/cli.md#tmpcli) and the same filename string is matched as the gauge key referenced from `tgage` in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). The reader records daily maximum and minimum air temperature.

## Source

- Reader: [`src/cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_tmeas.f90)
- Type definition: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (the `tmp` array; `ts` holds daily max, `ts2` holds daily min)

## Format

List-directed reads (free format, whitespace-separated). The first two lines are skipped. The third line is the station header. From line four to end of file are the daily records.

### Line 1: title

Single string, skipped.

### Line 2: column header

Skipped. SWAT+ Editor writes `NBYR    TSTEP      LAT     LONG     ELEV`.

### Line 3: station header

Read by `read (108,*,iostat=eof) tmp(i)%nbyr, tmp(i)%tstep, tmp(i)%lat, tmp(i)%long, tmp(i)%elev`.

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | nbyr  | int  | years | Number of years of record in the file. |
| 2 | tstep | int  | minutes | Time step indicator. Stored but the reader expects daily values regardless. |
| 3 | lat   | real | degrees | Latitude of the gauge. |
| 4 | long  | real | degrees | Longitude of the gauge. |
| 5 | elev  | real | m | Elevation of the gauge. |

### Records (line 4 onward)

Daily values only:

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | year  | int  | calendar year | Calendar year of the record. |
| 2 | jday  | int  | day-of-year | Julian day (1 to 365 or 366). |
| 3 | tmax  | real | deg C | Daily maximum air temperature. Stored in `tmp(i)%ts(jday, year_index)`. |
| 4 | tmin  | real | deg C | Daily minimum air temperature. Stored in `tmp(i)%ts2(jday, year_index)`. |

Records are read sequentially. The reader detects the year change after `jday = 365` or `366` and increments its internal year index.

While reading, the routine accumulates monthly sums into `tmp(i)%max_mon` and `tmp(i)%min_mon` (per the `xmon` call) and at end of file divides by the total day count to get the average monthly maximum and minimum. A `-99` flag is treated like any other value at this stage, so missing-data flags carry into the monthly statistics unless the file is clean over the simulation window.

## Example

First lines of `refdata/Ames_sub1/ames.tem` (the temperature time series for the Ames reference dataset; the same record layout applies to a `*.tmp` file):

```
AME.Tmp
 NBYR    TSTEP      LAT     LONG     ELEV
   121        0    42.04   -93.89   316
1900	1	-99	-99
1900	2	-99	-99
...
1983	185	32.2	10.6
1983	186	26.7	11.1
```

Station header: 121 years, time step `0`, latitude 42.04, longitude -93.89, elevation 316 m. Early years carry the `-99` missing-data flag for both max and min.

## Related files

- [`tmp.cli`](../input-reference/cli.md#tmpcli). Lists each temperature gauge filename.
- [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). Binds a temperature gauge to a weather station via `tgage`.
- [`file.cio`](../input-reference/file-cio.md). Names the `tmp.cli` index and the optional path prefix `in_path_tmp%tmp` applied to every temperature filename.
- [`*.tem`](../input-reference/tem.md). Same record layout, alternate filename extension used by some toolchains.

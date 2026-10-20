---
title: "*.tmp (temperature data)"
description: Measured daily maximum and minimum air temperature for one gauge, listed in tmp.cli and used by weather stations in weather-sta.cli.
status: review
verified_against:
  - src/cli_tmeas.f90
  - src/climate_control.f90
  - src/cli_bounds_check.f90
  - src/cli_staread.f90
  - src/search.f90
  - src/climate_module.f90
  - src/cli_tgen.f90
  - src/cli_weatgn.f90
  - src/cli_lapse.f90
  - src/hru_control.f90
  - src/readcio_read.f90
  - src/input_file_module.f90
  - src/cal_conditions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A temperature data file contains the measured daily maximum and minimum air temperature of one gauge. Each file is named on one line of [`tmp.cli`](cli.md#observed-data-lists), and a weather station uses it when the `tmp` column of [`weather-sta.cli`](cli.md#weather-stacli) gives the same name. Days without usable values are filled by the weather generator station named in the `wgn` column of the same weather station.

SWAT+ does not check the file extension. SWAT+ Editor writes `.tmp`; some older data sets use [`.tem`](tem.md). If `tmp_path` in [`file.cio`](file-cio.md) is not `null`, its value is put in front of every file name in [`tmp.cli`](../input-reference/cli.md#observed-data-lists) (see [path prefixes](cli.md#path-prefixes)).

Temperature is always read as daily data, also in sub-daily runs.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is a column header; both are skipped. Line 3 describes the gauge and every later line is one daily record.

### Gauge line

SWAT+ Editor writes the header `nbyr tstep lat lon elev` above this line.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `nbyr` | years | Number of years of record. SWAT+ uses it to size the store for the data, so it must be at least the number of calendar years the record spans. |
| 2 | `tstep` | - | Time step of the data. Not used by SWAT+; give `0`. |
| 3 | `lat` | decimal degrees | Latitude of the gauge. Not used by SWAT+. |
| 4 | `lon` | decimal degrees | Longitude of the gauge. Not used by SWAT+. |
| 5 | `elev` | m | Elevation of the gauge. Used only for the [elevation adjustment](#elevation-adjustment). |

### Daily records

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | year | - | Calendar year. |
| 2 | day | - | Day of the year, 1 to 366. Called `jday` in earlier documentation. |
| 3 | tmax | °C | Maximum air temperature for the day, called `tmpmax` in earlier documentation. A value of -97 or less marks it as missing. |
| 4 | tmin | °C | Minimum air temperature for the day, called `tmpmin` in earlier documentation. A value of -97 or less marks it as missing. |

Records must be continuous and in date order, as for precipitation: SWAT+ counts years by watching for day 365 or 366 followed by a record from a new year. Records before the simulation start are skipped when the file is read, by the rule described for [precipitation files](pcp.md#reading-and-storage).

## Missing days

SWAT+ generates both temperatures for a day when

- `tmax` or `tmin` is -97 or less (SWAT+ Editor and most tools write -99), or
- the day is before the first record or after the last record of the file.

When only one of the two values is missing, the measured value of the other is replaced by a generated one as well, so the pair always comes from one source. The generated maximum is lower on wet days than on dry days, using the day's precipitation from the same weather station. The method is described in [Climate and weather](../model-theory/climate-weather.md#weather-generator).

The daily mean air temperature used by snow, plant growth and other processes is

$$T_{av} = \frac{T_{max} + T_{min}}{2}$$

## Elevation adjustment

When `lapse` = 1 in [`codes.bsn`](codes-bsn.md), the temperatures of each HRU are changed for the difference between the gauge elevation and the HRU elevation:

$$T_{hru} = T + \mathrm{tlaps}\,\frac{z_{gauge} - z_{hru}}{1000}$$

applied to the maximum, minimum and mean temperature. `tlaps` is the temperature lapse rate in [`parameters.bsn`](parameters-bsn.md) (°C per km, default 6.5), $z_{hru}$ is the `elev` column of [`hru.con`](con.md) and $z_{gauge}$ is `elev` from this file (m). When the station's `tmp` column is `sim`, the elevation of the weather generator station is used for $z_{gauge}$. As for precipitation, the adjustment values are calculated during channel and reservoir routing, so in a model without channels or reservoirs they remain zero.

## Calibration

The calibration parameter `temp` (object type `cli`) is meant to change the stored values of listed temperature records, but in 62.0.1 it does not change the listed records. See [Climate changes](../calibration/hard-calibration.md#climate-changes).

## Example

First lines of `refdata/Osu_1hru/Imsiltmp.tmp` in the SWAT+ repository:

```
Imsiltmp.tmp: Temperature data - file written by SWAT+ editor 2023-03-22 04:22:29.141050
nbyr     tstep       lat       lon      elev
  42         0    35.610   127.290   247.900
1981    1    2.70000   -17.50000
1981    2   -3.00000    -7.50000
...
2023  364        2.3        -4.3
2023  365        0.8        -8.4
```

A daily record from 1 January 1981 to 31 December 2023 at 247.9 m. The record spans 43 calendar years while `nbyr` is 42. The Osu run starts in 2010, so only the 14 years from 2010 are stored and the smaller `nbyr` does no harm here; a run starting in 1981 would need `nbyr` of at least 43.

## Related files

- [`tmp.cli`](cli.md#observed-data-lists): lists the temperature files.
- [`weather-sta.cli`](cli.md#weather-stacli): assigns a temperature file to each weather station in its `tmp` column.
- [`weather-wgn.cli`](cli.md#weather-wgncli): weather generator statistics that fill missing days.
- [`*.tem`](tem.md): the same format under another extension.
- [`file.cio`](file-cio.md): names [`tmp.cli`](../input-reference/cli.md#observed-data-lists) and the `tmp_path` prefix.
- [`codes.bsn`](codes-bsn.md) and [`parameters.bsn`](parameters-bsn.md): `lapse` switch and `tlaps` rate.
- [`snow.sno`](sno.md): snowfall and melt use the daily mean and maximum temperature.

??? quote "Sources"

    - Reader: [`cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tmeas.f90)
    - Type definition: `type climate_measured_data` in [`climate_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_module.f90)
    - Gauge name lookup from `weather-sta.cli`: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90), [`search.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/search.f90)
    - Daily use, missing values and range check: [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90), [`cli_bounds_check.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_bounds_check.f90)
    - Weather generator: [`cli_weatgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_weatgn.f90), [`cli_tgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tgen.f90)
    - Elevation adjustment: [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90), applied in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Path prefix: `in_path_tmp` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Calibration change `temp`: [`cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `nbyr` | `tmp(i)%nbyr` |
    | `tstep` | `tmp(i)%tstep` |
    | `lat` | `tmp(i)%lat` |
    | `lon` | `tmp(i)%long` |
    | `elev` | `tmp(i)%elev` |
    | tmax | `tmp(i)%ts(day, iyr)` |
    | tmin | `tmp(i)%ts2(day, iyr)` |

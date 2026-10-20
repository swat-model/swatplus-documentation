---
title: "*.tem (temperature data, older extension)"
description: Temperature data file with the .tem extension. Same format and handling as a .tmp file.
status: review
verified_against:
  - src/cli_tmeas.f90
  - src/cli_staread.f90
  - src/search.f90
  - src/climate_control.f90
  - src/climate_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`.tem` is an older extension for temperature data files, used by some data sets and preprocessing tools. SWAT+ opens a temperature file by the name given in [`tmp.cli`](cli.md#observed-data-lists) and does not look at the extension, so a `.tem` file is read in the same way as a [`.tmp`](tmp.md) file. SWAT+ Editor writes `.tmp`.

The name has to be the same, extension included, in two places:

- a line of [`tmp.cli`](../input-reference/cli.md#observed-data-lists), which tells SWAT+ to read the file, and
- the `tmp` column of [`weather-sta.cli`](cli.md#weather-stacli), which assigns it to a weather station.

If the `tmp` column names a file that is not listed in [`tmp.cli`](../input-reference/cli.md#observed-data-lists), SWAT+ writes `<name> file not found (tgage)` to `diagnostics.out` and generates the temperatures of that station for the whole run.

## Format

The format is that of a [`.tmp` file](tmp.md#format): a title line, a header line, a gauge line with `nbyr`, `tstep`, `lat`, `lon` and `elev`, and one record per day with year, day of year, maximum and minimum temperature in °C. Values of -97 or less mark missing data.

## Example

`refdata/Ames_sub1/ames.tem` in the SWAT+ repository:

```
AME.Tmp
 NBYR    TSTEP      LAT     LONG     ELEV
   121        0    42.04   -93.89   316
1900	1	-99	-99
1900	2	-99	-99
...
1975	1	4.4	-7.2
1975	2	5	-7.8
...
2020	365	-1.7	-7.8
2020	366	-2.8	-8.9
```

A daily record of 121 years, 1900 to 2020, separated by tabs, which free-format reading accepts. In this data set the `tmp` column of [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) names `ames.tem`, while [`tmp.cli`](../input-reference/cli.md#observed-data-lists) lists `ames.tmp`, which is an empty file. SWAT+ therefore does not find `ames.tem`, never reads it, and generates the temperatures of the Ames run. Listing `ames.tem` in [`tmp.cli`](../input-reference/cli.md#observed-data-lists) instead of `ames.tmp` makes the run use the measured record.

## Related files

- [`*.tmp`](tmp.md): the same format; missing values, elevation adjustment and storage are described there.
- [`tmp.cli`](cli.md#observed-data-lists): lists the temperature files to read.
- [`weather-sta.cli`](cli.md#weather-stacli): assigns a temperature file to each weather station.

??? quote "Sources"

    - Reader: [`cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tmeas.f90)
    - Type definition: `type climate_measured_data` in [`climate_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_module.f90)
    - Name lookup and the `file not found (tgage)` message: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90), [`search.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/search.f90)
    - Daily use: [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90)

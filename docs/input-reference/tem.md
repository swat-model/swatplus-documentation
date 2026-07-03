---
title: "*.tem (temperature data, alternate extension)"
description: Temperature time-series file using the .tem extension. Same record layout as a .tmp file.
status: review
verified_against:
  - src/cli_tmeas.f90
  - src/climate_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

A `*.tem` file is a temperature time-series file with the same record layout as a [`*.tmp`](../input-reference/tmp.md). The `.tem` extension is used by the reference datasets shipped with SWAT+ (for example `refdata/Ames_sub1/ames.tem`) and by some external preprocessors. There is no separate reader for `.tem`. The temperature reader at `src/cli_tmeas.f90` opens whatever filename is supplied; the extension is not inspected.

## Source

- Reader: [`src/cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_tmeas.f90)
- Type definition: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data`

The reader is reached only when the filename appears in [`tmp.cli`](../input-reference/cli.md#tmpcli). The `tgage` slot in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) is matched against the filename listed in `tmp.cli` via the `tmp_n` lookup array, so both files must agree on the string (including the `.tem` extension if used).

## Format

Identical to a daily `*.tmp` file. List-directed reads, whitespace-separated.

- Line 1: title (skipped).
- Line 2: column header (skipped). Conventionally `NBYR    TSTEP      LAT     LONG     ELEV`.
- Line 3: station header (`nbyr`, `tstep`, `lat`, `long`, `elev`).
- Line 4 onward: one record per day with year, Julian day, daily maximum temperature, daily minimum temperature.

See [`*.tmp`](../input-reference/tmp.md#format) for the field tables.

## Example

`refdata/Ames_sub1/ames.tem` (excerpt):

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

## Related files

- [`*.tmp`](../input-reference/tmp.md). Same content, alternate extension. The reader is shared.
- [`tmp.cli`](../input-reference/cli.md#tmpcli). Lists each temperature filename (with whatever extension).
- [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). The `tgage` column must match a filename entry in `tmp.cli`.

---
title: "snow.sno"
description: Snow parameter database. One row per snow parameter set, referenced by name from each HRU.
status: review
verified_against:
  - src/snowdb_read.f90
  - src/hru_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`snow.sno` is the snow parameter database. Each row defines a named set of snow accumulation and melt parameters. HRUs reference a row by name through the `snow` column of [`hru-data.hru`](../input-reference/hru.md), which the reader resolves to an index into the `snodb` array. If `hru-data.hru` carries `null` for an HRU's snow entry, that HRU uses the default `snow_parameters` values.

## Source

- Reader: [`src/snowdb_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/snowdb_read.f90)
- Type definition: [`src/hru_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_module.f90), `type snow_parameters` (the `snodb` array)
- Filename slot: `in_parmdb%snow` in [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90) (default `snow.sno`).

## Format

List-directed reads (free format, whitespace-separated). The first two lines are skipped. From line three to end of file each line is one snow parameter row. The reader counts records on a first pass, allocates `snodb(0:imax)`, then reads each row into `snodb(isno)`.

- Line 1: title (skipped). Editor convention: `snow.sno: written by SWAT+ editor ...`.
- Line 2: column header (skipped). Editor convention: `name  fall_tmp  melt_tmp  melt_max  melt_min  tmp_lag  snow_h2o  cov50  snow_init`.
- Line 3+: one row per parameter set, 9 fields each.

The fields appear in the order declared in `type snow_parameters`:

| # | Field    | Type     | Units         | Default | Description |
|---|----------|----------|---------------|---------|-------------|
| 1 | name     | char(40) | -             | (none)  | Parameter set name. Referenced from the `snow` column of `hru-data.hru`. |
| 2 | falltmp  | real     | deg C         | 0.0     | Snowfall temperature. Precipitation falls as snow when the mean air temperature is at or below this threshold. |
| 3 | melttmp  | real     | deg C         | 0.5     | Snowmelt base temperature. Snowmelt only occurs when the snowpack temperature exceeds this value. |
| 4 | meltmx   | real     | mm/deg C/day  | 4.5     | Maximum melt rate factor for snow during the year (occurs near 21 June). |
| 5 | meltmn   | real     | mm/deg C/day  | 0.5     | Minimum melt rate factor for snow during the year (occurs near 21 December). |
| 6 | timp     | real     | none          | 0.8     | Snowpack temperature lag factor (0 to 1). Higher values give more weight to the current day's air temperature. |
| 7 | covmx    | real     | mm H2O        | 25.0    | Snow water content above which the ground is fully covered by snow. |
| 8 | cov50    | real     | none          | 0.5     | Fraction of `covmx` at which the ground is 50% snow-covered. Shape factor for the snowpack areal depletion curve. |
| 9 | init_mm  | real     | mm H2O        | 0.0     | Initial snow water content at the start of the simulation. |

The defaults above are the values assigned in `type snow_parameters` at declaration. They are not values the reader supplies, so every row of `snow.sno` must list all nine fields.

## Example

`refdata/Ames_sub1/snow.sno`:

```
snow.sno: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                  fall_tmp      melt_tmp      melt_max      melt_min       tmp_lag      snow_h2o         cov50     snow_init
snow001                1.00000       0.50000       4.50000       4.50000       1.00000       1.00000       0.50000       0.00000
```

One parameter set named `snow001`. Note that the example value for `meltmn` (column 5) is `4.5`, identical to `meltmx`. The defaults shipped in source set `meltmn = 0.5`.

## Related files

- [`hru-data.hru`](../input-reference/hru.md). References a `snow.sno` row by name in its `snow` column. `null` selects the type defaults.
- [`file.cio`](../input-reference/file-cio.md). Names the `snow.sno` file in the `init` group via `in_parmdb%snow`. Set to `null` to skip reading (no snow database is loaded; HRUs that point at a snow name will fall back as described above).

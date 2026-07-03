---
title: print.prt
description: Output print codes. Selects which output files SWAT+ writes and at what aggregation.
status: review
verified_against:
  - src/basin_print_codes_read.f90
  - src/basin_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`print.prt` controls every output the model writes. It sets the print window in calendar time, the daily print interval, the average-annual print intervals, three database-output toggles, four "other output" toggles, and one row per output object with four print-frequency flags (daily, monthly, yearly, average annual).

If `print.prt` is missing or set to `null` in `file.cio`, the model still runs but writes no time-stepped output.

## Source

- Reader: [`src/basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_print_codes_read.f90)
- Type definitions: [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_module.f90). See `type basin_print_codes` (`pco`) and `type print_interval`.

## Format

The file has fixed top-of-file blocks followed by one row per output object. There are two object-row modes, selected by the `use_obj_lbls` flag in the third block. The reader skips a header line before each block.

### Block 1: window

- Line 1: title (skipped).
- Line 2: header (skipped).
- Line 3: six integers.

| # | Name | Description | Default if unset |
|---|------|-------------|------------------|
| 1 | nyskip | number of warm-up years to skip in average-annual summaries | 0 |
| 2 | day_start | julian day to start daily printing | forced to 1 if 0 |
| 3 | yrc_start | calendar year to start daily printing | `time%yrc` from `time.sim` |
| 4 | day_end | julian day to end daily printing | forced to 366 if 0 |
| 5 | yrc_end | calendar year to end daily printing | `time%yrc + time%nbyr` |
| 6 | interval | days between daily prints | forced to 1 if `<= 0` |

### Block 2: average-annual print intervals

- Line 4: header (skipped).
- Line 5: `aa_numint` followed by `aa_numint` year values. If `aa_numint = 0`, only the value is read.

`aa_numint` is the number of end-years to use for average-annual outputs. When it is greater than zero, average-annual statistics are produced once for each interval defined by the listed end years.

### Block 3: database output toggles

- Line 6: header (skipped).
- Line 7: three single-character flags.

| Name | Values | Meaning |
|------|--------|---------|
| csvout | `n`, `y` | also write `.csv` versions of outputs |
| use_obj_lbls | `n`, `y` | object-row mode (see [Object rows](#object-rows)) |
| cdfout | `n`, `y` | also write netCDF (`.nc`) versions of outputs |

### Block 4: other output toggles

- Line 8: header (skipped).
- Line 9: four single-character flags.

| Name | Values | Meaning |
|------|--------|---------|
| crop_yld | `a`, `y`, `b`, `n` | crop yields: `a` average annual, `y` yearly, `b` both, `n` no print |
| mgtout | `n`, `y` | write `mgt_out.txt` (management operations log) |
| hydcon | `n`, `y` | write `hydcon.out` (hydrograph connections) |
| fdcout | `n`, `y` | flow duration curve. Read but the type comment notes "NOT ACTIVE" |

### Object rows

- Line 10: header (`objects daily monthly yearly avann`), skipped.
- Lines 11 and following: one row per output object. Each row has five fields: a name and four flags (`d`, `m`, `y`, `a`) with values `n` or `y`.

The reader interprets the rows in one of two modes:

- `use_obj_lbls = n` (positional): the reader expects rows in a fixed order. The name column is read but discarded. Missing or extra rows cause silent skips of later objects when the loop hits end-of-file.
- `use_obj_lbls = y` (labelled): rows can be in any order. The reader matches the first column against a list of recognised names. Repeated rows for the same object are flagged via `print_prt_error`. Unknown names cause the model to print an error and `error stop`.

#### Recognised object names (labelled mode)

| Group | Names |
|-------|-------|
| Basin | `basin_wb`, `basin_nb`, `basin_ls`, `basin_pw`, `basin_aqu`, `basin_res`, `basin_cha`, `basin_sd_cha`, `basin_psc` |
| Region | `region_wb`, `region_nb`, `region_ls`, `region_pw`, `region_aqu`, `region_res`, `region_sd_cha`, `region_psc`, `water_allo` |
| LSU | `lsunit_wb`, `lsunit_nb`, `lsunit_ls`, `lsunit_pw` |
| HRU | `hru_wb`, `hru_nb`, `hru_ls`, `hru_pw`, `hru_cb`, `hru_cb_vars` |
| HRU-lte | `hru-lte_wb`, `hru-lte_nb`, `hru-lte_ls`, `hru-lte_pw` |
| Other | `channel`, `channel_sd`, `aquifer`, `reservoir`, `recall`, `hyd`, `ru`, `pest` |
| Salt | `basin_salt`, `hru_salt`, `ru_salt`, `aqu_salt`, `channel_salt`, `res_salt`, `wetland_salt` |
| Constituents | `basin_cs`, `hru_cs`, `ru_cs`, `aqu_cs`, `channel_cs`, `res_cs`, `wetland_cs` |
| gwflow | `gwflow_wb`, `gwflow_flux`, `gwflow_heat`, `gwflow_solute`, `gwflow_obs`, `gwflow_pump` |

Each row's four flags map to the `print_interval` fields `d`, `m`, `y`, `a` (daily, monthly, yearly, average annual). Value `y` enables that aggregation. Value `n` disables it.

The HRU carbon rows `hru_cb` and `hru_cb_vars` drive the legacy CSU carbon output files (alongside the standardised per-family carbon outputs). SWAT+ Editor does not write these rows; the CSU team adds them by hand. The `hru_cb` flag letter selects detail (`l` = full per-layer set with diagnostics, `y` = light profile set). See the [carbon outputs reference](../output-reference/carbon.md#legacy-csu-carbon-outputs).

## Example

`refdata/Ames_sub1/print.prt`:

```
print.prt:
nyskip      day_start  yrc_start  day_end   yrc_end   interval
0           0               1975         0     2020         1
aa_int_cnt
0
csvout        use_obj_lbls  cdfout
n             n             n
crop_yld      mgtout        hydcon        fdcout
b             y             n             n
objects                  daily       monthly        yearly         avann
basin_wb                     n             n             n             y
basin_nb                     n             n             n             y
basin_ls                     n             n             n             y
basin_pw                     n             n             n             y
basin_aqu                    n             n             n             y
...
```

Window: print over 1975 to 2020, daily interval 1, no warm-up. `aa_int_cnt = 0` means a single average-annual interval over the whole period. CSV and netCDF off. Crop yields in both average-annual and yearly form. Management log on. `use_obj_lbls = n` so the rows are in fixed order.

## Related files

- [`time.sim`](../input-reference/time-sim.md). Defines the simulation period that bounds these print windows.
- [Output reference](../output-reference/index.md). Documents each output file produced when the corresponding row is enabled.

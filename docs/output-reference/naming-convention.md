---
title: Output naming convention
description: How SWAT+ assembles output filenames from scope, group, and interval, and how print.prt toggles each one.
status: review
verified_against:
  - src/output_landscape_init.f90
  - src/header_aquifer.f90
  - src/header_channel.f90
  - src/header_sd_channel.f90
  - src/header_reservoir.f90
  - src/header_write.f90
  - src/print_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Filename grammar

```
<scope>_<group>_<interval>.<ext>
```

- `scope` identifies the spatial unit.
- `group` identifies the variable family.
- `interval` identifies the time aggregation.
- `ext` is `txt` (always) and `csv` (when `csvout = y` in `print.prt`).

Examples that the source actually opens:

```
hru_wb_day.txt
hru_wb_mon.txt
hru_wb_yr.txt
hru_wb_aa.txt
basin_wb_aa.txt
lsunit_wb_aa.txt
hru-lte_wb_aa.txt
hru_nb_aa.txt
hru_ls_aa.txt
hru_pw_aa.txt
basin_aqu_aa.txt
basin_res_aa.txt
basin_cha_aa.txt
basin_sd_cha_aa.txt
channel_sd_day.txt
channel_day.txt
aquifer_day.txt
reservoir_day.txt
crop_yld_aa.txt
crop_yld_yr.txt
```

## Scopes

The scope prefix maps to a writer subroutine:

| Scope | Writer | Loop body |
|-------|--------|-----------|
| `hru_` | `hru_output.f90` | one record per HRU |
| `hru-lte_` | `hru_lte_output.f90` | one record per HRU-LTE |
| `lsunit_` | `lsu_output.f90` | one record per landscape unit |
| `ru_` | `ru_output.f90` | one record per routing unit |
| `region_` | `lsreg_output.f90` | one record per region per landuse |
| `basin_` | `basin_output.f90`, `basin_aquifer_output.f90`, `basin_channel_output.f90`, `basin_sdchannel_output.f90`, `basin_reservoir_output.f90` | one record (basin sum or average) |
| `channel_` | `channel_output.f90` | one record per legacy channel object |
| `channel_sd` (file group `sd_cha`) | `sd_channel_output.f90` | one record per sd_channel object |
| `aquifer_` | `aquifer_output.f90` | one record per aquifer |
| `reservoir_` | `reservoir_output.f90` | one record per reservoir |
| `wetland_` | `wetland_output.f90` | one record per wetland |
| `recall_` | `recall_output.f90` | one record per recall object |
| `crop_yld_` | `hru_output.f90` (last block) | one record per HRU per plant |

## Groups

The group token identifies the column family. Each writer holds its own Fortran derived type and the columns are the fields of that type in declaration order.

| Group | Type | Module |
|-------|------|--------|
| `_wb` | `output_waterbal` | `src/output_landscape_module.f90` |
| `_nb` | `output_nutbal` | `src/output_landscape_module.f90` |
| `_ls` | `output_losses` | `src/output_landscape_module.f90` |
| `_pw` | `output_plantweather` | `src/output_landscape_module.f90` |
| `_cha` | `ch_output` | `src/channel_module.f90` |
| `_sd_cha` | `water_body` plus two `hyd_output` records (in, out) | `src/water_body_module.f90`, `src/hydrograph_module.f90` |
| `_aqu` | `aquifer_dynamic` | `src/aquifer_module.f90` |
| `_res` | `water_body` plus two `hyd_output` records (in, out) | `src/water_body_module.f90`, `src/hydrograph_module.f90` |
| `_pest` | pesticide processes types | `src/output_ls_pesticide_module.f90`, others |
| `_salt` | salt ion types | `src/salt_module.f90` |
| `_cs` | constituents types | `src/cs_module.f90` |
| `_carbon`, `_soilcarb`, `_rescarb`, `_plcarb` | carbon pool types | `src/output_landscape_module.f90`, `src/carbon_module.f90` |

## Intervals

| Suffix | Meaning | `print.prt` column |
|--------|---------|--------------------|
| `_day` | one row per day | `daily` |
| `_mon` | one row per month | `monthly` |
| `_yr` | one row per year | `yearly` |
| `_aa` | one row, average annual over the print window | `avann` |

The print window is the simulation range minus `nyskip` warm-up years (set in the first table of `print.prt`).

## print.prt toggle

`print.prt` has a table of object groups, one row per group, with four columns (`daily`, `monthly`, `yearly`, `avann`). Each cell is `y` or `n`. The file is opened only if the cell is `y`. The toggles set `pco%<group>%<d|m|y|a>` (read in `print_read.f90`) and the file is opened in `output_landscape_init.f90` or one of the `header_*.f90` files.

Example: in `refdata/Ames_sub1/print.prt`, the row

```
hru_wb                       n             n             n             y
```

opens `hru_wb_aa.txt` only. The other three (`day`, `mon`, `yr`) are not written.

A separate row, `csvout`, switches on the matching `.csv` variant for every enabled file.

`crop_yld` in `print.prt` accepts `n`, `a` (annual only), `y` (yearly only), or `b` (both). Other groups use the four-column form.

## Subdaily output

When `time%step > 1` (subdaily simulation), additional `*_subday.txt` files are written. The current subdaily channel writer is in `sd_channel_output.f90` (`channel_sd_subday.txt`, unit 2508).

## Always-on outputs

A few files are not controlled by `print.prt` and are written every run:

- `simulation.out`. Daily progress log written from `main.f90` and `time_control.f90`.
- `files_out.out`. Index of every output file opened, written from `proc_bsn.f90`.
- `diagnostics.out`. Warnings about missing input references, opened in `proc_bsn.f90`.
- `checker.out`. HRU-level parameter sanity dump, written in `proc_hru.f90`.
- `erosion.out`. USLE inputs and outputs per HRU.
- `success.fin`. Empty marker created on successful completion.

See [Checker and diagnostics](../output-reference/checker-diagnostics.md) for the column-level breakdown.

---
title: Output naming convention
description: How SWAT+ names its output files, where it writes them, how they are laid out, and which print.prt row opens each one.
status: review
verified_against:
  - src/basin_print_codes_read.f90
  - src/basin_module.f90
  - src/output_path_module.f90
  - src/readcio_read.f90
  - src/proc_open.f90
  - src/proc_bsn.f90
  - src/proc_hru.f90
  - src/output_landscape_init.f90
  - src/header_write.f90
  - src/header_sd_channel.f90
  - src/header_channel.f90
  - src/header_aquifer.f90
  - src/header_reservoir.f90
  - src/header_wetland.f90
  - src/header_hyd.f90
  - src/header_yield.f90
  - src/header_mgt.f90
  - src/header_lu_change.f90
  - src/header_pest.f90
  - src/header_path.f90
  - src/header_salt.f90
  - src/header_const.f90
  - src/header_water_allocation.f90
  - src/time_control.f90
  - src/command.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Filename pattern

Most time-step outputs are named

```
<object>_<group>_<interval>.txt
```

for example `hru_wb_day.txt` (HRU water balance, daily) or `basin_sd_cha_aa.txt` (basin sum of channel outputs, average annual). Some files have no group (`aquifer_day.txt`, `reservoir_mon.txt`, `ru_yr.txt`), and a few files written once per run have no interval (`hru_cbn_lyr.txt`, `mgt_out.txt`).

| Interval | Meaning | [`print.prt`](../input-reference/print-prt.md) column |
|----------|---------|--------------------|
| `_day` | one row per object per day | `daily` |
| `_mon` | one row per object per month | `monthly` |
| `_yr` | one row per object per year | `yearly` |
| `_aa` | one row per object, average annual over the printed years | `avann` |

The channel sediment budget files `ch_sedbud_*` and `chanbud_order_*` use `_d`, `_m`, `_y` and `_a` instead.

When `csvout` is `y` in [`print.prt`](../input-reference/print-prt.md), most time-step files also get a comma-separated copy with the same name and the extension `.csv`.

## Output folder

Output files are written to the folder named on the output path line at the end of [`file.cio`](../input-reference/file-cio.md). SWAT+ creates the folder if it does not exist. When the line is missing, empty or `null`, outputs go to the folder SWAT+ runs in. `simulation.out`, `success.fin` and `erosion.txt` always go to the run folder.

## File layout

Time-step files share one layout:

- Line 1: the project name from [`file.cio`](../input-reference/file-cio.md) and the SWAT+ version banner.
- Line 2: column headers.
- Line 3: units (blank for columns without units).
- Lines 4 and on: data rows.

Rows with one object per row start with `jday`, `mon`, `day`, `yr`, `unit`, `gis_id` and `name`. Basin files use the same columns with `unit` and `gis_id` set to 1. `jday`, `mon`, `day` and `yr` are the date of the last day in the print step.

## Print timing

The first blocks of [`print.prt`](../input-reference/print-prt.md) set when rows are written:

- Daily rows are written from `day_start` of `yrc_start` to `day_end` of `yrc_end`, every `interval` days. A zero `day_start` means day 1, a zero `day_end` means day 366, and zero years mean the first and last simulated year.
- Monthly, yearly and average annual rows start after the first `nyskip` simulated years. Average annual values are averages over the remaining years.
- The average annual print intervals (`aa_int_cnt` and the end years that follow it) are read, but in 62.0.1 they are used only by the region output, which is not written, so they have no effect.

## print.prt rows and files

Each row in the objects block of [`print.prt`](../input-reference/print-prt.md) has a name and four `y`/`n` switches. When `use_obj_lbls` is `y`, rows are matched by name, may come in any order, and rows can be left out (they default to `n`). A name that appears twice stops the run with an error, and so does a name SWAT+ does not know. When `use_obj_lbls` is `n`, the rows are read by position and must follow the order of the table below up to `wetland_cs`; the carbon and gwflow rows can only be set in labelled mode.

Each `y` opens the file for that interval. The table shows the file stems; add `_day.txt`, `_mon.txt`, `_yr.txt` or `_aa.txt`.

| [`print.prt`](../input-reference/print-prt.md) row | Files | Described in |
|-----------------|-------|--------------|
| `basin_wb` | `basin_wb` | [Water balance](water-balance.md) |
| `basin_nb` | `basin_nb` | [Nutrient balance and losses](nutrient-balance.md) |
| `basin_ls` | `basin_ls` | [Nutrient balance and losses](nutrient-balance.md) |
| `basin_pw` | `basin_pw` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `basin_aqu` | `basin_aqu` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `basin_res` | `basin_res` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `basin_cha` | `basin_cha` (legacy channels) | [Channel and sediment](channel-sediment-nutrient.md) |
| `basin_sd_cha` | `basin_sd_cha`, `basin_sd_chamorph`, `basin_sd_chanbud` | [Channel and sediment](channel-sediment-nutrient.md) |
| `basin_psc` | `basin_psc` (recall objects summed) | [Recall](recall.md) |
| `region_wb`, `region_nb`, `region_ls`, `region_pw`, `region_aqu`, `region_res`, `region_sd_cha`, `region_psc` | none in 62.0.1 | |
| `water_allo` | `water_allo`, `wallo_use`, `wallo_treat` | [Water allocation](../input-reference/water-allocation.md) |
| `lsunit_wb` | `lsunit_wb` | [Water balance](water-balance.md) |
| `lsunit_nb`, `lsunit_ls`, `lsunit_pw` | `lsunit_nb`, `lsunit_ls`, `lsunit_pw` | [Nutrient balance and losses](nutrient-balance.md), [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `hru_wb` | `hru_wb`; also `hru_path` when constituents are simulated | [Water balance](water-balance.md) |
| `hru_nb` | `hru_nb`, `hru_ncycle` | [Nutrient balance and losses](nutrient-balance.md) |
| `hru_ls` | `hru_ls` | [Nutrient balance and losses](nutrient-balance.md) |
| `hru_pw` | `hru_pw` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `hru-lte_wb`, `hru-lte_nb`, `hru-lte_ls`, `hru-lte_pw` | `hru-lte_wb`, `hru-lte_ls`, `hru-lte_pw` | [Water balance](water-balance.md), [Nutrient balance and losses](nutrient-balance.md), [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `channel` | `channel` (legacy channels) | [Channel and sediment](channel-sediment-nutrient.md) |
| `channel_sd` | `channel_sd`, `channel_sdmorph`, `sd_chanbud`, `sedbud`, `ch_sedbud`, `chanbud_order`, `channel_sd_subday.txt` | [Channel and sediment](channel-sediment-nutrient.md) |
| `aquifer` | `aquifer` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `reservoir` | `reservoir`, `wetland` | [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) |
| `recall` | `recall` | [Recall](recall.md) |
| `hyd` | `hydin`, `hydout`, `deposition` | [Hydrographs](hydrographs.md) |
| `ru` | `ru` (routing unit hydrographs) | [Hydrographs](hydrographs.md) |
| `pest` | `hru_pest`, `channel_pest`, `reservoir_pest`, `aquifer_pest`, `basin_ls_pest`, `basin_ch_pest`, `basin_res_pest`, `basin_aqu_pest` | |
| `basin_salt`, `hru_salt`, `ru_salt`, `aqu_salt`, `channel_salt`, `res_salt`, `wetland_salt` | `basin_salt`, `hru_salt`, `rout_unit_salt`, `aquifer_salt`, `channel_salt`, `reservoir_salt`, `wetland_salt` | [Salts](../input-reference/salt.md) |
| `basin_cs`, `hru_cs`, `ru_cs`, `aqu_cs`, `channel_cs`, `res_cs` | `basin_cs`, `hru_cs`, `rout_unit_cs`, `aquifer_cs`, `channel_cs`; `res_cs` opens both `reservoir_cs` and `wetland_cs` | [Constituents](../input-reference/cs.md) |
| `wetland_cs` | none (wetland constituent files follow `res_cs`) | |
| `hru_cb`, `hru_cb_vars`, `hru_cb_gl`, `hru_cb_trf`, `hru_cb_lyr`, `hru_cb_cpool`, `hru_cb_npool`, `hru_cb_plt`, `hru_cb_flux`, `hru_cb_drv`, `hru_cb_dyn`, `hru_cb_snap`, `lsu_cb_gl`, `lsu_cb_trf`, `lsu_cb_plt` | carbon files | [Carbon](carbon.md) |
| `gwflow_wb`, `gwflow_flux`, `gwflow_heat`, `gwflow_solute`, `gwflow_obs`, `gwflow_pump` | gwflow files | [gwflow](gwflow.md) |

The rows `hru-lte_nb` and `region_*` are read but open no files in 62.0.1.

### Other switches

The line after `csvout` in [`print.prt`](../input-reference/print-prt.md) has four more switches:

| Switch | Values | Files |
|--------|--------|-------|
| `crop_yld` | `a` (average annual), `y` (yearly), `b` (both), `n` | `crop_yld_aa.txt`, `crop_yld_yr.txt`, `basin_crop_yld_aa.txt`, `basin_crop_yld_yr.txt`; `y` and `b` also open `yield.out` |
| `mgtout` | `y`, `n` | `mgt_out.txt`, the log of management operations |
| `hydcon` | `y`, `n` | `hydcon.out`, the object connection list (see [Hydrographs](hydrographs.md#hydconout)) |
| `fdcout` | `y`, `n` | `flow_duration_curve.out` |

`cdfout` (netCDF output) is read but not used.

## Files written every run

| File | Content |
|------|---------|
| `files_out.out` | List of every output file opened in the run, with a short tag. |
| `diagnostics.out` | Warnings about missing or unmatched inputs. |
| `checker.out` | Soil and HRU parameter summary. |
| `erosion.out` | USLE factors per HRU. |
| `area_calc.out` | Area checks for routing units and landscape units. |
| `lu_change_out.txt` | Land use and parameter changes made by decision tables. |
| `simulation.out` | Run log. |
| `success.fin` | Written when the run finishes normally. |

See [Checker and diagnostics](checker-diagnostics.md) for their contents.

## Related files

- [`print.prt`](../input-reference/print-prt.md): the switches described on this page.
- [`file.cio`](../input-reference/file-cio.md): names the output folder.
- [Output reference](index.md): overview of the output pages.

??? quote "Sources"

    - `print.prt` reader: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90); switch type `basin_print_codes` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - Output folder: [`output_path_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_path_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Header writers called at startup: [`proc_open.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_open.f90), which calls [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90), [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90), [`header_sd_channel.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_sd_channel.f90) and the other `header_*.f90` routines
    - Files written every run: [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90), [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90), [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - Print window: [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)

    | `print.prt` item | Fortran variable |
    |------------------|------------------|
    | `nyskip`, `day_start`, `yrc_start`, `day_end`, `yrc_end`, `interval` | `pco%nyskip`, `pco%day_start`, `pco%yrc_start`, `pco%day_end`, `pco%yrc_end`, `pco%int_day` |
    | `aa_int_cnt` and end years | `pco%aa_numint`, `pco%aa_yrs` |
    | `csvout`, `use_obj_lbls`, `cdfout` | `pco%csvout`, `pco%use_obj_labels`, `pco%cdfout` |
    | `crop_yld`, `mgtout`, `hydcon`, `fdcout` | `pco%crop_yld`, `pco%mgtout`, `pco%hydcon`, `pco%fdcout` |
    | object row `<name>` | `pco%<group>%d`, `%m`, `%y`, `%a` (for example `hru_wb` -> `pco%wb_hru`, `channel_sd` -> `pco%sd_chan`, `basin_psc` -> `pco%recall_bsn`) |

---
title: print.prt
description: Output control file. Sets the warm-up years, the daily print window and the output files SWAT+ writes at each interval.
status: review
verified_against:
  - src/basin_print_codes_read.f90
  - src/basin_module.f90
  - src/time_control.f90
  - src/command.f90
  - src/output_landscape_init.f90
  - src/header_write.f90
  - src/header_sd_channel.f90
  - src/header_yield.f90
  - src/header_mgt.f90
  - src/header_hyd.f90
  - src/hru_output.f90
  - src/basin_output.f90
  - src/lsreg_output.f90
  - src/gwflow_read.f90
  - src/carbon_legacy_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`print.prt` controls the output of a SWAT+ run. It sets the number of warm-up years left out of the outputs, the period and spacing of daily output, the extra output formats, a few special output files, and one row per output group with switches for daily, monthly, yearly and average annual files. The file is named in slot 2 of the `simulation` line of [`file.cio`](file-cio.md) (default `print.prt`).

If the name in [`file.cio`](../input-reference/file-cio.md) is `null`, SWAT+ uses the built-in values: no warm-up, every output group off, and crop yields written as average annual values only. A name that does not exist in the run folder has the same effect, and SWAT+ creates an empty file of that name. The files listed in [Output naming convention](../output-reference/naming-convention.md#files-written-every-run) are written in every case.

## Format

Free format, whitespace-separated. The file has four short blocks, each a header line followed by a line of values, then a header line and one row per output group. Line 1 is a title. All header lines are skipped, and values are read by position within each line.

| Line | Content |
|------|---------|
| 1 | title |
| 2 | header |
| 3 | `nyskip`, `day_start`, `yrc_start`, `day_end`, `yrc_end`, `interval` |
| 4 | header |
| 5 | `aa_int_cnt`, followed by `aa_int_cnt` end years |
| 6 | header |
| 7 | `csvout`, `use_obj_lbls`, `cdfout` |
| 8 | header |
| 9 | `crop_yld`, `mgtout`, `hydcon`, `fdcout` |
| 10 | header (`objects daily monthly yearly avann`) |
| 11 and on | output group rows |

### Print period (line 3)

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `nyskip` | years | 0 | Number of years at the start of the simulation left out of all outputs (warm-up period). |
| 2 | `day_start` | day of year | 1 | Day of the year on which daily output starts. 0 means 1. |
| 3 | `yrc_start` | year | first simulated year | Year in which daily output starts. 0 means the first year in [`time.sim`](time-sim.md). |
| 4 | `day_end` | day of year | 366 | Day of the year on which daily output ends. 0 means 366, the end of the year. |
| 5 | `yrc_end` | year | after the last simulated year | Year in which daily output ends. 0 means daily output runs to the end of the simulation. |
| 6 | `interval` | days | 1 | Days between daily output rows. 0 or less means 1. With 2, every other day is written. |

A warm-up period lets soil water, nutrient pools and plant cover settle from their initial values before results are used. It matters more for short simulations; for a simulation of five years or less, a warm-up period is recommended.

### Average annual intervals (line 5)

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `aa_int_cnt` | count | 0 | Number of average annual print intervals. When it is above 0, the end year of each interval follows on the same line, in order. |

For example, `3 1995 2005 2015` would end intervals in 1995, 2005 and 2015. In 62.0.1 the end years are read but have no effect on the outputs: every average annual file covers the whole printed period. See [Average annual values](#average-annual-values).

### Output formats (line 7)

| # | Column | Values | Default | Description |
|---|--------|--------|---------|-------------|
| 1 | `csvout` | `y`, `n` | `n` | `y` also writes a comma-separated `.csv` copy of most output files. |
| 2 | `use_obj_lbls` | `y`, `n` | `n` | How the output group rows are read: `y` by name, `n` by position. See [Output group rows](#output-group-rows). |
| 3 | `cdfout` | `y`, `n` | `n` | netCDF output. Read and not used. |

`print.prt` files written by older versions of the SWAT+ Editor have the header `csvout dbout cdfout` on line 6. SWAT+ reads the second value as `use_obj_lbls` whatever the header says, so an old file with `n` there is read by position.

### Special outputs (line 9)

| # | Column | Values | Default | Description |
|---|--------|--------|---------|-------------|
| 1 | `crop_yld` | `a`, `y`, `b`, `n` | `a` | Crop yield files: `a` average annual (`crop_yld_aa`), `y` yearly (`crop_yld_yr` and the basin crop yield files), `b` both, `n` none. |
| 2 | `mgtout` | `y`, `n` | `n` | `y` writes `mgt_out.txt`, the log of management operations, decision table actions and water allocation deliveries. |
| 3 | `hydcon` | `y`, `n` | `n` | `y` writes `hydcon.out`, the list of hydrograph connections between objects. It is mostly useful for finding connection errors. |
| 4 | `fdcout` | `y`, `n` | `n` | `y` computes flow duration curves and a flashiness index for SWAT+ channels and writes them to `flow_duration_curve.out`. |

Older Editor versions write the header `soilout` in place of `crop_yld`; the value is read as `crop_yld`.

## Output group rows

Each row from line 11 on has a group name and four switches, for the daily, monthly, yearly and average annual files of that group. A switch of `y` opens the file for that interval and any other value leaves it off. The legacy carbon rows `hru_cb` and `hru_cb_vars` also accept `l`. The files each row opens, and the pages that describe them, are listed in [Output naming convention](../output-reference/naming-convention.md#printprt-rows-and-files).

How the rows are read depends on `use_obj_lbls` on line 7:

- `use_obj_lbls = y`: each row is matched by its name, so rows can be in any order and rows can be left out. A row that is left out has all four switches off. A name SWAT+ does not know stops the run with `Error: The output object <name> in the input file print.prt is not a valid object`, and a name that appears twice stops it with `print object is duplicated`. Names are case-sensitive.
- `use_obj_lbls = n`: the rows are read in the fixed order of the table below, and the names in the first column are not checked. A missing row or an extra row shifts every later row, so its switches are applied to the wrong output group, with no message. Rows after the end of the file are off. The carbon and gwflow rows cannot be set in this mode.

| Order | Row | Output |
|-------|-----|--------|
| 1 | `basin_wb` | basin water balance |
| 2 | `basin_nb` | basin nutrient balance |
| 3 | `basin_ls` | basin losses from the land |
| 4 | `basin_pw` | basin plant and weather |
| 5 | `basin_aqu` | basin aquifers |
| 6 | `basin_res` | basin reservoirs |
| 7 | `basin_cha` | basin legacy channels |
| 8 | `basin_sd_cha` | basin SWAT+ channels, channel morphology and channel budget |
| 9 | `basin_psc` | basin point sources (recall objects summed) |
| 10 to 17 | `region_wb`, `region_nb`, `region_ls`, `region_pw`, `region_aqu`, `region_res`, `region_sd_cha`, `region_psc` | read, but no region files are written in 62.0.1 |
| 18 | `water_allo` | water allocation, water use and treatment |
| 19 to 22 | `lsunit_wb`, `lsunit_nb`, `lsunit_ls`, `lsunit_pw` | landscape unit water balance, nutrient balance, losses, plant and weather |
| 23 to 26 | `hru_wb`, `hru_nb`, `hru_ls`, `hru_pw` | HRU water balance, nutrient balance (with the nitrogen cycle file), losses, plant and weather |
| 27 to 30 | `hru-lte_wb`, `hru-lte_nb`, `hru-lte_ls`, `hru-lte_pw` | HRU-lte water balance, losses, plant and weather; `hru-lte_nb` is read but writes nothing |
| 31 | `channel` | legacy channels |
| 32 | `channel_sd` | SWAT+ channels, channel morphology, channel budget, and the sediment budget files per channel, per stream order and for the basin |
| 33 | `aquifer` | aquifers |
| 34 | `reservoir` | reservoirs and wetlands |
| 35 | `recall` | recall objects (point sources and inlets) |
| 36 | `hyd` | inflow and outflow hydrographs of every object, and deposition |
| 37 | `ru` | routing unit hydrographs |
| 38 | `pest` | pesticides in HRUs, channels, reservoirs, aquifers and the basin |
| 39 to 45 | `basin_salt`, `hru_salt`, `ru_salt`, `aqu_salt`, `channel_salt`, `res_salt`, `wetland_salt` | salts |
| 46 to 52 | `basin_cs`, `hru_cs`, `ru_cs`, `aqu_cs`, `channel_cs`, `res_cs`, `wetland_cs` | constituents; `res_cs` also opens the wetland constituent files, and `wetland_cs` writes nothing |

These rows are recognised only when `use_obj_lbls = y`:

| Row | Output |
|-----|--------|
| `hru_cb_gl`, `hru_cb_trf`, `hru_cb_lyr`, `hru_cb_cpool`, `hru_cb_npool`, `hru_cb_plt`, `hru_cb_flux`, `hru_cb_drv`, `hru_cb_dyn`, `hru_cb_snap` | HRU carbon output, one row per file family. See [Carbon outputs](../output-reference/carbon.md#files-and-switches). |
| `lsu_cb_gl`, `lsu_cb_trf`, `lsu_cb_plt` | landscape unit carbon output, area-weighted from the HRUs. See [Carbon outputs](../output-reference/carbon.md#files-and-switches). |
| `hru_cb`, `hru_cb_vars` | legacy CSU carbon files, switched with `y` or `l`. See [Legacy CSU carbon outputs](../output-reference/carbon.md#legacy-csu-carbon-outputs). |
| `gwflow_wb`, `gwflow_flux`, `gwflow_heat`, `gwflow_solute`, `gwflow_obs`, `gwflow_pump` | gwflow output. A row that is present replaces the setting from the gwflow input files; a row that is absent leaves it. See [gwflow output switches](../output-reference/gwflow.md#output-switches). |

Some rows write data only when the project has the matching objects. The `channel_sd` and `basin_sd_cha` files need SWAT+ channels, and the `channel` and `basin_cha` files need legacy channels. The basin landscape files (`basin_wb`, `basin_nb`, `basin_ls`, `basin_pw`) are summed from the landscape unit element file [`ls_unit.ele`](../input-reference/units.md#ls_unitele), and the landscape unit files need [`ls_unit.def`](../input-reference/units.md#ls_unitdef); both are named on the `regions` line of [`file.cio`](file-cio.md).

## Print timing

Every output file leaves out the first `nyskip` years of the simulation. After those years:

- Daily rows are written from `day_start` of `yrc_start` until `day_end` of `yrc_end`, every `interval` days, starting with the first day of the window. Output starts on the first simulated day whose day of the year is at least `day_start` in a year at or after `yrc_start`. If the simulation starts in a later year than `yrc_start`, daily output therefore starts on day `day_start` of the first simulated year. Days before it in that year are not written.
- Monthly rows are written at the end of each month, yearly rows at the end of each year, and average annual rows once, at the end of the simulation.

The print window applies to daily rows only. Monthly, yearly and average annual files always cover all years after the warm-up.

## Average annual values

The average annual files give the sum over the printed period divided by the number of printed years $Y$. SWAT+ counts the printed days $D$ (all days after the warm-up) and divides by 365:

$$Y = \frac{D}{365}$$

Leap days are counted in $D$, so $Y$ is slightly larger than the number of calendar years. When `nyskip` is above 0, 62.0.1 starts the count at the number of simulated years $N_{yr}$ instead of 0:

$$Y = \frac{D + N_{yr}}{365}$$

For a 10-year simulation with 2 warm-up years, $Y$ is about 8.03 instead of 8.00, and the average annual values are about 0.3% lower than the true averages over the printed years. If `nyskip` is equal to or larger than the number of simulated years, no output is written.

## Example

`refdata/Ames_sub1/print.prt` in the SWAT+ repository:

```
print.prt: 
nyskip      day_start  yrc_start  day_end   yrc_end   interval  
0           0               1975         0     2020         1         
aa_int_cnt  
0           
csvout        use_obj_lbls  cdfout        
n             y             n             
crop_yld      mgtout        hydcon        fdcout        
b             y             n             n             
objects                  daily       monthly        yearly         avann
hru_wb                       y             n             n             y  
hru_nb                       y             n             n             y  
hru_ls                       n             n             n             y  
hru_pw                       y             n             n             y  
hru_cb                       l             y             y             y  
hru_cb_vars                  l             y             y             y  
```

There is no warm-up period. Daily output covers the whole simulation (1975 to 2020) at an interval of one day. There is no `.csv` output. Crop yields are written both yearly and as average annual values, and the management log `mgt_out.txt` is written.

`use_obj_lbls = y`, so the rows are read by name and every row not listed is off. The HRU water balance, nutrient balance, and plant and weather files are written daily and as average annual values; the HRU losses only as average annual values. The `hru_cb` and `hru_cb_vars` rows switch on the legacy carbon files, with `l` in the daily column for the full set of layer diagnostics. The `hru_cb_vars` files are written only when the carbon model is on (`carbon = 2` in [`codes.bsn`](codes-bsn.md)).

`refdata/Osu_1hru/print.prt`, written by an older SWAT+ Editor, has `dbout` in place of `use_obj_lbls` with the value `n`, so its rows are read by position. Its list has an `hru_cb` row after `hru_pw`, which is not part of the fixed order: the reader applies that row to `hru-lte_wb` and every later row moves down one group. All rows in that file have the same switches (`n n n y`), so the shift has no visible effect there.

## Related files

- [`file.cio`](file-cio.md): names this file, the output folder, and the landscape unit files the basin and landscape unit outputs need.
- [`time.sim`](time-sim.md): the simulation period that contains the print period.
- [Output naming convention](../output-reference/naming-convention.md): file names and the files each row opens.
- [Output reference](../output-reference/index.md): contents of each output file.

??? quote "Sources"

    - Reader: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90), called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90) after `time_read`
    - Type definitions: `type basin_print_codes` and `type print_interval`, and `print_prt_error`, in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - Print window, warm-up and average annual years: [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Output calls and the `nyskip` test: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)
    - File opening: [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90), [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90), [`header_sd_channel.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_sd_channel.f90), [`header_yield.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_yield.f90), [`header_mgt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_mgt.f90), [`header_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_hyd.f90)
    - gwflow overrides: [`gwflow_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_read.f90)
    - Legacy carbon flags: [`carbon_legacy_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_legacy_module.f90)
    - Region output (not called): [`lsreg_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsreg_output.f90)

    | Column or row | Fortran variable |
    |---------------|------------------|
    | `nyskip`, `day_start`, `yrc_start`, `day_end`, `yrc_end`, `interval` | `pco%nyskip`, `pco%day_start`, `pco%yrc_start`, `pco%day_end`, `pco%yrc_end`, `pco%int_day` |
    | `aa_int_cnt` and end years | `pco%aa_numint`, `pco%aa_yrs` |
    | `csvout`, `use_obj_lbls`, `cdfout` | `pco%csvout`, `pco%use_obj_labels`, `pco%cdfout` |
    | `crop_yld`, `mgtout`, `hydcon`, `fdcout` | `pco%crop_yld`, `pco%mgtout`, `pco%hydcon`, `pco%fdcout` |
    | `basin_wb` ... `basin_psc` | `pco%wb_bsn`, `nb_bsn`, `ls_bsn`, `pw_bsn`, `aqu_bsn`, `res_bsn`, `chan_bsn`, `sd_chan_bsn`, `recall_bsn` |
    | `region_wb` ... `region_psc`, `water_allo` | `pco%wb_reg`, `nb_reg`, `ls_reg`, `pw_reg`, `aqu_reg`, `res_reg`, `sd_chan_reg`, `recall_reg`, `water_allo` |
    | `lsunit_*`, `hru_*`, `hru-lte_*` | `pco%{wb,nb,ls,pw}_lsu`, `pco%{wb,nb,ls,pw}_hru`, `pco%{wb,nb,ls,pw}_sd` |
    | `channel`, `channel_sd`, `aquifer`, `reservoir`, `recall`, `hyd`, `ru`, `pest` | `pco%chan`, `sd_chan`, `aqu`, `res`, `recall`, `hyd`, `ru`, `pest` |
    | salt rows | `pco%salt_basin`, `salt_hru`, `salt_ru`, `salt_aqu`, `salt_chn`, `salt_res`, `salt_wet` |
    | constituent rows | `pco%cs_basin`, `cs_hru`, `cs_ru`, `cs_aqu`, `cs_chn`, `cs_res`, `cs_wet` |
    | `hru_cb`, `hru_cb_vars`, `hru_cb_<family>`, `lsu_cb_<family>` | `pco%cb_hru`, `pco%cb_vars_hru`, `pco%cb_<family>_hru`, `pco%cb_<family>_lsu` |
    | `gwflow_<part>` | `pco%gwflow_<part>` |

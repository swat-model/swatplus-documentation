---
title: file.cio
description: Master index file. Lists the file names SWAT+ reads for every input category.
status: review
verified_against:
  - src/readcio_read.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`file.cio` is the master index. SWAT+ opens this file first. Each line tells the model which file to read for one input category. Every other input file in the project is reached through `file.cio`.

## Source

- Reader: [`src/readcio_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/readcio_read.f90)
- File-name fields and defaults: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90)

## Format

- Line 1: title line. Skipped by the reader.
- Lines 2 to 31: one line per input category. Each line starts with a category label (a free-form token that the reader reads but discards), followed by a fixed number of file-name fields whose order matches the corresponding `in_*` type in `input_file_module.f90`.
- Line 32: a single line for the optional output path.
- A field set to the literal token `null` disables the corresponding file.

The category labels written by tools like QSWAT+ and SWAT+ Editor are conventional. The reader does not validate them; only field order and count matter.

## Categories and fields

The table lists every category in the order the reader expects them, the number of file-name fields, and the default file names defined in `input_file_module.f90`.

| # | Category label | Fields (defaults from `input_file_module.f90`) |
|---|---|---|
| 1 | simulation | `time.sim`, `print.prt`, `object.prt`, `object.cnt`, `constituents.cs` |
| 2 | basin | `codes.bsn`, `parameters.bsn` |
| 3 | climate | `weather-sta.cli`, `weather-wgn.cli`, `pet.cli`, `pcp.cli`, `tmp.cli`, `slr.cli`, `hmd.cli`, `wnd.cli`, `atmodep.cli` |
| 4 | connect | `hru.con`, `hru-lte.con`, `rout_unit.con`, `gwflow.con`, `aquifer.con`, `aquifer2d.con`, `channel.con`, `reservoir.con`, `recall.con`, `exco.con`, `delratio.con`, `outlet.con`, `chandeg.con` |
| 5 | channel | `initial.cha`, `channel.cha`, `hydrology.cha`, `sediment.cha`, `nutrients.cha`, `channel-lte.cha`, `hyd-sed-lte.cha`, `temperature.cha` |
| 6 | reservoir | `initial.res`, `reservoir.res`, `hydrology.res`, `sediment.res`, `nutrients.res`, `weir.res`, `wetland.wet`, `hydrology.wet` |
| 7 | routing_unit | `rout_unit.def`, `rout_unit.ele`, `rout_unit.rtu`, `rout_unit.dr` |
| 8 | hru | `hru-data.hru`, `hru-lte.hru` |
| 9 | exco | `exco.exc`, `exco_om.exc`, `exco_pest.exc`, `exco_path.exc`, `exco_hmet.exc`, `exco_salt.exc` |
| 10 | recall | `recall.rec` |
| 11 | dr | `delratio.del`, `dr_om.del`, `dr_pest.del`, `dr_path.del`, `dr_hmet.del`, `dr_salt.del` |
| 12 | aquifer | `initial.aqu`, `aquifer.aqu` |
| 13 | herd | `animal.hrd`, `herd.hrd`, `ranch.hrd` |
| 14 | water_rights | `water_allocation.wro`, `element.wro`, `water_rights.wro` |
| 15 | link | `chan-surf.lin`, `aqu_cha.lin` |
| 16 | hydrology | `hydrology.hyd`, `topography.hyd`, `field.fld` |
| 17 | structural | `tiledrain.str`, `septic.str`, `filterstrip.str`, `grassedww.str`, `bmpuser.str` |
| 18 | hru_parm_db | `plants.plt`, `fertilizer.frt`, `tillage.til`, `pesticide.pes`, `pathogens.pth`, `metals.mtl`, `salt.slt`, `urban.urb`, `septic.sep`, `snow.sno` |
| 19 | ops | `harv.ops`, `graze.ops`, `irr.ops`, `chem_app.ops`, `fire.ops`, `sweep.ops` |
| 20 | lum | `landuse.lum`, `management.sch`, `cntable.lum`, `cons_practice.lum`, `ovn_table.lum` |
| 21 | chg | `cal_parms.cal`, `calibration.cal`, `codes.sft`, `wb_parms.sft`, `water_balance.sft`, `ch_sed_budget.sft`, `ch_sed_parms.sft`, `plant_parms.sft`, `plant_gro.sft` |
| 22 | init | `plant.ini`, `soil_plant.ini`, `om_water.ini`, `pest_hru.ini`, `pest_water.ini`, `path_hru.ini`, `path_water.ini`, `hmet_hru.ini`, `hmet_water.ini`, `salt_hru.ini`, `salt_water.ini` |
| 23 | soils | `soils.sol`, `nutrients.sol`, `soils_lte.sol` |
| 24 | decision_table | `lum.dtl`, `res_rel.dtl`, `scen_lu.dtl`, `flo_con.dtl` |
| 25 | regions | `ls_unit.ele`, `ls_unit.def`, `ls_reg.ele`, `ls_reg.def`, `ls_cal.reg`, `ch_catunit.ele`, `ch_catunit.def`, `ch_reg.def`, `aqu_catunit.ele`, `aqu_catunit.def`, `aqu_reg.def`, `res_catunit.ele`, `res_catunit.def`, `res_reg.def`, `rec_catunit.ele`, `rec_catunit.def`, `rec_reg.def` |
| 26 | pcp_path | one path string |
| 27 | tmp_path | one path string |
| 28 | slr_path | one path string |
| 29 | hmd_path | one path string |
| 30 | wnd_path | one path string |
| 31 | output_path | one path string (read as the whole line after the label) |

Categories 1 to 30 are read with list-directed I/O. Category 31 (`output_path`) is read with format `(A)` and the value is taken from the trailing portion of the line after the first space.

## Example

Top of `refdata/Ames_sub1/file.cio`:

```
file.cio: AMES
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli           null              null              null              null
connect           hru.con           null              null              null              null              null              null              null              null              null              null              null              null
channel           null       null       null        null         null        null        null        null
reservoir         null       null       null        null         null        null        null        null
routing_unit      null       null       null        null
hru               hru-data.hru      null
exco              null              null              null              null              null              null
recall            null
dr                null              null              null              null              null              null
aquifer           nbull             null
```

Notes on the example:

- Line 2 (`simulation`): only `time.sim`, `print.prt`, and `object.cnt` are in use. Slots 3 and 5 (`object.prt`, `constituents.cs`) are set to `null`.
- Line 4 (`climate`): only stations, weather generator, precipitation, and temperature are active. PET, solar, humidity, wind, and atmospheric deposition are disabled.
- Line 14 (`aquifer`): the dataset writes `nbull` for the initial-aquifer file. This is the file name in this project, not a default and not a typo of `null`. The model opens whatever file name appears here.

## Related files

Every input file referenced in `file.cio`. Start from the [Input reference](../input-reference/index.md) index.

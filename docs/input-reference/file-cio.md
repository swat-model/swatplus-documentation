---
title: file.cio
description: Master index file. Names the input file SWAT+ reads for every input category, the weather data folders and the output folder.
status: review
verified_against:
  - src/readcio_read.f90
  - src/input_file_module.f90
  - src/output_path_module.f90
  - src/proc_bsn.f90
  - src/carbon_bsn_read.f90
  - src/water_allocation_read.f90
  - src/cli_pmeas.f90
  - src/cli_tmeas.f90
  - src/cli_smeas.f90
  - src/cli_hmeas.f90
  - src/cli_wmeas.f90
  - src/cli_petmeas.f90
  - src/ch_read_elements.f90
  - src/salt_hru_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`file.cio` is the master index of a SWAT+ project. It is the first file SWAT+ opens, and it must be in the run folder under that name. Each line names the files for one input category, so every other input file is reached through `file.cio`. The last six lines give optional folders for the weather data files and for the output files.

## Format

Line 1 is a title and is skipped. Lines 2 to 26 each start with a category label and continue with file names in a fixed order. Lines 27 to 31 each give one weather data folder, and line 32 gives the output folder.

The reader takes the lines by position. The category label is read and discarded, so its text is not checked, and the file names are matched to slots by their order on the line. Values are separated by spaces.

- Write `null` for a file the project does not use. Most readers treat a name that does not exist in the run folder the same way as `null` and skip the file. The exceptions are listed under [Missing and null files](#missing-and-null-files).
- File names can be up to 25 characters long. Longer names are cut to 25 characters.
- Each line must give at least as many names as its category has slots. If a line is short, the reader continues onto the next line to fill the missing slots, and every later line is then read one line out of step. Extra names at the end of a line are ignored.

## Categories and default file names

The labels below are the ones the SWAT+ Editor writes. The default names are used only for slots that are never read, which happens when `file.cio` ends early. A project normally gives every name explicitly.

| Line | Label | Files, in slot order (default names) | Documented in |
|------|-------|--------------------------------------|---------------|
| 2 | `simulation` | [`time.sim`](../input-reference/time-sim.md), [`print.prt`](../input-reference/print-prt.md), [`object.prt`](../input-reference/management.md#objectprt), [`object.cnt`](../input-reference/object-cnt.md), [`constituents.cs`](../input-reference/cs.md#constituentscs) | [time.sim](time-sim.md), [print.prt](print-prt.md), [object.prt](management.md), [object.cnt](object-cnt.md), [constituents.cs](cs.md) |
| 3 | `basin` | [`codes.bsn`](../input-reference/codes-bsn.md), [`parameters.bsn`](../input-reference/parameters-bsn.md), [`carbon.bsn`](../input-reference/carbon-bsn.md) | [codes.bsn](codes-bsn.md), [parameters.bsn](parameters-bsn.md), [carbon.bsn](carbon-bsn.md) |
| 4 | `climate` | [`weather-sta.cli`](../input-reference/cli.md#weather-stacli), [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli), [`pet.cli`](../input-reference/cli.md#observed-data-lists), [`pcp.cli`](../input-reference/cli.md#observed-data-lists), [`tmp.cli`](../input-reference/cli.md#observed-data-lists), [`slr.cli`](../input-reference/cli.md#observed-data-lists), [`hmd.cli`](../input-reference/cli.md#observed-data-lists), [`wnd.cli`](../input-reference/cli.md#observed-data-lists), [`atmodep.cli`](../input-reference/cli.md#atmodepcli) | [climate index files](cli.md) |
| 5 | `connect` | [`hru.con`](../input-reference/con.md), [`hru-lte.con`](../input-reference/con.md), [`rout_unit.con`](../input-reference/con.md), [`gwflow.con`](../input-reference/gwflow.md#gwflowcon), [`aquifer.con`](../input-reference/con.md), [`aquifer2d.con`](../input-reference/con.md), [`channel.con`](../input-reference/con.md), [`reservoir.con`](../input-reference/con.md), [`recall.con`](../input-reference/con.md), [`exco.con`](../input-reference/con.md), [`delratio.con`](../input-reference/con.md), [`outlet.con`](../input-reference/con.md), [`chandeg.con`](../input-reference/con.md) | [connectivity files](con.md) |
| 6 | `channel` | [`initial.cha`](../input-reference/cha.md#initialcha), [`channel.cha`](../input-reference/cha.md#channelcha), [`hydrology.cha`](../input-reference/cha.md#hydrologycha), [`sediment.cha`](../input-reference/cha.md#sedimentcha), [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha), [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha), [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), [`temperature.cha`](../input-reference/cha.md#temperaturecha) | [legacy channel files](cha.md), [channel tables](sd-channel.md) |
| 7 | `reservoir` | [`initial.res`](../input-reference/res.md#initialres), [`reservoir.res`](../input-reference/res.md#reservoirres), [`hydrology.res`](../input-reference/res.md#hydrologyres), [`sediment.res`](../input-reference/res.md#sedimentres), [`nutrients.res`](../input-reference/res.md#nutrientsres), [`weir.res`](../input-reference/res.md#weirres), [`wetland.wet`](../input-reference/wet.md#wetlandwet), [`hydrology.wet`](../input-reference/wet.md#hydrologywet) | [reservoir files](res.md), [wetland files](wet.md) |
| 8 | `routing_unit` | [`rout_unit.def`](../input-reference/units.md#rout_unitdef), [`rout_unit.ele`](../input-reference/units.md#rout_unitele), [`rout_unit.rtu`](../input-reference/units.md#rout_unitrtu), `rout_unit.dr` | [connectivity files](con.md) |
| 9 | `hru` | [`hru-data.hru`](../input-reference/hru.md), [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru) | [hru-data.hru](hru.md) |
| 10 | `exco` | [`exco.exc`](../input-reference/recall.md), [`exco_om.exc`](../input-reference/recall.md), `exco_pest.exc`, `exco_path.exc`, `exco_hmet.exc`, `exco_salt.exc` | [connectivity files](con.md) |
| 11 | `recall` | [`recall.rec`](../input-reference/recall.md#recallrec) | [recall](recall.md) |
| 12 | `dr` | [`delratio.del`](../input-reference/con.md), `dr_om.del`, `dr_pest.del`, `dr_path.del`, `dr_hmet.del`, `dr_salt.del` | [connectivity files](con.md) |
| 13 | `aquifer` | [`initial.aqu`](../input-reference/aqu.md#initialaqu), [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) | [aquifer files](aqu.md) |
| 14 | `herd` | `animal.hrd`, `herd.hrd`, `ranch.hrd` | not read |
| 15 | `water_rights` | [`place_of_use.wro`](../input-reference/water-allocation.md#place_of_usewro), [`point_of_diver.wro`](../input-reference/water-allocation.md#point_of_diverwro) | [water allocation](water-allocation.md) |
| 16 | `link` | [`chan-surf.lin`](../input-reference/link.md#chan-surflin), [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) | [Link files](link.md) |
| 17 | `hydrology` | [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd), [`topography.hyd`](../input-reference/hyd.md#topographyhyd), [`field.fld`](../input-reference/hyd.md#fieldfld) | [hydrology and topography](hyd.md) |
| 18 | `structural` | [`tiledrain.str`](../input-reference/str.md#tiledrainstr), [`septic.str`](../input-reference/str.md#septicstr), [`filterstrip.str`](../input-reference/str.md#filterstripstr), [`grassedww.str`](../input-reference/str.md#grassedwwstr), [`bmpuser.str`](../input-reference/str.md#bmpuserstr) | [structural BMPs](str.md) |
| 19 | `hru_parm_db` | [`plants.plt`](../input-reference/plt.md), [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt), [`tillage.til`](../input-reference/til.md), [`pesticide.pes`](../input-reference/pes.md#pesticidepes), [`pathogens.pth`](../input-reference/pth.md#pathogenspth), [`metals.mtl`](../input-reference/mtl.md), `salt.slt`, [`urban.urb`](../input-reference/str.md#urbanurb), [`septic.sep`](../input-reference/str.md#septicsep), [`snow.sno`](../input-reference/sno.md) | [plants.plt](plt.md), [fertilizer.frt](frt.md), [tillage.til](til.md), [pesticide.pes](pes.md), [pathogens.pth](pth.md), [metals.mtl](mtl.md), [salt inputs](salt.md), [urban.urb and septic.sep](str.md), [snow.sno](sno.md) |
| 20 | `ops` | [`harv.ops`](../input-reference/ops.md#harvops), [`graze.ops`](../input-reference/ops.md#grazeops), [`irr.ops`](../input-reference/ops.md#irrops), [`chem_app.ops`](../input-reference/ops.md#chem_appops), [`fire.ops`](../input-reference/ops.md#fireops), [`sweep.ops`](../input-reference/ops.md#sweepops) | [operation databases](ops.md) |
| 21 | `lum` | [`landuse.lum`](../input-reference/lum.md), [`management.sch`](../input-reference/management.md#managementsch), [`cntable.lum`](../input-reference/lum-tables.md#cntablelum), [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum), [`ovn_table.lum`](../input-reference/lum-tables.md#ovn_tablelum) | [landuse.lum](lum.md), [management.sch](management.md), [lookup tables](lum-tables.md) |
| 22 | `chg` | [`cal_parms.cal`](../calibration/parameter-change-files.md), [`calibration.cal`](../calibration/parameter-change-files.md), [`codes.sft`](../calibration/soft-calibration.md), [`wb_parms.sft`](../calibration/soft-calibration.md), [`water_balance.sft`](../calibration/soft-calibration.md), [`ch_sed_budget.sft`](../calibration/soft-calibration.md), [`ch_sed_parms.sft`](../calibration/soft-calibration.md), [`plant_parms.sft`](../calibration/soft-calibration.md), [`plant_gro.sft`](../calibration/soft-calibration.md) | [parameter change files](../calibration/parameter-change-files.md), [soft calibration](../calibration/soft-calibration.md) |
| 23 | `init` | [`plant.ini`](../input-reference/ini.md#plantini), [`soil_plant.ini`](../input-reference/ini.md#soil_plantini), [`om_water.ini`](../input-reference/ini.md#om_waterini), [`pest_hru.ini`](../input-reference/pes.md#pest_hruini), [`pest_water.ini`](../input-reference/pes.md#pest_waterini), [`path_hru.ini`](../input-reference/pth.md#path_hruini), [`path_water.ini`](../input-reference/pth.md#path_waterini), [`hmet_hru.ini`](../input-reference/mtl.md#hmet_hruini), `hmet_water.ini`, [`salt_hru.ini`](../input-reference/salt.md#salt_hruini), `salt_water.ini` | [initial conditions](ini.md) |
| 24 | `soils` | [`soils.sol`](../input-reference/sol.md), [`nutrients.sol`](../input-reference/ini.md#nutrientssol), [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol) | [soils.sol](sol.md) |
| 25 | `decision_table` | [`lum.dtl`](../input-reference/dtl.md), [`res_rel.dtl`](../input-reference/dtl.md), [`scen_lu.dtl`](../input-reference/dtl.md), [`flo_con.dtl`](../input-reference/dtl.md) | [decision tables](dtl.md) |
| 26 | `regions` | [`ls_unit.ele`](../input-reference/units.md#ls_unitele), [`ls_unit.def`](../input-reference/units.md#ls_unitdef), `ls_reg.ele`, `ls_reg.def`, `ls_cal.reg`, `ch_catunit.ele`, `ch_catunit.def`, `ch_reg.def`, [`aqu_catunit.ele`](../input-reference/units.md#aqu_catunitele), `aqu_catunit.def`, `aqu_reg.def`, `res_catunit.ele`, `res_catunit.def`, `res_reg.def`, `rec_catunit.ele`, `rec_catunit.def`, `rec_reg.def` | [aquifer files](aqu.md), [recall](recall.md), [soft calibration](../calibration/soft-calibration.md) |
| 27 | `pcp_path` | folder for the precipitation data files | [precipitation data](pcp.md) |
| 28 | `tmp_path` | folder for the temperature data files | [temperature data](tmp.md) |
| 29 | `slr_path` | folder for the solar radiation data files | [climate index files](cli.md) |
| 30 | `hmd_path` | folder for the relative humidity data files | [climate index files](cli.md) |
| 31 | `wnd_path` | folder for the wind speed data files | [climate index files](cli.md) |
| 32 | any word | output folder | [Output folder](#output-folder) |

### Unused slots

These names are read from `file.cio`, but SWAT+ 62.0.1 never opens the file they name. Any name or `null` can be given.

- `connect`: [`aquifer2d.con`](../input-reference/con.md) (slot 6).
- `routing_unit`: `rout_unit.dr` (slot 4).
- `herd`: all three slots.
- `hru_parm_db`: [`metals.mtl`](../input-reference/mtl.md) and `salt.slt` (slots 6 and 7).
- `init`: `hmet_water.ini`, [`salt_hru.ini`](../input-reference/salt.md#salt_hruini) and `salt_water.ini` (slots 9 to 11).
- `regions`: `ls_cal.reg` and `ch_catunit.ele` (slots 5 and 6).

Two of these files are read under a fixed name instead. When salts are simulated, the HRU salt initial conditions come from a file named [`salt_hru.ini`](../input-reference/salt.md#salt_hruini) in the run folder, whatever slot 10 of the `init` line says. Channel catchment unit elements come from a file named `element.ccu`.

The `climate` line has no wind direction file. It has nine slots, and slot 3 is [`pet.cli`](../input-reference/cli.md#observed-data-lists).

## Missing and null files

For most slots, a name of `null` or a name that does not exist in the run folder means the file is skipped and the related feature is off. Some files behave differently:

- [`object.cnt`](../input-reference/object-cnt.md): if it is missing or `null`, SWAT+ prints `Cannot find object.cnt input file` and stops.
- [`carbon.bsn`](../input-reference/carbon-bsn.md): read only when `carbon = 2` in [`codes.bsn`](codes-bsn.md). It is then required, and SWAT+ stops with an error, written to the screen and to `diagnostics.out`, if the file named in slot 3 of the `basin` line does not exist or cannot be opened. The per-layer carbon file has no slot on the line: its name is built from the carbon file name, so [`carbon.bsn`](../input-reference/carbon-bsn.md) gives [`carbon_lyr.bsn`](carbon-lyr-bsn.md).
- [`time.sim`](../input-reference/time-sim.md) and [`print.prt`](../input-reference/print-prt.md): there is no check for a missing file. If the name is not `null` and the file does not exist, SWAT+ creates an empty file of that name and continues with built-in values. For [`time.sim`](../input-reference/time-sim.md) this leaves the run without a valid simulation period, so the file is required in practice.
- [`place_of_use.wro`](../input-reference/water-allocation.md#place_of_usewro) and [`point_of_diver.wro`](../input-reference/water-allocation.md#point_of_diverwro): if either is missing or `null`, SWAT+ creates an empty file of that name (a file called `null` in the second case), reads nothing from it, and water allocation is off. See [water allocation](water-allocation.md).
- [`chan-surf.lin`](../input-reference/link.md#chan-surflin): if the name is not `null` and the file does not exist, SWAT+ creates an empty file of that name. See [link files](link.md).

## Weather data folders

Lines 27 to 31 let the precipitation, temperature, solar radiation, humidity and wind data files be kept outside the run folder. Each line has a label and one value of up to 80 characters. A value of `null` means the data files are in the run folder.

SWAT+ joins the folder and the file name from the climate index file (for example [`pcp.cli`](../input-reference/cli.md#observed-data-lists)) without adding a separator, so the folder must end with `/` or `\`. The folder is read in the same way as a file name, with two consequences:

- A folder name that contains spaces must be in quotes.
- An unquoted `/` ends the value. `data/pcp/` is read as `data`, and an unquoted value that starts with `/` is read as empty, so the files are looked for in the run folder. Put any folder that uses forward slashes in quotes, for example `"C:/swat/weather/pcp/"`, or use backslashes on Windows.

There is no folder line for potential evapotranspiration data. Files listed in [`pet.cli`](../input-reference/cli.md#observed-data-lists) are always read from the run folder.

## Output folder

Line 32 is optional. It has a label (any word) and a folder name. SWAT+ reads the whole line, drops the first word and takes the rest of the line as the folder, so the folder name can contain spaces and forward slashes without quotes. Up to 256 characters are kept. If the line is missing or empty, or the folder is `null` or `NULL`, the output files are written to the run folder.

When a folder is given, SWAT+ converts the separators to the ones the operating system uses, creates the folder and any missing parent folders, and prints `Output path set to:` with the folder name. A relative folder is taken from the run folder. On Linux and macOS a folder that contains `:` is treated as a Windows path, and SWAT+ stops with an error. On Windows a folder that starts with `/` is placed on drive `C:`. SWAT+ also stops if it cannot create or open the folder.

The standard output files go to this folder, including `files_out.out`, `diagnostics.out`, `checker.out` and the time series outputs switched on in [`print.prt`](print-prt.md). In 62.0.1 the gwflow output files and the soft calibration output files (`hru-out.cal`, `hru-new.cal` and others) are still written to the run folder.

## Older file.cio files

Two lines changed length in recent revisions, and a `file.cio` written for an earlier revision needs both updated before it is run with 62.0.1:

- The `basin` line now has three slots. Add [`carbon.bsn`](../input-reference/carbon-bsn.md) or `null` after [`parameters.bsn`](../input-reference/parameters-bsn.md). With only two names on the `basin` line, SWAT+ takes the first word of line 4 (`climate`) as the carbon file name and discards the rest of that line. Every later category is then read from the line below the one it belongs to: the climate files are taken from the `connect` line, the connection files from the `channel` line, and so on. No message reports the shift. If `carbon = 2` in [`codes.bsn`](codes-bsn.md), SWAT+ stops with `ERROR: climate is required when carbon is enabled`; otherwise the run continues with wrong file names in every later slot.
- The `water_rights` line (line 15) now has two slots, the place-of-use file and the point-of-diversion file. An older line with `water_allocation.wro element.wro water_rights.wro` makes SWAT+ read `water_allocation.wro` as the place-of-use file and `element.wro` as the point-of-diversion file, and the third name is ignored. See [water allocation](water-allocation.md) for those files.

## Example

`refdata/Osu_1hru/file.cio` in the SWAT+ repository (long lines cut at the right):

```
file.cio: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn    null
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli           slr.cli           null              wnd.cli           null
connect           hru.con           null              rout_unit.con     null              aquifer.con       null              null              null        recall.con ...
channel           initial.cha       null              null              null              nutrients.cha     channel-lte.cha   hyd-sed-lte.cha   null
reservoir         initial.res       null              null              sediment.res      nutrients.res     weir.res              wetland.wet       hydrology.wet
routing_unit      rout_unit.def     rout_unit.ele     rout_unit.rtu     null
hru               hru-data.hru      null
exco              null              null              null              null              null              null
recall            recall.rec
dr                null              null              null              null              null              null
aquifer           initial.aqu       aquifer.aqu
herd              null              null              null
water_rights      null              null              null
link              null              null
hydrology         hydrology.hyd     topography.hyd    field.fld
structural        tiledrain.str     septic.str        filterstrip.str   grassedww.str     bmpuser.str
hru_parm_db       plants.plt        fertilizer.frt    tillage.til       pesticide.pes     null              null              null              urban.urb         septic.sep        snow.sno
ops               harv.ops          graze.ops         irr.ops           chem_app.ops      fire.ops          sweep.ops
lum               landuse.lum       management.sch    cntable.lum       cons_practice.lum  ovn_table.lum
chg               cal_parms.cal     calibration.cal   null              null              null              null              null              null              null
init              plant.ini         soil_plant.ini    om_water.ini      null              null              null              null              null              null              null  ...
soils             soils.sol         nutrients.sol     null
decision_table    lum.dtl           res_rel.dtl       null              null
regions           ls_unit.ele       ls_unit.def       null              null              null              null              null              null              aqu_catunit.ele ...
pcp_path          null
tmp_path          null
slr_path          null
hmd_path          null
wnd_path          null
```

The `basin` line has three slots, with `null` for the carbon file because the project does not use the carbon model. The `climate` line uses measured precipitation, temperature, solar radiation and wind; the PET, humidity and atmospheric deposition files are not used. The `water_rights` line still has the older three slots, all `null`; the first two switch water allocation off and the third is ignored. All weather data files are in the run folder, and there is no output folder line, so the outputs are written to the run folder.

In `refdata/Ames_sub1/file.cio` the `aquifer` line reads `aquifer nbull null`. `nbull` is taken as a file name. No file of that name exists, so the initial aquifer file is skipped in the same way as for `null`.

## Related files

- [`time.sim`](time-sim.md), [`print.prt`](print-prt.md) and [`object.cnt`](object-cnt.md): the simulation control files named on line 2.
- [`codes.bsn`](codes-bsn.md): its `carbon` code decides whether the carbon file on line 3 is read.
- [Input reference](index.md): every input file reached from `file.cio`.

??? quote "Sources"

    - Reader: [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90), called first from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Slot names and defaults: [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)
    - Output folder: [`output_path_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_path_module.f90)
    - Weather folders: [`cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pmeas.f90), [`cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tmeas.f90), [`cli_smeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_smeas.f90), [`cli_hmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_hmeas.f90), [`cli_wmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_wmeas.f90), [`cli_petmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_petmeas.f90)
    - Carbon file check: [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90)
    - Water allocation files: [`water_allocation_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_allocation_read.f90)
    - Fixed-name readers: [`ch_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_elements.f90) (`element.ccu`), [`salt_hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_hru_read.f90) (`salt_hru.ini`)

    | Line | Fortran variable |
    |------|------------------|
    | 2 `simulation` | `in_sim` (`time`, `prt`, `object_prt`, `object_cnt`, `cs_db`) |
    | 3 `basin` | `in_basin` (`codes_bas`, `parms_bas`, `carbon_bsn`) |
    | 4 `climate` | `in_cli` |
    | 5 `connect` | `in_con` |
    | 6 `channel` | `in_cha` |
    | 7 `reservoir` | `in_res` |
    | 8 `routing_unit` | `in_ru` |
    | 9 `hru` | `in_hru` |
    | 10 `exco` | `in_exco` |
    | 11 `recall` | `in_rec` |
    | 12 `dr` | `in_delr` |
    | 13 `aquifer` | `in_aqu` |
    | 14 `herd` | `in_herd` |
    | 15 `water_rights` | `in_wallo` (`pou`, `pod`) |
    | 16 `link` | `in_link` |
    | 17 `hydrology` | `in_hyd` |
    | 18 `structural` | `in_str` |
    | 19 `hru_parm_db` | `in_parmdb` |
    | 20 `ops` | `in_ops` |
    | 21 `lum` | `in_lum` |
    | 22 `chg` | `in_chg` |
    | 23 `init` | `in_init` |
    | 24 `soils` | `in_sol` |
    | 25 `decision_table` | `in_cond` |
    | 26 `regions` | `in_regs` |
    | 27 to 31 | `in_path_pcp%pcp`, `in_path_tmp%tmp`, `in_path_slr%slr`, `in_path_hmd%hmd`, `in_path_wnd%wnd` |
    | 32 | `out_path` in `output_path_module` |

---
title: Project folder anatomy
status: review
verified_against:
  - swatplus/refdata/Ames_sub1/file.cio
  - swatplus/src/input_file_module.f90
  - swatplus/src/readcio_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

A SWAT+ project is one folder of plain-text files, usually called `TxtInOut`. The model reads every input from that folder and writes its outputs back into it. Weather data files can be kept in separate folders named in [`file.cio`](../input-reference/file-cio.md); everything else is in the one folder.

## The master file

[`file.cio`](../input-reference/file-cio.md) is the index of the project. Each line names a group of inputs and the files to read for it, in a fixed order. `null` means that the file is not used. Read this file first when you open a project. The full description is on [`file.cio`](../input-reference/file-cio.md).

[`file.cio`](../input-reference/file-cio.md) of the `Ames_sub1` reference dataset at 62.0.1 (spacing shortened):

```
file.cio: AMES
simulation      time.sim  print.prt  null  object.cnt  null
basin           codes.bsn  parameters.bsn  carbon.bsn
climate         weather-sta.cli  weather-wgn.cli  null  pcp.cli  tmp.cli  null  null  null  null
connect         hru.con  null  null  null  null  null  null  null  null  null  null  null  null
channel         null  null  null  null  null  null  null  null
reservoir       null  null  null  null  null  null  null  null
routing_unit    null  null  null  null
hru             hru-data.hru  null
exco            null  null  null  null  null  null
recall          null
dr              null  null  null  null  null  null
aquifer         nbull  null
herd            null  null  null
water_rights    null  null  null
link            null  null
hydrology       hydrology.hyd  topography.hyd  null
structural      tiledrain.str  septic.str  filterstrip.str  grassedww.str  bmpuser.str
hru_parm_db     plants.plt  fertilizer.frt  tillage.til  pesticide.pes  null  null  null  urban.urb  septic.sep  snow.sno
ops             harv.ops  graze.ops  irr.ops  chem_app.ops  fire.ops  sweep.ops
lum             landuse.lum  management.sch  cntable.lum  cons_practice.lum  ovn_table.lum
chg             null  null  null  null  null  null  null  null  null
init            plant.ini  soil_plant.ini  null  null  null  null  null  null  null  null  null  null
soils           soils.sol  nutrients.sol  null
decision_table  lum.dtl  null  null  null
regions         ls_unit.ele  null  null  null  null  null  null  null  aqu_catunit.ele  null  null  null  null  null  null  null  null
pcp_path        null
tmp_path        null
slr_path        null
hmd_path        null
wnd_path        null
```

The `basin` line names three files from revision 62 on ([`carbon.bsn`](../input-reference/carbon-bsn.md) was added). A [`file.cio`](../input-reference/file-cio.md) written for an earlier revision has two names there and is misread by 62.0.1; rewrite it with SWAT+ Editor 4 or add the third name. The same applies to the `water_rights` line, which names the water allocation files. See [`file.cio`](../input-reference/file-cio.md) for the details.

## Input groups

### Simulation control

| File | Content |
|---|---|
| [`time.sim`](../input-reference/time-sim.md) | start and end dates, time step |
| [`print.prt`](../input-reference/print-prt.md) | which output files to write, and at which time steps |
| [`object.cnt`](../input-reference/object-cnt.md) | number of objects of each type (HRUs, channels, aquifers, ...) |
| [`object.prt`](../input-reference/management.md#objectprt) | extra output for individual objects (optional) |

### Basin

| File | Content |
|---|---|
| [`codes.bsn`](../input-reference/codes-bsn.md) | method switches (PET method, runoff method, routing, carbon model, gwflow, ...) |
| [`parameters.bsn`](../input-reference/parameters-bsn.md) | basin-wide parameters |
| [`carbon.bsn`](../input-reference/carbon-bsn.md), [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) | carbon model parameters; [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) is found from the name of [`carbon.bsn`](../input-reference/carbon-bsn.md) and is not listed in [`file.cio`](../input-reference/file-cio.md) |

### Climate

| File | Content |
|---|---|
| [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) | weather stations and the data files each one uses |
| [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) | weather generator statistics, used to fill missing data or generate whole records |
| [`pcp.cli`](../input-reference/cli.md#observed-data-lists), [`tmp.cli`](../input-reference/cli.md#observed-data-lists), [`slr.cli`](../input-reference/cli.md#observed-data-lists), [`hmd.cli`](../input-reference/cli.md#observed-data-lists), [`wnd.cli`](../input-reference/cli.md#observed-data-lists) | lists of the data files for each variable |
| `*.pcp`, `*.tmp`, `*.slr`, `*.hmd`, `*.wnd` | daily (or sub-daily) records |

### Objects and connections

| File | Content |
|---|---|
| [`hru.con`](../input-reference/con.md), [`rout_unit.con`](../input-reference/con.md), [`aquifer.con`](../input-reference/con.md), [`chandeg.con`](../input-reference/con.md), [`reservoir.con`](../input-reference/con.md), [`recall.con`](../input-reference/con.md), ... | position of each object and where its outflow goes |
| [`hru-data.hru`](../input-reference/hru.md) | for each HRU, the names of its topography, hydrology, soil, land use, initial conditions, snow and field records |
| [`rout_unit.def`](../input-reference/units.md#rout_unitdef), [`rout_unit.ele`](../input-reference/units.md#rout_unitele), [`ls_unit.def`](../input-reference/units.md#ls_unitdef), [`ls_unit.ele`](../input-reference/units.md#ls_unitele), [`aqu_catunit.ele`](../input-reference/units.md#aqu_catunitele) | which HRUs belong to each routing unit, landscape unit and aquifer catchment |

### Hydrology and topography

| File | Content |
|---|---|
| [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | HRU hydrology parameters (lateral flow, evaporation, percolation, ...) |
| [`topography.hyd`](../input-reference/hyd.md#topographyhyd) | slope, slope length and related values |
| [`field.fld`](../input-reference/hyd.md#fieldfld) | field length, width and orientation |

### Soils

| File | Content |
|---|---|
| [`soils.sol`](../input-reference/sol.md) | soil layers and their physical properties |
| [`nutrients.sol`](../input-reference/ini.md#nutrientssol) | initial soil nutrient contents |

### Land use and management

| File | Content |
|---|---|
| [`landuse.lum`](../input-reference/lum.md) | land uses, each naming its plant community, management schedule, curve number set, conservation practice and structural practices |
| [`management.sch`](../input-reference/management.md#managementsch) | management schedules: dated operations and decision tables |
| [`cntable.lum`](../input-reference/lum-tables.md#cntablelum), [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum), [`ovn_table.lum`](../input-reference/lum-tables.md#ovn_tablelum) | curve numbers, USLE support practice factors, overland Manning's n |
| [`lum.dtl`](../input-reference/dtl.md) | decision tables for land use and management |
| [`harv.ops`](../input-reference/ops.md#harvops), [`graze.ops`](../input-reference/ops.md#grazeops), [`irr.ops`](../input-reference/ops.md#irrops), [`chem_app.ops`](../input-reference/ops.md#chem_appops), [`fire.ops`](../input-reference/ops.md#fireops), [`sweep.ops`](../input-reference/ops.md#sweepops) | parameters of each type of operation |

### Databases

| File | Content |
|---|---|
| [`plants.plt`](../input-reference/plt.md) | plant growth parameters |
| [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt), [`manure_db.frt`](../input-reference/frt.md#manure_dbfrt), [`manure_om.frt`](../input-reference/frt.md#manure_omfrt) | fertilizers and manures |
| [`tillage.til`](../input-reference/til.md), [`pesticide.pes`](../input-reference/pes.md#pesticidepes), [`urban.urb`](../input-reference/str.md#urbanurb), [`septic.sep`](../input-reference/str.md#septicsep), [`snow.sno`](../input-reference/sno.md) | tillage, pesticide, urban, septic system and snow parameters |

### Initial conditions

| File | Content |
|---|---|
| [`plant.ini`](../input-reference/ini.md#plantini) | plant communities at the start of the run |
| [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) | which soil nutrient and constituent records each HRU starts with |

### Channels, aquifers, reservoirs and wetlands

| File | Content |
|---|---|
| [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha), [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha), [`initial.cha`](../input-reference/cha.md#initialcha) | channels (the SWAT-DEG channel model, connected through [`chandeg.con`](../input-reference/con.md)) |
| [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu), [`initial.aqu`](../input-reference/aqu.md#initialaqu) | aquifers |
| [`reservoir.res`](../input-reference/res.md#reservoirres), [`hydrology.res`](../input-reference/res.md#hydrologyres), [`sediment.res`](../input-reference/res.md#sedimentres), [`nutrients.res`](../input-reference/res.md#nutrientsres), [`initial.res`](../input-reference/res.md#initialres), [`weir.res`](../input-reference/res.md#weirres) | reservoirs |
| [`wetland.wet`](../input-reference/wet.md#wetlandwet), [`hydrology.wet`](../input-reference/wet.md#hydrologywet) | wetlands |

### Calibration

| File | Content |
|---|---|
| [`cal_parms.cal`](../calibration/parameter-change-files.md), [`calibration.cal`](../calibration/parameter-change-files.md) | parameter changes applied at start-up ([Hard calibration](../calibration/hard-calibration.md)) |
| [`codes.sft`](../calibration/soft-calibration.md) and the other `*.sft` files | [Soft calibration](../calibration/soft-calibration.md) |

Optional groups (structural practices, water allocation, gwflow, salts and constituents, pesticides and pathogens, export coefficients, recall) are described in the [Input Reference](../input-reference/index.md).

## Outputs

Output files end in `_day`, `_mon`, `_yr` or `_aa` (average annual) and `.txt`, or `.csv` when CSV output is switched on in [`print.prt`](../input-reference/print-prt.md). The first part of the name gives the object (`basin_`, `lsunit_`, `hru_`, `channel_sd_`, `aquifer_`, `reservoir_`, ...) and the next part the variables:

| Code | Variables |
|---|---|
| `wb` | water balance |
| `nb` | nutrient balance |
| `ls` | sediment and nutrient losses |
| `pw` | plant growth and stress |
| `aqu`, `sd_cha`, `res` | aquifer, channel, reservoir |

The [Output Reference](../output-reference/index.md) describes each file.

## Log and check files

| File | Content |
|---|---|
| `simulation.out` | run progress and the completion message |
| `diagnostics.out` | names that could not be matched, missing files, unexpected values |
| `checker.out` | summary of the inputs for each HRU, written before the simulation |
| `files_out.out` | list of the output files written |
| `area_calc.out` | area summary |
| `erosion.out` | header lines only in 62.0.1 |
| `success.fin` | written only when the run completes |

Check `simulation.out` and `diagnostics.out` after every first run of a new or changed project.

??? quote "Sources"

    - File groups and default names: the `input_*` types in [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90); `file.cio` is read by [`src/readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90).
    - Example: [`refdata/Ames_sub1/file.cio`](https://github.com/swat-model/swatplus/blob/62.0.1/refdata/Ames_sub1/file.cio). The `aquifer` line contains `nbull`, a typing error in the shipped file; the dataset has no aquifers, so the name is never used.

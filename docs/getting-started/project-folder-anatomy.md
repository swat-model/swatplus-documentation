---
title: Project folder anatomy
status: review
verified_against:
  - swatplus/refdata/Ames_sub1/file.cio
  - swatplus/src/input_file_module.f90
  - swatplus/src/readcio_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

A SWAT+ project is a single flat folder of plain-text files. The executable reads everything in that folder and writes outputs back into the same folder.

There are no subdirectories. The grouping below is by purpose, not by location.

## The master file: `file.cio`

`file.cio` is the index. It tells SWAT+ which file names to read for each category of input. Every line names a category and the file(s) to read. The literal token `null` means "no file for this slot". Full column reference: [`file.cio`](../input-reference/file-cio.md).

Excerpt from `Ames_sub1/file.cio`:

```
file.cio: AMES
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli           null              null              null              null
connect           hru.con           null              null              null              null              null              null              null              null              null              null              null              null
hru               hru-data.hru      null
aquifer           nbull             null
hydrology         hydrology.hyd     topography.hyd    null
hru_parm_db       plants.plt        fertilizer.frt    tillage.til       pesticide.pes     null              null              null              urban.urb         septic.sep        snow.sno
ops               harv.ops          graze.ops         irr.ops           chem_app.ops      fire.ops          sweep.ops
lum               landuse.lum       management.sch    cntable.lum       cons_practice.lum ovn_table.lum
init              plant.ini         soil_plant.ini    null              null              null              null              null              null              null              null              null              null
soils             soils.sol         nutrients.sol     null              null
decision_table    lum.dtl           null              null              null
regions           ls_unit.ele       null              null              null              null              null              null              null              aqu_catunit.ele
```

Read this file first when you open a project. It tells you what every other file is for.

## File groups

### Simulation control

| File | What it controls |
|---|---|
| `time.sim` | Start and end dates, time step |
| `print.prt` | Which output files to write, and at which aggregation (`_day`, `_mon`, `_yr`, `_aa`) |
| `object.cnt` | Object counts (how many HRUs, channels, aquifers, etc.) |

### Basin parameters

| File | What it controls |
|---|---|
| `codes.bsn` | Method switches (which equation set to use for ET, runoff, routing, ...) |
| `parameters.bsn` | Basin-wide numeric parameters |

### Climate

| File | What it controls |
|---|---|
| `weather-sta.cli` | List of weather stations and which files belong to each |
| `weather-wgn.cli` | Weather generator parameters (used to fill missing data) |
| `pcp.cli`, `tmp.cli`, ... | Indexes pointing to the actual `.pcp`, `.tmp`, etc. data files |
| `<name>.pcp`, `<name>.tmp` | The daily precipitation and temperature time series |

### Spatial objects and connectivity

| File | What it controls |
|---|---|
| `hru.con` | HRU connectivity (which object each HRU drains to) |
| `chandeg.con`, `aquifer.con`, `reservoir.con` | Channel, aquifer, reservoir connectivity |
| `rout_unit.con` | Routing unit connectivity |
| `hru-data.hru` | Per-HRU pointers to topography, soils, land use, management |

### Hydrology

| File | What it controls |
|---|---|
| `hydrology.hyd` | Per-HRU hydrologic parameters |
| `topography.hyd` | Per-HRU slope, slope length, field length |

### Soils

| File | What it controls |
|---|---|
| `soils.sol` | Soil layer properties (bulk density, available water, conductivity, ...) |
| `nutrients.sol` | Initial soil nutrient pools |

### Land use and management

| File | What it controls |
|---|---|
| `landuse.lum` | List of land use scenarios and the files that define each |
| `management.sch` | Operation schedules (planting, harvest, fertilizer, ...) |
| `cntable.lum` | Curve number lookup |
| `cons_practice.lum` | Conservation practice factor |
| `ovn_table.lum` | Manning's n for overland flow |
| `lum.dtl` | Decision tables that trigger operations based on conditions |

### Plant, fertiliser, tillage, pesticide databases

| File | What it controls |
|---|---|
| `plants.plt` | Plant parameter database |
| `fertilizer.frt` | Fertiliser composition |
| `tillage.til` | Tillage operation effects |
| `pesticide.pes` | Pesticide properties |

### Initial conditions

| File | What it controls |
|---|---|
| `plant.ini` | Starting plant communities by HRU |
| `soil_plant.ini` | Starting soil water, residue, plant biomass |

### Aquifers, reservoirs, channels

| File | What it controls |
|---|---|
| `aquifer.aqu` | Aquifer parameters |
| `reservoir.res`, `initial.res` | Reservoir parameters and initial state |
| `channel-lte.cha`, `hyd-sed-lte.cha` | Legacy channel routing |
| `hydrology.cha`, `sediment.cha`, `nutrients.cha` | SWAT+ channel routing parameters |

### Outputs (written by the model)

Files ending in `_day.txt`, `_mon.txt`, `_yr.txt`, or `_aa.txt`. The prefix tells you the spatial scope (`basin_`, `region_`, `lsunit_`, `hru_`, `channel_`, `aquifer_`, `reservoir_`, ...) and the underscore code tells you the variable group:

| Code | Variables |
|---|---|
| `_wb` | water balance |
| `_nb` | nutrient balance |
| `_ls` | landscape (sediment) |
| `_pw` | plant and water stress |
| `_aqu` | aquifer |
| `_cha` / `_sd_cha` | channel |
| `_res` | reservoir |

See [Output reference](../output-reference/index.md) for column details.

### Diagnostics

| File | What it tells you |
|---|---|
| `simulation.out` | Run progress and successful completion message |
| `diagnostics.out` | Warnings and unexpected values during the run |
| `checker.out` | Validation messages produced before the simulation starts |
| `area_calc.out`, `files_out.out`, `erosion.txt` | Setup summaries |

Always check these three (`simulation.out`, `diagnostics.out`, `checker.out`) when a run does not behave as expected.

## Next

The full per-file reference lives in [Input reference](../input-reference/index.md), with one page per file and a real example pulled from `Ames_sub1`.

---
title: SWAT vs SWAT+
status: review
verified_against:
  - swatplus/src/input_file_module.f90
  - swatplus/src/aquifer_module.f90
  - swatplus/src/gwflow_module.f90
  - swatplus/CMakeLists.txt
  - swatplus/refdata/Ames_sub1
  - https://github.com/swat-model/swat2012
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ is the restructured successor to SWAT (Soil and Water Assessment Tool). Most of the process equations are the same. The code structure, the input files and the way parts of a watershed are connected are different. The SWAT column below refers to SWAT2012, the last release of the original model ([`swat-model/swat2012`](https://github.com/swat-model/swat2012)).

## Spatial structure

| | SWAT2012 | SWAT+ |
|---|---|---|
| Units | subbasins, each with HRUs and one main channel | landscape units, routing units, HRUs, channels, aquifers, reservoirs, wetlands, point sources, each a separate object |
| Connections | fixed: HRUs drain to their subbasin's channel, subbasins drain downstream in numbered order | defined in connection files (`*.con`): any object can send any part of its flow (surface runoff, lateral flow, tile flow, recharge) to any other object |
| Floodplain and upland | not separated | landscape units can separate upland and floodplain areas |

The connection files make it possible, for example, to route upland runoff across a floodplain before it reaches the channel, to send tile flow from one HRU to a wetland, or to divide a reservoir's outflow between two channels.

## Input files

SWAT2012 used one set of files per subbasin and HRU (`.sub`, `.hru`, `.mgt`, `.gw`, `.rte`, `.sol`, ...), each repeating the full parameter list.

SWAT+ uses relational input files grouped by purpose. A parameter set is written once, given a name, and referenced by name from every object that uses it. For example, one row of [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) can serve hundreds of HRUs. The master file [`file.cio`](../input-reference/file-cio.md) lists every input file by group:

- simulation: [`time.sim`](../input-reference/time-sim.md), [`print.prt`](../input-reference/print-prt.md), [`object.cnt`](../input-reference/object-cnt.md)
- basin: [`codes.bsn`](../input-reference/codes-bsn.md), [`parameters.bsn`](../input-reference/parameters-bsn.md), [`carbon.bsn`](../input-reference/carbon-bsn.md)
- climate: [`weather-sta.cli`](../input-reference/cli.md#weather-stacli), [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli), [`pcp.cli`](../input-reference/cli.md#observed-data-lists), [`tmp.cli`](../input-reference/cli.md#observed-data-lists) and the station files
- connections: [`hru.con`](../input-reference/con.md), [`rout_unit.con`](../input-reference/con.md), [`aquifer.con`](../input-reference/con.md), [`chandeg.con`](../input-reference/con.md), [`reservoir.con`](../input-reference/con.md), [`recall.con`](../input-reference/con.md), ...
- HRUs, land use and management: [`hru-data.hru`](../input-reference/hru.md), [`landuse.lum`](../input-reference/lum.md), [`management.sch`](../input-reference/management.md#managementsch), [`cntable.lum`](../input-reference/lum-tables.md#cntablelum), decision tables (`*.dtl`)
- hydrology: [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd), [`topography.hyd`](../input-reference/hyd.md#topographyhyd), [`field.fld`](../input-reference/hyd.md#fieldfld)
- soils and plants: [`soils.sol`](../input-reference/sol.md), [`nutrients.sol`](../input-reference/ini.md#nutrientssol), [`plants.plt`](../input-reference/plt.md), [`plant.ini`](../input-reference/ini.md#plantini)
- databases: fertilizer, tillage, pesticide, urban and other parameter tables

The [Input Reference](../input-reference/index.md) describes each file.

## Management

SWAT2012 scheduled operations in the `.mgt` file of each HRU, by date or by fraction of heat units.

SWAT+ management schedules ([`management.sch`](../input-reference/management.md#managementsch)) are shared between HRUs, and can combine dated operations with decision tables (`*.dtl`). A decision table checks conditions every day (soil water, plant growth stage, date, crop rotation year, reservoir level, and so on) and applies an action when they are met. Decision tables also drive reservoir releases, flow control and land use change. See [Decision tables](../model-theory/decision-tables.md).

## Groundwater

SWAT2012 had a shallow and a deep aquifer for each HRU, with the shallow aquifer feeding the main channel of its subbasin.

SWAT+ aquifers are separate objects, usually one per landscape unit or group of HRUs, connected to channels through [`aquifer.con`](../input-reference/con.md). SWAT+ also includes gwflow, a gridded groundwater module that simulates water table heads and exchanges with channels, soils, tile drains, reservoirs and wells cell by cell. See [Aquifers](../model-theory/aquifers.md).

## Additional processes

SWAT+ adds or extends: a carbon module with soil organic matter pools, water allocation between sources and users, salts and other constituents, rice paddies, and a sediment budget for channels. Each is described in the [Model Theory](../model-theory/index.md) section.

## Outputs

SWAT2012 wrote a fixed set of files (`output.hru`, `output.sub`, `output.rch`, `output.std`).

SWAT+ writes one file per object type, process and time step, switched on and off in [`print.prt`](../input-reference/print-prt.md). Examples from the `Ames_sub1` reference dataset:

```
basin_wb_aa.txt        basin water balance, average annual
hru_wb_aa.txt          HRU water balance, average annual
channel_sd_day.txt     channel flow and loads, daily
basin_aqu_aa.txt       aquifer, average annual
```

The suffix gives the time step: `_day`, `_mon`, `_yr` or `_aa`. Each row of [`print.prt`](../input-reference/print-prt.md) switches the four time steps on or off. See the [Output Reference](../output-reference/index.md).

## Code

| | SWAT2012 | SWAT+ |
|---|---|---|
| Language | Fortran, fixed form | Fortran, free form |
| Organization | shared common blocks | modules grouped by process and object |
| Source | released as archives | public on GitHub, LGPL-2.1 |
| Build | hand-written makefiles | CMake |

## Migration

There is no automatic converter from a SWAT2012 project to SWAT+. Rebuild the project in QSWAT+ from the same DEM, soil, land use and climate data, then transfer calibrated parameter values by hand, checking each against the SWAT+ units and meaning.

??? quote "Sources"

    - Connection and input file names: `type input_con` and the other `input_*` types in [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90).
    - Aquifer objects: [`src/aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aquifer_module.f90), read by `aqu_read.f90`. Gridded groundwater: `gwflow_*.f90`. Spatial aquifer connections (`aquifer2d.con`): `aqu2d_read.f90`, `aqu2d_init.f90`.
    - Build: [`CMakeLists.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/CMakeLists.txt) compiles `src/*.f90` free form (`-free` for Intel, `-ffree-line-length-none` for GNU) into one executable.
    - SWAT2012: [`swat-model/swat2012`](https://github.com/swat-model/swat2012).

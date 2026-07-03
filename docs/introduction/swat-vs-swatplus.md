---
title: SWAT vs SWAT+
status: review
verified_against:
  - swatplus/src/input_file_module.f90
  - swatplus/src/aquifer_module.f90
  - swatplus/src/aqu2d_init.f90
  - swatplus/src/aqu2d_read.f90
  - swatplus/src/gwflow_module.f90
  - swatplus/CMakeLists.txt
  - swatplus/refdata/Ames_sub1
  - https://github.com/swat-model/swat2012
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

SWAT+ is the modernised successor to SWAT (Soil and Water Assessment Tool). The science is largely the same. The code structure, input file layout, and connectivity model are different.

The SWAT (2012) column below is sourced from the legacy model repository at [`swat-model/swat2012`](https://github.com/swat-model/swat2012).

## Code

| | SWAT (2012) | SWAT+ |
|---|---|---|
| Language | Fortran (fixed-form) | Fortran free-form (`.f90`) |
| Structure | Large shared common blocks | Modular, files grouped per process (`aqu_*`, `channel_*`, `hru_*`, `gwflow_*`, ...) |
| Source | Distributed as archives | Git on GitHub, public, LGPL-2.1 |
| Build | Hand-written Makefiles | CMake |

The CMake build for SWAT+ uses `-free` (Intel) or `-ffree-line-length-none` (GNU) and glob-compiles `src/*.f90` into a single executable. See `CMakeLists.txt` in the source repository.

## Inputs

SWAT2012 used a set of input file extensions tied to subbasins (`.sub`, `.rte`, `.gw`, `.sol`, etc.) with one file per HRU and subbasin.

SWAT+ replaces this with an object-based layout. The watershed is a graph of objects (HRUs, channels, aquifers, reservoirs, point sources, recall objects, decision tables) that are wired together through connectivity files (`.con`). The connectivity slots are defined by the `input_con` type in `src/input_file_module.f90`:

```
hru.con, hru-lte.con, rout_unit.con, gwflow.con, aquifer.con,
aquifer2d.con, channel.con, reservoir.con, recall.con, exco.con,
delratio.con, outlet.con, chandeg.con
```

Inputs are grouped by purpose, not by spatial unit:

- climate: `*.cli`, `*.pcp`, `*.tmp`, `weather-sta.cli`, `weather-wgn.cli`
- land use management: `landuse.lum`, `management.sch`, `cntable.lum`, `cons_practice.lum`, `ovn_table.lum`
- soils: `soils.sol`, `nutrients.sol`
- decision tables: `lum.dtl` (rule-based management triggers)
- hydrology: `hydrology.hyd`, `topography.hyd`
- basin-level: `codes.bsn`, `parameters.bsn`, `time.sim`, `print.prt`
- master index: `file.cio`

## Routing

SWAT2012 routed water from subbasin to subbasin in a fixed order based on subbasin numbering.

SWAT+ uses the `*.con` files to describe arbitrary connectivity between HRUs, routing units, channels, aquifers, reservoirs, and exit points. Routing follows the graph defined in those files. This makes it possible to route landscape units (LSUs) within an HRU to a channel via a routing unit, or to send flow to a wetland or reservoir before the channel.

## Management

SWAT2012 used `mgt` files with a fixed sequence of operations by date and heat unit.

SWAT+ separates the schedule (`management.sch`) from rule-based triggers (`*.dtl`, decision tables). A decision table evaluates conditions (soil water, plant heat units, day of year, etc.) at each time step and fires an operation when the condition is met. The same schedule can be reused across HRUs with different decision tables driving when operations occur.

## Aquifers

SWAT2012 had a single shallow-aquifer storage per subbasin.

SWAT+ supports 1D aquifer objects, defined in `src/aquifer_module.f90` and read by `src/aqu_read.f90`, with one aquifer per landscape unit or group. It also includes a 2D groundwater module rooted in `src/aqu2d_read.f90`, `src/aqu2d_init.f90`, and the `gwflow_*` source files, where the aquifer is discretised in plan view and exchanges water laterally with channels, the unsaturated zone, reservoirs, and other objects.

## Outputs

SWAT2012 wrote a fixed set of files (`output.hru`, `output.sub`, `output.rch`, `output.std`).

SWAT+ writes one file per object type and aggregation level, controlled by `print.prt`. Examples from `refdata/Ames_sub1`:

```
basin_wb_aa.txt        basin water balance, annual average
hru_wb_aa.txt          HRU water balance, annual average
basin_cha_aa.txt       channel, annual average
basin_aqu_aa.txt       aquifer, annual average
```

The aggregation suffix is `_day`, `_mon`, `_yr`, or `_aa`. Each object row in `print.prt` toggles `daily`, `monthly`, `yearly`, and `avann` independently with `y` or `n`.

## Migration

There is no automatic converter from a SWAT2012 project to a SWAT+ project. The recommended path is to rebuild the project in QSWAT+ from the same DEM, soils, land use, and climate inputs, then transfer calibrated parameter changes by hand.

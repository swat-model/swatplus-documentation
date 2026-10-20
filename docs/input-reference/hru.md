---
title: hru-data.hru
description: HRU property file. Each row names the topography, hydrology, soil, land use and management, initial conditions, surface storage, snow and field records an HRU uses.
status: review
verified_against:
  - src/hru_read.f90
  - src/hru_module.f90
  - src/hrudb_init.f90
  - src/topohyd_init.f90
  - src/proc_hru.f90
  - src/wet_initial.f90
  - src/wet_all_initial.f90
  - src/input_file_module.f90
  - src/hydrology_data_module.f90
  - src/topography_data_module.f90
  - src/soil_data_module.f90
  - src/landuse_data_module.f90
  - src/water_allocation_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`hru-data.hru` lists the HRU property sets of the project. Each row names one record in each of the parameter files an HRU needs: topography, hydrology, soil, land use and management, soil and plant initialization, surface storage (wetland), snow and field. An HRU picks its row through the `hru` column of [`hru.con`](con.md), which gives the `id` of a row in this file. The file is named on the `hru` line of [`file.cio`](file-cio.md) (default `hru-data.hru`).

The parameter values themselves are in the files the names point to. This file only links them together, so several HRUs can share one hydrology or topography record while having different soils or land uses.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one property set with ten values in the order below. The reader does not match columns by header name, so all ten values must be present and in this order.

| # | Column | Looked up in | Description |
|---|--------|--------------|-------------|
| 1 | `id` | - | Number of the property set. The `hru` column of [`hru.con`](../input-reference/con.md) refers to this value. The numbers do not have to be consecutive; the largest `id` sets the size of the table. |
| 2 | `name` | - | Name of the property set, up to 40 characters. Not used in calculations. |
| 3 | `topo` | [`topography.hyd`](hyd.md#topographyhyd) | Topography record: slope, slope lengths and deposition coefficient. |
| 4 | `hydro` | [`hydrology.hyd`](hyd.md#hydrologyhyd) | Hydrology record: lateral flow, canopy storage, evaporation and percolation parameters. |
| 5 | `soil` | [`soils.sol`](sol.md) | Soil profile. |
| 6 | `lu_mgt` | [`landuse.lum`](lum.md) | Land use and management record, which sets the plant community, management schedule, curve numbers, conservation practices and structures such as tile drains. |
| 7 | `soil_plant_init` | [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) (see [initial conditions](ini.md)) | Initial soil water, soil nutrients and constituents. The names of the soil test, pesticide, pathogen, heavy metal, salt and constituent records given in that row are matched at the same time. |
| 8 | `surf_stor` | [`wetland.wet`](wet.md) | Surface storage (wetland or paddy) record, or `null` for an HRU without surface storage. |
| 9 | `snow` | [`snow.sno`](sno.md) | Snow parameter set. |
| 10 | `field` | [`field.fld`](hyd.md#fieldfld) | Field dimensions, or `null` to use the built-in values. |

A name must match the record name in the target file character for character, including case. Names in [`topography.hyd`](../input-reference/hyd.md#topographyhyd), [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) and [`field.fld`](../input-reference/hyd.md#fieldfld) are stored with at most 16 characters and soil names with at most 20, so a longer name in this file can never match a record there.

## Name lookup

Each name is looked up once, when the files are read. The table gives what happens when a name is not found:

| Column | `null` or a name that is not found |
|--------|-----------------------------------|
| `topo`, `hydro`, `soil`, `lu_mgt`, `soil_plant_init`, `snow` | The HRU uses the first record of the target file. No message is written. |
| `surf_stor` | `null` means no surface storage. Any other name that is not in [`wetland.wet`](../input-reference/wet.md#wetlandwet) is reported in `diagnostics.out` as `<name> not found (wetland.wet)` and the HRU has no surface storage. |
| `field` | The HRU uses the built-in field values (length 500 m, width 100 m, angle 30°). A name other than `null` that is not found is reported in `diagnostics.out` as `<name> not found (field.fld)`. |

The reader has checks that would write `not found` messages for `topo`, `hydro`, `soil`, `lu_mgt`, `soil_plant_init` and `snow`, but they test for a pointer of zero while the pointers start at one, so in 62.0.1 these messages are never written. Check these names by hand, or in the SWAT+ Editor, before a run.

For `snow` this means that `null` selects the first row of [`snow.sno`](../input-reference/sno.md), the same as an unmatched name. A project that has no [`snow.sno`](../input-reference/sno.md) file at all has no first row to fall back on.

The `surf_stor` name is matched when the wetlands are initialized, which happens only when [`wetland.wet`](../input-reference/wet.md#wetlandwet) has at least one record.

## Tile drainage

The `lu_mgt` record decides whether an HRU has tile drains. For a tile-drained HRU, SWAT+ replaces two values from its `hydro` record at the start of the run: `cn3_swf` is set to 0.95 and `perco` to 0.1. Calibration changes to `cn3_swf` and `perco` are also skipped for these HRUs. See [hydrology.hyd](hyd.md#hydrologyhyd).

## Example

`refdata/Ames_sub1/hru-data.hru` in the SWAT+ repository (first four rows):

```
hru-data.hru: 
      id  name                          topo             hydro              soil            lu_mgt   soil_plant_init         surf_stor              snow             field  
       1  hru0001                topohru0001           hyd0001           soil_01-h1       cosy_lum        soilplant1              null           snow001              null  
       2  hru0002                topohru0002           hyd0002           soil_02          mntill_corn_lum soilplant1              null           snow001              null  
       3  hru0003                topohru0003           hyd0003           soil_03-h3       cosy_lum        soilplant1              null           snow001              null  
       4  hru0004                topohru0004           hyd0004           soil_04          cosy_lum        soilplant1              null           snow001              null
```

Each HRU has a separate topography record, hydrology record and soil. HRU 2 uses the land use `mntill_corn_lum`, the others `cosy_lum`. No HRU has surface storage, all use the snow set `snow001`, and `field` is `null`, so every HRU uses the built-in field dimensions.

## Related files

- [`hru.con`](con.md): one row per HRU; its `hru` column selects a row of this file by `id`. The HRU's area, elevation, latitude and weather station come from [`hru.con`](../input-reference/con.md).
- [`object.cnt`](object-cnt.md): number of HRUs.
- [`topography.hyd`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) and `field.fld`](hyd.md), [`soils.sol`](sol.md), [`landuse.lum`](lum.md), [initial conditions](ini.md), [`wetland.wet`](wet.md), [`snow.sno`](sno.md): the files the names point to.
- [`file.cio`](file-cio.md): names this file on its `hru` line.
- [Water allocation](water-allocation.md): an HRU can be named as a point of diversion in [`point_of_diver.wro`](../input-reference/water-allocation.md#point_of_diverwro). That link is made in the water allocation files; there is no column for it here.

??? quote "Sources"

    - Reader: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90), called from [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90)
    - Type definitions: `type hru_databases`, `type hru_databases_char`, `type hydrologic_response_unit_db` in [`hru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_module.f90)
    - Copy to each HRU through `hru.con`: [`hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90)
    - Use of the topography, hydrology, snow and field pointers, and the tile-drain override: [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90)
    - Surface storage lookup: [`wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90), called from [`wet_all_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_all_initial.f90)
    - Name lengths of the target records: [`hydrology_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrology_data_module.f90), [`topography_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topography_data_module.f90), [`soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_data_module.f90), [`landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_data_module.f90)
    - Points of diversion: [`water_allocation_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_allocation_read.f90)
    - File name: `in_hru%hru_data` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable | Resolved pointer |
    |--------|------------------|------------------|
    | `id` | array index `i` of `hru_db` | |
    | `name` | `hru_db(i)%dbsc%name` | |
    | `topo` | `hru_db(i)%dbsc%topo` | `hru_db(i)%dbs%topo` into `topo_db` |
    | `hydro` | `hru_db(i)%dbsc%hyd` | `hru_db(i)%dbs%hyd` into `hyd_db` |
    | `soil` | `hru_db(i)%dbsc%soil` | `hru_db(i)%dbs%soil` into `soildb` |
    | `lu_mgt` | `hru_db(i)%dbsc%land_use_mgt` | `hru_db(i)%dbs%land_use_mgt` into `lum` |
    | `soil_plant_init` | `hru_db(i)%dbsc%soil_plant_init` | `hru_db(i)%dbs%soil_plant_init` into `sol_plt_ini` |
    | `surf_stor` | `hru_db(i)%dbsc%surf_stor` | `hru(j)%dbs%surf_stor` into `wet_dat` (set in `wet_initial`) |
    | `snow` | `hru_db(i)%dbsc%snow` | `hru_db(i)%dbs%snow` into `snodb` |
    | `field` | `hru_db(i)%dbsc%field` | `hru_db(i)%dbs%field` into `field_db` |

---
title: hru-data.hru
description: Per-HRU pointers to topography, hydrology, soils, land use, surface storage, snow, and field data.
status: review
verified_against:
  - src/hru_read.f90
  - src/hru_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`hru-data.hru` is the pointer table for every HRU in the project. Each record names one HRU and lists the parameter sets it draws from: topography, hydrology, soils, land use management, soil and plant initialization, surface storage, snow, and field. The names in this file are looked up in the corresponding parameter files (`topography.hyd`, `hydrology.hyd`, `soils.sol`, `landuse.lum`, `plant.ini`, `snow.sno`, `field.fld`). The integer indices resolved by those lookups are stored in `hru_db(i)%dbs` and used throughout the simulation to fetch HRU properties.

If the file is missing or set to `null` in `file.cio`, the reader allocates `hru_db(0:0)` and no HRU data is loaded.

## Source

- Reader: [`src/hru_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_read.f90)
- Type definition: [`src/hru_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_module.f90) (`type hru_databases_char`, `type hydrologic_response_unit_db`)
- File name pointer: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90) (`in_hru%hru_data`, default `"hru-data.hru"`)

## Format

- Line 1: title. Skipped.
- Line 2: header. Skipped.
- Line 3 and beyond: one record per HRU. The reader makes two passes. The first pass scans the file to find the largest `id` and allocates `hru_db(0:imax)`. The second pass reads each record list-directed into `k, hru_db(i)%dbsc`, where `k` is a throwaway read of the id and `i` is the id parsed from the same line.

Record layout: 10 list-directed values per HRU.

| # | Column | Maps to | Type | Description |
|---|--------|---------|------|-------------|
| 1 | id | record index `i` | int | HRU number. Used as the array index into `hru_db`. Does not have to be sequential. The largest `id` in the file sets the array size. |
| 2 | name | `hru_db(i)%dbsc%name` | char(40) | HRU name. Free-form identifier. |
| 3 | topo | `hru_db(i)%dbsc%topo` | char(40) | Topography record name. Looked up in `topography.hyd`. Missing names are logged to `diagnostics.out` as "not found (topography.hyd)". |
| 4 | hydro | `hru_db(i)%dbsc%hyd` | char(40) | Hydrology record name. Looked up in `hydrology.hyd`. Missing names are logged as "not found (hydrograph.hyd)". |
| 5 | soil | `hru_db(i)%dbsc%soil` | char(40) | Soil record name. Looked up in `soils.sol`. Missing names are logged as "not found (soils.sol)". |
| 6 | lu_mgt | `hru_db(i)%dbsc%land_use_mgt` | char(40) | Land use and management record name. Looked up in `landuse.lum`. Missing names are logged as "not found (landuse.lum)". |
| 7 | soil_plant_init | `hru_db(i)%dbsc%soil_plant_init` | char(40) | Soil and plant initialization record name. Looked up in `plant.ini`. Missing names are logged as "not found (plant.ini)". A match also cross-walks the initial soil-test, pesticide, pathogen, heavy-metal, salt, and constituent records named inside the `plant.ini` entry. |
| 8 | surf_stor | `hru_db(i)%dbsc%surf_stor` | char(40) | Surface storage (reservoir or wetland) record name. The reader stores the name but does not resolve a pointer for it in `hru_read`. Use `null` if the HRU has no surface storage. |
| 9 | snow | `hru_db(i)%dbsc%snow` | char(40) | Snow record name. Looked up in `snow.sno`. The literal `null` is allowed and suppresses the not-found warning. |
| 10 | field | `hru_db(i)%dbsc%field` | char(40) | Field record name. Looked up in `field.fld`. The literal `null` is allowed and suppresses the not-found warning. |

The reader does not enforce a count line. The number of HRUs comes from the maximum `id` seen during the scan pass, so a gap in the numbering allocates unused slots in `hru_db`.

## Example

`refdata/Ames_sub1/hru-data.hru`:

```
hru-data.hru: 
      id  name                          topo             hydro              soil            lu_mgt   soil_plant_init         surf_stor              snow             field  
       1  hru0001                topohru0001           hyd0001           soil_01-h1       cosy_lum        soilplant1              null           snow001              null  
       2  hru0002                topohru0002           hyd0002           soil_02          mntill_corn_lum soilplant1              null           snow001              null  
       3  hru0003                topohru0003           hyd0003           soil_03-h3       cosy_lum        soilplant1              null           snow001              null  
       4  hru0004                topohru0004           hyd0004           soil_04          cosy_lum        soilplant1              null           snow001              null
```

Notes on the example:

- HRU 2 uses `mntill_corn_lum` while the rest use `cosy_lum`. The land use record drives tillage, plant cover, and management operations.
- `surf_stor` and `field` are `null` for every HRU. None of the HRUs has a pond, wetland, or tile-drained field assigned.
- `snow001` is the same record for every HRU. The snow record is a per-elevation-band parameter set.

## Related files

- [`object.cnt`](../input-reference/object-cnt.md). The `hru` count must be at least the largest `id` in this file.
- [`hru.con`](../input-reference/con.md). One row per HRU, in the same id order.
- `topography.hyd`, `hydrology.hyd`, `soils.sol`, `landuse.lum`, `plant.ini`, `snow.sno`, `field.fld`. Targets of the name pointers above.
- `file.cio`. The `hru` category line points to this file.

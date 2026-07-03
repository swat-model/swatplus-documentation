---
title: hydrology and topography (per HRU)
description: Per-HRU hydrology, topography, field, and shade-factor input files. Referenced by hru-data.hru.
status: review
verified_against:
  - src/hydrol_read.f90
  - src/topo_read.f90
  - src/field_read.f90
  - src/shade_factor_read.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

This page documents the per-HRU hydrology and topography parameter files: `hydrology.hyd`, `topography.hyd`, and `field.fld`, plus the closely related shade-factor file `shade_factor.shf`. File names for the first three are set in `type input_hydrology` in `src/input_file_module.f90`; the shade file is set in `type shade_factor` in the same module.

Records in `hydrology.hyd`, `topography.hyd`, and `field.fld` are referenced by name from [`hru-data.hru`](../input-reference/hru.md) (columns `hydro`, `topo`, and the field-name slot). Every HRU points at one record from each. Records in `shade_factor.shf` are used by the channel temperature routine in `src/ch_temp.f90`.

Each file is optional. If the slot in `file.cio` is `null` or the file is missing, the reader allocates a zero-length array and skips on. All four readers skip two header lines, then read one record per parameter set.

## Source

- File names: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_hydrology`, `type shade_factor`
- Readers:
  - [`src/hydrol_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrol_read.f90) (`hydrology.hyd`)
  - [`src/topo_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/topo_read.f90) (`topography.hyd`)
  - [`src/field_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/field_read.f90) (`field.fld`)
  - [`src/shade_factor_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/shade_factor_read.f90) (`shade_factor.shf`)
- Type definitions: [`src/hydrology_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrology_data_module.f90), [`src/topography_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/topography_data_module.f90), [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90)

## hydrology.hyd

Per-HRU hydrology parameter sets (lateral flow, canopy, evaporation compensation, percolation, enrichment ratios). Read into `hyd_db` (`type hydrology_db` in `src/hydrology_data_module.f90`).

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "" | parameter set name |
| 2 | lat_ttime | real | days | 0.0 | exponential of the lateral flow travel time (0..120) |
| 3 | lat_sed | real | g/L | 0.0 | sediment concentration in lateral flow |
| 4 | canmx | real | mm H2O | 0.0 | maximum canopy storage |
| 5 | esco | real | none | 0.0 | soil evaporation compensation factor (0..1) |
| 6 | epco | real | none | 0.0 | plant water uptake compensation factor (0..1) |
| 7 | erorgn | real | none | 0.0 | organic N enrichment ratio (0 = model calculates per event) |
| 8 | erorgp | real | none | 0.0 | organic P enrichment ratio (0 = model calculates per event) |
| 9 | cn3_swf | real | none | 0.0 | soil water at CN3 (0 = field capacity, 0.99 = near saturation) |
| 10 | biomix | real | none | 0.0 | biological mixing efficiency, applied at end of each calendar year |
| 11 | perco | real | none | 0.0 | percolation coefficient, linear adjustment to daily perc (0..1) |
| 12 | lat_orgn | real | ppm | 0.0 | organic N concentration in lateral flow |
| 13 | lat_orgp | real | ppm | 0.0 | organic P concentration in lateral flow |
| 14 | pet_co | real | none | 1.0 | radiation coefficient used in Hargreaves equation |
| 15 | latq_co | real | none | 0.3 | lateral soil flow coefficient, linear adjustment to daily lateral flow (0..1) |

Example from `refdata/Osu_1hru/hydrology.hyd`:

```
hydrology.hyd: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                 lat_ttime       lat_sed       can_max          esco          epco   orgn_enrich   orgp_enrich       cn3_swf       bio_mix         perco      lat_orgn      lat_orgp      harg_pet       latq_co  
hyd0001                0.00000       0.00000       1.00000       0.95000       0.50000       0.00000       0.00000       0.95000       0.20000       0.90000       0.00000       0.00000       0.00000       0.01000
```

Editor column names (`can_max`, `harg_pet`, `bio_mix`) differ from source field names. The reader uses position only.

## topography.hyd

Per-HRU topography parameter sets. Read into `topo_db` (`type topography_db` in `src/topography_data_module.f90`).

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "default" | parameter set name |
| 2 | slope | real | m/m | 0.02 | average slope steepness in HRU |
| 3 | slope_len | real | m | 50.0 | average slope length for erosion |
| 4 | lat_len | real | m | 50.0 | slope length for lateral subsurface flow |
| 5 | dis_stream | real | m | 100.0 | average distance to stream |
| 6 | dep_co | real | none | 1.0 | deposition coefficient |

Example from `refdata/Osu_1hru/topography.hyd`:

```
topography.hyd: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       slp       slp_len       lat_len      dist_cha         depos  
topohru0001            0.01078      10.00000      10.00000     121.00000       0.00000
```

The same type and array are also used for landscape units; `hru-data.hru` and the subbasin objects both reference entries in `topo_db` by name.

## field.fld

Per-field geometry used by the wind-erosion routine. Read into `field_db` (`type fields_db` in `src/topography_data_module.f90`).

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "default" | parameter set name |
| 2 | length | real | m | 500.0 | field length for wind erosion |
| 3 | wid | real | m | 100.0 | field width for wind erosion |
| 4 | ang | real | deg | 30.0 | field angle for wind erosion |

Example from `refdata/Osu_1hru/field.fld` (first four records shown):

```
field.fld: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       len            wd           ang  
fld011               500.00000     100.00000      30.00000  
fld012               500.00000     100.00000      30.00000  
fld031               500.00000     100.00000      30.00000  
fld032               500.00000     100.00000      30.00000
```

The reader uses a `read .. backspace .. read` pattern, but the file format is one record per line, same as the other files on this page.

## shade_factor.shf

Time- and landscape-unit-resolved shade factor used by the channel water-temperature routine. Read into `shf_db` (`type shade_factor_data` in `src/hydrograph_module.f90`). Activated per channel by `sf_on = 1` in [`temperature.cha`](../input-reference/cha.md); when `sf_on = 0` the channel uses the calibration-file value instead.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | jday | int | day of year | 0 | day of year the record applies to |
| 2 | lsu | int | none | 0 | landscape unit number |
| 3 | value | real | none | 0.0 | shade factor value |

In `src/ch_temp.f90` the array is scanned for the matching `(jday, lsu)` pair and the `value` is assigned to `ssff`. There is no name column.

No example dataset in `refdata/` ships a `shade_factor.shf` file.

## Related files

- [`file.cio`](../input-reference/file-cio.md). The `hru` line selects `hydrology.hyd`, `topography.hyd`, and `field.fld`; the shade file is listed separately.
- [`hru-data.hru`](../input-reference/hru.md). Every HRU references one entry from each of `hydrology.hyd`, `topography.hyd`, and `field.fld`.
- [`temperature.cha`](../input-reference/cha.md). Controls whether `shade_factor.shf` is consulted (`sf_on` flag).

---
title: hydrology and topography (per HRU)
description: HRU hydrology, topography and field parameter files (hydrology.hyd, topography.hyd, field.fld) and the channel shade factor file shade_factor.shf.
status: review
verified_against:
  - src/hydrol_read.f90
  - src/topo_read.f90
  - src/field_read.f90
  - src/shade_factor_read.f90
  - src/hydrology_data_module.f90
  - src/topography_data_module.f90
  - src/hydrograph_module.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_read.f90
  - src/topohyd_init.f90
  - src/hydro_init.f90
  - src/swr_substor.f90
  - src/swr_percmicro.f90
  - src/swr_latsed.f90
  - src/sq_canopyint.f90
  - src/et_act.f90
  - src/et_pot.f90
  - src/plant_init.f90
  - src/curno.f90
  - src/nut_orgn.f90
  - src/nut_orgnc2.f90
  - src/nut_psed.f90
  - src/time_control.f90
  - src/mgt_newtillmix_cswat0.f90
  - src/rls_routesurf.f90
  - src/time_conc_init.f90
  - src/ru_read.f90
  - src/ch_temp.f90
  - src/ch_read_temp.f90
  - src/channel_data_module.f90
  - src/cal_parm_select.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

This page covers three HRU parameter files and one channel file:

- `hydrology.hyd`: lateral flow, canopy storage, evaporation, percolation and enrichment parameters.
- `topography.hyd`: slope, slope lengths and the deposition coefficient. Also used by routing units.
- `field.fld`: field length and width for routing water and sediment across the landscape. Also used by routing units.
- `shade_factor.shf`: daily shade factors for the channel water temperature routine.

An HRU picks one record from each of the first three files by name, in the `hydro`, `topo` and `field` columns of [`hru-data.hru`](hru.md). `hydrology.hyd`, `topography.hyd` and `field.fld` are named on the `hydrology` line of [`file.cio`](file-cio.md). `shade_factor.shf` is not listed in [`file.cio`](../input-reference/file-cio.md); SWAT+ looks for a file with that name in the project folder.

All four files are free format and whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one record. The readers do not match columns by header name, so every value must be present and in the order given. Record names are stored with at most 16 characters.

An unmatched or misspelt `hydro` or `topo` name in [`hru-data.hru`](../input-reference/hru.md) makes the HRU use the first record of the file without a message (see [name lookup](hru.md#name-lookup)). `hydrology.hyd` and `topography.hyd` must therefore exist and must contain every name used.

## hydrology.hyd

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Name of the hydrology record, matched against the `hydro` column of [`hru-data.hru`](../input-reference/hru.md). |
| 2 | `lat_ttime` | days | 0 to 180 | Lateral flow travel time, called `lat_time` in earlier documentation. 0 lets SWAT+ compute it from the soil. See [Lateral flow](#lateral-flow). |
| 3 | `lat_sed` | mg/L | 0 to 5000 | Sediment concentration in lateral and tile flow. |
| 4 | `can_max` | mm H₂O | 0 to 100 | Maximum canopy storage when the canopy is fully developed. |
| 5 | `esco` | - | 0.01 to 1 | Soil evaporation compensation factor. See [Soil evaporation](#soil-evaporation). |
| 6 | `epco` | - | 0.01 to 1 | Plant uptake compensation factor. |
| 7 | `orgn_enrich` | - | 0 to 5 | Organic N enrichment ratio for loading with sediment. 0 lets SWAT+ compute it for each runoff event. |
| 8 | `orgp_enrich` | - | 0 to 5 | Organic and sediment-attached P enrichment ratio for loading with sediment. 0 lets SWAT+ compute it for each runoff event. |
| 9 | `cn3_swf` | - | 0 to 1 | Soil water factor for the moisture condition III curve number: 0 puts it at field capacity, 1 at saturation. |
| 10 | `bio_mix` | - | 0 to 1 | Biological mixing efficiency. |
| 11 | `perco` | - | 0 to 1 | Percolation coefficient for the bottom soil layer. See [Percolation from the soil profile](#percolation-from-the-soil-profile). |
| 12 | `lat_orgn` | mg/L | 0 to 200 | Organic N concentration in lateral flow. |
| 13 | `lat_orgp` | mg/L | 0 to 200 | Organic P concentration in lateral flow. |
| 14 | `pet_co` | - | 0.8 to 1.2 | Multiplier on potential evapotranspiration. Older files call this column `harg_pet`. See [Potential evapotranspiration](#potential-evapotranspiration). |
| 15 | `latq_co` | - | 0 to 1 | Lateral flow coefficient. See [Lateral flow](#lateral-flow). |

For an HRU with tile drains (set in its [`landuse.lum`](lum.md) record), SWAT+ replaces `cn3_swf` with 0.95 and `perco` with 0.1 at the start of the run, whatever the record gives, and calibration changes to these two parameters are skipped for that HRU.

### Lateral flow

Lateral flow is computed for each soil layer below the first with a hillslope storage method:

$$q_{lat,ly} = 0.024\;\mathrm{latq\_co}\;\frac{2\,SW_{ex,ly}}{\phi_{d,ly}/h_{ly}}\;K_{sat,ly}\;\frac{slp}{L_{lat}}$$

where $SW_{ex,ly}$ is the water above field capacity in the layer (mm), $\phi_{d,ly}$ the drainable porosity (saturation minus field capacity, mm), $h_{ly}$ the layer thickness (mm), $K_{sat,ly}$ the saturated hydraulic conductivity (mm/h), $slp$ the `slp` value from `topography.hyd` and $L_{lat}$ its `lat_len` (m). The result is limited to the water above field capacity. The top layer produces no lateral flow. `latq_co` scales lateral flow linearly; 0 turns it off.

Lateral flow does not leave the HRU on the day it is generated. A fraction of the stored lateral flow is released each day:

$$f_{lat} = 1 - \exp\!\left(-\frac{1}{TT_{lat}}\right)$$

where $TT_{lat}$ is `lat_ttime` in days. When `lat_ttime` is 0, SWAT+ computes it from the soil and the lateral slope length:

$$TT_{lat} = \max\!\left(1,\; 10.4\,\frac{L_{lat}}{K_{sat,mx}}\right)$$

with $K_{sat,mx}$ the highest saturated hydraulic conductivity in the profile (mm/h). Set `lat_ttime` to a specific value only when the base flow behaviour of the watershed is well known.

### Soil evaporation

The evaporative demand on the soil is distributed with depth. The cumulative demand down to depth $z$ (mm) is

$$E_z = E_s\,\frac{z}{z + \exp(2.374 - 0.00713\,z)}$$

where $E_s$ is the soil evaporation demand for the day. A layer whose top is at depth $z_u$ and bottom at $z_l$ is asked for

$$E_{ly} = E_{z_l} - (1 - \mathrm{esco})\,E_{z_u}$$

so with `esco` = 0 each layer meets only its share of the depth distribution, and as `esco` increases more of the demand can be met from lower layers. Layers below the soil evaporation depth do not take part. The demand on a layer is further reduced when the layer is drier than field capacity.

### Plant uptake compensation

`epco` is copied to every plant of the HRU's plant community when the plants are initialized. As `epco` approaches 1, more of the water uptake demand can be met by lower layers when upper layers are dry; as it approaches 0, uptake stays closer to the original depth distribution.

### Enrichment ratios

When `orgn_enrich` or `orgp_enrich` is above 0.001, it is used as a fixed enrichment ratio for organic N, or for organic and sediment-attached P, for every runoff event. Otherwise SWAT+ computes the enrichment ratio for each event from the sediment concentration in surface runoff. The enrichment ratio is the ratio of the concentration of the constituent in the transported sediment to its concentration in the soil surface layer; it is above 1 because the sediment in runoff contains a larger share of the fine particles that the nutrients are attached to.

### Curve number soil water factor

`cn3_swf` sets the soil water content at which the curve number for moisture condition III applies:

$$SW_{CN3} = FC + \mathrm{cn3\_swf}\,(SAT - FC)$$

where $FC$ and $SAT$ are the profile water contents at field capacity and saturation. Larger values delay the onset of surface runoff after dry periods. See [hydrology](../model-theory/hydrology.md) in the model theory.

### Biological mixing

Biological mixing redistributes residue and nutrients in the soil through the activity of earthworms and other soil biota, using the same method as a tillage operation with `bio_mix` as the mixing efficiency. With `carbon` = 0 in [`codes.bsn`](codes-bsn.md), it is applied once at the end of every calendar year, down to 50 mm or the bottom of the profile if that is shallower. With the other `carbon` codes this column is not used; `carbon` = 2 applies a daily biological mixing with an efficiency taken from the tillage data.

### Percolation from the soil profile

`perco` limits percolation out of the bottom soil layer, for example to represent an impermeable layer or a high water table. Percolation between the upper layers is not affected. The potential percolation from the bottom layer is multiplied by

$$f_{perc} = \min\!\left[1,\; \exp\!\left(-\left(1.0052\,\ln\!\left(-\ln \mathrm{perco}\right) + 5.6862\right)\right)\right]$$

The relation is strongly non-linear:

| `perco` | 0 | 0.1 | 0.5 | 0.8 | 0.9 | 0.95 | 0.99 | 0.999 and above |
|---|---|---|---|---|---|---|---|---|
| fraction of potential percolation | 0 | 0.002 | 0.005 | 0.015 | 0.033 | 0.067 | 0.35 | 1 |

So 0 stops percolation from the profile, values up to about 0.9 allow only a few percent of it, and the restriction is lifted only as `perco` approaches 1.

### Potential evapotranspiration

`pet_co` multiplies the potential evapotranspiration of the HRU, whichever method is selected in [`codes.bsn`](codes-bsn.md) (Priestley-Taylor, Penman-Monteith, Hargreaves or values read from file). A value of 0 is treated as 1. Values below 0.01 are taken as the old Hargreaves coefficient written to `harg_pet` by earlier editors and divided by 0.0023, so 0.0023 becomes 1.0.

### Canopy storage

The canopy storage available on a day is

$$CAN_{day} = \mathrm{can\_max}\;\frac{LAI}{LAI_{mx}}$$

where $LAI$ is the current leaf area index of the plant community and $LAI_{mx}$ its maximum. Precipitation fills the canopy before it reaches the ground.

### Sediment and organic nutrients in lateral flow

`lat_sed` adds sediment to the HRU sediment yield in proportion to lateral and tile flow, and `lat_orgn` and `lat_orgp` add organic N and P in proportion to lateral flow. In 62.0.1 the sediment from `lat_sed` is added twice: once as a mass computed from the HRU area and once again as a value that does not use the area. Sediment yields from HRUs with a non-zero `lat_sed` therefore include an extra term. The conversion used for `lat_orgn` and `lat_orgp` is 100 times smaller than mg/L of lateral flow would give, so the loads are 1% of what the stated units suggest.

## topography.hyd

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | `default` | Name of the topography record, matched against the `topo` column of [`hru-data.hru`](../input-reference/hru.md) and of [`rout_unit.rtu`](../input-reference/units.md#rout_unitrtu). |
| 2 | `slp` | m/m | 0.02 | Average slope steepness, usually computed from the DEM. Used for lateral flow, the USLE slope-length factor, time of concentration and sediment transport across the HRU. |
| 3 | `slp_len` | m | 50 | Average slope length for erosion: the distance over which sheet flow is the main surface runoff process, measured to the point where flow begins to concentrate. Used in the USLE slope-length factor. The full value is used: 62.0.1 does not apply the maximum slope length of the HRU's conservation practice. |
| 4 | `lat_len` | m | 50 | Slope length for lateral subsurface flow, usually longer than `slp_len`. A value of 0 is replaced by 50 m. |
| 5 | `dist_cha` | m | 100 | Average distance to the stream. Not used. |
| 6 | `depos` | - | 1 | Deposition coefficient for sediment transport capacity when surface runoff from another object is routed across the HRU. A larger value gives a higher transport capacity, so more sediment leaves the HRU. |

The built-in values apply only to a record that is never read; an HRU always uses a record from the file.

When runoff from upslope objects is routed across an HRU, its sediment transport capacity is proportional to

$$\mathrm{depos}\; C\; slp^{1.4}\; w^{1.4}$$

and to the overland flow, where $C$ is the USLE cover factor of the HRU and $w$ the field width `wd` from `field.fld`.

## field.fld

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | `default` | Name of the field record, matched against the `field` column of [`hru-data.hru`](../input-reference/hru.md) and of [`rout_unit.rtu`](../input-reference/units.md#rout_unitrtu). |
| 2 | `len` | m | 500 | Field length. Used for the time of concentration of routing units; not used for HRUs. |
| 3 | `wd` | m | 100 | Field width. Used in the sediment transport capacity when surface runoff is routed across an HRU. |
| 4 | `ang` | degrees | 30 | Field angle. Not used. |

An HRU whose `field` entry is `null`, or a name that is not found, uses the built-in values.

## shade_factor.shf

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `jday` | day of year | Day the value applies to (1 to 365). |
| 2 | `cha` | - | Channel number (row in [`chandeg.con`](../input-reference/con.md)). In revisions before 62.0.1 this column was a landscape unit number. |
| 3 | `value` | fraction | Shade factor, the fraction of incoming solar radiation blocked before it reaches the water surface. |

The file has no name column and is read as a list of (day, channel, value) rows. The channel water temperature routine reduces short-wave radiation at the water surface by the factor $(1 - \text{value})$. On day 366 of leap years the factor is 0.5.

The file is meant to be used when `sf_on` = 1 in [`temperature.cha`](cha.md). In 62.0.1 the temperature routine takes all its settings from the built-in record instead of from the rows of [`temperature.cha`](../input-reference/cha.md#temperaturecha). The built-in record has `sf_on` = 0 and `ssff` = 0.5, so the shade factor is 0.5 for every channel and day, and `shade_factor.shf` is read but not used. No example dataset in `refdata/` has a `shade_factor.shf` file.

## Calibration

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md) (see [parameter change files](../calibration/parameter-change-files.md)), using these names: `lat_ttime`, `lat_sed`, `canmx` (`can_max`), `esco`, `epco`, `erorgn` (`orgn_enrich`), `erorgp` (`orgp_enrich`), `cn3_swf`, `biomix` (`bio_mix`), `perco`, `lat_orgn`, `lat_orgp`, `petco` (`pet_co`), `latq_co`, `slope` (`slp`), `slope_len` (`slp_len`), `lat_len`, `dis_stream` (`dist_cha`), `field_len` (`len`), `field_wid` (`wd`) and `field_ang` (`ang`).

A change to `lat_ttime` is applied to the daily release fraction $f_{lat}$, which SWAT+ has already computed from the input, and the result is then converted again as if it were a travel time in days. The effect of a `lat_ttime` change is therefore not the effect of changing the travel time in the file by the same amount. Changes to `dis_stream` and `field_ang` have no effect, because the values are not used.

## Examples

`refdata/Ames_sub1/hydrology.hyd` in the SWAT+ repository (first two rows):

```
hydrology.hyd:
name                 lat_ttime       lat_sed       can_max          esco          epco   orgn_enrich   orgp_enrich       cn3_swf       bio_mix         perco      lat_orgn      lat_orgp        pet_co       latq_co  
hyd0001                0.00000       0.00000       0.00000       0.95000       1.00000       0.00000       0.00000       0.00000       0.20000       0.50000       0.00000       0.00000       1.00000       0.01000  
hyd0002                0.00000       0.00000       0.00000       0.95000       1.00000       0.00000       0.00000       0.00000       0.20000       0.50000       0.00000       0.00000       1.00000       0.01000  
```

Lateral flow travel time and enrichment ratios are computed by SWAT+, there is no canopy storage, and `cn3_swf` = 0 puts the moisture condition III curve number at field capacity. `perco` = 0.5 lets only about 0.5% of the potential percolation leave the bottom of the profile (unless the HRU is tile drained, which resets `perco` to 0.1), and `latq_co` = 0.01 keeps lateral flow small.

`refdata/Osu_1hru/hydrology.hyd` uses the older column header `harg_pet` with the value 0, which SWAT+ treats as a `pet_co` of 1.

`refdata/Ames_sub1/topography.hyd` (first two rows):

```
topography.hyd: 
name                       slp       slp_len       lat_len      dist_cha         depos  
topohru0001            0.02500      91.46300      91.46300     100.00000       1.00000  
topohru0002            0.02500      91.46300      91.46300     100.00000       1.00000  
```

`refdata/Osu_1hru/field.fld` (first two rows):

```
field.fld: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       len            wd           ang  
fld011               500.00000     100.00000      30.00000  
fld012               500.00000     100.00000      30.00000  
```

## Related files

- [`hru-data.hru`](hru.md): selects the records by name in its `hydro`, `topo` and `field` columns.
- [`file.cio`](file-cio.md): names the three HRU files on its `hydrology` line.
- [`landuse.lum`](lum.md): sets tile drainage, which overrides `cn3_swf` and `perco`.
- [`codes.bsn`](codes-bsn.md): PET method and `carbon` code that `pet_co` and `bio_mix` depend on.
- [`temperature.cha`](cha.md): channel temperature settings, including `sf_on` for `shade_factor.shf`.
- [Hydrology](../model-theory/hydrology.md) and [soil water](../model-theory/soil-water-temperature.md) in the model theory.

??? quote "Sources"

    - Readers: [`hydrol_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrol_read.f90), [`topo_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topo_read.f90), [`field_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/field_read.f90), [`shade_factor_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/shade_factor_read.f90) (called from [`proc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_read.f90))
    - Type definitions: `type hydrology_db` in [`hydrology_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrology_data_module.f90); `type topography_db` and `type fields_db` in [`topography_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topography_data_module.f90); `type shade_factor_data` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - File names: `type input_hydrology` and `type shade_factor` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), `in_hyd` read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Copy to each HRU, tile override, `pet_co` and `perco` conversion: [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90); routing units in [`ru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_read.f90)
    - Lateral flow: [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90), [`swr_percmicro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmicro.f90), [`swr_substor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_substor.f90)
    - Evaporation, PET and uptake: [`et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90), [`et_pot.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_pot.f90), [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90)
    - Canopy: [`sq_canopyint.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_canopyint.f90); curve number: [`curno.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/curno.f90)
    - Enrichment ratios: [`nut_orgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_orgn.f90), [`nut_orgnc2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_orgnc2.f90), [`nut_psed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_psed.f90)
    - Lateral sediment and organic nutrients: [`swr_latsed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_latsed.f90)
    - Biological mixing: [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90), [`mgt_newtillmix_cswat0.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_cswat0.f90)
    - Landscape routing and time of concentration: [`rls_routesurf.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rls_routesurf.f90), [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90)
    - Shade factor use: [`ch_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_temp.f90), [`ch_read_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_temp.f90), `type channel_temperature_data` in [`channel_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/channel_data_module.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | hydrology.hyd | `lat_ttime` | `hyd_db%lat_ttime` |
    | hydrology.hyd | `lat_sed` | `hyd_db%lat_sed` |
    | hydrology.hyd | `can_max` | `hyd_db%canmx` |
    | hydrology.hyd | `esco` | `hyd_db%esco` |
    | hydrology.hyd | `epco` | `hyd_db%epco` |
    | hydrology.hyd | `orgn_enrich` | `hyd_db%erorgn` |
    | hydrology.hyd | `orgp_enrich` | `hyd_db%erorgp` |
    | hydrology.hyd | `cn3_swf` | `hyd_db%cn3_swf` |
    | hydrology.hyd | `bio_mix` | `hyd_db%biomix` |
    | hydrology.hyd | `perco` | `hyd_db%perco` (converted to `hru%hyd%perco_lim`) |
    | hydrology.hyd | `lat_orgn` | `hyd_db%lat_orgn` |
    | hydrology.hyd | `lat_orgp` | `hyd_db%lat_orgp` |
    | hydrology.hyd | `pet_co` | `hyd_db%pet_co` |
    | hydrology.hyd | `latq_co` | `hyd_db%latq_co` |
    | topography.hyd | `slp` | `topo_db%slope` |
    | topography.hyd | `slp_len` | `topo_db%slope_len` |
    | topography.hyd | `lat_len` | `topo_db%lat_len` |
    | topography.hyd | `dist_cha` | `topo_db%dis_stream` |
    | topography.hyd | `depos` | `topo_db%dep_co` |
    | field.fld | `len` | `field_db%length` |
    | field.fld | `wd` | `field_db%wid` |
    | field.fld | `ang` | `field_db%ang` |
    | shade_factor.shf | `jday`, `cha`, `value` | `shf_db%jday`, `shf_db%cha`, `shf_db%value` |

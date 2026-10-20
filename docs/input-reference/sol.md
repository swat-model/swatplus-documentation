---
title: soils.sol
description: Soil profile and layer properties for every soil in the watershed, with the optional soil_lyr_depths.sol and soils_lte.sol files.
status: review
verified_against:
  - src/soil_db_read.f90
  - src/soil_data_module.f90
  - src/soil_module.f90
  - src/soils_init.f90
  - src/soil_phys_init.f90
  - src/soil_nutcarb_init.f90
  - src/soils_test_adjust.f90
  - src/soil_lte_db_read.f90
  - src/hru_read.f90
  - src/hru_lte_read.f90
  - src/hydro_init.f90
  - src/cn2_init.f90
  - src/curno.f90
  - src/albedo.f90
  - src/mgt_plantop.f90
  - src/pl_root_gro.f90
  - src/nut_pminrl2.f90
  - src/nut_nlch.f90
  - src/proc_hru.f90
  - src/proc_read.f90
  - src/main.f90.in
  - src/cal_parm_select.f90
  - src/cal_conditions.f90
  - src/conditions.f90
  - src/calsoft_sed.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`soils.sol` defines every soil used in the watershed. Each soil is a block of lines: one profile line with the soil name, number of layers, hydrologic soil group and other whole-profile values, followed by one line per layer with depth, bulk density, available water capacity, saturated hydraulic conductivity, organic carbon, texture and other layer properties. An HRU picks a soil by name in the `soil` column of [`hru-data.hru`](hru.md). The file is named first on the `soils` line of [`file.cio`](file-cio.md) (default `soils.sol`).

Every HRU should name a soil that is in the file. An unknown name is not reported: the HRU silently gets the first soil in `soils.sol`. Check the `sname` column of [`checker.out`](../output-reference/checker-diagnostics.md#checkerout), which lists the soil each HRU uses.

The initial nutrient and carbon contents of the soil come from [`nutrients.sol`](ini.md#nutrientssol), which an HRU selects through [`soil_plant.ini`](ini.md#soil_plantini). The same `soils` line of [`file.cio`](../input-reference/file-cio.md) names [`nutrients.sol`](../input-reference/ini.md#nutrientssol) second and `soils_lte.sol` third (see [soils_lte.sol](#soils_ltesol) below).

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each soil then takes `nly + 1` lines: the profile line and `nly` layer lines. The reader counts soils by reading each profile line and skipping the next `nly` lines, so `nly` must equal the number of layer lines that follow. Columns are read by position; the header names are not checked. Spacing is not significant, so the wide indentation the SWAT+ Editor gives the layer lines has no meaning.

### Profile line

| # | Column | Units | Used if zero or out of range | Description |
|---|--------|-------|------------------------------|-------------|
| 1 | `name` | - | - | Soil name, up to 20 characters, matched against the `soil` column of [`hru-data.hru`](../input-reference/hru.md). |
| 2 | `nly` | - | - | Number of layer lines that follow. There is no upper limit in the model. |
| 3 | `hyd_grp` | - | - | Hydrologic soil group: `A`, `B`, `C` or `D`. It selects the curve number from [`cntable.lum`](lum-tables.md#cntablelum) and the conductivity used when `soil_k` is zero. Dual groups such as `A/D` and lower-case letters are not recognized. |
| 4 | `dp_tot` | mm | - | Maximum rooting depth. See [Rooting depth](#rooting-depth) for how 62.0.1 uses it. |
| 5 | `anion_excl` | fraction | 0.5 if 0; 0.99 if 1 or more | Fraction of porosity from which anions are excluded. |
| 6 | `perc_crk` | fraction | - | Potential (maximum) crack volume of the soil profile as a fraction of total soil volume. Used only when crack flow is switched on (`crack` = 1 in [`codes.bsn`](codes-bsn.md#crack-flow)). |
| 7 | `texture` | - | - | Texture label, up to 16 characters. Only the first whitespace-delimited word is read, so `L-L-L-L` is read whole but `L- L- L- L` is read as `L-`. The label is not used in any process; it can serve as a condition in [`calibration.cal`](../calibration/parameter-change-files.md) (condition `texture`). |

### Layer lines

Layers are listed from the surface down. Each line has fourteen values.

| # | Column | Units | Used if zero or out of range | Description |
|---|--------|-------|------------------------------|-------------|
| 1 | `dp` | mm | - | Depth from the soil surface to the bottom of the layer. |
| 2 | `bd` | Mg/m³ | 1.3 if 0; capped at 2.0 | Moist bulk density: oven-dry mass divided by the soil volume at or near field capacity. |
| 3 | `awc` | mm H₂O/mm soil | 0.005 if 0; capped at 0.8 | Available water capacity: water held between field capacity (-0.033 MPa) and permanent wilting point (-1.5 MPa). |
| 4 | `soil_k` | mm/h | by `hyd_grp` if 0 or less: A 50, B 20, C 5, D 2, other 10 | Saturated hydraulic conductivity. |
| 5 | `carbon` | % of soil mass | 0.001 if below 0.001 | Organic carbon content of the fine earth (material passing a 2 mm sieve). |
| 6 | `clay` | % | - | Clay, particles below 0.002 mm. |
| 7 | `silt` | % | - | Silt, particles between 0.002 and 0.05 mm. |
| 8 | `sand` | % | - | Sand, particles between 0.05 and 2.0 mm. |
| 9 | `rock` | % of total mass | capped at 98 | Rock fragments, particles above 2 mm. |
| 10 | `alb` | fraction | - | Moist soil albedo. Only the top layer value is used. |
| 11 | `usle_k` | 0.013 t m² h/(m³ t cm) | - | USLE soil erodibility factor. Only the top layer value is used. |
| 12 | `ec` | dS/m | - | Electrical conductivity. Read and reported, but not used by any process in 62.0.1. |
| 13 | `caco3` | % | 2.8 if 0 | Calcium carbonate content. |
| 14 | `ph` | - | 6.5 if 0 | Soil pH. Read and reported, but not used by any process in 62.0.1. |

`clay`, `silt` and `sand` are percentages of the mineral fraction and should add up to 100. The model does not check this, except that in sub-daily runs the sand content of the top layer is reset to $100 - \mathrm{clay} - \mathrm{silt}$.

## Layering

### Thin first layer

After reading a soil, the reader checks the first layer. If it is shallower than 20 mm and the soil has only one layer, or the second layer reaches deeper than 20 mm, the bottom of the first layer is set to 20 mm.

### Added 10 mm surface layer

Without a `soil_lyr_depths.sol` file in the run folder (the usual case), SWAT+ adds a 10 mm surface layer to every soil whose first layer is deeper than 19.5 mm. The new layer takes all its properties from the first input layer, so a soil with four input layers is simulated with five. The first input layer then runs from 10 mm to its listed depth. Outputs by layer count this added layer.

If the first layer is 19.5 mm or shallower (possible only when the second layer is also within 20 mm), no layer is added and the first layer is given a depth of 10 mm.

### soil_lyr_depths.sol

If a file named `soil_lyr_depths.sol` is in the run folder, every soil is re-layered to the depths it lists. The file is not named in [`file.cio`](../input-reference/file-cio.md); SWAT+ looks for this name.

- Line 1 is a title, line 2 a header and line 3 a units label; all three are skipped.
- Each later line gives one depth in mm, from the surface down, as a whole number.
- Depths of 10 mm or less are skipped. The first layer is always 0 to 10 mm.
- A depth beyond the bottom of a soil is replaced by its total depth, and the list ends there for that soil. If the deepest listed depth is shallower than a soil, the profile is cut off at that depth.

Each new layer takes the depth-weighted average of the input layers it overlaps, computed millimetre by millimetre, for every layer property. `refdata/Ames_sub1/soil_lyr_depths.sol` lists 10, 25, 50, 100, 150, 200, 300, 450, 600, 750, 900, 1050, 1200, 1500, 1800 and 2100 mm, so a 2000 mm soil gets sixteen layers with the last from 1800 to 2000 mm.

### Septic biozone layer

In an HRU with a septic system (the `sep` column of [`landuse.lum`](lum.md)), the profile is split further so that the biozone set in [`septic.str`](str.md) is a separate layer.

## Derived layer properties

At the start of the run SWAT+ derives the water contents of each layer from `bd`, `awc` and `clay`. As volume fractions:

$$\theta_{wp} = 0.40\,\frac{c\,\rho_b}{100}, \qquad \theta_{fc} = \theta_{wp} + AWC, \qquad \phi = 1 - \frac{\rho_b}{2.65}$$

where $c$ is `clay` (%), $\rho_b$ is `bd` and $AWC$ is `awc`. If $\theta_{wp}$ is zero (no clay) it is set to 0.005. If $\theta_{fc}$ reaches the porosity $\phi$, field capacity is set to $\phi - 0.05$ and the wilting point to $\theta_{fc} - AWC$; if that is not positive, field capacity becomes $0.75\,\phi$ and the wilting point $0.25\,\phi$.

For a layer of thickness $h$ (mm), the plant-available water at field capacity is $FC = h\,(\theta_{fc} - \theta_{wp})$, the water between wilting point and saturation is $UL = h\,(\phi - \theta_{wp})$, and the percolation travel time (h) is

$$TT_{perc} = \frac{UL - FC}{K_{sat}}$$

with a minimum of 1 hour, where $K_{sat}$ is `soil_k`. The profile sums of $FC$ and $UL$ are reported as `sumfc` and `sumul` in [`checker.out`](../output-reference/checker-diagnostics.md#checkerout).

The crack volume of each layer is

$$V_{crk} = \mathrm{perc\_crk} \times 0.916\,e^{-0.0012\,z}\,h$$

where $z$ is the depth to the bottom of the layer (mm).

The top layer's sand, silt and clay set the particle-size make-up of eroded sediment (sand, silt, clay, small and large aggregates). For the Green and Ampt infiltration method, the wetting front suction head is estimated from the porosity, clay and sand of the top layer.

## Use of the soil properties

### Initial soil water

Each layer starts at a fraction of its field capacity water. The fraction is `sw_init` in [`parameters.bsn`](parameters-bsn.md). If `sw_init` is zero, it is estimated from the average annual precipitation $P$ (mm) of the HRU's weather generator:

$$f = \frac{P}{P + \exp(9.043 - 0.002135\,P)}$$

The `sw_frac` column of [`soil_plant.ini`](ini.md#soil_plantini) is read but not used for this in 62.0.1.

### Rooting depth

`dp_tot` limits root depth only while plants that start the run already growing are initialized. After that the model sets the HRU's maximum rooting depth to the bottom of the soil profile. Each planting operation then lowers it to the smaller of its current value and the plant's maximum root depth in [`plants.plt`](plt.md). The value is never raised again during the run, so after a shallow-rooted crop is planted, later crops in the same HRU are limited to that depth as well. The `zmx` column of `checker.out` shows this profile depth. It does not show `dp_tot`.

### Runoff, percolation and solute leaching

`hyd_grp` picks one of the four curve numbers in [`cntable.lum`](lum-tables.md#cntablelum) for the HRU's land use. `anion_excl` reduces the pore volume available to nitrate, salts and other constituents moving down with percolating water. The nitrate that moves with a water volume $w$ (mm) leaving a layer is

$$NO3_{mobile} = NO3_{ly}\left[1 - \exp\!\left(\frac{-w}{(1 - \mathrm{anion\_excl})\,UL}\right)\right]$$

See [hydrology](../model-theory/hydrology.md), [soil water and temperature](../model-theory/soil-water-temperature.md) and [nutrient cycling](../model-theory/nutrient-cycling.md).

### Erosion

The MUSLE soil factor of an HRU uses the top layer only:

$$K \cdot CFRG = \mathrm{usle\_k}_1\; e^{-0.053\,\mathrm{rock}_1}$$

which is multiplied by the support practice factor from [`cons_practice.lum`](lum-tables.md#cons_practicelum) and the slope length and steepness factor. See [erosion and sediment](../model-theory/erosion-sediment.md).

### Albedo

On days with less than 0.5 mm of snow, the albedo of a bare HRU is the top layer `alb`. With plant cover it is $0.23\,(1 - e) + \mathrm{alb}_1\,e$, where $e = \exp(-5\times10^{-5}(CV + 0.1))$ and $CV$ is above-ground biomass plus residue (kg/ha). There is no lower limit on `alb`, so a zero value gives zero albedo for bare soil.

### Carbon and nutrients

`carbon`, `bd` and the layer thickness set the starting organic matter of each layer: the soil mass is $10\,000\,h\,\rho_b$ kg/ha, organic carbon is `carbon` percent of that, and organic matter is carbon divided by 0.58. How this is split into pools depends on the carbon model (the `carbon` column of [`codes.bsn`](codes-bsn.md#carbon-model)) and on [`nutrients.sol`](../input-reference/ini.md#nutrientssol); see [nutrients.sol](ini.md#nutrientssol). In 62.0.1 the 0.001% floor on `carbon` applies to every layer; earlier revisions applied it to the top layer only.

With the Vadas and White phosphorus model (`soil_p` = 1 in [`codes.bsn`](../input-reference/codes-bsn.md)), `clay` and `carbon` set the initial phosphorus sorption coefficient and `caco3` sets the rate of transfer between the active and stable mineral P pools:

$$k_{as} = 0.0023\,\mathrm{caco3} + 0.005, \qquad 0.002 \le k_{as} \le 0.05$$

`caco3` is not used with the original phosphorus model.

## Calibration and conditions

Soil columns can be changed in [`calibration.cal`](../calibration/parameter-change-files.md) with these parameter names, for a range of layers: `anion_excl`, `crk` (`perc_crk`), `z` (`dp`), `bd`, `awc`, `k` (`soil_k`), `cbn` (`carbon`), `clay`, `silt`, `sand`, `rock`, `alb`, `usle_k`, `ec`, `cal` (`caco3`) and `ph`. Changes to `z`, `bd`, `awc` and `clay` recompute the layer water contents and the curve number coefficients. See [parameter change files](../calibration/parameter-change-files.md).

Calibration changes are applied before the soil organic pools are set up, and that setup works from the `carbon` column. A `cbn` change acts on the layer's organic carbon pool, so it is replaced when the pools are initialized and has no lasting effect in 62.0.1.

The [`calibration.cal`](../calibration/parameter-change-files.md) conditions `hsg` and `texture` select HRUs by `hyd_grp` and `texture`. Decision tables can test `hyd_soil_group` and `k_factor` (the top layer `usle_k`).

## soils_lte.sol

`soils_lte.sol` is used only by HRU-LTE objects ([`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru)), which select a soil texture by name instead of a layered profile. Line 1 is a title and line 2 a header. The next twelve lines are read, one per texture class, each with four values:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `texture` | - | Texture class name, matched against the soil texture column of [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru). |
| 2 | `awc` | mm/mm | Available water capacity, multiplied by the soil depth given in [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru). |
| 3 | `por` | mm/mm | Porosity, multiplied by the same soil depth. |
| 4 | `scon` | mm/h | Saturated hydraulic conductivity. |

Twelve lines are always read. A project with HRU-LTE objects needs this file, since there is no built-in texture table.

## Example

`refdata/Osu_1hru/soils.sol` in the SWAT+ repository, first soil, with the spacing reduced:

```
soils.sol: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name     nly hyd_grp     dp_tot anion_excl perc_crk texture  dp      bd     awc   soil_k  carbon   clay   silt   sand   rock    alb  usle_k     ec  caco3     ph
SONGSAN    5       A 1200.00000    0.50000  0.50000 LS
                                                           180.0 1.39000 0.10871 16.10093 1.41760 17.300 25.000 57.700  7.700 0.2000 0.24977 0.0100 0.0000 0.0000
                                                           250.0 1.64000 0.09959 19.31345 0.58820 15.700 25.100 59.200 25.400 0.2000 0.25416 0.0100 0.0000 0.0000
                                                           460.0 1.48000 0.10069 18.05822 0.42350 16.100 26.000 57.900  1.700 0.2000 0.25832 0.0100 0.0000 0.0000
                                                           820.0 2.00000 0.07661 37.49110 0.20000 11.300 18.600 70.100 25.000 0.2000 0.22186 0.0100 0.0000 0.0000
                                                          1200.0 2.00000 0.06645 59.38071 0.26470  7.800 15.800 76.400 29.000 0.2000 0.19525 0.0100 0.0000 0.0000
```

A loamy sand in hydrologic group A with five layers to 1200 mm. Because the first layer reaches 180 mm, SWAT+ adds a 10 mm surface layer and simulates six layers. `caco3` and `ph` are zero, so the model uses 2.8% and 6.5. The albedo (0.20) and K factor (0.24977) of the first layer are the only values of those two columns that affect the run.

## Related files

- [`hru-data.hru`](hru.md): selects a soil by name in its `soil` column.
- [`soil_plant.ini` and `nutrients.sol`](ini.md): initial soil water, nutrients and other constituents of the soil.
- [`cntable.lum`](lum-tables.md#cntablelum): curve numbers chosen by `hyd_grp`.
- [`plants.plt`](plt.md): plant maximum root depth, which limits rooting together with the soil depth.
- [`codes.bsn`](codes-bsn.md) and [`parameters.bsn`](parameters-bsn.md): crack flow switch, phosphorus model, carbon model and `sw_init`.
- [`septic.str`](str.md): septic biozone layer.
- [`checker.out`](../output-reference/checker-diagnostics.md#checkerout): profile summary by HRU.

??? quote "Sources"

    - Readers: [`soil_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_db_read.f90), [`soil_lte_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_lte_db_read.f90), called from [`proc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_read.f90)
    - Type definitions: `type soil_profile_db`, `type soilayer_db` and `type soil_lte_database` in [`soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_data_module.f90); simulated soil in [`soil_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_module.f90)
    - Name lookup from `hru-data.hru`: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90)
    - Layering, `soil_lyr_depths.sol` and septic split: [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90), [`layersplit.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/layersplit.f90)
    - Value checks and derived properties: [`soil_phys_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_phys_init.f90), [`soil_awc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_awc_init.f90), [`soil_text_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_text_init.f90)
    - Initial soil water, rooting depth and MUSLE factor: [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90), [`mgt_plantop.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_plantop.f90), [`pl_root_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_root_gro.f90)
    - Curve number: [`cn2_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cn2_init.f90), [`curno.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/curno.f90)
    - Albedo, leaching and P: [`albedo.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/albedo.f90), [`nut_nlch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nlch.f90), [`nut_pminrl2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_pminrl2.f90)
    - Carbon and nutrient start values: [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90), called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - HRU-LTE texture lookup: [`hru_lte_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_read.f90)
    - Calibration and conditions: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90), [`cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90), [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90)
    - File name slots: `in_sol%soils_sol`, `in_sol%nut_sol`, `in_sol%lte_sol` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `soildb%s%snam` |
    | `nly` | `soildb%s%nly` |
    | `hyd_grp` | `soildb%s%hydgrp` |
    | `dp_tot` | `soildb%s%zmx` |
    | `anion_excl` | `soildb%s%anion_excl` |
    | `perc_crk` | `soildb%s%crk` |
    | `texture` | `soildb%s%texture` |
    | `dp` | `soildb%ly%z`, then `sol%phys%d` |
    | `bd` | `soildb%ly%bd`, then `sol%phys%bd` |
    | `awc` | `soildb%ly%awc`, then `sol%phys%awc` |
    | `soil_k` | `soildb%ly%k`, then `sol%phys%k` |
    | `carbon` | `soildb%ly%cbn`, then `sol%phys%cbn` and `soil1%cbn` |
    | `clay`, `silt`, `sand`, `rock` | `soildb%ly%clay`, `%silt`, `%sand`, `%rock`, then `sol%phys%...` |
    | `alb`, `usle_k`, `ec` | `soildb%ly%alb`, `%usle_k`, `%ec`, then `sol%ly%...` |
    | `caco3` | `soildb%ly%cal`, then `sol%ly%cal` |
    | `ph` | `soildb%ly%ph`, then `sol%ly%ph` |
    | `soils_lte.sol` columns | `soil_lte%texture`, `%awc`, `%por`, `%scon` |

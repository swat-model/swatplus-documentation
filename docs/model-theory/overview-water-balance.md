---
title: Overview and Water Balance
description: The HRU water balance in SWAT+, the order of the daily landscape calculations, and where each term is reported.
status: review
verified_against:
  - src/hru_control.f90
  - src/et_act.f90
  - src/swr_percmain.f90
  - src/swr_substor.f90
  - src/sq_surfst.f90
  - src/output_landscape_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

The water balance drives everything else SWAT+ simulates: to predict the movement of sediment, nutrients, pesticides or salts, the model first has to reproduce the movement of water. SWAT+ splits the hydrology of a watershed into two parts. The land phase, covered here and in the pages that follow, controls how much water, sediment and chemical load each hydrologic response unit (HRU) delivers. The routing phase moves those loads through channels, aquifers, reservoirs and wetlands to the outlet.

Each HRU is computed once per day (or per sub-daily time step for runoff when Green-Ampt infiltration is used). The HRU keeps track of four water stores: the plant canopy, the snowpack, the soil profile and, where one is defined, a ponded surface such as a wetland or rice paddy. Water that leaves the soil profile at the bottom becomes recharge to an aquifer object or to the gwflow module.

## Soil water balance

The land-phase balance for the soil profile of an HRU over a period of $t$ days is

$$SW_t = SW_0 + \sum_{i=1}^{t}\left(R_{day} + I - Q_{surf} - E_a - w_{perc} - Q_{lat} - Q_{tile}\right)$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $SW_t$ | Soil water content at the end of day $t$ | mm H2O |
| $SW_0$ | Soil water content at the start of the period | mm H2O |
| $R_{day}$ | Rain and snowmelt reaching the soil surface, after canopy interception and snowfall | mm H2O |
| $I$ | Irrigation and run-on from upslope objects | mm H2O |
| $Q_{surf}$ | Surface runoff generated on the day | mm H2O |
| $E_a$ | Evaporation from the soil and transpiration by plants | mm H2O |
| $w_{perc}$ | Percolation from the bottom of the soil profile | mm H2O |
| $Q_{lat}$ | Lateral subsurface flow leaving the soil layers | mm H2O |
| $Q_{tile}$ | Tile drain flow | mm H2O |

All terms are depths over the HRU area. Water in the canopy and in the snowpack is stored outside the soil profile: precipitation first fills canopy storage, then falls as snow on cold days, and only the remainder (plus snowmelt) is available for runoff and infiltration. Total evapotranspiration reported for the HRU is the sum of canopy evaporation, plant transpiration and soil evaporation, with snow sublimation and evaporation from ponded water counted in soil evaporation.

Surface runoff, lateral flow and tile flow do not all reach the channel on the day they are generated. Each passes through a lag store (see [Hydrology](hydrology.md)), so the HRU water yield on a day is

$$Q_{yld} = Q_{surf,lag} + Q_{lat,lag} + Q_{tile,lag}$$

where the subscript $lag$ marks the part of each store released that day.

## Daily order of calculations

The order matters because each process sees the state left by the processes before it. For each HRU on each day SWAT+ 62.0.1 runs:

1. Elevation lapse corrections to precipitation and temperature, when `lapse` is on in [`codes.bsn`](../input-reference/codes-bsn.md).
2. Decision table operations and water allocation demands for the HRU.
3. Base-zero heat unit accumulation, albedo, salt and constituent soil chemistry.
4. Soil temperature for every layer.
5. Canopy interception.
6. Snowfall, snowpack temperature and snowmelt.
7. Run-on from upslope objects: surface runoff, lateral flow, tile flow and aquifer flow routed onto the HRU.
8. Soil crack volume, when `crack` is on in [`codes.bsn`](../input-reference/codes-bsn.md).
9. Potential evapotranspiration, canopy evaporation and soil evaporation.
10. Scheduled management operations from the HRU's management schedule.
11. Surface runoff, peak runoff rate and erosion. HRUs with a ponded surface (wetland or paddy) produce no surface runoff or erosion here; their water is handled in the next step.
12. Wetland and paddy water balance.
13. Infiltration and soil water routing: percolation, lateral flow, tile flow and saturation excess.
14. Grazing, residue decomposition, mineralisation, nitrification and volatilisation, and mineral phosphorus transformations.
15. Plant growth, including plant water and nutrient uptake (transpiration).
16. Pesticide wash-off, uptake, decay and leaching; nutrient and pesticide losses with runoff and sediment; atmospheric deposition; nitrate and soluble phosphorus movement.
17. Urban build-up and wash-off, sediment in lateral flow, and the surface lag store for sediment and chemicals.
18. Lag of lateral and tile flow, filter strips, grassed waterways and user-defined BMPs.
19. Lag of surface runoff.
20. Water yield and routing of the HRU's outflow to the objects it is connected to.

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `pet` | [`codes.bsn`](../input-reference/codes-bsn.md) | Potential evapotranspiration method. See [Climate and weather](climate-weather.md). |
| `gampt` | [`codes.bsn`](../input-reference/codes-bsn.md) | Curve number (`0`) or Green-Ampt (`1`) infiltration. See [Hydrology](hydrology.md). |
| `lapse` | [`codes.bsn`](../input-reference/codes-bsn.md) | Elevation lapse of precipitation and temperature. |
| `crack` | [`codes.bsn`](../input-reference/codes-bsn.md) | Bypass flow through soil cracks. |
| `surq_lag` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Surface runoff lag coefficient. |
| `sw_init` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Initial soil water as a fraction of field capacity. See [Soil water and temperature](soil-water-temperature.md). |
| `can_max`, `esco`, `epco`, `lat_ttime`, `perco`, `cn3_swf`, `latq_co`, `pet_co` | [`hydrology.hyd`](../input-reference/hyd.md) | HRU-level hydrology parameters, described on the pages for each process. |

## Output

The terms of the HRU balance are written to the water balance files at HRU, landscape unit and basin level (`hru_wb_*`, `lsunit_wb_*`, `basin_wb_*`). `precip`, `snofall` and `snomlt` give the inputs; `surq_gen`, `latq`, `qtile`, `perc`, `et`, `eplant`, `esoil` and `ecanopy` the losses; `sw_init`, `sw_final` and `snopack` the stores; and `lagsurf` and `laglatq` the water still in the lag stores. See [Water balance output](../output-reference/water-balance.md).

## Related pages

- [Climate and weather](climate-weather.md) for precipitation, temperature and potential evapotranspiration.
- [Hydrology](hydrology.md) for interception, runoff, lateral flow, percolation and tile flow.
- [Soil water and temperature](soil-water-temperature.md) for the soil profile and soil evaporation.
- [Aquifers](aquifers.md) for the fate of percolation below the soil profile.
- [Reservoirs and wetlands](reservoirs-wetlands.md) for ponded HRUs.

??? quote "Sources"

    - Daily HRU sequence: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Evapotranspiration totals: [`et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90)
    - Soil water routing: [`swr_percmain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmain.f90)
    - Lateral and tile lag: [`swr_substor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_substor.f90); surface runoff lag: [`sq_surfst.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_surfst.f90)
    - Water balance output type: `type output_waterbal` in [`output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_module.f90)

    | Symbol or output | Fortran variable |
    |------------------|------------------|
    | $SW$ | `soil(j)%sw` |
    | $R_{day}$ (before infiltration) | `precip_eff` |
    | Infiltration into layer 1 | `inflpcp` |
    | $Q_{surf}$ (generated, lagged) | `surfq(j)`, `qday` |
    | $Q_{lat}$ | `latq(j)` |
    | $Q_{tile}$ | `qtile` |
    | $w_{perc}$ | `sepbtm(j)` |
    | Canopy evaporation, transpiration, soil evaporation | `canev`, `ep_day`, `es_day` |
    | Total ET (`et` output) | `etday = ep_day + es_day + canev` |
    | Water yield | `qdr(j) = qday + latq(j) + qtile` |
    | Lag stores (`lagsurf`, `laglatq`, `lagsatex`) | `surf_bs(1,j)`, `bss(1,j)`, `bss_ex(1,j)` |

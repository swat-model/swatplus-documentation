---
title: Hydrology
description: Canopy interception, surface runoff, percolation, lateral flow, tile drainage and the lag of flow to the channel in SWAT+ HRUs.
status: review
verified_against:
  - src/hru_control.f90
  - src/surface.f90
  - src/sq_canopyint.f90
  - src/sq_volq.f90
  - src/sq_daycn.f90
  - src/sq_dailycn.f90
  - src/curno.f90
  - src/cn2_init.f90
  - src/sq_greenampt.f90
  - src/soils_init.f90
  - src/sq_crackvol.f90
  - src/sq_crackflow.f90
  - src/swr_percmacro.f90
  - src/sq_surfst.f90
  - src/time_conc_init.f90
  - src/swr_percmain.f90
  - src/swr_percmicro.f90
  - src/swr_satexcess.f90
  - src/swr_origtile.f90
  - src/swr_drains.f90
  - src/swr_substor.f90
  - src/topohyd_init.f90
  - src/hydro_init.f90
  - src/basin_prm_default.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Precipitation reaching an HRU may be caught by the plant canopy or fall on the soil surface. Water on the surface infiltrates into the soil profile or runs off. Runoff moves quickly towards a channel and gives the short-term response of a stream. Infiltrated water is stored in the soil and later evaporated or transpired, or it moves slowly through the profile: laterally towards the channel, into tile drains, or down past the bottom of the profile to recharge groundwater.

Evaporation from the soil is described in [Soil water and temperature](soil-water-temperature.md). What happens to the water once it reaches a channel is on the [Channels](channels.md) page.

## Canopy interception

The plant canopy intercepts part of the rain, and the amount stored depends on how much canopy there is. The storage capacity on a day is

$$can_{day} = can_{mx}\,\frac{LAI}{LAI_{mx}}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $can_{day}$ | Maximum canopy storage on the day | mm H2O |
| $can_{mx}$ | Maximum canopy storage when the canopy is fully developed, `can_max` in [`hydrology.hyd`](../input-reference/hyd.md) | mm H2O |
| $LAI$ | Leaf area index of the plant community on the day | m²/m² |
| $LAI_{mx}$ | Maximum leaf area index of the plant community | m²/m² |

Precipitation first fills the empty part of the canopy store, and only the rest reaches the ground. In sub-daily runs the store is filled from the first time steps of the day. Water stored in the canopy is the first water evaporated (see [Soil water and temperature](soil-water-temperature.md)). Interception applies with both the curve number and the Green-Ampt method. HRUs with no leaf area have no interception.

## Surface runoff

Surface runoff, or overland flow, occurs when water reaches the ground faster than it can infiltrate. SWAT+ has two methods, chosen with `gampt` in [`codes.bsn`](../input-reference/codes-bsn.md): the SCS curve number method (`0`) and the Green and Ampt infiltration method (`1`). Runoff is computed only on days when more than 0.1 mm of water reaches the surface. Runoff from irrigation is added to it afterwards.

### SCS curve number

The SCS runoff equation (SCS, 1972) is an empirical model that came into common use in the 1950s, built from more than 20 years of rainfall and runoff studies on small rural watersheds across the U.S.:

$$Q_{surf} = \frac{(R_{day} - I_a)^2}{R_{day} - I_a + S} \quad\text{for } R_{day} > I_a, \qquad Q_{surf} = 0 \text{ otherwise}$$

with the initial abstraction $I_a = 0.2\,S$, so that

$$Q_{surf} = \frac{(R_{day} - 0.2\,S)^2}{R_{day} + 0.8\,S}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $Q_{surf}$ | Accumulated runoff or rainfall excess | mm H2O |
| $R_{day}$ | Rain and snowmelt reaching the surface on the day, after interception | mm H2O |
| $I_a$ | Initial abstraction: surface storage, interception and infiltration before runoff | mm H2O |
| $S$ | Retention parameter for the day | mm H2O |

The retention parameter is linked to the curve number for the day, $CN$:

$$S = 25.4\left(\frac{1000}{CN} - 10\right)$$

**Curve number for average conditions.** Each HRU takes its moisture condition II curve number, $CN_2$, from the row of [`cntable.lum`](../input-reference/lum-tables.md) named in the `cn2` column of its [`landuse.lum`](../input-reference/lum.md) row, using the column for the soil's hydrologic group (`cn_a` to `cn_d`, from `hyd_grp` in [`soils.sol`](../input-reference/sol.md)). SWAT+ 62.0.1 does not adjust $CN_2$ for slope. The curve number for dry conditions (wilting point) and for wet conditions are

$$CN_1 = CN_2 - \frac{20\,(100 - CN_2)}{100 - CN_2 + \exp\left[2.533 - 0.0636\,(100 - CN_2)\right]}, \qquad CN_1 \ge 0.4\,CN_2$$

$$CN_3 = CN_2\,\exp\left[0.006729\,(100 - CN_2)\right]$$

**Daily curve number from soil water.** The retention parameter varies with the water content of the soil profile:

$$S = S_{max}\left(1 - \frac{SW}{SW + \exp(w_1 - w_2\,SW)}\right), \qquad S \ge 3 \text{ mm}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $S_{max}$ | Retention parameter for $CN_1$ | mm H2O |
| $SW$ | Soil water content of the whole profile, excluding water below wilting point | mm H2O |
| $w_1$, $w_2$ | Shape coefficients | - |

The shape coefficients are fixed at the start of the run so that $S$ equals $S_{max}$ for a dry profile, equals the $CN_3$ retention parameter when the profile water content is $SW_3$, and equals 2.54 mm (a curve number of 99) when the profile is saturated:

$$SW_3 = FC + \mathrm{cn3\_swf}\,(SAT - FC)$$

where $FC$ and $SAT$ are the profile water contents at field capacity and saturation, and `cn3_swf` is the column in [`hydrology.hyd`](../input-reference/hyd.md). With `cn3_swf = 0` the wet condition is reached at field capacity; values towards 1 move it towards saturation and reduce runoff from wet soils. For HRUs with a tile drain SWAT+ sets `cn3_swf` to 0.95.

SWAT 2009 offered a second method that ties the curve number to accumulated plant evapotranspiration. SWAT+ 62.0.1 has only the soil water method.

**Frozen soil.** When the second soil layer is at or below 0 °C, infiltration is reduced:

$$S_{frz} = S_{max}\left[1 - \exp(-\mathrm{cn\_froz}\;S)\right]$$

where `cn_froz` is the frozen soil parameter in [`parameters.bsn`](../input-reference/parameters-bsn.md).

**Urban areas.** For an HRU with an urban land use, runoff from the directly connected impervious fraction (`frac_dc_imp` in [`urban.urb`](../input-reference/str.md#urbanurb)) is computed with a curve number of 98 and mixed with the runoff from the rest of the HRU by area. The `urb_cn` column of [`urban.urb`](../input-reference/str.md#urbanurb) is read but not used.

### Green and Ampt infiltration

The Green and Ampt method (Green and Ampt, 1911) needs precipitation at a sub-daily time step, set in [`time.sim`](../input-reference/time-sim.md) and supplied in the precipitation files. It assumes a sharp wetting front that separates saturated soil above from soil at its initial water content below. SWAT+ uses the Mein and Larson (1973) form with the modification of Kim et al., where the infiltration rate at the end of a time step is

$$f_{inf} = K_e\left(1 + \frac{\Psi_{wf}\,\Delta\theta_v}{F_{inf}}\right)$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $f_{inf}$ | Infiltration rate | mm/hr |
| $K_e$ | Effective hydraulic conductivity | mm/hr |
| $\Psi_{wf}$ | Wetting front matric potential | mm |
| $\Delta\theta_v$ | Change in volumetric water content across the wetting front | mm/mm |
| $F_{inf}$ | Cumulative infiltration since the start of the day | mm H2O |

Within each time step, while the rainfall intensity is below the infiltration rate all rain infiltrates. Otherwise the cumulative infiltration at the end of the step is solved by iteration from

$$F_{inf,t} = F_{inf,t-1} + K_e\,\Delta t + \Psi_{wf}\,\Delta\theta_v\,\ln\!\left(\frac{F_{inf,t} + \Psi_{wf}\,\Delta\theta_v}{F_{inf,t-1} + \Psi_{wf}\,\Delta\theta_v}\right)$$

and the rain that does not infiltrate becomes runoff for that step.

The effective conductivity is estimated from the saturated conductivity of the top soil layer, $K_{sat}$, and the curve number (Nearing et al., 1996):

$$K_e = \frac{56.82\,K_{sat}^{0.286}}{1 + 0.051\,\exp(0.062\,CN)} - 2, \qquad K_e \ge 0.001$$

The curve number used here is updated every time step from the soil water plus the water infiltrated so far, with the same relationship as the curve number method. The moisture deficit is

$$\Delta\theta_v = 0.95\,\phi_{soil}\left(1 - \frac{SW}{FC}\right)$$

where $\phi_{soil}$ is the porosity of the top layer and $SW/FC$ is limited to 0.999. If more than 12 mm of rain fell on the previous day, the soil is assumed to be nearly saturated at the start of the day and the previous day's final infiltration rate is used as the starting rate. $\Psi_{wf}$ is estimated once for each HRU from the porosity and the sand and clay content of the top layer (Rawls and Brakensiek, 1985).

On urban HRUs the directly connected impervious fraction produces runoff from the rain left after an initial abstraction store. The store is depleted by rain and recovers on dry time steps up to `urb_init_abst` in [`parameters.bsn`](../input-reference/parameters-bsn.md).

### Crack flow

When `crack` is 1 in [`codes.bsn`](../input-reference/codes-bsn.md), SWAT+ computes a crack volume for each layer from the soil's `perc_crk` value in [`soils.sol`](../input-reference/sol.md) and its current water deficit. Cracks develop slowly as the soil dries and close as it wets. Runoff up to the total crack volume is moved into the cracks, where it fills layers below field capacity from the bottom of the profile upward, and any remainder percolates from the bottom of the profile.

## Surface runoff lag

In large HRUs, or HRUs with a long time of concentration, only part of the runoff generated on a day reaches the channel that day. SWAT+ keeps a surface runoff store and releases a fixed fraction of it each day:

$$Q_{surf,lag} = \left(Q'_{surf} + Q_{stor,i-1}\right)\left[1 - \exp\left(\frac{-\mathrm{surq\_lag}}{t_{conc}}\right)\right]$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $Q_{surf,lag}$ | Surface runoff released to the channel on the day | mm H2O |
| $Q'_{surf}$ | Surface runoff generated on the day | mm H2O |
| $Q_{stor,i-1}$ | Runoff stored or lagged from the previous day | mm H2O |
| $\mathrm{surq\_lag}$ | Surface runoff lag coefficient, `surq_lag` in [`parameters.bsn`](../input-reference/parameters-bsn.md) | - |
| $t_{conc}$ | Time of concentration of the HRU | hr |

For a given time of concentration, a smaller `surq_lag` keeps more water in storage. In sub-daily runs the time of concentration is expressed in time steps, and the same fraction is released every step. Sediment, nutrients and other constituents in surface runoff are lagged in the same way.

The time of concentration is the sum of the overland flow time and a channel flow time within the HRU:

$$t_{ov} = \frac{0.0556\,(L_{slp}\,n)^{0.6}}{slp^{0.3}}, \qquad t_{ch} = \frac{0.31\,L\,n^{0.75}}{A^{0.125}\,(0.5\,slp + 0.001)^{0.375}}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $L_{slp}$ | Slope length, `slp_len` in [`topography.hyd`](../input-reference/hyd.md) | m |
| $slp$ | Average slope, `slp` in [`topography.hyd`](../input-reference/hyd.md#topographyhyd) | m/m |
| $n$ | Manning's n for overland flow, from the `ov_mann` column of [`landuse.lum`](../input-reference/lum.md) | - |
| $L$ | Flow length, taken as $0.5\sqrt{\text{HRU area in ha}/2}$ | km |
| $A$ | HRU area | km² |

## Soil water routing

Water that infiltrates enters the top soil layer and is routed down the profile layer by layer. A layer can lose water by percolation to the layer below and by lateral flow, but only the water stored above field capacity can move.

### Percolation

Percolation from a layer is computed with a storage routing method:

$$w_{perc} = SW_{ex}\left[1 - \exp\left(\frac{-24}{TT_{perc}}\right)\right], \qquad TT_{perc} = \frac{SAT - FC}{K_{sat}}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $w_{perc}$ | Water percolating to the next layer on the day | mm H2O |
| $SW_{ex}$ | Water in the layer above field capacity | mm H2O |
| $TT_{perc}$ | Travel time for percolation, at least 2 hours | hr |
| $SAT$, $FC$ | Water content of the layer at saturation and at field capacity | mm H2O |
| $K_{sat}$ | Saturated hydraulic conductivity of the layer, `soil_k` in [`soils.sol`](../input-reference/sol.md) | mm/hr |

No water percolates or flows laterally from a layer whose temperature is at or below 0 °C. Percolation from the bottom layer leaves the soil profile as recharge, and is multiplied by a factor derived from `perco` in [`hydrology.hyd`](../input-reference/hyd.md):

$$f_{perco} = \min\left(1,\; \exp\left[-\left(1.0052\,\ln(-\ln \mathrm{perco}) + 5.6862\right)\right]\right)$$

`perco` close to 1 gives a factor of 1, so the bottom layer drains freely. Smaller values keep water in the profile, and `perco = 0` stops deep percolation. For HRUs with a tile drain, SWAT+ sets `perco` to 0.1. Above the bottom layer, percolation is not restricted.

### Lateral flow

Lateral subsurface flow is computed with a kinematic storage model (Sloan et al., 1983), applied to every layer below the top one:

$$Q_{lat} = \mathrm{latq\_co}\times 0.024\,\frac{2\,SW_{ex}\,K_{sat}\,slp}{\phi_d\,L_{hill}}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $Q_{lat}$ | Lateral flow from the layer | mm H2O/day |
| $\mathrm{latq\_co}$ | Lateral flow coefficient, `latq_co` in [`hydrology.hyd`](../input-reference/hyd.md) | - |
| $\phi_d$ | Drainable porosity of the layer, $(SAT - FC)$ divided by layer thickness | mm/mm |
| $slp$ | Average slope of the HRU | m/m |
| $L_{hill}$ | Slope length for lateral flow, `lat_len` in [`topography.hyd`](../input-reference/hyd.md#topographyhyd); 50 m when blank or zero | m |

If percolation and lateral flow together exceed the water above field capacity, both are reduced in proportion. The top soil layer, which is the 10 mm surface layer for most soils (see [Soil water and temperature](soil-water-temperature.md)), produces no lateral flow in SWAT+.

### Saturation excess

After percolation, any layer with more water than it can at saturation passes the excess to the layer above. Excess in the top layer is pushed down to the next layer with room, and what cannot be stored becomes surface runoff (or, on HRUs with a ponded surface, flows into the wetland or over its weir).

### Tile drainage

Tile drains take water from the soil when a perched water table rises above the drain. Tile flow is computed for HRUs with a tile drain (`tile` in [`landuse.lum`](../input-reference/lum.md), pointing to a row of [`tiledrain.str`](../input-reference/str.md)) when the second soil layer is above freezing. The method is set by `tiledrain` in [`codes.bsn`](../input-reference/codes-bsn.md): `0` uses the drawdown equation below, `1` the DRAINMOD equations.

With `wtable = 0` in [`codes.bsn`](../input-reference/codes-bsn.md), the height of the water table above the bottom of the profile is estimated from the water stored above field capacity:

$$h_{wtbl} = \frac{SW - FC}{SAT_{90} - FC}\,depth_{prof}, \qquad SAT_{90} = \max(0.9\,SAT,\; 1.1\,FC)$$

where $SW$, $FC$ and $SAT$ are profile totals and $depth_{prof}$ is the profile depth. When the water table is above the drain, the drawdown method gives

$$Q_{tile} = \frac{h_{wtbl} - h_{drain}}{h_{wtbl}}\,(SW - FC)\left[1 - \exp\left(\frac{-24}{t_{drain}}\right)\right]$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $Q_{tile}$ | Tile flow on the day, at most `drain` in [`tiledrain.str`](../input-reference/str.md#tiledrainstr) | mm H2O |
| $h_{drain}$ | Height of the drain above the bottom of the profile, profile depth minus `dp` | mm |
| $t_{drain}$ | Time to drain the soil to field capacity, `t_fc` in [`tiledrain.str`](../input-reference/str.md#tiledrainstr); all excess drains in one day when it is under 1 hour | hr |

Tile flow is taken from the layers with water above field capacity, starting at the top.

### Lag of lateral and tile flow

In large HRUs with a mild slope, lateral and tile flow can take more than a day to reach the channel. Both pass through a store, and the part released on a day is

$$Q_{lat,lag} = \left(Q'_{lat} + Q_{latstor,i-1}\right)\left[1 - \exp\left(\frac{-1}{TT_{lag}}\right)\right]$$

$TT_{lag}$ is `lat_ttime` in [`hydrology.hyd`](../input-reference/hyd.md), in days. When `lat_ttime` is zero, SWAT+ estimates it from the slope length for lateral flow and the highest conductivity in the profile, $TT_{lag} = 10.4\,L_{hill}/K_{sat,mx}$ (at least one day). Tile flow uses $1 - \exp(-24/lag)$, with `lag` in hours from [`tiledrain.str`](../input-reference/str.md#tiledrainstr). Nitrate in lateral and tile flow is lagged with the water.

## Channel routing

Water yield from the HRUs enters channels, where it is routed downstream by the variable storage method or the Muskingum method, chosen with `rte_cha` in [`codes.bsn`](../input-reference/codes-bsn.md). See [Channels](channels.md).

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `gampt` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` curve number, `1` Green-Ampt |
| `crack` | [`codes.bsn`](../input-reference/codes-bsn.md) | `1` computes crack flow |
| `tiledrain` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` drawdown tile equation, `1` DRAINMOD |
| `wtable` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` water table from profile water, `1` DRAINMOD water table |
| `surq_lag` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Surface runoff lag coefficient |
| `cn_froz` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Frozen soil infiltration factor |
| `urb_init_abst` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Maximum initial abstraction on impervious urban area, Green-Ampt only |
| `can_max`, `cn3_swf`, `perco`, `latq_co`, `lat_ttime` | [`hydrology.hyd`](../input-reference/hyd.md) | Canopy storage, wet-condition curve number, deep percolation, lateral flow, lateral flow lag |
| `slp`, `slp_len`, `lat_len` | [`topography.hyd`](../input-reference/hyd.md) | Slope, slope length, slope length for lateral flow |
| `cn2`, `ov_mann`, `tile` | [`landuse.lum`](../input-reference/lum.md) | Curve number table row, overland Manning's n, tile drain |
| `dp`, `t_fc`, `lag`, `drain` | [`tiledrain.str`](../input-reference/str.md) | Drain depth, drainage time, tile lag, drainage coefficient |
| `soil_k`, `awc`, `bd`, `perc_crk` | [`soils.sol`](../input-reference/sol.md) | Layer conductivity and water retention, crack volume |

## Related pages

- [Overview and water balance](overview-water-balance.md) for the order of these calculations within the day.
- [Soil water and temperature](soil-water-temperature.md) for soil layers and soil evaporation.
- [Erosion and sediment](erosion-sediment.md) for the peak runoff rate and soil loss.
- [Aquifers](aquifers.md) for recharge below the soil profile.
- [Channels](channels.md) for channel routing.
- [Water balance output](../output-reference/water-balance.md).

??? quote "Sources"

    - Daily sequence: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`surface.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/surface.f90)
    - Interception: [`sq_canopyint.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_canopyint.f90)
    - Curve number: [`sq_volq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_volq.f90), [`sq_daycn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_daycn.f90), [`sq_dailycn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_dailycn.f90), [`curno.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/curno.f90), [`cn2_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cn2_init.f90)
    - Green-Ampt: [`sq_greenampt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_greenampt.f90); wetting front suction in [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90)
    - Cracks: [`sq_crackvol.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_crackvol.f90), [`sq_crackflow.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_crackflow.f90), [`swr_percmacro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmacro.f90)
    - Runoff lag and time of concentration: [`sq_surfst.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_surfst.f90), [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90)
    - Soil water routing: [`swr_percmain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmain.f90), [`swr_percmicro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmicro.f90), [`swr_satexcess.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_satexcess.f90)
    - Tile drainage: [`swr_origtile.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_origtile.f90), [`swr_drains.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_drains.f90)
    - Subsurface lag: [`swr_substor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_substor.f90); lag factors in [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90)
    - HRU hydrology parameters: [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90)

    | Symbol or column | Fortran variable |
    |------------------|------------------|
    | `gampt`, `crack`, `tiledrain`, `wtable` (codes.bsn) | `bsn_cc%gampt`, `bsn_cc%crk`, `bsn_cc%tdrn`, `bsn_cc%wtdn` |
    | `surq_lag`, `cn_froz`, `urb_init_abst` | `bsn_prm%surlag`, `bsn_prm%cn_froz`, `bsn_prm%urb_init_abst` |
    | `can_max` | `hru(j)%hyd%canmx` |
    | `cn3_swf`, `perco`, `latq_co`, `lat_ttime` | `hru(j)%hyd%cn3_swf`, `hru(j)%hyd%perco`, `hru(j)%hyd%latq_co`, `hru(j)%hyd%lat_ttime` |
    | $f_{perco}$ | `hru(j)%hyd%perco_lim` |
    | `slp`, `slp_len`, `lat_len` | `hru(j)%topo%slope`, `hru(j)%topo%slope_len`, `hru(j)%topo%lat_len` |
    | `ov_mann` | `hru(j)%luse%ovn` |
    | `dp`, `t_fc`, `lag`, `drain` | `sdr%depth`, `sdr%time`, `sdr%lag`, `sdr%drain_co` |
    | $CN$, $S_{max}$, $w_1$, $w_2$ | `cnday(j)`, `smx(j)`, `wrt(1,j)`, `wrt(2,j)` |
    | $\Psi_{wf}$ | `wfsh(j)` |
    | $t_{conc}$, lag fraction | `tconc(j)`, `brt(j)` |
    | $SW_{ex}$, $w_{perc}$, $Q_{lat}$ (layer) | `sw_excess`, `sepday`, `latlyr` |
    | $TT_{perc}$ | `soil(j)%phys(ly)%hk` |
    | $h_{wtbl}$ | `wt_shall` |
    | Lag stores | `surf_bs(1,j)`, `bss(1,j)` (lateral), `bss(3,j)` (tile) |

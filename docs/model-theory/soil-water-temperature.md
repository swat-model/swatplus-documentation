---
title: Soil Water and Temperature
description: Soil layers, water retention, initial soil water, actual evapotranspiration and daily soil temperature in SWAT+.
status: review
verified_against:
  - src/soils_init.f90
  - src/soil_phys_init.f90
  - src/soil_db_read.f90
  - src/hydro_init.f90
  - src/et_act.f90
  - src/sq_canopyint.f90
  - src/stmp_solt.f90
  - src/hru_control.f90
  - src/reservoir_data_module.f90
  - src/basin_prm_default.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

The soil profile is the main water store of an HRU. Water that infiltrates is stored in the soil layers, taken up by plants, evaporated from the soil surface, or moved down and sideways as described in [Hydrology](hydrology.md).

## Soil layers

Each HRU uses one soil from [`soils.sol`](../input-reference/sol.md). The soil can have any number of layers, each defined by the depth to its bottom (`dp`) and its physical properties.

If the first layer of the soil is deeper than 19.5 mm, SWAT+ adds a 10 mm surface layer with the properties of the first layer, so most HRUs have one more layer than the soil in [`soils.sol`](../input-reference/sol.md). The thin surface layer is used for soil evaporation, surface nutrient processes and erosion. When a file named [`soil_lyr_depths.sol`](../input-reference/sol.md#soil_lyr_depthssol) is present in the project folder, SWAT+ instead rebuilds the layers of every soil at the depths listed in it, with a 10 mm surface layer on top. HRUs with an active septic system get extra layer boundaries at the top and bottom of the septic biozone.

Missing or out-of-range layer properties are replaced when the soil is read:

| Property | Replacement |
|----------|-------------|
| Bulk density `bd` | 1.3 Mg/m³ when zero; at most 2.0 Mg/m³ |
| Available water capacity `awc` | 0.005 mm/mm when zero; at most 0.8 mm/mm |
| Saturated conductivity `soil_k` | When zero: 50, 20, 5 or 2 mm/hr for hydrologic group (`hyd_grp`) A, B, C or D, 10 mm/hr otherwise |
| Rock fragments `rock` | at most 98% |
| Soil albedo `alb` | at least 0.1 |
| Calcium carbonate `caco3` and `ph` | 2.8% and 6.5 when zero |
| Anion exclusion `anion_excl` | 0.5 when zero; at most 0.99 |

### Water retention

SWAT+ stores soil water as the depth of water above the wilting point. The volumetric water contents of each layer are

$$\theta_{wp} = 0.40\,\frac{m_c\,\rho_b}{100}, \qquad \theta_{fc} = \theta_{wp} + AWC, \qquad \phi = 1 - \frac{\rho_b}{2.65}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $\theta_{wp}$ | Water content at wilting point (−1.5 MPa) | mm/mm |
| $\theta_{fc}$ | Water content at field capacity (−0.033 MPa) | mm/mm |
| $\phi$ | Porosity | mm/mm |
| $m_c$ | Clay content, `clay` in [`soils.sol`](../input-reference/sol.md) | % |
| $\rho_b$ | Moist bulk density, `bd` in [`soils.sol`](../input-reference/sol.md) | Mg/m³ |
| $AWC$ | Available water capacity, `awc` in [`soils.sol`](../input-reference/sol.md) | mm/mm |

If field capacity reaches the porosity, it is set to $\phi - 0.05$ and the wilting point is moved down with it. The water a layer can store above wilting point is then

$$FC_{ly} = (\theta_{fc} - \theta_{wp})\,depth_{ly}, \qquad SAT_{ly} = (\phi - \theta_{wp})\,depth_{ly}$$

where $depth_{ly}$ is the layer thickness in mm. $FC_{ly}$ is the water that plants can use, and the difference $SAT_{ly} - FC_{ly}$ is the drainable water that can percolate or flow laterally.

### Initial soil water

Each layer starts the run with the same fraction of its field capacity water. The fraction is `sw_init` in [`parameters.bsn`](../input-reference/parameters-bsn.md). When `sw_init` is zero, SWAT+ estimates it from the average annual precipitation of the HRU's weather generator station:

$$f_{init} = \frac{P_{an}}{P_{an} + \exp(9.043 - 0.002135\,P_{an})}$$

with $P_{an}$ in mm. Dry climates start near zero and wet climates near field capacity. The water content then adjusts during the warm-up years skipped in [`print.prt`](../input-reference/print-prt.md).

## Actual evapotranspiration

Evapotranspiration covers every process that turns liquid or solid water at or near the land surface into water vapour: evaporation from the canopy, transpiration, sublimation and evaporation from the soil and from ponded water. SWAT+ starts from the HRU's potential evapotranspiration (PET, see [Climate and weather](climate-weather.md)) and removes water in this order.

### Canopy evaporation

Water stored on the canopy (see [Hydrology](hydrology.md)) evaporates first. If PET is smaller than the canopy store, the canopy loses PET and there is no transpiration or soil evaporation that day. Otherwise the canopy is emptied and the remaining demand is $E'_0 = PET - E_{can}$.

### Transpiration and soil evaporation demand

The maximum transpiration on the day depends on the leaf area of the plant community:

$$E_t = \frac{E'_0\,LAI}{3} \quad\text{for } LAI \le 3, \qquad E_t = E'_0 \quad\text{for } LAI > 3$$

The soil evaporation demand is reduced by shading from plants and residue:

$$E_s = E'_0\,cov_{sol}, \qquad cov_{sol} = \exp(-5.0\times10^{-5}\,CV)$$

where $CV$ is the above-ground biomass plus surface residue (kg/ha). When the snowpack contains 0.5 mm of water or more, $cov_{sol}$ is 0.5. If $E_t + E_s$ is larger than the demand, $E_s$ is reduced so that the two together do not exceed it. The transpiration demand is met by plant water uptake (see [Plant growth and land use management](plant-growth-lum.md)).

The same leaf area rule sets the transpiration demand for all three PET methods. SWAT+ 62.0.1 does not use the crop transpiration computed by the Penman-Monteith method.

### Sublimation and ponded water

On days with a mean air temperature above 0 °C, the soil evaporation demand is taken first from the snowpack as sublimation. On HRUs with ponded water (wetlands and paddies), the evaporation demand is

$$E_s = \mathrm{evap}\left(1 - \frac{LAI}{4}\right)E'_0 \quad\text{for } LAI \le 4, \qquad E_s = 0 \text{ otherwise}$$

where `evap` is the evaporation coefficient in [`hydrology.wet`](../input-reference/wet.md#hydrologywet). It is taken from the ponded water, and the soil itself does not evaporate while ponded water remains.

### Soil evaporation by layer

The remaining demand is distributed with depth. The demand down to depth $z$ is

$$E_{soil,z} = E''_s\,\frac{z}{z + \exp(2.374 - 0.00713\,z)}$$

where $E''_s$ is the remaining demand and $z$ is in mm. Half of the demand comes from the top 10 mm and 95% from the top 100 mm. The demand on a layer with its top at $z_u$ and bottom at $z_l$ is

$$E_{soil,ly} = E_{soil,z_l} - E_{soil,z_u}\,(1 - \mathrm{esco})$$

| Symbol | Meaning | Input |
|--------|---------|-------|
| $\mathrm{esco}$ | Soil evaporation compensation factor | `esco` in [`hydrology.hyd`](../input-reference/hyd.md), 0 to 1 |

With `esco = 0` each layer meets only its share of the demand. As `esco` increases, deeper layers can make up for demand that the layers above could not meet, so more water can be evaporated from lower in the profile. This direction is the opposite of SWAT 2009, where lowering `esco` allowed more compensation.

When a layer is drier than field capacity its demand is reduced:

$$E'_{soil,ly} = E_{soil,ly}\,\exp\left(\frac{2.5\,(SW_{ly} - FC_{ly})}{FC_{ly}}\right)$$

and a layer never gives up more than 80% of its plant-available water on one day. Only layers whose top is shallower than 500 mm evaporate. As water evaporates from the second layer, a small amount of nitrate moves up with it into the surface layer.

## Soil temperature

Soil temperature affects water movement and the rate of residue decomposition and nutrient transformations. SWAT+ computes the temperature at the centre of each layer every day from the soil surface temperature, the annual average air temperature and a damping depth.

### Damping depth

The maximum damping depth depends on the average bulk density of the profile, $\rho_b$:

$$dd_{max} = 1000 + \frac{2500\,\rho_b}{\rho_b + 686\,\exp(-5.63\,\rho_b)}$$

The damping depth on a day is scaled by the soil water content:

$$dd = dd_{max}\,\exp\left[\ln\left(\frac{500}{dd_{max}}\right)\left(\frac{1 - wc}{1 + wc}\right)^2\right], \qquad wc = \frac{SW}{(0.356 - 0.144\,\rho_b)\,z_{tot}}$$

where $SW$ is the profile water content (mm) and $z_{tot}$ the profile depth (mm).

### Surface temperature

The temperature of a bare soil surface is

$$T_{bare} = \bar{T} + \frac{T_{max} - T_{min}}{2}\cdot\frac{H_{day}(1 - \alpha) - 14}{20}$$

where $H_{day}$ is the solar radiation and $\alpha$ the albedo of the day. Biomass, residue and snow insulate the surface. The cover weighting factor is

$$bcv = \max\left(\frac{CV}{CV + \exp(7.563 - 1.297\times10^{-4}\,CV)},\; \frac{SNO}{SNO + \exp(6.055 - 0.3002\,SNO)}\right)$$

with $CV$ the above-ground biomass and residue (kg/ha) and $SNO$ the snow water content (mm); the snow term is 1 above 120 mm. The surface temperature is

$$T_{srf} = \frac{1}{2}\left[T_{bare} + bcv\,T_{ly2} + (1 - bcv)\,T_{bare}\right]$$

where $T_{ly2}$ is the previous day's temperature of the second soil layer.

### Layer temperature

$$T_{ly} = \ell\,T_{ly,prev} + (1 - \ell)\left[df\,(\bar{T}_{AA} - T_{srf}) + T_{srf}\right]$$

$$df = \frac{zd}{zd + \exp(-0.8669 - 2.0775\,zd)}, \qquad zd = \frac{z_{mid}}{dd}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $\ell$ | Lag coefficient, 0.8 | - |
| $T_{ly,prev}$ | Layer temperature on the previous day | °C |
| $\bar{T}_{AA}$ | Average annual air temperature of the weather generator station | °C |
| $z_{mid}$ | Depth to the centre of the layer | mm |

Layers start the run at the average December maximum temperature of the weather generator station. In septic HRUs, layers at and below the biozone are kept from falling far below 10 °C.

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `sw_init` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Initial soil water as a fraction of field capacity; zero estimates it from precipitation |
| `esco` | [`hydrology.hyd`](../input-reference/hyd.md) | Soil evaporation compensation |
| `epco` | [`hydrology.hyd`](../input-reference/hyd.md) | Plant uptake compensation (see [Plant growth](plant-growth-lum.md)) |
| `can_max` | [`hydrology.hyd`](../input-reference/hyd.md) | Maximum canopy storage |
| `evap` | [`hydrology.wet`](../input-reference/wet.md#hydrologywet) | Evaporation coefficient for ponded water |
| `dp`, `bd`, `awc`, `soil_k`, `clay`, `rock`, `alb` | [`soils.sol`](../input-reference/sol.md) | Layer depth, bulk density, water retention, conductivity, texture, albedo |
| `lai_noevap` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Read but not used: the leaf area index of 3.0 in the transpiration rule is fixed |

## Related pages

- [`soils.sol`](../input-reference/sol.md) for the soil input file.
- [Hydrology](hydrology.md) for infiltration, percolation and lateral flow.
- [Plant growth and land use management](plant-growth-lum.md) for transpiration and root water uptake.
- [Nutrient cycling](nutrient-cycling.md) for the effect of soil water and temperature on nutrient transformations.
- [Water balance output](../output-reference/water-balance.md) for `esoil`, `eplant`, `ecanopy` and soil water.

??? quote "Sources"

    - Soil database and layering: [`soil_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_db_read.f90), [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90)
    - Physical properties: [`soil_phys_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_phys_init.f90)
    - Initial soil water and temperature: [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90)
    - Actual evapotranspiration: [`et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90)
    - Soil temperature: [`stmp_solt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/stmp_solt.f90)
    - Wetland evaporation coefficient: `type wetland_hyd_data` in [`reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_data_module.f90)

    | Symbol or column | Fortran variable |
    |------------------|------------------|
    | `sw_init` | `bsn_prm%ffcb`; per soil `soil(j)%ffc` |
    | `lai_noevap` | `bsn_prm%evlai` |
    | `esco`, `epco` | `hru(j)%hyd%esco`, `hru(j)%hyd%epco` |
    | `evap` (hydrology.wet) | `wet_hyd(ihyd)%evrsv` |
    | $\theta_{wp}$, $\theta_{fc}$, $\phi$ | `soil(j)%phys(ly)%wp`, `%up`, `%por` |
    | $FC_{ly}$, $SAT_{ly}$, $SW_{ly}$ | `soil(j)%phys(ly)%fc`, `%ul`, `%st` |
    | Profile totals | `soil(j)%sumfc`, `soil(j)%sumul`, `soil(j)%sw` |
    | $E'_0$, $E_t$, $E_s$ | `pet`, `ep_max`, `es_max` |
    | $E_{can}$, soil evaporation, sublimation | `canev`, `es_day`, `snoev` |
    | $dd_{max}$, $dd$, $\rho_b$ | `dp`, `dd`, `soil(j)%avbd` |
    | $T_{srf}$, $T_{ly}$ | `soil(j)%tmp_srf`, `soil(j)%phys(ly)%tmp` |

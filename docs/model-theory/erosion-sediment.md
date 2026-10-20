---
title: Erosion and Sediment
description: Peak runoff rate, MUSLE soil loss, sub-daily erosion, sediment in lateral flow and the lag of sediment to the channel in SWAT+ HRUs.
status: review
verified_against:
  - src/surface.f90
  - src/ero_pkq.f90
  - src/ero_ysed.f90
  - src/ero_cfactor.f90
  - src/ero_eiusle.f90
  - src/ero_ovrsed.f90
  - src/swr_latsed.f90
  - src/stor_surfstor.f90
  - src/hydro_init.f90
  - src/plant_init.f90
  - src/soil_phys_init.f90
  - src/climate_control.f90
  - src/cli_initwgn.f90
  - src/basin_prm_default.f90
  - src/sd_channel_sediment3.f90
  - src/hru_control.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Erosion is the detachment, transport and deposition of soil particles by raindrop impact and flowing water. Raindrops detach particles on unprotected ground between rills, and the particles move to rills, then to larger channels and rivers, and can be deposited anywhere along the way. Erosion matters for reservoirs, which lose storage to deposited sediment, and for the soil, which loses the organic matter and nutrients in its surface layer.

SWAT+ computes soil loss from each HRU with the Modified Universal Soil Loss Equation (MUSLE) (Williams, 1975) on daily runs, or with a splash and overland flow erosion model on sub-daily runs. MUSLE replaces the rainfall energy factor of the Universal Soil Loss Equation (USLE) (Wischmeier and Smith, 1965, 1978) with a runoff factor, so it applies to single storms, reflects antecedent moisture through runoff, and needs no delivery ratio. Sediment is then lagged on its way to the channel together with surface runoff. Erosion and deposition in channels are covered on the [Channels](channels.md) page.

Erosion is computed only on days with surface runoff and a positive peak runoff rate. HRUs with a ponded surface (wetlands and paddies) produce no surface runoff and no erosion.

## Peak runoff rate

The peak runoff rate is the largest flow rate during a runoff event. It sets the erosive power of the storm in MUSLE. The method is chosen with `sed_det` in [`codes.bsn`](../input-reference/codes-bsn.md).

**NRCS peak rate equation** (`sed_det = 0`):

$$q_{peak} = \frac{prf}{6578.6}\cdot\frac{A\,Q_{surf}}{t_{conc}}\cdot\frac{1}{35.3}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $q_{peak}$ | Peak runoff rate | m³/s |
| $prf$ | Peak rate factor, `adj_pkrt_sed` in [`parameters.bsn`](../input-reference/parameters-bsn.md) | - |
| $A$ | HRU area | ha |
| $Q_{surf}$ | Surface runoff generated on the day | mm H2O |
| $t_{conc}$ | Time of concentration of the HRU (see [Hydrology](hydrology.md)) | hr |

This is the NRCS triangular unit hydrograph peak, $q = 484\,A\,Q/t_p$ in U.S. units, with the time of concentration used as the time to peak. The NRCS value of the peak rate factor is 484, which is also the built-in value. A zero in [`parameters.bsn`](../input-reference/parameters-bsn.md) is replaced by 1.0, and the SWAT+ reference data sets use 1.0, which gives peak rates 484 times smaller than the NRCS equation. Users of this method should check the value against their calibration.

**Rational formula with half-hour rainfall** (`sed_det = 1`):

$$q_{peak} = \frac{\alpha_{tc}\,Q_{surf}\,A_{km}}{3.6\,t_{conc}}, \qquad \alpha_{tc} = 1 - \exp\left[2\,t_{conc}\,\ln(1 - \alpha_{0.5})\right]$$

where $\alpha_{tc}$ is the fraction of daily rain that falls in the time of concentration, $\alpha_{0.5}$ the fraction that falls in the wettest half hour (generated daily, see [Climate and weather](climate-weather.md)) and $A_{km}$ the HRU area in km².

## MUSLE

SWAT+ computes daily sediment yield as

$$sed = 11.8\left(V_{surf}\,q_{peak}\right)^{0.56} K_{USLE}\,C_{USLE}\,P_{USLE}\,LS_{USLE}\,CFRG$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $sed$ | Sediment yield on the day | metric tons |
| $V_{surf}$ | Surface runoff volume, $10\,Q_{surf}\,A$ | m³ |
| $K_{USLE}$ | Soil erodibility factor, `usle_k` of the first layer in [`soils.sol`](../input-reference/sol.md) | 0.013 t m² hr/(m³ t cm) |
| $C_{USLE}$ | Cover and management factor, computed daily | - |
| $P_{USLE}$ | Support practice factor, `usle_p` in [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum) | - |
| $LS_{USLE}$ | Topographic factor | - |
| $CFRG$ | Coarse fragment factor | - |

The runoff factor is the original MUSLE form of Williams (1975), with the runoff volume in m³. The SWAT 2009 documentation writes the same factor with runoff in mm and area in ha, without the factor 10, so SWAT+ sediment yields for the same inputs are larger by $10^{0.56}$, about 3.6.

### Soil erodibility

Some soils erode more easily than others even when all other factors are the same. $K_{USLE}$ is the soil loss per unit of erosion index on a standard plot 22.1 m long on a 9% slope, kept in continuous fallow. Values are entered for each soil in [`soils.sol`](../input-reference/sol.md) (see that page for estimation methods).

### Cover and management

The cover and management factor is the ratio of soil loss from land under given conditions to soil loss from clean-tilled, continuous fallow. Plant cover changes through the year, so SWAT+ computes $C_{USLE}$ every day from the surface residue and the plant canopy:

$$C_{USLE} = \exp\left[-\mathrm{rsd\_cover}\,\frac{rsd + 1}{1000}\right]\left[1 - f_{gc}\,\exp(-0.328\,h_c)\right]$$

$$f_{gc} = \frac{B}{B + \exp(1.175 - 1.748\,B)}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $\mathrm{rsd\_cover}$ | Residue cover factor, `rsd_cover` in [`parameters.bsn`](../input-reference/parameters-bsn.md) (0.75 when zero) | - |
| $rsd$ | Surface residue | kg/ha |
| $B$ | Above-ground biomass of the plant community | t/ha |
| $h_c$ | Canopy height of the plant community | m |

The minimum C factor of each plant (`usle_c_min` in [`plants.plt`](../input-reference/plt.md)) is not used by this daily calculation. It is used only by the sub-daily erosion model below. The daily C factor and its two parts are written to the erosion output.

### Support practice

The support practice factor is the ratio of soil loss with a practice such as contouring, strip cropping or terracing to soil loss with up-and-down-slope culture. It comes from the row of [`cons_practice.lum`](../input-reference/lum-tables.md) named in the `cons_prac` column of [`landuse.lum`](../input-reference/lum.md).

### Topographic factor

$$LS_{USLE} = \left(\frac{L_{hill}}{22.1}\right)^m\left(65.41\,\sin^2\alpha_{hill} + 4.56\,\sin\alpha_{hill} + 0.065\right), \qquad m = 0.6\left[1 - \exp(-35.835\,slp)\right]$$

where $L_{hill}$ is the slope length (`slp_len` in [`topography.hyd`](../input-reference/hyd.md#topographyhyd), m), $slp$ the slope (`slp`, m/m) and $\alpha_{hill} = \arctan(slp)$. [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum) also has a maximum slope length for each practice (`slp_len_max`); SWAT+ 62.0.1 reads it but the LS factor uses the full slope length.

### Coarse fragments

$$CFRG = \exp(-0.053\,rock)$$

where $rock$ is the rock content of the first soil layer (`rock` in [`soils.sol`](../input-reference/sol.md), %).

### Snow cover

The SWAT 2009 documentation reduces MUSLE sediment yield under a snowpack. In SWAT+ 62.0.1 that reduction is not reached for any snow depth, so snow cover does not change the sediment yield. Snowmelt runoff still produces erosion through $Q_{surf}$ and $q_{peak}$.

### USLE soil loss for output

Alongside MUSLE, SWAT+ computes the USLE soil loss from rainfall energy for output (`usle` in the HRU loss files):

$$A_{USLE} = 1.292\,EI_{USLE}\,K_{USLE}\,C_{USLE}\,P_{USLE}\,LS_{USLE}\,CFRG$$

$$EI_{USLE} = R_{day}\left[12.1 + 8.9\left(\log_{10} I - 0.434\right)\right]\frac{I_{30}}{1000}$$

where $I_{30} = 2\,\alpha_{0.5}\,R_{day}$ is the maximum 30-minute intensity (mm/hr) and $I = -2\ln(1 - \alpha_{0.5})\,R_{day}$ the peak intensity. The USLE value is reported only. It does not add to the sediment yield.

## Sub-daily erosion

When the simulation uses a sub-daily time step with Green-Ampt infiltration, sediment for each time step comes from raindrop splash and overland flow erosion instead of MUSLE.

**Splash erosion.** Rain is split into direct throughfall and leaf drip by the canopy cover, $\min(LAI, 1)$. Their kinetic energies are

$$KE_{direct} = 8.95 + 8.44\,\log_{10} I, \qquad KE_{leaf} = 15.8\sqrt{0.5\,h_c} - 5.87$$

in J/m²/mm, where $I$ is the rainfall intensity of the step (mm/hr). Splash detachment is

$$sed_{spl} = k_d\,KE\,\exp\left(-\mathrm{splash}\,\frac{h_{flow}}{1000}\right)A_{km}$$

with $k_d$ a soil detachability (g/J) set from the texture of the top layer (1.2 for silt up to 3.0 for loamy sand), $KE$ the total kinetic energy of the step, $h_{flow}$ the runoff depth of the step (mm) and `splash` in [`parameters.bsn`](../input-reference/parameters-bsn.md). Splash stops when the runoff depth is at least three times the median raindrop diameter, or is negligible.

**Overland flow erosion.**

$$sed_{ov} = 11.02\,\mathrm{rill}\;K_{USLE}\;\mathrm{cov\_mgt}\;C\;\tau^{\,\mathrm{surq\_exp}}, \qquad \tau = 9807\,\frac{h_{flow}}{1000}\,slp$$

in kg/hr/m², converted to tons for the step and the HRU area. `rill`, `cov_mgt` and `surq_exp` are in [`parameters.bsn`](../input-reference/parameters-bsn.md); $C$ is the SWAT 2009 cover factor computed from `usle_c_min` and the soil cover. All three default to zero. The rate is proportional to `rill` and `cov_mgt`, so overland flow erosion is zero unless both are set; a zero `surq_exp` makes the shear stress term equal to 1.

On urban HRUs both terms apply only to the pervious fraction. The sediment of the day is the sum over the steps after the lag described below.

With a sub-daily time step and the curve number method, the splash and overland flow terms are not computed and MUSLE is not used either, so the HRU produces no lagged sediment from the surface.

## Sediment in lateral and tile flow

Lateral and tile flow transport a small sediment load:

$$sed_{lat} = \frac{\mathrm{lat\_sed}\,(Q_{lat} + Q_{tile})\,A}{100000}$$

in metric tons, with `lat_sed` from [`hydrology.hyd`](../input-reference/hyd.md) treated as a concentration in mg/L, and $Q_{lat}$, $Q_{tile}$ in mm. Sediment concentrations in subsurface flow are usually very low and matter only where return flow is large. Organic nitrogen and phosphorus in lateral flow are set by `lat_orgn` and `lat_orgp` in the same file.

## Particle size

The sediment from the surface is split into five classes (sand, silt, clay, small aggregates and large aggregates) using fractions set from the sand, silt and clay content of the top soil layer (Foster et al., 1980):

| Class | Fraction of detached sediment |
|-------|-------------------------------|
| Sand | $f_{sa}(1 - f_{cl})^{2.49}$ |
| Silt | $0.13\,f_{si}$ |
| Clay | $0.20\,f_{cl}$ |
| Small aggregates | $2.0\,f_{cl}$ for $f_{cl} < 0.25$; $0.28\,(f_{cl} - 0.25) + 0.5$ up to $f_{cl} = 0.5$; 0.57 above |
| Large aggregates | the remainder |

where $f_{sa}$, $f_{si}$ and $f_{cl}$ are the sand, silt and clay fractions. If the first four add up to more than 1, they are rescaled and large aggregates are set to zero.

## Sediment lag

Sediment, the particle size classes and the nutrients attached to sediment pass through the same surface lag store as runoff, and the same fraction, $1 - \exp(-\mathrm{surq\_lag}/t_{conc})$, is released each day (see [Hydrology](hydrology.md)).

## Urban areas

For an HRU with an urban land use (the `urban` and `urb_ro` columns of [`landuse.lum`](../input-reference/lum.md), parameters in [`urban.urb`](../input-reference/str.md#urbanurb)), the sediment and nutrient loads of the impervious fraction $f_{imp}$ (`frac_imp`) are computed separately and mixed with the loads of the pervious part:

$$L = L_{urb}\,f_{imp} + L_{perv}\,(1 - f_{imp})$$

where $L_{perv}$ is the load from MUSLE and the soil nutrient routines. Urban loads are computed before the surface lag store, and sediment from impervious surfaces is all silt. `urb_ro` selects one of two methods; any other value gives no urban loads.

**USGS regression equations** (`usgs_reg`). On days with more than 0.1 mm of precipitation and of surface runoff, the storm load of each constituent (kg) is

$$Y = \frac{\beta_0}{2.205}\left(\frac{R_{day}}{25.4}\right)^{\beta_1}\left(\frac{A\,f_{imp}}{2.589}\right)^{\beta_2}\left(100\,f_{imp} + 1\right)^{\beta_3}\beta_4$$

with $R_{day}$ the precipitation (mm) and $A$ the HRU area (km²). The coefficients (Driver and Tasker, 1988) depend on the mean annual precipitation of the HRU's weather generator station:

| Constituent | Below 508 mm | 508 to 1016 mm | 1016 mm and above |
|---|---|---|---|
| Suspended solids | 1778, 0.867, 0.728, 0.157, 2.367 | 812, 1.236, 0.436, 0.202, 1.938 | 97.7, 1.002, 1.009, 0.837, 2.818 |
| Total N | 20.2, 0.825, 1.070, 0.479, 1.258 | 4.04, 0.936, 0.937, 0.692, 1.373 | 1.66, 0.703, 0.465, 0.521, 1.845 |
| Total P | 1.725, 0.884, 0.826, 0.467, 2.130 | 0.697, 1.008, 0.628, 0.469, 1.790 | 1.618, 0.954, 0.789, 0.289, 2.247 |

Each cell lists $\beta_0$ to $\beta_4$. Total N is split into 70 % organic N and 30 % nitrate, and total P into 75 % sediment-bound and 25 % soluble P.

**Build-up and wash-off** (`buildup_washoff`). Solids build up on impervious surfaces between storms:

$$SED = \frac{SED_{mx}\,t}{t_{1/2} + t}$$

where $SED_{mx}$ is `dirt_max` (kg per curb km), $t_{1/2}$ is `t_halfmax` (days) and $t$ the number of days since the surface was last washed. On a day with more than 0.1 mm of surface runoff the solids left after wash-off are

$$SED_{after} = SED\,\exp\!\left(-k_w\,q_{pk}\,t_{ro}\right)$$

with $k_w$ = `urb_wash` (1/mm), $q_{pk}$ the peak runoff rate (mm/h) and $t_{ro}$ the storm duration from the half-hour rainfall fraction plus the time of concentration (h, at most 24). The washed-off solids are $(SED - SED_{after})$ times `curb_den`, in kg/ha; their N, P and nitrate contents are `conc_totn`, `conc_totp` and `conc_no3n` (mg/kg). Organic N is total N minus nitrate, and total P is split 75 % sediment-bound and 25 % soluble. After the storm, $t$ is reset to the time that would build up $SED_{after}$. Sub-daily runs apply the same method for each time step. Street sweeping has no effect in 62.0.1 (see [`sweep.ops`](../input-reference/ops.md#sweepops)).

## Filter strips, grassed waterways and user BMPs

These practices are attached to a land use through the `vfs`, `grww` and `bmp` columns of [`landuse.lum`](../input-reference/lum.md) (parameters in [the structural practice files](../input-reference/str.md)). They act on the loads released from the surface lag store each day. None of them changes the runoff volume, so the water balance is unchanged.

### Filter strips

A vegetative filter strip at the field edge (White and Arnold, 2009) is split into two sections. Section 1, 90 % of the strip area, receives the fraction $1 - c$ of the field runoff; section 2, 10 % of the strip area, receives the fraction $c\,(1 - h)$. The rest, $c\,h$, is channelized and passes the strip unchanged. Here $c$ is `con_vfs` and $h$ is `cha_q`, and the strip area is the HRU area divided by `fld_vfs`.

For each section $i$, the runoff depth over the strip $q_i$ (mm) and the sediment load per strip area $s_i$ (kg/m²) give the percent reductions

$$RR_i = 75.8 - 10.8\,\ln q_i + 25.9\,\ln K_{sat}, \qquad SR_i = 79.0 - 1.04\,s_i + 0.213\,RR_i$$

with $K_{sat}$ the saturated conductivity of the top soil layer (mm/h). The runoff reduction $RR_i$ is used only to estimate nutrient removal. The other reductions follow from these:

| Load | Reduction (%) |
|---|---|
| Sediment | $SR_i$ |
| Organic N | $0.036\,SR_i^{1.69}$ |
| Nitrate in surface runoff | $39.4 + 0.584\,RR_i$ |
| Sediment-bound P | $0.903\,SR_i$ |
| Soluble P | $29.3 + 0.51\,RR_i$ |
| Pesticide in runoff and on sediment | $RR$ and $SR$ |

Each reduction is limited to 0 to 100 % and weighted by the share of the HRU runoff each section receives. Pesticide removed by the strip is returned to the top soil layer. In 62.0.1 the soluble P reduction of section 2 uses the value computed for sediment-bound P, and pesticide loads are reduced a second time after the removed amount is returned.

### Grassed waterways

A grassed waterway is a vegetated trapezoidal channel with 8:1 side slopes through the field. The peak flow is computed from the day's runoff with a triangular hydrograph, and the flow depth in the waterway from Manning's equation. Part of the runoff enters the waterway as sheet flow over its side slopes; 20 % of the wetted side slope area above the flow, at most 10 % of the HRU, acts as a filter, with reductions computed as for filter strips:

$$RR = 95.6 - 10.79\,\ln q_{sf}, \qquad SR = 79.0 - 1.04\,s_{sf} + 0.213\,RR$$

both limited to 95 %. The sediment left after this filtering is then routed through the waterway: where its concentration exceeds the transport capacity $C_{ch} = \mathrm{sed\_co}\;v^{1.5}$ (with $v$ the flow velocity), the excess is deposited. Sediment, organic N and sediment-bound P are reduced by the fraction of sediment that leaves the waterway, and nitrate and soluble P in surface runoff by $RR$.

### User BMPs

A user BMP multiplies the HRU loads by $1 - e$ for each removal efficiency $e$ in [`bmpuser.str`](../input-reference/str.md#bmpuserstr): sediment, sediment-bound P, soluble P, organic N, and nitrate in surface runoff and lateral flow.

### Riparian buffers and saturated buffers

A riparian buffer reduction of nitrate in lateral flow is coded but depends on a buffer width that no input sets, so it has no effect in 62.0.1. A saturated buffer diverts part of the tile flow of one HRU into the soil of another HRU under a decision table (see [`satbuffer.str`](../input-reference/str.md#satbufferstr)).

## Channel erosion and deposition

Sediment that reaches a channel can be deposited on the floodplain, deposited in the channel, or joined by sediment eroded from the channel banks and bed. These processes use the channel properties in [`hyd-sed-lte.cha`](../input-reference/sd-channel.md) and are described on the [Channels](channels.md) page.

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `sed_det` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` NRCS peak rate, `1` rational formula with half-hour rainfall |
| `adj_pkrt_sed` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Peak rate factor for `sed_det = 0` |
| `adj_pkrt` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Multiplier on the generated half-hour rainfall fraction |
| `rsd_cover` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Residue term of the daily C factor |
| `splash`, `rill`, `surq_exp`, `cov_mgt` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Sub-daily splash and overland flow erosion |
| `usle_k`, `rock`, `sand`, `silt`, `clay` | [`soils.sol`](../input-reference/sol.md) | Erodibility, coarse fragments, particle size |
| `usle_p` | [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum) | Support practice factor |
| `slp`, `slp_len` | [`topography.hyd`](../input-reference/hyd.md#topographyhyd) | Slope and slope length |
| `lat_sed` | [`hydrology.hyd`](../input-reference/hyd.md) | Sediment concentration in lateral and tile flow |

## Related pages

- [Hydrology](hydrology.md) for surface runoff, time of concentration and the surface lag.
- [Nutrient cycling](nutrient-cycling.md) for nitrogen and phosphorus attached to sediment.
- [Channels](channels.md) for channel erosion and deposition.
- [Channel, sediment and nutrient output](../output-reference/channel-sediment-nutrient.md).

??? quote "Sources"

    - Daily call sequence: [`surface.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/surface.f90), [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Peak rate: [`ero_pkq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_pkq.f90)
    - MUSLE: [`ero_ysed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ysed.f90); C factor: [`ero_cfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_cfactor.f90); erosivity: [`ero_eiusle.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_eiusle.f90)
    - K, P and CFRG product: [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90); LS and P: [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90)
    - Sub-daily erosion: [`ero_ovrsed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ovrsed.f90)
    - Lateral sediment: [`swr_latsed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_latsed.f90)
    - Particle size fractions: [`soil_phys_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_phys_init.f90)
    - Sediment lag: [`stor_surfstor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/stor_surfstor.f90)
    - Urban loads: [`hru_urban.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_urban.f90), [`hru_urbanhr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_urbanhr.f90) (sub-daily), regression in [`regres.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/regres.f90); precipitation region `wgn_pms%ireg` set in `cli_initwgn.f90`; days since wash-off `twash`. The regression for COD is computed but not used.
    - Filter strips: [`smp_filter.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_filter.f90) (section 2 soluble P assigns `remove21` and then uses `remove2`); riparian buffer: [`smp_buffer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_buffer.f90) (`filterw` is allocated as zero and never set). Grassed waterways: [`smp_grass_wway.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_grass_wway.f90). User BMPs: [`smp_bmpfixed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_bmpfixed.f90). Called from `hru_control.f90` after `stor_surfstor`.
    - References: Driver, N. E., and Tasker, G. D. (1988), Techniques for estimation of storm-runoff loads, volumes, and selected constituent concentrations in urban watersheds in the United States, USGS Open-File Report 88-191. White, M. J., and Arnold, J. G. (2009), Development of a simplistic vegetative filter strip model for sediment and nutrient retention at the field scale, Hydrological Processes 23, 1602–1616.
    - Half-hour rainfall: [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90), [`cli_initwgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_initwgn.f90)
    - Defaults for zero parameters: [`basin_prm_default.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_prm_default.f90)

    | Symbol or column | Fortran variable |
    |------------------|------------------|
    | `sed_det` | `bsn_cc%sed_det` |
    | `adj_pkrt_sed` ($prf$), `adj_pkrt` | `bsn_prm%prf`, `bsn_prm%adj_pkr` |
    | `rsd_cover` | `bsn_prm%rsd_covco` |
    | `splash`, `rill`, `surq_exp`, `cov_mgt` | `bsn_prm%eros_spl`, `bsn_prm%rill_mult`, `bsn_prm%eros_expo`, `bsn_prm%c_factor` |
    | `usle_c_min` | `pldb%usle_c`, community value `cvm_com(j)` |
    | `lat_sed` | `hru(j)%hyd%lat_sed` |
    | $q_{peak}$ | `qp_cms` |
    | $sed$ | `sedyld(j)` |
    | $C_{USLE}$ | `usle_cfac(j)` |
    | $K\,P\,LS\,CFRG\times 11.8$ | `hru(j)%lumv%usle_mult` |
    | $C \times$ the above | `cklsp(j)` |
    | $LS_{USLE}$, $P_{USLE}$ | `hru(j)%lumv%usle_ls`, `hru(j)%lumv%usle_p` |
    | $EI_{USLE}$, $A_{USLE}$ | `usle_ei`, `usle` |
    | Sub-daily sediment | `hhsedy(j,k)` |
    | Particle size fractions | `soil(j)%det_san`, `det_sil`, `det_cla`, `det_sag`, `det_lag` |

---
title: Reservoirs and wetlands
description: Reservoir water balance, release rules, sediment and nutrient settling, and wetlands and rice paddies on HRUs in SWAT+.
status: review
verified_against:
  - src/res_control.f90
  - src/res_hydro.f90
  - src/res_initial.f90
  - src/res_read.f90
  - src/res_sediment.f90
  - src/res_nutrient.f90
  - src/reservoir_module.f90
  - src/reservoir_data_module.f90
  - src/wetland_control.f90
  - src/wet_initial.f90
  - src/et_act.f90
  - src/hru_control.f90
  - src/theta.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

SWAT+ has two kinds of water body:

- Reservoirs are spatial objects in the routing network. They receive water from channels, HRUs, routing units, aquifers or recall objects, store it, and release it by rules written in a decision table. They are defined in [`reservoir.res`](../input-reference/res.md#reservoirres), which points to records in [`hydrology.res`](../input-reference/res.md#hydrologyres), [`sediment.res`](../input-reference/res.md#sedimentres), [`nutrients.res`](../input-reference/res.md#nutrientsres), [`initial.res`](../input-reference/res.md#initialres) and a release table in [`res_rel.dtl`](../input-reference/dtl.md).
- Wetlands belong to an HRU. They store water on the HRU surface (including rice paddies and other impoundments), receive rain, irrigation and the HRU's runoff, and release water by the same kind of decision table. They are defined in [`wetland.wet`](../input-reference/wet.md#wetlandwet) and [`hydrology.wet`](../input-reference/wet.md#hydrologywet) and assigned to HRUs through the `surf_stor` column of [`hru-data.hru`](../input-reference/hru.md).

Both use the same release, sediment and nutrient calculations.

## Reservoir water balance

A reservoir starts to operate in the year and month given by `yr_op` and `mon_op` in [`hydrology.res`](../input-reference/res.md#hydrologyres). Before that date, inflow passes through unchanged.

Each day:

1. Inflow is added to storage. If the reservoir is a point of diversion in the water allocation inputs, withdrawals are taken.
2. The release table is evaluated and the release computed (see below). The release is smoothed with lag factors.
3. Rain on the water surface is added, then release, evaporation and seepage are removed, each limited to the water available.
4. The surface area is updated from the new storage.

$$
V_i = V_{i-1} + V_{in} + V_{pcp} - V_{out} - V_{evap} - V_{seep}
$$

$$
V_{pcp} = 10\,R\,A, \qquad V_{evap} = 10\,\eta\,E_o\,A, \qquad V_{seep} = 240\,K_{sat}\,A
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $V$ | water stored | m³ | |
| $R$ | precipitation | mm | |
| $E_o$ | potential evapotranspiration | mm | |
| $\eta$ | evaporation coefficient | - | `evap_co` |
| $K_{sat}$ | hydraulic conductivity of the reservoir bottom | mm/h | `k` |
| $A$ | water surface area on the previous day | ha | |

When gwflow is active, seepage is computed by gwflow as exchange with the groundwater cells under the reservoir.

### Surface area

Surface area is a power function of storage, $A = \beta_1 V^{\beta_2}$. The coefficients are computed from the areas and volumes at the principal and emergency spillways (`area_ps`, `vol_ps`, `area_es`, `vol_es`):

$$
\beta_2 = \frac{\log_{10} A_{es} - \log_{10} A_{ps}}{\log_{10} V_{es} - \log_{10} V_{ps}} \;(\le 0.9), \qquad \beta_1 = \left(\frac{A_{es}}{V_{es}}\right)^{\beta_2}
$$

If $\beta_2$ would exceed 0.9, it is set to 0.9 and $\beta_1 = (A_{ps}/V_{ps})^{0.9}$.

### Release smoothing

The release from the decision table is blended with the previous day's release so that outflow does not jump:

$$
Q_i = \alpha\,Q^{*} + (1 - \alpha)\,Q_{i-1}, \qquad \alpha = e^{-\lambda}
$$

where $Q^{*}$ is the release from the table and $\lambda$ is the lag for rising releases or the lag for falling releases. The two lags are read from the last two columns of [`hydrology.res`](../input-reference/res.md#hydrologyres), which the SWAT+ Editor labels `shp_co1` and `shp_co2` (formerly area-volume shape coefficients). A lag of 0 gives no smoothing.

## Release rules

Each reservoir names a release table. Names that begin with `ctbl_` refer to a conditions table; all others refer to a decision table in [`res_rel.dtl`](../input-reference/dtl.md). The decision table conditions are evaluated as described in [Decision tables](decision-tables.md), and every action that fires adds a release. Release options (the `option` of a `release` action):

| Option | Release for the day |
|---|---|
| `rate` | constant × 86400 (constant in m³/s) |
| `rate_pct` | constant % of the principal volume |
| `inflo_rate` | larger of (inflow + second constant × 86400) and constant × 86400 |
| `inflo_frac` | constant × inflow |
| `ab_emer` | all storage above the emergency volume |
| `days` | (storage − lower bound) / constant days, where the lower bound is 0, or a fraction (second constant) of the principal or emergency volume |
| `dyrt` | (storage − lower bound) / constant days + second constant % of the principal volume, with the lower bound 0, the principal or the emergency volume |
| `dyrt1` | as `dyrt`, with the lower bound taken from a condition of the table |
| `inflo_targ` | inflow + (storage − target), with the target a fraction of the principal volume taken from a condition |
| `weir` | discharge over a weir from [`weir.res`](../input-reference/res.md#weirres) |
| `meas` | measured release from a recall file |
| `natlake` | natural lake outflow, $k_r\,S_{eff}\,(S_{eff}/(S_{max} - S_0))^{1.5}$ with $S_0$ a fraction of the principal volume and $S_{max}$ the principal volume |
| `nonirr-h06`, `irr-h06` | Hanasaki et al. (2006) release for non-irrigation and irrigation reservoirs, from the long-term mean monthly inflow and demand |
| `hydrop` | hydropower release: mean inflow scaled by a storage factor and a seasonal factor |

## Reservoir sediment

When the suspended sediment concentration is above the equilibrium concentration `nsed`, the excess settles:

$$
C_{sed,i} = (C_{sed} - C_{eq})\,e^{-0.184\,d_{50}} + C_{eq}
$$

where $d_{50}$ is the median particle size in [`sediment.res`](../input-reference/res.md#sedimentres) (µm). Sediment leaves with the release at the settled concentration. When the concentration is at or below `nsed`, no sediment is released.

## Reservoir nutrients

Organic N, particulate P, soluble N (nitrate, ammonium, nitrite) and soluble P are removed by settling. The fraction removed each day is

$$
f = \min\left(1,\;(C - C_{min})\,r\,\theta^{\,T - 20}\right)
$$

| Symbol | Meaning | Input |
|---|---|---|
| $C$ | concentration of the pool | mg/L |
| $C_{min}$ | minimum concentration for settling | `n_min_stl`, `p_min_stl` |
| $r$ | settling rate; for organic N and particulate P it differs between the mid-year period (`mid_start` to `mid_end` months) and the rest of the year; soluble N and P have one rate each | `mid_n_stl`, `n_stl`, `mid_p_stl`, `p_stl`; positions 8 and 9 for soluble N and P |
| $\theta$ | temperature factor | `theta_n`, `theta_p` |
| $T$ | air temperature | °C |

For soluble N and P the fraction is multiplied by 0.2. After settling, the release takes nutrients in proportion to its share of the water.

Pesticides, salts and constituents in reservoirs are described on the [Pesticides](pesticides.md) and [Salts and constituents](salts-constituents.md) pages.

## Wetlands and paddies

A wetland covers part of its HRU and stores water on the surface. Its principal and emergency volumes are the HRU area times the depths `dp_ps` and `dp_es` in [`hydrology.wet`](../input-reference/wet.md#hydrologywet). When a weir is assigned in [`weir.res`](../input-reference/res.md#weirres), the principal volume is the HRU area times the weir height, and the emergency volume is at least 1.2 times that.

Each day:

1. Rain and irrigation are added to the wetland.
2. The wetted area is updated from storage with the volume-depth coefficients of [`hydrology.wet`](../input-reference/wet.md#hydrologywet). Rice paddies are treated as flat and cover the whole HRU.
3. Seepage into the soil is $24\,K_{sat}\,A$, with $K_{sat}$ the `k` of [`hydrology.wet`](../input-reference/wet.md#hydrologywet) (or the conductivity set by a puddling operation). Seepage that the soil cannot take because it is saturated stays in the wetland. Nutrients move into the top soil layer with the seepage.
4. Release follows the decision table, or the weir equation for paddies, and becomes surface runoff of the HRU.
5. Sediment, nutrients, salts and constituents are updated as for reservoirs.

Evaporation from standing water is taken from the wetland first, as part of the HRU soil evaporation, before any water is taken from the soil.

## Parameters

| Parameter | File | Effect |
|---|---|---|
| `yr_op`, `mon_op` | [`hydrology.res`](../input-reference/res.md#hydrologyres) | Year and month the reservoir starts operating |
| `area_ps`, `vol_ps`, `area_es`, `vol_es` | [`hydrology.res`](../input-reference/res.md#hydrologyres) | Surface areas (ha) and volumes (ha-m) at the principal and emergency spillways |
| `k` | [`hydrology.res`](../input-reference/res.md#hydrologyres), [`hydrology.wet`](../input-reference/wet.md#hydrologywet) | Bottom hydraulic conductivity (mm/h) |
| `evap_co` | [`hydrology.res`](../input-reference/res.md#hydrologyres) | Evaporation coefficient |
| `shp_co1`, `shp_co2` | [`hydrology.res`](../input-reference/res.md#hydrologyres) | Release lags for rising and falling outflow |
| `nsed`, `d50` | [`sediment.res`](../input-reference/res.md#sedimentres) | Equilibrium sediment concentration (mg/L) and median particle size (µm) |
| settling rates, $\theta$, minimum concentrations | [`nutrients.res`](../input-reference/res.md#nutrientsres) | Nutrient settling |
| `dp_ps`, `dp_es`, `hru_ps`, `hru_es` | [`hydrology.wet`](../input-reference/wet.md#hydrologywet) | Wetland depths (mm) and HRU fractions at the principal and emergency levels |
| release table | [`res_rel.dtl`](../input-reference/dtl.md) | Release rules |

## Related pages

- [Reservoir inputs](../input-reference/res.md) and [wetland inputs](../input-reference/wet.md)
- [Decision tables](decision-tables.md) and the [`*.dtl` files](../input-reference/dtl.md)
- [Channels](channels.md), [Aquifers](aquifers.md)
- [Aquifer, reservoir and plant output](../output-reference/aquifer-reservoir-plant.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Reservoir daily driver: [`src/res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90)
    - Release options: [`src/res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90); conditions tables: [`src/res_rel_conds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_rel_conds.f90); weir release for paddies: [`src/res_weir_release.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_weir_release.f90)
    - Initialisation, area coefficients and lags: [`src/res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90); reader: [`src/res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read.f90)
    - Sediment and nutrients: [`src/res_sediment.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_sediment.f90), [`src/res_nutrient.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_nutrient.f90), [`src/theta.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/theta.f90)
    - Types: [`src/reservoir_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_module.f90), [`src/reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_data_module.f90)
    - Wetlands: [`src/wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90), [`src/wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90); evaporation from standing water: [`src/et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90)

    Columns and variables:

    | Column | Variable |
    |---|---|
    | `yr_op`, `mon_op` | `res_hyd%iyres`, `%mores` |
    | `area_ps`, `vol_ps`, `area_es`, `vol_es` | `res_hyd%psa`, `%pvol`, `%esa`, `%evol` |
    | `evap_co`, `k` | `res_hyd%evrsv`, `%k` |
    | `shp_co1`, `shp_co2` | `res_hyd%br1`, `%br2`, copied to `res_ob%lag_up`, `%lag_down` |
    | $\beta_1$, $\beta_2$ | `res_ob%br1`, `res_ob%br2` |
    | `nsed`, `d50` | `res_sed%nsed`, `%d50`; settling factor `res_prm%sed_stlr_co` |
    | `mid_start`, `mid_end`, `mid_n_stl`, `n_stl`, `mid_p_stl`, `p_stl` | `res_nut%ires1`, `%ires2`, `%nsetlr1`, `%nsetlr2`, `%psetlr1`, `%psetlr2` |
    | `chla_co`, `secchi_co` (positions 8 and 9) | `res_nut%nsolr`, `%psolr` (soluble N and P settling rates) |
    | `theta_n`, `theta_p`, `n_min_stl`, `p_min_stl` | `res_nut%theta_n`, `%theta_p`, `%conc_nmin`, `%conc_pmin` |
    | wetland `dp_ps`, `dp_es`, `k` | `wet_hyd%pdep`, `%edep`, `%k` (copied to `hru%wet_hc`) |

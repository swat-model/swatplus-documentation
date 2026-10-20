---
title: Pesticides
description: Pesticide application, washoff, decay, plant uptake and transport in runoff, sediment, soil water, channels and aquifers.
status: review
verified_against:
  - src/pest_apply.f90
  - src/pest_washp.f90
  - src/pest_decay.f90
  - src/pest_lch.f90
  - src/pest_pesty.f90
  - src/pest_pl_up.f90
  - src/pest_parm_read.f90
  - src/pest_tempdecay_module.f90
  - src/pesticide_data_module.f90
  - src/mgt_sched.f90
  - src/hru_control.f90
  - src/ch_rtpest.f90
  - src/sd_hydsed_init.f90
  - src/res_pest.f90
  - src/aqu_1d_control.f90
  - src/basin_module.f90
  - src/basin_read_prm.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

SWAT+ simulates any number of pesticides, listed in the constituent setup and described in [`pesticide.pes`](../input-reference/pes.md#pesticidepes). Each pesticide has a sorption coefficient, a solubility, half-lives on foliage, in soil, in water and in benthic sediment, and optional degradation products (metabolites). On land, a pesticide is applied by a management operation, split between plant foliage and the soil, washed from foliage by rain, decayed, taken up by plants, and moved by surface runoff, lateral flow, tile flow, percolation and eroded sediment. Pesticide that reaches channels, reservoirs and aquifers continues to react and move there.

The daily order in an HRU is washoff (on days with at least 2.54 mm of rain), plant uptake, decay, transport in water, then transport with sediment (on days with erosion).

## Application

A pesticide application operation names the pesticide, the amount and an application method from [`chem_app.ops`](../input-reference/ops.md#chem_appops). The amount reaching the field is the applied amount multiplied by the application efficiency of the method:

$$
P_{app} = P_{op}\,\varepsilon_{app}
$$

The fraction intercepted by the canopy depends on the leaf area index of all plants in the HRU:

$$
f_{gc} = \frac{1.99532 - \operatorname{erfc}(1.333\,LAI - 2)}{2.1}, \qquad f_{gc} \ge 0
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $P_{app}$ | pesticide reaching the field | kg/ha | |
| $P_{op}$ | amount in the operation | kg/ha | application operation |
| $\varepsilon_{app}$ | application efficiency | fraction | `app_eff` in [`chem_app.ops`](../input-reference/ops.md#chem_appops) |
| $f_{gc}$ | fraction intercepted by foliage | fraction | |
| $LAI$ | sum of leaf area index of all plants | m²/m² | |

The intercepted part, $f_{gc}P_{app}$, is divided among the plants in proportion to their leaf area. The rest reaches the soil: the surface fraction `surf_frac` of the application method goes to the top soil layer (10 mm) and the remainder to the second layer.

## Washoff

On days with at least 2.54 mm of precipitation, a fixed fraction of the pesticide on each plant's foliage is washed to the top soil layer:

$$
P_{wash} = f_{wash}\,P_{fol}
$$

where $f_{wash}$ is the washoff fraction `frac_wash` of the pesticide and $P_{fol}$ the pesticide on the foliage (kg/ha).

## Decay

Pesticide on foliage and in each soil layer decays by first-order kinetics. The daily survival factor is computed from the half-life:

$$
P_{i} = P_{i-1}\,\exp\!\left(\frac{-0.693}{t_{1/2}}\right)
$$

with $t_{1/2}$ the foliar half-life `hl_foliage` for foliage and the soil half-life `hl_soil` for soil (days). A half-life of 0 removes all of the pesticide in one day.

### Temperature adjustment

When the temperature switch for pesticide decay in [`parameters.bsn`](../input-reference/parameters-bsn.md) is 1, the half-lives are treated as values at 25 °C and adjusted each day with a Q10 relation:

$$
t_{1/2}(T) = t_{1/2,25}\;Q_{10}^{\,(25 - T)/10}, \qquad Q_{10} = 2.58
$$

| Pool | Half-life used | Temperature $T$ |
|---|---|---|
| Soil layer | `hl_soil` | temperature of that layer |
| Foliage | `hl_foliage` | temperature of the top soil layer |
| Channel water | `aq_hlife` | channel water temperature (at least 0.1 °C) |
| Channel benthic sediment | `ben_hlife` | channel water temperature |
| Aquifer | `aq_hlife` | 0 °C; the aquifer temperature is not set in 62.0.1 |

Each 10 °C below 25 °C multiplies the half-life by 2.58, and each 10 °C above 25 °C divides it by 2.58. Reservoirs always use the unadjusted half-lives.

The temperature switch and the pesticide groundwater mixing factor are read as the 6th and 7th values of [`parameters.bsn`](../input-reference/parameters-bsn.md). Files written by the SWAT+ Editor label these columns `lin_sed` and `exp_sed`, which older revisions did not use. A file with `exp_sed = 1` therefore turns temperature-adjusted decay on, and the `lin_sed` value becomes the groundwater mixing factor. Check both columns before running pesticides with an older [`parameters.bsn`](../input-reference/parameters-bsn.md).

### Metabolites

When a pesticide has degradation products, a share of the mass that decays is added to each daughter pesticide:

$$
\Delta P_{d} = \Delta P_{parent}\;f_{d}\;\frac{M_{d}}{M_{parent}}
$$

| Symbol | Meaning | Units |
|---|---|---|
| $\Delta P_{d}$ | mass added to the daughter | kg/ha |
| $\Delta P_{parent}$ | parent mass decayed on the day | kg/ha |
| $f_{d}$ | fraction of the parent that degrades to this daughter, set separately for foliage, soil, water and benthic sediment | fraction |
| $M$ | molecular weight `mol_wt` | g/mol |

Metabolites form on foliage, in soil, in channel water and benthic sediment, and in aquifers.

## Plant uptake

Growing plants take up dissolved pesticide with the water they extract from each soil layer. Uptake from a layer is

$$
P_{up} = f_{TSCF}\;\frac{w_{up}}{SW_{eff} + w_{up} + K_d\,\rho_b\,z}\;P_{ly}
$$

$$
SW_{eff} = SW + n\,\max(0,\;FC - SW)
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $P_{up}$ | pesticide taken up from the layer | kg/ha | |
| $f_{TSCF}$ | transpiration stream concentration factor | - | `pl_uptake` |
| $w_{up}$ | plant water uptake from the layer | mm | |
| $SW$, $FC$ | layer soil water and field capacity | mm | |
| $n$ | resistance blending factor, 0 uses actual soil water and 1 uses field capacity | 0 to 1 | `resistance_n` (default 1) |
| $K_d$ | soil partition coefficient, $K_{oc}\cdot OC/100$ | mL/g | `soil_ads` |
| $\rho_b$, $z$ | bulk density and layer thickness | Mg/m³, mm | |
| $P_{ly}$ | pesticide in the layer | kg/ha | |

When `harvest_sink` is 1 (default), pesticide taken up is lost from the system. When it is 0, it is stored in the plant, removed with the harvested yield, and returned to the soil surface when the plant is killed.

## Transport in water

In each soil layer, pesticide is shared between the soil water and sorbed phases with a linear partition coefficient based on the organic carbon content of the layer:

$$
K_d = \frac{K_{oc}\;OC}{100}
$$

where $K_{oc}$ is `soil_ads` (mL/g) and $OC$ the organic carbon content of the layer (%). The concentration of pesticide in water leaving the layer is

$$
C = \min\!\left(\frac{P_{ly}\left[1 - \exp\!\left(\dfrac{-w}{SAT + K_d\,\rho_b\,z}\right)\right]}{w},\;\frac{S_w}{100}\right)
$$

| Symbol | Meaning | Units |
|---|---|---|
| $C$ | pesticide concentration in mobile water | kg/ha per mm |
| $w$ | water leaving the layer: percolation and lateral flow, plus surface runoff for the top layer and tile flow for the drained layer | mm |
| $SAT$ | water content of the layer at saturation | mm |
| $S_w$ | solubility `solub` | mg/L |

Mass moved by each flow path is the concentration times the flow:

- surface runoff removes $\beta_{perc}\,C$ times the runoff depth, where $\beta_{perc}$ is the pesticide percolation coefficient `pest_perc` in [`parameters.bsn`](../input-reference/parameters-bsn.md);
- lateral flow from the top layer also uses $\beta_{perc}\,C$; lateral flow from deeper layers uses $C$;
- tile flow and percolation use $C$. Percolation moves pesticide to the next layer, and out of the bottom layer to the aquifer.

## Transport with sediment

On days with erosion, pesticide sorbed to the top soil layer leaves with the sediment yield:

$$
P_{sed} = 0.001\;\frac{C_{sorb}\;sed\;\varepsilon_{er}}{A}
$$

| Symbol | Meaning | Units |
|---|---|---|
| $P_{sed}$ | pesticide removed with sediment | kg/ha |
| $C_{sorb}$ | sorbed concentration in the top layer | g/t |
| $sed$ | sediment yield | t |
| $\varepsilon_{er}$ | enrichment ratio, `erorgn` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) if above 0.001, otherwise computed from the sediment concentration | - |
| $A$ | HRU area | ha |

## Channels

Pesticide entering a channel is split into dissolved and sorbed phases using the channel carbon content and the sediment concentration of the inflow. Over the travel time through the reach (as a fraction of a day, at most 1) the dissolved and sorbed mass in water decays with the aquatic half-life `aq_hlife`. Dissolved pesticide volatilises at rate `aq_volat` and sorbed pesticide settles to the bed at rate `aq_settle` (m/day, divided by flow depth). Bed pesticide is resuspended at rate `aq_resus`, exchanges with the water by diffusion (a mixing velocity derived from the molecular weight and bed porosity), is buried at rate `ben_bury` over the active bed depth `ben_act_dep`, and decays with the benthic half-life `ben_hlife`. Dissolved pesticide above the solubility limit is moved to the bed. The pesticide left in the water leaves the reach in proportion to outflow over outflow plus storage.

Reservoirs follow the same set of processes (decay, volatilisation, settling, resuspension, diffusion and burial) without temperature adjustment. Pesticide reactions in wetlands are not simulated in this revision.

## Aquifers

Pesticide reaching an aquifer decays with the aquatic half-life and leaves in baseflow and deep seepage. Its concentration is the aquifer pesticide mass divided by a mixing volume made of baseflow, seepage, revap and a fraction of aquifer storage. That fraction is the pesticide groundwater mixing factor in [`parameters.bsn`](../input-reference/parameters-bsn.md) (default 0, so only the day's outflows dilute the pesticide). See [Aquifers](aquifers.md).

## Parameters

| Parameter | File | Effect |
|---|---|---|
| `soil_ads` | [`pesticide.pes`](../input-reference/pes.md) | Sorption coefficient normalised for organic carbon, $K_{oc}$ (mL/g) |
| `frac_wash` | [`pesticide.pes`](../input-reference/pes.md) | Fraction washed off foliage by rain |
| `hl_foliage`, `hl_soil` | [`pesticide.pes`](../input-reference/pes.md) | Half-lives on foliage and in soil (days) |
| `solub` | [`pesticide.pes`](../input-reference/pes.md) | Water solubility (mg/L) |
| `aq_hlife`, `ben_hlife` | [`pesticide.pes`](../input-reference/pes.md) | Half-lives in water and in benthic sediment (days) |
| `aq_volat`, `aq_resus`, `aq_settle`, `ben_bury` | [`pesticide.pes`](../input-reference/pes.md) | Channel volatilisation, resuspension, settling and burial velocities (m/day) |
| `ben_act_dep` | [`pesticide.pes`](../input-reference/pes.md) | Depth of the active benthic layer (m) |
| `mol_wt` | [`pesticide.pes`](../input-reference/pes.md) | Molecular weight (g/mol) |
| `pl_uptake`, `harvest_sink`, `resistance_n` | [`pesticide.pes`](../input-reference/pes.md) | Plant uptake factor and its fate in the plant |
| `app_eff`, `surf_frac` | [`chem_app.ops`](../input-reference/ops.md) | Application efficiency and share placed in the top 10 mm |
| `pest_perc` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Pesticide concentration in runoff relative to soil water |
| 6th and 7th values | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Groundwater mixing factor and temperature switch (columns labelled `lin_sed` and `exp_sed` by the Editor) |

## Related pages

- [`pesticide.pes`](../input-reference/pes.md) and [operation files](../input-reference/ops.md)
- [`parameters.bsn`](../input-reference/parameters-bsn.md)
- [Plant growth and land use management](plant-growth-lum.md)
- [Erosion and sediment](erosion-sediment.md)
- [Channels](channels.md), [Reservoirs and wetlands](reservoirs-wetlands.md), [Aquifers](aquifers.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Application: [`src/pest_apply.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_apply.f90), amount and efficiency in [`src/mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90) and [`src/actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Washoff: [`src/pest_washp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_washp.f90); call order and the 2.54 mm rain threshold: [`src/hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Decay and metabolites: [`src/pest_decay.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_decay.f90); Q10 function: [`src/pest_tempdecay_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_tempdecay_module.f90)
    - Plant uptake: [`src/pest_pl_up.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_pl_up.f90); harvest and kill: [`src/mgt_harvtuber.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvtuber.f90), [`src/mgt_killop.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_killop.f90)
    - Transport in water: [`src/pest_lch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_lch.f90); with sediment: [`src/pest_pesty.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_pesty.f90), [`src/pest_enrsb.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_enrsb.f90)
    - Database and decay factors: [`src/pest_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_parm_read.f90), [`src/pesticide_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pesticide_data_module.f90)
    - Channels: [`src/ch_rtpest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpest.f90), mixing velocity in [`src/sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90); reservoirs: [`src/res_pest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_pest.f90); aquifers: [`src/aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90)
    - Basin parameters: [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90) (`basin_parms`), read list-directed in [`src/basin_read_prm.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_prm.f90)

    Symbols and variables:

    | Symbol or column | Variable |
    |---|---|
    | $f_{gc}$ | `gc` |
    | `app_eff`, `surf_frac` | `chemapp_db%app_eff`, `chemapp_db%surf_frac` |
    | `soil_ads`, `frac_wash`, `hl_foliage`, `hl_soil` | `pestdb%koc`, `%washoff`, `%foliar_hlife`, `%soil_hlife` |
    | daily survival factors | `pestcp%decay_f`, `%decay_s`, `%decay_a`, `%decay_b` |
    | $f_d$ | `pestcp%daughter%foliar_fr`, `%soil_fr`, `%aq_fr`, `%ben_fr` |
    | $f_{TSCF}$, $n$ | `pestdb%pl_uptake`, `pestdb%resistance_n` |
    | $\beta_{perc}$ | `bsn_prm%percop` |
    | temperature switch | `bsn_prm%temp_decay` |
    | groundwater mixing factor | `bsn_prm%pestgwfact` |
    | pesticide on foliage, in the plant, in soil | `cs_pl%pl_on%pest`, `cs_pl%pl_in%pest`, `cs_soil%ly%pest` |

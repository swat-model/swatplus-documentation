---
title: Salts and Constituents
description: Transport, equilibrium chemistry and plant effects of salt ions, and transport, reactions and sorption of selenium and boron in SWAT+.
status: review
verified_against:
  - src/salt_lch.f90
  - src/salt_chem_hru.f90
  - src/salt_chem_soil_single.f90
  - src/salt_data_module.f90
  - src/salt_plant_read.f90
  - src/salt_uptake.f90
  - src/salt_uptake_read.f90
  - src/salt_roadsalt.f90
  - src/pl_waterup.f90
  - src/pl_biomass_gro.f90
  - src/cs_lch.f90
  - src/cs_rctn_hru.f90
  - src/se_reactions_soil.f90
  - src/cs_sorb_hru.f90
  - src/cs_reactions_read.f90
  - src/aqu_1d_control.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

SWAT+ can simulate two optional groups of dissolved substances, both listed in [`constituents.cs`](../input-reference/cs.md#constituentscs):

- Salt ions: the eight major ions sulfate (SO₄), calcium (Ca), magnesium (Mg), sodium (Na), potassium (K), chloride (Cl), carbonate (CO₃) and bicarbonate (HCO₃). In soil and aquifers they take part in mineral precipitation and dissolution and in cation exchange, and soil salinity can reduce plant growth.
- Constituents: selenate (SeO₄), selenite (SeO₃) and boron. Selenium species react in the soil (reduction, release from shale), and all three sorb to soil.

Both groups move with water along the same paths as nitrate: surface runoff, lateral flow, tile flow and percolation in the soil profile, then through aquifers, channels, reservoirs and wetlands. Inputs come from initial conditions, rain and dry deposition, fertiliser, irrigation, urban runoff and, for salts, road salt.

## Transport in soil water

Salt ions and constituents are transported in each layer with the nitrate leaching equations, including anion exclusion. For each ion or constituent $m$ in a layer:

$$
C_m = \frac{M_m}{w}\left[1 - \exp\!\left(\frac{-w}{(1 - \theta_e)\,SAT}\right)\right]
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $C_m$ | concentration in water leaving the layer | kg/ha per mm | |
| $M_m$ | mass in the layer | kg/ha | |
| $w$ | percolation plus lateral flow, plus surface runoff for the top layer and tile flow for the drained layer | mm | |
| $\theta_e$ | fraction of porosity from which anions are excluded | fraction | `anion_excl` in [`soils.sol`](../input-reference/sol.md) |
| $SAT$ | water content at saturation | mm | |

Percolation, tile flow and lateral flow below the top layer remove mass at concentration $C_m$. Surface runoff and lateral flow from the top layer remove mass at $\beta_N C_m$, where $\beta_N$ is the nitrate percolation coefficient `n_perc` in [`parameters.bsn`](../input-reference/parameters-bsn.md) (adjusted per HRU by calibration). Percolation moves mass to the next layer and out of the bottom of the profile to the aquifer. When gwflow is active with solute transport, groundwater discharging into the soil profile also adds mass.

## Salt chemistry

In each soil layer and in each aquifer, the dissolved ions are brought into equilibrium with five minerals and with the exchange sites of the soil:

- Precipitation and dissolution of calcite (CaCO₃), magnesite (MgCO₃), gypsum (CaSO₄), epsomite (MgSO₄) and halite (NaCl). A mineral dissolves when the ion activity product is below its solubility product and precipitates when above it.
- Activity coefficients from the ionic strength $I$ of the solution: the extended Debye-Hückel equation for $I \le 0.1$ mol/L and the Davies equation above. For $I \ge 5$ mol/L the Davies equation is evaluated at $I = 0.5$.
- Cation exchange among Ca, Mg, Na and K.

The calculation iterates until concentrations converge. The solubility products are fixed in the code:

| Mineral | Solubility product |
|---|---|
| CaCO₃ | 3.0702 × 10⁻⁹ |
| MgCO₃ | 4.7937 × 10⁻⁶ |
| CaSO₄ | 7.888 × 10⁻⁵ |
| MgSO₄ | 7.244 × 10⁻³ |
| NaCl | 37.3 |

## Salinity stress on plants

When the stress option in `salt_plants` is on and salts are simulated, each rooted soil layer gets a reduction factor from the FAO crop salt tolerance relation:

$$
f_{salt} =
\begin{cases}
1 & EC_e \le a \\
\dfrac{100 - b\,(EC_e - a)}{100} & EC_e > a
\end{cases}, \qquad 0 \le f_{salt} \le 1
$$

$$
EC_e = \frac{TDS}{k_{EC}}
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $EC_e$ | electrical conductivity of the soil water | dS/m | |
| $TDS$ | sum of the salt ion concentrations in the soil water, scaled by water content | mg/L | |
| $k_{EC}$ | TDS to EC conversion factor | (mg/L)/(dS/m) | `salt_plants` |
| $a$ | salinity threshold of the plant | dS/m | `salt_plants`, per plant |
| $b$ | yield loss per dS/m above the threshold | %/(dS/m) | `salt_plants`, per plant |

For gypsiferous soils (soil type 1 in `salt_plants`) the threshold is raised by 2 dS/m. A plant with $a = 0$ has no salt stress. The smallest factor over the rooted layers is the plant's salt stress.

Salt stress reduces daily biomass growth. With the "after other stresses" option (`salt_effect = 1`), growth is multiplied by the salt stress after taking the smallest of the water, temperature, nitrogen, phosphorus and aeration stresses. With option 2, salt stress is included in that minimum.

## Salt uptake by plants

If the file `salt_uptake` is present, each ion is removed from the soil in the amounts it specifies (kg/ha per day), distributed over the layers in proportion to root mass. The first plant of the HRU's plant community is used. Without the file, plants take up no salt.

## Selenium reactions

Selenate, selenite and nitrate in each soil layer are solved together each day (fourth-order Runge-Kutta, one-day step). The processes are:

- reduction of selenate to selenite and of selenite to elemental selenium, both first order and slowed by nitrate through the inhibition term $I/(I + C_{NO3})$;
- oxidation of selenium-bearing shale by oxygen and by nitrate, which releases selenate and consumes nitrate, in proportion to the shale fraction of the soil.

Rate constants, the inhibition constant, oxygen content and shale fractions are given per soil group in `cs_reactions`. Boron does not react.

## Sorption of constituents

Selenate, selenite and boron are split between soil water and the soil matrix with a linear partition coefficient:

$$
M_{sol} = \frac{M_{tot}}{1 + \dfrac{K_d\,\rho_b\,V_{soil}}{V_w}}, \qquad M_{sorb} = M_{tot} - M_{sol}
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $M_{tot}$, $M_{sol}$, $M_{sorb}$ | total, dissolved and sorbed mass in the layer | kg | |
| $K_d$ | partition coefficient for each constituent | L/kg | `cs_reactions` |
| $\rho_b$ | bulk density | Mg/m³ | |
| $V_{soil}$, $V_w$ | volumes of soil and of soil water in the layer | m³ | |

Aquifers use the same reaction and sorption equations with the aquifer parameters in `cs_reactions`.

## Inputs

| Source | File |
|---|---|
| Initial soil and aquifer content | [`salt_hru.ini`](../input-reference/salt.md#salt_hruini), [`salt_aqu.ini`](../input-reference/salt.md#salt_aquini), [`cs_hru.ini`](../input-reference/cs.md#cs_hruini), [`cs_aqu.ini`](../input-reference/cs.md#cs_aquini); channels: [`salt_channel.ini`](../input-reference/salt.md#salt_channelini), [`cs_channel.ini`](../input-reference/cs.md#cs_channelini) |
| Rain and dry deposition | [`salt_atmo.cli`](../input-reference/cli.md#salt_atmocli) |
| Fertiliser | [`salt_fertilizer.frt`](../input-reference/salt.md#salt_fertilizerfrt), `fertilizer.frt_cs` |
| Irrigation water | `salt_irrigation`, `cs_irrigation` |
| Urban runoff | `salt_urban`, `cs_urban` |
| Road salt (monthly, daily or annual amounts added to the top layer) | `salt_road` |
| Plant tolerance and stress options | `salt_plants` |
| Plant uptake | `salt_uptake`, `cs_uptake` |
| Reaction and sorption parameters | `cs_reactions` |
| Point sources | recall files (see [Recall and point sources](recall-point-sources.md)) |

## Aquifers, channels and water bodies

In the 1D aquifer, recharge adds salt and constituent mass; the salt chemistry, constituent reactions and sorption are applied; and baseflow and seepage remove mass at the concentration of the aquifer water (mass divided by groundwater volume). Channels, reservoirs and wetlands mix incoming mass with the stored water and release it with outflow. With gwflow, salts and constituents are transported between grid cells.

## Pathogens and heavy metals

[`constituents.cs`](../input-reference/cs.md#constituentscs) can also list pathogens and heavy metals.

Pathogens (bacteria and other microorganisms) are followed on foliage and in the top soil layer. Each day their number changes by first-order die-off minus growth, corrected for temperature:

$$N_d = N_{d-1}\,\exp\!\left(-(k_{die} - k_{grow})\,\theta^{\,T - 20}\right)$$

with the rates of [`pathogens.pth`](../input-reference/pth.md) for foliage or soil, $\theta$ = `t_adj` and $T$ the mean air temperature. Rain of at least 2.54 mm washes a fraction of the pathogens on foliage to the soil; pathogens then leave the top layer with percolation, surface runoff and sediment. In channels they die off over the travel time at `do_stream`, corrected to the water temperature. The pathogen routines of 62.0.1 do not form a complete model: the HRU routines use one [`pathogens.pth`](../input-reference/pth.md#pathogenspth) row for all pathogens, the runoff step removes all pathogens left in the top layer every day, and the channel die-off does not act on the routed water. [`pathogens.pth`](../input-reference/pth.md#behaviour-in-6201) lists these points.

Heavy metals are not transformed. They enter the network only from export coefficient and delivery ratio objects and move with the water as conservative loads (see [`metals`](../input-reference/mtl.md) and [Recall and point sources](recall-point-sources.md)).

## Related pages

- [Salt inputs](../input-reference/salt.md) and [constituent inputs](../input-reference/cs.md)
- [Nutrient cycling](nutrient-cycling.md) for the nitrate transport equations
- [Plant growth and land use management](plant-growth-lum.md) for plant stresses
- [Aquifers](aquifers.md), [Channels](channels.md), [Reservoirs and wetlands](reservoirs-wetlands.md)
- [Recall and point sources](recall-point-sources.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Pathogens: [`src/path_ls_process.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_process.f90) (die-off, growth, wash-off), [`src/path_ls_runoff.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_runoff.f90), [`src/path_ls_swrouting.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_swrouting.f90), channels [`src/ch_rtpath.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpath.f90); heavy metals: [`src/exco_read_hmet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_read_hmet.f90), [`src/dr_read_hmet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_read_hmet.f90)

    - Soil transport: [`src/salt_lch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_lch.f90), [`src/cs_lch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_lch.f90)
    - Salt chemistry: [`src/salt_chem_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_chem_hru.f90), [`src/salt_chem_soil_single.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_chem_soil_single.f90), [`src/salt_chem_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_chem_aqu.f90); solubility products in [`src/salt_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_data_module.f90)
    - Salinity stress: [`src/pl_waterup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_waterup.f90), [`src/pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90); options read in [`src/salt_plant_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_plant_read.f90)
    - Salt uptake: [`src/salt_uptake.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_uptake.f90), [`src/salt_uptake_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_uptake_read.f90); road salt: [`src/salt_roadsalt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_roadsalt.f90)
    - Selenium reactions: [`src/cs_rctn_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_rctn_hru.f90), [`src/se_reactions_soil.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/se_reactions_soil.f90); sorption: [`src/cs_sorb_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_sorb_hru.f90); parameters: [`src/cs_reactions_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_reactions_read.f90)
    - Aquifers: [`src/aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90), [`src/cs_rctn_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_rctn_aqu.f90), [`src/cs_sorb_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_sorb_aqu.f90)

    Symbols and variables:

    | Symbol or setting | Variable |
    |---|---|
    | $M_m$, concentration | `cs_soil%ly%salt`, `%saltc`; `cs_soil%ly%cs`, `%csc` |
    | $\theta_e$ | `soil%anion_excl` |
    | $\beta_N$ | `hru%nut%nperco` |
    | solubility products (soil, aquifer) | `Ksp11` to `Ksp51`, `Ksp12` to `Ksp52` |
    | $k_{EC}$, stress option, soil type, effect option | `salt_tds_ec`, `salt_tol_sim`, `salt_soil_type`, `salt_effect` |
    | $a$, $b$ | `salt_stress_a`, `salt_stress_b` |
    | $f_{salt}$ | `pcom%plstr%strss` |
    | salt uptake switch | `salt_uptake_on` |
    | selenium rates, inhibition, oxygen, shale | `cs_rct_soil%kseo4`, `%kseo3`, `%se_ino3`, `%oxy_soil`, `%shale`, `%ko2a`, `%kno3a` |
    | $K_d$ | `cs_rct_soil%kd_seo4`, `%kd_seo3`, `%kd_born` |

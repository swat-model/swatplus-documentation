---
title: Soil Carbon
description: The static soil organic matter model and the CENTURY-based carbon model in SWAT+, with the pools, rates and controls the carbon model uses.
status: review
verified_against:
  - src/basin_module.f90
  - src/hru_control.f90
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
  - src/cbn_zhang2.f90
  - src/cbn_surfrsd_decomp.f90
  - src/cbn_rsd_transfer.f90
  - src/nut_orgnc2.f90
  - src/fcgd.f90
  - src/soil_nutcarb_init.f90
  - src/plant_parm_read.f90
  - src/plant_data_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

The `carbon` column of [`codes.bsn`](../input-reference/codes-bsn.md) selects how SWAT+ handles soil organic matter:

| `carbon` | Model |
|---|---|
| 0 | Static model. Residue decomposes and organic N and P mineralise as in SWAT; soil carbon is not tracked as a state. See [Nutrient cycling](nutrient-cycling.md). |
| 1 | Reserved for C-FARM, which is not implemented. |
| 2 | Carbon model based on CENTURY (Parton et al., 1993, 1994) as implemented in SWAT-C by Zhang (2018). Carbon, nitrogen and phosphorus move through litter and soil organic matter pools in every soil layer. |

The carbon model is switched on by `carbon = 2`; earlier revisions used 1. With `carbon = 1` neither model runs, so residue does not decompose and organic N and P are not mineralised. Set the column to 0 or 2.

When `carbon = 2`, the files [`carbon.bsn`](../input-reference/carbon-bsn.md) (basin-wide settings) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) (rates and CO₂ fractions) are required, and the run stops if either is missing. The legacy [`carb_coefs.cbn`](../input-reference/cbn.md) file is no longer read.

## Pools

Each soil layer has three litter pools and three soil organic matter pools. Every pool contains mass, carbon, nitrogen and phosphorus.

| Pool | Content |
|---|---|
| Metabolic litter | Easily decomposed part of residue and manure |
| Structural litter | Resistant part of residue, of which a share is lignin |
| Lignin | Lignin within structural litter |
| Microbial biomass | Active microbes and their products |
| Slow humus | Organic matter with turnover times of years to decades |
| Passive humus | Stabilised organic matter with turnover times of centuries |

Surface residue is kept separately for each plant until it decomposes into the litter pools of the top soil layer.

Carbon moves between pools as follows. Each transfer releases part of the carbon as CO₂.

- structural litter (non-lignin part) and metabolic litter to microbial biomass
- lignin to slow humus (70 %; the other 30 % is respired)
- microbial biomass to slow humus and passive humus
- slow humus to microbial biomass and passive humus
- passive humus to microbial biomass

## Residue inputs

### Surface residue

Each plant's surface residue decomposes when the top soil layer is above 0 °C:

$$
\Delta R = \delta\,R, \qquad \delta = \min\left(1,\;\max\left(\delta_{min},\;k_{rsd}\;\gamma_{nut}\;\sqrt{\gamma_{tmp}\,\gamma_{sw}}\right)\right)
$$

$$
\gamma_{tmp} = \max\left(0.1,\;0.9\,\frac{T}{T + e^{9.93 - 0.312\,T}} + 0.1\right), \qquad \gamma_{sw} = \max\left(0.05,\;0.1 + 0.9\sqrt{SW/FC}\right)
$$

$$
\gamma_{nut} = \min\left(1,\;e^{-0.693\,(CN - CN_{ref})/CN_{ref}},\;e^{-0.693\,(CP - CP_{ref})/CP_{ref}}\right)
$$

| Symbol | Meaning | Input |
|---|---|---|
| $R$ | surface residue of a plant (mass, C, N, P) | |
| $k_{rsd}$ | residue decomposition coefficient of the plant | `plnt_decomp` in [`plants.plt`](../input-reference/plt.md) |
| $\delta_{min}$ | minimum daily decomposition fraction | `rsd_decay` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $T$, $SW$, $FC$ | top layer temperature (°C), soil water and field capacity (mm) | |
| $CN$, $CP$ | residue C:N and C:P ratios, capped at `cnr_cap` and `cpr_cap` | [`carbon.bsn`](../input-reference/carbon-bsn.md) |
| $CN_{ref}$, $CP_{ref}$ | ratios at which the factor is 1 | `cnr_ref`, `cpr_ref` in [`carbon.bsn`](../input-reference/carbon-bsn.md) |

The decomposed residue is added to the litter pools of the top soil layer. The plant's above-ground lignin fraction (`ab_lig_frac` in [`plants.plt`](../input-reference/plt.md)) goes to lignin, the lignin fraction divided by 0.8 goes to structural litter (lignin included), and the rest goes to metabolic litter.

Before decomposition, a fraction `sfc_rsd_photodeg` ([`carbon.bsn`](../input-reference/carbon-bsn.md)) of each plant's surface residue is lost each day to photodegradation and counted as emitted carbon.

### Roots and incorporated residue

Residue in the soil (dead roots and residue mixed in by tillage) is moved to the litter pools of its layer on each day the layer is above 0 °C, using the plant's below-ground lignin fraction (`bg_lig_frac` in [`plants.plt`](../input-reference/plt.md)) in the same way.

Manure adds to the litter pools according to the manure partitioning settings in [`carbon.bsn`](../input-reference/carbon-bsn.md).

## Pool transformations

### Environmental controls

The daily rate of every transformation in a layer is the optimal rate times a combined control factor:

$$
c_s = \min\left(15,\;0.9\,\sqrt{f_{tmp}\,f_{sw}}\;f_{ox}\;f_{till}\right)
$$

**Temperature** $f_{tmp}$ is chosen with `tmpf_eqn` in [`carbon.bsn`](../input-reference/carbon-bsn.md):

| `tmpf_eqn` | Function of layer temperature $T$ (°C) |
|---|---|
| 1 | $T/(T + e^{5.058 - 0.2504T})$ up to 35 °C, then $1 - 0.04(T - 35)$ up to 60 °C, then 0 |
| 2 | $\dfrac{(T - T_n)^{q}\,(T_x - T)}{(T_o - T_n)^{q}\,(T_x - T_o)}$ with $q = (T_n - T_o)/(T_o - T_x)$, and 0 outside $T_n < T < T_x$; $T_n$, $T_o$, $T_x$ are `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` |
| 3 | $0.9\,T/(T + e^{9.93 - 0.312T}) + 0.1$ |

**Soil water** $f_{sw}$ is chosen with `watf_eqn`:

| `watf_eqn` | Function |
|---|---|
| 1 | $0.1 + 0.9\sqrt{SW/FC}$, limited to 0.05 to 1 |
| 2 | Product of a water factor (rising from 0 at no water to 1 at field capacity) and an aeration factor based on the air-filled pore space; reduces activity in both dry and waterlogged soil |

**Oxygen** decreases with the depth $z$ (mm) of the middle of the layer:

$$
f_{ox} = 1 - \frac{0.8\,z}{z + e^{18.40961 - 0.023683632\,z}}
$$

**Tillage** $f_{till}$ depends on `idc_till` in [`codes.bsn`](../input-reference/codes-bsn.md):

| `idc_till` | Effect |
|---|---|
| 1 | $f_{till} = 1.6$ in layers within the tillage depth for `till_eff_days` days after tillage (partly in the layer containing the tillage depth), otherwise 1 |
| 2, 4 | No effect ($f_{till} = 1$) |
| 3 (default) | $f_{till}$ is 1 plus the layer tillage factor, which rises with each tillage operation and decays afterwards (Kemanian method) |

### Rates

Potential daily transformation of each pool is its carbon (and nitrogen) content times an optimal rate from [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md), times $c_s$:

| Pool | Daily fraction transformed | Rate column |
|---|---|---|
| Structural litter | $k_{str}\,c_s\,e^{-3\,L}$, where $L$ is the lignin share of structural litter (at most 0.8) | `str_rate` |
| Metabolic litter | $k_{meta}\,c_s$ | `meta_rate` |
| Microbial biomass | $k_{mic}\,c_s\,x_{bm}$, with $x_{bm} = 1$ in the top layer and $0.25 + 0.0075\,\text{sand}$ below | `microb_top_rate` (top layer), `microb_rate` |
| Slow humus | $k_{hs}\,c_s$ | `hs_rate` |
| Passive humus | $k_{hp}\,c_s$ | `hp_rate` |

[`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) has two rows: row 1 applies to the top soil layer and row 2 to all other layers.

### Allocation and CO₂

| Transfer | Fraction respired as CO₂ | Remainder goes to |
|---|---|---|
| Metabolic and non-lignin structural litter | `a1co2` | microbial biomass |
| Lignin | 0.3 | slow humus |
| Microbial biomass | `abco2` in the top layer; $0.17 + 0.0068\,\text{sand}$ below | passive humus ($0.003 + 0.00032\,\text{clay}$), rest to slow humus |
| Slow humus | `asco2` | passive humus (the larger of 0.001 and `hs_hp` minus 0.00009 × clay), rest to microbial biomass |
| Passive humus | `apco2` | microbial biomass |

Sand and clay are in percent.

### Nitrogen

Each receiving pool has a target N:C ratio. In the top layer these depend on the N content of the residue; in deeper layers they depend on the mineral N concentration of the layer. When the N released by the decomposing pools is less than the N needed to build the receiving pools, the difference is immobilised from soil nitrate and ammonium. If mineral N cannot cover it, the transformations that need N are reduced in proportion. Surplus N is mineralised to ammonium.

Before the transformations, denitrification removes nitrate when the soil water factor exceeds `denit_frac` in [`parameters.bsn`](../input-reference/parameters-bsn.md), at a rate set by `denit_exp`, the temperature factor and the layer organic carbon.

### Phosphorus

Phosphorus is mineralised from passive humus at 1.4 times the fraction of humus N that was transformed on the day, and goes to the labile mineral pool. Phosphorus in decomposing litter is released in proportion to the litter carbon transformed: 80 % to labile mineral P and 20 % to passive humus.

## Carbon in water and sediment

- Sediment: eroded soil removes organic carbon from the top layer in proportion to the share of the layer mass eroded (at most 90 %).
- Dissolved carbon from microbial biomass: in the top layer, microbial carbon is lost to water leaving the layer with $1 - \exp\left(-w/(SAT + 10^{-4}\,K_{oc}\,C)\right)$, where $w$ is runoff plus lateral flow plus percolation, $K_{oc}$ is `koc_c` and $C$ the layer organic carbon. The concentration in surface runoff and lateral flow is `solc_ratio` times the concentration in percolation. In deeper layers, carbon moving with percolation and lateral flow is removed with $1 - \exp(-w/(\phi z - WP))$.
- Carbon leaving the bottom of the profile is reported as percolated carbon.

## Initial pools

At the start of the run, the organic carbon of each layer (from [`soils.sol`](../input-reference/sol.md)) is split into pools. A share `init_seq` is humus and microbial carbon, divided between microbial biomass (`init_microb`), slow humus (`init_slow`) and passive humus (`init_passive`). Humus pools start with C:N of 10 and C:P of 80; microbial biomass with C:N of 8 and C:P of 80. With `mathers_method = 1`, slow humus is initialised with the Mathers relation based on clay plus silt content.

## Parameters

| Parameter | File | Effect |
|---|---|---|
| `carbon` | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = static, 1 = reserved, 2 = carbon model |
| `idc_till` | [`codes.bsn`](../input-reference/codes-bsn.md) | Tillage effect on decomposition (default 3) |
| `tmpf_eqn`, `watf_eqn`, `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Temperature and soil water controls |
| `till_eff_days`, `bmix_*`, `tillmix_*`, `bio_consol`, `till_consol` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Duration and shape of tillage and biological mixing effects |
| `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref`, `sfc_rsd_photodeg` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Surface residue decomposition |
| `koc_c`, `solc_ratio` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Dissolved carbon losses |
| `init_seq`, `init_microb`, `init_slow`, `init_passive`, `mathers_method` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Initial pool split |
| `hp_rate`, `hs_rate`, `microb_rate`, `microb_top_rate`, `meta_rate`, `str_rate` | [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) | Optimal transformation rates (1/day) |
| `hs_hp`, `a1co2`, `asco2`, `apco2`, `abco2` | [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) | Allocation and CO₂ fractions |
| `plnt_decomp`, `ab_lig_frac`, `bg_lig_frac` | [`plants.plt`](../input-reference/plt.md) | Residue decomposition rate and lignin fractions |

Carbon model parameters can be calibrated through the parameter change files; see [Parameter change files](../calibration/parameter-change-files.md).

## Related pages

- [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md)
- [Carbon outputs](../output-reference/carbon.md)
- [Nutrient cycling](nutrient-cycling.md) for the static model
- [Plant growth and land use management](plant-growth-lum.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Model switch: `cswat` in [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90); daily calls in [`src/hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Inputs: [`src/carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90) (reads `carbon.bsn` and `carbon_lyr.bsn`), types in [`src/carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90)
    - Pool transformations: [`src/cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90); temperature option 2: [`src/fcgd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/fcgd.f90)
    - Residue: [`src/cbn_surfrsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_surfrsd_decomp.f90), [`src/cbn_rsd_transfer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_rsd_transfer.f90); lignin partitioning in [`src/plant_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_parm_read.f90)
    - Carbon in runoff, sediment and percolation: [`src/nut_orgnc2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_orgnc2.f90)
    - Initial pools: [`src/soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90)
    - Tillage: [`src/mgt_newtillmix_cswat1.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_cswat1.f90), [`src/mgt_tillfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_tillfactor.f90), [`src/mgt_biomix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_biomix.f90)

    Symbols and variables:

    | Symbol or column | Variable |
    |---|---|
    | `carbon` in `codes.bsn` | `bsn_cc%cswat` |
    | $c_s$, $f_{tmp}$, $f_{sw}$, $f_{ox}$, $f_{till}$ | `org_con%cs`, `%cdg`, `%sut`, `%ox`, `%till_eff` |
    | `tmpf_eqn`, `watf_eqn`, `t_cbn_min/opt/max` | `org_con%tmpf`, `%watf`, `%tn`, `%top`, `%tx` |
    | `koc_c`, `solc_ratio` | `cb_wtr_coef%prmt_21`, `cb_wtr_coef%prmt_44` |
    | `init_seq`, `init_microb`, `init_slow`, `init_passive` | `org_frac%frac_seq`, `%frac_hum_microb`, `%frac_hum_slow`, `%frac_hum_passive` |
    | rates in `carbon_lyr.bsn` | `carbdb(1:2)%hp_rate`, `%hs_rate`, `%microb_rate`, `%microb_top_rate`, `%meta_rate`, `%str_rate`, `%hs_hp` |
    | CO₂ fractions | `org_allo(1:2)%a1co2`, `%asco2`, `%apco2`, `%abco2` |
    | microbial to passive, slow to passive | `org_allo%abp`, `org_allo%asp` |
    | pools | `soil1%meta`, `%str`, `%lig`, `%microb`, `%hs`, `%hp` |
    | lignin fractions of residue | `cswat_1_part_fracs%lig_frac_abg`, `%lig_frac_blg` (from `pldb%res_part_fracs%str_frac` and `%lig_frac`) |

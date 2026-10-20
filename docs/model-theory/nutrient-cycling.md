---
title: Nutrient Cycling (N and P)
description: Soil nitrogen and phosphorus pools, mineralisation, decomposition, nitrification, volatilisation, denitrification, deposition and losses in runoff, sediment, lateral flow, tile flow and percolation in SWAT+.
status: review
verified_against:
  - src/hru_control.f90
  - src/soil_nutcarb_init.f90
  - src/soil_data_module.f90
  - src/carbon_module.f90
  - src/rsd_decomp.f90
  - src/nut_nminrl.f90
  - src/nut_nitvol.f90
  - src/nut_nrain.f90
  - src/nut_nlch.f90
  - src/nut_orgn.f90
  - src/nut_psed.f90
  - src/nut_solp.f90
  - src/nut_pminrl.f90
  - src/nut_pminrl2.f90
  - src/pest_enrsb.f90
  - src/et_act.f90
  - src/swr_substor.f90
  - src/stor_surfstor.f90
  - src/hrudb_init.f90
  - src/sd_channel_control3.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

SWAT+ follows nitrogen and phosphorus through mineral, organic and plant pools in every soil layer. Fertiliser, manure, residue and atmospheric deposition add nutrients; plants take them up; and runoff, sediment, lateral flow, tile flow, percolation, denitrification and volatilisation remove them. The nutrients that leave the HRU are routed through channels, where in-stream processes are described on the [Channels](channels.md) page.

The soil processes below are those of the static carbon option (`carbon = 0` in [`codes.bsn`](../input-reference/codes-bsn.md)). With `carbon = 2` the residue and humus pools and their decomposition follow the CENTURY-based model on the [Carbon](carbon.md) page, while nitrification, volatilisation, mineral phosphorus, deposition and all the transport processes below stay the same. `carbon = 1` is reserved for C-FARM, which is not implemented; with it SWAT+ 62.0.1 skips residue decomposition and mineralisation altogether.

Plant uptake and nitrogen fixation are described in [Plant growth and land use management](plant-growth-lum.md).

## Soil pools

| Element | Pool | Contents |
|---------|------|----------|
| N | Nitrate | NO3-N in solution, mobile with water |
| N | Ammonium | NH4-N, adsorbed on the soil |
| N | Active humus N | The part of humus organic N that mineralises |
| N | Stable humus N | The rest of humus organic N |
| N | Residue N | Organic N in fresh residue, kept separately for each plant in each layer and on the surface |
| P | Labile (solution) P | Soluble mineral P available to plants and mobile with water |
| P | Active mineral P | Mineral P in rapid equilibrium with labile P |
| P | Stable mineral P | Mineral P in slow equilibrium with active P |
| P | Humus organic P | Organic P in humus |
| P | Residue P | Organic P in fresh residue |

Manure applied to the soil has separate organic pools, which are also lost with sediment.

### Initial values

The initial nutrient contents come from the row of [`nutrients.sol`](../input-reference/ini.md#nutrientssol) named for the HRU in [`soil_plant.ini`](../input-reference/ini.md#soil_plantini), with built-in values when there is none:

| Pool | Initial value |
|------|---------------|
| Nitrate | `nitrate` (7 mg/kg) at the surface, decreasing with depth as $\exp(-\mathrm{exp\_co}\,z)$, with $z$ the depth to the bottom of the layer in mm |
| Labile P | `lab_p` (5 mg/kg) at the surface, decreasing with depth the same way |
| Active mineral P | Labile P × (1 − PSP)/PSP |
| Stable mineral P | 4 × active P; with the Vadas and White P model, from the White et al. (2009) ratio of 1 to 7 times active plus labile P |
| Humus C, N and P | Humus C from the organic carbon of the layer (`carbon` in [`soils.sol`](../input-reference/sol.md)); N and P from the humus C:N and C:P ratios `hum_c_n` (10) and `hum_c_p` (80) |
| Active and stable humus | `fr_hum_act` (0.02) of humus in the active pool |

Concentrations in mg/kg are converted to kg/ha with the bulk density and thickness of each layer. The other soil test columns of [`nutrients.sol`](../input-reference/ini.md#nutrientssol) (`inorgp`, `watersol_p`, `h3a_p`, `mehlich_p`, `bray_strong_p`) are not used.

## Temperature and water factors

Mineralisation, decomposition and denitrification depend on soil temperature and water through two factors:

$$\gamma_{tmp} = \max\left(0.1,\; 0.9\,\frac{T_{soil}}{T_{soil} + \exp(9.93 - 0.312\,T_{soil})} + 0.1\right), \qquad \gamma_{sw} = \max\left(0.05,\; 0.1 + 0.9\sqrt{\frac{SW_{ly}}{FC_{ly}}}\right)$$

where $T_{soil}$ is the layer temperature (°C), $SW_{ly}$ the layer water and $FC_{ly}$ its field capacity water. They combine as $\gamma = \sqrt{\gamma_{tmp}\,\gamma_{sw}}$. None of these processes runs in a layer at or below 0 °C. For the 10 mm surface layer, SWAT+ uses the temperature and water content of the second layer.

## Humus mineralisation

Nitrogen moves between the active and stable humus pools towards a fixed active fraction:

$$N_{trns} = 10^{-5}\left[orgN_{act}\left(\frac{1}{fr_{actN}} - 1\right) - orgN_{sta}\right]$$

where $fr_{actN}$ is `n_act_frac` in [`carbon.bsn`](../input-reference/carbon-bsn.md) (0.02). A positive value moves N from active to stable humus.

Active humus N mineralises to nitrate:

$$N_{mina} = \beta_{min}\,\gamma\,orgN_{act}$$

with $\beta_{min}$ the rate coefficient for humus mineralisation, `orgn_min` in [`parameters.bsn`](../input-reference/parameters-bsn.md). Phosphorus is mineralised from humus in proportion:

$$P_{mina} = 1.4\,N_{mina}\,\frac{orgP_{hum}}{orgN_{act} + orgN_{sta}}$$

and added to the labile pool.

## Residue decomposition

Fresh residue decomposes at a rate limited by its C:N and C:P ratios. For each plant's residue in each layer,

$$\gamma_{ntr} = \min\left(\exp\left[-0.693\,\frac{\varepsilon_{C:N} - 25}{25}\right],\; \exp\left[-0.693\,\frac{\varepsilon_{C:P} - 200}{200}\right],\; 1\right)$$

with $\varepsilon_{C:N}$ capped at 500 and $\varepsilon_{C:P}$ at 5000. The fraction decomposed on the day is

$$\delta_{ntr} = \min\left[1,\; \max\left(\mathrm{rsd\_decay},\; \beta_{rsd}\,\gamma_{ntr}\,\gamma\right)\right]$$

where $\beta_{rsd}$ is the residue decomposition coefficient of the plant (`plnt_decomp` in [`plants.plt`](../input-reference/plt.md)) and `rsd_decay` in [`parameters.bsn`](../input-reference/parameters-bsn.md) is a minimum daily rate. Of the N and P released, 80% goes to nitrate and labile P, and 20% to humus (active humus N; stable humus P for soil residue, active humus P for surface residue).

Surface residue decomposes the same way, using the temperature and water of the top layer.

## Nitrification and ammonia volatilisation

Ammonium is nitrified and volatilised together in each layer (Reddy et al., 1979; Godwin et al., 1984). The temperature factor is

$$\eta_{tmp} = 0.41\,\frac{T_{soil} - 5}{10}$$

and both processes need $\eta_{tmp} \ge 0.001$. The water factor for nitrification rises linearly from 0 at wilting point to 1 at wilting point plus 25% of the field capacity water. Volatilisation decreases with depth through

$$\eta_{midz} = 1 - \frac{z_{mid}}{z_{mid} + \exp(4.706 - 0.0305\,z_{mid})}$$

with $z_{mid}$ the depth to the middle of the layer (mm), and uses a cation exchange factor of 0.15. With $\eta_{nit} = \eta_{tmp}\,\eta_{sw}$ and $\eta_{vol} = 0.15\,\eta_{tmp}\,\eta_{midz}$, the ammonium lost to both is

$$N_{nit|vol} = NH_4\left[1 - \exp(-\eta_{nit} - \eta_{vol})\right]$$

and is split between nitrification and volatilisation in proportion to $1 - \exp(-\eta_{nit})$ and $1 - \exp(-\eta_{vol})$.

## Denitrification

When the water factor reaches a threshold, nitrate in the layer is denitrified:

$$N_{denit} = NO_3\left[1 - \exp\left(-\beta_{denit}\,\gamma_{tmp}\,\frac{orgC}{100}\right)\right] \quad\text{for } \gamma_{sw} \ge \gamma_{sw,thr}$$

| Symbol | Meaning | Input |
|--------|---------|-------|
| $\beta_{denit}$ | Denitrification rate coefficient | `denit_exp` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $\gamma_{sw,thr}$ | Threshold of the water factor | `denit_frac` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $orgC$ | Organic carbon of the layer | `carbon` in [`soils.sol`](../input-reference/sol.md), % |

The septic biozone layer of an active septic system is excluded.

## Atmospheric deposition

Nitrate and ammonium in rain and dry deposition are added to the surface layer every day from the station named in the `atmo_dep` column of [`weather-sta.cli`](../input-reference/cli.md#weather-stacli). Rain deposition is the concentration in rain (mg/L) times the day's precipitation; dry deposition is spread evenly over the days of the month or year, depending on whether [`atmodep.cli`](../input-reference/cli.md#atmodepcli) gives monthly, yearly or average annual values.

## Nitrate movement

Nitrate is mobile and moves with water. In each layer the water that moves is the percolation, lateral flow, surface runoff (top layer only) and tile flow (tile layer only), $w_{mobile}$. The nitrate concentration in the mobile water is

$$conc_{NO_3} = \frac{NO_3\left[1 - \exp\left(\dfrac{-w_{mobile}}{(1 - \theta_e)\,SAT_{ly}}\right)\right]}{w_{mobile}}$$

where $\theta_e$ is the fraction of porosity from which anions are excluded (`anion_excl` in [`soils.sol`](../input-reference/sol.md)) and $SAT_{ly}$ the saturation water of the layer. Then:

| Path | Nitrate removed |
|------|-----------------|
| Surface runoff | $\beta_{NO_3}\,conc_{NO_3}\,Q_{surf}$, top layer, with $\beta_{NO_3}$ = `n_perc` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| Lateral flow | $conc_{NO_3}\,Q_{lat,ly}$ for each layer |
| Tile flow | `nperco_lchtile` × concentration in the tile flow × $Q_{tile}$, with the concentration taken over the tile layer and all layers below |
| Percolation | $conc_{NO_3}\,w_{perc,ly}$, added to the next layer; from the bottom layer it leaves the profile |

`n_perc` close to 0 gives little nitrate in surface runoff; close to 1 gives runoff the same concentration as percolate. As water evaporates from the second layer, a small amount of nitrate moves up with it into the surface layer.

Nitrate in lateral and tile flow passes through the same lag stores as the water (see [Hydrology](hydrology.md)). When the gwflow module passes groundwater into the soil profile, it also adds the nitrate and phosphorus that the groundwater contains.

## Organic N and P with sediment

Organic nitrogen leaving with sediment is

$$orgN_{surf} = 1000\,\frac{orgN_{ly1}}{M_{ly1}}\,\varepsilon_N\,\frac{sed}{A}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $orgN_{surf}$ | Organic N removed in sediment | kg N/ha |
| $orgN_{ly1}$ | Active plus stable humus N in the surface layer | kg N/ha |
| $M_{ly1}$ | Mass of the surface layer, $10000\,\rho_b\,depth$ | kg/ha |
| $\varepsilon_N$ | Nitrogen enrichment ratio | - |
| $sed$ | Sediment yield | metric tons |
| $A$ | HRU area | ha |

Sediment-attached phosphorus is computed the same way from the humus, manure and active and stable mineral P of the surface layer, using $\varepsilon_P$, and is reported as organic P and mineral P.

The enrichment ratio accounts for the finer, nutrient-rich particles that erosion removes. It is `orgn_enrich` (N) or `orgp_enrich` (P) in [`hydrology.hyd`](../input-reference/hyd.md) when that is above 0.001. Otherwise it is computed from the sediment concentration in runoff (Menzel, 1980):

$$\varepsilon = 0.78\,(conc_{sed})^{-0.2468}, \qquad conc_{sed} = \frac{sed}{10\,A\,Q_{surf}}, \qquad \varepsilon \le 3$$

## Soluble phosphorus

Labile phosphorus is strongly bound by the soil, so little of it moves with water. The amount removed in surface runoff is

$$P_{surf} = \frac{P_{lab,1}\,Q_{surf}}{\rho_b\,depth_1\,k_{d,surf} + 1}$$

where $P_{lab,1}$ is the labile P of the surface layer (kg/ha), $\rho_b$ and $depth_1$ its bulk density and thickness (mm), and $k_{d,surf}$ the phosphorus soil partitioning coefficient, `p_soil` in [`parameters.bsn`](../input-reference/parameters-bsn.md) (m³/Mg).

Leaching of labile P from each layer to the next is

$$P_{perc} = 0.001\,P_{lab}\left[1 - \exp\left(\frac{-w_{perc}}{0.01\,SW_{ly} + 0.1\,k_{d,perc}\,\rho_b}\right)\right]$$

with $k_{d,perc}$ the phosphorus percolation coefficient `p_perc` in [`parameters.bsn`](../input-reference/parameters-bsn.md). The same expression with tile flow in place of percolation gives the P in tile flow from the tile layer. This form differs from the SWAT 2009 leaching equation.

## Mineral phosphorus transformations

### Original model

With `soil_p = 0` in [`codes.bsn`](../input-reference/codes-bsn.md), labile and active mineral P move towards the ratio set by the phosphorus availability index $pai$ (`p_avail` in [`parameters.bsn`](../input-reference/parameters-bsn.md)):

$$P_{sol|act} = P_{lab} - P_{act}\,\frac{pai}{1 - pai}$$

Movement from labile to active P takes 10% of the imbalance per day; movement back takes 60%. Active and stable P move towards a stable pool four times the active pool:

$$P_{act|sta} = 0.01\,(4\,P_{act} - P_{sta})$$

with a tenth of that rate when stable P returns to the active pool.

### Vadas and White model

With `soil_p = 1`, SWAT+ uses the phosphorus model of Vadas and White (2010). The availability index is computed for each layer from clay content, labile P and organic carbon, and averaged over 30 days. The rate of movement between labile and active P depends on how many days the imbalance has lasted. The active to stable equilibrium ratio follows the White et al. (2009) relationship, and the active to stable rate depends on the calcium carbonate content (`caco3` in [`soils.sol`](../input-reference/sol.md)). Both rates are scaled by the water content of the layer relative to field capacity, with a lower limit of 0.25.

## Lag of nutrients in surface runoff

Nitrate and labile P in surface runoff, organic N and P, and mineral P attached to sediment pass through the surface lag store with the runoff and sediment, and the same daily fraction is released (see [Hydrology](hydrology.md)).

## Algae, CBOD and dissolved oxygen in runoff

Each day SWAT+ also gives the water leaving an HRU a chlorophyll-a, carbonaceous BOD and dissolved oxygen load, which the channels then use as inflow concentrations. On days without water yield all three are zero. With water yield $Q$ (surface runoff, lateral flow and tile flow, mm):

- Chlorophyll-a is 0.1 times the concentration of organic N in sediment plus nitrate in surface runoff, $100\,(N_{org,sed} + NO_{3,surq})/Q$.
- CBOD is 2.7 times the organic carbon in the day's sediment yield, divided by the water yield. The carbon is the soil carbon content of the top layer times the sediment yield and the enrichment ratio, or, with `carbon` = 2 in [`codes.bsn`](../input-reference/codes-bsn.md), the carbon the carbon model reports in the sediment.
- Dissolved oxygen is $O_{sat}\,e^{-0.1\,CBOD}$, limited to between 0 and $O_{sat}$, with $O_{sat}$ the saturation concentration at a water temperature of $5 + 0.75\,\bar{T}_{air}$ (see [Channels](channels.md#nitrogen-phosphorus-cbod-and-oxygen) for the formula).

## Septic systems

A land use with a septic system (the `sep` column of [`landuse.lum`](../input-reference/lum.md)) adds a biozone layer to the soil, and the biozone routine runs on days when that layer is above freezing. In 62.0.1 the effluent volume is never computed, so septic systems add no water, nitrogen, phosphorus or BOD to the soil. See [`septic.str`](../input-reference/str.md#septicstr) for the inputs.

## In-stream processes

Nutrients entering channels are transformed by the QUAL2E water quality routines. With `i_fpwet = 1` in [`codes.bsn`](../input-reference/codes-bsn.md) (the column read as the QUAL2E switch), a simplified exchange between dissolved and particulate N and P is added. See [Channels](channels.md).

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `carbon` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` static pools, `2` CENTURY-based carbon, `1` reserved |
| `soil_p` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` original mineral P model, `1` Vadas and White (2010) |
| `orgn_min` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Humus mineralisation rate coefficient |
| `rsd_decay` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Minimum daily residue decomposition |
| `denit_exp`, `denit_frac` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Denitrification rate and water threshold |
| `n_perc` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Nitrate in surface runoff relative to percolate |
| `nperco_lchtile` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Nitrate concentration coefficient for tile flow |
| `p_soil`, `p_perc` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Phosphorus partitioning in runoff and percolation |
| `p_avail` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Phosphorus availability index (original model) |
| `n_act_frac` | [`carbon.bsn`](../input-reference/carbon-bsn.md) | Active fraction of humus N |
| `orgn_enrich`, `orgp_enrich` | [`hydrology.hyd`](../input-reference/hyd.md) | Fixed enrichment ratios |
| `plnt_decomp` | [`plants.plt`](../input-reference/plt.md) | Residue decomposition coefficient of each plant |
| `nitrate`, `lab_p`, `exp_co`, `fr_hum_act`, `hum_c_n`, `hum_c_p` | [`nutrients.sol`](../input-reference/ini.md#nutrientssol) | Initial nutrient contents |
| `carbon`, `anion_excl`, `caco3` | [`soils.sol`](../input-reference/sol.md) | Organic carbon, anion exclusion, CaCO3 |

`orgn_min`, `n_perc`, `nperco_lchtile`, `p_soil`, `p_perc` and `p_avail` are copied to every HRU at the start of the run, so calibration can change them for single HRUs.

## Related pages

- [Plant growth and land use management](plant-growth-lum.md) for uptake and fixation.
- [Carbon](carbon.md) for the CENTURY-based pools.
- [Erosion and sediment](erosion-sediment.md) for the sediment yield that transports organic nutrients.
- [`fertilizer.frt`](../input-reference/frt.md) and [manure allocation](../input-reference/manure-allocation.md) for nutrient inputs.
- [Channels](channels.md) for in-stream processes.

??? quote "Sources"

    - Daily sequence and carbon switch: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Initial pools: [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90); `type soiltest_db` in [`soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_data_module.f90)
    - Mineralisation, soil residue decomposition, denitrification: [`nut_nminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nminrl.f90); surface residue: [`rsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rsd_decomp.f90)
    - Nitrification and volatilisation: [`nut_nitvol.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nitvol.f90)
    - Deposition: [`nut_nrain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nrain.f90)
    - Nitrate movement: [`nut_nlch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nlch.f90); upward nitrate with evaporation in [`et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90)
    - Sediment-bound nutrients: [`nut_orgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_orgn.f90), [`nut_psed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_psed.f90); enrichment ratio: [`pest_enrsb.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_enrsb.f90)
    - Soluble P: [`nut_solp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_solp.f90); mineral P: [`nut_pminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_pminrl.f90), [`nut_pminrl2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_pminrl2.f90)
    - Chlorophyll-a, CBOD and dissolved oxygen in HRU runoff: [`swr_subwq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_subwq.f90) (`chl_a`, `cbodu`, `doxq`; the code labels the organic N plus nitrate concentration `tp`), passed to the HRU outflow in [`hru_hyds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_hyds.f90)
    - Septic biozone: [`sep_biozone.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sep_biozone.f90), called from `hru_control.f90`; set up in `soils_init.f90`
    - Lag stores: [`swr_substor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_substor.f90), [`stor_surfstor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/stor_surfstor.f90)
    - HRU copies of basin nutrient parameters: [`hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90)
    - `n_act_frac`: [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90)

    | Column or symbol | Fortran variable |
    |------------------|------------------|
    | `carbon`, `soil_p`, `i_fpwet` (codes.bsn) | `bsn_cc%cswat`, `bsn_cc%sol_p_model`, `bsn_cc%qual2e` |
    | `orgn_min` ($\beta_{min}$) | `bsn_prm%cmn`, per HRU `hru(j)%nut%cmn` |
    | `rsd_decay` | `bsn_prm%decr_min` |
    | `denit_exp`, `denit_frac` | `bsn_prm%cdn`, `bsn_prm%sdnco` |
    | `n_perc`, `nperco_lchtile` | `hru(j)%nut%nperco`, `hru(j)%nut%nperco_lchtile` |
    | `p_soil`, `p_perc`, `p_avail` | `hru(j)%nut%phoskd`, `hru(j)%nut%pperco`, `hru(j)%nut%psp` |
    | `orgn_enrich`, `orgp_enrich` | `hru(j)%hyd%erorgn`, `hru(j)%hyd%erorgp` |
    | `plnt_decomp` | `pldb%rsdco_pl` |
    | Nitrate, ammonium | `soil1(j)%mn(ly)%no3`, `%nh4` |
    | Active and stable humus | `soil1(j)%hact(ly)`, `soil1(j)%hsta(ly)` |
    | Labile, active, stable mineral P | `soil1(j)%mp(ly)%lab`, `%act`, `%sta` |
    | Residue in soil, on surface | `soil1(j)%pl(ipl)%rsd(ly)`, `pl_mass(j)%rsd(ipl)` |
    | $\gamma_{tmp}$, $\gamma_{sw}$, $\gamma$ | `cdg`, `sut`, `csf` |
    | $\varepsilon$ (computed) | `enratio` |
    | Nitrate in runoff, lateral, tile, percolation | `surqno3(j)`, `latno3(j)`, `tileno3(j)`, `percn(j)` |
    | Sediment-bound N and P | `sedorgn(j)`, `sedorgp(j)`, `sedminpa(j)`, `sedminps(j)` |
    | Soluble P in runoff | `surqsolp(j)` |

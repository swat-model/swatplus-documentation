---
title: Plant Growth and Land Use Management
description: Heat units, light interception, biomass, leaf area, roots, stresses, nutrient uptake and harvest in SWAT+, and how land use, management schedules and decision tables drive operations.
status: review
verified_against:
  - src/hru_control.f90
  - src/plant_init.f90
  - src/pl_community.f90
  - src/pl_grow.f90
  - src/pl_nut_demand.f90
  - src/pl_biomass_gro.f90
  - src/pl_leaf_gro.f90
  - src/pl_leaf_senes.f90
  - src/pl_root_gro.f90
  - src/pl_seed_gro.f90
  - src/pl_dormant.f90
  - src/pl_waterup.f90
  - src/pl_tstr.f90
  - src/pl_nupd.f90
  - src/pl_nup.f90
  - src/pl_nfix.f90
  - src/pl_pupd.f90
  - src/pl_pup.f90
  - src/nuts.f90
  - src/mgt_operatn.f90
  - src/mgt_sched.f90
  - src/mgt_read_mgtops.f90
  - src/mgt_harvgrain.f90
  - src/mgt_harvbiomass.f90
  - src/mgt_operations_module.f90
  - src/plant_data_module.f90
  - src/basin_prm_default.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Each HRU has a plant community: one or more plants listed in [`plant.ini`](../input-reference/ini.md#plantini) and described in [`plants.plt`](../input-reference/plt.md). SWAT+ grows every living plant of the community each day with a simplified version of the EPIC plant growth model. Phenological development follows accumulated heat units. Potential growth comes from intercepted light and the radiation use efficiency of the plant, and is reduced by water, temperature, nitrogen, phosphorus, aeration and (when salts are simulated) salinity stress. Growth removes water and nutrients from the soil, and harvest, kill and senescence return plant material to the residue and soil pools.

Plants are planted, harvested and killed by the management schedule of the HRU and by decision tables (see [Land use management](#land-use-management)).

## Plant types

The `plnt_typ` column of [`plants.plt`](../input-reference/plt.md) sets how a plant develops:

| `plnt_typ` | Behaviour |
|------------|-----------|
| `warm_annual`, `warm_annual_tuber` | Annual; leaf area declines towards the end of the season |
| `cold_annual`, `cold_annual_tuber` | Annual; goes dormant in winter if planted late enough |
| `perennial` | Grows over several years towards maturity (`yrs_mat`); goes dormant each year |

The `gro_trig` column sets what restarts growth: `temp_gro` for plants driven by temperature and day length, `moisture_gro` for plants in climates with a wet and dry season, where growth follows the ratio of precipitation to PET.

## Heat units

Plants develop at a rate set by temperature. Each day a plant above its base temperature accumulates heat units:

$$HU = \bar{T} - T_{base} \quad\text{when } \bar{T} > T_{base}$$

and the fraction of potential heat units reached is

$$fr_{PHU} = \sum_{i=1}^{d}\frac{HU_i}{PHU}$$

| Symbol | Meaning | Input |
|--------|---------|-------|
| $\bar{T}$ | Mean air temperature of the day | °C |
| $T_{base}$ | Minimum (base) temperature for growth | `tmp_base` in [`plants.plt`](../input-reference/plt.md), °C |
| $PHU$ | Potential heat units needed to bring the plant to maturity | see below |

$fr_{PHU}$ starts at 0 at planting and reaches 1 at maturity. SWAT+ sets PHU for each plant at the start of the run from the long-term monthly temperatures of the weather generator station and `days_mat` in [`plants.plt`](../input-reference/plt.md):

- `days_mat` > 0: the heat units accumulated over `days_mat` days, starting from an estimated planting date. For annuals the planting date is taken where base-zero heat units reach 15% of their annual total.
- `days_mat` = 0: 95% of the heat units above $T_{base}$ in a whole year, so the plant can stay active through the entire growing season.

For perennials a second counter runs over the years to maturity, with $PHU \times$ `yrs_mat` as its target. It sets canopy height and root depth.

Base-zero heat units ($T_{base} = 0$, divided by the annual total) are also accumulated each year from 1 January. They schedule operations that happen when no plant is growing.

## Dormancy

Perennials and cold-season annuals go dormant when the day length falls below the minimum day length of the station plus a threshold. While dormant a plant does not grow. When a perennial goes dormant its seed mass is moved to residue and its heat unit counter is reset; it starts accumulating heat units again when the day length rises above the threshold. Cold-season annuals go dormant only if they have reached less than 75% of their heat units.

## Light interception and biomass

Each growing plant intercepts photosynthetically active radiation (PAR), taken as half of incoming solar radiation, according to Beer's law:

$$H_{phosyn} = 0.5\,H_{day}\left[1 - \exp\left(-k_\ell\,(LAI + 0.05)\right)\right]$$

where $H_{day}$ is the solar radiation (MJ/m²), $k_\ell$ the light extinction coefficient (`ext_co` in [`plants.plt`](../input-reference/plt.md)) and $LAI$ the leaf area index of the plant. Each plant intercepts light as though it were alone: SWAT+ 62.0.1 has a routine for competition for light between taller and shorter plants, but it is switched off.

### Radiation use efficiency

The radiation use efficiency (RUE) is the biomass produced per unit of intercepted light. It responds to CO2 (Stockle et al., 1992). When `co2` in [`parameters.bsn`](../input-reference/parameters-bsn.md) is above 350 ppm,

$$RUE = \frac{100\,CO_2}{CO_2 + \exp(r_1 - r_2\,CO_2)}$$

where $r_1$ and $r_2$ are fitted so that RUE equals `bm_e` at 330 ppm and `bm_e_hi` at `co2_hi`. Otherwise RUE is `bm_e`. $CO_2$ is the concentration for the year (see [Climate and weather](climate-weather.md)).

When the vapour pressure deficit $vpd$ is above 1 kPa, RUE declines:

$$RUE = RUE - \Delta ruedcl_{vpd}\,(vpd - 1), \qquad RUE \ge 0.27\,\mathrm{bm\_e}$$

where $\Delta ruedcl_{vpd}$ is `ru_vpd` in [`plants.plt`](../input-reference/plt.md).

### Biomass growth

Potential daily biomass growth is $\Delta bio = RUE \times H_{phosyn}$ (kg/ha). The actual growth is

$$\Delta bio_{act} = \Delta bio\;\gamma_{reg}, \qquad \gamma_{reg} = \min\left(\gamma_w,\;\gamma_t,\;\gamma_n,\;\gamma_p,\;\gamma_a,\;\gamma_s\right)$$

where each $\gamma$ is a growth factor between 0 (no growth) and 1 (no stress) for water, temperature, nitrogen, phosphorus, aeration and salinity. When salinity is simulated with the salt tolerance option, the salinity factor multiplies the minimum of the others instead. Plant carbon is taken as 42% of biomass. `nostress` in [`codes.bsn`](../input-reference/codes-bsn.md) turns stresses off: `1` sets all factors to 1 and `2` sets only the nitrogen and phosphorus factors to 1.

The new biomass is split into roots, leaves, stems and seed. The root fraction falls from `rt_st_beg` at the start of the season to `rt_st_end` at maturity (for perennials, over the first 20% of the years to maturity).

## Leaf area and canopy

### Leaf area development

Leaf area follows an optimal curve defined by two points from [`plants.plt`](../input-reference/plt.md): at `frac_hu1` of the heat units the plant reaches `lai_max1` of its maximum LAI, and at `frac_hu2` it reaches `lai_max2`. The fraction of maximum LAI for a given $fr_{PHU}$ is

$$fr_{LAImx} = \frac{fr_{PHU}}{fr_{PHU} + \exp(\ell_1 - \ell_2\,fr_{PHU})}$$

with the shape coefficients $\ell_1$ and $\ell_2$ fitted to the two points. Until $fr_{PHU}$ reaches `hu_lai_decl`, the leaf area added on a day is

$$\Delta LAI = \left(fr_{LAImx,i} - fr_{LAImx,i-1}\right)LAI_{mx}\left[1 - \exp\left(5\,(LAI_{i-1} - LAI_{mx})\right)\right]\sqrt{\gamma_w}$$

and is shared among plants in proportion to their LAI times canopy height. $LAI_{mx}$ is `lai_pot`. For perennials it grows with age:

$$LAI_{mx} = \mathrm{lai\_pot}\left(\frac{yr_{cur}}{\mathrm{yrs\_mat}}\right)^{\mathrm{bm\_tree\_acc}}$$

### Leaf senescence

After `hu_lai_decl`, annuals lose leaf area until maturity:

$$LAI = LAI_{mx}\left(\frac{1 - fr_{PHU}}{1 - fr_{PHU,sen}}\right)^{\mathrm{dlai\_rate}}$$

where $fr_{PHU,sen}$ is the heat unit fraction at which decline started. Temperature-driven perennials drop to `lai_min` over 15 days once `hu_lai_decl` is passed. Moisture-driven perennials shed leaves continuously at a turnover rate between `leaf_tov_mn` and `leaf_tov_mx` months, faster when the 30-day precipitation to PET ratio is below 0.5. Leaves that fall are added to the surface residue.

### Canopy height and roots

$$h_c = h_{c,mx}\sqrt{fr_{LAImx}}$$

with $h_{c,mx}$ = `can_ht_max`. Root depth grows with heat units:

$$z_{root} = 2.5\,fr_{PHU}\,z_{root,mx}, \qquad 25.4\text{ mm} \le z_{root} \le \text{profile depth}$$

with $z_{root,mx}$ = `rt_dp_max` (converted to mm). Perennials use the multi-year heat unit fraction, so their roots keep deepening until maturity.

## Water uptake

The potential transpiration of the HRU (see [Soil water and temperature](soil-water-temperature.md)) is shared among growing plants in proportion to their LAI. Each plant takes up water from the layers within its root zone. The potential uptake down to depth $z$ is

$$w_{up,z} = \frac{E_t}{1 - \exp(-\beta_w)}\left[1 - \exp\left(-\beta_w\,\frac{z}{z_{root}}\right)\right]$$

with the water use distribution parameter $\beta_w$ fixed at 10, so about half of the demand comes from the top 7% of the root zone. The uptake from a layer is the potential uptake to its bottom minus that to its top, with the shortfall of the layers above added back in part:

$$w'_{up,ly} = w_{up,z_l} - w_{up,z_u}\,(1 - \mathrm{epco})$$

where `epco` is the plant uptake compensation factor in [`hydrology.hyd`](../input-reference/hyd.md). With `epco` near 1 deeper layers can make up for dry layers above; near 0 they cannot. The second soil layer always compensates fully. Uptake is limited by the water in the layer, and SWAT+ does not reduce uptake as the soil dries below 25% of available water as SWAT 2009 did.

The water stress factor is the ratio of actual to potential transpiration:

$$\gamma_w = \frac{\sum w_{actualup}}{E_t}$$

### Aeration stress

When the profile contains more water than field capacity, roots lack oxygen. With $sat_{co} = (SW - FC)/(SAT - FC)$ for the whole profile and $a$ = `aeration` in [`plants.plt`](../input-reference/plt.md),

$$\gamma_a = 1 - \frac{s}{s + \exp(2.9014 - 0.03867\,s)}, \qquad s = 100\,\frac{sat_{co} - a}{1.0001 - a}$$

for $s > 0$; otherwise $\gamma_a = 1$.

## Temperature stress

In SWAT+ 62.0.1 temperature stress is

$$\gamma_t = \sin\left(\frac{\pi}{2}\cdot\frac{\bar{T} - T_{base}}{T_{opt} - T_{base}}\right), \qquad 0 \le \gamma_t \le 1$$

where $T_{opt}$ is `tmp_opt`. The factor is 0 at or below the base temperature, 1 at the optimum, falls again above it, and reaches 0 at $2\,T_{opt} - T_{base}$. The SWAT 2009 exponential temperature stress and the cold-night rule (no growth when the minimum temperature is 15 °C below the annual mean) are computed first but replaced by this sine function.

## Nitrogen and phosphorus

### Demand

The optimal nitrogen fraction of the plant falls as it develops:

$$fr_N = (fr_{N,1} - fr_{N,3})\left[1 - \frac{x}{x + \exp(n_1 - n_2\,x)}\right] + fr_{N,3}$$

where $fr_{N,1}$, $fr_{N,2}$ and $fr_{N,3}$ are `frac_n_em`, `frac_n_50` and `frac_n_mat` (at emergence, at 50% of maturity and at maturity), $n_1$ and $n_2$ are fitted to them, and $x$ is $fr_{PHU}$ for annuals or the fraction of `yrs_mat` reached for perennials. The demand is the optimal nitrogen mass, $fr_N \times$ biomass, minus the nitrogen in the plant, and is limited to four times `frac_n_mat` times the day's potential growth. Phosphorus follows the same form with `frac_p_em`, `frac_p_50` and `frac_p_mat`.

### Uptake

Nitrate is taken from the root zone with a depth distribution like water uptake, using `n_uptake` in [`parameters.bsn`](../input-reference/parameters-bsn.md) as the distribution parameter; labile phosphorus uses `p_uptake`. When several plants compete and the soil cannot meet the total demand, each plant gets a share in proportion to its demand.

### Nitrogen fixation

Legumes (`nfix_co` > 0 in [`plants.plt`](../input-reference/plt.md)) fix nitrogen when the soil cannot supply their demand. Fixation depends on growth stage, soil water and soil nitrate:

$$N_{fix} = \min\left(6,\; f_{gr}\,\min(1, f_{sw}, f_{no3})\,(N_{dem} - N_{up})\right)$$

| Factor | Value |
|--------|-------|
| $f_{gr}$ | 0 before 15% of heat units; rises to 1 at 30%; 1 to 55%; falls to 0 at 75% |
| $f_{sw}$ | $SW/(0.85\,FC)$ for the profile |
| $f_{no3}$ | 1 for profile nitrate up to 100 kg N/ha, falling linearly to 0 at 300 kg N/ha |

The result is blended with the unmet demand by the legume coefficient, $N'_{fix} = \mathrm{nfix\_co}\,N_{fix} + (1 - \mathrm{nfix\_co})(N_{dem} - N_{up})$, and limited to the unmet demand and to `n_fix_max` in [`parameters.bsn`](../input-reference/parameters-bsn.md) (kg N/ha/day).

### Nutrient stress

For non-legumes the nitrogen stress factor is

$$\gamma_n = \frac{\varphi}{\varphi + \exp(3.535 - 0.02597\,\varphi)}, \qquad \varphi = 200\left(\frac{N_{plant}}{N_{opt}} - 0.5\right)$$

which is 0 when the plant contains half its optimal nitrogen and close to 1 at the optimum. It is raised to the ratio of the day's uptake to demand when that is larger. Legumes have no nitrogen stress. Phosphorus stress uses the same form.

## Harvest index and yield

The harvest index is the fraction of above-ground biomass removed as yield. It grows through the season towards the optimal value `harv_idx` in [`plants.plt`](../input-reference/plt.md):

$$HI = \mathrm{harv\_idx}\,\frac{100\,fr_{PHU}}{100\,fr_{PHU} + \exp(11.1 - 10\,fr_{PHU})}$$

After half the heat units are reached, water deficit lowers it. With $wu = 100\,\sum E_t/\sum PET$ accumulated from that point,

$$HI_{act} = (HI - HI_{min})\frac{wu}{wu + \exp(6.13 - 0.0883\,wu)} + HI_{min}$$

with $HI_{min}$ = HI/2. The seed (yield) pool of the plant is kept at this fraction of the above-ground biomass as the plant grows. A grain harvest raises the plant's harvest index target to at least `harv_idx_ws`, but only after the seed pool has been built, so `harv_idx_ws` does not change the yield of that harvest.

Harvest operations are defined in [`harv.ops`](../input-reference/ops.md#harvops) by `harv_typ`, `harv_idx`, `harv_eff` and `harv_bm_min`. A harvest takes place only when the plant biomass is above `harv_bm_min` (kg/ha).

| `harv_typ` | Yield removed |
|------------|---------------|
| `grain`, `picker` | `harv_eff` × seed mass; the rest of the seed goes to the soil's active humus |
| `biomass`, `tree`, `stripper` | `harv_idx` × `harv_eff` × (seed + leaf + stem) |
| `tuber`, `peanuts` | Below-ground yield |
| `residue` | A fraction of surface residue, given in the operation |

Yield is reduced by any pesticide stress on the plant, and pesticide in the plant is removed with the yield.

## Land use management

### landuse.lum

Each HRU points to a row of [`landuse.lum`](../input-reference/lum.md), which names the plant community (`plnt_com`), the management schedule (`mgt`), the curve number row (`cn2`), the conservation practice (`cons_prac`), the urban land type, the overland Manning's n row (`ov_mann`), and any tile drain, septic system, filter strip, grassed waterway or user BMP.

### Management schedules

A schedule in [`management.sch`](../input-reference/management.md#managementsch) lists operations by date or by heat units, followed by the names of any decision tables that apply to the HRU. Each operation has a type, a month and day, a heat unit value and up to three data columns:

| Operation | Action |
|-----------|--------|
| `plnt` | Plant one plant or the whole community |
| `harv` | Harvest (see above) |
| `kill` | Kill the plant; biomass goes to residue |
| `hvkl` | Harvest and kill |
| `till` | Tillage, mixing residue and nutrients into the soil ([`tillage.til`](../input-reference/til.md)) |
| `irrm` | Irrigation by date ([`irr.ops`](../input-reference/ops.md#irrops)) |
| `fert` | Fertiliser ([`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt)) |
| `manu` | Manure application |
| `pest` | Pesticide application ([`chem_app.ops`](../input-reference/ops.md#chem_appops)) |
| `graz` | Start grazing ([`graze.ops`](../input-reference/ops.md#grazeops)) |
| `cnup` | Change the curve number |
| `burn` | Prescribed burn ([`fire.ops`](../input-reference/ops.md#fireops)) |
| `swep` | Street sweeping |
| `dwm` | Set drain depth for drainage water management |
| `weir` | Set or change a paddy or wetland weir height |
| `irrp`, `irpm`, `pudl` | Rice paddy irrigation and puddling |
| `mons` | Start or end of a monsoon planting window |
| `skip` | Skip to the end of the year |

What each operation does to plants and soil, with its equations, is described with its parameters: harvest types and harvest efficiency, grazing, irrigation, burning and street sweeping in [`*.ops`](../input-reference/ops.md); fertilizer and manure placement in [`fertilizer.frt`](../input-reference/frt.md#fertilizer-application); tillage and biological mixing in [`tillage.til`](../input-reference/til.md); and automatic irrigation and fertilization by decision table in [`*.dtl`](../input-reference/dtl.md).

An operation with a heat unit value runs when the heat unit fraction passes it: $fr_{PHU}$ of the plant named in the operation if that plant is growing, or the base-zero heat units otherwise. An operation without a heat unit value runs on its month and day. When all remaining operations of a year share one date, the scheduler moves on after one full pass.

### Decision tables

Decision tables in [`lum.dtl`](../input-reference/dtl.md) are conditional rule sets: each table has conditions, alternatives that combine them, and actions that fire when an alternative is true. The tables named in an HRU's schedule are evaluated every day before the other landscape processes, so they can plant, harvest, irrigate, fertilise or change land use in response to weather, soil water or plant growth. See [Decision tables](decision-tables.md).

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `nostress` | [`codes.bsn`](../input-reference/codes-bsn.md) | `0` all stresses, `1` no stress, `2` no nutrient stress |
| `co2` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | CO2 concentration without `co2_yr.dat`, ppm |
| `n_uptake`, `p_uptake` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Depth distribution of N and P uptake |
| `n_fix_max` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Maximum daily N fixation, kg N/ha |
| `epco` | [`hydrology.hyd`](../input-reference/hyd.md) | Plant uptake compensation |
| `plnt_typ`, `gro_trig`, `days_mat` | [`plants.plt`](../input-reference/plt.md) | Plant type, growth trigger, days to maturity |
| `bm_e`, `bm_e_hi`, `co2_hi`, `ru_vpd`, `ext_co` | [`plants.plt`](../input-reference/plt.md) | Light interception and RUE |
| `lai_pot`, `frac_hu1`, `lai_max1`, `frac_hu2`, `lai_max2`, `hu_lai_decl`, `dlai_rate`, `lai_min` | [`plants.plt`](../input-reference/plt.md) | Leaf area curve and decline |
| `can_ht_max`, `rt_dp_max`, `rt_st_beg`, `rt_st_end` | [`plants.plt`](../input-reference/plt.md) | Canopy height, root depth, root fraction |
| `tmp_base`, `tmp_opt` | [`plants.plt`](../input-reference/plt.md) | Temperature response |
| `frac_n_*`, `frac_p_*`, `nfix_co` | [`plants.plt`](../input-reference/plt.md) | Nutrient demand and fixation |
| `harv_idx`, `harv_idx_ws` | [`plants.plt`](../input-reference/plt.md) | Harvest index |
| `aeration` | [`plants.plt`](../input-reference/plt.md) | Aeration stress threshold |
| `yrs_mat`, `bm_tree_acc`, `bm_tree_max`, `leaf_tov_mn`, `leaf_tov_mx` | [`plants.plt`](../input-reference/plt.md) | Perennials |
| `bm_dieoff` | [`plants.plt`](../input-reference/plt.md) | Read but not applied at dormancy in 62.0.1 |

## Related pages

- [`plants.plt`](../input-reference/plt.md), [`landuse.lum`](../input-reference/lum.md), [`management.sch` and operations](../input-reference/ops.md), [`lum.dtl`](../input-reference/dtl.md)
- [Soil water and temperature](soil-water-temperature.md) for the transpiration demand.
- [Nutrient cycling](nutrient-cycling.md) for the soil nitrogen and phosphorus pools.
- [Carbon](carbon.md) for residue and soil carbon.
- [Decision tables](decision-tables.md).

??? quote "Sources"

    - Community, PAR and transpiration split: [`pl_community.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_community.f90)
    - Growth driver: [`pl_grow.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_grow.f90); biomass: [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90)
    - Heat units and nutrient demand: [`pl_nut_demand.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nut_demand.f90), [`pl_nupd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nupd.f90), [`pl_pupd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_pupd.f90); PHU setup in [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90)
    - Leaf area, roots, seed: [`pl_leaf_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_leaf_gro.f90), [`pl_leaf_senes.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_leaf_senes.f90), [`pl_root_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_root_gro.f90), [`pl_seed_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_seed_gro.f90)
    - Dormancy: [`pl_dormant.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_dormant.f90)
    - Stresses: [`pl_waterup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_waterup.f90), [`pl_tstr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_tstr.f90), [`nuts.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nuts.f90)
    - Uptake and fixation: [`pl_nup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nup.f90), [`pl_pup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_pup.f90), [`pl_nfix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nfix.f90)
    - Scheduling: [`mgt_operatn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operatn.f90), [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90), [`mgt_read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_mgtops.f90); decision tables evaluated in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Harvest: [`mgt_harvgrain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvgrain.f90), [`mgt_harvbiomass.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvbiomass.f90), [`mgt_harvtuber.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvtuber.f90), [`mgt_harvresidue.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvresidue.f90); `type harvest_operation` in [`mgt_operations_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operations_module.f90)
    - Plant database type: `type plant_db` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90)

    | `plants.plt` column | Fortran variable |
    |---------------------|------------------|
    | `plnt_typ`, `gro_trig` | `pldb%typ`, `pldb%trig` |
    | `bm_e`, `bm_e_hi`, `co2_hi`, `ru_vpd` | `pldb%bio_e`, `pldb%bioehi`, `pldb%co2hi`, `pldb%wavp` |
    | `harv_idx`, `harv_idx_ws` | `pldb%hvsti`, `pldb%wsyf` |
    | `lai_pot`, `frac_hu1`, `lai_max1`, `frac_hu2`, `lai_max2` | `pldb%blai`, `pldb%frgrw1`, `pldb%laimx1`, `pldb%frgrw2`, `pldb%laimx2` |
    | `hu_lai_decl`, `dlai_rate`, `lai_min` | `pldb%dlai`, `pldb%dlai_rate`, `pldb%alai_min` |
    | `can_ht_max`, `rt_dp_max` | `pldb%chtmx`, `pldb%rdmx` |
    | `tmp_opt`, `tmp_base` | `pldb%t_opt`, `pldb%t_base` |
    | `frac_n_em`, `frac_n_50`, `frac_n_mat` | `pldb%pltnfr1`, `pldb%pltnfr2`, `pldb%pltnfr3` |
    | `frac_p_em`, `frac_p_50`, `frac_p_mat` | `pldb%pltpfr1`, `pldb%pltpfr2`, `pldb%pltpfr3` |
    | `stcon_max`, `vpd`, `frac_stcon` | `pldb%gsi`, `pldb%vpdfr`, `pldb%gmaxfr` |
    | `usle_c_min` | `pldb%usle_c` |
    | `plnt_decomp` | `pldb%rsdco_pl` |
    | `bm_tree_acc`, `yrs_mat`, `bm_tree_max` | `pldb%laixco_tree`, `pldb%mat_yrs`, `pldb%bmx_peren` |
    | `ext_co`, `leaf_tov_mn`, `leaf_tov_mx` | `pldb%ext_coef`, `pldb%leaf_tov_min`, `pldb%leaf_tov_max` |
    | `rt_st_beg`, `rt_st_end` | `pldb%rsr1`, `pldb%rsr2` |
    | `n_uptake`, `p_uptake`, `n_fix_max` (parameters.bsn) | `bsn_prm%n_updis`, `bsn_prm%p_updis`, `bsn_prm%nfixmx` |
    | `harv_typ`, `harv_idx`, `harv_eff`, `harv_bm_min` (harv.ops) | `harvop_db%typ`, `%hi_ovr`, `%eff`, `%bm_min` |

    | Symbol | Fortran variable |
    |--------|------------------|
    | $fr_{PHU}$, multi-year fraction | `pcom(j)%plcur(ipl)%phuacc`, `%phuacc_p` |
    | $PHU$ | `pcom(j)%plcur(ipl)%phumat`, `%phumat_p` |
    | $H_{phosyn}$ | `par(ipl)` |
    | $\Delta bio$, $\gamma_{reg}$ | `bioday`, `pcom(j)%plstr(ipl)%reg` |
    | $\gamma_w$, $\gamma_t$, $\gamma_n$, $\gamma_p$, $\gamma_a$, $\gamma_s$ | `pcom(j)%plstr(ipl)%strsw`, `%strst`, `%strsn`, `%strsp`, `%strsa`, `%strss` |
    | $E_t$ per plant | `epmax(ipl)` |
    | $\beta_w$ | `uptake%water_dis` |
    | $HI$ | `pcom(j)%plg(ipl)%hi_adj` |

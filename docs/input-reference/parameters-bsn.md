---
title: parameters.bsn
description: Basin-wide parameters. Coefficients for runoff, peak rate, nutrients, pesticides, channel routing, lapse rates, erosion and CO2 that apply to the whole watershed.
status: review
verified_against:
  - src/basin_read_prm.f90
  - src/basin_prm_default.f90
  - src/basin_module.f90
  - src/input_file_module.f90
  - src/proc_bsn.f90
  - src/proc_hru.f90
  - src/hrudb_init.f90
  - src/hydro_init.f90
  - src/time_conc_init.f90
  - src/cli_initwgn.f90
  - src/ero_pkq.f90
  - src/wetland_control.f90
  - src/aqu_1d_control.f90
  - src/pest_decay.f90
  - src/pest_tempdecay_module.f90
  - src/ch_rtpest.f90
  - src/pest_lch.f90
  - src/nut_nminrl.f90
  - src/nut_nlch.f90
  - src/nut_solp.f90
  - src/nut_pminrl.f90
  - src/cbn_zhang2.f90
  - src/cbn_surfrsd_decomp.f90
  - src/rsd_decomp.f90
  - src/plantparm_init.f90
  - src/pl_nup.f90
  - src/pl_pup.f90
  - src/pl_nfix.f90
  - src/pl_biomass_gro.f90
  - src/sd_hydsed_init.f90
  - src/ch_rtmusk.f90
  - src/ch_rthr.f90
  - src/ch_rtday.f90
  - src/unit_hyd.f90
  - src/sq_dailycn.f90
  - src/sq_greenampt.f90
  - src/cli_lapse.f90
  - src/ero_cfactor.f90
  - src/ero_ovrsed.f90
  - src/co2_read.f90
  - src/gcycl.f90
  - src/hyd_connect.f90
  - src/cal_parm_select.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`parameters.bsn` contains the coefficients that apply to the whole watershed: initial soil water, surface runoff lag, peak rate factors, nutrient and pesticide transport coefficients, denitrification, channel routing coefficients, lapse rates, erosion coefficients for sub-daily runs and the starting CO2 concentration. It is named in the second position of the `basin` line of [`file.cio`](file-cio.md) (default `parameters.bsn`). Several of the parameters only matter for the methods selected in [`codes.bsn`](codes-bsn.md).

If the file named in [`file.cio`](../input-reference/file-cio.md) does not exist, every parameter keeps its built-in value, after the zero-value replacements described in [Zero and missing values](#zero-and-missing-values).

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Line 3 contains 44 values in the order below: 42 real numbers followed by two integers. The reader matches values by position only, so all 44 must be present and in this order. The table gives the column headers the SWAT+ Editor writes; several no longer describe what the model does with the value.

| # | Column | Units | Built-in value | Typical range | Description |
|---|--------|-------|----------------|---------------|-------------|
| 1 | `lai_noevap` | - | 3.0 | - | Not used. Read and can be changed by calibration, but no routine uses it. |
| 2 | `sw_init` | fraction | 0.0 | 0 to 1 | Initial soil water as a fraction of field capacity, the same for all soils. 0 means it is calculated from average annual precipitation. See [Initial soil water](#initial-soil-water). |
| 3 | `surq_lag` | - | 4.0 | 1 to 24 | Surface runoff lag coefficient. See [Surface runoff lag](#surface-runoff-lag). |
| 4 | `adj_pkrt` | - | 1.0 | 0.5 to 2 | Multiplier on the monthly mean fraction of daily rain that falls in the maximum half hour, calculated from the weather generator statistics (limited to 0.1 to 0.95). The daily fraction drawn from it is used by the half-hour intensity peak rate method (`sed_det = 1`), the rainfall erosivity of the MUSLE, urban washoff and the generation of sub-daily rainfall. |
| 5 | `adj_pkrt_sed` | - | 484.0 | - | Peak rate factor of the NRCS peak runoff equation, used for HRU erosion when `sed_det = 0` in [`codes.bsn`](../input-reference/codes-bsn.md) and for wetlands. See [Peak rate factor](#peak-rate-factor). |
| 6 | `lin_sed` | - | 0.0 | 0 and up | Pesticide groundwater mixing factor. See [Pesticides in aquifers](#pesticides-in-aquifers). |
| 7 | `exp_sed` | - | 0.0 | 0 or 1 | Temperature-dependent pesticide decay: `1` on, any other value off. See [Pesticide decay and temperature](#pesticide-decay-and-temperature). |
| 8 | `orgn_min` | 1/day | 0.003 | 0.0003 to 0.003 | Rate factor for mineralization of the active humus N and P pools (static carbon model, `carbon = 0`). |
| 9 | `n_uptake` | - | 20.0 | 0 to 100 | Nitrogen uptake distribution parameter. See [Uptake distribution](#uptake-distribution). |
| 10 | `p_uptake` | - | 20.0 | 0 to 100 | Phosphorus uptake distribution parameter. |
| 11 | `n_perc` | - | 0.10 | 0 to 1 | Nitrate percolation coefficient: ratio of the nitrate concentration in surface runoff to the concentration in water leaving the top layer. |
| 12 | `p_perc` | m³/Mg | 10.0 | 10 to 17.5 | Phosphorus percolation coefficient, used in the leaching of soluble P from each layer. |
| 13 | `p_soil` | m³/Mg | 175.0 | 100 to 200 | Phosphorus soil partitioning coefficient: ratio of soluble P in the top 10 mm of soil to soluble P in surface runoff. |
| 14 | `p_avail` | fraction | 0.40 | 0.01 to 0.7 | Phosphorus availability index: fraction of fertilizer P that is in solution after the fast reaction period. Sets the balance between the labile and active mineral P pools in the original P model (`soil_p = 0`). |
| 15 | `rsd_decomp` | fraction/day | 0.05 | 0.02 to 0.1 | Residue decomposition coefficient: daily fraction of residue that decomposes under ideal conditions. Used for every plant whose `plnt_decomp` in [`plants.plt`](../input-reference/plt.md) is 0. |
| 16 | `pest_perc` | - | 0.5 | 0 to 1 | Pesticide percolation coefficient: ratio of the pesticide concentration in surface runoff and lateral flow to the concentration in percolate. |
| 17 | `msk_co1` | - | 0.75 | 0 to 10 | Weight of the storage time constant at bankfull depth in the Muskingum storage constant. |
| 18 | `msk_co2` | - | 0.25 | 0 to 10 | Weight of the storage time constant at 0.1 bankfull depth in the Muskingum storage constant. |
| 19 | `msk_x` | - | 0.20 | 0 to 0.3 | Muskingum weighting factor for inflow and outflow in channel storage. |
| 20 | `nperco_lchtile` | - | 0.5 | 0 to 1 | Ratio of the nitrate concentration in tile flow to the concentration in the mobile water of the tile layer. |
| 21 | `evap_adj` | - | 0.60 | 0.5 to 1 | Channel evaporation adjustment factor: multiplier on station PET for evaporation from the channel water surface. |
| 22 | `scoef` | - | 1.0 | 0 to 1 | Channel storage coefficient of the variable storage routing method (`rte_cha = 0` in [`codes.bsn`](../input-reference/codes-bsn.md)). |
| 23 | `denit_exp` | - | 1.40 | 0 to 3 | Denitrification exponential rate coefficient. See [Denitrification](#denitrification). |
| 24 | `denit_frac` | - | 1.30 | see text | Denitrification threshold on the soil water factor. See [Denitrification](#denitrification). |
| 25 | `man_bact` | fraction | 0.15 | - | Not used. |
| 26 | `adj_uhyd` | h | 0.0 | 0 and up | Added to the base time of the sub-daily unit hydrograph. See [unit hydrograph](codes-bsn.md#unit-hydrograph). |
| 27 | `cn_froz` | 1/mm | 0.000862 | - | Frozen soil coefficient of the curve number retention parameter. See [Frozen soil](#frozen-soil). |
| 28 | `dorm_hr` | h | -1.0 | 0 to 24 | Day length threshold for dormancy. 0 or less means it is calculated from latitude. See [Dormancy threshold](#dormancy-threshold). |
| 29 | `plaps` | mm/km | 0.0 | - | Precipitation lapse rate. Positive values increase precipitation with elevation. Used when `lapse = 1` in [`codes.bsn`](../input-reference/codes-bsn.md). |
| 30 | `tlaps` | °C/km | 6.5 | - | Temperature lapse rate. Positive values decrease temperature with elevation. Used when `lapse = 1` in [`codes.bsn`](../input-reference/codes-bsn.md). |
| 31 | `n_fix_max` | kg N/ha/day | 20.0 | 1 to 20 | Maximum daily nitrogen fixation of a plant. |
| 32 | `rsd_decay` | fraction/day | 0.01 | 0 to 0.05 | Minimum daily residue decay fraction. The daily decay rate of residue is never below this value. |
| 33 | `rsd_cover` | ha/t | 0.75 | - | Residue cover factor in the USLE C factor. See [USLE C factor](#usle-c-factor). |
| 34 | `urb_init_abst` | mm | 1.0 | 0 to 10 | Maximum initial abstraction on impervious urban areas. Used only with Green-Ampt (`gampt = 1`). |
| 35 | `petco_pmpt` | % | 100.0 | - | Not used. The PET of every method is adjusted with `pet_co` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) instead. |
| 36 | `uhyd_alpha` | - | 1.0 | 0.5 to 10 | Shape coefficient of the gamma unit hydrograph (`uhyd = 1` in [`codes.bsn`](../input-reference/codes-bsn.md)). |
| 37 | `splash` | - | 0.0 | 0.9 to 3.1 | Splash erosion coefficient. See [Sub-daily erosion](#sub-daily-erosion). |
| 38 | `rill` | - | 0.0 | 0.5 to 2 | Rill erosion coefficient, a multiplier on the USLE K factor of the top layer. |
| 39 | `surq_exp` | - | 0.0 | 1 to 3 | Exponent on bed shear stress in overland flow erosion. |
| 40 | `cov_mgt` | - | 0.0 | 0.001 to 0.45 | Scaling factor on the cover and management factor in overland flow erosion. |
| 41 | `cha_d50` | mm | 0.0 | - | Not used. The median particle size of each channel is read from the channel input. |
| 42 | `co2` | ppm | 400.0 | - | Atmospheric CO2 concentration, used for every year when there is no `co2_yr.dat`. See [CO2](#co2). |
| 43 | `day_lag_max` | days | 0 | - | Not used as read. The model always sets it to 2. |
| 44 | `igen` | - | 5 | 0 and up | Random number seed code. See [Random numbers](#random-numbers). |

Values are read in one free-format read. A line with fewer values continues onto the next line, and the parameters that are not reached keep their built-in values. A value that cannot be read ends the read without a message.

## Zero and missing values

After reading, SWAT+ replaces values that are zero or negative (strictly, below $10^{-6}$) for some parameters. For most of them the replacement is the built-in value, so leaving a column at 0 has the same effect as entering the built-in value. These are: `lai_noevap`, `surq_lag`, `adj_pkrt`, `n_uptake`, `p_uptake`, `n_perc`, `p_perc`, `p_soil`, `p_avail`, `rsd_decomp`, `pest_perc`, `msk_co1`, `msk_co2`, `msk_x`, `nperco_lchtile`, `evap_adj`, `denit_exp`, `denit_frac`, `man_bact`, `cn_froz`, `n_fix_max`, `rsd_decay`, `rsd_cover` and `uhyd_alpha`.

The exceptions are:

| Column | Value read | Value used |
|--------|-----------|------------|
| `adj_pkrt_sed` | 0 or less | 1.0 (the built-in value is 484.0) |
| `orgn_min` | 0 or less | 0.0003 (the built-in value is 0.003) |
| `urb_init_abst` | 0 or less | 0.0 (the built-in value is 1.0) |
| `co2` | below 100 | 400.0 |
| `day_lag_max` | any | 2 |

`sw_init`, `adj_uhyd`, `dorm_hr`, `splash`, `rill`, `surq_exp`, `cov_mgt` and `cha_d50` stay at 0 when 0 is read, and 0 has a meaning for some of them (see the sections below). `lin_sed`, `exp_sed`, `scoef`, `plaps`, `tlaps` and `igen` are used as read.

## Initial soil water

All soils start at the same fraction of field capacity. If `sw_init` is 0 or less, the fraction is calculated from the average annual precipitation $P$ (mm) of the HRU's weather generator station:

$$f_{fc} = \frac{P}{P + \exp(9.043 - 0.002135\,P)}$$

A warm-up period of at least one year (`nyskip` in [`print.prt`](print-prt.md)) makes results largely independent of `sw_init`.

## Surface runoff lag

In HRUs with a long time of concentration, only part of the surface runoff reaches the channel on the day it is generated. The fraction released each day is

$$f_{rel} = 1 - \exp\!\left(-\frac{\mathrm{surq\_lag}}{t_{conc}}\right)$$

with $t_{conc}$ in hours. In sub-daily runs $t_{conc}$ is expressed in time steps. The rest is kept in surface storage and added to the next day's runoff. Smaller values of `surq_lag` keep more water in storage and smooth the hydrograph.

## Peak rate factor

The column labelled `adj_pkrt_sed` by the SWAT+ Editor is the peak rate factor of the NRCS peak runoff equation (see [peak runoff rate](codes-bsn.md#peak-runoff-rate)). The built-in value, 484, is the standard factor for the NRCS dimensionless unit hydrograph. The Editor writes 1.0 in this column, and a value of 0 is also replaced by 1.0. A factor of 1 gives peak rates 484 times lower than the standard factor, which lowers MUSLE sediment yields from HRUs when `sed_det = 0`. The value only affects the peak rate used for erosion and in wetlands; it does not change runoff volumes.

## Pesticides in aquifers

The columns labelled `lin_sed` and `exp_sed` by the Editor are pesticide parameters in 62.0.1. In each aquifer, the pesticide concentration in return flow and seepage is the pesticide mass divided by a mixing volume:

$$C = \frac{M_{pest}}{f_{mix}\,S_{aqu} + Q_{rtn} + Q_{revap} + Q_{seep}}$$

where $f_{mix}$ is `lin_sed`, $S_{aqu}$ is the aquifer storage and the $Q$ terms are the day's return flow, revap and seepage (mm). With `lin_sed = 0` the concentration is based on the day's outflows only. Larger values dilute the pesticide in more of the stored water and slow its release.

## Pesticide decay and temperature

With `exp_sed = 1` (the value 1.0; other values such as 2 do not count), pesticide decay in soil, on foliage, in aquifers, in channel water and in channel bed sediment uses half-lives adjusted for temperature with a Q10 model:

$$t_{1/2}(T) = t_{1/2,25}\; Q_{10}^{(25 - T)/10}, \qquad Q_{10} = 2.58$$

where $t_{1/2,25}$ is the half-life from the pesticide database, taken as the value at 25 °C, and the daily fraction remaining is $\exp(-0.693 / t_{1/2}(T))$. Soil decay uses the layer temperature, foliar decay the top soil layer temperature, and channel decay the water temperature. In aquifers the temperature is fixed at 0 °C, which makes aquifer half-lives about 10.7 times longer than the database value. Any other value of `exp_sed` uses the database half-lives without a temperature adjustment.

The Ames example file (see [Example](#example)) has `exp_sed = 1.0`, so temperature-dependent decay is on in that dataset.

## Uptake distribution

The maximum nitrogen uptake from the soil above depth $z$ is

$$U(z) = U_{pot}\,\frac{1 - \exp(-\beta_n\,z / z_{root})}{1 - \exp(-\beta_n)}$$

where $\beta_n$ is `n_uptake` and $z_{root}$ is the root depth. Larger values concentrate uptake near the surface. Because the top 10 mm interacts with surface runoff, `n_uptake` affects the nitrate available for runoff; lower layers can make up a shortfall in the upper layers, so plant N stress changes little with this parameter. `p_uptake` works the same way for phosphorus.

## Denitrification

Denitrification in a soil layer is

$$N_{denit} = NO_3\left[1 - \exp\!\left(-\mathrm{denit\_exp}\;\gamma_{tmp}\;\frac{OC}{100}\right)\right]$$

where $\gamma_{tmp}$ is the temperature factor and $OC$ the organic carbon content (%). It only occurs on days when the soil water factor $\gamma_{sw}$ is at or above `denit_frac`.

With the static carbon model (`carbon = 0`), $\gamma_{sw} = 0.1 + 0.9\sqrt{SW/FC}$, with no upper limit. With the default `denit_frac` of 1.3, denitrification needs $SW/FC \ge 1.78$, that is, a layer well above field capacity.

With the dynamic carbon model (`carbon = 2`), $\gamma_{sw}$ comes from the water factor selected in [`carbon.bsn`](carbon-bsn.md) and is never above 1. Any `denit_frac` above 1, including the default 1.3, then switches denitrification off for the whole run. Datasets using `carbon = 2` need a `denit_frac` of 1 or less to simulate denitrification.

## Frozen soil

When the second soil layer is at or below 0 °C, the curve number retention parameter $S$ is reduced:

$$S_{frz} = S_{max}\left[1 - \exp(-\mathrm{cn\_froz}\cdot S)\right]$$

which increases runoff from frozen soil. The same adjustment is applied with Green-Ampt.

## Dormancy threshold

A plant goes dormant when the day length falls below the station's minimum day length plus a threshold $t_{dorm}$ (hours). If `dorm_hr` is above 0, $t_{dorm}$ = `dorm_hr` everywhere. Otherwise it depends on the latitude $\phi$ of the weather generator station: 1 h above 40°, $(|\phi| - 20)/20$ h between 20° and 40°, and -1 h below 20°.

## USLE C factor

The C factor is the product of a residue factor and a biomass factor:

$$C = \exp\!\left(-\mathrm{rsd\_cover}\cdot\frac{R + 1}{1000}\right)\left[1 - f_{cov}\,\exp(-0.328\,h_c)\right]$$

where $R$ is the residue on the surface (kg/ha), $h_c$ is the canopy height (m), and $f_{cov}$ is the ground cover fraction of the above-ground biomass. This is the only C factor method in 62.0.1 (see [USLE C factor](codes-bsn.md#usle-c-factor)).

## Sub-daily erosion

With Green-Ampt (`gampt` above 0 in [`codes.bsn`](../input-reference/codes-bsn.md)), sediment from each time step is the sum of splash and overland flow erosion. Splash erosion decreases with runoff depth $h$ (mm) as $\exp(-\mathrm{splash}\cdot h/1000)$ and depends on rainfall kinetic energy and a soil texture erodibility. Overland flow erosion is

$$E_{ov} = 11.02\;\mathrm{rill}\;K\;\mathrm{cov\_mgt}\;C\;\tau^{\,\mathrm{surq\_exp}}$$

in kg/h/m², where $K$ is the USLE K factor of the top layer, $C$ is a cover factor from biomass and residue, and $\tau$ is the bed shear stress (N/m²). With the built-in values of 0 for `rill` or `cov_mgt`, overland flow erosion is zero.

## CO2

Without a `co2_yr.dat` file in the run folder, every year uses `co2`. With the file, the yearly values come from it (see [co2_yr.dat](management.md#co2_yrdat-and-co2out)). The radiation use efficiency of plants is adjusted for CO2 only when `co2` in `parameters.bsn` is above 350 ppm, even when the yearly values come from `co2_yr.dat`. Penman-Monteith PET uses the yearly values in all cases.

## Random numbers

With `igen = 0`, the weather generator and other random processes start from fixed seeds, so every run gives the same random sequence. With any other value, each seed is advanced by a number of steps that depends on `igen`, so different `igen` values give different sequences. The same `igen` always gives the same sequence, so a new value is needed for each different realisation.

## Calibration

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md) with object type `bsn`, using their model names: `surlag` (`surq_lag`), `adj_pkr` (`adj_pkrt`), `prf` (`adj_pkrt_sed`), `evlai` (`lai_noevap`), `ffcb` (`sw_init`), `cmn` (`orgn_min`), `nperco` (`n_perc`), `pperco` (`p_perc`), `phoskd` (`p_soil`), `psp` (`p_avail`), `rsdco` (`rsd_decomp`), `percop` (`pest_perc`), `msk_co1`, `msk_co2`, `msk_x`, `nperco_lchtile`, `evrch` (`evap_adj`), `cdn` (`denit_exp`), `sdnco` (`denit_frac`), `tb_adj` (`adj_uhyd`), `n_updis` (`n_uptake`), `rsd_covco` (`rsd_cover`), `dorm_hr`, `plaps` and `tlaps`. See [parameter change files](../calibration/parameter-change-files.md).

The changes in [`calibration.cal`](../calibration/parameter-change-files.md) are applied once, after the HRUs, channels and weather stations have been set up. Several of these parameters are only used during that setup, so changing them in [`calibration.cal`](../calibration/parameter-change-files.md) has no effect on the run:

- `cmn`, `nperco`, `pperco`, `phoskd`, `psp` and `nperco_lchtile` have already been copied to each HRU. Use the HRU-level names `cmn_h`, `nperco_h`, `pperco_h`, `phoskd_h`, `psp_h` and `nperco_lchtile_h` instead.
- `ffcb`: the initial soil water has already been set.
- `adj_pkr` and `dorm_hr`: the half-hour rainfall fractions and the dormancy thresholds of the weather stations have already been calculated.
- `msk_co1`, `msk_co2` and `msk_x`: the Muskingum coefficients of the channels have already been calculated.
- `rsdco`: it has already been copied to the plants with `plnt_decomp` = 0.

`surlag` is recalculated into the runoff release fraction when it is changed, and the others are used directly during the simulation, so their changes take effect.

## Example

`refdata/Ames_sub1/parameters.bsn` in the SWAT+ repository:

```
parameters.bsn: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
  lai_noevap       sw_init      surq_lag      adj_pkrt  adj_pkrt_sed       lin_sed       exp_sed      orgn_min      n_uptake      p_uptake        n_perc        p_perc        p_soil       p_avail    rsd_decomp     pest_perc       msk_co1       msk_co2         msk_x  nperco_lchtile      evap_adj         scoef     denit_exp    denit_frac      man_bact      adj_uhyd       cn_froz       dorm_hr         plaps         tlaps     n_fix_max     rsd_decay     rsd_cover  urb_init_abst    petco_pmpt    uhyd_alpha        splash          rill      surq_exp       cov_mgt       cha_d50           co2   day_lag_max      igen
     3.00000       0.50000       4.00000       1.00000       1.00000       0.00000       1.00000       0.00000      20.00000      20.00000       0.10000      10.00000     175.00000       0.40000       0.05000       0.50000       0.75000       0.25000       0.20000       0.50000       0.60000       1.00000       1.40000       1.30000       0.15000       0.00000       0.00000       0.00000       0.00000       0.00000      20.00000       0.01000       0.30000       1.00000       1.00000       5.00000       1.00000       0.70000       1.20000       0.03000      50.00000     400.00000      0                0
```

How the model reads some of these values:

- `sw_init = 0.5`: soils start at half of field capacity.
- `adj_pkrt_sed = 1.0`: the NRCS peak rate factor is 1. The standard factor is 484.
- `exp_sed = 1.0`: temperature-dependent pesticide decay is on.
- `orgn_min = 0.0`: replaced by 0.0003.
- `cn_froz = 0.0`: replaced by 0.000862.
- `dorm_hr = 0.0`: the dormancy threshold is calculated from latitude.
- `plaps = 0.0` and `tlaps = 0.0`: no lapse rate adjustment, even if `lapse = 1` in [`codes.bsn`](../input-reference/codes-bsn.md).
- `denit_frac = 1.3`: this dataset uses `carbon = 2` in its [`codes.bsn`](../input-reference/codes-bsn.md), so no denitrification occurs (see [Denitrification](#denitrification)).
- `petco_pmpt`, `cha_d50` and `man_bact` have no effect; `day_lag_max` is set to 2.
- `igen = 0`: fixed random seeds.

## Related files

- [`file.cio`](file-cio.md): names `parameters.bsn` on its `basin` line.
- [`codes.bsn`](codes-bsn.md): method codes that decide which of these parameters are used.
- [`hydrology.hyd`](hyd.md): HRU-level hydrology parameters, including `pet_co`.
- [`plants.plt`](plt.md): `plnt_decomp` overrides `rsd_decomp` for a plant.
- [Parameter change files](../calibration/parameter-change-files.md): calibration names for these parameters.
- [Nutrient cycling](../model-theory/nutrient-cycling.md), [pesticides](../model-theory/pesticides.md), [erosion and sediment](../model-theory/erosion-sediment.md), [channels](../model-theory/channels.md) and [hydrology](../model-theory/hydrology.md): process descriptions.

??? quote "Sources"

    - Reader: [`basin_read_prm.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_prm.f90), followed by the zero-value replacements in [`basin_prm_default.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_prm_default.f90); both called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Type definition: `type basin_parms` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - File name slot: `in_basin%parms_bas` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)
    - Copy to HRUs: [`hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90)
    - Hydrology: [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90), [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90), [`sq_dailycn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_dailycn.f90), [`sq_greenampt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_greenampt.f90), [`unit_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/unit_hyd.f90), [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90)
    - Weather generator: [`cli_initwgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_initwgn.f90), [`gcycl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gcycl.f90), [`co2_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/co2_read.f90)
    - Peak rate and erosion: [`ero_pkq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_pkq.f90), [`wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90), [`ero_cfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_cfactor.f90), [`ero_ovrsed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ovrsed.f90)
    - Pesticides: [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90), [`pest_decay.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_decay.f90), [`pest_tempdecay_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_tempdecay_module.f90), [`ch_rtpest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpest.f90), [`pest_lch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_lch.f90)
    - Nutrients: [`nut_nminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nminrl.f90), [`cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90), [`nut_nlch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nlch.f90), [`nut_solp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_solp.f90), [`nut_pminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_pminrl.f90), [`rsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rsd_decomp.f90), [`cbn_surfrsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_surfrsd_decomp.f90), [`plantparm_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plantparm_init.f90)
    - Plants: [`pl_nup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nup.f90), [`pl_pup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_pup.f90), [`pl_nfix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nfix.f90), [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90)
    - Channels: [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`ch_rtmusk.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtmusk.f90), [`ch_rthr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rthr.f90), [`ch_rtday.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtday.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `lai_noevap` | `bsn_prm%evlai` |
    | `sw_init` | `bsn_prm%ffcb` |
    | `surq_lag` | `bsn_prm%surlag` |
    | `adj_pkrt` | `bsn_prm%adj_pkr` |
    | `adj_pkrt_sed` | `bsn_prm%prf` |
    | `lin_sed` | `bsn_prm%pestgwfact` |
    | `exp_sed` | `bsn_prm%temp_decay` |
    | `orgn_min` | `bsn_prm%cmn` |
    | `n_uptake` | `bsn_prm%n_updis` |
    | `p_uptake` | `bsn_prm%p_updis` |
    | `n_perc` | `bsn_prm%nperco` |
    | `p_perc` | `bsn_prm%pperco` |
    | `p_soil` | `bsn_prm%phoskd` |
    | `p_avail` | `bsn_prm%psp` |
    | `rsd_decomp` | `bsn_prm%rsdco` |
    | `pest_perc` | `bsn_prm%percop` |
    | `msk_co1`, `msk_co2`, `msk_x` | `bsn_prm%msk_co1`, `%msk_co2`, `%msk_x` |
    | `nperco_lchtile` | `bsn_prm%nperco_lchtile` |
    | `evap_adj` | `bsn_prm%evrch` |
    | `scoef` | `bsn_prm%scoef` |
    | `denit_exp` | `bsn_prm%cdn` |
    | `denit_frac` | `bsn_prm%sdnco` |
    | `man_bact` | `bsn_prm%bact_swf` |
    | `adj_uhyd` | `bsn_prm%tb_adj` |
    | `cn_froz` | `bsn_prm%cn_froz` |
    | `dorm_hr` | `bsn_prm%dorm_hr` |
    | `plaps`, `tlaps` | `bsn_prm%plaps`, `%tlaps` |
    | `n_fix_max` | `bsn_prm%nfixmx` |
    | `rsd_decay` | `bsn_prm%decr_min` |
    | `rsd_cover` | `bsn_prm%rsd_covco` |
    | `urb_init_abst` | `bsn_prm%urb_init_abst` |
    | `petco_pmpt` | `bsn_prm%petco_pmpt` |
    | `uhyd_alpha` | `bsn_prm%uhalpha` |
    | `splash` | `bsn_prm%eros_spl` |
    | `rill` | `bsn_prm%rill_mult` |
    | `surq_exp` | `bsn_prm%eros_expo` |
    | `cov_mgt` | `bsn_prm%c_factor` |
    | `cha_d50` | `bsn_prm%ch_d50` |
    | `co2` | `bsn_prm%co2` |
    | `day_lag_max` | `bsn_prm%day_lag_mx` |
    | `igen` | `bsn_prm%igen` |

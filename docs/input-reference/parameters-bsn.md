---
title: parameters.bsn
description: Basin-wide numeric parameters. Coefficients and constants shared across the watershed.
status: review
verified_against:
  - src/basin_read_prm.f90
  - src/basin_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`parameters.bsn` holds the basin-wide numeric coefficients (initial soil water, surface runoff lag, nutrient cycling rates, channel routing factors, lapse rates, CO2, and so on). Values are read into `bsn_prm` (`type basin_parms`) and consulted by hydrology, nutrient, erosion, and routing routines.

## Source

- Reader: [`src/basin_read_prm.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_read_prm.f90)
- Type definition: [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_module.f90), `type basin_parms`

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Line 3: 44 values, list-directed, read into `bsn_prm` in declaration order. The last two values are integers; the rest are reals.

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | evlai | real | 3.0 | none | leaf area index above which no soil evaporation occurs |
| 2 | ffcb | real | 0.0 | fraction | initial soil water content as a fraction of field capacity |
| 3 | surlag | real | 4.0 | days | surface runoff lag time |
| 4 | adj_pkr | real | 1.0 | none | peak rate adjustment factor in the subbasin |
| 5 | prf | real | 484.0 | none | peak rate factor for the peak rate equation |
| 6 | spcon | real | 0.0 | none | not used |
| 7 | spexp | real | 0.0 | none | not used |
| 8 | cmn | real | 0.003 | 1/day | rate factor for mineralization of active organic N |
| 9 | n_updis | real | 20.0 | none | nitrogen uptake distribution parameter |
| 10 | p_updis | real | 20.0 | none | phosphorus uptake distribution parameter |
| 11 | nperco | real | 0.10 | 0..1 | nitrate percolation coefficient |
| 12 | pperco | real | 10.0 | 0..1 | phosphorus percolation coefficient |
| 13 | phoskd | real | 175.0 | none | phosphorus soil partitioning coefficient |
| 14 | psp | real | 0.40 | none | phosphorus availability index |
| 15 | rsdco | real | 0.05 | none | residue decomposition coefficient |
| 16 | percop | real | 0.5 | 0..1 | pesticide percolation coefficient |
| 17 | msk_co1 | real | 0.75 | none | Muskingum storage time constant for bankfull depth |
| 18 | msk_co2 | real | 0.25 | none | Muskingum storage time constant for low flow |
| 19 | msk_x | real | 0.20 | none | Muskingum weighting factor for inflow vs outflow |
| 20 | nperco_lchtile | real | 0.5 | none | N concentration coefficient for tile flow and bottom-layer leaching |
| 21 | evrch | real | 0.60 | none | reach evaporation adjustment factor |
| 22 | scoef | real | 1.0 | 0..1 | channel storage coefficient |
| 23 | cdn | real | 1.40 | none | denitrification exponential rate coefficient |
| 24 | sdnco | real | 1.30 | none | denitrification threshold (fraction of field capacity) |
| 25 | bact_swf | real | 0.15 | fraction | fraction of manure containing active colony-forming units |
| 26 | tb_adj | real | 0.0 | none | adjustment factor for sub-daily unit hydrograph base time |
| 27 | cn_froz | real | 0.000862 | none | parameter for frozen-soil adjustment on infiltration/runoff |
| 28 | dorm_hr | real | -1.0 | hours | dormancy time threshold |
| 29 | plaps | real | 0.0 | mm/km | precipitation lapse rate per km of elevation difference |
| 30 | tlaps | real | 6.5 | deg C/km | temperature lapse rate per km of elevation difference |
| 31 | nfixmx | real | 20.0 | kg/ha/day | maximum daily nitrogen fixation |
| 32 | decr_min | real | 0.01 | 1/day | minimum daily residue decay |
| 33 | rsd_covco | real | 0.75 | none | residue cover factor for computing cover fraction |
| 34 | urb_init_abst | real | 1.0 | none | maximum initial abstraction for urban areas (Green-Ampt) |
| 35 | petco_pmpt | real | 100.0 | percent | PET adjustment for Penman-Monteith and Priestley-Taylor |
| 36 | uhalpha | real | 1.0 | none | alpha coefficient for the gamma-function unit hydrograph |
| 37 | eros_spl | real | 0.0 | none | coefficient of splash erosion (typical range 0.9 to 3.1) |
| 38 | rill_mult | real | 0.0 | none | rill erosion coefficient |
| 39 | eros_expo | real | 0.0 | none | exponential coefficient for overland flow |
| 40 | c_factor | real | 0.0 | none | cover and management factor scaling for overland-flow erosion |
| 41 | ch_d50 | real | 0.0 | mm | median particle diameter of the main channel |
| 42 | co2 | real | 400.0 | ppm | CO2 concentration at start of simulation |
| 43 | day_lag_mx | int | 0 | days | maximum days to lag hydrographs for HRU, RU, and channels on non-draining soils |
| 44 | igen | int | 5 | none | random generator code. `0` use defaults, `1` generate new numbers every run |

## Example

`refdata/Ames_sub1/parameters.bsn`:

```
parameters.bsn: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
  lai_noevap       sw_init      surq_lag      adj_pkrt  adj_pkrt_sed       lin_sed       exp_sed      orgn_min      n_uptake      p_uptake        n_perc        p_perc        p_soil       p_avail    rsd_decomp     pest_perc       msk_co1       msk_co2         msk_x  nperco_lchtile      evap_adj         scoef     denit_exp    denit_frac      man_bact      adj_uhyd       cn_froz       dorm_hr         plaps         tlaps     n_fix_max     rsd_decay     rsd_cover  urb_init_abst    petco_pmpt    uhyd_alpha        splash          rill      surq_exp       cov_mgt       cha_d50           co2   day_lag_max      igen
     3.00000       0.50000       4.00000       1.00000       1.00000       0.00000       1.00000       0.00000      20.00000      20.00000       0.10000      10.00000     175.00000       0.40000       0.05000       0.50000       0.75000       0.25000       0.20000       0.50000       0.60000       1.00000       1.40000       1.30000       0.15000       0.00000       0.00000       0.00000       0.00000       0.00000      20.00000       0.01000       0.30000       1.00000       1.00000       5.00000       1.00000       0.70000       1.20000       0.03000      50.00000     400.00000      0                0
```

Notes:

- Tool header names (`lai_noevap`, `sw_init`, `surq_lag`, `adj_pkrt`, `orgn_min`, `n_uptake`, `evap_adj`, `denit_exp`, `denit_frac`, `man_bact`, `adj_uhyd`, `n_fix_max`, `rsd_decay`, `rsd_cover`, `uhyd_alpha`, `splash`, `rill`, `surq_exp`, `cov_mgt`, `cha_d50`, `day_lag_max`) do not match the field names in the source (`evlai`, `ffcb`, `surlag`, `adj_pkr`, `cmn`, `n_updis`, `evrch`, `cdn`, `sdnco`, `bact_swf`, `tb_adj`, `nfixmx`, `decr_min`, `rsd_covco`, `uhalpha`, `eros_spl`, `rill_mult`, `eros_expo`, `c_factor`, `ch_d50`, `day_lag_mx`). The reader uses position only.
- Position 8 in this dataset is `orgn_min = 0.0`. In the source this is `cmn`, with default `0.003`. The example overrides the default to zero, which disables active organic-N mineralization.
- Position 7 is `exp_sed = 1.0`. This is `spexp` in the source, marked "not used".
- Positions 28 to 30 (`dorm_hr`, `plaps`, `tlaps`) are all zero in this dataset. The default for `tlaps` is `6.5` deg C/km; this dataset disables temperature lapse.

## Related files

- [`codes.bsn`](../input-reference/codes-bsn.md). Method switches that select which of these parameters are active.

---
title: "plants.plt"
description: Plant parameter database. Growth, phenology, biomass, nutrient and residue parameters for every plant or land cover the simulation can grow.
status: review
verified_against:
  - src/plant_parm_read.f90
  - src/plant_data_module.f90
  - src/plantparm_init.f90
  - src/plant_init.f90
  - src/pl_leaf_gro.f90
  - src/pl_leaf_senes.f90
  - src/pl_root_gro.f90
  - src/pl_dormant.f90
  - src/pl_mortality.f90
  - src/pl_biomass_gro.f90
  - src/pl_nfix.f90
  - src/pl_waterup.f90
  - src/hru_control.f90
  - src/cbn_rsd_transfer.f90
  - src/cbn_surfrsd_decomp.f90
  - src/cal_parm_select.f90
  - src/basin_module.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`plants.plt` is the plant growth database. Each row is one plant species, crop variety or land cover, with the parameters SWAT+ needs to grow it: plant type, heat units to maturity, leaf area development, radiation use efficiency, canopy height, rooting depth, temperature limits, nutrient content, stomatal conductance and residue properties.

Plant communities in [`plant.ini`](ini.md), plant operations in [`management.sch`](management.md) and decision tables, and land uses in [`landuse.lum`](lum.md) all refer to rows of this file by name. The names are also used by the GIS interfaces to link land cover maps to SWAT+ land uses.

The file is named on the `hru_parm_db` line of [`file.cio`](file-cio.md) (default `plants.plt`). If the file is missing, the database is empty.

The database distributed with SWAT+ has parameters for most common crops, grasses, trees and land covers. If a land use or plant is not in it, start from a row for a plant with similar growth habits.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one plant with 56 values in the order below. The reader does not match columns by header name, so every value must be present and in this order. It ignores anything after the 56th value, so the `description` column written by the SWAT+ Editor has no effect.

If the `event` column of [`codes.bsn`](codes-bsn.md) is not 0, one more word is read after the 56th value: a plant class name of up to 25 characters (for example `row_crop`). In that case the plant class takes the place of the description.

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `name` | - | - | Name of the plant or land cover, up to 40 characters. Must be unique. |
| 2 | `plnt_typ` | - | - | Plant type: `warm_annual`, `cold_annual`, `warm_annual_tuber`, `cold_annual_tuber` or `perennial`. See [Plant types](#plant-types). |
| 3 | `gro_trig` | - | - | Growth trigger: `temp_gro` (growth driven by temperature and day length) or `moisture_gro` (tropical plants whose growth starts with the monsoon). |
| 4 | `nfix_co` | - | 0.0 | Nitrogen fixation coefficient: 0.5 for legumes, 0 for non-legumes. Any value above 0 lets the plant fix nitrogen when soil nitrate cannot meet its demand. |
| 5 | `days_mat` | days | 110 | Days to maturity, an integer. Used to compute the heat units to maturity. 0 means the plant uses the heat units of the whole year. See [Heat units to maturity](#heat-units-to-maturity). |
| 6 | `bm_e` | (kg/ha)/(MJ/m²) | 15.0 | Biomass-energy ratio (radiation use efficiency): dry biomass produced, including roots, per unit of intercepted photosynthetically active radiation, with no stress, at ambient CO2 and a vapor pressure deficit of 1 kPa. |
| 7 | `harv_idx` | (kg/ha)/(kg/ha) | 0.76 | Harvest index for optimal growing conditions: fraction of above-ground biomass removed as yield. Values above 0.7 are replaced by 0.02 (see [Values set by the model](#values-set-by-the-model)). |
| 8 | `lai_pot` | m²/m² | 5.0 | Maximum potential leaf area index. Values are limited to 0 to 10. |
| 9 | `frac_hu1` | fraction | 0.05 | Fraction of heat units to maturity at the 1st point of the optimal leaf area development curve. |
| 10 | `lai_max1` | fraction | 0.05 | Fraction of `lai_pot` at the 1st point of the optimal leaf area development curve. |
| 11 | `frac_hu2` | fraction | 0.40 | Fraction of heat units to maturity at the 2nd point of the optimal leaf area development curve. |
| 12 | `lai_max2` | fraction | 0.95 | Fraction of `lai_pot` at the 2nd point of the optimal leaf area development curve. |
| 13 | `hu_lai_decl` | fraction | 0.99 | Fraction of heat units to maturity at which leaf area starts to decline. |
| 14 | `dlai_rate` | - | 1.0 | Exponent of the leaf area decline of annuals after `hu_lai_decl`. 1 gives a linear decline. |
| 15 | `can_ht_max` | m | 6.0 | Maximum canopy height. |
| 16 | `rt_dp_max` | m | 3.5 | Maximum rooting depth. The soil profile depth also limits roots. |
| 17 | `tmp_opt` | °C | 30.0 | Optimal temperature for plant growth. |
| 18 | `tmp_base` | °C | 10.0 | Base (minimum) temperature for plant growth. Heat units accumulate only above it. |
| 19 | `frac_n_yld` | kg N/kg yield | 0.0015 | Fraction of nitrogen in the yield, dry weight. |
| 20 | `frac_p_yld` | kg P/kg yield | 0.0003 | Fraction of phosphorus in the yield, dry weight. |
| 21 | `frac_n_em` | kg N/kg biomass | 0.006 | Normal fraction of nitrogen in plant biomass at emergence. |
| 22 | `frac_n_50` | kg N/kg biomass | 0.002 | Normal fraction of nitrogen in plant biomass at 50% maturity. |
| 23 | `frac_n_mat` | kg N/kg biomass | 0.0015 | Normal fraction of nitrogen in plant biomass at maturity. |
| 24 | `frac_p_em` | kg P/kg biomass | 0.0007 | Normal fraction of phosphorus in plant biomass at emergence. |
| 25 | `frac_p_50` | kg P/kg biomass | 0.0004 | Normal fraction of phosphorus in plant biomass at 50% maturity. |
| 26 | `frac_p_mat` | kg P/kg biomass | 0.0003 | Normal fraction of phosphorus in plant biomass at maturity. |
| 27 | `harv_idx_ws` | (kg/ha)/(kg/ha) | 0.01 | Harvest index under severe water stress: the lowest harvest index expected, between 0 and `harv_idx`. |
| 28 | `usle_c_min` | - | 0.001 | Minimum USLE C factor for water erosion. Values are limited to 0.001 to 1. |
| 29 | `stcon_max` | m/s | 0.002 | Maximum stomatal conductance at high solar radiation and low vapor pressure deficit. Used with the Penman-Monteith ET method. |
| 30 | `vpd` | kPa | 4.0 | Vapor pressure deficit at the 2nd point of the stomatal conductance curve. |
| 31 | `frac_stcon` | fraction | 0.75 | Fraction of `stcon_max` at the 2nd point of the stomatal conductance curve. |
| 32 | `ru_vpd` | (kg/ha)/(MJ/m²)/kPa | 8.0 | Rate of decline in radiation use efficiency per unit increase in vapor pressure deficit above 1 kPa. 0 turns the adjustment off. |
| 33 | `co2_hi` | µL CO2/L air | 660.0 | Elevated CO2 concentration at the 2nd point of the radiation use efficiency curve. |
| 34 | `bm_e_hi` | (kg/ha)/(MJ/m²) | 16.0 | Biomass-energy ratio at the CO2 concentration `co2_hi`. |
| 35 | `plnt_decomp` | - | 0.05 | Plant residue decomposition coefficient: fraction of residue that decomposes in a day under optimal moisture, temperature, C:N and C:P. 0 takes `rsd_decomp` from [`parameters.bsn`](parameters-bsn.md). |
| 36 | `lai_min` | m²/m² | 0.75 | Minimum leaf area index of perennials during the dormant period. |
| 37 | `bm_tree_acc` | - | 0.3 | Exponent that limits the maximum leaf area index of young perennials. See [Perennials and trees](#perennials-and-trees). |
| 38 | `yrs_mat` | years | 10 | Years for a perennial to reach full development, an integer. Values below 1 are set to 1. |
| 39 | `bm_tree_max` | t/ha | 1000.0 | Maximum above-ground biomass. Checked once a year. |
| 40 | `ext_co` | - | 0.65 | Light extinction coefficient for intercepted photosynthetically active radiation. 0 is replaced by 0.65. |
| 41 | `leaf_tov_mn` | months | 12.0 | Leaf turnover time of `moisture_gro` perennials with minimum stress. Called `leaf_tov_min` in earlier documentation. |
| 42 | `leaf_tov_mx` | months | 3.0 | Leaf turnover time of `moisture_gro` perennials with maximum stress. Called `leaf_tov_max` in earlier documentation. |
| 43 | `bm_dieoff` | fraction | 0.0 | Factor on the excess biomass removed when above-ground biomass exceeds `bm_tree_max`. 0 is replaced by 1. |
| 44 | `rt_st_beg` | fraction | 0.0 | Root to shoot ratio at the start of the growing season. 0 is replaced by 0.4. |
| 45 | `rt_st_end` | fraction | 0.0 | Root to shoot ratio at the end of the growing season. 0 is replaced by 0.2. Tuber types always use 0.7. |
| 46 | `plnt_pop1` | plants/m² | 0.0 | Plant population at the 1st point of the population and leaf area curve. |
| 47 | `frac_lai1` | fraction | 0.0 | Fraction of `lai_pot` at the 1st point of the population and leaf area curve. |
| 48 | `plnt_pop2` | plants/m² | 0.0 | Plant population at the 2nd point of the population and leaf area curve. |
| 49 | `frac_lai2` | fraction | 0.0 | Fraction of `lai_pot` at the 2nd point of the population and leaf area curve. |
| 50 | `frac_sw_gro` | - | 0.5 | Intended as the 30-day precipitation to PET ratio that starts growth of `moisture_gro` plants. Read but not used, which uses a fixed 0.5. |
| 51 | `aeration` | fraction | 0.2 | Aeration stress threshold: the fraction of pore space above field capacity that can fill with water before the plant is stressed by lack of air. 0 is replaced by 0.2. |
| 52 | `rsd_pctcov` | - | 0.0 | Residue factor for the percent cover equation. 0 is replaced by 0.4. |
| 53 | `rsd_covfac` | - | 0.0 | Residue factor for the surface cover (C factor) equation. 0 is replaced by 0.04. |
| 54 | `avg_lig_frac` | fraction | 0.85 | Average lignin fraction of residue. Read but not used. |
| 55 | `ab_lig_frac` | fraction | 0.15 | Lignin fraction of above-ground residue. Used by the dynamic carbon model only. |
| 56 | `bg_lig_frac` | fraction | 0.12 | Lignin fraction of below-ground residue (roots). Used by the dynamic carbon model only. |

The defaults are the values SWAT+ uses for a component that is not set. They are not filled in for missing columns, since every row must have all 56 values.

## Plant types

`plnt_typ` decides how the plant goes through the year.

- `warm_annual` and `cold_annual` are annual crops. A `cold_annual` is planted in the fall and goes dormant over winter when day length falls below the dormancy threshold. Leaf area declines after `hu_lai_decl`, following `dlai_rate`.
- `warm_annual_tuber` and `cold_annual_tuber` are annuals whose yield is below ground. Their root to shoot ratio at the end of the season is fixed at 0.7.
- `perennial` covers grasses, shrubs and trees. Perennials go dormant when day length falls below the threshold, keep at least `lai_min` of leaf area, and develop over `yrs_mat` years.

`gro_trig` = `moisture_gro` is for tropical plants. If the plant was planted with the monsoon option, it starts growing when the 30-day ratio of precipitation to potential ET reaches 0.5. Leaf turnover of `moisture_gro` perennials varies between `leaf_tov_mx` and `leaf_tov_mn` months with moisture stress.

## Heat units to maturity

SWAT+ computes the heat units a plant needs to reach maturity at the start of the run, from the monthly mean temperatures of the HRU's weather generator station.

- `days_mat` = 0: the plant grows through the whole year. Heat units to maturity are 95% of the year's sum of mean daily temperature above `tmp_base`.
- `days_mat` > 0 for an annual: the planting date is taken as the day when the sum of mean daily temperatures above 0 °C reaches 15% of the annual sum. Heat units above `tmp_base` are then summed for `days_mat` days from that date.

The calculation works in both hemispheres. Giving the days of a variety (for example 90, 100, 110 or 120 days for corn) lets one database support several varieties. If `days_mat` is longer than the growing season at a site, the heat units of the whole season are used.

## Leaf area development

The optimal leaf area index follows a curve through two points, (`frac_hu1`, `lai_max1`) and (`frac_hu2`, `lai_max2`), where the first value is the fraction of heat units to maturity and the second the fraction of `lai_pot`:

$$f_{LAI} = \frac{f_{PHU}}{f_{PHU} + \exp(l_1 - l_2\,f_{PHU})}$$

$l_1$ and $l_2$ are set at the start of the run so that the curve passes through both points. The values of `lai_pot` in the standard database are for typical plant densities in rainfed agriculture. Drought-prone regions with low planting densities, or irrigated land with high densities, may need different values. Canopy height grows with the square root of $f_{LAI}$ up to `can_ht_max`.

When `plnt_pop1` and `plnt_pop2` are given, a second curve through (`plnt_pop1`, `frac_lai1`) and (`plnt_pop2`, `frac_lai2`) limits `lai_pot` by plant population.

## Radiation use efficiency

When the `co2` column of [`parameters.bsn`](parameters-bsn.md) is above 350 µL/L, radiation use efficiency is adjusted for CO2 along a curve through (330 µL/L, `bm_e`) and (`co2_hi`, `bm_e_hi`). Otherwise `bm_e` is used as given. Values for `co2_hi` and `bm_e_hi` are needed even when climate change is not simulated, and `bm_e_hi` should be larger than `bm_e`. A `co2_hi` of 330 is replaced by 660.

When the vapor pressure deficit is above 1 kPa, radiation use efficiency drops by `ru_vpd` for each kPa above 1, down to no less than 27% of `bm_e`. A value of 6 to 8 is a reasonable approximation for most plants, and 0 turns the adjustment off.

## Perennials and trees

The maximum leaf area index of a perennial grows with its age:

$$LAI_{max} = \mathrm{lai\_pot} \left(\frac{y}{\mathrm{yrs\_mat}}\right)^{\mathrm{bm\_tree\_acc}}$$

where $y$ is the number of years since the plant was established (at least 1), and $LAI_{max}$ is at most `lai_pot`. With `bm_tree_acc` = 0 the plant reaches `lai_pot` in its first year.

At the end of each year, if above-ground biomass $B$ exceeds `bm_tree_max` (converted to kg/ha), the amount

$$D = (1 + \mathrm{bm\_dieoff})\,(B - 1000\,\mathrm{bm\_tree\_max})$$

dies and goes to the residue pools, with roots in the same proportion. Nothing dies if $D$ is not smaller than $B$. A mature forest stand typically has 30 to 50 t/ha of biomass. `bm_dieoff` is not used at the start of dormancy in 62.0.1.

## Nutrient uptake

The six fractions `frac_n_em` to `frac_p_mat` describe the nitrogen and phosphorus content of the whole plant, roots included, on a dry weight basis, at emergence, at 50% maturity and at maturity. They set the plant's nutrient demand through the season. Each fraction must be smaller than the one before it: if `frac_n_50` is not at least 0.0001 below `frac_n_em`, it is set to `frac_n_em` − 0.0001, and if `frac_n_mat` is not at least 0.0001 below `frac_n_50`, it is multiplied by 0.75. The phosphorus fractions are treated the same way.

## Residue lignin

With `carbon` = 2 in [`codes.bsn`](codes-bsn.md), residue entering the soil is split into metabolic, structural and lignin pools. Below ground, the lignin fraction is `bg_lig_frac`, the structural fraction is `bg_lig_frac` / 0.8, and the rest is metabolic. Above ground the same split uses `ab_lig_frac`. With `carbon` = 0 these columns are not used.

## Values set by the model

After the file is read, SWAT+ changes some values:

| Column | Change |
|--------|--------|
| `harv_idx` | Values above 0.7 are set to 0.02. |
| `lai_pot` | Limited to 0 to 10. |
| `usle_c_min` | Limited to 0.001 to 1. |
| `plnt_decomp` | 0 is replaced by `rsd_decomp` of [`parameters.bsn`](../input-reference/parameters-bsn.md). |
| `yrs_mat` | Values below 1 are set to 1. |
| `ext_co` | 0 is replaced by 0.65. |
| `bm_dieoff` | 0 is replaced by 1. |
| `rt_st_beg`, `rt_st_end` | 0 is replaced by 0.4 and 0.2. Tuber types get `rt_st_end` = 0.7. |
| `aeration`, `rsd_pctcov`, `rsd_covfac` | 0 is replaced by 0.2, 0.4 and 0.04. |
| `co2_hi` | 330 is replaced by 660. |
| `frac_n_50`, `frac_n_mat`, `frac_p_50`, `frac_p_mat` | Adjusted to decrease, as described above. |

The `harv_idx` change affects crops whose harvest index is above 0.7, such as alfalfa (0.9 in the standard database) and tuber crops with a harvest index above 1. Their harvest index becomes 0.02.

## Calibration

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md): `bio_e` (`bm_e`), `hvsti` (`harv_idx`), `rdmx` (`rt_dp_max`), `t_opt` (`tmp_opt`), `t_base` (`tmp_base`) and `usle_c` (`usle_c_min`).

## Example

The first rows of `refdata/Ames_sub1/plants.plt` in the SWAT+ repository:

```
plants.plt
name  plnt_typ  gro_trig  nfix_co  days_mat  bm_e  harv_idx  lai_pot  frac_hu1  lai_max1  frac_hu2  lai_max2  hu_lai_decl  dlai_rate  can_ht_max  rt_dp_max  tmp_opt  tmp_base  frac_n_yld  frac_p_yld  frac_n_em  frac_n_50  frac_n_mat  frac_p_em  frac_p_50  frac_p_mat  harv_idx_ws  usle_c_min  stcon_max  vpd  frac_stcon  ru_vpd  co2_hi  bm_e_hi  plnt_decomp  lai_min  bm_tree_acc  yrs_mat  bm_tree_max  ext_co  leaf_tov_mn  leaf_tov_mx  bm_dieoff  rt_st_beg  rt_st_end  plnt_pop1  frac_lai1  plnt_pop2  frac_lai2  frac_sw_gro  aeration  rsd_pctcov  rsd_covfac  avg_lig_frac  ab_lig_frac  bg_lig_frac  description
alfa  perennial  temp_gro  0.5  0  20  0.9  4  0.15  0.01  0.5  0.95  0.9  0.5  0.9  3  20  4  0.02  0.0035  0.04  0.02  0.02  0.0035  0.0028  0.002  0.9  0.01  0.01  4  0.75  10  660  35  0.05  0  0.3  2  0  0.65  12  3  0.1  0.4  0.2  0  0  0  0  0.5  0.2  0.5  0.07  0.1214  0.0900  0.2000  alfalfa
cana  warm_annual  temp_gro  0  100  34  0.3  4.5  0.15  0.02  0.45  0.95  0.5  0.3  1.3  1.4  21  5  0.03  0.0079  0.04  0.01  0.01  0.0074  0.0037  0.0023  0.01  0.2  0.006  4  0.75  10  660  40  0.05  0  0  0  0  0.65  12  3  0.1  0.4  0.2  0  0  0  0  0.5  0.2  0.53  0.028  0.1190  0.1050  0.2100  canola_spring_argentine
```

- `alfa` (alfalfa) is a perennial legume (`nfix_co` = 0.5) with `days_mat` = 0, so it uses the heat units of the whole year. Its `harv_idx` of 0.9 is replaced by 0.02.
- `alfa` has `frac_n_50` = `frac_n_mat` = 0.02, so `frac_n_mat` is multiplied by 0.75 to 0.015.
- `bm_tree_max` is 0 for both rows. With `bm_dieoff` = 0.1, $D = 1.1\,B$ at the end of the year, which is not smaller than $B$, so no biomass dies off.
- Ames_sub1 has `event` = 0 and `carbon` = 2 in [`codes.bsn`](../input-reference/codes-bsn.md). No plant class is read, so the `description` column is ignored, and the lignin columns are used: for `alfa`, 9% of decomposing surface residue and 20% of root residue entering the soil goes to the lignin pool. `avg_lig_frac` is read but has no effect.

## Related files

- [`plant.ini`](ini.md): plant communities for HRUs, by plant name.
- [`management.sch`](management.md) and [decision tables](dtl.md): plant, harvest and kill operations name plants from this file.
- [`landuse.lum`](lum.md): land uses and their plant communities.
- [`codes.bsn`](codes-bsn.md): `event` switches the plant class column on; `carbon` selects whether the lignin fractions are used.
- [`parameters.bsn`](parameters-bsn.md): `rsd_decomp` replaces a `plnt_decomp` of 0.
- [Weather generator](cli.md): monthly temperatures used for heat units to maturity.

??? quote "Sources"

    - Reader: [`plant_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_parm_read.f90)
    - Type definition: `type plant_db` and `type residue_partition_fracs` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90)
    - Derived values and overrides: [`plantparm_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plantparm_init.f90)
    - Heat units to maturity: [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90)
    - Growth: [`pl_leaf_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_leaf_gro.f90), [`pl_leaf_senes.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_leaf_senes.f90), [`pl_root_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_root_gro.f90), [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90), [`pl_dormant.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_dormant.f90), [`pl_mortality.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_mortality.f90), [`pl_nfix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nfix.f90), [`pl_waterup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_waterup.f90)
    - Monsoon trigger: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Residue lignin: [`cbn_rsd_transfer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_rsd_transfer.f90), [`cbn_surfrsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_surfrsd_decomp.f90)
    - Calibration parameters: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `pldb%plantnm` |
    | `plnt_typ` | `pldb%typ` |
    | `gro_trig` | `pldb%trig` |
    | `days_mat` | `pldb%days_mat` |
    | `bm_e` | `pldb%bio_e` |
    | `harv_idx` | `pldb%hvsti` |
    | `lai_pot` | `pldb%blai` |
    | `frac_hu1`, `lai_max1` | `pldb%frgrw1`, `pldb%laimx1` |
    | `frac_hu2`, `lai_max2` | `pldb%frgrw2`, `pldb%laimx2` |
    | `hu_lai_decl` | `pldb%dlai` |
    | `can_ht_max` | `pldb%chtmx` |
    | `rt_dp_max` | `pldb%rdmx` |
    | `tmp_opt`, `tmp_base` | `pldb%t_opt`, `pldb%t_base` |
    | `frac_n_yld`, `frac_p_yld` | `pldb%cnyld`, `pldb%cpyld` |
    | `frac_n_em`, `frac_n_50`, `frac_n_mat` | `pldb%pltnfr1`, `pltnfr2`, `pltnfr3` |
    | `frac_p_em`, `frac_p_50`, `frac_p_mat` | `pldb%pltpfr1`, `pltpfr2`, `pltpfr3` |
    | `harv_idx_ws` | `pldb%wsyf` |
    | `usle_c_min` | `pldb%usle_c` |
    | `stcon_max` | `pldb%gsi` |
    | `vpd` | `pldb%vpdfr` |
    | `frac_stcon` | `pldb%gmaxfr` |
    | `ru_vpd` | `pldb%wavp` |
    | `co2_hi`, `bm_e_hi` | `pldb%co2hi`, `pldb%bioehi` |
    | `plnt_decomp` | `pldb%rsdco_pl` |
    | `lai_min` | `pldb%alai_min` |
    | `bm_tree_acc` | `pldb%laixco_tree` |
    | `yrs_mat` | `pldb%mat_yrs` |
    | `bm_tree_max` | `pldb%bmx_peren` |
    | `ext_co` | `pldb%ext_coef` |
    | `leaf_tov_mn`, `leaf_tov_mx` | `pldb%leaf_tov_min`, `pldb%leaf_tov_max` |
    | `rt_st_beg`, `rt_st_end` | `pldb%rsr1`, `pldb%rsr2` |
    | `plnt_pop1`, `frac_lai1` | `pldb%pop1`, `pldb%frlai1` |
    | `plnt_pop2`, `frac_lai2` | `pldb%pop2`, `pldb%frlai2` |
    | `frac_sw_gro` | `pldb%frsw_gro` |
    | `avg_lig_frac` | `pldb%res_part_fracs%meta_frac` |
    | `ab_lig_frac` | `pldb%res_part_fracs%str_frac` |
    | `bg_lig_frac` | `pldb%res_part_fracs%lig_frac` |
    | plant class (`event` /= 0) | `pl_class` |
    | `event` in codes.bsn | `bsn_cc%nam1` |

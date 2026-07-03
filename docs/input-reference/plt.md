---
title: "plants.plt"
description: Plant parameter database. Growth, phenology, biomass, and nutrient parameters for every plant the simulation can grow.
status: review
verified_against:
  - src/plant_parm_read.f90
  - src/plant_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`plants.plt` holds one parameter set per plant species the model can grow. Each record fills a `plant_db` entry in the `pldb` array. Plant growth, phenology, biomass-to-energy conversion, root and canopy geometry, nutrient uptake, and residue partition fractions all come from this file. HRU plant communities (`plant.ini`) and management operations (`plant.ops`, `landuse.lum`) reference these records by name.

## Source

- Reader: [`src/plant_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/plant_parm_read.f90)
- Type definition: [`src/plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/plant_data_module.f90), `type plant_db`

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one record per plant. List-directed read into `pldb(ic)` (`type plant_db`). The last sub-object is `res_part_fracs` (`type residue_partition_fracs`), which contributes three trailing fields.

The reader has a conditional branch:

```fortran
if (bsn_cc%nam1 == 0) then
  read (104,*,iostat=eof) pldb(ic)
else
  read (104,*,iostat=eof) pldb(ic), pl_class(ic)
end if
```

`bsn_cc%nam1` is a switch in `codes.bsn`. With the default `nam1 = 0`, the standard column list below applies. With `nam1 /= 0`, one extra `pl_class` token (a 25-character name like `row_crop`, `tree`, `grass`) is read at the end of each record.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | plantnm | char(40) | none | "" | plant name (used as the key from other files) |
| 2 | typ | char(18) | none | "" | plant category: `warm_annual`, `cold_annual`, `warm_annual_tuber`, `cold_annual_tuber`, `perennial` |
| 3 | trig | char(18) | none | "" | phenology trigger: `moisture_gro` or `temp_gro` |
| 4 | nfix_co | real | none | 0.0 | nitrogen fixation coefficient (0.5 for legumes, 0 for non-legumes) |
| 5 | days_mat | int | days | 110 | days to maturity. If 0, heat units run the entire growing season |
| 6 | bio_e | real | (kg/ha)/(MJ/m^2) | 15.0 | biomass-energy ratio |
| 7 | hvsti | real | (kg/ha)/(kg/ha) | 0.76 | harvest index: crop yield over above-ground biomass |
| 8 | blai | real | none | 5.0 | maximum potential leaf area index |
| 9 | frgrw1 | real | fraction | 0.05 | fraction of growing season at the 1st point on the optimal LAI curve |
| 10 | laimx1 | real | fraction | 0.05 | fraction of maximum LAI at the 1st point on the optimal LAI curve |
| 11 | frgrw2 | real | fraction | 0.4 | fraction of growing season at the 2nd point on the optimal LAI curve |
| 12 | laimx2 | real | fraction | 0.95 | fraction of maximum LAI at the 2nd point on the optimal LAI curve |
| 13 | dlai | real | fraction | 0.99 | fraction of growing season when LAI starts to decline |
| 14 | dlai_rate | real | none | 1.0 | exponent governing LAI decline rate |
| 15 | chtmx | real | m | 6.0 | maximum canopy height |
| 16 | rdmx | real | m | 3.5 | maximum root depth |
| 17 | t_opt | real | deg C | 30.0 | optimal temperature for plant growth |
| 18 | t_base | real | deg C | 10.0 | minimum (base) temperature for plant growth |
| 19 | cnyld | real | kg N / kg yield | 0.0015 | fraction of nitrogen in yield |
| 20 | cpyld | real | kg P / kg yield | 0.0003 | fraction of phosphorus in yield |
| 21 | pltnfr1 | real | kg N / kg biomass | 0.006 | nitrogen uptake parameter 1 (emergence) |
| 22 | pltnfr2 | real | kg N / kg biomass | 0.002 | nitrogen uptake parameter 2 (mid-season) |
| 23 | pltnfr3 | real | kg N / kg biomass | 0.0015 | nitrogen uptake parameter 3 (maturity) |
| 24 | pltpfr1 | real | kg P / kg biomass | 0.0007 | phosphorus uptake parameter 1 (emergence) |
| 25 | pltpfr2 | real | kg P / kg biomass | 0.0004 | phosphorus uptake parameter 2 (mid-season) |
| 26 | pltpfr3 | real | kg P / kg biomass | 0.0003 | phosphorus uptake parameter 3 (maturity) |
| 27 | wsyf | real | (kg/ha)/(kg/ha) | 0.01 | lower bound of harvest index under water stress |
| 28 | usle_c | real | none | 0.001 | minimum value of the USLE C factor for water erosion |
| 29 | gsi | real | m/s | 0.002 | maximum stomatal conductance |
| 30 | vpdfr | real | kPa | 4.0 | vapor pressure deficit at which `gmaxfr` is valid |
| 31 | gmaxfr | real | none | 0.75 | fraction of maximum stomatal conductance achieved at `vpdfr` |
| 32 | wavp | real | none | 8.0 | rate of decline in radiation use efficiency per unit VPD |
| 33 | co2hi | real | uL CO2 / L air | 660.0 | elevated CO2 concentration at the 2nd point on the RUE-CO2 curve |
| 34 | bioehi | real | (kg/ha)/(MJ/m^2) | 16.0 | biomass-energy ratio at the elevated CO2 level (`co2hi`) |
| 35 | rsdco_pl | real | none | 0.05 | plant residue decomposition coefficient |
| 36 | alai_min | real | m^2/m^2 | 0.75 | minimum LAI during winter dormant period |
| 37 | laixco_tree | real | none | 0.3 | coefficient used to estimate maximum LAI during tree growth |
| 38 | mat_yrs | int | years | 10 | years to maturity (forced to at least 1 by the reader) |
| 39 | bmx_peren | real | metric tons/ha | 1000.0 | maximum biomass for forest |
| 40 | ext_coef | real | none | 0.65 | light extinction coefficient |
| 41 | leaf_tov_min | real | months | 12.0 | perennial leaf turnover rate with minimum stress |
| 42 | leaf_tov_max | real | months | 3.0 | perennial leaf turnover rate with maximum stress |
| 43 | bm_dieoff | real | fraction | 0.0 | above-ground biomass that dies off at dormancy |
| 44 | rsr1 | real | fraction | 0.0 | initial root-to-shoot ratio at the beginning of the growing season |
| 45 | rsr2 | real | fraction | 0.0 | root-to-shoot ratio at the end of the growing season |
| 46 | pop1 | real | plants/m^2 | 0.0 | plant population at the 1st point on the population-LAI curve |
| 47 | frlai1 | real | fraction | 0.0 | fraction of maximum LAI at the 1st point on the population-LAI curve |
| 48 | pop2 | real | plants/m^2 | 0.0 | plant population at the 2nd point on the population-LAI curve |
| 49 | frlai2 | real | fraction | 0.0 | fraction of maximum LAI at the 2nd point on the population-LAI curve |
| 50 | frsw_gro | real | fraction | 0.5 | 30-day sum of P-PET that triggers monsoon-season growth in tropical plants |
| 51 | aeration | real | none | 0.2 | aeration stress factor |
| 52 | rsd_pctcov | real | none | 0.0 | residue factor for the percent cover equation |
| 53 | rsd_covfac | real | none | 0.0 | residue factor for the surface cover (C factor) equation |
| 54 | res_part_fracs%meta_frac | real | fraction | 0.85 | metabolic fraction of residue |
| 55 | res_part_fracs%str_frac | real | fraction | 0.15 | structural fraction of residue |
| 56 | res_part_fracs%lig_frac | real | fraction | 0.12 | lignin fraction of residue |

When `cswat = 2` in `codes.bsn`, the three residue partition fractions are reinterpreted into above- and below-ground metabolic, structural, and lignin pools (`cswat_1_part_fracs`) in `plant_parm_read`. When `cswat /= 2`, the reader overwrites the read values with hard-coded defaults of 0.85, 0.15, and 0.12.

## Example

First two records of `refdata/Ames_sub1/plants.plt`:

```
plants.plt
name  plnt_typ  gro_trig  nfix_co  days_mat  bm_e  harv_idx  lai_pot  frac_hu1  lai_max1  frac_hu2  lai_max2  hu_lai_decl  dlai_rate  can_ht_max  rt_dp_max  tmp_opt  tmp_base  frac_n_yld  frac_p_yld  frac_n_em  frac_n_50  frac_n_mat  frac_p_em  frac_p_50  frac_p_mat  harv_idx_ws  usle_c_min  stcon_max  vpd  frac_stcon  ru_vpd  co2_hi  bm_e_hi  plnt_decomp  lai_min  bm_tree_acc  yrs_mat  bm_tree_max  ext_co  leaf_tov_mn  leaf_tov_mx  bm_dieoff  rt_st_beg  rt_st_end  plnt_pop1  frac_lai1  plnt_pop2  frac_lai2  frac_sw_gro  aeration  rsd_pctcov  rsd_covfac  avg_lig_frac  ab_lig_frac  bg_lig_frac  description
alfa  perennial  temp_gro  0.5  0  20  0.9  4  0.15  0.01  0.5  0.95  0.9  0.5  0.9  3  20  4  0.02  0.0035  0.04  0.02  0.02  0.0035  0.0028  0.002  0.9  0.01  0.01  4  0.75  10  660  35  0.05  0  0.3  2  0  0.65  12  3  0.1  0.4  0.2  0  0  0  0  0.5  0.2  0.5  0.07  0.1214  0.0900  0.2000  alfalfa
cana  warm_annual  temp_gro  0  100  34  0.3  4.5  0.15  0.02  0.45  0.95  0.5  0.3  1.3  1.4  21  5  0.03  0.0079  0.04  0.01  0.01  0.0074  0.0037  0.0023  0.01  0.2  0.006  4  0.75  10  660  40  0.05  0  0  0  0  0.65  12  3  0.1  0.4  0.2  0  0  0  0  0.5  0.2  0.53  0.028  0.1190  0.1050  0.2100  canola_spring_argentine
```

Notes on the example:

- Header column names written by the editor (`plnt_typ`, `gro_trig`, `bm_e`, `harv_idx`, `lai_pot`, `frac_hu1`, `frac_n_yld`, `frac_n_em`, `stcon_max`, `frac_stcon`, `ru_vpd`, `co2_hi`, `bm_e_hi`, `plnt_decomp`, `lai_min`, `bm_tree_acc`, `yrs_mat`, `bm_tree_max`, `ext_co`, `leaf_tov_mn`, `leaf_tov_mx`, `rt_st_beg`, `rt_st_end`, `plnt_pop1`, `frac_lai1`, `frac_sw_gro`, `avg_lig_frac`, `ab_lig_frac`, `bg_lig_frac`) do not match the field names in the source. The reader uses position only.
- The trailing `description` column is not part of `plant_db`. List-directed reads stop after the type is filled, so the description is silently discarded.
- For `alfa`, `days_mat = 0` is the explicit "use heat units for the full season" signal.

## Related files

- [`codes.bsn`](../input-reference/codes-bsn.md). `bsn_cc%nam1` selects whether `pl_class` is read after each record. `bsn_cc%cswat` selects how residue partition fractions are interpreted.
- `plant.ini`. Lists which plants are present in each HRU at the start of simulation, keyed by `plantnm`.
- [`landuse.lum`](../input-reference/lum.md) and `plant.ops`. Reference plant names from this file in management schedules.

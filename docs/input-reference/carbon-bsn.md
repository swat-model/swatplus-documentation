---
title: carbon.bsn
description: Basin-wide scalar carbon parameters. One record of 28 values controlling initial pool fractions, water coupling, manure partitioning, consolidation, temperature and water factor selectors, biomixing and tillage curves, photodegradation, residue C:N / C:P controls, and the slow-humus initialization method.
status: new
verified_against:
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
  - src/tillage_data_module.f90
  - src/plant_data_module.f90
  - src/input_file_module.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

## Purpose

`carbon.bsn` holds the basin-wide scalar coefficients for the SWAT+ carbon module. The reader fills `org_frac`, `cb_wtr_coef`, `man_coef`, and `org_con` (all defined in [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_module.f90)), the basin-scope tillage variables in [`tillage_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/tillage_data_module.f90) (`bio_consf`, `till_consf`, `bmix_a/b/c`, `tillmix_a/b/c`, `till_eff_days`), the `photo_degrade_factor` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/plant_data_module.f90), and the five residue-decomposition tunables (`n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref`) promoted from hard-coded constants into module-scope reals in `carbon_module.f90`.

`carbon.bsn` replaces the legacy `carb_coefs.cbn` (keyword-style) and works alongside the per-layer file [`carbon_lyr.bsn`](carbon-lyr-bsn.md), which holds the rate constants and CO2 fractions that differ between the surface and subsurface layer groups.

## Source

- Reader: [`src/carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_bsn_read.f90)
- Filename slot: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_basin`, field `carbon_bsn = "carbon.bsn"`.
- Target types: `organic_fractions`, `carbon_water_coef`, `manure_coef`, `organic_controls` in [`src/carbon_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_module.f90); module-scope reals `n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref` in the same module; `bio_consf`, `till_consf`, `till_eff_days`, `bmix_a/b/c`, `tillmix_a/b/c` in [`src/tillage_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/tillage_data_module.f90); `photo_degrade_factor` in [`src/plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/plant_data_module.f90).

## Activation

The reader runs only when `bsn_cc%cswat == 2` (set in [`codes.bsn`](codes-bsn.md)). When `cswat == 2` the file is **required**: if `carbon.bsn` (or its companion `carbon_lyr.bsn`) is missing or its data row cannot be parsed, the reader writes an error message to stdout and unit 9001 and calls `error stop`. There is no silent fallback to compiled defaults. `carbon_bsn_read.f90` returns early for any other `cswat` value, so `cswat = 1` (the reserved C-FARM slot) does not read this file.

The dynamic carbon model activates on `cswat = 2`, matching legacy SWAT numbering (1 = C-FARM, 2 = CENTURY). It was previously `cswat = 1`; existing `codes.bsn` files left at `carbon = 1` now run with the carbon model off and must be changed to `carbon = 2`.

`carbon.bsn` is listed in the BASIN row of `file.cio` alongside `codes.bsn` and `parameters.bsn` (three columns). `carbon_lyr.bsn` rides at a fixed name beside it and does not appear in `file.cio`.

!!! note
    The legacy `cbn_diag` first column is retired. Output gating now lives entirely in [`print.prt`](print-prt.md) through the `hru_cb_*` and `lsu_cb_*` rows (see the [carbon outputs reference](../output-reference/carbon.md)).

## Format

- Line 1: title (skipped).
- Line 2: column header (skipped).
- Line 3: 28 values, list-directed, read into the target fields in the order below. (The 28th value, `mathers_method`, was added when carbonDev merged to main; 27-value files from before the merge fail to parse and must add the trailing column.)

Values are space-delimited. Position is significant; the column header is decorative.

| # | Field | Type | Target | Units | Description |
|---|-------|------|--------|-------|-------------|
| 1 | `init_seq` | real | `org_frac%frac_seq` | fraction | initial fraction of total soil carbon held in the sequestered pool |
| 2 | `init_microb` | real | `org_frac%frac_hum_microb` | fraction | initial microbial-humus fraction of non-sequestered carbon |
| 3 | `init_slow` | real | `org_frac%frac_hum_slow` | fraction | initial slow-humus fraction of non-sequestered carbon |
| 4 | `init_passive` | real | `org_frac%frac_hum_passive` | fraction | initial passive-humus fraction of non-sequestered carbon |
| 5 | `koc_c` | real | `cb_wtr_coef%prmt_21` | none | partition coefficient for carbon loss in water and sediment (formerly `prmt_21`) |
| 6 | `solc_ratio` | real | `cb_wtr_coef%prmt_44` | 0..1 | ratio of soluble C in surface runoff to soluble C in percolate (formerly `prmt_44`) |
| 7 | `till_eff_days` | real | `till_eff_days` | days | number of days a tillage event remains effective |
| 8 | `manure_c_frac` | real | `man_coef%rtof` | none | manure organic N and P partition between fresh and stable pools (formerly `rtof`) |
| 9 | `bio_consol` | real | `bio_consf` | none | biological consolidation factor for soil moisture mixing |
| 10 | `till_consol` | real | `till_consf` | none | tillage consolidation factor for soil moisture mixing |
| 11 | `tmpf_eqn` | int | `org_con%tmpf` | none | temperature factor selector (1, 2, or 3) used in `cbn_zhang2.f90` |
| 12 | `watf_eqn` | int | `org_con%watf` | none | water factor selector (1 or 2) used in `cbn_zhang2.f90` |
| 13 | `t_cbn_min` | real | `org_con%tn` | deg C | minimum temperature bound for `tmpf2` (lower limit of biological activity) |
| 14 | `t_cbn_opt` | real | `org_con%top` | deg C | optimum temperature for `tmpf2` |
| 15 | `t_cbn_max` | real | `org_con%tx` | deg C | maximum temperature bound for `tmpf2` (upper limit of biological activity) |
| 16 | `bmix_a` | real | `bmix_a` | none | biological mixing curve coefficient A (`mgt_tillfactor.f90` tillf option 4) |
| 17 | `bmix_b` | real | `bmix_b` | none | biological mixing curve coefficient B |
| 18 | `bmix_c` | real | `bmix_c` | none | biological mixing curve coefficient C |
| 19 | `tillmix_a` | real | `tillmix_a` | none | tillage mixing curve coefficient A |
| 20 | `tillmix_b` | real | `tillmix_b` | none | tillage mixing curve coefficient B |
| 21 | `tillmix_c` | real | `tillmix_c` | none | tillage mixing curve coefficient C |
| 22 | `sfc_rsd_photodeg` | real | `photo_degrade_factor` | 1/day | surface residue photodegradation rate factor |
| 23 | `n_act_frac` | real | `n_act_frac` | fraction | fraction of organic N held in the active humus pool (drives active-to-stable flow in `nut_nminrl.f90`) |
| 24 | `cnr_cap` | real | `cnr_cap` | none | upper cap on residue C:N ratio before computing the decomposition factor |
| 25 | `cnr_ref` | real | `cnr_ref` | none | reference C:N ratio where the C:N decomposition factor equals 1 |
| 26 | `cpr_cap` | real | `cpr_cap` | none | upper cap on residue C:P ratio before computing the decomposition factor |
| 27 | `cpr_ref` | real | `cpr_ref` | none | reference C:P ratio where the C:P decomposition factor equals 1 |
| 28 | `mathers_method` | int | `org_frac%mathers_method` | flag | slow-humus pool initialization: `0` original humus-slow init (default), `1` Mathers method (clay+silt based, from "Updating carbon pool initialization with DSSAT-CENTURY"). Used in `soil_nutcarb_init`. |

The reader does not interpret column 1-4 as a probability simplex; the four `init_*` values are used as supplied. The four target fields hold the fractional partitioning of soil carbon into sequestered, microbial-humus, slow-humus, and passive-humus pools at simulation start.

The `tmpf_eqn` (col 11) and `watf_eqn` (col 12) integers select between the temperature and water response equations encoded in `cbn_zhang2.f90`. They are integers in the file but the reader does not enforce that; the consuming code treats them as `int(real)`.

## Example

`refdata/Lafayette/carbon.bsn`:

```
carbon.bsn: basin-wide scalar carbon parameters (one record)
   init_seq   init_microb   init_slow   init_passive   koc_c   solc_ratio   till_eff_days   manure_c_frac   bio_consol   till_consol   tmpf_eqn   watf_eqn   t_cbn_min   t_cbn_opt   t_cbn_max   bmix_a   bmix_b   bmix_c   tillmix_a   tillmix_b   tillmix_c   sfc_rsd_photodeg   n_act_frac   cnr_cap   cnr_ref   cpr_cap   cpr_ref   mathers_method
       0.95        0.02        0.44        0.54        1000         0.5         100        0.50        0.15        0.10           2           1        -0.5        30.0        50.0         3.0         5.0        -5.5         3.0        15.0        -3.5       0.001        0.02       500.0        25.0      5000.0       200.0                0
```

## Calibration

Eighteen of the 28 fields are wired in `cal_parm_select.f90` and may be touched through [`calibration.cal`](../calibration/parameter-change-files.md): `init_seq`, `init_microb`, `init_slow`, `init_passive`, `koc_c`, `solc_ratio`, `manure_c_frac`, `bio_consol`, `till_consol`, `sfc_rsd_photodeg`, `n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref`, `t_cbn_min`, `t_cbn_opt`, `t_cbn_max`. The six bmix/tillmix curve coefficients are also wired. The selector integers (`tmpf_eqn`, `watf_eqn`) and the integer-valued `till_eff_days` are not calibrated.

!!! warning
    `proc_cal` must run **before** `soil_nutcarb_init` for the `init_*` calibration values to take effect. The current `main.f90` already orders these correctly; do not reorder.

## Related files

- [`carbon_lyr.bsn`](carbon-lyr-bsn.md). Per-layer rate constants and CO2 allocation fractions.
- [`codes.bsn`](codes-bsn.md). The `cswat` switch that gates this file.
- [`print.prt`](print-prt.md). Output gating for the carbon families.
- [Soil carbon (model theory)](../model-theory/carbon.md). Equations and pool structure.
- [Parameter change files](../calibration/parameter-change-files.md). Calibration entries for the wired carbon parameters.

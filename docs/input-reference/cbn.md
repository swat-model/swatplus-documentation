---
title: carb_coefs.cbn (deprecated)
description: The legacy carb_coefs.cbn keyword file has been removed. Carbon inputs now live in carbon.bsn and carbon_lyr.bsn.
status: deprecated
verified_against:
  - src/carbon_bsn_read.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

!!! warning "Removed"
    `carb_coefs.cbn` was removed. The keyword-style reader (`carbon_coef_read.f90`) and the dead companion file `basins_carbon.tes` have also been deleted. The 22 daily hard-coded coefficient overrides that previously lived in `cbn_zhang2.f90` are gone; user-supplied values now flow end-to-end.

## What replaces it

Carbon inputs have been split into two flat-table files that follow the same layout convention as the rest of the SWAT+ inputs (title line, header line, data rows):

- [`carbon.bsn`](carbon-bsn.md): 28 basin-wide scalar parameters in a single data row. Initial pool fractions, water coupling, manure partitioning, temperature and water factor selectors, the `t_cbn_*` triple, biomixing and tillage curves, photodegradation, residue C:N / C:P controls, and the slow-humus initialization method (`mathers_method`).
- [`carbon_lyr.bsn`](carbon-lyr-bsn.md) — per-layer rate constants and CO2 allocation fractions. One row per layer group (1 = top, 2 = subsurface).

Both files are required when `bsn_cc%cswat == 2` (the dynamic carbon model; the activation value moved from 1 to 2). Either missing or malformed file triggers `error stop`; there is no silent fallback to compiled defaults.

## Migration

| Old keyword in `carb_coefs.cbn` | New location |
|---|---|
| `cbn_diagnostics` | retired; output gating now lives in [`print.prt`](print-prt.md) via the `hru_cb_*` and `lsu_cb_*` rows |
| `hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp` | per-layer rows of [`carbon_lyr.bsn`](carbon-lyr-bsn.md) |
| `a1co2`, `asco2`, `apco2`, `abco2` | per-layer rows of [`carbon_lyr.bsn`](carbon-lyr-bsn.md) |
| `org_frac` (`frac_seq`, `frac_hum_microb`, `frac_hum_slow`, `frac_hum_passive`) | `init_seq`, `init_microb`, `init_slow`, `init_passive` columns of [`carbon.bsn`](carbon-bsn.md) |
| `prmt_21` | `koc_c` column of [`carbon.bsn`](carbon-bsn.md) |
| `prmt_44` | `solc_ratio` column of [`carbon.bsn`](carbon-bsn.md) |
| `till_eff_days` | `till_eff_days` column of [`carbon.bsn`](carbon-bsn.md) |
| `rtof` | `manure_c_frac` column of [`carbon.bsn`](carbon-bsn.md) |
| `cbn_consolidation_factors` (2 values) | `bio_consol`, `till_consol` columns of [`carbon.bsn`](carbon-bsn.md) |
| `cbn_factor_approaches` (2 ints) | `tmpf_eqn`, `watf_eqn` columns of [`carbon.bsn`](carbon-bsn.md) |
| `tn`, `top`, `tx` | `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` columns of [`carbon.bsn`](carbon-bsn.md) |
| `zz_bmix_coefs` (3 values) | `bmix_a`, `bmix_b`, `bmix_c` columns of [`carbon.bsn`](carbon-bsn.md). `zz_` prefix dropped to match the column name. |
| `zz_emix_coefs` (3 values) | `tillmix_a`, `tillmix_b`, `tillmix_c` columns of [`carbon.bsn`](carbon-bsn.md) |
| `photo_degrade_factor` | `sfc_rsd_photodeg` column of [`carbon.bsn`](carbon-bsn.md) |
| `nmbr_soil_test_layers`, `soil_test` | retired; no replacement (sub-table was unused downstream) |

Five new tunables were promoted from hard-coded constants and added to [`carbon.bsn`](carbon-bsn.md):

- `n_act_frac` (formerly the `nactfr` local in `nut_nminrl.f90`)
- `cnr_cap`, `cnr_ref` (formerly the 500 and 25 hard-coded values in `cbn_surfrsd_decomp.f90`)
- `cpr_cap`, `cpr_ref` (formerly the 5000 and 200 hard-coded values in `cbn_surfrsd_decomp.f90`)

## Related files

- [`carbon.bsn`](carbon-bsn.md). Replacement for the basin-wide scalars.
- [`carbon_lyr.bsn`](carbon-lyr-bsn.md). Replacement for the per-layer table.
- [`codes.bsn`](codes-bsn.md). The `cswat` switch. `cswat == 2` and `cswat == 3` are no longer accepted; set `0` (no carbon) or `1` (active carbon).
- [Carbon outputs](../output-reference/carbon.md). Replacement for the `cbn_diagnostics` flag.

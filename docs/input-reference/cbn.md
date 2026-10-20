---
title: carb_coefs.cbn (removed)
description: The keyword file carb_coefs.cbn is no longer read. Its settings moved to carbon.bsn and carbon_lyr.bsn, and its output switch to print.prt.
status: deprecated
verified_against:
  - src/carbon_bsn_read.f90
  - src/carbon_layers_read.f90
  - src/carbon_module.f90
  - src/basin_module.f90
  - src/basin_print_codes_read.f90
  - src/proc_bsn.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

`carb_coefs.cbn` is no longer read.

!!! warning "Removed"
    SWAT+ 62.0.1 ignores a copy of `carb_coefs.cbn` left in the run directory. Its settings now come from [`carbon.bsn`](carbon-bsn.md) and [`carbon_lyr.bsn`](carbon-lyr-bsn.md).

## Replacement files

The dynamic carbon model is switched on with `carbon` = 2 in [`codes.bsn`](codes-bsn.md). In earlier revisions the value was 1; in 62.0.1 the value 1 is reserved for the C-FARM model, which is not implemented. With `carbon` = 0 soil carbon is static and neither replacement file is read.

With `carbon` = 2 SWAT+ needs two files, both with a title line, a header line and data rows like other SWAT+ inputs:

- [`carbon.bsn`](carbon-bsn.md): one row of 28 basin-wide values. It is named on the basin line of [`file.cio`](file-cio.md) (default [`carbon.bsn`](../input-reference/carbon-bsn.md)).
- [`carbon_lyr.bsn`](carbon-lyr-bsn.md): decomposition rates and CO2 fractions, one row for the top soil layer (`layer` 1) and one for the layers below (`layer` 2). Its name is built from the [`carbon.bsn`](../input-reference/carbon-bsn.md) name by adding `_lyr` before the extension, so it is not listed in [`file.cio`](../input-reference/file-cio.md).

If either file is missing, or [`carbon.bsn`](../input-reference/carbon-bsn.md) does not have 28 values, SWAT+ stops with an error. There is no fallback to built-in values.

An optional file `carbon_layers.prt` sets how many soil layers the per-layer carbon outputs include. Without it, the outputs cover the largest number of layers of any HRU.

## Keyword migration

| Keyword in `carb_coefs.cbn` | Replacement |
|---|---|
| `cbn_diagnostics` | Removed. Carbon outputs are switched on per file in [`print.prt`](print-prt.md) with the `hru_cb_*` and `lsu_cb_*` rows. |
| `hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp` | Columns of the same names in [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md). |
| `a1co2`, `asco2`, `apco2`, `abco2` | Columns of the same names in [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md). |
| `org_frac` (4 values) | `init_seq`, `init_microb`, `init_slow`, `init_passive` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `prmt_21` | `koc_c` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `prmt_44` | `solc_ratio` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `till_eff_days` | `till_eff_days` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `rtof` | `manure_c_frac` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `cbn_consolidation_factors` (2 values) | `bio_consol`, `till_consol` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `cbn_factor_approaches` (2 values) | `tmpf_eqn`, `watf_eqn` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `tn`, `top`, `tx` | `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `zz_bmix_coefs` (3 values) | `bmix_a`, `bmix_b`, `bmix_c` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `zz_emix_coefs` (3 values) | `tillmix_a`, `tillmix_b`, `tillmix_c` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `photo_degrade_factor` | `sfc_rsd_photodeg` in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| `nmbr_soil_test_layers`, `soil_test` | Removed, no replacement. |

Six values that were fixed in the code are now columns of [`carbon.bsn`](../input-reference/carbon-bsn.md): `n_act_frac` (fraction of humus nitrogen kept in the active pool), `cnr_cap` and `cnr_ref` (cap and reference C:N ratio of surface residue, formerly 500 and 25), `cpr_cap` and `cpr_ref` (cap and reference C:P ratio, formerly 5000 and 200), and `mathers_method` (method for the initial slow humus pool).

## Example

`refdata/Ames_sub1` in the SWAT+ repository has both replacement files, converted from its former `carb_coefs.cbn`:

```
carbon.bsn: derived from carb_coefs.cbn (basin carbon scalars)
          init_seq       init_microb         init_slow      init_passive             koc_c        solc_ratio     till_eff_days     manure_c_frac        bio_consol       till_consol          tmpf_eqn          watf_eqn         t_cbn_min         t_cbn_opt         t_cbn_max            bmix_a            bmix_b            bmix_c         tillmix_a         tillmix_b         tillmix_c  sfc_rsd_photodeg        n_act_frac           cnr_cap           cnr_ref           cpr_cap           cpr_ref    mathers_method
              0.95              0.02              0.44              0.54            1000.0               0.5               100               0.5              0.15              0.10                 2                 1              -0.5              30.0              50.0               3.0               5.0              -5.5               3.0              15.0              -3.5             0.001              0.02             500.0              25.0            5000.0             200.0                 1
```

```
carbon_lyr.bsn: derived from carb_coefs.cbn (per-layer carbon coefficients)
           layer         hp_rate         hs_rate     microb_rate       meta_rate        str_rate microb_top_rate           hs_hp           a1co2           asco2           apco2           abco2
               1         1.2e-05        2.92e-04          0.0164          0.0405          0.0107          0.0164            0.05            0.60            0.55            0.55            0.55
               2         1.2e-05        1.81e-04            0.02          0.0507          0.0134            0.02            0.05            0.55            0.55            0.55             0.0
```

## Related files

- [`carbon.bsn`](carbon-bsn.md) and [`carbon_lyr.bsn`](carbon-lyr-bsn.md): the replacement inputs.
- [`codes.bsn`](codes-bsn.md): the `carbon` switch.
- [`print.prt`](print-prt.md): carbon output switches.
- [Carbon outputs](../output-reference/carbon.md): the files written by the dynamic carbon model.

??? quote "Sources"

    - Readers: [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90) (reads `carbon.bsn` and `carbon_lyr.bsn`), [`carbon_layers_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_layers_read.f90), both called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Variables: [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90)
    - Carbon switch: `bsn_cc%cswat` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - Output switches: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)
    - File name slot: `in_basin%carbon_bsn` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

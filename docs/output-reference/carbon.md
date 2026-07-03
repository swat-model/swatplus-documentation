---
title: Carbon outputs
description: The carbon output family at HRU and LSU level. Ten HRU files and three LSU files, each with a dedicated print.prt row.
status: updated
verified_against:
  - src/output_landscape_init.f90
  - src/output_landscape_module.f90
  - src/hru_carbon_output.f90
  - src/lsu_carbon_output.f90
  - src/soil_nutcarb_write.f90
  - src/carbon_module.f90
  - src/basin_print_codes_read.f90
  - src/carbon_layers_read.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

## Purpose

The carbon output family reports the state and fluxes of the SWAT+ Century-style carbon module: per-HRU and per-LSU gain and loss totals, soil C transformations, per-layer pool composition, plant carbon state, and process drivers. The family supersedes the old sprawl of 47 files in 26 base names. Every file is opt-in through [`print.prt`](../input-reference/print-prt.md): each carbon family has its own row with the standard four-slot `d / m / y / a` layout.

The outputs are produced only when `bsn_cc%cswat == 2` (the dynamic carbon model; the activation value moved from 1 to 2). See [`codes.bsn`](../input-reference/codes-bsn.md) and the [carbon model theory](../model-theory/carbon.md).

## Source

- HRU writer: [`src/hru_carbon_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_carbon_output.f90) (gain/loss and transformations) and [`src/soil_nutcarb_write.f90`](https://github.com/swat-model/swatplus/blob/main/src/soil_nutcarb_write.f90) (per-layer pools, fluxes, drivers, dynamics, soil snapshot).
- LSU writer: [`src/lsu_carbon_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/lsu_carbon_output.f90).
- File opening and headers: [`src/output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_init.f90).
- Header types and variable-name lists: [`src/output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_module.f90) (`output_carb_gl_header`, `output_hscf_header`, ...); [`src/carbon_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_module.f90) (`cpool_vars`, `n_p_pool_vars`, `cflux_vars`, `carb_drv_vars`, `carb_dyn_vars`, `soil_snap_vars`).
- Per-family `print.prt` parsing: [`src/basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_print_codes_read.f90), `hru_cb_*` and `lsu_cb_*` case branches.

## File naming

Every file follows the canonical convention `<family>_{day,mon,yr,aa}.{txt,csv}`. The `_day` variant is daily, `_mon` is end-of-month, `_yr` is end-of-year, `_aa` is the average-annual record written once at end-of-simulation. The `hru_soil_snap` family uses `_tot` instead of `_aa` because an annual average of a snapshot pool is degenerate; the `_tot` file carries one begsim row and one endsim row, so `endsim_c - begsim_c` is the simulated SOC change per layer (see the carbon outputs reference).

CSV variants are emitted in parallel when `csvout = y` in `print.prt`. Both variants share the same column header and units row.

## Per-family print.prt gating

Each carbon family has its own row in the per-object output block of `print.prt`. The `basin_print_codes_read.f90` `case (...)` table accepts these names; each row is one object label followed by four flags (`d m y a`):

| `print.prt` row | Files gated | Output scope |
|---|---|---|
| `hru_cb_gl` | `hru_carb_gl_*.{txt,csv}` | HRU |
| `hru_cb_trf` | `hru_scf_*.{txt,csv}` | HRU |
| `hru_cb_lyr` | `hru_cbn_lyr_*.{txt,csv}` | HRU |
| `hru_cb_cpool` | `hru_cpool_stat_*.{txt,csv}` | HRU |
| `hru_cb_npool` | `hru_n_p_pool_stat_*.{txt,csv}` | HRU |
| `hru_cb_plt` | `hru_plc_stat_*.{txt,csv}` | HRU |
| `hru_cb_flux` | `hru_cflux_stat_*.{txt,csv}` | HRU |
| `hru_cb_drv` | `hru_carb_drv_*.{txt,csv}` | HRU |
| `hru_cb_dyn` | `hru_carb_dyn_*.{txt,csv}` | HRU |
| `hru_cb_snap` | `hru_soil_snap_*.{txt,csv}` (uses `_tot` instead of `_aa`) | HRU |
| `lsu_cb_gl` | `lsu_carb_gl_*.{txt,csv}` | LSU |
| `lsu_cb_trf` | `lsu_scf_*.{txt,csv}` | LSU |
| `lsu_cb_plt` | `lsu_plc_stat_*.{txt,csv}` | LSU |

The output restructure split the previous coarse `hru_cb` flag into the ten per-family flags above. The old `hru_cb` and `hru_cb_vars` rows now drive a parallel set of legacy CSU output files (see below), reinstated so the CSU team's existing workflows keep working alongside the standardised per-family files.

The LSU files are emitted only when `db_mx%lsu_out > 0` (the dataset contains routing units), regardless of the `lsu_cb_*` flag. Datasets without `rout_unit.con` populated do not create empty LSU carbon files.

## Legacy CSU carbon outputs

A second, older set of carbon output files runs alongside the standardised per-family files above. These are not exposed in SWAT+ Editor, so regular users do not see them; the CSU team adds the driving rows to `print.prt` by hand. This legacy path is temporary and is marked for removal in revision 63.

Two `print.prt` rows drive it, both read by `basin_print_codes_read.f90` and name-driven (a `print.prt` without them produces none of these files):

| `print.prt` row | When | Files |
|---|---|---|
| `hru_cb` | always when present | `hru_cbn_lyr`, `hru_seq_lyr`, `hru_n_p_pool_stat` |
| `hru_cb` = `l` (layer detail) | flag letter `l` turns diagnostics on | adds `hru_cpool_stat`, `hru_cflux_stat`, `hru_plc_stat`, `hru_begsim_soil_prop`, `hru_endsim_soil_prop`, `basin_carbon_all` |
| `hru_cb` = `y` (profile) | flag letter `y` | light set only (diagnostics off) |
| `hru_cb_vars` | requires carbon on (`cswat == 2`) | `hru_carbvars`, `hru_org_allo_vars`, `hru_org_ratio_vars`, `hru_org_trans_vars` |

Each file is written as `.txt`, plus `.csv` when `csvout = y` in `print.prt`.

The legacy and standardised files hold the same values in a different layout. For example, legacy `hru_cbn_lyr` (totals) plus `hru_seq_lyr` (sequestered) together equal the merged new `hru_cbn_lyr_yr`, which carries totals, sequestered, and depths in one wide table.

The internal `cbn_diagnostics` switch (which gates the heavy diagnostic files) is no longer read from an input file; it is set at startup from the `hru_cb` flag letter (`l` = on, `y` = off). Legacy output uses Fortran file units 8348-8387.

!!! note
    The `cbn_diagnostics` flag in the old `carb_coefs.cbn` is retired. Output gating now lives entirely in `print.prt`.

## HRU files

### `hru_carb_gl_*` (family `hru_cb_gl`)

Merged HRU carbon gain and loss totals. 21 value columns covering soil C balance, residue C balance, and plant C balance. Replaces the former `hru_soilcarb_*`, `hru_rescarb_*`, and `hru_plcarb_*` triplet. Units are `kg C/ha` for every value column.

Columns (in declaration order in `output_carb_gl_header`): `jday`, `mon`, `day`, `yr`, `unit`, `gis_id`, `name`, then `sed_c`, `surq_c`, `latq_c`, `perc_c`, `res_decay`, `man_app_c`, `man_graze_c`, `rsp_c`, `soil_emit_c`, `plant_surf_c`, `plant_root_c`, `rsd_surfdecay_c`, `rsd_rootdecay_c`, `harv_stov_c`, `rsd_emit_c`, `npp_c`, `harv_abgr_c`, `harv_root_c`, `drop_c`, `grazeat_c`, `plant_emit_c`.

The output restructure broke out four sub-fields that the previous output silently summed under a single label: `plant_surf_c`, `plant_root_c`, `harv_abgr_c`, `harv_root_c`.

### `hru_scf_*` (family `hru_cb_trf`)

HRU-level soil carbon transformations (the 13 inter-pool fluxes). One row per HRU per timestep.

Columns: `jday`, `mon`, `day`, `yr`, `unit`, `gis_id`, `name`, then `meta_micr`, `str_micr`, `str_hs`, `co2_meta`, `co2_str`, `micr_hs`, `micr_hp`, `hs_micr`, `hs_hp`, `hp_micr`, `co2_micr`, `co2_hs`, `co2_hp`.

### `hru_cbn_lyr_*` (family `hru_cb_lyr`)

Per-layer total soil carbon, written wide (one row per HRU per timestep with per-layer columns). The number of layers in the output is `cb_n_layers`. When the optional `carbon_layers.prt` is absent this defaults to the largest soil layer count across all HRUs, so the deepest profile is written in full; when the file is present it fixes the count to the value given. Each row carries that HRU's own layer depths, and layers a soil does not have are filled with the sentinel `-99`.

Header is built at first data write and carries the structure `layer depth (mm) | total_c_lyr1 | total_c_lyr2 | ... | total_c_lyrN`. Units: `Mg C/ha` per layer column.

### `hru_cpool_stat_*` (family `hru_cb_cpool`)

Per-layer C pools. Wide layout, with the columns in `cpool_vars` (`src/carbon_module.f90:20`) expanded to `<var>_lyr1 ... <var>_lyrN`:

```
residue_c, structural_c, metabolic_c, hs_c, hp_c, microbial_c,
lignin_c, nonlignin_c, root_mass, soil_water
```

10 variables x `cb_n_layers` columns. Units are kg C/ha for the C pools, kg/ha for `root_mass`, mm for `soil_water`.

### `hru_n_p_pool_stat_*` (family `hru_cb_npool`)

Per-layer N and P content of the carbon pools. Variables in `n_p_pool_vars`:

```
tot_pool_n, residue_n, structural_n, metabolic_n, hs_n, hp_n,
microbial_n, lignin_n, nonlignin_n,
tot_pool_p, residue_p, structural_p, metabolic_p, hs_p, hp_p,
microbial_p, lignin_p, nonlignin_p
```

18 variables x `cb_n_layers` columns. Units kg N/ha or kg P/ha as the column name implies.

### `hru_plc_stat_*` (family `hru_cb_plt`)

HRU-level plant carbon state. No per-layer expansion. Seven flat columns:

```
total_c, ab_gr_c, leaf_c, stem_c, seed_c, root_c, surf_rsd_c
```

Units kg C/ha.

### `hru_cflux_stat_*` (family `hru_cb_flux`)

Per-layer C and N fluxes from the Century pool transformations. Variables in `cflux_vars` (37 entries):

```
cfmets1, cfstrs1, cfstrs2,                          (C flows from litter)
efmets1, efstrs1, efstrs2,                          (E = effective C)
immmets1, immstrs1, immstrs2,                       (immobilisation)
mnrmets1, mnrstrs1, mnrstrs2,                       (mineralisation)
co2fmet, co2fstr,                                   (CO2 from litter)
cfs1s2, cfs1s3, cfs2s1, cfs2s3, cfs3s1,             (inter-SOC pool C flows)
efs1s2, efs1s3, efs2s1, efs2s3, efs3s1,
imms1s2, imms1s3, imms2s1, imms2s3, imms3s1,
mnrs1s2, mnrs1s3, mnrs2s1, mnrs2s3, mnrs3s1,
co2fs1, co2fs2, co2fs3                              (CO2 from SOC pools)
```

37 variables x `cb_n_layers` columns. Pool indices: `s1` = microbial, `s2` = slow humus, `s3` = passive humus, `met` = metabolic litter, `str` = structural litter.

### `hru_carb_drv_*` (family `hru_cb_drv`)

Per-layer environmental drivers and intermediate factors for the Century transformations. Variables in `carb_drv_vars` (14 entries):

```
sut, tillagef, cons_bmix, tillagef_biomix, tillagef_tillmix,
till_eff, cdg, ox, cs, no3, nh4, co2_resp, soil_temp, emix
```

14 variables x `cb_n_layers` columns. `sut`, `cdg`, `ox`, `cs` are dimensionless factors; `no3`, `nh4` are kg/ha; `co2_resp` is kg C/ha; `soil_temp` is deg C; `tillagef*`, `till_eff`, `cons_bmix`, `emix` are dimensionless.

### `hru_carb_dyn_*` (family `hru_cb_dyn`)

Per-layer carbon pool dynamics: allocation fractions and the C-to-N ratios of each pool transformation. Variables in `carb_dyn_vars` (21 entries):

```
asp, abp, abco2, a1co2, asco2, apco2,               (CO2 / passive allocations)
ncbm, nchp, nchs,                                   (N:C of microbial, passive, slow)
bmctp, bmntp, hsctp, hsntp, hpctp, hpntp,           (pool C and N totals)
lmctp, lmntp, lsctp, lslctp, lslnctp, lsntp         (litter pool totals)
```

21 variables x `cb_n_layers` columns. Allocation fractions are dimensionless; pool totals are kg C/ha or kg N/ha.

### `hru_soil_snap_*` (family `hru_cb_snap`)

Per-layer soil snapshot. Uses `_tot` in place of `_aa` because an annual average of a snapshot is degenerate.

Variables in `soil_snap_vars` (13 entries):

```
bd, awc, soil_k, tot_c, clay, silt, sand, rock,
alb, usle_k, ec, caco3, ph
```

13 variables x `cb_n_layers` columns.

The `_day`, `_mon`, `_yr` files emit end-of-period rows on the usual cadence. The `_tot` file is special: it emits one row at simulation begin (`begsim`) and one at simulation end (`endsim`). Both rows carry pool values in the same unit (`kg C/ha` for `tot_c`), so `endsim_tot_c_lyrK - begsim_tot_c_lyrK` is the simulated SOC change for layer K. The previous design wrote a percentage on the begsim row and a mass on the endsim row, which made the delta meaningless.

## LSU files

The LSU files are area-weighted HRU aggregates produced by `lsu_carbon_output.f90`. Per-layer families are **not** aggregated to LSU because different HRUs within an LSU can have different soil profiles.

### `lsu_carb_gl_*` (family `lsu_cb_gl`)

LSU-level carbon gain and loss totals, area-weighted from the HRU `hru_carb_gl_*` values. Reuses the `output_carb_gl_header` columns (same 21 value columns as the HRU file).

### `lsu_scf_*` (family `lsu_cb_trf`)

LSU-level soil C transformations, area-weighted from the HRU values. Reuses the `output_hscf_header` columns.

### `lsu_plc_stat_*` (family `lsu_cb_plt`)

LSU-level plant carbon, summed across HRUs with the `ru_frac` weight. Single value column `plant_c` (kg C/ha), printed once per LSU per timestep.

## Optional supporting file

### `carbon_layers.prt`

Optional file that fixes `cb_n_layers`, the number of soil layers expanded in every wide per-layer carbon file. It is only needed when you want a specific column count; if it is absent the model uses the largest soil layer count across all HRUs (see below). Format:

- Line 1: title (free text, skipped).
- Line 2: header (free text, skipped).
- Line 3: single integer giving the layer count.

Only line 3 carries data. The reader skips lines 1 and 2 entirely, so their text is for the reader's own benefit and may say anything. An integer below 1 is rejected and the automatic default is used instead.

### Example

```
carbon_layers.prt: layers to expand in per-layer carbon output
n_layers
10
```

Here line 1 is a free-text title, line 2 is a free-text header, and line 3 is the only value the reader uses. With `10`, every per-layer carbon file carries ten layer columns regardless of the soils present, and any unused slots are filled by `-99`. Use this to force a fixed column count, for example to truncate output to the top layers or to keep a constant width across runs.

If the file is absent, `cb_n_layers` defaults to the largest soil layer count across all HRUs. This means the deepest profile is written in full and no real layer is truncated; HRUs with fewer layers than that maximum get the sentinel `-99` in their extra slots. (Earlier versions defaulted to a fixed 7, which silently truncated deeper soils.) Reader: [`src/carbon_layers_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_layers_read.f90). Not listed in `file.cio`.

## Related pages

- [Carbon (model theory)](../model-theory/carbon.md). Pool definitions and Century-style transformation equations.
- [`carbon.bsn`](../input-reference/carbon-bsn.md). Basin-wide scalar inputs.
- [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md). Per-layer inputs.
- [`print.prt`](../input-reference/print-prt.md). Output gating.
- [Naming convention](../output-reference/naming-convention.md). Common naming rules across output files.

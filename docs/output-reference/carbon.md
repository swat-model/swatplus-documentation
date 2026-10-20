---
title: Carbon outputs
description: Soil, residue and plant carbon output files at HRU and landscape unit level, the print.prt rows that switch them on, their columns and units, and the older CSU carbon files that still run beside them.
status: review
verified_against:
  - src/basin_print_codes_read.f90
  - src/output_landscape_init.f90
  - src/output_landscape_module.f90
  - src/carbon_module.f90
  - src/carbon_layers_read.f90
  - src/hru_carbon_output.f90
  - src/lsu_carbon_output.f90
  - src/soil_nutcarb_write.f90
  - src/soil_carbvar_write.f90
  - src/carbon_legacy_module.f90
  - src/command.f90
  - src/hru_output.f90
  - src/hru_control.f90
  - src/lsu_read_elements.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The carbon output files report the carbon budget of the soil, residue and plants. Two kinds of file are available:

- Flat files with one row per HRU or landscape unit per interval: carbon gains and losses, soil carbon transformations and plant carbon.
- Per-layer files with one row per HRU per interval and one column per soil layer for each variable: soil carbon totals, carbon pools, N and P in the pools, carbon and N fluxes, process drivers, pool dynamics and soil properties.

Every family has a row in [`print.prt`](../input-reference/print-prt.md) with the usual daily, monthly, yearly and average annual flags. The rows are recognised only when [`print.prt`](../input-reference/print-prt.md) uses object labels (`use_obj_lbls = y`); in the fixed-order layout there is no place for them. A row name that SWAT+ does not know stops the run with an error.

Most columns are filled by the dynamic carbon model, which runs when `carbon = 2` in [`codes.bsn`](../input-reference/codes-bsn.md). Four per-layer families (`hru_cb_cpool`, `hru_cb_flux`, `hru_cb_drv`, `hru_cb_dyn`) are written only with `carbon = 2`. The other families are written for any setting, but with `carbon = 0` many of their columns stay at zero. See the [carbon model theory](../model-theory/carbon.md) for the pools and transformations.

## Files and switches

| [`print.prt`](../input-reference/print-prt.md) row | Files | Rows | Layers |
|-----------------|-------|------|--------|
| `hru_cb_gl` | `hru_carb_gl_{day,mon,yr,aa}` | HRU | no |
| `hru_cb_trf` | `hru_scf_{day,mon,yr,aa}` | HRU | no |
| `hru_cb_lyr` | `hru_cbn_lyr_{day,mon,yr,aa}` | HRU | yes |
| `hru_cb_cpool` | `hru_cpool_stat_{day,mon,yr,aa}` | HRU | yes, `carbon = 2` only |
| `hru_cb_npool` | `hru_n_p_pool_stat_{day,mon,yr,aa}` | HRU | yes |
| `hru_cb_plt` | `hru_plc_stat_{day,mon,yr,aa}` | HRU | no |
| `hru_cb_flux` | `hru_cflux_stat_{day,mon,yr,aa}` | HRU | yes, `carbon = 2` only |
| `hru_cb_drv` | `hru_carb_drv_{day,mon,yr,aa}` | HRU | yes, `carbon = 2` only |
| `hru_cb_dyn` | `hru_carb_dyn_{day,mon,yr,aa}` | HRU | yes, `carbon = 2` only |
| `hru_cb_snap` | `hru_soil_snap_{day,mon,yr}` and `hru_soil_snap_tot` | HRU | yes |
| `lsu_cb_gl` | `lsu_carb_gl_{day,mon,yr,aa}` | landscape unit | no |
| `lsu_cb_trf` | `lsu_scf_{day,mon,yr,aa}` | landscape unit | no |
| `lsu_cb_plt` | `lsu_plc_stat_{day,mon,yr,aa}` | landscape unit | no |

Each file is written as `.txt`, plus `.csv` when `csvout = y`. The `hru_cb_snap` row writes `_tot` in place of `_aa`; see [Soil snapshot](#soil-snapshot). The landscape unit files are written only when the model defines landscape units in [`ls_unit.def`](../input-reference/units.md#ls_unitdef).

Example [`print.prt`](../input-reference/print-prt.md) rows (labelled layout):

```
objects                  daily       monthly        yearly         avann
hru_cb_gl                    n             y             y             y
hru_cb_lyr                   n             n             y             y
hru_cb_snap                  n             n             n             y
```

## Value types and aggregation

The flat gain and loss files (`hru_carb_gl`, `hru_scf`, `lsu_carb_gl`, `lsu_scf`) report fluxes. Monthly and yearly files are sums over the interval, and the average annual file divides the run total by the number of printed years.

All other files report a state at the moment the row is written: the monthly file gives the value on the last day of the month, the yearly file the value on the last day of the year, and the average annual file the value at the end of the run. They are not averages. This also applies to the per-layer flux file `hru_cflux_stat`: its daily, monthly and yearly rows give the flux of the last day of the interval in kg/ha/day, and only the average annual file gives the run total divided by the number of printed years, in kg/ha/yr.

## Flat HRU files

### Carbon gains and losses

`hru_carb_gl_*` (row `hru_cb_gl`). One row per HRU. After the seven leading columns (`jday`, `mon`, `day`, `yr`, `unit`, `gis_id`, `name`) come 21 columns in kg C/ha, in three groups.

Soil:

| Column | Description |
|--------|-------------|
| `sed_c` | carbon removed with eroded sediment |
| `surq_c` | dissolved carbon in surface runoff |
| `latq_c` | dissolved organic carbon in lateral flow, all layers |
| `perc_c` | dissolved carbon in percolation below the profile |
| `res_decay` | carbon added to the soil by residue decay |
| `man_app_c` | carbon added with applied manure |
| `man_graze_c` | carbon added with manure from grazing animals |
| `rsp_c` | CO₂-C from soil respiration, whole profile |
| `soil_emit_c` | CO₂-C from burning soil carbon |

Residue:

| Column | Description |
|--------|-------------|
| `plant_surf_c` | carbon added to surface residue by leaf drop and kill |
| `plant_root_c` | carbon added to soil residue by root death |
| `rsd_surfdecay_c` | carbon lost from surface residue by decay |
| `rsd_rootdecay_c` | carbon lost from root and incorporated residue by decay |
| `harv_stov_c` | carbon removed by residue harvest |
| `rsd_emit_c` | CO₂-C from burning surface residue |

Plant:

| Column | Description |
|--------|-------------|
| `npp_c` | plant carbon growth (net primary production) |
| `harv_abgr_c` | carbon removed by grain and biomass harvest |
| `harv_root_c` | carbon removed by tuber (root) harvest |
| `drop_c` | carbon moved to residue by leaf drop and kill |
| `grazeat_c` | carbon eaten by grazing animals |
| `plant_emit_c` | CO₂-C from burning plants |

### Soil carbon transformations

`hru_scf_*` (row `hru_cb_trf`). One row per HRU with 13 columns in kg C/ha: `meta_micr`, `str_micr`, `str_hs`, `co2_meta`, `co2_str`, `micr_hs`, `micr_hp`, `hs_micr`, `hs_hp`, `hp_micr`, `co2_micr`, `co2_hs`, `co2_hp`. Each name gives the source and destination pool: `meta` metabolic litter, `str` structural litter, `micr` microbial biomass, `hs` slow humus, `hp` passive humus, and `co2` carbon lost as CO₂.

In 62.0.1 these columns are reset to zero each day and never filled, so every value in `hru_scf_*` and `lsu_scf_*` is zero. For the same flows by layer, use `hru_cflux_stat` (`cfmets1` for `meta_micr`, `co2fs1` for `co2_micr`, and so on).

### Plant carbon

`hru_plc_stat_*` (row `hru_cb_plt`). One row per HRU with seven columns in kg C/ha:

| Column | Description |
|--------|-------------|
| `total_c` | carbon in all plant parts |
| `ab_gr_c` | carbon in above-ground biomass |
| `leaf_c` | carbon in leaves |
| `stem_c` | carbon in stems |
| `seed_c` | carbon in seeds |
| `root_c` | carbon in roots |
| `surf_rsd_c` | carbon in residue |

## Per-layer HRU files

### Layout

Each row starts with the seven leading columns, then a depth block `depth_lyr1` to `depth_lyrN` giving the depth to the bottom of each soil layer in mm, then one block of N columns for each variable, named `<variable>_lyr1` to `<variable>_lyrN`. There is no units line: line 1 is the project name and version, line 2 the column header, and the data start on line 3.

N is the same for every HRU. By default it is the largest number of soil layers among all HRUs, so the deepest profile is written in full. The optional file [`carbon_layers.prt`](#layer-count-file) sets N directly. In an HRU with fewer layers than N, the extra columns contain `-99`.

### Soil carbon by layer

`hru_cbn_lyr_*` (row `hru_cb_lyr`). Line 1 ends with the note `total soil carbon (Mg/ha) by layer depth in mm`. The value columns are in Mg C/ha:

| Columns | Description |
|---------|-------------|
| `depth_lyr1` ... `depth_lyrN` | depth to the bottom of each layer (mm) |
| `tot_300_sum` | total soil organic carbon in the top 300 mm |
| `tot_lyr1` ... `tot_lyrN` | total soil organic carbon in each layer |
| `seq_300_sum` | sequestered (humus and microbial) carbon in the top 300 mm |
| `seq_lyr1` ... `seq_lyrN` | sequestered carbon in each layer |

For the 300 mm sums, the layer that crosses 300 mm is counted in proportion to its thickness above 300 mm. With `carbon = 0`, both totals are the sum of the active humus, stable humus and microbial carbon.

### Carbon pools

`hru_cpool_stat_*` (row `hru_cb_cpool`, `carbon = 2` only). Ten variables per layer:

| Variable | Units | Description |
|----------|-------|-------------|
| `residue_c` | kg C/ha | residue carbon in the layer |
| `structural_c` | kg C/ha | structural litter |
| `metabolic_c` | kg C/ha | metabolic litter |
| `hs_c` | kg C/ha | slow humus |
| `hp_c` | kg C/ha | passive humus |
| `microbial_c` | kg C/ha | microbial biomass |
| `lignin_c` | kg C/ha | lignin part of structural litter |
| `nonlignin_c` | kg C/ha | non-lignin part of structural litter |
| `root_mass` | kg/ha | root mass in the layer |
| `soil_water` | mm | water in the layer |

### N and P in the pools

`hru_n_p_pool_stat_*` (row `hru_cb_npool`). Eighteen variables per layer, in kg N/ha and kg P/ha: `tot_pool_n`, `residue_n`, `structural_n`, `metabolic_n`, `hs_n`, `hp_n`, `microbial_n`, `lignin_n`, `nonlignin_n`, then the same nine with `_p`. `tot_pool_n` and `tot_pool_p` add residue, structural and metabolic litter, slow and passive humus, microbial biomass, the dissolved organic pool and manure.

### Carbon and N fluxes

`hru_cflux_stat_*` (row `hru_cb_flux`, `carbon = 2` only). Thirty-seven variables per layer. In the names, `s1` is microbial biomass, `s2` slow humus, `s3` passive humus, `met` metabolic litter and `str` structural litter, so `cfs1s2` is the carbon flow from microbial biomass to slow humus.

| Variables | Units | Description |
|-----------|-------|-------------|
| `cfmets1`, `cfstrs1`, `cfstrs2` | kg C/ha/day | carbon moved from litter to microbial biomass or slow humus |
| `efmets1`, `efstrs1`, `efstrs2` | kg N/ha/day | nitrogen moved with those flows |
| `immmets1`, `immstrs1`, `immstrs2` | kg N/ha/day | N immobilised by the litter flows |
| `mnrmets1`, `mnrstrs1`, `mnrstrs2` | kg N/ha/day | N mineralised by the litter flows |
| `co2fmet`, `co2fstr` | kg C/ha/day | CO₂-C from metabolic and structural litter |
| `cfs1s2`, `cfs1s3`, `cfs2s1`, `cfs2s3`, `cfs3s1` | kg C/ha/day | carbon moved between the humus and microbial pools |
| `efs1s2`, `efs1s3`, `efs2s1`, `efs2s3`, `efs3s1` | kg N/ha/day | nitrogen moved with those flows |
| `imms1s2`, `imms1s3`, `imms2s1`, `imms2s3`, `imms3s1` | kg N/ha/day | N immobilised by those flows |
| `mnrs1s2`, `mnrs1s3`, `mnrs2s1`, `mnrs2s3`, `mnrs3s1` | kg N/ha/day | N mineralised by those flows |
| `co2fs1`, `co2fs2`, `co2fs3` | kg C/ha/day | CO₂-C from microbial biomass, slow humus and passive humus |

The average annual file gives yearly totals (kg/ha/yr); see [Value types and aggregation](#value-types-and-aggregation).

### Process drivers

`hru_carb_drv_*` (row `hru_cb_drv`, `carbon = 2` only). Fourteen variables per layer, all for the day the row is written:

| Variable | Units | Description |
|----------|-------|-------------|
| `sut` | fraction | soil water control on decomposition |
| `tillagef` | - | tillage factor of the layer |
| `cons_bmix` | - | biological mixing coefficient of the layer |
| `tillagef_biomix` | - | part of the tillage factor from biological mixing |
| `tillagef_tillmix` | - | part of the tillage factor from tillage operations |
| `till_eff` | fraction | tillage effect on decomposition |
| `cdg` | fraction | soil temperature control on decomposition |
| `ox` | fraction | oxygen control on decomposition |
| `cs` | fraction | combined control on decomposition |
| `no3` | kg N/ha | nitrate available to the transformations |
| `nh4` | kg N/ha | ammonium available to the transformations |
| `co2_resp` | kg C/ha | CO₂-C respired in the layer |
| `soil_temp` | °C | soil temperature |
| `emix` | fraction | fraction of the layer mixed by tillage or biological mixing |

### Pool dynamics

`hru_carb_dyn_*` (row `hru_cb_dyn`, `carbon = 2` only). Twenty-one variables per layer:

| Variables | Units | Description |
|-----------|-------|-------------|
| `asp`, `abp` | fraction | share of decomposed slow humus and of decomposed microbial biomass sent to passive humus |
| `abco2`, `a1co2`, `asco2`, `apco2` | fraction | share of decomposed microbial biomass, metabolic and passive pools, slow humus and passive humus lost as CO₂ |
| `ncbm`, `nchp`, `nchs` | ratio | N:C ratio of microbial biomass, passive humus and slow humus |
| `bmctp`, `bmntp` | kg/ha/day | potential C and N transformation of microbial biomass |
| `hsctp`, `hsntp` | kg/ha/day | potential C and N transformation of slow humus |
| `hpctp`, `hpntp` | kg/ha/day | potential C and N transformation of passive humus |
| `lmctp`, `lmntp` | kg/ha/day | potential C and N transformation of metabolic litter |
| `lsctp`, `lslctp`, `lslnctp`, `lsntp` | kg/ha/day | potential transformation of structural litter: C, lignin C, non-lignin C and N |

### Soil snapshot

`hru_soil_snap_*` (row `hru_cb_snap`). Thirteen soil properties per layer:

| Variable | Units | Description |
|----------|-------|-------------|
| `bd` | Mg/m³ | bulk density |
| `awc` | mm/mm | available water capacity |
| `soil_k` | mm/h | saturated hydraulic conductivity |
| `tot_c` | kg C/ha | total soil organic carbon |
| `clay`, `silt`, `sand`, `rock` | % | particle size fractions and rock fragments |
| `alb` | fraction | albedo |
| `usle_k` | - | USLE soil erodibility |
| `ec` | dS/m | electrical conductivity |
| `caco3` | % | calcium carbonate content |
| `ph` | - | soil pH |

The daily, monthly and yearly flags write `hru_soil_snap_day`, `_mon` and `_yr`. The average annual flag writes `hru_soil_snap_tot` instead, which has one row per HRU at the start of the run (marked `jday = 0`) and one at the end. Both rows give `tot_c` in kg C/ha, so the change in soil carbon in layer K over the run is `tot_c_lyrK` on the end row minus `tot_c_lyrK` on the start row. The start rows are written only when `carbon = 2`.

### Repeated rows

In 62.0.1 the files of the `hru_cb_lyr`, `hru_cb_cpool`, `hru_cb_npool`, `hru_cb_plt`, `hru_cb_flux`, `hru_cb_drv` and `hru_cb_dyn` rows, and the daily, monthly and yearly files of `hru_cb_snap`, repeat their block of HRU rows once per HRU. In a model with 12 HRUs, every interval has 144 rows: the 12 HRU rows written 12 times with the same values. Keep the first occurrence of each `unit` within an interval when reading these files. `hru_soil_snap_tot`, `hru_carb_gl`, `hru_scf` and the landscape unit files are not affected.

## Landscape unit files

The landscape unit files are area-weighted averages of the HRU values, each HRU weighted by its fraction of the landscape unit. Per-layer files have no landscape unit version because the HRUs in a unit can have different soil profiles.

| File | Columns |
|------|---------|
| `lsu_carb_gl_*` | the 21 columns of `hru_carb_gl` |
| `lsu_scf_*` | the 13 columns of `hru_scf` (all zero in 62.0.1) |
| `lsu_plc_stat_*` | one column, `lsu_plt_c`: carbon in all plant parts (kg C/ha) |

`lsu_plt_c` is a state value: the monthly, yearly and average annual files give the value on the last day of the interval.

## Layer count file

`carbon_layers.prt` is optional and is not listed in [`file.cio`](../input-reference/file-cio.md). When it is present in the run folder, it fixes N, the number of layer columns in every per-layer file. Use it to keep the same number of columns across runs, or to write only the top layers.

- Line 1: title, skipped.
- Line 2: header, skipped.
- Line 3: the number of layers, a whole number of 1 or more.

```
carbon_layers.prt: layers to expand in per-layer carbon output
n_layers
10
```

With `10`, every per-layer file has ten columns per variable, whatever the soils. A value below 1 is rejected with a message in `diagnostics.out`, and N then defaults to the largest layer count among the HRUs.

## Legacy CSU carbon outputs

An older set of carbon files, kept for existing CSU workflows, runs beside the files above. SWAT+ Editor does not write the rows that switch them on; they are added to [`print.prt`](../input-reference/print-prt.md) by hand. The code marks them for removal in revision 63.

| [`print.prt`](../input-reference/print-prt.md) row and flag | Files |
|--------------------------|-------|
| `hru_cb` with `y` or `l` in the daily, monthly or yearly column | `hru_cbn_lyr.txt`, `hru_seq_lyr.txt`, `hru_n_p_pool_stat.txt` |
| as above, with `l` in any column | adds `hru_begsim_soil_prop.txt` and `hru_endsim_soil_prop.txt` (the start rows need `carbon = 2`) |
| as above, with `carbon = 2` | adds `hru_plc_stat.txt`, `hru_cflux_stat.txt`, `hru_cpool_stat.txt` |
| `hru_cb` with any flag other than `n` | `basin_carbon_all.txt` (header lines only when `hru_nb` has `y` in the average annual column) |
| `hru_cb_vars` with `y` or `l` in the daily, monthly or yearly column, and `carbon = 2` | `hru_carbvars.txt`, `hru_org_allo_vars.txt`, `hru_org_ratio_vars.txt`, `hru_org_trans_vars.txt` |

These files have no interval suffix: one file collects the rows for every interval switched on. Each also gets a `.csv` copy when `csvout = y`. The legacy files contain the same quantities as the files above in a different layout. For example, legacy `hru_cbn_lyr.txt` and `hru_seq_lyr.txt` together contain the values that the new `hru_cbn_lyr_yr.txt` gives in one table.

The legacy files do not use the [layer count file](#layer-count-file). The `cbn_diagnostics` setting from the old [`carb_coefs.cbn`](../input-reference/cbn.md) no longer exists; the `l` flag on the `hru_cb` row takes its place.

## Example

Header and first row of `hru_carb_gl_yr.txt` from a two-year run of the `Ames_sub1` reference dataset with 62.0.1 (`carbon = 2`), shortened to the first eleven value columns:

```
        jday        mon        day         yr            unit              gis_id     name                   sed_c          surq_c          latq_c          perc_c       res_decay       man_app_c     man_graze_c           rsp_c     soil_emit_c    plant_surf_c    plant_root_c
                                                                                                           kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha         kg C/ha
         365          12          31        1975           1                     1 hru0001           0.7020391       18.35945      0.2045390      0.0000000E+00  0.0000000E+00  0.0000000E+00  0.0000000E+00   12925.00      0.0000000E+00   4012.786       2223.632
```

Start of the first data row of `hru_cbn_lyr_yr.txt` from the same run, as values per column. Every soil in this dataset has 16 layers, so N = 16 and no column contains `-99`:

| Column | Value |
|--------|-------|
| `unit` | 1 |
| `depth_lyr1` to `depth_lyr16` | 10, 25, 50, 100, 150, 200, 300, 450, 600, 750, 900, 1050, 1200, 1500, 1800, 2000 |
| `tot_300_sum` | 44.06 |
| `tot_lyr1`, `tot_lyr2`, `tot_lyr3` | 2.28, 2.55, 4.24 |

The 12 HRU rows for 1975 appear 12 times each in this file (see [Repeated rows](#repeated-rows)).

## Related files

- [`print.prt`](../input-reference/print-prt.md): output switches.
- [`codes.bsn`](../input-reference/codes-bsn.md): the `carbon` switch.
- [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md): carbon model inputs.
- [Carbon model theory](../model-theory/carbon.md): pools and transformations.
- [Naming convention](naming-convention.md): file suffixes and leading columns.

??? quote "Sources"

    - `print.prt` rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)
    - File opening and headers: [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90), header types `output_carb_gl_header` and `output_hscf_header` in [`output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_module.f90), variable lists and header and row helpers in [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90)
    - Flat HRU files: [`hru_carbon_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_carbon_output.f90) (units 4520 to 4527 and 4550 to 4557)
    - Per-layer files: [`soil_nutcarb_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_write.f90) and [`soil_carbvar_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_carbvar_write.f90) (units 4530 to 4605), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90) and, for the end-of-run snapshot, [`hru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_output.f90)
    - Landscape unit files: [`lsu_carbon_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_carbon_output.f90) (units 4750 to 4773), landscape unit count from [`lsu_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_read_elements.f90)
    - Layer count file: [`carbon_layers_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_layers_read.f90)
    - Legacy files: [`carbon_legacy_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_legacy_module.f90) (units 8348 to 8387)

    | `print.prt` row | Flag variable |
    |-----------------|---------------|
    | `hru_cb_gl`, `hru_cb_trf`, `hru_cb_lyr`, `hru_cb_cpool`, `hru_cb_npool` | `pco%cb_gl_hru`, `pco%cb_trf_hru`, `pco%cb_lyr_hru`, `pco%cb_cpool_hru`, `pco%cb_npool_hru` |
    | `hru_cb_plt`, `hru_cb_flux`, `hru_cb_drv`, `hru_cb_dyn`, `hru_cb_snap` | `pco%cb_plt_hru`, `pco%cb_flux_hru`, `pco%cb_drv_hru`, `pco%cb_dyn_hru`, `pco%cb_snap_hru` |
    | `lsu_cb_gl`, `lsu_cb_trf`, `lsu_cb_plt` | `pco%cb_gl_lsu`, `pco%cb_trf_lsu`, `pco%cb_plt_lsu` |
    | `hru_cb`, `hru_cb_vars` (legacy) | `pco%cb_hru`, `pco%cb_vars_hru` |

    | Output columns | Fortran source |
    |----------------|----------------|
    | `hru_carb_gl` | `hsc_d`, `hrc_d`, `hpc_d` (`carbon_soil_gain_losses`, `carbon_residue_gain_losses`, `carbon_plant_gain_losses`); `res_decay` is `rsd_decay_c`, `man_graze_c` is `man_graz_c`, the three `*_emit_c` columns are each type's `emit_c` |
    | `hru_scf` | `hscf_d` (`carbon_soil_transformations`) |
    | `tot_lyrK`, `seq_lyrK`, `tot_300_sum`, `seq_300_sum` | `soil1%tot(k)%c`, `soil1%seq(k)%c`, `soil1%tot_300_c`, `soil1%seq_tot_300_c`, all divided by 1000 |
    | `hru_cflux_stat` | `soil1%org_flx_lr(k)`; `_aa` uses `soil1%org_flx_cum_lr(k)` divided by `yrs_prt` |
    | `hru_carb_drv` | `soil1%org_con_lr(k)`, `soil%ly(k)%tillagef*`, `soil%ly(k)%bmix`, `soil%phys(k)%tmp`, `soil1%emix(k)` |
    | `hru_carb_dyn` | `soil1%org_allo_lr(k)`, `soil1%org_ratio_lr(k)`, `soil1%org_tran_lr(k)` |
    | `lsu_plt_c` | sum of `pl_mass%tot_com%c * lsu_elem%ru_frac` |

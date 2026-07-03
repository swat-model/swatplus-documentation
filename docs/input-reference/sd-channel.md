---
title: "sd_channel companion tables (hydrology.cha, sediment.cha, nutrients.cha)"
description: Per-channel hydrology, sediment, and nutrient parameter tables referenced by channel pointer files.
status: review
verified_against:
  - src/ch_read_hyd.f90
  - src/ch_read_sed.f90
  - src/ch_read_nut.f90
  - src/channel_data_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

This page documents the three per-channel parameter tables that hold hydraulic, sediment, and nutrient coefficients used inside the channel routing modules: `hydrology.cha`, `sediment.cha`, and `nutrients.cha`. Each is a flat database. Records are referenced by name from the pointer files [`channel.cha` (legacy)](../input-reference/cha.md) and [`channel-lte.cha` (SWAT+ deg)](../input-reference/cha.md). When the SWAT+ deg routine routes water and constituents through reaches listed under `chandeg.con`, the parameters in these tables drive the in-channel processes.

File names are declared in `type input_cha` in `src/input_file_module.f90` (`hyd`, `sed`, `nut`). Each file is optional. If the slot in `file.cio` is `null` or the file is missing, the reader allocates an empty array and the matching pointer is left at index 0.

## Source

- File names: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_cha`
- Readers:
  - [`src/ch_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read_hyd.f90)
  - [`src/ch_read_sed.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read_sed.f90)
  - [`src/ch_read_nut.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read_nut.f90)
- Type definitions: [`src/channel_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/channel_data_module.f90), types `channel_hyd_data`, `channel_sed_data`, `channel_nut_data`

Every reader skips two header lines, then reads one record per parameter set.

## hydrology.cha

Hydraulic and bank parameters for the original SWAT-style reach routine. Read into `ch_hyd` (`type channel_hyd_data`). The reader rewrites a few fields after read: `alpha_bnk` is replaced with `exp(-alpha_bnk)`, `s` is floored at 0.0001, `n` is clamped to `[0.01, 0.70]`, `l` is floored at 0.0010, `wdr` defaults to 3.5 if non-positive, and `side` defaults to 2.0 if non-positive.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "default" | parameter set name |
| 2 | w | real | m | 2.0 | average width of main channel |
| 3 | d | real | m | 0.5 | average depth of main channel |
| 4 | s | real | m/m | 0.01 | average slope of main channel |
| 5 | l | real | km | 0.1 | main channel length in subbasin |
| 6 | n | real | none | 0.05 | Manning's n |
| 7 | k | real | mm/hr | 0.01 | effective hydraulic conductivity of channel alluvium |
| 8 | wdr | real | m/m | 6.0 | channel width-to-depth ratio |
| 9 | alpha_bnk | real | days | 0.03 | alpha factor for bank storage recession (read as days, stored as `exp(-alpha_bnk)`) |
| 10 | side | real | none | 0.0 | channel side slope (horizontal per unit vertical) |

No example dataset in `refdata/` ships with `hydrology.cha`. The included reference datasets configure this slot as `null` in `file.cio` and use [`hyd-sed-lte.cha`](../input-reference/cha.md) instead.

## sediment.cha

Channel sediment routing parameters. Read into `ch_sed` (`type channel_sed_data`). The 12 monthly `erod` values follow the scalar fields. The reader clamps several values: cover and erodibility factors are bounded by the routing equation choice, bank and bed `d50` default to 50 and 500 micrometers if non-positive, bank and bed bulk density default to 1.40 and 1.50 g/cc if non-positive, and bank and bed jet-test erodibility default to 0.2 (or `0.2 / sqrt(tc_*)` if a critical shear stress is given). If all 12 monthly `erod` values are effectively zero, the reader fills the monthly array with `cov1`.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "" | parameter set name |
| 2 | eqn | int | none | 0 | sediment routing method. `0` original SWAT, `1` Bagnold, `2` Kodatie, `3` Molinas-Wu, `4` Yang |
| 3 | cov1 | real | none | 0.1 | channel erodibility factor (0..1 when `eqn = 0`, 0..25 otherwise) |
| 4 | cov2 | real | none | 0.1 | channel cover factor (same bounds as `cov1`) |
| 5 | bnk_bd | real | g/cc | 0.0 | bulk density of channel bank sediment (1.1..1.9) |
| 6 | bed_bd | real | g/cc | 0.0 | bulk density of channel bed sediment (1.1..1.9) |
| 7 | bnk_kd | real | cm^3/N/s | 0.0 | bank erodibility from jet test |
| 8 | bed_kd | real | cm^3/N/s | 0.0 | bed erodibility from jet test |
| 9 | bnk_d50 | real | micrometers | 0.0 | bank median particle diameter (clamped to 10000 max) |
| 10 | bed_d50 | real | micrometers | 0.0 | bed median particle diameter (clamped to 10000 max) |
| 11 | tc_bnk | real | N/m^2 | 0.0 | critical shear stress of channel bank |
| 12 | tc_bed | real | N/m^2 | 0.0 | critical shear stress of channel bed |
| 13..24 | erod(1..12) | real | none | 0.0 | monthly channel erodibility factor. `0.0` = non-erosive, `1.0` = no resistance to erosion |

No example dataset in `refdata/` ships with `sediment.cha`.

## nutrients.cha

In-stream nutrient cycling parameters. Read into `ch_nut` (`type channel_nut_data`). After read, several rate constants are scaled by the routing time step (`time%step`) so that values defined per day are converted to per-substep. The light half-saturation `k_l` is converted from kJ/(m^2 min) to MJ/(m^2 hr) by multiplying by 0.06. Defaults are applied (in place of zero) for every coefficient.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "" | parameter set name |
| 2 | onco | real | ppm | 0.0 | channel organic N concentration |
| 3 | opco | real | ppm | 0.0 | channel organic P concentration |
| 4 | rs1 | real | m/day | 1.0 | local algal settling rate at 20 deg C |
| 5 | rs2 | real | (mg disP-P)/(m^2 day) | 0.05 | benthos source rate for dissolved P at 20 deg C |
| 6 | rs3 | real | (mg NH4-N)/(m^2 day) | 0.5 | benthos source rate for ammonia at 20 deg C |
| 7 | rs4 | real | 1/day | 0.05 | organic N settling rate at 20 deg C |
| 8 | rs5 | real | 1/day | 0.05 | organic P settling rate at 20 deg C |
| 9 | rs6 | real | 1/day | 2.5 | settling rate for arbitrary non-conservative constituent |
| 10 | rs7 | real | (mg ANC)/(m^2 day) | 2.5 | benthal source rate for arbitrary non-conservative constituent |
| 11 | rk1 | real | 1/day | 1.71 | CBOD deoxygenation rate at 20 deg C |
| 12 | rk2 | real | 1/day | 1.0 | reaeration rate (Fickian) at 20 deg C |
| 13 | rk3 | real | 1/day | 2.0 | CBOD loss rate due to settling at 20 deg C |
| 14 | rk4 | real | (mg O2)/(m^2 day) | 0.0 | sediment oxygen demand at 20 deg C |
| 15 | rk5 | real | 1/day | 1.71 | coliform die-off rate |
| 16 | rk6 | real | 1/day | 1.71 | decay rate for arbitrary non-conservative constituent |
| 17 | bc1 | real | 1/hr | 0.55 | NH3 to NO2 biological oxidation rate at 20 deg C |
| 18 | bc2 | real | 1/hr | 1.1 | NO2 to NO3 biological oxidation rate at 20 deg C |
| 19 | bc3 | real | 1/hr | 0.21 | organic N to ammonia hydrolysis rate at 20 deg C |
| 20 | bc4 | real | 1/hr | 0.35 | organic P to dissolved P decay rate at 20 deg C |
| 21 | lao | real | none | 2.0 | QUAL2E light averaging option. Only option `2` is implemented in SWAT |
| 22 | igropt | int | none | 2 | algal growth limiting equation. `1` multiplicative, `2` limiting nutrient, `3` harmonic mean |
| 23 | ai0 | real | ug chla / mg alg | 50.0 | ratio of chlorophyll-a to algal biomass |
| 24 | ai1 | real | mg N / mg alg | 0.08 | nitrogen fraction of algal biomass |
| 25 | ai2 | real | mg P / mg alg | 0.015 | phosphorus fraction of algal biomass |
| 26 | ai3 | real | mg O2 / mg alg | 1.60 | rate of O2 production per unit of algal photosynthesis |
| 27 | ai4 | real | mg O2 / mg alg | 2.0 | rate of O2 uptake per unit of algal respiration |
| 28 | ai5 | real | mg O2 / mg N | 3.5 | rate of O2 uptake per unit of NH3 oxidation |
| 29 | ai6 | real | mg O2 / mg N | 1.07 | rate of O2 uptake per unit of NO2 oxidation |
| 30 | mumax | real | 1/hr | 2.0 | maximum specific algal growth rate at 20 deg C |
| 31 | rhoq | real | 1/day | 2.5 | algal respiration rate |
| 32 | tfact | real | none | 0.3 | fraction of solar radiation that is photosynthetically active |
| 33 | k_l | real | kJ/(m^2 min) read, stored as MJ/(m^2 hr) | 0.75 | light half-saturation coefficient |
| 34 | k_n | real | mg N / L | 0.02 | Michaelis-Menten N half-saturation constant |
| 35 | k_p | real | mg P / L | 0.025 | Michaelis-Menten P half-saturation constant |
| 36 | lambda0 | real | 1/m | 1.0 | non-algal portion of the light extinction coefficient |
| 37 | lambda1 | real | 1/(m * ug chla/L) | 0.03 | linear algal self-shading coefficient |
| 38 | lambda2 | real | (1/m)(ug chla/L)^(-2/3) | 0.054 | nonlinear algal self-shading coefficient |
| 39 | p_n | real | none | 0.5 | algal preference factor for ammonia |

Example from `refdata/Osu_1hru/nutrients.cha`:

```
nutrients.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                     plt_n         ptl_p       alg_stl      ben_disp      ben_nh3n      ptln_stl      ptlp_stl       cst_stl       ben_cst    cbn_bod_co        air_rt   cbn_bod_stl       ben_bod      bact_die     cst_decay     nh3n_no2n     no2n_no3n     ptln_nh3n     ptlp_solp    q2e_lt   q2e_alg      chla_alg         alg_n         alg_p   alg_o2_prod   alg_o2_resp       o2_nh3n       o2_no2n      alg_grow      alg_resp       slr_act         lt_co       const_n       const_p     lt_nonalg     alg_shd_l    alg_shd_nl      nh3_pref  description
nutcha1                0.00000       0.00000       1.00000       0.05000       0.50000       0.05000       0.05000       2.50000       2.50000       1.71000      50.00000       0.36000       2.00000       2.00000       1.71000       0.55000       1.10000       0.21000       0.35000         2         2      50.00000       0.08000       0.01500       1.60000       2.00000       3.50000       1.07000       2.00000       2.50000       0.30000       0.75000       0.02000       0.02500       1.00000       0.03000       0.05400       0.50000
```

Editor column names (`plt_n`, `ptl_p`, `alg_stl`, ...) do not match the source field names (`onco`, `opco`, `rs1`, ...). The reader uses position only.

Notes on the Osu_1hru example:

- Position 11 in this dataset (`cbn_bod_co = 1.71`) is `rk1` in the source.
- Position 13 (`cbn_bod_stl = 0.36`) is `rk3`. The source default is 2.0; this dataset overrides it.
- Position 14 (`ben_bod = 2.0`) is `rk4`. The source default is 0.0; this dataset overrides it.
- Positions 21 and 22 (`q2e_lt = 2`, `q2e_alg = 2`) are `lao` (read as real) and `igropt` (read as int).

## Related files

- [`*.cha` legacy channel files (`channel.cha`, `channel-lte.cha`, `hyd-sed-lte.cha`, `initial.cha`, `temperature.cha`)](../input-reference/cha.md). The pointer files that select records from `hydrology.cha`, `sediment.cha`, and `nutrients.cha` by name.
- [`chandeg.con`](../input-reference/con.md). Connectivity file for SWAT+ deg routing.
- [`channel.con`](../input-reference/con.md). Connectivity file for the original SWAT-style routing.
- [`file.cio`](../input-reference/file-cio.md). The `channel` line lists the file names that occupy each slot in `type input_cha`.

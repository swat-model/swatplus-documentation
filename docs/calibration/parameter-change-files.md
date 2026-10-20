---
title: Parameter change files
description: Layout of cal_parms.cal and calibration.cal, and every parameter name SWAT+ 62.0.1 accepts in a calibration change list.
status: review
verified_against:
  - src/cal_parm_read.f90
  - src/cal_parmchg_read.f90
  - src/cal_conditions.f90
  - src/cal_parm_select.f90
  - src/define_unit_elements.f90
  - src/calibration_data_module.f90
  - src/input_file_module.f90
  - src/main.f90.in
  - src/soil_nutcarb_init.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`cal_parms.cal` is the list of parameters that calibration may change: the name of each parameter, the type of object it belongs to, and the lowest and highest value it may take. `calibration.cal` is the change list for one run: each row picks a parameter from `cal_parms.cal`, says how to change it, and optionally limits the change to some objects or to objects that meet conditions. How SWAT+ applies the list is described on [Hard calibration](../calibration/hard-calibration.md).

Both files are named on the `chg` line of [`file.cio`](../input-reference/file-cio.md), in the first two positions (defaults `cal_parms.cal` and `calibration.cal`). A `null` name or a missing file switches the change list off.

All values are free format and separated by blanks. Names must not contain blanks.

## cal_parms.cal

- Line 1: title (skipped).
- Line 2: number of parameter rows.
- Line 3: column header (skipped).
- Then one row per parameter.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Parameter name, as listed under [Parameter names](#parameter-names). |
| 2 | `obj_typ` | Type of object the parameter belongs to: `hru`, `sol`, `plt`, `hlt`, `aqu`, `sdc`, `rte`, `swq`, `res`, `rdt`, `bsn`, `pst`, `gwf`, `gwf_riv`, `gwf_sgl` or `cli`. It decides which objects are changed when a row of `calibration.cal` lists none. |
| 3 | `abs_min` | Lowest value the parameter may take. Every change is limited to this value. |
| 4 | `abs_max` | Highest value the parameter may take. Every change is limited to this value. |
| 5 | `units` | Units, for information only. |

SWAT+ Editor writes this file with suitable limits for each parameter, and it rarely needs editing. A narrower range for a calibration run belongs in the calibration tool; the range here is the physical limit.

Example from `refdata/Osu_1hru` in the SWAT+ repository:

```
cal_parms.cal: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
186
name                       obj_typ       abs_min       abs_max             units
cn2                            hru      35.00000      95.00000              null
cn3_swf                        hru       0.00000       1.00000              null
usle_p                         hru       0.00000       1.00000              null
ovn                            hru       0.01000      30.00000              null
elev                           hru       0.00000    5000.00000                 m
slope                          hru       0.00010       0.90000               m/m
slope_len                      hru      10.00000     150.00000                 m
lat_ttime                      hru       0.50000     180.00000              days
```

The count on line 2 must match the number of rows. Rows past the count are not read.

## calibration.cal

- Line 1: title (skipped).
- Line 2: number of change rows.
- Line 3: column header (skipped).
- Then one row per change, each followed directly by its condition lines, if it has any.

### Change rows

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Parameter name. Must also be in `cal_parms.cal`. |
| 2 | `chg_typ` | `absval` (replace), `abschg` (add), `pctchg` (percent change) or `relchg` (relative change). See [Change types](../calibration/hard-calibration.md#change-types). |
| 3 | `val` | Size of the change. |
| 4 | `conds` | Number of condition lines that follow this row. 0 for none. |
| 5 | `lyr1` | First soil layer to change, for `sol` parameters (0 = top layer). For reservoir decision tables, a zone switch. |
| 6 | `lyr2` | Last soil layer to change, for `sol` parameters (0 = bottom layer). For reservoir decision tables, a zone switch. |
| 7 | `year1` | First year of the window, for `precip` and `temp`. For reservoir decision tables, a zone switch. |
| 8 | `year2` | Last year of the window, for `precip` and `temp`. For reservoir decision tables, a zone switch. |
| 9 | `day1` | First day of the year in the window, for `precip` and `temp`. For reservoir decision tables, a zone switch. |
| 10 | `day2` | Last day of the year in the window, for `precip` and `temp`. |
| 11 | `obj_tot` | Number of entries in the object list that follows on the same line. 0 means every object of the parameter's type. |
| 12... | object list | `obj_tot` object numbers. |

The object numbers are the sequence numbers of the objects (the first HRU is 1, and so on). A negative number closes a range started by the number before it, so `obj_tot` = 3 with the list `1 -20 35` means objects 1 to 20 and object 35.

### Condition lines

Each change row is followed by `conds` condition lines. A condition line has one of two forms:

- `range <var> <min> <max>`: the object's value of `<var>` must lie between `<min>` and `<max>`. Only `res_pvol` is recognised.
- `<var> <alt> <targ> <targc>`: a test against the text value `<targc>`. `<alt>` and `<targ>` must be present but are not used by the conditions that exist.

The variables and how they are tested are on [Conditions and regionalization](../calibration/conditions-regionalization.md).

### Example

`refdata/Osu_1hru/calibration.cal`:

```
  hru-new.cal developed from soft data calibration
    13
 NAME           CHG_TYP                  VAL   CONDS  LYR1  LYR2   YEAR1  YEAR2   DAY1   DAY2  OBJ_TOT
cn2         pctchg                  7.714000E+00  0           0           0           0           0           0           0           0           0
petco       pctchg                 -5.273950E+01  0           0           0           0           0           0           0           0           0
latq_co     pctchg                 -3.732030E+01  0           0           0           0           0           0           0           0           0
alpha       pctchg                  6.859000E+00  0           0           0           0           0           0           0           0           0
epco        pctchg                  6.534100E+01  0           0           0           0           0           0           0           0           0
awc         pctchg                 -6.256550E+01  0           0           0           0           0           0           0           0           0
esco        pctchg                  3.305500E+01  0           0           0           0           0           0           0           0           0
perco       pctchg                  1.434000E+00  0           0           0           0           0           0           0           0           0
cn3_swf     pctchg                 -7.710000E-02  0           0           0           0           0           0           0           0           0
canmx       pctchg                 -6.680230E+01  0           0           0           0           0           0           0           0           0
lat_len     pctchg                 -6.241200E+00  0           0           0           0           0           0           0           0           0
revap_co    pctchg                 -5.854530E+01  0           0           0           0           0           0           0           0           0
surlag      pctchg                 -2.125720E+01  0           0           0           0           0           0           0           0           0
```

Every row has no conditions and an empty object list, so each change applies to all objects of its type. The rows have one more zero than the header has columns; the reader stops after `obj_tot` when it is 0, so the extra value is ignored.

A row that changes `cn2` by +5 only on HRUs 1 to 20 and HRU 35, and only where the hydrologic soil group is `C`:

```
cn2         abschg      5.0    1   0   0   0   0   0   0   3   1  -20   35
hsg         =           0      C
```

## Parameter names

The names SWAT+ 62.0.1 recognises are listed below with the object type to give in `cal_parms.cal` and the input the parameter comes from. A name that is in neither list is skipped without a message. Some recognised names have no effect at 62.0.1, or change a different value; the notes with each name say which.

### HRU parameters (`hru`)

| Name | Input | Notes |
|------|-------|-------|
| `cn2` | condition II curve number from [`cntable.lum`](../input-reference/lum-tables.md) | The curve numbers for the other moisture conditions are recomputed. |
| `cn3_swf` | `cn3_swf`, [`hydrology.hyd`](../input-reference/hyd.md) | Not changed on tile-drained HRUs. |
| `perco` | `perco`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | Not changed on tile-drained HRUs. |
| `esco`, `epco` | `esco`, `epco`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | `epco` is also set for every plant in the HRU. |
| `petco` | `pet_co`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `latq_co`, `lat_sed` | `latq_co`, `lat_sed`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `lat_ttime` | `lat_ttime`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | Use `absval` with a value in days. `abschg`, `pctchg` and `relchg` act on an internal coefficient and give wrong travel times. |
| `canmx` | `can_max`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `biomix` | `bio_mix`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `erorgn`, `erorgp` | `orgn_enrich`, `orgp_enrich`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `lat_orgn`, `lat_orgp` | `lat_orgn`, `lat_orgp`, [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | |
| `slope`, `slope_len`, `lat_len`, `dis_stream` | `slp`, `slp_len`, `lat_len`, `dist_cha`, [`topography.hyd`](../input-reference/hyd.md) | |
| `elev` | HRU elevation | |
| `ovn` | Manning's n for overland flow, [`ovn_table.lum`](../input-reference/lum-tables.md) | |
| `usle_p` | USLE support practice factor, [`cons_practice.lum`](../input-reference/lum-tables.md) | |
| `field_len`, `field_wid`, `field_ang` | `len`, `wd`, `ang`, [`field.fld`](../input-reference/hyd.md#fieldfld) | |
| `snofall_tmp`, `snomelt_tmp`, `snomelt_max`, `snomelt_min`, `snomelt_lag` | `fall_tmp`, `melt_tmp`, `melt_max`, `melt_min`, `tmp_lag`, [`snow.sno`](../input-reference/sno.md) | |
| `tile_dep`, `tile_dtime`, `tile_lag`, `tile_rad`, `tile_dist`, `tile_drain`, `tile_pump` | `dp`, `t_fc`, `lag`, `rad`, `dist`, `drain`, `pump`, [`tiledrain.str`](../input-reference/str.md) | |
| `tile_latk` | `lat_ksat`, [`tiledrain.str`](../input-reference/str.md#tiledrainstr) | The result is written to the tile lag time (`lag`). |
| `cmn_h`, `nperco_h`, `pperco_h`, `phoskd_h`, `psp_h`, `nperco_lchtile_h` | HRU values of the basin nutrient parameters `cmn`, `nperco`, `pperco`, `phoskd`, `psp` and `nperco_lchtile` | Change one HRU's copy. The basin names below change the basin value. |

### Soil layer parameters (`sol`)

Changed in soil layers `lyr1` to `lyr2` of each HRU.

| Name | Input | Notes |
|------|-------|-------|
| `z` | layer depth `dp`, [`soils.sol`](../input-reference/sol.md) | |
| `bd`, `awc`, `k` | `bd`, `awc`, `soil_k`, [`soils.sol`](../input-reference/sol.md) | Dependent water contents are recomputed after `awc` changes. |
| `clay`, `silt`, `sand`, `rock` | `clay`, `silt`, `sand`, `rock`, [`soils.sol`](../input-reference/sol.md) | |
| `alb`, `usle_k`, `ec`, `cal`, `ph` | `alb`, `usle_k`, `ec`, `caco3`, `ph`, [`soils.sol`](../input-reference/sol.md) | |
| `anion_excl`, `crk` | `anion_excl`, `perc_crk`, [`soils.sol`](../input-reference/sol.md) | Whole profile values. |
| `cbn` | `carbon`, [`soils.sol`](../input-reference/sol.md) | No effect: the soil carbon pools are set up after the change list is applied. |
| `lab_p`, `hum_c_n`, `hum_c_p` | `lab_p`, `hum_c_n`, `hum_c_p`, [`nutrients.sol`](../input-reference/sol.md) | No effect, for the same reason. |

### Plant parameters (`plt`)

Changed for the plants named in the row's `plant` conditions, in the plant community of each listed HRU. See [Plant parameters](../calibration/hard-calibration.md#plant-parameters) for how to write these rows.

| Name | Input |
|------|-------|
| `lai_pot` | `lai_pot`, [`plants.plt`](../input-reference/plt.md) |
| `harv_idx` | `harv_idx`, [`plants.plt`](../input-reference/plt.md) |
| `phu_mat` | heat units to maturity of the plant in the HRU's community, computed at start-up from the plant and the climate |

`bio_e`, `hvsti`, `rdmx`, `t_opt`, `t_base` and `usle_c` are recognised names, but rows for them change nothing.

### Basin parameters (`bsn`)

Changed once for the whole basin.

| Name | Input |
|------|-------|
| `surlag`, `prf`, `evrch`, `percop`, `cdn`, `sdnco`, `tb_adj`, `n_updis`, `rsd_covco` | [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| `init_seq`, `init_microb`, `init_slow`, `init_passive`, `koc_c`, `solc_ratio`, `manure_c_frac`, `bio_consol`, `till_consol`, `sfc_rsd_photodeg`, `n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref`, `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` | [`carbon.bsn`](../input-reference/carbon-bsn.md) |
| `bmix_a`, `bmix_b`, `bmix_c`, `tillmix_a`, `tillmix_b`, `tillmix_c` | biological and tillage mixing curve coefficients, [`carbon.bsn`](../input-reference/carbon-bsn.md) |

Basin rows for `adj_pkr`, `ffcb`, `dorm_hr`, `cmn`, `nperco`, `pperco`, `phoskd`, `psp`, `nperco_lchtile`, `rsdco`, `msk_co1`, `msk_co2`, `msk_x`, `plaps`, `tlaps` and `evlai` change nothing. SWAT+ copies these basin values to the HRUs, channels, plants and weather stations while it sets them up, before the change list is applied, and does not read the basin value again. For the nutrient parameters, use the HRU names (`cmn_h`, `nperco_h`, `pperco_h`, `phoskd_h`, `psp_h`, `nperco_lchtile_h`) instead.

The per-layer carbon rates of [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) (`hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp`, `a1co2`, `asco2`, `apco2`, `abco2`) are recognised names, but rows for them change nothing.

### Aquifer parameters (`aqu`)

| Name | Input |
|------|-------|
| `flo_init_mm`, `dep_bot`, `dep_wt_init`, `no3_init`, `minp_init`, `cbn_init`, `flo_dist`, `bf_max`, `alpha`, `revap_co`, `deep_seep`, `sp_yld`, `hlife_n`, `flo_min`, `revap_min` | `gw_flo`, `dep_bot`, `dep_wt`, `no3_n`, `sol_p`, `carbon`, `flo_dist`, `bf_max`, `alpha_bf`, `revap`, `rchg_dp`, `spec_yld`, `hl_no3n`, `flo_min`, `revap_min`, [`aquifer.aqu`](../input-reference/aqu.md) |

### Channel parameters (`sdc` or `rte`)

| Name | Input |
|------|-------|
| `chw`, `chd`, `chs`, `chl`, `chn`, `chk`, `cov`, `d50`, `ch_clay`, `carbon`, `ch_bd`, `chss`, `bank_exp`, `vcr_coef`, `bankfull_flo`, `fps`, `fpn`, `hc_kh`, `hc_hgt`, `hc_ini`, `ch_n_conc`, `ch_p_conc`, `ch_p_bio`, `pk_rto`, `fp_inun_days`, `n_setl`, `p_setl`, `n_sol_part`, `p_sol_part`, `n_dep_enr`, `p_dep_enr`, `arc_len_fr`, `bed_exp`, `wash_bed_fr` | channel geometry, hydraulics, sediment and nutrient parameters of the [SWAT-DEG channel inputs](../input-reference/sd-channel.md) |

### Channel nutrient parameters (`swq`)

| Name | Input |
|------|-------|
| `mumax`, `rs1` to `rs7`, `rk1` to `rk6`, `bc1` to `bc4` | in-stream nutrient and algae rates, [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha) (see [channel inputs](../input-reference/sd-channel.md)) |

A `rk5` row changes `rs2` (the `ben_disp` column of [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha)) instead.

### Reservoir parameters (`res`)

| Name | Input |
|------|-------|
| `esa`, `evol`, `psa`, `pvol` | emergency and principal spillway surface areas and volumes, [`hydrology.res`](../input-reference/res.md) |
| `k_res`, `evrsv` | bottom hydraulic conductivity and evaporation coefficient, [`hydrology.res`](../input-reference/res.md#hydrologyres) |
| `nsed`, `res_d50`, `sed_stlr`, `velsetlr` | normal sediment concentration, median particle size, settling rate and settling velocity, [`sediment.res`](../input-reference/res.md#sedimentres) |
| `psetlr1`, `psetlr2`, `nsetlr1`, `nsetlr2`, `nsolr`, `psolr`, `soln_stl_fr`, `solp_stl_fr` | nutrient settling rates, [`nutrients.res`](../input-reference/res.md#nutrientsres) |
| `vol`, `sed`, `orgn`, `orgp`, `no3`, `nh3`, `no2`, `solp` | water, sediment and nutrient content at the start of the run, [`initial.res`](../input-reference/res.md#initialres) |

### Reservoir decision table parameters (`rdt`)

| Name | Input |
|------|-------|
| `drawdown_days`, `withdraw_rate` | release rules of the reservoir decision tables in [`res_rel.dtl`](../input-reference/dtl.md), per storage zone (see [Reservoir decision tables](../calibration/hard-calibration.md#reservoir-decision-tables)) |

### Pesticide parameters (`pst`)

List the pesticides to change (their order in [`pesticide.pes`](../input-reference/pes.md#pesticidepes)) in the object list. With an empty list nothing is changed.

| Name | Input |
|------|-------|
| `pst_koc`, `pst_washoff`, `pst_foliar_hlife`, `pst_soil_hlife`, `pst_solub`, `pst_aq_hlife`, `pst_aq_volat`, `pst_aq_settle`, `pst_aq_resus`, `pst_ben_hlife`, `pst_ben_bury`, `pst_ben_act_dep` | `soil_ads`, `frac_wash`, `hl_foliage`, `hl_soil`, `solub`, `aq_hlife`, `aq_volat`, `aq_settle`, `aq_resus`, `ben_hlife`, `ben_bury`, `ben_act_dep`, [`pesticide.pes`](../input-reference/pes.md) |

### Simplified HRU parameters (`hlt`)

| Name | Input |
|------|-------|
| `cn2_lte`, `awc_lte`, `etco_lte`, `tc_lte`, `soildep_lte`, `slope_lte`, `slopelen_lte`, `sy_lte`, `abf_lte`, `revapc_lte`, `percc_lte`, `sw_lte`, `gw_lte`, `gwflow_lte`, `gwdeep_lte`, `snow_lte`, `uslek_lte`, `uslec_lte`, `uslep_lte`, `uslels_lte` | [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru) |

`awc_lte` is given per mm of soil depth; SWAT+ multiplies the change and the upper limit by the soil depth.

### gwflow parameters

These only act when gwflow is switched on in [`codes.bsn`](../input-reference/codes-bsn.md). Each name needs the object type shown.

| Name | Object type | Objects changed | Input |
|------|-------------|-----------------|-------|
| `aquifer_K`, `aquifer_Sy`, `aquifer_exdp` | `gwf` | gwflow cells | aquifer hydraulic conductivity, specific yield and extinction depth, [gwflow inputs](../input-reference/gwflow.md) |
| `tile_K`, `floodplain_K` | `gwf` | gwflow cells | tile drain and floodplain conductivity, only when tile or floodplain exchange is on |
| `aquifer_delay` | `hru` | HRUs | recharge delay from the soil to the water table, in days |
| `stream_K`, `stream_thk` | `gwf_riv` | channels | streambed conductivity and thickness of the cells connected to each channel |
| `stream_bed` | `gwf_sgl` | applied once | streambed elevation offset, one value for all channels |
| `reservoir_K`, `pond_bed_K` | `gwf_sgl` | applied once | reservoir and pond bed conductivity |

### Climate parameters (`cli`)

| Name | Input |
|------|-------|
| `precip` | daily precipitation of the listed [`*.pcp`](../input-reference/pcp.md) records, from `day1` to `day2` of each year from `year1` to `year2` |
| `temp` | daily temperature of the listed [`*.tmp`](../input-reference/tmp.md) records; changes nothing |

See [Climate changes](../calibration/hard-calibration.md#climate-changes) before using these.

## Related pages

- [Hard calibration](../calibration/hard-calibration.md). When and how the change list is applied.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Condition line variables.
- [Soft calibration](../calibration/soft-calibration.md). The seven `.sft` files that follow these two on the `chg` line.

??? quote "Sources"

    - Readers: [`src/cal_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_read.f90) and [`src/cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parmchg_read.f90). Object list expansion: [`src/define_unit_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/define_unit_elements.f90).
    - Parameter names and the variables they change: [`src/cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90). Object type dispatch: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90).
    - Types: `type calibration_parameters`, `type calibration_conditions` and `type update_parameters` in [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90). File name slots: `in_chg%cal_parms` and `in_chg%cal_upd` in [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90).

    | Column | Fortran variable |
    |--------|------------------|
    | `cal_parms.cal` `name`, `obj_typ`, `abs_min`, `abs_max`, `units` | `cal_parms(i)%name`, `%ob_typ`, `%absmin`, `%absmax`, `%units` |
    | `calibration.cal` `name` to `day2` | `cal_upd(i)%name`, `%chg_typ`, `%val`, `%conds`, `%lyr1`, `%lyr2`, `%year1`, `%year2`, `%day1`, `%day2` |
    | `calibration.cal` `obj_tot` and list | `cal_upd(i)%num_tot`, expanded into `cal_upd(i)%num(:)` |
    | condition `var alt targ targc` | `cal_upd(i)%cond(j)%var`, `%alt`, `%targ`, `%targc` |
    | condition `range var min max` | `cal_upd(i)%cond(j)%var`, `cal_upd(i)%val1`, `cal_upd(i)%val2` (shared by all range lines of the row) |

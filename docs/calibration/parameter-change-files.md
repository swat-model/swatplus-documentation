---
title: Parameter change files
description: Column layout of cal_parms.cal and calibration.cal, verified against the readers. Includes the 40 wired carbon parameters.
status: updated
verified_against:
  - src/cal_parm_read.f90
  - src/cal_parmchg_read.f90
  - src/cal_parm_select.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

## Purpose

`cal_parms.cal` is the dictionary of every parameter that calibration can touch: its name, the object type it lives on, and the absolute range it may be moved through. `calibration.cal` is the change list applied during a hard-calibration run: each row picks a parameter from the dictionary, sets a change type and magnitude, optionally restricts the change to a list of objects, and optionally attaches conditions. Both files feed the same parameter selector (`cal_parm_select`) used by hard calibration and by parameter changes inside soft calibration.

## Source

- `cal_parms.cal` reader: [`src/cal_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parm_read.f90)
- `calibration.cal` reader: [`src/cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parmchg_read.f90)
- Type definitions: [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/calibration_data_module.f90), `type calibration_parameters` (rows of `cal_parms.cal`) and `type update_parameters` (rows of `calibration.cal`).
- File slot names: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_chg`. Defaults: `cal_parms = "cal_parms.cal"`, `cal_upd = "calibration.cal"`.

## cal_parms.cal

`cal_parm_read.f90` reads:

- Line 1: title (skipped).
- Line 2: integer `mchg_par`, the number of parameter records that follow.
- Line 3: header (skipped).
- Lines 4 .. 3 + `mchg_par`: one record per parameter, read list-directed into `cal_parms(i)`.

Record layout (`type calibration_parameters`):

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | `name` | char(25) | Parameter name. Must match a case in `cal_parm_select.f90`. Examples: `cn2`, `awc`, `alpha`, `epco`, `lat_ttime`. |
| 2 | `ob_typ` | char(25) | Object type the parameter is attached to: `hru`, `hlt`, `sol`, `lyr`, `plt`, `aqu`, `cha`, `sdc`, `rte`, `swq`, `res`, `rdt`, `ru`, `bsn`, `pcp`, `tmp`, `gwf`. Determines which collection is iterated. |
| 3 | `absmin` | real | Lower bound. Any change is clamped to this value. |
| 4 | `absmax` | real | Upper bound. Any change is clamped to this value. |
| 5 | `units` | char(25) | Units string for the parameter (`mm`, `m`, `days`, `null`, ...). Documentation only; the reader does not interpret it. |

### Example

`refdata/Osu_1hru/cal_parms.cal`:

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

The count line on line 2 (`186`) drives the allocation of `cal_parms(0:mchg_par)`. The header on line 3 (`name`, `obj_typ`, `abs_min`, `abs_max`, `units`) is skipped; values are read by position.

## calibration.cal

`cal_parmchg_read.f90` reads:

- Line 1: title (skipped).
- Line 2: integer `mcal`, the number of change records.
- Line 3: header (skipped).
- Then `mcal` change records, each followed by `conds` condition lines (often zero).

### Change record

Each change record is one logical line, read list-directed in two passes. The first pass reads the fixed prefix; if the prefix indicates an object list is present, the line is backspaced and re-read to pick up the integers.

Fixed prefix:

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | `name` | char(25) | Parameter name. Must match a `name` in `cal_parms.cal`. The reader crosswalks this to `num_db`. |
| 2 | `chg_typ` | char(16) | Change operator. One of `absval` (replace), `abschg` (add), `pctchg` (percent change). |
| 3 | `val` | real | Magnitude of the change, interpreted per `chg_typ`. |
| 4 | `conds` | int | Number of condition lines that follow this record. May be zero. |
| 5 | `lyr1` | int | First soil layer in range (0 means all layers). For reservoir decision tables, reused as a storage-zone flag. |
| 6 | `lyr2` | int | Last soil layer in range (0 means through last layer). |
| 7 | `year1` | int | First year (for climate parameter changes). |
| 8 | `year2` | int | Last year (for climate parameter changes). |
| 9 | `day1` | int | First day of year (for climate parameter changes). |
| 10 | `day2` | int | Last day of year (for climate parameter changes). |
| 11 | `nspu` | int | Number of object indices listed after this prefix. `0` means apply to every object of this parameter's `ob_typ`. |

If `nspu > 0`, the same line continues with `nspu` integers giving the object indices to update. When `nspu == 0` the reader allocates a `num` array that lists every object of the matching type (every HRU, every channel, every plant, and so on) so the change applies globally.

### Condition lines

A condition line takes one of two forms, distinguished by the literal token in column 1:

- `range <var> <val1> <val2>`. Restricts the change to objects whose `<var>` falls between `val1` and `val2`. Used in `cal_conditions.f90` for `res_pvol`.
- `<var> <alt> <targ> <targc>`. Read as a `calibration_conditions` record. Used for categorical filters: `hsg`, `texture`, `plant`, `pl_class`, `landuse`, `cal_group`, `res_typ`.

See [Conditions and regionalization](../calibration/conditions-regionalization.md) for the supported variable list.

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

In this file every record has `conds = 0` and `nspu = 0`, so each change applies to every HRU. The trailing integer count is `11` per row: `conds`, `lyr1`, `lyr2`, `year1`, `year2`, `day1`, `day2`, and `nspu` (eight integers), padded by the editor with extra zeros that the list-directed reader ignores.

## Carbon parameters

SWAT+ wires 40 carbon-related parameters in `cal_parm_select.f90`. Each entry below maps a calibration name to its target field, suggests a working min/max range, and notes the object type (`bsn`, `lyr`, `plt`, `hru`) that must appear in the `ob_typ` column of `cal_parms.cal`. Bounds come from the sptAPI bundled `cal_parms.cal` (261 entries), with the temperature triple tightened to physical bounds to physically realistic ranges.

### Basin scalars from `carbon.bsn` (18 entries)

| name | ob_typ | units | abs_min | abs_max | description |
|---|---|---|---|---|---|
| `init_seq` | bsn | fraction | 0.5 | 1.0 | initial sequestration fraction (`org_frac%frac_seq`) |
| `init_microb` | bsn | fraction | 0.0 | 0.1 | initial microbial-humus fraction (`org_frac%frac_hum_microb`) |
| `init_slow` | bsn | fraction | 0.2 | 0.6 | initial slow-humus fraction (`org_frac%frac_hum_slow`) |
| `init_passive` | bsn | fraction | 0.2 | 0.6 | initial passive-humus fraction (`org_frac%frac_hum_passive`) |
| `koc_c` | bsn | none | 500 | 1500 | KOC for C transport (`cb_wtr_coef%prmt_21`) |
| `solc_ratio` | bsn | 0..1 | 0.1 | 1.0 | runoff:percolate soluble C ratio (`cb_wtr_coef%prmt_44`) |
| `manure_c_frac` | bsn | none | 0.0 | 1.0 | manure C partition between fresh and stable pools (`man_coef%rtof`) |
| `bio_consol` | bsn | none | 0.05 | 0.5 | biological consolidation factor (`bio_consf`) |
| `till_consol` | bsn | none | 0.05 | 0.5 | tillage consolidation factor (`till_consf`) |
| `sfc_rsd_photodeg` | bsn | 1/day | 0.0 | 0.05 | surface residue photodegradation rate (`photo_degrade_factor`) |
| `n_act_frac` | bsn | fraction | 0.005 | 0.04 | fraction of organic N in active humus pool (`n_act_frac`) |
| `cnr_cap` | bsn | none | 100 | 1000 | upper cap on residue C:N ratio |
| `cnr_ref` | bsn | none | 10 | 50 | reference C:N ratio where decomp factor = 1 |
| `cpr_cap` | bsn | none | 1000 | 10000 | upper cap on residue C:P ratio |
| `cpr_ref` | bsn | none | 100 | 400 | reference C:P ratio where decomp factor = 1 |
| `t_cbn_min` | bsn | deg C | -5 | 5 | minimum temperature bound for `tmpf2` (`org_con%tn`); tightened to physical bounds |
| `t_cbn_opt` | bsn | deg C | 25 | 40 | optimum temperature for `tmpf2` (`org_con%top`); tightened to physical bounds |
| `t_cbn_max` | bsn | deg C | 45 | 55 | maximum temperature bound for `tmpf2` (`org_con%tx`); tightened to physical bounds |

!!! note
    The `min < opt < max` ordering invariant is not enforced by `cal_parms.cal` itself; calibration tools may still produce invalid combinations. The `fcgd` clamp ensures invalid orderings degrade gracefully (return 0) rather than crashing.

### Per-layer fields from `carbon_lyr.bsn` (11 entries)

Each entry addresses `carbdb(ly)` or `org_allo(ly)` using the `lyr1`/`lyr2` slot of the `calibration.cal` record. Bounds are guarded to `[1, size(carbdb)]` inside the `case` branch, so out-of-range layer indices are silently no-op.

| name | ob_typ | units | abs_min | abs_max | description |
|---|---|---|---|---|---|
| `hp_rate` | lyr | 1/day | 1.0e-06 | 1.0e-04 | passive humus turnover rate (`carbdb(ly)%hp_rate`) |
| `hs_rate` | lyr | 1/day | 1.0e-05 | 1.0e-03 | slow humus turnover rate (`carbdb(ly)%hs_rate`) |
| `microb_rate` | lyr | 1/day | 0.005 | 0.05 | microbial biomass turnover rate (`carbdb(ly)%microb_rate`) |
| `meta_rate` | lyr | 1/day | 0.01 | 0.1 | metabolic litter turnover rate (`carbdb(ly)%meta_rate`) |
| `str_rate` | lyr | 1/day | 0.005 | 0.05 | structural litter turnover rate (`carbdb(ly)%str_rate`) |
| `microb_top_rate` | lyr | 1/day | 0.005 | 0.05 | top-layer microbial activity adjustment (`carbdb(ly)%microb_top_rate`) |
| `hs_hp` | lyr | none | 0.01 | 0.2 | slow-to-passive humus allocation (`carbdb(ly)%hs_hp`) |
| `a1co2` | lyr | fraction | 0.3 | 0.8 | metabolic litter to CO2 (`org_allo(ly)%a1co2`) |
| `asco2` | lyr | fraction | 0.3 | 0.8 | slow humus to CO2 (`org_allo(ly)%asco2`) |
| `apco2` | lyr | fraction | 0.3 | 0.8 | passive humus to CO2 (`org_allo(ly)%apco2`) |
| `abco2` | lyr | fraction | 0.0 | 0.8 | microbial biomass to CO2 (`org_allo(ly)%abco2`) |

### Biomixing and tillage curve coefficients (6 entries)

Curve fit coefficients used by `mgt_tillfactor.f90` tillf option 4. The `zz_` prefix that the older code carried was dropped to match the column names in [`carbon.bsn`](../input-reference/carbon-bsn.md).

| name | ob_typ | units | abs_min | abs_max | description |
|---|---|---|---|---|---|
| `bmix_a` | bsn | none | 1.0 | 5.0 | biological mixing coefficient A |
| `bmix_b` | bsn | none | 1.0 | 10.0 | biological mixing coefficient B |
| `bmix_c` | bsn | none | -10.0 | -1.0 | biological mixing coefficient C |
| `tillmix_a` | bsn | none | 1.0 | 5.0 | tillage mixing coefficient A |
| `tillmix_b` | bsn | none | 5.0 | 25.0 | tillage mixing coefficient B |
| `tillmix_c` | bsn | none | -10.0 | -1.0 | tillage mixing coefficient C |

### Plant carbon parameters (5 entries)

Carbon-relevant parameters on the plant database (`pldb(ielem)`). These were not previously exposed even though plant biomass drives the whole NPP and residue chain.

| name | ob_typ | units | abs_min | abs_max | description |
|---|---|---|---|---|---|
| `bio_e` | plt | (kg/ha)/(MJ/m^2) | 10.0 | 60.0 | biomass-energy ratio (drives NPP) |
| `hvsti` | plt | fraction | 0.1 | 0.8 | harvest index (controls residue vs grain C split) |
| `rdmx` | plt | m | 0.5 | 3.0 | maximum root depth |
| `t_opt` | plt | deg C | 15 | 35 | optimum plant growth temperature |
| `t_base` | plt | deg C | 0 | 15 | base plant growth temperature |

The existing `usle_c` plant parameter is retained from earlier releases.

!!! warning
    For the `init_*` parameters to take effect, `proc_cal` must run **before** `soil_nutcarb_init`. The current `main.f90` already orders these correctly; do not reorder. Previously the order was reversed and `init_*` calibration was a silent no-op because the pools were already sized using pre-cal values.

## Related files

- [`carbon.bsn`](../input-reference/carbon-bsn.md). Basin-wide carbon scalar inputs whose fields these parameters target.
- [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md). Per-layer carbon inputs.
- [Hard calibration](../calibration/hard-calibration.md). How these files are consumed during a calibration run.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Condition-line vocabulary.

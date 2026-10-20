---
title: Decision tables
description: How SWAT+ evaluates decision tables for conditional management, reservoir and wetland releases, land use change scenarios and flow control.
status: review
verified_against:
  - src/conditional_module.f90
  - src/conditions.f90
  - src/cond_real.f90
  - src/actions.f90
  - src/dtbl_lum_read.f90
  - src/dtbl_res_read.f90
  - src/hru_control.f90
  - src/time_control.f90
  - src/res_control.f90
  - src/res_hydro.f90
  - src/wetland_control.f90
  - src/cal_cond_read.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

A decision table is a set of rules of the form "if these conditions are met, do these actions". SWAT+ uses them wherever an operation depends on the state of the model instead of a fixed date: irrigation when plants are water stressed, planting when the soil is warm enough, fertilising only a share of the fields in a land use, releasing reservoir water by storage and season, or changing land use partway through a run.

There are four decision table files. They have the same format and are evaluated the same way.

| File | Used for | Evaluated |
|---|---|---|
| [`lum.dtl`](../input-reference/dtl.md) | Conditional management of HRUs | daily, for each HRU whose management schedule lists the table as an automatic operation |
| [`res_rel.dtl`](../input-reference/dtl.md) | Reservoir and wetland releases | daily, for each reservoir or wetland that names the table as its release rule |
| [`scen_lu.dtl`](../input-reference/dtl.md) | Land use and management change scenarios | daily, for every HRU, for each table listed in `scen_dtl.upd` |
| [`flo_con.dtl`](../input-reference/dtl.md) | Flow control (water allocation, saturated buffers) | when the controlled object is processed |

## Structure

Each table has conditions, alternatives and actions.

- Conditions (rows) name a state variable, the object it is taken from, and a limit.
- Alternatives (columns) are rules. For each condition, an alternative gives a comparison operator (`<`, `>`, `<=`, `>=`, `=`, `/=`) or `-` when that condition does not matter for the rule.
- Actions (rows) say what to do. For each alternative, an action has an outcome `y` (do it if this rule is true) or `n`.

An example from `refdata/Ames_sub1/lum.dtl` irrigates with a sprinkler when the plant is water stressed, has accumulated more than 20 % of its heat units and has a leaf area index above 0.5, as long as less than 500 mm has been applied in the year:

```
name                     conds      alts      acts
irr_year_irr                4         1         1
var                        obj   obj_num           lim_var            lim_op  lim_const      alt1
irr_year                   hru         0              null                 -   500.00000         <
w_stress                   hru         0              null                 -   0.80000           <
phu_plant                  hru         0           phu_mat                 -     0.20000         >
leaf_area                  hru         0           null                    -     0.50000         >
act_typ                    obj   obj_num              name            option    const        const2                fp  outcome
irrigate                   hru        0           sprinkler     sprinkler_ilm    25.00000   20.00000  unlim  y
```

An object number of 0 means the object the table is being evaluated for (the current HRU, reservoir or wetland).

## Evaluation

Each time a table is evaluated:

1. Every alternative starts as true.
2. For each condition, the current value of the variable is compared with the limit. An alternative whose operator for that condition is not satisfied becomes false. A `-` leaves the alternative unchanged.
3. Each action is taken if at least one alternative that is still true has `y` for that action.

Any number of alternatives can be true at once, and an action shared by several alternatives is taken once.

### Limits

The limit a variable is compared with is built from three columns: `lim_var`, `lim_op` and `lim_const`. For variables measured against a property of the object, `lim_var` names the property and `lim_op` combines it with the constant. For example, for `soil_water` the property can be `wp` (taken as 0), `fc` (profile water at field capacity) or `ul` (profile water at saturation), and `fc * 0.8` is written as `lim_var = fc`, `lim_op = *`, `lim_const = 0.8`. For reservoir volume, the property can be `pvol` or `evol`. For variables compared with a plain number, `lim_var` is `null` and only `lim_const` is used.

### Condition variables

| Group | Variables |
|---|---|
| Plant stress and growth | `w_stress`, `n_stress`, `p_stress`, `phu_plant`, `phu_base0`, `plant_gro`, `plant_name_gro`, `biomass`, `leaf_area`, `ground_cov`, `cur_yrs_mat`, `plant_com` |
| Time | `jday`, `month`, `year_rot`, `year_gro`, `year_cal`, `year_seq`, `year_start`, `days_plant`, `days_harv`, `days_irr`, `days_act`, `day_start` |
| Weather | `precip_cur`, `precip_next`, `p_pet` |
| Soil and land | `soil_water`, `soil_temp2`, `soil_carbon`, `p_lab_150`, `slope`, `hyd_soil_group`, `p_factor`, `k_factor`, `tile_drained`, `tillage`, `land_use`, `cal_group` |
| Water | `irr_year`, `irr_demand`, `irr_pou_dmd`, `tile_flo`, `channel_flo`, `aqu_dep`, `ch_order` |
| Water bodies | `vol`, `res_inflo`, `wet_depth`, `vol_wet`, `wtow_vol` |
| Probability | `prob`, `prob_unif`, `prob_unif1`, `prob_unif_lu` |

### Probabilistic conditions

Probability conditions make actions happen on a random day or on a random share of HRUs:

- `prob` compares a uniform random number with `lim_const`, so the action happens on that fraction of evaluations.
- `prob_unif` picks one random day in the window from day `obj_num` to day `lim_const` of the year, so the action happens once in the window.
- `prob_unif1` spreads the probability evenly over a window of `lim_const` days that starts on 1 January of the calendar year given in `obj_num`.
- `prob_unif_lu` spreads an operation over the HRUs of a land use (named in a `land_use` condition) during the window from day `obj_num` to day `lim_const`, so that the share of HRUs treated grows evenly through the window. This is how an operation such as "fertilise 30 % of corn fields in May" is set up.

### Actions

| Group | Action types |
|---|---|
| Crops and soil | `plant`, `harvest`, `kill`, `harvest_kill`, `till`, `fertilize`, `manure`, `fert_future`, `pest_apply`, `graze`, `burn`, `grow_init`, `grow_end`, `puddle`, `herd` |
| Irrigation and demand | `irrigate`, `irr_demand`, `manure_demand`, `wallo_dmd`, `set_dmd`, `irr_dmd`, `res_irr_dmd`, `fill_res`, `fill_wtow`, `fill_can`, `duty_reset`, `duty_fr` |
| Counters | `rot_reset`, `harv_reset`, `kill_reset`, `plant_reset`, `irr_reset`, `pheno_reset` |
| Land use and practices | `lu_change`, `hru_fr_update`, `cn_update`, `p_factor`, `contour`, `stripcrop`, `terrace`, `tile_install`, `septic_install`, `fstrip_install`, `grassww_install`, `grassww_uninstall`, `user_def_bmp`, `snow_change`, `chan_change` |
| Water control | `tileflo_control`, `tiledep_control`, `impound_on`, `impound_off`, `weir_height` |
| Releases | `release` with the options described in [Reservoirs and wetlands](reservoirs-wetlands.md) |

For management actions, `name` points to a record in the matching database (a plant, fertiliser, tillage implement, harvest operation, irrigation operation and so on), and `option`, `const` and `const2` give the amount or method. The `fp` column names an extra file record or object, depending on the action.

## Related pages

- [`*.dtl` input files](../input-reference/dtl.md)
- [Management](../input-reference/management.md) for management schedules and automatic operations
- [Reservoirs and wetlands](reservoirs-wetlands.md) for release options
- [Plant growth and land use management](plant-growth-lum.md)
- [Water allocation](../input-reference/water-allocation.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Types `conditions_var`, `actions_var`, `decision_table` and the arrays `dtbl_lum`, `dtbl_res`, `dtbl_scen`, `dtbl_flo`: [`src/conditional_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditional_module.f90)
    - Readers: [`src/dtbl_lum_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_lum_read.f90), [`src/dtbl_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_res_read.f90), [`src/dtbl_scen_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_scen_read.f90), [`src/dtbl_flocon_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_flocon_read.f90); scenario activation: [`src/cal_cond_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_cond_read.f90) (`scen_dtl.upd`)
    - Condition evaluation: [`src/conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`src/cond_real.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cond_real.f90), [`src/cond_integer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cond_integer.f90)
    - Actions: [`src/actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90); release actions: [`src/res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90)
    - Call sites: automatic operations in [`src/hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), scenarios in [`src/time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90), reservoirs in [`src/res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), wetlands in [`src/wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90)

    Columns and variables:

    | Column | Variable |
    |---|---|
    | `var`, `obj`, `obj_num`, `lim_var`, `lim_op`, `lim_const` | `d_tbl%cond%var`, `%ob`, `%ob_num`, `%lim_var`, `%lim_op`, `%lim_const` |
    | `alt1` ... | `d_tbl%alt(cond, alt)` |
    | `act_typ`, `obj`, `obj_num`, `name`, `option`, `const`, `const2`, `fp` | `d_tbl%act%typ`, `%ob`, `%ob_num`, `%name`, `%option`, `%const`, `%const2`, `%file_pointer` |
    | outcomes | `d_tbl%act_outcomes(act, alt)` |
    | alternative still true | `d_tbl%act_hit(alt)` |

---
title: "*.dtl (decision tables)"
description: Decision table files. Rules that check conditions each day and trigger management operations, reservoir releases, land use changes and water allocation settings.
status: review
verified_against:
  - src/dtbl_lum_read.f90
  - src/dtbl_res_read.f90
  - src/dtbl_scen_read.f90
  - src/dtbl_flocon_read.f90
  - src/cal_cond_read.f90
  - src/conditional_module.f90
  - src/conditions.f90
  - src/cond_real.f90
  - src/cond_integer.f90
  - src/actions.f90
  - src/res_hydro.f90
  - src/proc_cond.f90
  - src/hru_control.f90
  - src/hru_dtbl_actions_init.f90
  - src/time_control.f90
  - src/res_control.f90
  - src/wallo_start_day.f90
  - src/mallo_control.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A decision table is a set of rules. Each day SWAT+ checks the table's conditions for an object (an HRU, a reservoir, a water allocation object), finds which of the table's alternatives are satisfied, and performs the actions that those alternatives switch on. Decision tables drive automatic management (planting, harvest, fertilizer, irrigation), reservoir and paddy releases, land use change scenarios, and water allocation demands. See [decision tables](../model-theory/decision-tables.md) for the concept.

There are four decision table files. Their names are given on the `decision_table` line of [`file.cio`](file-cio.md), in this order:

| File | Default name | Used by |
|------|--------------|---------|
| land use and management | `lum.dtl` | HRUs, through the automatic operations listed in [`management.sch`](management.md); HRU-lte growing seasons; manure demands in [`manure_allo.mnu`](manure-allocation.md); irrigation demands, outside-source concentrations and treatment in [water allocation](water-allocation.md) |
| reservoir release | `res_rel.dtl` | reservoirs and HRU wetlands or paddies that name a release table (see [`*.res`](res.md) and [`*.wet`](wet.md)) |
| land use scenarios | `scen_lu.dtl` | tables listed in `scen_dtl.upd`, checked for every HRU every day |
| flow control | `flo_con.dtl` | saturated buffers, and water allocation demand and source or receiver fractions |

A file that is missing, or named `null` in [`file.cio`](../input-reference/file-cio.md), gives an empty set of tables.

## Format

All four files have the same layout. Free format, whitespace-separated.

- Line 1: title (skipped).
- Line 2: the number of decision tables in the file.
- Line 3: skipped (normally blank).
- Then each table in turn:
    - a header line (skipped);
    - the table line: `name`, `conds`, `alts`, `acts` (table name, number of conditions, number of alternatives, number of actions);
    - a header line (skipped);
    - `conds` condition rows;
    - a header line (skipped);
    - `acts` action rows;
    - in `res_rel.dtl`, `scen_lu.dtl` and `flo_con.dtl` only: one more line, which is skipped. Leave a blank line here. Without it the next table's header is skipped in its place and the following lines are read out of step.

The counts on the table line must match the rows that follow. Extra or missing rows shift every later table. Names are matched exactly, and a name that is not found is not reported.

### Condition rows

| # | Column | Description |
|---|--------|-------------|
| 1 | `var` | Condition variable (see [Condition variables](#condition-variables)). |
| 2 | `obj` | Object type the variable belongs to, for example `hru`, `res`, `null`. For `prob_unif`, this column contains the application probability instead (see below). |
| 3 | `obj_num` | Object number. 0 means the object the table is being checked for. |
| 4 | `lim_var` | Limit variable. A name (land use, plant, soil group) or a reference volume, depending on the condition. `null` when not used. |
| 5 | `lim_op` | Limit operator: `*`, `+`, `-` or `/`. Combines `lim_var` with `lim_const` for `soil_water`, `vol` and `vol_wet`. `-` when not used. |
| 6 | `lim_const` | Limit constant. |
| 7 and on | `alt1`, `alt2`, ... | One alternative operator per alternative. |

For most conditions the current value of the variable is compared with `lim_const`. For `soil_water`, `vol` and `vol_wet` it is compared with a target built from `lim_var`, `lim_op` and `lim_const`, for example "emergency volume × 0.8".

### Alternatives

Each alternative is a column of operators, one per condition. An alternative is satisfied when every one of its conditions is true. For numeric conditions the operators are:

| Operator | Condition is true when |
|----------|----------------------|
| `<` | value < limit |
| `>` | value > limit |
| `<=` | value ≤ limit |
| `>=` | value ≥ limit |
| `=` | value = limit |
| `/=` | value ≠ limit |
| `-` | always (the condition does not apply to this alternative) |

Any other text in a numeric condition's alternative column is treated like `-`. In particular `/` does not mean "not equal" for numeric conditions.

The yes/no conditions (`plant_gro`, `plant_name_gro`, `hyd_soil_group`, `land_use`, `cal_group`, `tillage`, `prob_unif`, `prob_unif1`, `prob_unif_lu`, `ch_order`) use only `=`, meaning the condition must be true. `tile_drained` and `plant_com` also accept `/`, meaning the condition must be false. Every other operator is treated like `-`.

### Action rows

| # | Column | Description |
|---|--------|-------------|
| 1 | `act_typ` | Action type (see [Land use and management actions](#land-use-and-management-actions) and [Reservoir release actions](#reservoir-release-actions)). |
| 2 | `obj` | Object type. For `irrigate`, the type of the water source. |
| 3 | `obj_num` | Object number. 0 means the object the table is being checked for. |
| 4 | `name` | Action name. Used to link `days_act` conditions to this action, and by `irrigate`, `irr_demand` and `puddle` as described below. Otherwise free text. |
| 5 | `option` | Action option, specific to the action type. |
| 6 | `const` | First action constant. |
| 7 | `const2` | Second action constant. In `lum.dtl`, values below 1 are raised to 1. |
| 8 | `fp` | File pointer: a name in another input file, specific to the action type. |
| 9 and on | `outcome1`, `outcome2`, ... | `y` or `n` for each alternative. |

An action runs when at least one alternative is satisfied and the action's outcome for that alternative is `y`. Actions run in the order of the rows.

In `lum.dtl`, many actions use `const2` as the maximum number of times the action may run in a calendar year for each HRU. The count is reset on 31 December. These actions are marked "per year: `const2`" in the table below.

## Condition variables

Units are those of the compared value. "Plants" means the plants of the HRU's plant community.

| `var` | Value compared | Notes |
|-------|----------------|-------|
| `w_stress` | Average water stress factor of the growing plants (1 = no stress) | 1 when no plant is growing. |
| `n_stress` | Average nitrogen stress factor of the growing plants | 0 when no plant is growing. |
| `p_stress` | Average phosphorus stress factor of the growing plants | 0 when no plant is growing. |
| `phu_plant` | Fraction of potential heat units accumulated by the first plant that has started accumulating (plant 1 if none) | |
| `phu_base0` | Fraction of the annual base-zero heat units accumulated at the HRU's weather station | `obj` must be `hru` or `hlt`. |
| `precip_cur` | Precipitation today, mm | `obj` must be `hru` or `hlt`. |
| `precip_next` | Precipitation tomorrow, mm | `obj` must be `hru` or `hlt`. |
| `plant_gro` | Plant number `lim_const` (1 if 0) is growing | Yes/no. |
| `plant_name_gro` | The plant named in `lim_var` is in the community and growing | Yes/no. |
| `days_plant` | Days since the last planting | |
| `days_harv` | Days since the last harvest | |
| `days_irr` | Days since the last irrigation | |
| `days_act` | Days since the action named in `lim_var` (an action `name` in the same table) last ran | Compared with `lim_const` + 2. |
| `day_start` | Day of year on which the simulation started | |
| `irr_year` | Irrigation applied to the HRU, mm | In 62.0.1 the total is not reset each year, so it is the total since the start of the run. |
| `slope` | HRU slope, m/m | |
| `soil_water` | Soil water content above wilting point, mm | Target: `lim_var` (`wp` = 0, `fc` = water at field capacity, `ul` = water at saturation), combined with `lim_const` by `lim_op`. |
| `jday` | Day of year | |
| `month` | Month | |
| `year_rot` | Year of the crop rotation | Starts at the plant community's initial rotation year and increases by 1 each 31 December. |
| `year_gro`, `cur_yrs_mat` | Years of growth of plant 1 | Same value for both names. |
| `year_cal` | Calendar year | |
| `year_seq` | Year of the simulation (1 for the first year) | |
| `year_start` | First calendar year of the simulation | |
| `biomass` | Above-ground plant biomass, kg/ha | |
| `leaf_area` | Leaf area index of all plants | |
| `ground_cov` | Above-ground plant biomass, kg/ha | Residue is not included in 62.0.1, so it gives the same value as `biomass`. |
| `p_factor` | USLE P factor | |
| `k_factor` | USLE K factor of the top soil layer | |
| `hyd_soil_group` | Soil hydrologic group equals `lim_var` (`A`, `B`, `C` or `D`) | Yes/no. |
| `p_pet` | Ratio of average annual precipitation to PET from the weather generator | |
| `p_lab_150` | Labile phosphorus in the upper soil, ppm | Uses the first two soil layers. |
| `soil_temp2` | Temperature of soil layer 2, °C | |
| `soil_carbon` | Organic carbon of soil layer 1, % | |
| `tile_drained` | The HRU has tile drains | `=` true, `/` false. |
| `prob` | A uniform random number between 0 and 1 | Compared with `lim_const`; use `<` to act with probability `lim_const`. |
| `prob_unif` | Today is the drawn application day | See [Probability conditions](#probability-conditions). |
| `prob_unif1` | Random draw within a window that starts on 1 January | See [Probability conditions](#probability-conditions). |
| `prob_unif_lu` | Random draw that spreads an operation over the HRUs of a land use | See [Probability conditions](#probability-conditions). |
| `channel_flo` | Flow in the current hydrograph, m³/s | |
| `tile_flo` | Tile flow from the HRU today, mm | |
| `irr_demand` | Irrigation demand of the HRU, m³ | |
| `irr_pou_dmd` | Demand of water allocation place of use `obj_num`, m³ | |
| `aqu_dep` | Depth to the water table of aquifer `obj_num`, m | |
| `land_use` | HRU land use equals `lim_var` (a name in [`landuse.lum`](lum.md)) | Yes/no. |
| `cal_group` | HRU calibration group in [`landuse.lum`](../input-reference/lum.md) equals `lim_var` | Yes/no. |
| `tillage` | The HRU's management schedule lists the decision table named in `lim_var` | Yes/no. |
| `plant_com` | The plant named in `lim_var` is in the plant community | `=` true, `/` false. |
| `ch_order` | Stream order of channel `obj_num` equals `lim_const` | Yes/no. |
| `wtow_vol` | Water in water tower `obj_num`, m³ | Target: `lim_const` × tower capacity. |
| `vol` | Reservoir volume, m³ | Target: `lim_var` `pvol` (principal volume) or `evol` (emergency volume) combined with `lim_const` by `lim_op`. With `+` and `-`, `lim_const` is in ha·m. With `lim_var` `e-pv`, the target is $V_p + \mathrm{lim\_const}\,(V_e - V_p)$. |
| `res_inflo` | Inflow to reservoir `obj_num`, m³/s | |
| `wet_depth` | Water depth of the HRU wetland or paddy | `lim_const` in mm. |
| `weirh` | Weir height of the HRU wetland or paddy | `lim_const` in mm. |
| `vol_wet` | Water volume of the HRU wetland or paddy, m³ | Target: `lim_var` `pvol` or `evol` combined with `lim_const` by `lim_op`. |

### Probability conditions

These three conditions let an operation happen on a random day within a window instead of on a fixed date.

`prob_unif` uses the columns differently from other conditions: `obj` is the probability $f$ that the operation happens at all this year, `obj_num` is the first day of the window and `lim_const` is the last day (day of year). On the first day of the window SWAT+ decides, with probability $f$, whether the operation will happen this year, and if so draws one day in the window at random. The condition is true only on that day. A window that ends before it starts (for example 330 to 30) runs over the turn of the year.

`prob_unif1` uses `obj_num` as a calendar year and `lim_const` as a number of days. The window starts on 1 January of that year. On each day of the window the condition is true with probability $1/n$, where $n$ is the number of days left in the window.

`prob_unif_lu` uses `obj_num` as the first day and `lim_const` as the last day of the window. It is meant to be combined with a `land_use` condition in the same table: it spreads the operation over the HRUs of that land use so that the share of HRUs treated by day $d$ follows a uniform distribution over the window.

## Land use and management actions

Actions in `lum.dtl`. Unless stated otherwise, `obj` is `hru` and `obj_num` 0 means the HRU being checked.

| `act_typ` | `option` | `const` | `const2` | `fp` | Effect |
|-----------|----------|---------|----------|------|--------|
| `plant` | plant name in the community | - | - | name in [`transplant.ops`](../input-reference/management.md#transplantops) | Starts growth of the plant if it is not already growing. With a transplant entry, the plant starts from the transplant state (see [`management.sch`](management.md#transplantops)). |
| `harvest` | plant name, or `all` | residue harvest efficiency | per year | name in [`harv.ops`](ops.md#harvops) | Harvests the plant. |
| `harvest_kill` | plant name, or `all` | residue harvest efficiency | per year | name in [`harv.ops`](../input-reference/ops.md#harvops) | Harvests and kills the plant. |
| `kill` | plant name, or `all` | - | per year | - | Kills the plant; biomass becomes residue. |
| `till`, `tillage` | name in [`tillage.til`](til.md) | - | per year | - | Tillage. |
| `fertilize` | name in [`fertilizer.frt`](frt.md) | amount, kg/ha | per year | name in [`chem_app.ops`](ops.md#chem_appops) | Applies fertilizer. On an HRU with standing water and a method with `surf_frac` 1, the fertilizer goes into the water. |
| `fert_future` | name in [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt) | amount, kg/ha | day of year | name in [`chem_app.ops`](../input-reference/ops.md#chem_appops) | Schedules a fertilizer application on the given day. `obj_num` is the sequence number of the `fert_future` action in the table. |
| `manure` | - | amount, kg/ha | per year | - | In 62.0.1 the manure and method names are not looked up, so this action applies an empty fertilizer entry. Use `fertilize` with a manure from [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt), or `manure_demand`. |
| `manure_demand` | name in [`chem_app.ops`](../input-reference/ops.md#chem_appops) | amount, t/ha | per year | - | Sets a manure request for [manure allocation](manure-allocation.md). `obj_num` is the manure source number. |
| `pest_apply` | pesticide name listed in [`constituents.cs`](../input-reference/cs.md#constituentscs) | amount, kg/ha | per year | name in [`chem_app.ops`](../input-reference/ops.md#chem_appops) | Applies the amount times the method's `app_eff`. |
| `graze` | name in [`graze.ops`](ops.md#grazeops) | - | - | - | One day of grazing. |
| `burn` | name in [`fire.ops`](ops.md#fireops) | - | per year | - | Burns plants and residue. |
| `irrigate` | name in [`irr.ops`](ops.md#irrops) | depth, mm | per year | - | Irrigates with $\mathrm{const} \cdot \mathrm{eff\_frac} \cdot (1-\mathrm{sumq\_frac})$. `obj` and `obj_num` name the source: `aqu`, `cha` or `sdc`, or `res` takes the water from that object and irrigates nothing if it has too little; any other `obj` (for example `hru`) is an unlimited source. With `name` `ponding`, the HRU is a paddy: `const` is the target ponding depth (mm), `const2` the depth below which water is added, and the depth applied is the shortfall from the target. |
| `irr_demand` | name in [`irr.ops`](../input-reference/ops.md#irrops) | depth, mm | per year | `unlim` or other | Sets the HRU's irrigation demand for water allocation ($\mathrm{const} \times$ area). With `fp` `unlim`, the `amt_mm` of the [`irr.ops`](../input-reference/ops.md#irrops) entry is applied directly. With `name` `ponding`, `const` and `const2` are the target and threshold ponding depths (mm). |
| `res_irr_dmd` | - | depth, mm | - | - | Records an irrigation demand on reservoir `obj_num`. |
| `rot_reset` | - | rotation year | - | - | Sets the rotation year (minimum 1). |
| `plant_reset`, `harv_reset`, `kill_reset`, `irr_reset` | - | days | - | - | Sets the days since the last planting, harvest, kill or irrigation (minimum 1). |
| `pheno_reset` | - | - | per year | - | Restarts the phenology of plants with a `moisture_gro` trigger in [`plants.plt`](../input-reference/plt.md). |
| `cn_update` | `absval`, `abschg`, `pctchg` or `relchg` | value | per year | - | Changes the curve number for moisture condition II: set to the value, add the value, change by the value in percent, or multiply by (1 + value). The result is kept between 35 and 95. |
| `tiledep_control` | - | drain depth, mm | per year | - | Sets the tile drain depth for drainage water management. |
| `impound_on` | - | - | - | name in [`wetland.wet`](wet.md) | Turns on impounded water (paddy or wetland) on the HRU. |
| `impound_off` | - | - | - | - | Turns off impounded water on the HRU. |
| `weir_height` | `wet`, or other | height, mm | - | - | With `wet`, sets the HRU paddy weir height and the principal and emergency volumes from it. Otherwise sets the weir height of reservoir `obj_num`. |
| `puddle` | name in [`puddle.ops`](../input-reference/management.md#puddleops) | - | per year | - | Puddles a paddy (see [`management.sch`](management.md#puddleops)). The action `name` must be the tillage operation in [`tillage.til`](../input-reference/til.md) used for the soil mixing. |
| `lu_change` | - | - | - | name in [`landuse.lum`](lum.md) | Changes the HRU's land use and management and reinitialises plants and curve number. Logged in `lu_change_out.txt`. |
| `snow_change` | - | - | - | name in [`snow.sno`](sno.md) | Switches the HRU to another snow parameter set. Logged in `lu_change_out.txt`. |
| `hru_fr_update` | new [`ls_unit.ele`](../input-reference/units.md#ls_unitele) file | - | - | new [`rout_unit.ele`](../input-reference/units.md#rout_unitele) file | Updates HRU area fractions. Logged in `lu_change_out.txt`. |
| `p_factor` | - | new USLE P | - | - | Sets the USLE P factor. |
| `contour` | - | - | - | - | Sets $P = 2.7\,S + 0.26$, with $S$ the slope (m/m). |
| `stripcrop` | - | - | - | `pasture` or other | Sets $P = 2.32\,S + 0.36$, halved when `fp` is `pasture`. |
| `terrace` | - | - | - | `sod_outlet` or other | Sets $P = 1.4\,S + 0.13$, doubled when `fp` is `sod_outlet`. |
| `tile_install` | - | - | - | name in [`tiledrain.str`](../input-reference/str.md#tiledrainstr) | Installs tile drains (see [`*.str`](str.md)). |
| `septic_install` | - | - | - | name in [`septic.str`](../input-reference/str.md#septicstr) | Installs a septic system. |
| `fstrip_install` | - | - | - | name in [`filterstrip.str`](../input-reference/str.md#filterstripstr) | Installs a filter strip. |
| `grassww_install`, `grassww_uninstall` | - | - | - | name in [`grassedww.str`](../input-reference/str.md#grassedwwstr) | Installs or removes a grassed waterway. |
| `user_def_bmp` | - | - | - | name in [`bmpuser.str`](../input-reference/str.md#bmpuserstr) | Applies user-defined BMP removal fractions. |
| `grow_init`, `grow_end` | - | - | - | - | Start and end of the growing season of an HRU-lte (`obj` `hlt`). `grow_end` computes the yield. |
| `chan_change` | - | cover | stream order | - | Sets the cover and stream order of the channel being checked. |
| `herd` | - | - | - | - | No effect in 62.0.1. |

The `plant`, `harvest` and `harvest_kill` actions of the generic tables `pl_hv_summer1`, `pl_hv_winter1` and `pl_hv_summer2` take the plant name from [`management.sch`](../input-reference/management.md#managementsch) instead of `option` (see [`management.sch`](management.md#automatic-operations)).

Flow control and water allocation actions, used in `flo_con.dtl`:

| `act_typ` | `option` | `const` | `const2` | Effect |
|-----------|----------|---------|----------|--------|
| `tileflo_control` | `flo_mm`, `max_mm` (at most `const` mm), `min_mm` (at least `const` mm), `all_flo`, `zero_flo`, `frac` (`const` × tile flow) | mm or fraction | - | Sets the tile flow sent from a saturated buffer source HRU to its receiving HRU. |
| `wallo_dmd` | `set_dmd` | demand, m³ | - | Sets the demand of a water allocation place of use. |
| `wallo_dmd` | `irr_dmd` | - | - | Adds the irrigation demand of place of use `obj_num`. |
| `wallo_dmd` | `fill_res`, `fill_wtow`, `fill_can` | target fraction of capacity | fraction of the shortfall per day | Demand to fill reservoir, water tower or canal `obj_num` to `const` times its capacity (for `fill_res`, `fp` `pvol` or `evol`). |
| `duty_fr` | `fr1` to `fr6` | fraction | - | Fraction of the demand taken from point of diversion 1 to 6 (or sent to return 1 to 6). |
| `duty_reset` | - | point of diversion number | new maximum withdrawal | Resets the withdrawal limit of a point of diversion of place of use `obj_num`. |

See [water allocation](water-allocation.md) for how these demands and fractions are used.

## Reservoir release actions

In `res_rel.dtl` the action type is `release` and `option` selects how the release is computed. The releases of all actions that run on a day are added together. A table with zero alternatives runs all its actions every day. $V$ is the current volume, $V_p$ the principal and $V_e$ the emergency volume.

| `option` | `const` | `const2` | `fp` | Release |
|----------|---------|----------|------|---------|
| `rate` | rate, m³/s | - | - | constant rate |
| `rate_pct` | percent | - | - | `const` % of $V_p$ per day |
| `inflo_rate` | maximum rate, m³/s | change to inflow, m³/s | - | the larger of inflow + `const2` and `const` |
| `inflo_frac` | fraction | - | - | `const` × inflow |
| `ab_emer` | - | - | - | all volume above $V_e$ |
| `days` | days | multiplier | `null`, `pvol` or `evol` | $(V - V_t)/\mathrm{const}$, with target $V_t$ = 0, `const2` × $V_p$ or `const2` × $V_e$ |
| `dyrt` | days | percent | `null`, `pvol` or `evol` | $(V - V_t)/\mathrm{const}$ plus `const2` % of $V_p$, with $V_t$ = 0, $V_p$ or $V_e$ |
| `dyrt1` | days | percent | `con1`, `con2` or `con3` | as `dyrt`, with the target taken from condition 5, 4 or 3 of the table |
| `inflo_targ` | condition number | - | - | inflow plus all volume above $V_p$ × that condition's `lim_const` |
| `weir` | - | - | name in [`weir.res`](../input-reference/res.md#weirres) | weir equation |
| `meas` | - | - | name of a recall object | measured outflow |
| `natlake` | inactive storage, fraction of $V_p$ | release coefficient, 1/day | - | natural lake outflow (Döll et al., 2003) |
| `nonirr-h06` | $\alpha$ | - | - | Hanazaki et al. (2006) scheme for non-irrigation reservoirs |
| `irr-h06` | $\alpha$ | $\beta$ | - | Hanazaki et al. (2006) scheme for irrigation reservoirs |
| `hydrop` | amplitude | phase | - | HYPE hydropower scheme (Arheimer et al., 2019) |

See [`*.res`](res.md) for the reservoir side of these options.

## Land use scenarios

Tables in `scen_lu.dtl` run only if they are listed in `scen_dtl.upd`. That file has a title line, the number of entries, a header line, and one row per entry with three columns: `max_hits`, `typ` and the name of a table in `scen_lu.dtl`. Each listed table is checked for every HRU every day, before the HRUs are simulated. The usual actions are `lu_change` and `snow_change`.

## Example

`refdata/Ames_sub1/lum.dtl` in the SWAT+ repository contains two tables:

```
lum.dtl: yearly irrigation limit example for Ames dataset
2

name                     conds      alts      acts       !limit yearly irrigation to 500 mm using irrigate action
irr_year_irr                4         1         1
var                        obj   obj_num           lim_var            lim_op  lim_const      alt1
irr_year                   hru         0              null                 -   500.00000         <
w_stress                   hru         0              null                 -   0.80000           <
phu_plant                  hru         0           phu_mat                 -     0.20000         >
leaf_area                  hru         0           null                    -     0.50000         >
act_typ                    obj   obj_num              name            option    const        const2                fp  outcome
irrigate                   hru        0           sprinkler     sprinkler_ilm    25.00000   20.00000  unlim  y
```

Table `irr_year_irr` has four conditions, one alternative and one action. The alternative is satisfied on a day when the irrigation applied so far is below 500 mm, the average water stress factor is below 0.8, the crop has accumulated more than 20% of its heat units, and the leaf area index is above 0.5. On such a day the HRU is irrigated with 25 mm using the `sprinkler_ilm` entry of [`irr.ops`](../input-reference/ops.md#irrops), at most 20 times a year. `obj` is `hru`, so the water comes from an unlimited source. The table is used by naming `irr_year_irr` as an automatic operation in [`management.sch`](../input-reference/management.md#managementsch). In 62.0.1 the irrigation total behind `irr_year` is not reset each year, so once 500 mm has been applied over the whole run, the table stops irrigating for the rest of the simulation.

A reservoir table from `refdata/Osu_1hru/res_rel.dtl`, followed by the blank line that `res_rel.dtl` needs:

```
name                     conds      alts             acts
paddy_auto_rel               2         2                2
var                        obj   obj_num           lim_var            lim_op     lim_const      alt1   alt2
wet_depth                  hru         0          weir_hgt                 -       0.00000         >       -
wet_depth                  hru         0              null                 -       2.00000         >       >
act_typ                    obj   obj_num              name            option         const        const2       fp      outcome
release                    hru         0        above_emer              days       1.00000       0.00000      null    y   n
release                    hru         0        below_emer              weir      10.00000       0.00000      weir1   y   n

```

Both alternatives need a water depth above 2 mm, and the first also above 0 mm. When the first alternative is satisfied, the paddy releases its whole volume within one day (`days` with `const` 1 and target 0) and also releases over the weir `weir1`.

## Related files

- [`management.sch`](management.md): lists the `lum.dtl` tables each HRU uses.
- [`*.ops`](ops.md), [`tillage.til`](til.md), [`fertilizer.frt`](frt.md), [`landuse.lum`](lum.md), [`snow.sno`](sno.md), [`*.str`](str.md): databases named by actions.
- [`*.res`](res.md) and [`*.wet`](wet.md): name the release tables in `res_rel.dtl`.
- [Water allocation](water-allocation.md) and [manure allocation](manure-allocation.md): name tables in `lum.dtl` and `flo_con.dtl`.
- [`file.cio`](file-cio.md): names the four files on its `decision_table` line.

??? quote "Sources"

    - Readers: [`dtbl_lum_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_lum_read.f90), [`dtbl_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_res_read.f90), [`dtbl_scen_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_scen_read.f90), [`dtbl_flocon_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_flocon_read.f90), [`cal_cond_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_cond_read.f90) (`scen_dtl.upd`)
    - Type definitions: [`conditional_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditional_module.f90)
    - Conditions: [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`cond_real.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cond_real.f90), [`cond_integer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cond_integer.f90)
    - Actions: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90); reservoir releases: [`res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90)
    - Linking tables to HRUs: [`proc_cond.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cond.f90), [`hru_dtbl_actions_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_dtbl_actions_init.f90)
    - Callers: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90), [`res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), [`wallo_start_day.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_start_day.f90), [`mallo_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mallo_control.f90)
    - File name slots: `type input_condition` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | condition `var`, `obj`, `obj_num`, `lim_var`, `lim_op`, `lim_const` | `d_tbl%cond(ic)%var`, `%ob`, `%ob_num`, `%lim_var`, `%lim_op`, `%lim_const` |
    | `alt1` ... | `d_tbl%alt(ic, ialt)` |
    | `prob_unif` probability (`obj` column) | `d_tbl%frac_app` |
    | action `act_typ` | `d_tbl%act(iac)%typ` |
    | action `obj`, `obj_num`, `name`, `option`, `const`, `const2` | `d_tbl%act(iac)%ob`, `%ob_num`, `%name`, `%option`, `%const`, `%const2` |
    | action `fp` | `d_tbl%act(iac)%file_pointer` |
    | `outcome1` ... | `d_tbl%act_outcomes(iac, ialt)` |

---
title: manure_allo.mnu
description: Manure allocation. Manure sources with monthly production, and the HRUs that draw manure from them. Applies no manure in 62.0.1.
status: review
verified_against:
  - src/manure_allocation_read.f90
  - src/manure_allocation_module.f90
  - src/mallo_control.f90
  - src/actions.f90
  - src/dtbl_lum_read.f90
  - src/hru_dtbl_actions_init.f90
  - src/time_control.f90
  - src/command.f90
  - src/manure_source_output.f90
  - src/manure_demand_output.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`manure_allo.mnu` sets up manure allocation: manure sources with a monthly production, and HRUs that receive manure from them when a decision table in [`lum.dtl`](dtl.md) asks for it. The file name is fixed. If the file is missing, manure allocation is off.

SWAT+ 62.0.1 reads this file and checks the decision tables every day, but applies no manure to any HRU. To apply manure, use a `fertilize` action in [`lum.dtl`](../input-reference/dtl.md) or a `manu` operation in [`management.sch`](management.md).

## Format

Free format, whitespace-separated.

- Line 1: title (skipped).
- Line 2: number of allocation objects.
- Then, for each allocation object:
    1. header line (skipped);
    2. object line: `name`, `rule_typ`, `src_obs`, `trn_obs`;
    3. header line (skipped);
    4. `src_obs` source lines;
    5. header line (skipped);
    6. `trn_obs` demand lines.

### Object line

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Allocation object name. |
| 2 | `rule_typ` | Allocation rule. Read but not used. |
| 3 | `src_obs` | Number of source lines. |
| 4 | `trn_obs` | Number of demand lines. |

### Source lines

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `num` | - | Source number, 1 to `src_obs`. The line is stored at this position. |
| 2 | `mois_typ` | - | Moisture class, `wet` or `dry`. |
| 3 | `manure_typ` | - | Manure name in [`fertilizer.frt`](frt.md). |
| 4 | `lat` | degrees | Latitude of the source. |
| 5 | `long` | degrees | Longitude of the source. |
| 6 | `stor_init` | t | Manure in storage at the start of the simulation. |
| 7 | `stor_max` | t | Storage capacity. |
| 8 to 19 | `prod_jan` ... `prod_dec` | t/month | Manure produced in each month, January to December. |

### Demand lines

| # | Column | Description |
|---|--------|-------------|
| 1 | `num` | Demand number, 1 to `trn_obs`. The line is stored at this position. |
| 2 | `ob_typ` | Receiving object type: `hru`, `muni` (treatment) or `divert` (diversion out of the basin). Only `hru` demands are linked to a decision table. |
| 3 | `ob_num` | Number of the receiving object. |
| 4 | `dtbl` | Name of the decision table in [`lum.dtl`](../input-reference/dtl.md) that requests manure for this HRU, or `null`. |
| 5 | `right` | Manure right, `sr` (senior) or `jr` (junior). |

The decision table requests manure with a `manure_demand` action: `obj_num` is the source number, `option` the application method in [`chem_app.ops`](ops.md#chem_appops), `const` the amount in t/ha and `const2` the maximum number of requests per year (see [`*.dtl`](dtl.md#land-use-and-management-actions)).

## Example

One allocation object with one source and one HRU demand:

```
manure_allo.mnu: example
1
name            rule_typ    src_obs  trn_obs
farm_a          fixed             1        1
num  mois_typ  manure_typ  lat       long      stor_init  stor_max   prod_jan  feb  mar  apr  may  jun  jul  aug  sep  oct  nov  dec
  1  wet       beef_fr     41.99   -93.62          0.0       500.0    5.0  5.0  6.0  6.0  7.0  7.0  7.0  7.0  6.0  6.0  5.0  5.0
num  ob_typ    ob_num  dtbl                 right
  1  hru            1  apply_manure          sr
```

With a table `apply_manure` in [`lum.dtl`](../input-reference/dtl.md) whose first action is `manure_demand` with source 1, method `broadcast` and 2 t/ha, the intent is to apply 2 t/ha of `beef_fr` from the source whenever the table's conditions are met. In 62.0.1 the request is recorded but nothing is applied.

## Related files

- [`fertilizer.frt`](frt.md): the manure named in `manure_typ`.
- [`*.dtl`](dtl.md): the decision tables named on demand lines and the `manure_demand` action.
- [`chem_app.ops`](ops.md#chem_appops): application methods.

??? quote "Sources"

    - Reader: [`manure_allocation_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_allocation_read.f90), called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) after `dtbl_lum_read`
    - Types: [`manure_allocation_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_allocation_module.f90) (`manure_allocation`, `manure_source_objects`, `manure_demand_objects`)
    - Daily calculation: [`mallo_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mallo_control.f90), called from [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - `manure_demand` action: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90), cross-walk in [`dtbl_lum_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_lum_read.f90)
    - HRU decision table slot: [`hru_dtbl_actions_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_dtbl_actions_init.f90)
    - Output: [`manure_source_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_source_output.f90), [`manure_demand_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_demand_output.f90), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | object line | `mallo%name`, `%rule_typ`, `%src_obs`, `%trn_obs` |
    | source `manure_typ` | `mallo%src%manure_typ` (index in `mallo%src%fertdb`) |
    | source `prod_jan` ... `prod_dec` | `mallo%src%prod_mon(1:12)` |
    | demand `dtbl` | `mallo%trn%dtbl` (index in `mallo%trn%dtbl_num` and `hru%man_trn_dtbl`) |
    | `manure_demand` `obj_num`, `const`, `option` | `manure_amt%src_obj`, `%app_t_ha`, `%app_method` |

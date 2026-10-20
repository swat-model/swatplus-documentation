---
title: Conditions and regionalization
description: Limit a calibration.cal change to objects that meet conditions, and set up regional calibration with calibration groups or object lists.
status: review
verified_against:
  - src/cal_parmchg_read.f90
  - src/cal_conditions.f90
  - src/cal_cond_read.f90
  - src/hrudb_init.f90
  - src/landuse_data_module.f90
  - src/time_control.f90
  - src/calibration_data_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A row of [`calibration.cal`](../calibration/parameter-change-files.md) can be followed by condition lines. SWAT+ then changes the parameter only on the objects that meet every condition of the row. Conditions are checked once, at start-up, against the state of each object after the inputs are read.

Conditions and object lists are the two ways to calibrate parts of a watershed separately, for example one set of curve number changes for cropland and another for forest, or different groundwater parameters upstream and downstream of a gauge.

## Condition lines

The number of condition lines is given in the `conds` column of the change row, and the lines follow the row directly. Each line has one of two forms.

**Range condition**

```
range  <variable>  <min>  <max>
```

The object's value must be greater than `<min>` and less than `<max>`.

**Text condition**

```
<variable>  <operator>  <number>  <text>
```

The object's value must equal `<text>`. All four values must be present. The operator and number are read but none of the existing conditions uses them, so any placeholder works (for example `=` and `0`).

When a row has several condition lines, an object must meet all of them.

## Condition variables

| Variable | Form | Objects | Condition met when |
|----------|------|---------|--------------------|
| `cal_group` | text | HRU | the `cal_group` of the HRU's land use in [`landuse.lum`](../input-reference/lum.md) equals the text |
| `landuse` | text | HRU | the HRU's land use name (the `lu_mgt` entry of [`hru-data.hru`](../input-reference/hru.md)) equals the text |
| `hsg` | text | HRU | the hydrologic soil group of the HRU's soil (`hyd_grp` in [`soils.sol`](../input-reference/sol.md)) equals the text, for example `C` |
| `texture` | text | HRU | the `texture` of the HRU's soil in [`soils.sol`](../input-reference/sol.md) equals the text |
| `plant` | text | HRU | the first plant of the HRU's plant community is the named plant |
| `pl_class` | text | | see below |
| `res_typ` | text | reservoir decision table | the decision table's name equals the text |
| `res_pvol` | range | reservoir | the principal spillway volume, in 10⁴ m³ (ha-m, as in [`hydrology.res`](../input-reference/res.md#hydrologyres)), is between `<min>` and `<max>` |

The HRU conditions apply to parameters whose object type is `hru`, `sol` or `plt`. They compare against the HRU with the same number as the object being changed, so with other object types (aquifers, channels) they test an unrelated HRU.

Text comparisons are exact and case sensitive, and an unknown variable name is ignored, so a misspelt condition lets every object through.

Notes on specific variables:

- `plant`: only the first plant in the community is checked. For a community of corn and soybean in that order, `plant = corn` matches and `plant = soyb` does not. For the plant parameters `lai_pot`, `harv_idx` and `phu_mat` the `plant` condition has a second role: it names the plant whose value is changed (see [Plant parameters](../calibration/hard-calibration.md#plant-parameters)).
- `pl_class`: compares the class of the plant at the same position in [`plants.plt`](../input-reference/plt.md) as the object number. It does not look at the HRU's plants, so it is not useful for selecting HRUs.
- `res_pvol`: both limits are taken from the last `range` line of the row.

## Regional calibration

### Calibration groups

The most direct way to calibrate regions or land-use groups separately is the `cal_group` column of [`landuse.lum`](../input-reference/lum.md):

1. Give each land use a group name in `cal_group`, for example `crop_north`, `crop_south`, `forest`. Land uses that share a name form one group.
2. Write one change row per group, each with a `cal_group` condition.

```
cn2      pctchg   -8.0   1   0  0  0  0  0  0   0
cal_group  =  0  crop_north
cn2      pctchg    4.0   1   0  0  0  0  0  0   0
cal_group  =  0  forest
```

The same `cal_group` names are used by [soft calibration](../calibration/soft-calibration.md) to match its water balance targets to HRUs.

### Object lists

The other way is to list the objects in the row itself (`obj_tot` and the numbers after it), for example the HRUs, aquifers or channels upstream of a gauge. A negative number closes a range, so `3  1 -120 245` selects objects 1 to 120 and 245. Object lists work for every object type.

Object lists and conditions can be combined: the conditions are then checked only on the listed objects.

## Scheduled land use updates

SWAT+ also reads a file named `scen_dtl.upd` from the project folder, if it exists. It lists decision tables from the scenario decision table file ([`scen_lu.dtl`](../input-reference/dtl.md) by default, named on the `decision_table` line of [`file.cio`](../input-reference/file-cio.md)) that are checked for every HRU at the start of every simulated day. Their actions can change land use, management or other HRU settings during the run, for example to simulate land use change at a set date.

- Line 1: title.
- Line 2: number of tables.
- Line 3: header.
- One line per table: maximum number of times the table may act, table type, and table name.

The maximum and the type are read but not used in 62.0.1: every listed table is checked every day for every HRU.

This file is separate from [`calibration.cal`](../calibration/parameter-change-files.md). Its changes happen during the run, while [`calibration.cal`](../calibration/parameter-change-files.md) changes happen before the run starts. See [Decision tables](../model-theory/decision-tables.md) for how tables are written.

## Related pages

- [Parameter change files](../calibration/parameter-change-files.md). Layout of the change rows.
- [Hard calibration](../calibration/hard-calibration.md). When and how changes are applied.
- [landuse.lum](../input-reference/lum.md). The `cal_group` column.

??? quote "Sources"

    - Reading condition lines: [`src/cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parmchg_read.f90).
    - Evaluating conditions: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90).
    - Calibration group of an HRU: [`src/hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90) copies `lum(ilu)%cal_group` to `hru(ihru)%cal_group`.
    - `scen_dtl.upd`: [`src/cal_cond_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_cond_read.f90); used in [`src/time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90).
    - Types: `type calibration_conditions`, `type update_parameters` and `type update_conditional` in [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90).

    | Condition variable | Compared with |
    |--------------------|---------------|
    | `cal_group` | `hru(ielem)%cal_group` |
    | `landuse` | `hru(ielem)%land_use_mgt_c` |
    | `hsg` | `soil(ielem)%hydgrp` |
    | `texture` | `soil(ielem)%texture` |
    | `plant` | `pcom(ielem)%pl(1)` |
    | `pl_class` | `pl_class(ielem)` |
    | `res_typ` | `dtbl_res(ielem)%name` |
    | `res_pvol` | `res_ob(ielem)%pvol`, against `10000 * val1` and `10000 * val2` |

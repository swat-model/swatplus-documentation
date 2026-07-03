---
title: Conditions and regionalization
description: Apply a parameter change only to objects that match a condition or live in a named region.
status: review
---

A change in `calibration.cal` can carry condition lines that restrict where the change is applied. The conditions are tested object by object in `cal_conditions.f90`. If every condition evaluates true for a given object, the change is passed to `cal_parm_select` for that object; otherwise the object is skipped.

## Source

- Condition evaluation: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_conditions.f90)
- Condition reader: [`src/cal_cond_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_cond_read.f90)
- Parameter dispatch: [`src/cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parm_select.f90)
- Condition record type: [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/calibration_data_module.f90), `type calibration_conditions` and `type update_conditional`.

## Two condition syntaxes

`cal_parmchg_read.f90` peeks at the first token of each condition line:

- If the token is the literal word `range`, the line is read as `range <var> <val1> <val2>`. The condition holds when the value of `<var>` for the current object falls inside `[val1, val2]`. `val1` and `val2` are stored on the parent change record (shared across that record's range conditions).
- Otherwise the line is read as a `calibration_conditions` record: `<var> <alt> <targ> <targc>`. `targ` is a real, `targc` is a string. The reader stores all four fields but `cal_conditions.f90` only uses `var`, `targc`, and `targ` depending on the variable.

## Supported variables

The `select case (cal_upd(ichg_par)%cond(ic)%var)` block in `cal_conditions.f90` accepts:

| Variable | Object type | Form | Semantics |
|----------|-------------|------|-----------|
| `res_pvol` | reservoirs | range | Reservoir principal storage volume (compared in units of 10000). |
| `hsg` | HRU soils | categorical (`targc`) | Hydrologic soil group must equal `targc` (`A`, `B`, `C`, `D`). |
| `res_typ` | reservoirs | categorical (`targc`) | Reservoir decision-table name must equal `targc`. |
| `texture` | HRU soils | categorical (`targc`) | Soil texture string must equal `targc`. |
| `plant` | HRU plant community | categorical (`targc`) | The HRU's plant community must contain a plant named `targc`. |
| `pl_class` | HRU plants | categorical (`targc`) | Plant class for the HRU must equal `targc`. |
| `landuse` | HRU land use management | categorical (`targc`) | `hru%land_use_mgt_c` must equal `targc`. |
| `cal_group` | HRU calibration tag | categorical (`targc`) | `hru%cal_group` must equal `targc`. |

A change with multiple conditions implements an AND: all must hold for the object to be modified.

## Regionalization

Two patterns produce a regional effect:

- **Implicit through `cal_group`.** Tag every HRU with a `cal_group` name (set on the HRU input). Then a change with a `cal_group <name>` condition runs only on that group. This is how named region-based hard calibration is typically done.
- **Explicit object list.** Put the HRU (or channel, or aquifer) indices directly on the change record (`nspu > 0`). No conditions needed. This is what soft calibration writes when it commits its perturbations.

The two can combine: an explicit object list with one or more conditions further filters the list.

## Decision-table conditional updates

`cal_cond_read.f90` reads a separate file, `scen_dtl.upd`, that schedules updates by decision table. Each row gives a maximum number of times the table may fire, a table type, and the name of a `dtbl` entry in `conditional.ctl`. The reader crosswalks the table name into `dtbl_scen` and stores the result in `upd_cond` (`type update_conditional`). The same decision-table machinery used elsewhere in SWAT+ (land-use change scenarios, management triggers) is reused here.

## Parameter dispatch

Once conditions pass, the change is sent to `cal_parm_select.f90` with the parameter name, change type, magnitude, absolute bounds, the target element, and the soil layer (for layer-targeted soil parameters). `cal_parm_select` is a long `select case (chg_parm)` that writes the change into the live model state via `chg_par` (the change operator) and calls the relevant re-initializer (`curno` for `cn2`, `soil_awc_init` for `awc`, and so on).

## Related pages

- [Parameter change files](../calibration/parameter-change-files.md). The columns that hold these conditions on disk.
- [Hard calibration](../calibration/hard-calibration.md). When conditions are evaluated in the calibration run.

---
title: Hard calibration
description: Adjust named SWAT+ parameters within absolute bounds and re-run the model.
status: review
---

Hard calibration applies a list of named parameter changes from `calibration.cal`, re-initializes all model objects, then re-runs the time loop. Each change names a parameter, a change type (`absval`, `abschg`, `pctchg`), a value, a list of objects (HRUs, channels, aquifers, plants, ...) to apply the change to, and optional conditions. The parameter universe and the absolute min/max for each parameter are defined in `cal_parms.cal`.

## Source

- Driver: [`src/calhard_control.f90`](https://github.com/swat-model/swatplus/blob/main/src/calhard_control.f90)
- Parameter selector: [`src/cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parm_select.f90)
- Change application with conditions: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_conditions.f90)
- Parameter database reader: [`src/cal_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parm_read.f90)
- Change list reader: [`src/cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cal_parmchg_read.f90)

## Workflow

1. The model is run once normally. Output baseline is captured.
2. The user edits `calibration.cal` with the parameter changes to test (or an external driver writes it).
3. SWAT+ is re-launched. During startup, `cal_parm_read` loads `cal_parms.cal` into the `cal_parms` array and `cal_parmchg_read` loads `calibration.cal` into the `cal_upd` array. Each `cal_upd` entry is crosswalked to its `cal_parms` entry by name to pick up the absolute bounds and object type.
4. Inside the simulation, `cal_conditions` is called once. For every entry in `cal_upd`, it evaluates the conditions, then walks the element list and calls `cal_parm_select` for each affected object. `cal_parm_select` does the actual write into the live model state (HRU, channel, aquifer, plant, soil layer, climate series).
5. The master switch `cal_hard = "y"` triggers a second pass: `calhard_control` calls `re_initialize` then `time_control`, re-running the full simulation with the modified parameters.

The change type drives how the value is applied to the existing parameter:

| `chg_typ` | Effect |
|-----------|--------|
| `absval` | The new value replaces the existing one. |
| `abschg` | The value is added to the existing one (signed). |
| `pctchg` | The value is interpreted as a percent change. |

After every change the result is clamped to the `[absmin, absmax]` range from `cal_parms.cal`.

## Object types

`cal_parms.cal` tags each parameter with an object type (`ob_typ`). The type determines which collection in the model state is iterated when the change is applied:

| Code | Collection | Examples |
|------|------------|----------|
| `hru` | HRUs | `cn2`, `ovn`, `lat_ttime`, `canmx` |
| `hlt` | `hru_lte` | parameters of the simplified HRU |
| `sol` | Soil layers within an HRU (`lyr1`/`lyr2` select the range) | `awc`, `bd`, `k` |
| `lyr` | Soil layers | layer-targeted variants |
| `plt` | Plants | `lai_pot`, `harv_idx`, `epco`, `phu_mat` |
| `aqu` | Aquifers | `alpha`, `revap_co`, `flo_min` |
| `cha`, `sdc`, `rte` | Channels (legacy, degraded, routed) | channel routing and sediment parameters |
| `swq` | Channel water quality | nutrient parameters |
| `res` | Reservoirs | `res_pvol`, surface area parameters |
| `rdt` | Reservoir decision tables | `drawdown_days`, `withdraw_rate` |
| `ru` | Routing units | RU-level parameters |
| `bsn` | Basin | basin-wide scalars in `parameters.bsn` |
| `pcp`, `tmp`, `cli` | Climate gauges and series | `precip`, `temp` adjustments over date ranges |
| `gwf` | gwflow cells | gwflow parameters |

The list above is taken from the `select case (cal_parms(ipar)%ob_typ)` block in `cal_parmchg_read.f90` and the dispatch in `cal_conditions.f90`.

## Re-initialization

`calhard_control.f90` calls `re_initialize` before re-running. This resets simulation state (water content, plant state, accumulators) so the second run is comparable to the baseline rather than continuing from baseline end-state.

## Related pages

- [Parameter change files](../calibration/parameter-change-files.md). Column-level format of `cal_parms.cal` and `calibration.cal`.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Limiting a change to HRUs that match a condition.
- [Sensitivity workflow](../calibration/sensitivity-workflow.md). Driving hard calibration from an external sampler.
- [Soft calibration](../calibration/soft-calibration.md). Adjust process outputs toward regional targets before fitting to time series.

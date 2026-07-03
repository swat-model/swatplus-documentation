---
title: Calibration
description: Hard and soft calibration workflows in SWAT+, plus parameter change files and sensitivity analysis.
status: review
---

SWAT+ supports two calibration modes that are configured and run from inside the model.

- **Hard calibration** fits named model parameters to observed time series (streamflow, sediment, nutrient loads). Parameter values are perturbed within absolute bounds, the model is re-run, and the simulation is compared with measured data. Implemented in `calhard_*.f90`. Driven by `cal_parms.cal` (parameter definitions and bounds) and `calibration.cal` (the change list applied each run).
- **Soft calibration** adjusts process outputs toward regional water-balance and yield targets without exposing the underlying parameters as a sample space. Targets are expressed as fractions of precipitation for the water balance, channel sediment budgets, and plant growth. Implemented in `calsoft_*.f90`. Driven by `codes.sft`, `wb_parms.sft`, `water_balance.sft`, `ch_sed_budget.sft`, `ch_sed_parms.sft`, `plant_parms.sft`, and `plant_gro.sft`.

The two modes share the same internal parameter selector (`cal_parm_select.f90`) and the same conditional change machinery (`cal_conditions.f90`).

## Pages

- [Hard calibration](../calibration/hard-calibration.md). Parameter perturbation, sources, the role of `calibration.cal`.
- [Soft calibration](../calibration/soft-calibration.md). Regional water balance and yield targets, sources, the role of `codes.sft`.
- [Parameter change files](../calibration/parameter-change-files.md). Format of `cal_parms.cal` and `calibration.cal`, verified against the readers.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Applying a change only to HRUs that match a condition (HSG, texture, plant, land use, calibration group).
- [Sensitivity workflow](../calibration/sensitivity-workflow.md). Driving SWAT+ from an external tool to compute sensitivity indices, using the same `cal_parms.cal` to define the sample space.

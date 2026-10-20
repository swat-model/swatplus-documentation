---
title: Calibration
description: Hard and soft calibration in SWAT+, the parameter change files that drive them, and sensitivity analysis with external tools.
status: review
verified_against:
  - src/main.f90.in
  - src/proc_cal.f90
  - src/cal_conditions.f90
  - src/calsoft_control.f90
  - src/calibration_data_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ can change model parameters from inside the model, using two kinds of calibration data.

**Hard data** are measured time series at a point, such as daily streamflow at a gauge, sediment or nutrient loads, or groundwater levels. Fitting the model to hard data is done by an external tool (SWAT+ Toolbox, SWAT-CUP, a script) that writes a parameter change list to [`calibration.cal`](../calibration/parameter-change-files.md), runs SWAT+, compares the output with the observations and repeats. SWAT+ applies the change list at start-up, before the simulation begins.

**Soft data** are estimates of individual processes that are not measured at the site, or only as long-term averages: the share of precipitation that leaves as surface runoff or evapotranspiration, the baseflow share of streamflow, or an average county crop yield (Seibert and McDonnell, 2002; Arnold et al., 2015). SWAT+ fits these itself. After the normal run it adjusts a few water balance and plant parameters one at a time, rerunning the simulation after each change, until the average annual values for each land-use group match the targets.

The usual order is soft calibration first, so that each part of the water balance is about right, then hard calibration against the gauge record, which should then need mostly adjustments to peaks and recessions.

## Pages

- [Hard calibration](../calibration/hard-calibration.md). How SWAT+ applies a parameter change list, change types and object types.
- [Parameter change files](../calibration/parameter-change-files.md). Layout of [`cal_parms.cal`](../calibration/parameter-change-files.md) and [`calibration.cal`](../calibration/parameter-change-files.md), and every parameter name SWAT+ accepts.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Applying a change only to objects that match a condition, such as a soil group, land use or calibration group.
- [Soft calibration](../calibration/soft-calibration.md). The [`codes.sft`](../calibration/soft-calibration.md) switches, the targets in each `.sft` file, the adjustment steps and the output files.
- [Sensitivity workflow](../calibration/sensitivity-workflow.md). Running a sensitivity analysis with an external sampler that writes [`calibration.cal`](../calibration/parameter-change-files.md).

## References

Arnold, J. G., Youssef, M. A., Yen, H., White, M. J., Sheshukov, A. Y., Sadeghi, A. M., Moriasi, D. N., Steiner, J. L., Amatya, D. M., Skaggs, R. W., Haney, E. B., Jeong, J., Arabi, M., and Gowda, P. H. (2015). Hydrological processes and model representation: impact of soft data on calibration. Transactions of the ASABE, 58(6), 1637–1660.

Seibert, J., and McDonnell, J. J. (2002). On the dialog between experimentalist and modeler in catchment hydrology: use of soft data for multicriteria model calibration. Water Resources Research, 38(11), 1241.

??? quote "Sources"

    - Calibration start-up: [`src/proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90), called from [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) before the simulation.
    - Hard calibration changes: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90) and [`src/cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90).
    - Soft calibration: [`src/calsoft_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_control.f90), run from `main.f90.in` after the base simulation when `cal_soft = "y"`.
    - Data types: [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90).

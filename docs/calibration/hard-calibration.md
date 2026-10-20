---
title: Hard calibration
description: How SWAT+ applies the parameter changes in calibration.cal at start-up, and how external tools use this to fit the model to measured time series.
status: review
verified_against:
  - src/main.f90.in
  - src/proc_cal.f90
  - src/cal_parm_read.f90
  - src/cal_parmchg_read.f90
  - src/cal_conditions.f90
  - src/cal_parm_select.f90
  - src/chg_par.f90
  - src/calhard_control.f90
  - src/calibration_data_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Hard calibration fits the model to measured time series such as streamflow, sediment or nutrient loads at a gauge. SWAT+ does not search for parameter values itself. An external tool (SWAT+ Toolbox, SWAT-CUP, a script) picks a set of parameter changes, writes them to [`calibration.cal`](../calibration/parameter-change-files.md), runs SWAT+, compares the output with the observations, and repeats. Each run of SWAT+ applies the changes in [`calibration.cal`](../calibration/parameter-change-files.md) once, at start-up, and then simulates the full period with the changed parameters.

The input files are never edited. A change exists only for the run that reads it, so the same `TxtInOut` folder can be reused for every trial.

## Files

Two files, both named on the `chg` line of [`file.cio`](../input-reference/file-cio.md), drive hard calibration:

- [`cal_parms.cal`](../calibration/parameter-change-files.md) lists every parameter that may be changed, the object type it belongs to, and the lowest and highest value it may take. SWAT+ Editor writes this file and it rarely needs editing.
- [`calibration.cal`](../calibration/parameter-change-files.md) is the change list for one run. Each row names a parameter from [`cal_parms.cal`](../calibration/parameter-change-files.md), the type and size of the change, and optionally the objects to change and the conditions they must meet.

If either slot is `null` or the file is missing, no changes are applied. The column layouts and the full list of parameter names are on [Parameter change files](../calibration/parameter-change-files.md).

## Run sequence

1. SWAT+ reads all input files and sets up every object (HRUs, soils, plants, channels, aquifers, reservoirs).
2. It reads [`cal_parms.cal`](../calibration/parameter-change-files.md) and [`calibration.cal`](../calibration/parameter-change-files.md).
3. For each row of [`calibration.cal`](../calibration/parameter-change-files.md), in file order, it goes through the listed objects (all objects of that type when none are listed), checks the row's conditions for each object, and changes the parameter on every object that meets them.
4. The simulation runs once with the changed parameters.

Because the changes are applied after the inputs are read and before the first day is simulated, they act for the whole simulation period. The year and day columns of [`calibration.cal`](../calibration/parameter-change-files.md) only limit changes to the precipitation and temperature records (see [Climate changes](#climate-changes)).

Rows are applied in order, and a later row for the same parameter acts on the value left by the earlier row. Two `pctchg` rows of 10 for `cn2` give a 21 % increase.

## Change types

| Type | New value | Example (current value 70, change 5) |
|------|-----------|--------------------------------------|
| `absval` | the change value replaces the current value | 5 |
| `abschg` | current value + change | 75 |
| `pctchg` | current value × (1 + change / 100) | 73.5 |
| `relchg` | current value × (1 + change) | 420 |

After every change the result is limited to the range `abs_min` to `abs_max` given for that parameter in [`cal_parms.cal`](../calibration/parameter-change-files.md). Use one of the four types; any other text in the change type column gives an undefined value.

## Object types

The `obj_typ` column of [`cal_parms.cal`](../calibration/parameter-change-files.md) tells SWAT+ which objects a parameter belongs to. When a row of [`calibration.cal`](../calibration/parameter-change-files.md) lists no objects, every object of that type is changed.

| Type | Objects changed when none are listed | Example parameters |
|------|--------------------------------------|--------------------|
| `hru` | every HRU | `cn2`, `esco`, `epco`, `perco`, `lat_ttime`, `canmx` |
| `sol` | every HRU, in the soil layers from `lyr1` to `lyr2` | `awc`, `k`, `bd`, `usle_k` |
| `plt` | see [Plant parameters](#plant-parameters) | `lai_pot`, `harv_idx`, `phu_mat` |
| `hlt` | every HRU of the simplified `hru-lte` type | `cn2_lte`, `awc_lte` |
| `aqu` | every aquifer | `alpha`, `revap_co`, `flo_min` |
| `sdc` | every channel | `chn`, `chk`, `bank_exp` |
| `swq` | every channel nutrient parameter set | `rs1`, `bc1`, `mumax` |
| `res` | every reservoir | `k_res`, `evrsv`, `nsed` |
| `rdt` | every reservoir decision table | `drawdown_days`, `withdraw_rate` |
| `bsn` | the basin (applied once) | `surlag`, `cdn`, `nperco` |
| `gwf` | every gwflow cell | `aquifer_K`, `aquifer_Sy` |
| `gwf_riv` | every channel connected to gwflow | `stream_K`, `stream_thk` |
| `gwf_sgl` | applied once | `stream_bed`, `reservoir_K` |
| `cli` | see [Climate changes](#climate-changes) | `precip`, `temp` |

### Soil layers

For `sol` parameters, `lyr1` and `lyr2` in [`calibration.cal`](../calibration/parameter-change-files.md) set the first and last soil layer to change. A `lyr1` of 0 starts at the top layer, and a `lyr2` of 0 or more than the number of layers ends at the bottom layer.

### Reservoir decision tables

For `rdt` parameters (`drawdown_days`, `withdraw_rate`) the five integer columns after `conds` select which storage zones of the decision table to change. A non-zero value in the column switches that zone on:

| Column | Zone |
|--------|------|
| `lyr1` | exclusive flood control storage |
| `lyr2` | seasonal flood control storage, non-flood season |
| `year1` | seasonal flood control storage, flood season |
| `year2` | multiple use storage, non-flood season |
| `day1` | multiple use storage, second zone |

### Plant parameters

Plant parameters with object type `plt` are changed in the plant community of each listed HRU, for the plants named in the row's conditions. Only `phu_mat`, `lai_pot` and `harv_idx` are handled this way. Each row needs a condition that names the plant (see [Conditions and regionalization](../calibration/conditions-regionalization.md)); a row without one changes nothing.

Give the HRUs to change in the object list of the row. When the list is empty, SWAT+ goes through as many HRUs as there are plants in [`plants.plt`](../input-reference/plt.md), starting from HRU 1.

To change `epco` use object type `hru`. That changes the HRU value and sets the same value for every plant in the HRU's community. With object type `plt`, an `epco` row changes `lai_pot` instead.

The plant carbon parameters `bio_e`, `hvsti`, `rdmx`, `t_opt` and `t_base` are listed with object type `plt` in the SWAT+ Editor [`cal_parms.cal`](../calibration/parameter-change-files.md). In 62.0.1 rows for these parameters change nothing.

### Climate changes

Precipitation and temperature records can be changed over a date window with the parameters `precip` and `temp`, giving object type `cli` in [`cal_parms.cal`](../calibration/parameter-change-files.md). The change is applied to every daily value from day `day1` to day `day2` of each year from `year1` to `year2` (calendar years, inside the simulation period).

List the records to change in the object list of the row. With no list, nothing is changed. List one record per row. When a row lists several records, the change is applied to every listed record once for each record in the list, so a `pctchg` of 10 on three records gives a 33 % increase on each. In 62.0.1 `temp` rows do not change the listed temperature record.

## Unknown names

A row whose name is not in [`cal_parms.cal`](../calibration/parameter-change-files.md), or whose name SWAT+ does not recognise as a parameter, is skipped without a message. Check spelling against the [parameter list](../calibration/parameter-change-files.md#parameter-names) if a change seems to have no effect.

## Related pages

- [Parameter change files](../calibration/parameter-change-files.md). Column layout of [`cal_parms.cal`](../calibration/parameter-change-files.md) and [`calibration.cal`](../calibration/parameter-change-files.md), and the parameter names.
- [Conditions and regionalization](../calibration/conditions-regionalization.md). Limiting a change to objects that meet a condition.
- [Sensitivity workflow](../calibration/sensitivity-workflow.md). Driving many runs from an external sampler.
- [Soft calibration](../calibration/soft-calibration.md). Fitting the average annual water balance and crop yields before hard calibration.

??? quote "Sources"

    - Readers: [`src/cal_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_read.f90) (`cal_parms.cal`) and [`src/cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parmchg_read.f90) (`calibration.cal`), called from [`src/proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90).
    - Applying changes: [`src/cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90), which calls [`src/cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90) for each object. The change operator is [`src/chg_par.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/chg_par.f90).
    - Order of calls: [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in). `proc_cal` runs after `proc_hru`, `proc_cha`, `proc_aqu` and the reservoir and wetland setup, and before `time_control`.
    - Types: `type calibration_parameters` and `type update_parameters` in [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90).

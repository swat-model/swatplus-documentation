---
title: Soft calibration
description: Adjust SWAT+ process outputs toward regional water-balance, sediment, and plant-growth targets.
status: review
---

Soft calibration nudges model outputs toward regional targets expressed as fractions of precipitation (water balance), per-stream-order channel sediment budgets, and per-region plant yields. The targets are user-supplied and the model adjusts a small fixed set of parameters internally until each component falls inside its target window. Soft calibration is run separately from a normal simulation; it loops over the relevant land-use regions and process components, updates parameters, and re-runs the affected balance routine.

## Components

The soft codes file (`codes.sft`) is read by `calsoft_read_codes.f90` into `cal_codes` (`type soft_calibration_codes` in `calibration_data_module.f90`). Each switch enables one component of the soft calibration:

| Code | Switch | Component | Driver routine |
|------|--------|-----------|----------------|
| `hyd_hru` | `n`, `a`, `b`, `y` | HRU water balance by land use in each region. `a` calibrates all components (ET, surface runoff, lateral flow, percolation). `b` calibrates baseflow and total runoff only. | `calsoft_hyd.f90`, `calsoft_hyd_bfr.f90` |
| `hyd_hrul` | `y`/`n` | `hru_lte` water balance by land use in each region | `caltsoft_hyd.f90` |
| `plt` | `y`/`n` | Plant growth (LAI, harvest index) by region | `calsoft_plant.f90` |
| `sed` | `y`/`n` | Upland sediment yield by land use in each region | `calsoft_sed.f90` |
| `nut` | `y`/`n` | HRU nutrient balance by land use in each region | (gated in `calsoft_control.f90`) |
| `chsed` | `y`/`n` | Channel widening and bank accretion by stream order | (gated in `calsoft_control.f90`) |
| `chnut` | `y`/`n` | Channel nutrient balance by stream order | (gated in `calsoft_control.f90`) |
| `res` | `y`/`n` | Reservoir budgets by reservoir | (gated in `calsoft_control.f90`) |

If any switch is non-default the master flag `cal_soft` is set to `"y"` and `calsoft_control` is called instead of (or alongside) the normal simulation.

## HRU water balance

`calsoft_hyd.f90` is the full water-balance loop. It iterates over land-use regions, reads the regional water-balance targets (`water_balance.sft`) and the per-parameter perturbation envelope (`wb_parms.sft`), and adjusts the active parameter set until each component is within tolerance. The components and their helper routines are:

- PET, `calsoft_hyd_bfr_pet.f90`
- ET, `calsoft_hyd_bfr_et.f90`
- Surface runoff, `calsoft_hyd_bfr_surq.f90`
- Lateral flow, `calsoft_hyd_bfr_latq.f90`
- Percolation, `calsoft_hyd_bfr_perc.f90`

The shared baseflow ratio loop is `calsoft_hyd_bfr.f90`.

Adjustable parameters for the upland water balance are read into `ls_prms` (`type soft_calib_parms`). Each entry carries a parameter name, the change type (`absval`, `abschg`, or `pctchg`), and `neg`/`pos` perturbation limits with absolute floor/ceiling values.

## Channel sediment

`ch_sed_budget.sft` carries the per-stream-order sediment budget targets. `ch_sed_parms.sft` carries the perturbation envelope for channel sediment parameters, read into `ch_prms`. The channel sediment block is gated in `calsoft_control.f90` but the call to a `calsoft_chsed` driver is commented out in the current source; only the per-order accounting loop runs.

## Plant growth

`plant_parms.sft` defines the plant parameter envelope (LAI potential, harvest index) and `plant_gro.sft` carries the per-region plant target table. The driver is `calsoft_plant.f90`; `calsoft_plant_zero.f90` zeros the running statistics between iterations. After soft calibration writes the new plant parameter values, `pl_write_parms_cal` dumps a fresh `plants.plt` and a `hydrology-cal.hyd` snapshot.

## Outputs

`calsoft_control.f90` writes:

- `hydrology-cal.hyd` (unit 5001) with per-HRU hydrology parameters after the run.
- A channel sediment summary (unit 5000) when `chsed = y`.

These outputs are intended to be copied back into the model inputs to lock in the soft-calibrated values.

## Input files

| File | Read by | Purpose |
|------|---------|---------|
| `codes.sft` | `calsoft_read_codes.f90` | Component switches. |
| `wb_parms.sft` | (read in `calsoft_init`) | Upland water-balance parameter envelope. |
| `water_balance.sft` | (read in `calsoft_init`) | Regional water-balance targets (SR, LF, PC, ET, TF as fractions of precipitation). |
| `ch_sed_budget.sft` | (read in `calsoft_init`) | Channel sediment budget targets by stream order. |
| `ch_sed_parms.sft` | (read in `calsoft_init`) | Channel sediment parameter envelope. |
| `plant_parms.sft` | (read in `calsoft_init`) | Plant parameter envelope. |
| `plant_gro.sft` | (read in `calsoft_init`) | Per-region plant yield targets. |

All `*.sft` slots are declared in `input_file_module.f90`, `type input_chg`. Set the slot to `null` (or remove the file) to skip a component.

## Related pages

- [Hard calibration](../calibration/hard-calibration.md). Use after soft calibration to fit remaining parameters to observed time series.
- [Parameter change files](../calibration/parameter-change-files.md). `cal_parms.cal` defines the parameter universe and bounds shared with hard calibration.

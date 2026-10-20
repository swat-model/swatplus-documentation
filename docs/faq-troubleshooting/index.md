---
title: FAQ and troubleshooting
description: Finding the cause when a SWAT+ 62.0.1 run stops, gives implausible results or takes too long.
status: review
verified_against:
  - src/proc_bsn.f90
  - src/main.f90.in
  - src/hru_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

These pages help when a SWAT+ run stops, completes with results that do not make sense, or takes too long. First runs and installation problems are covered in [Getting started](../getting-started/index.md), and adjusting parameters to observations in [Calibration](../calibration/index.md).

## Pages

- [Common runtime errors](common-runtime-errors.md): the messages SWAT+ prints when a run stops or a name in the inputs is not matched, the names it matches without a message, files it creates when they are missing, and inputs in an older format.
- [Water balance issues](water-balance-issues.md): implausible precipitation, runoff, ET, percolation, lateral and tile flow, and basin totals that do not match the HRUs.
- [Performance tips](performance-tips.md): build type, time step, output volume and the size of the carbon output files.

## Checks after every run

1. `simulation.out` ends with `Execution successfully completed`, and `success.fin` exists. If not, the run stopped early: keep the screen output, since stop messages are not copied to the log files.
2. Read `diagnostics.out` to the end. Every line after the first is a name that was not matched, and SWAT+ used a default or left the feature off.
3. Check the names that are not reported when they do not match, above all the names in [`hru-data.hru`](../input-reference/hru.md), which fall back to the first record of each file. See [Names matched without a message](common-runtime-errors.md#names-matched-without-a-message).
4. Read `checker.out`: the soil group, rooting depth, field capacity, `perco`, `latq_co` and tile flag of each HRU show whether the intended soil and parameters were used.
5. Compare the average annual water balance with regional estimates before calibrating.

The file layouts are in [Checker and diagnostics](../output-reference/checker-diagnostics.md). The revision of the executable is in the banner at the top of `simulation.out` (`Revision 62.0.1`); inputs written for an earlier revision can be misread without a message (see [Old-format inputs](common-runtime-errors.md#old-format-inputs)).

??? quote "Sources"

    - `diagnostics.out` and `files_out.out` are opened in [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90); the banner and the completion message are written by [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in).
    - Name lookup for HRUs: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90).

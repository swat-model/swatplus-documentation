---
title: time.sim
description: Simulation period and time step.
status: review
verified_against:
  - src/time_read.f90
  - src/time_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`time.sim` sets the simulation start date, end date, and the sub-daily time step. All time-driven processes (climate reads, routing, output aggregation) use these values.

## Source

- Reader: [`src/time_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/time_read.f90)
- Type definition: [`src/time_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/time_module.f90), `type time_current`

## Format

- Line 1: title line. Skipped.
- Line 2: header line. Skipped.
- Line 3: five integer values, list-directed.

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | day_start | int | Julian day of year on which the simulation starts (1 to 366) |
| 2 | yrc_start | int | Calendar year on which the simulation starts |
| 3 | day_end | int | Julian day of year on which the simulation ends |
| 4 | yrc_end | int | Calendar year on which the simulation ends |
| 5 | step | int | Sub-daily time step code (see below) |

### Sub-daily time step values

The type definition in `time_module.f90` documents these step codes:

| Value | Meaning |
|-------|---------|
| 0 | daily |
| 1 | 12-hour increment |
| 24 | hourly |
| 96 | 15 minutes |
| 1440 | per minute |

### Defaults and derived values

The reader applies these adjustments after parsing:

- `step <= 0` is forced to `1`.
- `day_start <= 0` is forced to `1`.
- `time%nbyr` is set to `yrc_end - yrc_start + 1`.
- `time%mo`, `time%day_mo`, and `time%mo_start` are computed from `day_start` via the `xmon` helper.
- `time%yrc` is initialised to `yrc_start`.

## Example

`refdata/Ames_sub1/time.sim`:

```
time.sim:
day_start  yrc_start   day_end   yrc_end      step
       0      1975         0      2020         0
```

This runs from 1 Jan 1975 through 31 Dec 2020 (the zero values for `day_start` and `day_end` are interpreted as the first and last day of the year). The `step` value of `0` is forced to `1` by the reader.

## Related files

- [`print.prt`](../input-reference/print-prt.md). Controls which outputs are written within this simulation window.

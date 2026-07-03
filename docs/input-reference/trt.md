---
title: treatment.trt
description: Legacy treatment operation database. Not read by SWAT+.
status: review
verified_against:
  - src/main.f90
  - src/water_treatment_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`treatment.trt` is a legacy file name carried over from the SWAT2012 treatment operation table. It is written by external setup tools (QSWAT+, SWAT+ Editor) into project directories, but no SWAT+ Fortran reader consumes it. The file plays no part in a SWAT+ run.

The current treatment functionality in SWAT+ lives in the water allocation module and uses [`water_treat.wal`](https://github.com/swat-model/swatplus/blob/main/src/water_treatment_read.f90), not `treatment.trt`. See `src/water_treatment_read.f90`.

## Source

A search of the SWAT+ Fortran tree at commit `8a1edd4a23915a2cac1cd90c788f0d521404700e` finds no `open`, `inquire`, or filename string referencing `treatment.trt` or any `.trt` extension. `file.cio` does not list it.

```bash
grep -rn "treatment.trt\|\\.trt" swatplus/src/
# no matches
```

## Format

There is no defined format. The file is not parsed.

## Example

Both reference datasets ship an empty `treatment.trt`:

```
$ wc -l refdata/Ames_sub1/treatment.trt refdata/Osu_1hru/treatment.trt
0 refdata/Ames_sub1/treatment.trt
0 refdata/Osu_1hru/treatment.trt
```

The file exists only as a placeholder.

## Related files

- [`water_treat.wal`](https://github.com/swat-model/swatplus/blob/main/src/water_treatment_read.f90). The active treatment input, read by `water_treatment_read`. Defines water treatment objects with storage, lag, loss fraction, and constituent links used by water allocation.

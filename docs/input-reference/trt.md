---
title: treatment.trt
description: Placeholder file left by project setup tools. SWAT+ does not read it.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/water_treatment_read.f90
  - src/om_treat_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`treatment.trt` is a file name kept from the SWAT2012 treatment table. Project setup tools can still write it into a project folder, but SWAT+ 62.0.1 does not open it, and [`file.cio`](file-cio.md) has no slot for it. Its contents have no effect on a run, and the file can be left empty or deleted.

Water treatment in SWAT+ is part of [water allocation](water-allocation.md). Treatment plants are defined in [`water_treat.wal`](../input-reference/water-allocation.md#water_treatwal), and the composition of treated water in `om_treat.wal`.

## Format

None. The file is not read.

## Example

Both reference datasets in the SWAT+ repository, `refdata/Ames_sub1` and `refdata/Osu_1hru`, contain an empty `treatment.trt`.

## Related files

- [Water allocation](water-allocation.md): [`water_treat.wal`](../input-reference/water-allocation.md#water_treatwal) and `om_treat.wal`, the treatment inputs SWAT+ reads.
- [`file.cio`](file-cio.md): lists the input files SWAT+ reads.

??? quote "Sources"

    - File name slots read from `file.cio`: [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Treatment inputs: [`water_treatment_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_treatment_read.f90) (`water_treat.wal`), [`om_treat_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_treat_read.f90) (`om_treat.wal`)

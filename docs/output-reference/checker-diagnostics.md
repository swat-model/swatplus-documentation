---
title: Checker and diagnostics
description: The always-on diagnostic files. checker.out, diagnostics.out, simulation.out, files_out.out, success.fin, erosion.out.
status: review
verified_against:
  - src/main.f90
  - src/proc_bsn.f90
  - src/proc_hru.f90
  - src/proc_date_time.f90
  - src/time_control.f90
  - src/hydrograph_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

These files are written every run, regardless of `print.prt`. Check them first when validating a simulation.

## simulation.out

### Source

Opened in [`src/main.f90`](https://github.com/swat-model/swatplus/blob/main/src/main.f90) on unit 9003 (first 30 lines). Daily progress lines written from [`src/time_control.f90`](https://github.com/swat-model/swatplus/blob/main/src/time_control.f90). Climate-file open events written from [`src/proc_date_time.f90`](https://github.com/swat-model/swatplus/blob/main/src/proc_date_time.f90).

### Content

- Banner: SWAT+ version, revision, compiler, OS, build date.
- One line per climate file as it is opened.
- One line per simulated day:
  ```
  <scenario name>  <mon>  <day>  <year>  Yr  <yr>  of  <yr_total>  Time  hh:mm:ss
  ```
- On successful completion, a line `Execution successfully completed` and a `Date of Sim` stamp.

### Example

```
                   SWAT+
             Revision 61.0.1-33-g68b1328
      Soil & Water Assessment Tool
IntelLLVM (2024.0.0), 2024-08-27 08:49:23, Linux
    Program reading . . . executing


  Date of Sim   8/27/2024 Time   8:49:51
 reading from pet file                   Time   8:49:51
 reading from precipitation file         Time   8:49:51
 ...
  Original Simulation        1   1  1975 Yr    1 of   46 Time   8:49:51
  ...
  Original Simulation       12  31  2020 Yr   46 of   46 Time   8:49:53

 Execution successfully completed

  Date of Sim   8/27/2024 Time   8:49:53
```

If `Execution successfully completed` is absent, the run aborted. Search upward in the file for the last day printed: the failure is on the next simulated day.

## diagnostics.out

### Source

Opened in [`src/proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/main/src/proc_bsn.f90) on unit 9001. Lines are appended by every `*_read.f90` that detects a missing input reference (`grep -rn "write *(9001"` lists about 60 call sites in the source).

### Content

One warning per line. Each warning is the name of a missing reference and the input file that pointed to it. Example:

```
 DIAGNOSTICS.OUT FILE
 corn_lum                                CORN_rot                                 not found in management.sch
 agrr_lum                                AGRR_rot                                 not found in management.sch
 soyb_lum                                SOYB_rot                                 not found in management.sch
 ames.tem                                          file not found (tgage)
 file not found (basins_carbon.tes)
```

Read this file end-to-end after every run. Lines here mean SWAT+ silently substituted a default or skipped a setting because the referenced object was not in the database it was supposed to be in. Common categories:

- `<name> not found in management.sch`. A land use management points at a schedule that does not exist.
- `<name> not found (initial.cha)`, `(hydrology.cha)`, `(sediment.cha)`, `(nutrients.cha)`. A channel object points to a property set that does not exist.
- `file not found (<gage>)`. A weather station refers to a gage file that is missing.
- `file not found (<file>)`. A control input (carbon coefficients, snow database) is missing.

An empty `diagnostics.out` (only the header) means no missing references were detected.

## checker.out

### Source

Opened in [`src/proc_hru.f90`](https://github.com/swat-model/swatplus/blob/main/src/proc_hru.f90) on unit 4000. Writes one row per HRU after model setup. Header types are `output_checker_header` and `output_checker_unit` in [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90).

### Format

- Line 1: scenario name and SWAT+ version.
- Line 2: column header (`chk_hdr`).
- Line 3: unit row (`chk_unit`). The last cell carries the legend `0=notile;1=tile;`.
- Lines 4+: one row per HRU.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | sname | name | soil name |
| 2 | hydgrp | A/B/C/D | hydrologic soil group |
| 3 | zmx | mm | maximum rooting depth (`soil%zmx`) |
| 4 | usle_k | none | USLE soil erodibility factor |
| 5 | sumfc | mm | sum of field capacity over profile |
| 6 | sumul | mm | sum of saturation (upper limit) over profile |
| 7 | usle_p | none | USLE practice factor |
| 8 | usle_ls | none | USLE slope-length-steepness factor |
| 9 | esco | none | soil evaporation compensation factor |
| 10 | epco | none | plant uptake compensation factor |
| 11 | cn3_swf | none | curve-number soil-water adjustment |
| 12 | perco | none | percolation coefficient |
| 13 | latq_co | none | lateral flow coefficient |
| 14 | tiledrain | 0 or 1 | tile drainage flag |

### Example

`refdata/Ames_sub1/checker.out`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
                                        zmx       usle_k       sumfc       sumul      usle_p     usle_ls        esco        epco     cn3_swf       perco     latq_co   tiledrain
 sname           hydgrp                 (mm)                    (mm)        (mm)                                                                                     0=notile;1=tile;
soil_01         B                  2000.0000      0.0000    361.5000    616.1781      1.0000      0.3638      0.9500      1.0000      0.0000      0.5000      0.0100           0
soil_02         B                  2000.0000      0.0000    361.5000    445.6733      1.0000      0.3638      0.9500      1.0000      0.0000      0.5000      0.0100           0
```

Check `usle_k`, `zmx`, `sumfc`, and `sumul` for unrealistic values (zero, negative, or extreme). A `zmx` of 2000 mm on every HRU usually means the soil definitions were not parsed and the model fell back to a default.

## files_out.out

### Source

Opened in [`src/proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/main/src/proc_bsn.f90) on unit 9000. Every `open_output_file` call that opens an output writes one line here, naming the file and a short tag.

### Format

- Line 1: header `files_out.out - OUTPUT FILES WRITTEN`.
- Lines 2+: two columns, tab/space separated.

| Column | Description |
|--------|-------------|
| tag | `CHK`, `HRU`, `BASIN`, `CHN`, `AQU`, `RES`, `MGT`, ... |
| filename | the file SWAT+ opened |

This is the master inventory: anything actually produced by this run is listed here. If you expect a file and it is missing from `files_out.out`, the corresponding switch in `print.prt` was `n`.

## erosion.out

### Source

Opened in [`src/proc_hru.f90`](https://github.com/swat-model/swatplus/blob/main/src/proc_hru.f90) on unit 4001. Writes one row per HRU of the USLE inputs and computed factors. Always on; not switchable in `print.prt`.

## success.fin

Created in [`src/main.f90`](https://github.com/swat-model/swatplus/blob/main/src/main.f90) on unit 107. An empty file written only at the end of a successful run. External tools (calibration drivers, test harnesses) test for its existence to confirm the run completed.

## erosion.txt

Opened in `main.f90` on unit 888. Internal debug log of erosion calculations. Not part of the documented output set.

## Recommended checks after every run

1. Open `simulation.out` and confirm the last line is `Execution successfully completed`. If not, look at the last printed day.
2. Open `diagnostics.out`. Every line is a problem. Resolve each one before trusting any output.
3. Open `checker.out`. Confirm `zmx`, `sumfc`, `sumul` are sane per HRU. Confirm `tiledrain` flag matches your design.
4. Confirm `success.fin` exists.
5. Open `files_out.out`. Confirm every output file your `print.prt` requested is listed.

## Related files

- [Naming convention](../output-reference/naming-convention.md).
- [Post-processing helpers](../output-reference/post-processing.md). Includes a parser for `checker.out`.

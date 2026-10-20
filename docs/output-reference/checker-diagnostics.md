---
title: Checker and diagnostics
description: Files SWAT+ writes on every run whatever print.prt says, such as simulation.out, diagnostics.out, checker.out and files_out.out, what each one contains, and which to check after a run.
status: review
verified_against:
  - src/main.f90.in
  - src/proc_bsn.f90
  - src/proc_hru.f90
  - src/proc_date_time.f90
  - src/time_control.f90
  - src/hyd_connect.f90
  - src/hru_control.f90
  - src/hydrograph_module.f90
  - src/carbon_layers_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

SWAT+ writes the files on this page on every run; [`print.prt`](../input-reference/print-prt.md) cannot switch them off. They show whether the run finished, which inputs SWAT+ could not match, the soil and HRU settings it used, and which output files it wrote. Check them before using any other output.

| File | Content |
|------|---------|
| `simulation.out` | run log: version banner, weather files read, one line per simulated day, completion message |
| `diagnostics.out` | input problems found while reading: names not found, files missing, values rejected |
| `checker.out` | one row per HRU with soil and hydrology settings after setup |
| `files_out.out` | list of output files opened in this run |
| `success.fin` | written only at the end of a run that finished |
| `area_calc.out` | drainage areas of routed objects, as given and as calculated |
| `erosion.out` | header lines only in 62.0.1 |
| `erosion.txt` | empty in 62.0.1 |
| `paddy_test.csv` | daily paddy rice water balance; column header only unless the model has paddy wetlands |

With the gwflow module on, `gwflow_record` is also always written; see [gwflow outputs](gwflow.md).

## simulation.out

The run log. It contains, in order:

- a banner with the revision, the compiler and its version, the build date and the operating system
- the date and time of the run
- one line for each weather input read (`reading from precipitation file`, `reading from temperature file`, and so on)
- one line per simulated day, giving the simulation name, month, day, year, the year number and the number of years, and the clock time
- at the end, `Execution successfully completed` and the date and time again

Each daily line starts with `Original Simulation` in a normal run. During soft calibration other names appear in that place.

```
                   SWAT+
             Revision 62.0.1
      Soil & Water Assessment Tool
IntelLLVM (2025.0.4), 2026-10-05 00:10:27, Linux
    Program reading . . . executing


 Date of Sim  10/20/2026 Time  12: 9:24
 reading from wgn file                                       Time  12: 9:24
 reading from wx station file                                Time  12: 9:24
 reading from precipitation file                             Time  12: 9:24
 reading from temperature file                               Time  12: 9:24
  ...
  Original Simulation            1   1  1975 Yr    1 of    2 Time  12: 9:24
  ...
  Original Simulation           12  31  1976 Yr    2 of    2 Time  12: 9:35

 Execution successfully completed

  Date of Sim  10/20/2026 Time  12: 9:35
```

If the completion message is missing, the run stopped early. The last daily line shows the last day that finished, so the problem occurred on the next day. Messages printed to the screen when the run stopped are not copied to this file.

## diagnostics.out

Line 1 is `DIAGNOSTICS.OUT FILE`. Every later line reports a problem found while reading the inputs. About 60 places in the code write to this file. Most lines say that a name given in one file was not found in the file it points to; SWAT+ then uses a default or skips the setting and continues.

Common messages:

| Message | Meaning |
|---------|---------|
| `<land use> <schedule> not found in management.sch` | a row of [`landuse.lum`](../input-reference/lum.md) names a management schedule that is not in [`management.sch`](../input-reference/management.md#managementsch) |
| `<name> not found (snow.sno)`, `(soils.sol)`, `(topography.hyd)`, and similar | an HRU or object points to a record that does not exist; the default record is used |
| `<file> file not found (tgage)`, `(pgage)`, and similar | a weather station names a climate file that is missing |
| `... could not be opened` | an input file listed in [`file.cio`](../input-reference/file-cio.md) could not be opened |
| `... is required when carbon is enabled (codes.bsn carbon = 2)` | a carbon input file is missing while the dynamic carbon model is on |
| `carbon_layers.prt: n_layers must be >= 1 ...` | the optional [layer count file](carbon.md#layer-count-file) has an invalid value |

Example from a run of the `Ames_sub1` reference dataset with 62.0.1:

```
 DIAGNOSTICS.OUT FILE
 agrr_lum                                AGRR_rot                                 not found in management.sch
 soyb_lum                                SOYB_rot                                 not found in management.sch
 oats_lum                                OATS_rot                                 not found in management.sch
 wwht_lum                                WWHT_rot                                 not found in management.sch
 ames.tem                                          file not found (tgage)
```

A file with only the first line means no problems were found. Read the whole file after each run and decide for each line whether the default SWAT+ used is acceptable.

## checker.out

One row per HRU, in HRU order, written after the HRUs are set up. Line 1 is the project name and version, line 2 the column header and line 3 the units; the last unit entry, `0=notile;1=tile;`, explains the `tiledrain` column.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `sname` | - | soil name used by the HRU (no header label; the name is in the units line) |
| 2 | `hydgrp` | - | hydrologic soil group, A to D (no header label) |
| 3 | `zmx` | mm | maximum rooting depth of the soil |
| 4 | `usle_k` | - | USLE soil erodibility factor |
| 5 | `sumfc` | mm | water held at field capacity, whole profile |
| 6 | `sumul` | mm | water held at saturation, whole profile |
| 7 | `usle_p` | - | USLE support practice factor |
| 8 | `usle_ls` | - | USLE slope length and steepness factor |
| 9 | `esco` | - | soil evaporation compensation factor |
| 10 | `epco` | - | plant uptake compensation factor |
| 11 | `cn3_swf` | - | soil water factor for curve number condition III |
| 12 | `perco` | - | percolation coefficient |
| 13 | `latq_co` | - | lateral flow coefficient |
| 14 | `tiledrain` | 0 or 1 | 1 if the HRU has tile drainage |

The file has no HRU number or name column. Row K belongs to HRU K in [`hru-data.hru`](../input-reference/hru.md).

Example from a run of `Ames_sub1` with 62.0.1:

```
 demo                      SWAT+ 2026-10-05        MODULAR Rev 2026.62.0.1
                                        zmx       usle_k       sumfc       sumul      usle_p     usle_ls        esco        epco     cn3_swf       perco     latq_co   tiledrain
 sname           hydgrp                 (mm)                    (mm)        (mm)                                                                                     0=notile;1=tile;
soil_01-h1      B                  2000.0000      0.0000    361.5003    616.0899      1.0000      0.3638      0.9500      1.0000      0.0000      0.5000      0.0100           0
soil_02         B                  2000.0000      0.0000    361.5004    449.0375      0.7500      0.3638      0.9500      1.0000      0.0000      0.5000      0.0100           0
```

Look for zero, negative or extreme values: here `usle_k` is zero for both soils, so these HRUs produce no USLE erosion. Check whether that is intended.

## files_out.out

Line 1 is `files_out.out - OUTPUT FILES WRITTEN`. Each later line names one output file opened in the run, after a tag for its type, such as `CHK`, `HRU`, `LSU`, `BASIN`, `BASIN_AQUIFER`, `BASIN_CROP_YLD`, `CROP`, `RES` or `DTBL`. `.csv` copies are listed separately.

```
 files_out.out - OUTPUT FILES WRITTEN
 CHK                       checker.out
 HRU                       hru_carb_gl_mon.txt
 HRU                       hru_carb_gl_mon.csv
```

Use it to confirm that every file you asked for in [`print.prt`](../input-reference/print-prt.md) was opened. A file missing from the list was not switched on, or its object type is not in the model (for example, reservoir files in a model without reservoirs). Some files are not listed even when they are written, including the gwflow files and `reservoir_mon.csv`.

## success.fin

Written at the end of a run that finished. It contains a blank line and `Execution successfully completed`. Calibration tools and scripts test for this file to tell whether a run finished. Delete it before starting a run if you rely on it, because SWAT+ does not remove an old copy at the start.

## area_calc.out

Drainage areas of every routed object except HRUs and routing units: the object number, type and number within its type, the drainage area given in the connection file and the area SWAT+ calculated from the routing, followed by the same areas for each incoming object. Use it to check that the routing delivers the expected area to each channel and outlet. The file is empty when the model has only HRUs and routing units.

## Other files

`erosion.out` contains three header lines and no data in 62.0.1. `erosion.txt` is opened at the start of each run and left empty.

`paddy_test.csv` is a temporary paddy rice output. It has a header line, and one line per day for each HRU that has a paddy wetland with water: date, HRU, precipitation, irrigation, seepage, PET, soil evaporation, plant transpiration, weir height, water depth, weir outflow, soil water, sediment concentration and yield, nitrate concentration and yield, LAI, salt concentration and soil water as a percentage of field capacity.

## Checks after a run

1. `simulation.out` ends with `Execution successfully completed`, and `success.fin` exists.
2. `diagnostics.out` has only its first line, or every remaining line is understood and accepted.
3. `checker.out` has plausible values for every HRU, and `tiledrain` matches the design.
4. `files_out.out` lists every file requested in [`print.prt`](../input-reference/print-prt.md).

## Related files

- [Naming convention](naming-convention.md): file names and suffixes.
- [Post-processing helpers](post-processing.md): includes a parser for `checker.out`.
- [`print.prt`](../input-reference/print-prt.md): switches for the other output files.

??? quote "Sources"

    - `simulation.out`, `success.fin`, `erosion.txt`, `paddy_test.csv`: [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) (units 9003, 107, 888, 100100); weather lines in [`proc_date_time.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_date_time.f90); daily lines in [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90); paddy rows in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - `files_out.out`, `diagnostics.out`, `area_calc.out`: opened in [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90) (units 9000, 9001, 9004); `area_calc.out` rows in [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - `checker.out`, `erosion.out`: [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90) (units 4000, 4001); header types `output_checker_header` and `output_checker_unit` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)

    | `checker.out` column | Fortran variable |
    |----------------------|------------------|
    | `sname`, `hydgrp`, `zmx`, `usle_k`, `sumfc`, `sumul` | `soil(j)%snam`, `%hydgrp`, `%zmx`, `%usle_k`, `%sumfc`, `%sumul` |
    | `usle_p`, `usle_ls` | `hru(j)%lumv%usle_p`, `hru(j)%lumv%usle_ls` |
    | `esco`, `epco`, `cn3_swf`, `perco`, `latq_co` | `hru(j)%hyd%esco`, `%epco`, `%cn3_swf`, `%perco`, `%latq_co` |
    | `tiledrain` | `hru(j)%tiledrain` |

---
title: Release notes
status: review
verified_against:
  - swatplus/CITATION.cff
  - swatplus/CMakeLists.txt
  - swatplus/src/input_file_module.f90
  - swatplus/src/basin_module.f90
  - https://github.com/swat-model/swatplus/releases/tag/62.0.1
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ releases are listed on the [GitHub releases page](https://github.com/swat-model/swatplus/releases), with prebuilt executables and the merged pull requests of each release. Version numbers are explained in [Tagging and releases](../developer-guide/tagging-releases.md).

This page lists the changes in each release that affect model users: input files, outputs and results. Each version of this documentation describes one release; use the version selector at the top of the page for earlier ones.

## 62.0.1

Released 19 October 2026.

### Input files

- [`file.cio`](../input-reference/file-cio.md), `water_rights` line: now names two files, the places of use ([`place_of_use.wro`](../input-reference/water-allocation.md#place_of_usewro)) and the points of diversion ([`point_of_diver.wro`](../input-reference/water-allocation.md#point_of_diverwro)), in place of the three water rights files. The water allocation input files were reorganized around places of use, points of diversion and return; see [Water allocation](../input-reference/water-allocation.md). A [`file.cio`](../input-reference/file-cio.md) written for 62.0.0 or earlier must be updated; see [Older file.cio files](../input-reference/file-cio.md#older-filecio-files).
- [`parameters.bsn`](../input-reference/parameters-bsn.md): two columns that were unused are now read as the pesticide groundwater mixing factor and a switch for temperature-dependent pesticide decay. SWAT+ Editor still labels them `lin_sed` and `exp_sed`; a value of 1 in the second turns temperature-dependent decay on. See [parameters.bsn](../input-reference/parameters-bsn.md).
- [`pesticide.pes`](../input-reference/pes.md#pesticidepes): three new columns for plant uptake. Files in the older layout are still read, with no plant uptake. See [pesticide.pes](../input-reference/pes.md).
- Recall: the recall file named in [`file.cio`](../input-reference/file-cio.md) is read (instead of a fixed name), and empty recall files are no longer created. See [recall](../input-reference/recall.md).
- [`exco.exc`](../input-reference/recall.md) and [`exco_om.exc`](../input-reference/recall.md): the original layout is restored.
- Manure: a manure database ([`manure_db.frt`](../input-reference/frt.md#manure_dbfrt), [`manure_om.frt`](../input-reference/frt.md#manure_omfrt)) and manure allocation inputs were added. See [manure allocation](../input-reference/manure-allocation.md).
- Transplanting: transplant data are read from [`transplant.ops`](../input-reference/management.md#transplantops); `transplant.plt` is no longer read.

### Outputs

- Water allocation outputs were replaced by place-of-use based files.
- New sediment budget outputs for channels, stream orders and the basin, with corrected average annual values.
- Rice paddy output, and paddy water included in the ET reports.
- gwflow outputs now follow their [`print.prt`](../input-reference/print-prt.md) and gwflow switches, and the average annual storage change is computed correctly.
- The legacy carbon output no longer writes duplicate rows for each HRU.

See the [Output Reference](../output-reference/index.md) for the files.

### Model changes

- Rice paddies: seepage, weir spill volume and the impoundment switch day were revised, and soil evaporation is skipped while paddy water remains.
- Canopy interception is applied for all runoff methods.
- Pesticides: temperature-dependent decay, plant uptake and mass balance corrections.
- Water allocation and irrigation were reworked; the irrigation days of an unlimited source are reset correctly.

### Calibration

- `aquifer_delay` (gwflow) is changed in days.
- New object types `gwf_riv` and `gwf_sgl` for gwflow channel and single-value parameters.
- `nperco_lchtile` changes the right parameter.

See [Parameter change files](../calibration/parameter-change-files.md).

### Fixes

- A crash in tillage mixing for plant communities with more than 12 plants.
- An endless loop when all operations of a management schedule share one date.
- Root depth of perennials stuck at 25.4 mm at a cold start.
- Release executables built with gfortran no longer stop with a floating-point trap on macOS, and the macOS executable no longer needs Homebrew's gcc libraries.

## Documentation for 62.0.1

This version of the documentation was rewritten against the 62.0.1 source. Pages now describe what the model does, including inputs that are read but have no effect and behaviour that differs from the input file labels, so that results can be interpreted correctly. Examples:

- Measured PET is replaced by the Hargreaves estimate within the same day, so `pet` 3 in [`codes.bsn`](../input-reference/codes-bsn.md) gives Hargreaves results ([codes.bsn](../input-reference/codes-bsn.md)).
- Name lookups between files fall back to the first entry without a message when a name does not match; check `diagnostics.out` and the names themselves ([weather-sta.cli](../input-reference/cli.md), [hru-data.hru](../input-reference/hru.md)).
- Several basin parameters cannot be changed through [`calibration.cal`](../calibration/parameter-change-files.md) ([Parameter change files](../calibration/parameter-change-files.md#basin-parameters-bsn)).
- Manure allocation, street sweeping and the pathogen simulation have no effect, and water allocation behaves as its inputs describe only for a single place of use ([Water allocation](../input-reference/water-allocation.md)).

Each page states these points where they apply.

??? quote "Sources"

    - [SWAT+ 62.0.1 release](https://github.com/swat-model/swatplus/releases/tag/62.0.1) and `git log 62.0.0..62.0.1` in the source repository.
    - Input changes: `type input_water_allocation` in `src/input_file_module.f90` and `read (107,*) name, in_wallo` in `src/readcio_read.f90`; `pestgwfact` and `temp_decay` replacing `spcon` and `spexp` in `src/basin_module.f90`; `src/pesticide_data_module.f90`; `src/recall_read.f90` and `src/recalldb_read.f90`; `src/exco_db_read.f90` and `src/exco_read_om.f90`; `src/plant_transplant_read.f90`.
    - Outputs: `src/wallo_pou_output.f90`, `src/basin_sedbud_output.f90`, `src/ch_sedbud_output.f90`, `src/chord_sedbud_output.f90`, `src/gwflow_output.f90`.
    - Build: `CMakeLists.txt` (gfortran flags and macOS linking).

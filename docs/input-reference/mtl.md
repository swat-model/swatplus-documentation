---
title: heavy metals module
description: Per-HRU and aquifer initial heavy metal concentrations.
status: review
verified_against:
  - src/hmet_hru_aqu_read.f90
  - src/constituent_mass_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The heavy metals module simulates user-listed metals across HRU soils and plants. The set of metals simulated is declared in [`constituents.cs`](cs.md), which populates `cs_db%num_metals`. Only initial soil and plant concentrations are loaded by a dedicated reader; no separate metal parameter database is read by `hmet_hru_aqu_read`.

## Activation

`in_parmdb%hmetcom_db` is defined in [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90) with default `metals.mtl`. No reader in `src/` opens this filename, so the parameter database is declared in `file.cio` but not loaded.

The initial-conditions file is referenced from `file.cio` via `in_init%hmet_soil` (default `hmet_hru.ini`). `hmet_hru_aqu_read` is called from `proc_read.f90`.

## Files

### hmet_hru.ini

Initial metal concentrations for HRU soils and plants.

- Reader: [`src/hmet_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/hmet_hru_aqu_read.f90)
- Type: `hmet_soil_ini` (`type cs_soil_init_concentrations`) in [`src/constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/constituent_mass_module.f90). Fields: `name`, `soil(num_metals)` (ppm), `plt(num_metals)` (ppm).
- Format: one title line, then per record: a header line, a name line, then `num_metals` pairs of lines (`metal_name, soil_value` then `metal_name, plt_value`) in `constituents.cs` order.

The same reader allocates `cs_hmet_solsor(num_metals)`.

### metals.mtl

Declared as `in_parmdb%hmetcom_db` in `input_file_module.f90` (default name `metals.mtl`). No reader in the current source opens this file. The file is reserved but inert.

## Related

- [`constituents.cs`](cs.md). Declares the metal list and sets `cs_db%num_metals`. The metals block in `constit_db_read` is read but its name-database cross-walk is commented out, so listed metals only contribute the count.
- [`pesticide module`](pes.md). Same per-object initial-condition pattern.
- [`pathogen module`](pth.md). Same per-object initial-condition pattern.

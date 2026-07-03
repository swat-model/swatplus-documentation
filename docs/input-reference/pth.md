---
title: pathogen module
description: Pathogen parameter database and per-object initial conditions.
status: review
verified_against:
  - src/path_parm_read.f90
  - src/path_cha_res_read.f90
  - src/path_hru_aqu_read.f90
  - src/pathogen_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The pathogen module simulates user-listed pathogens across soil, foliage, channel water, benthic sediment, and aquifers. The set of pathogens simulated is declared in [`constituents.cs`](cs.md), which populates `cs_db%num_paths`. The files below load the parameter database and the per-object initial conditions.

## Activation

The pathogen database `pathogens.pth` is referenced from `file.cio` as `in_parmdb%pathcom_db` (default `pathogens.pth`). The initial-condition files are referenced via `in_init%path_soil` (default `path_hru.ini`) and `in_init%path_water` (default `path_water.ini`).

`path_parm_read` is called from `proc_db.f90`. `path_hru_aqu_read` is called from `proc_read.f90`. `path_cha_res_read` is called later from `main.f90`.

## Files

### pathogens.pth

Pathogen parameter database. One row per pathogen.

- Reader: [`src/path_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/path_parm_read.f90)
- Type: `path_db(0:path)` (`type pathogen_db`) in [`src/pathogen_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/pathogen_data_module.f90).
- Format: title line, header line, then one line per pathogen.

| # | Field | Units | Description |
|---|-------|-------|-------------|
| 1 | pathnm | - | pathogen name |
| 2 | do_soln | 1/day | die-off factor in soil solution |
| 3 | gr_soln | 1/day | growth factor in soil solution |
| 4 | do_sorb | 1/day | die-off factor sorbed to soil particles |
| 5 | gr_sorb | 1/day | growth factor sorbed to soil particles |
| 6 | kd | none | partition coefficient between solution and sorbed phase in surface runoff |
| 7 | t_adj | none | temperature adjustment factor for die-off and growth |
| 8 | washoff | none | fraction on foliage washed off by a rainfall event |
| 9 | do_plnt | 1/day | die-off factor on foliage |
| 10 | gr_plnt | 1/day | growth factor on foliage |
| 11 | fr_manure | none | fraction of manure with active colony forming units |
| 12 | perco | none | percolation coefficient, ratio of solution bacteria in the surface layer |
| 13 | det_thrshd | cfu/m^2 | detection threshold below which soil pathogen levels are zeroed |
| 14 | do_stream | 1/day | die-off factor in streams |
| 15 | gr_stream | 1/day | growth factor in streams |
| 16 | do_res | 1/day | die-off factor in reservoirs |
| 17 | gr_res | 1/day | growth factor in reservoirs |
| 18 | conc_min | - | minimum pathogen concentration |

### path_hru.ini

Initial pathogen concentrations for HRU soils and plants. One block per record.

- Reader: [`src/path_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/path_hru_aqu_read.f90)
- Type: `path_soil_ini` (`type cs_soil_init_concentrations`) in [`src/constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/constituent_mass_module.f90). Fields: `name`, `soil(num_paths)`, `plt(num_paths)` in cfu/m^2.
- Format: one title line, then per record: a header line, a name line, then one line containing `name, soil(:), plt(:)` for all pathogens in `constituents.cs` order.

The same reader allocates `cs_path_solsor(num_paths)`.

### path_water.ini

Initial pathogen concentrations for channels and reservoirs (water column and benthic).

- Reader: [`src/path_cha_res_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/path_cha_res_read.f90)
- Type: `path_water_ini` (`type cs_water_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `water(num_paths)`, `benthic(num_paths)`. Record names are stored in `path_init_name`.
- Format: title line, header line, then per record: name line, then `num_paths` pairs of lines (water value, benthic value). On the second pass the reader reads a single line `name, water(:), benthic(:)` per record.

## Related

- [`constituents.cs`](cs.md). Declares the pathogen list and sets `cs_db%num_paths`.
- [`pesticide module`](pes.md). Same per-object initial-condition pattern.
- [`metals module`](mtl.md). Same per-object initial-condition pattern.

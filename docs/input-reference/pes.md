---
title: pesticide module
description: Pesticide parameter database, initial conditions, and metabolite chain.
status: review
verified_against:
  - src/pest_parm_read.f90
  - src/pest_cha_res_read.f90
  - src/pest_hru_aqu_read.f90
  - src/pest_metabolite_read.f90
  - src/pesticide_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The pesticide module simulates user-listed pesticides across foliage, soil, channel water, benthic sediment, and aquifers. The set of pesticides simulated is declared in [`constituents.cs`](cs.md), which populates `cs_db%num_pests`. The files below load the parameter database, the per-object initial conditions, and the parent-daughter metabolite chain.

## Activation

The pesticide parameter database `pesticide.pes` is referenced from `file.cio` as `in_parmdb%pest` (default `pesticide.pes`). The initial-condition files are referenced from `file.cio` via `in_init%pest_soil` (default `pest_hru.ini`) and `in_init%pest_water` (default `pest_water.ini`).

`pest_parm_read` is called from `proc_db.f90`. `pest_metabolite_read` and `pest_hru_aqu_read` are called from `proc_read.f90`. `pest_cha_res_read` is called later from `main.f90`.

## Files

### pesticide.pes

Pesticide parameter database. One row per pesticide.

- Reader: [`src/pest_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/pest_parm_read.f90)
- Type: `pestdb(0:pestparm)` (`type pesticide_db`) in [`src/pesticide_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/pesticide_data_module.f90). The reader also fills `pestcp(ip)%decay_f`, `decay_s`, `decay_a`, `decay_b` from the half-life columns as `exp(-0.693 / hlife)`.
- Format: title line, header line, then one line per pesticide.

| # | Field | Units | Description |
|---|-------|-------|-------------|
| 1 | name | - | pesticide name |
| 2 | koc | mL/g | soil adsorption coefficient normalized for soil organic carbon |
| 3 | washoff | none | fraction of pesticide on foliage washed off by a rainfall event |
| 4 | foliar_hlife | days | half-life on foliage |
| 5 | soil_hlife | days | half-life in soil |
| 6 | solub | mg/L | solubility in water |
| 7 | aq_hlife | days | aquatic half-life |
| 8 | aq_volat | m/day | aquatic volatilization coefficient |
| 9 | mol_wt | g/mol | molecular weight, used for mixing velocity |
| 10 | aq_resus | m/day | aquatic resuspension velocity for sorbed pesticide |
| 11 | aq_settle | m/day | aquatic settling velocity for sorbed pesticide |
| 12 | ben_act_dep | m | depth of the active benthic layer |
| 13 | ben_bury | m/day | burial velocity in benthic sediment |
| 14 | ben_hlife | days | half-life in benthic sediment |
| 15 | pl_uptake | none | fraction taken up by plant |
| 16 | descrip | - | description string |

### pest_hru.ini

Initial pesticide concentrations for HRU soils and plants. One block per record.

- Reader: [`src/pest_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/pest_hru_aqu_read.f90)
- Type: `pest_soil_ini` (`type cs_soil_init_concentrations`) in [`src/constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/constituent_mass_module.f90). Fields: `name`, `soil(num_pests)` (ppm), `plt(num_pests)` (ppm).
- Format: one title line, then per record: a header line, a name line, then `num_pests` lines each containing `pest_name, soil_value, plt_value` in the order declared in `constituents.cs`.

The same reader populates `cs_pest_solsor(num_pests)` (allocated only).

### pest_water.ini

Initial pesticide concentrations for channels and reservoirs (water column and benthic).

- Reader: [`src/pest_cha_res_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/pest_cha_res_read.f90)
- Type: `pest_water_ini` (`type cs_water_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `water(num_pests)`, `benthic(num_pests)`. Record names are stored in `pest_init_name`.
- Format: title line, header line, then per record: name line, then `num_pests` pairs of lines (water value, benthic value). The values are then read again on the second pass as a single record line of `name, water(:), benthic(:)`.

### pest_metabolite.pes

Parent-daughter metabolite chain. Filename is hard-coded in the reader (not driven by `file.cio`).

- Reader: [`src/pest_metabolite_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/pest_metabolite_read.f90)
- Target: `pestcp(ip)%daughter(num_metab)` (`type daughter_decay_fractions`) and `pestcp(ip)%num_metab` in `src/pesticide_data_module.f90`. The daughter `%num` field is set by cross-walk against `cs_db%pests` so the metabolite must also appear in `constituents.cs`.
- Format: title line, header line, then per parent: one line `parent_name num_metab`, followed by `num_metab` lines of `daughter_name, foliar_fr, soil_fr, aq_fr, ben_fr`. The parent name must match an entry in `pesticide.pes`.

| Field | Units | Description |
|-------|-------|-------------|
| name | - | daughter pesticide name |
| foliar_fr | 0-1 | fraction of parent on foliage that degrades to this daughter |
| soil_fr | 0-1 | fraction of parent in soil that degrades to this daughter |
| aq_fr | 0-1 | fraction of parent in aquatic phase that degrades to this daughter |
| ben_fr | 0-1 | fraction of parent in benthic phase that degrades to this daughter |

## Related

- [`constituents.cs`](cs.md). Declares the pesticide list and sets `cs_db%num_pests`.
- [`pathogen module`](pth.md). Same per-object initial-condition pattern.
- [`metals module`](mtl.md). Same per-object initial-condition pattern.

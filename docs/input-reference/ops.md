---
title: "*.ops (operation databases)"
description: Per-operation parameter databases for harvest, grazing, irrigation, chemical application, fire, and street sweeping.
status: review
verified_against:
  - src/mgt_read_harvops.f90
  - src/mgt_read_grazeops.f90
  - src/mgt_read_irrops.f90
  - src/mgt_read_chemapp.f90
  - src/mgt_read_fireops.f90
  - src/mgt_read_sweepops.f90
  - src/mgt_operations_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The six `.ops` files declared in `type input_ops` are parameter databases for the management operations that `management.sch` and the `lum.dtl` decision tables can invoke. Each file is a named list of parameter sets that other files reference by `name`.

All six readers follow the same structure: skip two header lines, count records, allocate, rewind, skip two, read one record per row into the corresponding `*_db` array.

## Source

- Readers: `src/mgt_read_harvops.f90`, `src/mgt_read_grazeops.f90`, `src/mgt_read_irrops.f90`, `src/mgt_read_chemapp.f90`, `src/mgt_read_fireops.f90`, `src/mgt_read_sweepops.f90`.
- Type definitions: `src/mgt_operations_module.f90`.

## File format

For every file:

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3 and following: one record per operation. List-directed read. The reader counts records on a first pass, allocates the database array, rewinds, and reads the values.

The "Common" first column is the operation name; other files reference it.

## harv.ops

Reader: `mgt_read_harvops.f90` → `harvop_db` (`type harvest_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | typ | char(40) | "" | none | `grain`, `biomass`, `residue`, `tree`, or `tuber` |
| 3 | hi_ovr | real | 0 | none | harvest index override at harvest |
| 4 | eff | real | 0 | fraction | harvest efficiency. Fraction of harvested yield removed; the remainder is left as residue |
| 5 | bm_min | real | 0 | kg/ha | minimum biomass required to allow harvest |

## graze.ops

Reader: `mgt_read_grazeops.f90` → `grazeop_db` (`type grazing_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | fertnm | char(40) | "" | none | manure name pointing into `fertilizer.frt` |
| 3 | manure_id | int | 0 | none | resolved id of `fertnm` in `fertilizer.frt` |
| 4 | eat | real | 0 | (kg/ha)/day | dry biomass removed by grazing per day |
| 5 | tramp | real | 0 | (kg/ha)/day | dry biomass removed by trampling per day |
| 6 | manure | real | 0 | (kg/ha)/day | dry manure deposited per day |
| 7 | biomin | real | 0 | kg/ha | minimum plant biomass to allow grazing |

## irr.ops

Reader: `mgt_read_irrops.f90` → `irrop_db` (`type irrigation_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | amt_mm | real | 25.4 | mm | application amount |
| 3 | eff | real | 0 | none | in-field application efficiency |
| 4 | surq | real | 0 | fraction | surface runoff ratio |
| 5 | dep_mm | real | 0 | mm | depth of application for subsurface irrigation |
| 6 | salt | real | 0 | mg/kg | total salt concentration in irrigation water |
| 7 | no3 | real | 0 | mg/kg | nitrate concentration |
| 8 | po4 | real | 0 | mg/kg | phosphate concentration |

## chem_app.ops

Reader: `mgt_read_chemapp.f90` → `chemapp_db` (`type chemical_application_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | form | char(40) | "" | none | `solid` or `liquid` |
| 3 | op_typ | char(40) | "" | none | `spread`, `spray`, `inject`, or `direct` |
| 4 | app_eff | real | 0 | none | application efficiency |
| 5 | foliar_eff | real | 0 | none | foliar efficiency |
| 6 | inject_dep | real | 0 | mm | injection depth |
| 7 | surf_frac | real | 0 | fraction | fraction in upper 10 mm of soil |
| 8 | drift_pot | real | 0 | none | drift potential |
| 9 | aerial_unif | real | 0 | none | aerial uniformity |

## fire.ops

Reader: `mgt_read_fireops.f90` → `fire_db` (`type fire_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | cn2_upd | real | 0 | none | change applied to SCS curve number II value |
| 3 | fr_burn | real | 0 | fraction | fraction of cover burned |

## sweep.ops

Reader: `mgt_read_sweepops.f90` → `sweepop_db` (`type streetsweep_operation`).

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | "" | none | operation name |
| 2 | eff | real | 0 | none | removal efficiency of the sweeping operation |
| 3 | fr_curb | real | 0 | none | availability factor: fraction of curb length that is sweepable |

## Example

`refdata/Ames_sub1/harv.ops`:

```
harv.ops written by SWAT+ editor v2.3.3 on 2023-10-25
name                  typ                hi_ovr        eff        bm_min
harv_grain            grain              0.0           1.0        0.0
harv_residue          residue            0.0           1.0        0.0
```

The other five files follow the same shape with their own column sets.

## Related files

- [`landuse.lum`](../input-reference/lum.md) and `management.sch` reference operations by `name`.
- [`*.dtl`](../input-reference/dtl.md) decision tables can fire operations by `name`.
- [`fertilizer.frt`](../input-reference/frt.md) provides the `manure_id` resolution target for `graze.ops`.

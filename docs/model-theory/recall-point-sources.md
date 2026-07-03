---
title: Recall and point sources
description: Recall time series, export coefficient objects, and delivery ratio objects in SWAT+.
status: review
---

## Overview

Three related object types let SWAT+ inject water and constituent loads into the routing network from outside the simulated land surface: recall objects, export coefficient objects, and delivery ratio objects.

- **Recall** objects deliver a time series of flow and mass (NO3, NH3, organic N, mineral P, organic P, sediment, pesticides, salts, constituents) read from `recall.rec` and supporting per-object data files. They are the standard point source representation, including municipal and industrial discharges, atmospheric deposition points, or measured imports.
- **Export coefficient** objects deliver an average annual flow and mass per unit area, computed once and applied each day. They are useful where only annual loading rates are known.
- **Delivery ratio** objects scale incoming loads on a routing unit basis (delivery from HRUs to channels), either calculated from time of concentration or set to a fixed fraction.

All three share a common reader infrastructure under `recall_module.f90` because internally they are all stored as recall databases.

## Process equations

### Recall objects

The recall reader (`recall_read.f90`) opens the file pointed to in `recall.rec` for each recall object and selects an allocation pattern based on the time step token:

| `tstep` | Storage shape | Meaning |
|---------|---------------|---------|
| `sub` | `hyd_flo(step*366, nbyr)` plus `hd(366, nbyr)` | Sub-daily values per simulation year |
| `day` | `hd(366, nbyr)` | One record per day |
| `mo` | `hd(12, nbyr)` | One record per month |
| `yr` | `hd(1, nbyr)` | One record per year |

At runtime the recall driver looks up the current day, month, or year and copies the stored hydrograph (`recall(irec)%hd(...)`) into the object's outgoing hydrograph. For sub-daily, flow is stored as `m^3/s` and converted to volume per step (`flo * 86400 / time%step`).

Recall objects can be linked to channel objects so the volume is added to the channel inflow, or to other receiving objects through the connectivity file `recall.con`.

Negative-flow recall objects represent diversions: `recall_nut.f90` and `recall_salt.f90` remove constituent mass from the source channel in proportion to the diverted volume and the source-water concentration.

### Export coefficient objects

Export coefficient objects (`exco_module.f90`) are stored in the same recall database type with one record per object that holds average annual flow and constituent loads. The reader chain (`exco_db_read.f90`, `exco_read_om.f90`, `exco_read_pest.f90`, `exco_read_path.f90`, `exco_read_hmet.f90`, `exco_read_salt.f90`) populates separate organic-mineral, pesticide, pathogen, heavy metal, and salt files keyed by `exco_*_name`. Each day the export coefficient flow is divided by 365.25 (TODO: verify exact daily fraction) and added to the receiving object.

### Delivery ratio objects

Delivery ratios scale incoming loads from a routing-unit element by a fraction between 0 and 1. The element database `dr_db` in `dr_module.f90` lists the organic-mineral, pesticide, pathogen, heavy metal, and salt delivery files for each delivery ratio object.

In `dr_ru.f90` each element of a routing unit gets a `dr` value built from the `dr_name` keyword:

```fortran
if (ru_elem(ielem)%dr_name == "calc" .or. "0") then
   ! compute from time of concentration
   rto = tconc(ihru) / ru_tc(iru)
   rto = min(1.0, sqrt(rto))
   ru_elem(ielem)%dr = rto + hz
   ru_elem(ielem)%dr%flo = 1.
else if (ru_elem(ielem)%dr_name == "full" .or. "1") then
   ru_elem(ielem)%dr = 1. + hz
end if
```

Three cases:

- `"calc"` or `"0"`: ratio is the square root of the HRU time of concentration over the routing unit time of concentration, capped at 1. Flow itself is delivered in full (`dr%flo = 1`).
- `"full"` or `"1"`: full delivery, ratio is 1 for everything.
- A named `dr_db` entry: ratios are read from the corresponding `_om`, `_pest`, `_path`, `_hmet`, and `_salt` files.

Delivery ratios apply only to the mass components (sediment, N, P, pesticide, salt), not to flow.

## Switches and parameters

| Parameter | File | Effect |
|-----------|------|--------|
| `recall_db%org_min%name` | `recall.rec` | Organic and mineral data file for this recall object |
| `recall_db%org_min%units` | `recall.rec` | `mass` or `conc` |
| `recall_db%org_min%tstep` | `recall.rec` | `sub`, `day`, `mo`, or `yr` |
| `recall_db%pest%name` | `recall.rec` | Pesticide data file |
| `recall_db%path%name` | `recall.rec` | Pathogen data file |
| `recall_db%hmet%name` | `recall.rec` | Heavy metal data file |
| `recall_db%salt%name` | `recall.rec` | Salt data file |
| `recall_db%constit%name` | `recall.rec` | Generic constituent data file |
| `exco_db%om_file` | `exco.exc` | Organic-mineral export coefficient file |
| `exco_db%pest_file` | `exco.exc` | Pesticide export coefficient file |
| `exco_db%salts_file` | `exco.exc` | Salt export coefficient file |
| `dr_db%om_file` | `delratio.del` | Organic-mineral delivery ratio file |
| `dr_db%pest_file` | `delratio.del` | Pesticide delivery ratio file |
| `dr_db%salts_file` | `delratio.del` | Salt delivery ratio file |
| `ru_elem%dr_name` | `rout_unit.def` | Delivery ratio choice: `calc`, `full`, or a named `dr_db` entry |

TODO: verify exact file names and column layouts against the source readers and current refdata.

## Implementation

Source modules in `swatplus/src/`:

- `recall_module.f90` defines `constituent_file_data` and `recall_databases`. The same `recall_db` type is used for recall, exco, and dr objects.
- `recall_read.f90` reads `recall_db.rec` (the database index) and dispatches per-object reads. For each recall it opens the organic-mineral file, allocates the storage for the selected time step, and stores hydrographs by day, month, or year.
- `recall_read_salt.f90` reads the salt data file.
- `recall_read_cs.f90` reads the generic constituent data file.
- `recall_nut.f90` removes nutrient mass from a source channel for negative-flow recall objects (diversions).
- `recall_salt.f90` does the same for salts.
- `recall_cs.f90` does the same for constituents.
- `recall_output.f90` writes recall object output.
- `exco_module.f90` defines `export_coefficient_datafiles` and the per-constituent name and number arrays.
- `exco_db_read.f90` reads `exco.exc`.
- `exco_read_om.f90`, `exco_read_pest.f90`, `exco_read_path.f90`, `exco_read_hmet.f90`, `exco_read_salt.f90` read the per-constituent export coefficient files.
- `dr_module.f90` defines `delivery_ratio_datafiles` and the per-constituent name and number arrays.
- `dr_db_read.f90` reads `delratio.del`.
- `dr_read_om.f90`, `dr_read_pest.f90`, `dr_path_read.f90`, `dr_read_hmet.f90`, `dr_read_salt.f90` read the per-constituent delivery ratio files.
- `dr_ru.f90` computes the per-element delivery ratio for `calc` and `full` cases and assigns named delivery ratios at runtime.

## Related pages

- [Channels](channels.md) for the receiving object.
- [Decision tables](decision-tables.md) for management triggers that may use recall objects.
- [Nutrient cycling](nutrient-cycling.md) for the channel and HRU receiving the recalled mass.
- TODO: link to input pages for `recall.rec`, `exco.exc`, and `delratio.del` once they exist.

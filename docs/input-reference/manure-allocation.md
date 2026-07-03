---
title: manure_allo.mnu
description: Manure allocation module. Defines named manure sources and routes them to HRUs and other receivers.
status: review
verified_against:
  - src/manure_allocation_read.f90
  - src/manure_allocation_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`manure_allo.mnu` defines manure-allocation objects. Each object names one or more source locations (manure storage on a farm, a feedlot, a lagoon) and one or more demand locations (HRUs, municipal treatment, inter-basin diversion). At runtime, manure produced at the sources is distributed to the demand objects under a named rule. Each allocation object holds its own source list, demand list, monthly production, storage, and per-source withdrawal history.

The allocation file ties three databases together:

- [`fertilizer.frt`](../input-reference/frt.md). Each source's `manure_typ` is a key into `fertdb` (cross-walked at read time into `src%fertdb`).
- [`lum.dtl`](../input-reference/dtl.md). For HRU demands, the rule name is a key into `dtbl_lum` (cross-walked into `trn%dtbl_num`).
- `chem_app.ops`. The first action of the matched lum decision table names a chemical-application profile in `chemapp_db`, cross-walked into `manure_amt%app_method`.

## Source

- Reader: [`src/manure_allocation_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/manure_allocation_read.f90)
- Types: [`src/manure_allocation_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/manure_allocation_module.f90)
  - `type manure_allocation` (variable `mallo`)
  - `type manure_source_objects` (`mallo(i)%src(j)`)
  - `type manure_demand_objects` (`mallo(i)%trn(j)`)

## Format

- Line 1: title (skipped).
- Line 2: number of allocation objects, `imax`. Stored in `db_mx%mallo_db`.
- Per allocation object, in order:
  1. Header line (skipped).
  2. Object header record: `name`, `rule_typ`, `src_obs`, `trn_obs`.
  3. Header line (skipped).
  4. `src_obs` source records.
  5. Header line (skipped).
  6. `trn_obs` demand records.

### Object header

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | name | char(25) | Allocation-object name. |
| 2 | rule_typ | char(25) | Allocation rule. Selects how unmet demand is split across sources. |
| 3 | src_obs | int | Number of source objects in this allocation. |
| 4 | trn_obs | int | Number of demand objects in this allocation. |

### Source record (one per source)

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | num | int | none | Sequential source id. Used as the array index. |
| 2 | mois_typ | char(3) | none | Moisture class: `wet` or `dry`. |
| 3 | manure_typ | char(25) | none | Manure-product name. Cross-walked against `fertdb(:)%fertnm` and stored in `fertdb`. |
| 4 | lat | real | degrees | Latitude of the source. |
| 5 | long | real | degrees | Longitude of the source. |
| 6 | stor_init | real | t | Initial manure in storage. |
| 7 | stor_max | real | t | Storage capacity. |
| 8..19 | prod_mon(1..12) | real | t/month | Average monthly manure production. Twelve values, January through December. |

### Demand record (one per demand)

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | num | int | Sequential demand id. Used as the array index. |
| 2 | ob_typ | char(10) | Receiver type: `hru` (apply to an HRU), `muni` (municipal treatment), or `divert` (inter-basin diversion). |
| 3 | ob_num | int | Number of the receiving object of `ob_typ`. |
| 4 | dtbl | char(25) | Decision-table name. For `hru`, matched against `dtbl_lum`. |
| 5 | right | char(2) | Allocation right. `sr` for senior, `jr` for junior. |

For an HRU demand, the reader sets `hru(ihru)%man_trn_dtbl` to the resolved decision-table index, and looks up the first action's `option` against `chemapp_db(:)%name` to set the application method on `mallo(imro)%trn(itrn)%manure_amt%app_method`.

## Example

A two-line skeleton with one source and one HRU demand:

```
manure_allo.mnu: example
1
name            rule_typ    src_obs  trn_obs
farm_a          fixed             1        1
num  mois_typ  manure_typ  lat       long      stor_init  stor_max   prod_mon(1..12)
  1  wet       beef_salt   41.99   -93.62          0.0       500.0    5.0  5.0  6.0  6.0  7.0  7.0  7.0  7.0  6.0  6.0  5.0  5.0
num  ob_typ    ob_num  dtbl                 right
  1  hru            1  apply_manure_dtbl       sr
```

The decision-table named `apply_manure_dtbl` must exist in [`lum.dtl`](../input-reference/dtl.md) and its first action must name an entry in `chem_app.ops` for the cross-walks to resolve.

## Related files

- [`fertilizer.frt`](../input-reference/frt.md). Defines the manure-product names that source records reference, and the manure organic-matter database (`manure_db.frt`, `manure_om.frt`).
- [`lum.dtl`](../input-reference/dtl.md). Decision tables that fire manure applications at each demand HRU.
- `chem_app.ops`. Chemical-application profiles (rate, method) selected by the decision-table action.

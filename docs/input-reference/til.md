---
title: "tillage.til"
description: Tillage operation database. Mixing efficiency, depth, random roughness, and ridge geometry for each named tillage implement.
status: review
verified_against:
  - src/till_parm_read.f90
  - src/tillage_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`tillage.til` defines each named tillage operation. Each record fills one `tillage_db` entry in the `tilldb` array. Tillage operations referenced in `chem_app.ops` and management decision tables look up the implement by name to get the mixing efficiency, mixing depth, random roughness, and ridge geometry that drive soil-mixing and surface-roughness updates in `mgt_newtillmix_*` and `mgt_tillfactor.f90`.

The reader also scans for the entry named `biomix`. If present, its `effmix` and `deptil` are copied into the module-level `bmix_eff` and `bmix_depth`, which control the daily biological mixing computed in `mgt_biomix.f90`. If no `biomix` entry is present, `bmix_eff` defaults to 0.2 and `bmix_depth` defaults to 50 mm.

## Source

- Reader: [`src/till_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/till_parm_read.f90)
- Type definition: [`src/tillage_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/tillage_data_module.f90), `type tillage_db`

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one record per tillage operation. List-directed read into `tilldb(itl)` (`type tillage_db`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | tillnm | char(16) | none | "" | tillage operation name (key from management schedules). The literal name `biomix` sets the biological mixing parameters at the module level |
| 2 | effmix | real | none | 0.0 | mixing efficiency of the tillage operation (fraction of soil mass redistributed within the till depth) |
| 3 | deptil | real | mm | 0.0 | depth of mixing caused by the tillage operation |
| 4 | ranrns | real | mm | 0.0 | random roughness imparted to the soil surface |
| 5 | ridge_ht | real | mm | 0.0 | ridge height |
| 6 | ridge_sp | real | mm | 0.0 | ridge interval (or row spacing) |

## Example

First lines of `refdata/Osu_1hru/tillage.til` (which has the title and header lines the reader expects):

```
tillage.til: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   mix_eff        mix_dp         rough      ridge_ht      ridge_sp  description
puddle                 0.980       150.000        00.000         0.000         0.000    rice_paddy_puddling_oprtn
```

The trailing `description` column is not in `tillage_db`. List-directed reads stop after the six fields are filled, so the description is silently discarded.

The Ames database has many more operations (the first records, after a correct two-line header, are):

```
chiselplow             0.65          225          20             0             0     chiselplow
cltiweed               0.3           100          15             0             0     cultiweeder
moldboardplow          0.95          250          30             0             0     mldboard
biomix                 0.01           50           0             0             0     biological_mixing
```

The `biomix` row above sets `bmix_eff = 0.01` and `bmix_depth = 50` at the module level after the file is read.

## Related files

- `chem_app.ops` and `lum.dtl` (and similar decision tables). Tillage operations reference `tillnm` from this file.
- [`codes.bsn`](../input-reference/codes-bsn.md). The active carbon model (`cswat`) selects which `mgt_newtillmix_*` routine performs the soil pool mixing.
- `hru-data.hru` and `landuse.lum`. Identify the HRUs that receive the tillage operations defined here.

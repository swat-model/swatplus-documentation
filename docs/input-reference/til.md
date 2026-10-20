---
title: "tillage.til"
description: Tillage operation database. Mixing efficiency and mixing depth for each named tillage implement, plus the biological mixing record.
status: review
verified_against:
  - src/till_parm_read.f90
  - src/tillage_data_module.f90
  - src/read_mgtops.f90
  - src/dtbl_lum_read.f90
  - src/mgt_sched.f90
  - src/actions.f90
  - src/mgt_newtillmix_cswat0.f90
  - src/mgt_newtillmix_cswat1.f90
  - src/mgt_newtillmix_wet.f90
  - src/mgt_tillfactor.f90
  - src/mgt_biomix.f90
  - src/soil_nutcarb_init.f90
  - src/time_control.f90
  - src/hru_control.f90
  - src/zero0.f90
  - src/swr_depstor.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`tillage.til` is the tillage database. Each row describes one tillage implement or operation: how much of the soil it mixes and how deep. A `till` operation in [`management.sch`](management.md), a `till` or `tillage` action in a [decision table](dtl.md), and a puddling operation all name a row of this file.

One row has a special role. A row named `biomix` sets the biological mixing efficiency and depth used by the dynamic carbon model (see [Biological mixing](#biological-mixing)).

The file is named on the `hru_parm_db` line of [`file.cio`](file-cio.md) (default `tillage.til`). If the file is missing or named `null`, the database is empty and tillage operations find no row.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one operation with the values below in this order. The reader does not match columns by header name. It reads the first six values and ignores the rest of the line, so the `description` column written by the SWAT+ Editor has no effect.

| # | Column | Units | Default | Typical range | Description |
|---|--------|-------|---------|---------------|-------------|
| 1 | `name` | - | - | - | Name of the tillage operation, up to 16 characters. Management schedules and decision tables refer to the operation by this name, so names must be unique. The name `biomix` is reserved for biological mixing. |
| 2 | `mix_eff` | fraction | 0.0 | 0.0 to 1.0 | Mixing efficiency. The fraction of the soil, residue, nutrients and other constituents in each layer within the mixing depth that is mixed uniformly over that depth. The rest stays in its original layer. |
| 3 | `mix_dp` | mm | 0.0 | 0 to 750 | Depth of mixing caused by the operation. |
| 4 | `rough` | mm | 0.0 | - | Random roughness. Read but not used. |
| 5 | `ridge_ht` | mm | 0.0 | - | Ridge height. Read but not used. |
| 6 | `ridge_sp` | mm | 0.0 | - | Ridge interval or row spacing. Read but not used. |

## Tillage mixing

On the day of a tillage operation SWAT+ takes `mix_eff` and `mix_dp` from the named row. For each soil layer whose bottom is within `mix_dp`, the fraction `mix_eff` of the layer's mass is mixed. A layer that straddles `mix_dp` contributes in proportion to the part of it above the mixing depth. The mixed material is then spread over the mixing depth in proportion to layer thickness. Soil water, texture, mineral and organic nutrient pools, residue and constituents are all mixed this way.

A mixing depth greater than 0 and less than 10 mm is raised to 11 mm. A row with `mix_dp` of 0 mixes nothing.

The `carbon` column of [`codes.bsn`](codes-bsn.md) decides what else happens. With `carbon` = 2 (dynamic carbon), the operation also raises the tillage factor of each mixed layer, which speeds the decomposition of soil organic matter for `till_eff_days` days. The tillage factor curve uses `tillmix_a`, `tillmix_b` and `tillmix_c` from [`carbon.bsn`](carbon-bsn.md). With `carbon` = 0, only the mixing is done.

A puddling operation (`pudl` in [`management.sch`](../input-reference/management.md#managementsch)) names a row of [`puddle.ops`](ops.md) and a row of this file. When the HRU has more than 1 mm of ponded water, the soil is mixed with a routine for flooded soils. Otherwise the mixing is the same as for an ordinary tillage operation.

## Biological mixing

Biological mixing is the slow mixing of the soil by roots, worms and other organisms. How it is set depends on the carbon model.

With `carbon` = 2 in [`codes.bsn`](../input-reference/codes-bsn.md), the `biomix` row of `tillage.til` sets it. Its `mix_eff` is the biological mixing efficiency and its `mix_dp` the maximum biological mixing depth. Biological mixing runs every day in layers above 0 °C. After a tillage operation the efficiency drops to zero and builds back up over the following days at a rate set by `bio_consol` in [`carbon.bsn`](../input-reference/carbon-bsn.md). If the file has no `biomix` row, the efficiency is 0.2 and the depth 50 mm. A `biomix` row with `mix_eff` of 0 turns daily biological mixing off.

With `carbon` = 0, the `biomix` row is not used for mixing. Biological mixing then happens once a year, at the end of the year, with the efficiency in the `bio_mix` column of [`hydrology.hyd`](hyd.md) and a fixed depth of 50 mm (or the soil depth, if smaller).

## Surface roughness

`rough`, `ridge_ht` and `ridge_sp` are not used. The random roughness used for surface depression storage is 20 mm for every HRU in 62.0.1, whatever tillage is done.

## Example

`refdata/Osu_1hru/tillage.til` in the SWAT+ repository:

```
tillage.til: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   mix_eff        mix_dp         rough      ridge_ht      ridge_sp  description
puddle                 0.980       150.000        00.000         0.000         0.000    rice_paddy_puddling_oprtn
```

One operation named `puddle`, used for rice paddy puddling. It mixes 98% of the soil in the top 150 mm. The file has no `biomix` row; Osu_1hru runs with `carbon` = 0 in [`codes.bsn`](../input-reference/codes-bsn.md), so biological mixing comes from [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) and the missing row has no effect.

The first lines of `refdata/Ames_sub1/tillage.til`, as shipped:

```
name           mix_eff         mix_dp        rough    ridge_ht    ridge_sp           description
bedderd            0.55           150           35           0           0           bedder(disk)
bedders            0.55           150           30           0           0           beddershaper
beddhipr           0.65           150           35           0           0           bedderdisk-hipper
beddkrow           0.85           100           40           0           0           bedderdisk-row
bedrollr           0.25            50            5           0           0           bedroller
beetcult           0.25            25           15           0           0           beetcultivator
biomix             0.01            50            0           0           0           biological_mixing
```

This file has no title line. SWAT+ skips the first two lines whatever they contain, so it takes the header as the title and the `bedderd` row as the header, and `bedderd` is not in the database. A schedule that names `bedderd` would not find it. The other 98 rows are read normally; for example `mldboard` (moldboard plow) mixes 95% of the top 250 mm. Ames_sub1 runs with `carbon` = 2, so its `biomix` row sets a daily biological mixing efficiency of 0.01 over the top 50 mm.

## Related files

- [`management.sch`](management.md): `till` and `pudl` operations name a row of this file.
- [Decision tables](dtl.md): `till` and `tillage` actions name a row of this file.
- [`puddle.ops`](ops.md): puddling parameters that go with the tillage row.
- [`codes.bsn`](codes-bsn.md): the `carbon` column selects the mixing routine and how biological mixing is set.
- [`carbon.bsn`](carbon-bsn.md): tillage factor coefficients, `till_eff_days` and `bio_consol` for the dynamic carbon model.
- [`hydrology.hyd`](hyd.md): the `bio_mix` column sets biological mixing when `carbon` = 0.

??? quote "Sources"

    - Reader: [`till_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/till_parm_read.f90)
    - Type definition and biological mixing defaults: [`tillage_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/tillage_data_module.f90)
    - Name lookup for schedules and decision tables: [`read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/read_mgtops.f90), [`dtbl_lum_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_lum_read.f90)
    - Operations: [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Mixing: [`mgt_newtillmix_cswat0.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_cswat0.f90), [`mgt_newtillmix_cswat1.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_cswat1.f90), [`mgt_newtillmix_wet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_wet.f90), [`mgt_tillfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_tillfactor.f90)
    - Biological mixing: [`mgt_biomix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_biomix.f90), [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90), [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Random roughness: [`zero0.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/zero0.f90), [`swr_depstor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_depstor.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `tilldb%tillnm` |
    | `mix_eff` | `tilldb%effmix` |
    | `mix_dp` | `tilldb%deptil` |
    | `rough` | `tilldb%ranrns` |
    | `ridge_ht` | `tilldb%ridge_ht` |
    | `ridge_sp` | `tilldb%ridge_sp` |

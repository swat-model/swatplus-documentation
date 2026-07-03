---
title: landuse.lum
description: Land use and management definitions. Pointers to plant communities, schedules, curve numbers, conservation practices, and structural BMPs.
status: review
verified_against:
  - src/landuse_read.f90
  - src/landuse_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`landuse.lum` is the master table of land use and management classes. Each row defines one class by name and lists string pointers to records in other files: the plant community (`plants.ini`), management schedule (`management.sch`), curve number entry (`cntable.lum`), conservation practice (`cons_practice.lum`), urban land use (`urban.urb`), overland-flow Manning's n class (`ovn_table.lum`), tile drainage (`tiledrain.str`), septic (`septic.str`), filter strip (`filterstrip.str`), grassed waterway (`grassedww.str`), and user BMP (`bmpuser.str`). HRUs reference a row in this table through `hru-data.hru`. After reading, the reader resolves every non-`null` string pointer to an integer index stored in `lum_str`; unresolved names are logged to `simulation.out` (unit 9001).

## Source

- Reader: [`src/landuse_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/landuse_read.f90)
- Type definition: [`src/landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/landuse_data_module.f90), `type land_use_management` (instances stored in `lum`)

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- One record per land use class. Records are list-directed (free format). All 14 fields are read on every row.
- Any pointer field that should be empty must be the literal string `null`. The reader treats `null` as "no link" and does not try to resolve it.

| # | Field | Type | Default | Description |
|---|-------|------|---------|-------------|
| 1 | name | char(40) | blank | name of the land use and management class. Referenced from `hru-data.hru` |
| 2 | cal_group | char(40) | blank | calibration group label. Not currently used by the solver |
| 3 | plant_cov | char(40) | blank | plant community pointer into `plants.ini`. Resolved to `lum_str%plant_cov` |
| 4 | mgt_ops | char(40) | blank | management schedule pointer into `management.sch`. Resolved to `lum_str%mgt_ops` |
| 5 | cn_lu | char(40) | blank | curve number entry pointer into `cntable.lum`. Resolved to `lum_str%cn_lu` |
| 6 | cons_prac | char(40) | blank | conservation practice pointer into `cons_practice.lum`. Resolved to `lum_str%cons_prac` |
| 7 | urb_lu | char(40) | blank | urban land use pointer into `urban.urb` (e.g. `URLD`, `URHD`). Resolved during urban init |
| 8 | urb_ro | char(40) | blank | urban runoff model. `usgs_reg` for USGS regression equations, `buildup_washoff` for build-up/wash-off |
| 9 | ovn | char(40) | blank | overland-flow Manning's n class pointer into `ovn_table.lum` |
| 10 | tiledrain | char(40) | blank | tile drainage pointer into `tiledrain.str`. Resolved to `lum_str%tiledrain` |
| 11 | septic | char(40) | blank | septic pointer into `septic.str`. Resolved to `lum_str%septic` |
| 12 | fstrip | char(40) | blank | filter strip pointer into `filterstrip.str`. Resolved to `lum_str%fstrip` |
| 13 | grassww | char(40) | blank | grassed waterway pointer into `grassedww.str`. Resolved to `lum_str%grassww` |
| 14 | bmpuser | char(40) | blank | user-defined BMP pointer into `bmpuser.str`. Resolved to `lum_str%bmpuser` |

The reader logs a line to `simulation.out` for every non-`null` pointer that fails to match a name in the target file. The simulation continues with the link unresolved (index zero), which means the corresponding behaviour is skipped.

## Example

Excerpt from `refdata/Ames_sub1/landuse.lum`:

```
landuse.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                         cal_group          plnt_com                                        mgt               cn2         cons_prac             urban            urb_ro           ov_mann              tile               sep               vfs              grww               bmp
cosy_lum                          null         cosy_comm                                     mgt_01        rc_strow_g     up_down_slope              null              null    convtill_nores              null              null              null              null              null
agrr_lum                          null         agrr_comm                                   AGRR_rot        rc_strow_g       cross_slope              null              null      convtill_res              null              null              null              null              null
frst_lum                          null         frst_comm                                       null            wood_f     up_down_slope              null              null        forest_med              null              null              null              null              null
urld_lum                          null              null                                       null             urban     up_down_slope              URLD   buildup_washoff     urban_asphalt              null              null              null              null              null
```

Notes:

- The header tokens written by SWAT+ Editor (`plnt_com`, `cn2`, `urban`, `ov_mann`, `tile`, `sep`, `vfs`, `grww`, `bmp`) do not match the field names in the source (`plant_cov`, `cn_lu`, `urb_lu`, `ovn`, `tiledrain`, `septic`, `fstrip`, `grassww`, `bmpuser`). The reader skips the header and uses position only.
- `urld_lum` is an urban class. Its `plant_cov` and `mgt_ops` are both `null`; the row links instead to `URLD` in `urban.urb` and selects `buildup_washoff` as the urban runoff model.
- `frst_lum` has no management schedule (`mgt_ops = null`). Forest classes typically rely on the plant community initialization alone.

## Related files

- [`hru-data.hru`](../input-reference/hru.md). Each HRU points to one `landuse.lum` row by name.
- [`cntable.lum`](../input-reference/lum.md). Curve number table referenced by the `cn_lu` field. Each row holds a name and four curve numbers (hydrologic conditions A through D).
- [`cons_practice.lum`](../input-reference/lum.md). Conservation practice table referenced by `cons_prac`. Holds USLE P factor and maximum slope length per practice.
- [`ovn_table.lum`](../input-reference/lum.md). Overland-flow Manning's n table referenced by `ovn`. Holds mean, minimum, and maximum n per class.
- [`plants.ini`](../input-reference/plt.md). Target of `plant_cov`.
- [`management.sch`](../input-reference/lum.md). Target of `mgt_ops`.
- `urban.urb`. Target of `urb_lu`.
- `tiledrain.str`, `septic.str`, `filterstrip.str`, `grassedww.str`, `bmpuser.str`. Structural BMP files targeted by the last five pointer columns.

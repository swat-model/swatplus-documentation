---
title: landuse.lum
description: Land use and management records. Each row names the plant community, management schedule, curve numbers, conservation practice, urban type, overland Manning's n and structural practices for the HRUs that use it.
status: review
verified_against:
  - src/landuse_read.f90
  - src/landuse_data_module.f90
  - src/proc_db.f90
  - src/hru_read.f90
  - src/hrudb_init.f90
  - src/hru_lum_init.f90
  - src/hru_lum_init_all.f90
  - src/plant_init.f90
  - src/cn2_init.f90
  - src/proc_hru.f90
  - src/structure_init.f90
  - src/structure_set_parms.f90
  - src/soils_init.f90
  - src/hru_control.f90
  - src/swr_percmain.f90
  - src/sep_biozone.f90
  - src/hru_urban.f90
  - src/time_conc_init.f90
  - src/actions.f90
  - src/cal_conditions.f90
  - src/conditions.f90
  - src/calsoft_hyd.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`landuse.lum` lists the land use and management records of the project. Each row has a name and a set of names that point to records in other files: the plant community in [`plant.ini`](ini.md#plantini), the management schedule in [`management.sch`](management.md), the curve numbers in [`cntable.lum`](lum-tables.md#cntablelum), the support practice in [`cons_practice.lum`](lum-tables.md#cons_practicelum), the urban land type in [`urban.urb`](str.md), the Manning's n in [`ovn_table.lum`](lum-tables.md#ovn_tablelum) and the structural practices in the [`.str` files](str.md). An HRU picks a row by name in the `lu_mgt` column of [`hru-data.hru`](hru.md). The file is named first on the `lum` line of [`file.cio`](file-cio.md) (default `landuse.lum`).

If an HRU names a land use that is not in the file, it silently gets the first row of `landuse.lum`; nothing is reported.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one land use with fourteen values, read by position. Every column must be filled; write `null` for an unused link. Names are up to 40 characters.

| # | Column | Points to | Description |
|---|--------|-----------|-------------|
| 1 | `name` | - | Land use and management name, matched against `lu_mgt` in [`hru-data.hru`](../input-reference/hru.md) and named by the decision table action `lu_change`. Names must be unique. |
| 2 | `cal_group` | - | Calibration group label, called `cal_grp` in earlier documentation. See [Calibration groups](#calibration-groups). |
| 3 | `plnt_com` | [`plant.ini`](../input-reference/ini.md#plantini) | Plant community at the start of the run. `null` starts the HRU with no plants (bare soil or an urban surface). |
| 4 | `mgt` | [`management.sch`](../input-reference/management.md#managementsch) | Management schedule. `null` means no scheduled operations: no planting, harvest or kill, so only plants that start the run growing (`lc_status` `y` in [`plant.ini`](../input-reference/ini.md#plantini)) grow. |
| 5 | `cn2` | [`cntable.lum`](../input-reference/lum-tables.md#cntablelum) | Curve number record. The HRU's soil group picks one of its four values. |
| 6 | `cons_prac` | [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum) | Conservation practice, which sets the USLE P factor. |
| 7 | `urban` | [`urban.urb`](../input-reference/str.md#urbanurb) | Urban land type. `null` for land that is not urban. |
| 8 | `urb_ro` | - | Urban build-up and wash-off method: `usgs_reg` (USGS regression equations) or `buildup_washoff` (build-up and wash-off, as in SWMM). Any other value, including `null`, gives no urban sediment and nutrient loads even when `urban` is set. |
| 9 | `ov_mann` | [`ovn_table.lum`](../input-reference/lum-tables.md#ovn_tablelum) | Overland flow Manning's n class. |
| 10 | `tile` | [`tiledrain.str`](../input-reference/str.md#tiledrainstr) | Tile drainage. |
| 11 | `sep` | [`septic.str`](../input-reference/str.md#septicstr) | Septic system. See [Septic systems](#septic-systems). |
| 12 | `vfs` | [`filterstrip.str`](../input-reference/str.md#filterstripstr) | Vegetative filter strip. |
| 13 | `grww` | [`grassedww.str`](../input-reference/str.md#grassedwwstr) | Grassed waterway. |
| 14 | `bmp` | [`bmpuser.str`](../input-reference/str.md#bmpuserstr) | User-defined BMP removal efficiencies. |

## Name matching

All names are matched case-sensitively when the files are read, before the HRUs are set up. For each name other than `null` that is not found, SWAT+ writes a line to `diagnostics.out` with the land use name and the missing name:

| Column | Message | Result when not found |
|--------|---------|-----------------------|
| `plnt_com` | `not found in plant.ini` | No plants |
| `mgt` | `not found in management.sch` | No schedule |
| `cn2` | `not found in cntable.lum` | Built-in curve numbers 30, 55, 70, 77 (soil groups A to D) |
| `cons_prac` | `not found (landuse-consprac)` | P factor 1.0 |
| `tile` | `not found (landuse-tiledr)` | No tile drain |
| `sep` | `not found (landuse-septic)` | No septic system |
| `vfs` | `not found (landuse-fstrip)` | No filter strip |
| `grww` | `not found (landuse-grassww)` | No grassed waterway |
| `bmp` | `not found (landuse-bmpuser)` | No user BMP |

`urban` and `ov_mann` are matched later, when each HRU's plant community is set up, and an unknown name is not reported. An unknown `urban` name leaves the HRU non-urban. An unknown `ov_mann` name leaves the HRU's Manning's n at its built-in value of 0.05.

## Use at the start of the run

For each HRU, SWAT+ takes from its land use:

- the plant community, the management schedule and the starting operation in the schedule (from `rot_yr_ini` in [`plant.ini`](../input-reference/ini.md#plantini));
- the curve number for moisture condition II from [`cntable.lum`](../input-reference/lum-tables.md#cntablelum), for the soil's hydrologic group, from which the condition I and III values follow (see [hydrology](../model-theory/hydrology.md));
- the USLE P factor from [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum);
- the urban land type and urban runoff method;
- the overland Manning's n (the `ovn_mean` column of [`ovn_table.lum`](../input-reference/lum-tables.md#ovn_tablelum)), used for the time of concentration;
- the structural practice parameters from the `.str` files. The septic record is assigned before the soil layers are set up, so that a biozone layer can be added to the profile.

## Land use change

The decision table action `lu_change` (see [decision tables](dtl.md)) switches an HRU to another `landuse.lum` row during the run and logs the change to `lu_change_out.txt`. The new plant community, schedule, curve number, P factor (and the USLE multiplier), urban type and Manning's n replace the old ones. Some values set at the start are not recalculated:

- The time of concentration keeps the old Manning's n.
- The structural practice parameters (tile, filter strip, grassed waterway, user BMP, septic) are not set again. The HRU keeps those of its first land use.
- The `cal_group` used by [`calibration.cal`](../calibration/parameter-change-files.md) and decision table conditions stays that of the first land use, while soft calibration uses the group of the current land use.

## Calibration groups

`cal_group` labels land uses for calibration:

- Soft calibration matches the `name` column of the land use regions in [`water_balance.sft`](../calibration/soft-calibration.md) against `cal_group`; the name `basin` matches every HRU.
- In [`calibration.cal`](../calibration/parameter-change-files.md), the condition `cal_group` limits a parameter change to HRUs with that group, and the condition `landuse` limits it to HRUs with that `landuse.lum` name.
- Decision tables can test `cal_group` as a condition.

A value of `null` is an ordinary label: all land uses with `null` form one group.

## Septic systems

When `sep` names a record in [`septic.str`](str.md), that record is assigned to every HRU with this land use. If its operation flag is not zero, SWAT+ adds a biozone layer to the soil profile at the depth and thickness given in [`septic.str`](../input-reference/str.md#septicstr), and from the year the system becomes operational it runs the biozone routine on each day the biozone layer is above freezing.

In 62.0.1 the daily volume of septic tank effluent is never calculated and stays at zero. No effluent water is added to the biozone layer, and the effluent concentrations in [`septic.sep`](../input-reference/str.md#septicsep), which are multiplied by that volume, add no nitrogen, phosphorus or BOD to the soil. The biozone routine still runs on the water and nutrients already in the layer. Septic systems set up through this column therefore have no effluent load on the HRU water or nutrient balance.

## Example

`refdata/Ames_sub1/landuse.lum` in the SWAT+ repository, four of its rows, with the spacing reduced:

```
landuse.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name      cal_group plnt_com  mgt      cn2        cons_prac     urban urb_ro          ov_mann        tile sep  vfs  grww bmp
cosy_lum  null      cosy_comm mgt_01   rc_strow_g up_down_slope null  null            convtill_nores null null null null null
agrr_lum  null      agrr_comm AGRR_rot rc_strow_g cross_slope   null  null            convtill_res   null null null null null
frst_lum  null      frst_comm null     wood_f     up_down_slope null  null            forest_med     null null null null null
urld_lum  null      null      null     urban      up_down_slope URLD  buildup_washoff urban_asphalt  null null null null null
```

- `cosy_lum` grows the corn and soybean community `cosy_comm` under schedule `mgt_01`, with row crop curve numbers (straight row, good condition) and no support practice (P = 1 for up-and-down-slope tillage).
- `frst_lum` has no schedule, so the forest in `frst_comm` has no operations; it grows only if `frst_comm` starts it growing.
- `urld_lum` has no plants. It links to the urban type `URLD` in [`urban.urb`](../input-reference/str.md#urbanurb), uses build-up and wash-off for urban loads, the `urban` curve numbers (98 for all soil groups) and the Manning's n of asphalt.
- In this project `AGRR_rot` is not in [`management.sch`](../input-reference/management.md#managementsch), so `diagnostics.out` reports `agrr_lum AGRR_rot not found in management.sch` and HRUs with `agrr_lum` run without a schedule.

## Related files

- [`hru-data.hru`](hru.md): selects a land use by name in its `lu_mgt` column.
- [`plant.ini`](ini.md#plantini): plant communities.
- [`management.sch`](management.md): management schedules.
- [`cntable.lum`, [`cons_practice.lum`](../input-reference/lum-tables.md#cons_practicelum) and `ovn_table.lum`](lum-tables.md): the lookup tables.
- [Structural practices and `urban.urb`](str.md): [`tiledrain.str`](../input-reference/str.md#tiledrainstr), [`septic.str`](../input-reference/str.md#septicstr), [`filterstrip.str`](../input-reference/str.md#filterstripstr), [`grassedww.str`](../input-reference/str.md#grassedwwstr), [`bmpuser.str`](../input-reference/str.md#bmpuserstr), [`septic.sep`](../input-reference/str.md#septicsep) and [`urban.urb`](../input-reference/str.md#urbanurb).
- [`lum.dtl`](dtl.md): decision tables, including `lu_change`.
- [Plant growth and land use management](../model-theory/plant-growth-lum.md).

??? quote "Sources"

    - Reader: [`landuse_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_read.f90), called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90) after the plant community, schedule, lookup table and structural files
    - Type definitions: `type land_use_management` and `type land_use_structures` in [`landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_data_module.f90)
    - Name lookup from `hru-data.hru`: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90); `cal_group` copied to the HRU in [`hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90)
    - HRU setup: [`hru_lum_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lum_init.f90), [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90), [`cn2_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cn2_init.f90), [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90)
    - Structural practices: [`structure_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/structure_init.f90), [`structure_set_parms.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/structure_set_parms.f90); septic setup in [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90) and [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90); daily septic code in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`swr_percmain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmain.f90), [`sep_biozone.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sep_biozone.f90)
    - Urban loads: [`hru_urban.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_urban.f90)
    - Land use change: `lu_change` in [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Calibration groups: [`cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90), [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`calsoft_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_hyd.f90)
    - File name slot: `in_lum%landuse_lum` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `lum%name` |
    | `cal_group` | `lum%cal_group`, copied to `hru%cal_group` and `hru%lum_group_c` |
    | `plnt_com` | `lum%plant_cov`, index `lum_str%plant_cov` |
    | `mgt` | `lum%mgt_ops`, index `lum_str%mgt_ops` |
    | `cn2` | `lum%cn_lu`, index `lum_str%cn_lu` |
    | `cons_prac` | `lum%cons_prac`, index `lum_str%cons_prac` |
    | `urban` | `lum%urb_lu`, index `hru%luse%urb_lu` |
    | `urb_ro` | `lum%urb_ro`, copied to `hru%luse%urb_ro` |
    | `ov_mann` | `lum%ovn`, value `hru%luse%ovn` |
    | `tile` | `lum%tiledrain`, index `lum_str%tiledrain` |
    | `sep` | `lum%septic`, index `lum_str%septic`, then `iseptic` |
    | `vfs` | `lum%fstrip`, index `lum_str%fstrip` |
    | `grww` | `lum%grassww`, index `lum_str%grassww` |
    | `bmp` | `lum%bmpuser`, index `lum_str%bmpuser` |

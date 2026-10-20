---
title: Land use lookup tables (*.lum)
description: Curve number, conservation practice and overland flow Manning's n tables that landuse.lum names by record.
status: review
verified_against:
  - src/cntbl_read.f90
  - src/cons_prac_read.f90
  - src/overland_n_read.f90
  - src/landuse_data_module.f90
  - src/landuse_read.f90
  - src/proc_db.f90
  - src/cn2_init.f90
  - src/curno.f90
  - src/plant_init.f90
  - src/hydro_init.f90
  - src/time_conc_init.f90
  - src/ero_ysed.f90
  - src/mgt_sched.f90
  - src/actions.f90
  - src/cal_parm_select.f90
  - src/main.f90.in
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Three lookup tables supply values that [`landuse.lum`](lum.md) names by record: `cntable.lum` (SCS curve numbers), `cons_practice.lum` (USLE support practice factor) and `ovn_table.lum` (Manning's n for overland flow). They are named third, fourth and fifth on the `lum` line of [`file.cio`](file-cio.md), after [`landuse.lum`](../input-reference/lum.md) and [`management.sch`](../input-reference/management.md#managementsch). If a file is missing or named `null`, every land use gets the built-in values given below.

All three files have the same layout. Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one record, read by position. Values after the last numeric column (the descriptions the SWAT+ Editor writes) are not read. Record names are up to 40 characters and are matched case-sensitively.

## cntable.lum

Curve numbers for moisture condition II, one value per hydrologic soil group, for each combination of land cover, treatment and hydrologic condition. The `cn2` column of [`landuse.lum`](../input-reference/lum.md) names a record.

| # | Column | Units | Built-in value | Range | Description |
|---|--------|-------|----------------|-------|-------------|
| 1 | `name` | - | - | - | Curve number record name. |
| 2 | `cn_a` | - | 30 | 30 to 100 | Curve number for hydrologic soil group A. |
| 3 | `cn_b` | - | 55 | 30 to 100 | Curve number for hydrologic soil group B. |
| 4 | `cn_c` | - | 70 | 30 to 100 | Curve number for hydrologic soil group C. |
| 5 | `cn_d` | - | 77 | 30 to 100 | Curve number for hydrologic soil group D. |

The SWAT+ Editor also writes `description`, `treat` and `cond_cov` columns, which are not read. The built-in values apply to land uses whose `cn2` is `null` or not found.

### Curve number in the model

At the start of the run each HRU takes the value for the hydrologic soil group (`hyd_grp`) of its soil in [`soils.sol`](sol.md). The table values are those of SCS Engineering Division (1986), which apply to a 5% slope; SWAT+ 62.0.1 does not adjust them for the HRU slope. From $CN_2$ SWAT+ derives the dry and wet condition values

$$CN_1 = CN_2 - \frac{20\,(100 - CN_2)}{(100 - CN_2) + \exp\!\left[2.533 - 0.0636\,(100 - CN_2)\right]}, \qquad CN_1 \ge 0.4\,CN_2$$

$$CN_3 = CN_2\,\exp\!\left[0.006729\,(100 - CN_2)\right]$$

and the retention parameter curve used for daily runoff, as described in [hydrology](../model-theory/hydrology.md).

$CN_2$ can change during the run through the management operation `cnup` in [`management.sch`](management.md), the decision table action `cn_update` (both limited to 35 to 95), a land use change (`lu_change`, which picks the new land use's record) and the calibration parameter `cn2` in [`calibration.cal`](../calibration/parameter-change-files.md).

### Example

`refdata/Ames_sub1/cntable.lum` in the SWAT+ repository, first records, with the spacing reduced:

```
cntable.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name        cn_a      cn_b      cn_c      cn_d  description  treat               cond_cov
fal_bare    77.00000  86.00000  91.00000  94.00000  Fallow   Bare_soil           ----
fal_res_p   76.00000  85.00000  90.00000  93.00000  Fallow   Crop_residue_cover  Poor
fal_res_g   74.00000  83.00000  88.00000  90.00000  Fallow   Crop_residue_cover  Good
rc_strow_p  72.00000  81.00000  88.00000  91.00000  Row_crops  Straight_row      Poor
```

The names combine land cover, treatment and condition: `rc_strow_p` is row crops, straight row, poor condition. The SWAT+ Editor's table has 52 records, from fallow and row crops to forest, farmsteads and roads.

## cons_practice.lum

USLE support practice factors for conservation practices. The `cons_prac` column of [`landuse.lum`](../input-reference/lum.md) names a record.

| # | Column | Units | Built-in value | Range | Description |
|---|--------|-------|----------------|-------|-------------|
| 1 | `name` | - | - | - | Conservation practice name. |
| 2 | `usle_p` | - | 1.0 | 0 to 1 | USLE support practice factor $P$. |
| 3 | `slp_len_max` | m | 1.0 | - | Maximum slope length for the practice. Read but not used (see below). |

The SWAT+ Editor also writes a `description` column, which is not read. The built-in values apply to land uses whose `cons_prac` is `null` or not found, so a P factor of 1 means no support practice.

### P factor in the model

$P$ enters the MUSLE sediment yield through a multiplier fixed at the start of the run:

$$K \cdot C_{frg} \cdot P \cdot LS \cdot 11.8$$

where $K$ and $C_{frg}$ come from the top soil layer (see [soils.sol](sol.md#erosion)), and the slope length and steepness factor is

$$LS = \left(\frac{L}{22.128}\right)^{m}\left(65.41\,\sin^2\alpha + 4.56\,\sin\alpha + 0.065\right), \qquad m = 0.6\left[1 - \exp(-35.835\,S)\right]$$

with $L$ the slope length (`slp_len` in [`topography.hyd`](hyd.md), m), $S$ the slope (m/m) and $\alpha = \arctan S$. The model works out the smaller of $L$ and `slp_len_max`, but then computes $LS$ from $L$, so `slp_len_max` has no effect on $LS$ in 62.0.1. See [erosion and sediment](../model-theory/erosion-sediment.md).

$P$ can also be set during the run by the decision table actions `p_factor`, `contour`, `stripcrop` and `terrace`, which recompute the multiplier. The calibration parameter `usle_p` in [`calibration.cal`](../calibration/parameter-change-files.md) changes the HRU's P factor after the multiplier has been computed and does not recompute it, so by itself it does not change sediment yield.

### Example

`refdata/Ames_sub1/cons_practice.lum`, first records:

```
cons_practice.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                    usle_p   slp_len_max  description
up_down_slope          1.00000     121.00000  Up_and_down_slope
cross_slope            0.75000     121.00000  Cross_slope_tillage
contour_farming        0.50000     121.00000  Contour_tillage
strip_cros_slope       0.37000     121.00000  Strip_cropping_cross_slope
```

The SWAT+ Editor's table has 38 records: up-and-down and cross-slope tillage, contouring and strip cropping by slope class (1-2% to 21-25%, with pasture or row crops), and terraces by slope class with sod or underflow outlets.

## ovn_table.lum

Manning's roughness coefficient for overland flow by tillage, residue and land cover. The `ov_mann` column of [`landuse.lum`](../input-reference/lum.md) names a record.

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Manning's n class name. |
| 2 | `ovn_mean` | s/m<sup>1/3</sup> | 0.5 | Mean Manning's n for overland flow. This is the value the model uses. |
| 3 | `ovn_min` | s/m<sup>1/3</sup> | 0.5 | Minimum Manning's n. Read but not used; a guide for calibration ranges. |
| 4 | `ovn_max` | s/m<sup>1/3</sup> | 0.5 | Maximum Manning's n. Read but not used; a guide for calibration ranges. |

The SWAT+ Editor also writes a `description` column, which is not read. A land use whose `ov_mann` is `null` or not found does not take a value from this file; its HRUs keep the model's starting value of 0.05.

### Manning's n in the model

The HRU's Manning's n sets the overland part of its time of concentration (hours), which controls the peak runoff rate:

$$t_{ov} = \frac{0.0556\,(L\,n)^{0.6}}{(S + 0.0001)^{0.3}}$$

with $L$ the slope length (m) and $S$ the slope (m/m). The same $n$ is used as the roughness of the HRU's concentrated flow channel in the channel part of the time of concentration, and in the area-weighted roughness of routing units.

The time of concentration is computed once, before calibration is applied. The calibration parameter `ovn` in [`calibration.cal`](../calibration/parameter-change-files.md) changes the HRU's Manning's n after that, and a land use change (`lu_change`) also leaves the time of concentration unchanged, so neither alters the peak runoff rate in 62.0.1.

### Example

`refdata/Ames_sub1/ovn_table.lum`, first records:

```
ovn_table.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                  ovn_mean       ovn_min       ovn_max  description
fallow_nores           0.01000       0.00800       0.01200  Fallow_no_residue
convtill_nores         0.09000       0.06000       0.12000  Conventional_tillage_no_residue
convtill_res           0.19000       0.16000       0.22000  Conventional_tillage_residue
chisplow_nores         0.09000       0.06000       0.12000  Chisel_plow_no_residue
```

The SWAT+ Editor's table has 20 records, from fallow (0.01) and tilled cropland through range, grasses and forest (up to 0.80 for heavy forest) to urban surfaces (0.011 for asphalt).

## Related files

- [`landuse.lum`](lum.md): names records in these tables in its `cn2`, `cons_prac` and `ov_mann` columns.
- [`soils.sol`](sol.md): the hydrologic soil group that picks the curve number, and the K factor and rock content of the MUSLE multiplier.
- [`topography.hyd`](hyd.md): slope and slope length.
- [`management.sch`](management.md) and [`lum.dtl`](dtl.md): the `cnup` operation and the `cn_update`, `p_factor`, `contour`, `stripcrop` and `terrace` actions.
- [Parameter change files](../calibration/parameter-change-files.md): calibration parameters `cn2`, `usle_p` and `ovn`.

??? quote "Sources"

    - Readers: [`cntbl_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cntbl_read.f90), [`cons_prac_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cons_prac_read.f90), [`overland_n_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/overland_n_read.f90), called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90)
    - Type definitions: `type curvenumber_table`, `type conservation_practice_table` and `type overlandflow_n_table` in [`landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_data_module.f90)
    - Name lookup: [`landuse_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_read.f90) (`cn2`, `cons_prac`); [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90) (`ov_mann`)
    - Curve number: [`cn2_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cn2_init.f90), [`curno.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/curno.f90); changes in [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90) (`cnup`) and [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90) (`cn_update`)
    - P factor and LS: [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90), [`hydro_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydro_init.f90), [`ero_ysed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ysed.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Manning's n: [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90); call order in [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - File name slots: `in_lum%cntable_lum`, `in_lum%cons_prac_lum`, `in_lum%ovn_lum` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `cntable.lum` `name` | `cn%name` |
    | `cn_a`, `cn_b`, `cn_c`, `cn_d` | `cn%cn(1)` to `cn%cn(4)`, copied to `cn2(j)` |
    | `cons_practice.lum` `name` | `cons_prac%name` |
    | `usle_p` | `cons_prac%pfac`, copied to `hru%lumv%usle_p` |
    | `slp_len_max` | `cons_prac%sl_len_mx` |
    | `ovn_table.lum` `name` | `overland_n%name` |
    | `ovn_mean` | `overland_n%ovn`, copied to `hru%luse%ovn` |
    | `ovn_min`, `ovn_max` | `overland_n%ovn_min`, `overland_n%ovn_max` |

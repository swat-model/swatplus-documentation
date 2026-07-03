---
title: Land use lookup tables (*.lum)
description: Curve number, conservation practice, and overland flow Manning's n tables referenced by landuse.lum.
status: review
verified_against:
  - src/cntbl_read.f90
  - src/cons_prac_read.f90
  - src/overland_n_read.f90
  - src/landuse_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

Three lookup files supply numeric parameters that [`landuse.lum`](lum.md) references by name: `cntable.lum` (SCS curve numbers), `cons_practice.lum` (USLE P factor and maximum slope length), and `ovn_table.lum` (overland-flow Manning's n). Each file has the same shape: a title line, a header line, then one record per row. Rows are read with list-directed I/O, so any column after the last typed field is ignored by the solver.

## cntable.lum

Curve number table. Each entry holds four SCS-CN values for hydrologic soil groups A, B, C, and D.

### Source

- Reader: [`src/cntbl_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cntbl_read.f90)
- Type: [`src/landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/landuse_data_module.f90), `type curvenumber_table` (instances stored in `cn`)
- Sized into `db_mx%cn_lu` after the file is read.

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- One record per curve number entry. Fields are list-directed.

| # | Field | Type | Default | Description |
|---|-------|------|---------|-------------|
| 1 | name | char(40) | blank | curve number entry name. Referenced from `landuse.lum` field `cn_lu` |
| 2 | cn(1) | real | 30.0 | curve number for hydrologic soil group A |
| 3 | cn(2) | real | 55.0 | curve number for hydrologic soil group B |
| 4 | cn(3) | real | 70.0 | curve number for hydrologic soil group C |
| 5 | cn(4) | real | 77.0 | curve number for hydrologic soil group D |

Curve numbers are dimensionless and bounded by 0 and 100. SWAT+ Editor writes additional `description`, `treat`, and `cond_cov` columns after `cn(4)`. The reader does not consume them.

### Example

Excerpt from `refdata/Ames_sub1/cntable.lum`:

```
cntable.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                      cn_a          cn_b          cn_c          cn_d  description                                                             treat                                     cond_cov
fal_bare              77.00000      86.00000      91.00000      94.00000  Fallow                                                                  Bare_soil                                 ----
rc_strow_g            67.00000      78.00000      85.00000      89.00000  Row_crops                                                               Straight_row                              Good
wood_f                36.00000      60.00000      73.00000      79.00000  Woods                                                                   ----                                      Fair
urban                 98.00000      98.00000      98.00000      98.00000  Paved_parking_lots_roofs_driveways_etc_(excl_right-of-way)              ----                                      ----
```

## cons_practice.lum

Conservation practice table. Supplies the USLE support practice factor (P) and the maximum slope length used for length-slope factor calculations.

### Source

- Reader: [`src/cons_prac_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cons_prac_read.f90)
- Type: [`src/landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/landuse_data_module.f90), `type conservation_practice_table` (instances stored in `cons_prac`)
- Sized into `db_mx%cons_prac` after the file is read.

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- One record per practice. Fields are list-directed.

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | blank | - | practice name. Referenced from `landuse.lum` field `cons_prac` |
| 2 | pfac | real | 1.0 | - | USLE support practice factor (P). Dimensionless, 0 to 1 |
| 3 | sl_len_mx | real | 1.0 | m | maximum slope length for the practice |

SWAT+ Editor writes a `description` column after `sl_len_mx`. The reader does not consume it.

### Example

Excerpt from `refdata/Ames_sub1/cons_practice.lum`:

```
cons_practice.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                    usle_p   slp_len_max  description
up_down_slope          1.00000     121.00000  Up_and_down_slope
cross_slope            0.75000     121.00000  Cross_slope_tillage
contour_farming        0.50000     121.00000  Contour_tillage
strip_contour          0.25000     121.00000  Strip_cropping_contour
ter_3-8_sodout         0.50000      76.00000  terraces_3-8%_slopes_sod-outlet
```

## ovn_table.lum

Overland-flow Manning's n table. Supplies a mean, minimum, and maximum n per land use class for sheet-flow routing across the HRU.

### Source

- Reader: [`src/overland_n_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/overland_n_read.f90)
- Type: [`src/landuse_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/landuse_data_module.f90), `type overlandflow_n_table` (instances stored in `overland_n`)
- Sized into `db_mx%ovn` after the file is read.

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- One record per class. Fields are list-directed.

| # | Field | Type | Default | Units | Description |
|---|-------|------|---------|-------|-------------|
| 1 | name | char(40) | blank | - | class name. Referenced from `landuse.lum` field `ovn` |
| 2 | ovn | real | 0.5 | s m^(-1/3) | mean Manning's n for overland flow |
| 3 | ovn_min | real | 0.5 | s m^(-1/3) | minimum Manning's n for overland flow |
| 4 | ovn_max | real | 0.5 | s m^(-1/3) | maximum Manning's n for overland flow |

SWAT+ Editor writes a `description` column after `ovn_max`. The reader does not consume it.

### Example

Excerpt from `refdata/Ames_sub1/ovn_table.lum`:

```
ovn_table.lum: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                  ovn_mean       ovn_min       ovn_max  description
convtill_nores         0.09000       0.06000       0.12000  Conventional_tillage_no_residue
convtill_res           0.19000       0.16000       0.22000  Conventional_tillage_residue
notill_2-9res          0.30000       0.17000       0.47000  No_till_2-9_t/ha_residue
forest_med             0.60000       0.50000       0.70000  Forest_medimum_good
urban_asphalt          0.01100       0.01100       0.01100  Urban_asphalt
```

## Related files

- [`landuse.lum`](lum.md). Master land-use management table. Its `cn_lu`, `cons_prac`, and `ovn` columns name rows in these three files.
- [`hru-data.hru`](hru.md). Selects a `landuse.lum` row per HRU, which in turn selects rows in these three tables.

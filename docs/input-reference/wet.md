---
title: "*.wet (wetland)"
description: Wetland object table and the hydrology database for HRU impoundments.
status: review
verified_against:
  - src/wet_read.f90
  - src/wet_read_hyd.f90
  - src/reservoir_data_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The wetland group has two input files declared in `type input_res` (`src/input_file_module.f90`):

- `wetland.wet` is the wetland object table. One record per wetland, naming the initial-condition set, hydrology profile, release rule, sediment profile, nutrient profile, and weir profile that apply.
- `hydrology.wet` is the wetland hydrology database. One record per named hydrology profile. The geometry is HRU-relative (fraction of HRU area, depth in mm) rather than absolute area and volume as for reservoirs.

Wetlands reuse the reservoir sediment, nutrient, weir, and initial-condition databases. The wetland records in `wetland.wet` point at the same `sediment.res`, `nutrients.res`, `weir.res`, and `initial.res` tables described in [reservoir.res](../input-reference/res.md).

## Source

- Readers: [`src/wet_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/wet_read.f90), [`src/wet_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/main/src/wet_read_hyd.f90)
- Type definitions: [`src/reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/reservoir_data_module.f90), `type reservoir_data_char_input` (shared with reservoirs) and `type wetland_hyd_data`
- Filename declarations: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_res`

## wetland.wet

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per wetland with list-directed I/O. The first integer on each record is the wetland id (used as the index into `wet_dat_c`). The remaining columns are read into `type reservoir_data_char_input` in declaration order (the same type used by reservoirs).

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | id | int | wetland id. Used as the array index into `wet_dat_c` |
| 2 | name | char(25) | wetland name |
| 3 | init | char(25) | initial-state pointer. Cross-walks with `init` in `initial.res` |
| 4 | hyd | char(25) | hydrology pointer. Cross-walks with `name` in `hydrology.wet` |
| 5 | release | char(25) | release rule pointer (decision-table name) |
| 6 | sed | char(25) | sediment pointer. Cross-walks with `name` in `sediment.res` |
| 7 | nut | char(25) | nutrient pointer. Cross-walks with `name` in `nutrients.res` |

The example dataset writes a trailing `WEIR` column. The base type has six character fields (name, init, hyd, release, sed, nut). A weir pointer is held in the extension type `reservoir_data` (`character (len=25) :: weir`). The list-directed reader for `wetland.wet` does not consume a separate weir token into the base record; the source links wetland weirs through dedicated reservoir-conditions input. See the Important note below.

### Example

`refdata/Osu_1hru/wetland.wet`:

```
wetland.       wet: written by SWAT+ edi############for SWAT+ rev.60.5.4
     id                name        init         hyd         rel         sed         nut        WEIR
       1          paddy0001    initwet2       paddy        weir     sedwet1     nutwet1       weir1
```

Notes:

- The title line in this dataset is partially corrupted ("wetland.       wet:"). The reader skips it as a single text line, so the content does not matter as long as it stays on one line.
- The `rel` column value `weir` is matched against decision-table names. If no match exists in `res_rel.dtl` (or in the `ctbl_` conditional tables), the wetland will be flagged as missing a release rule.

## hydrology.wet

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per hydrology profile with list-directed I/O. Records are read into `wet_hyddb` (an array of `type wetland_hyd_data`) in declaration order.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(25) | none | "default" | hydrology profile name |
| 2 | psa | real | fraction | 0.0 | fraction of HRU area at the principal spillway. Surface-inlet riser flow starts at this level |
| 3 | pdep | real | mm | 0.0 | average water depth at the principal spillway |
| 4 | esa | real | fraction | 0.0 | fraction of HRU area at the emergency spillway. Overflow into the ditch starts at this level |
| 5 | edep | real | mm | 0.0 | average water depth at the emergency spillway |
| 6 | k | real | mm/hr | 0.01 | hydraulic conductivity of the wetland bottom |
| 7 | evrsv | real | none | 0.7 | wetland evaporation coefficient |
| 8 | acoef | real | none | 1.0 | volume-surface area coefficient for HRU impoundment |
| 9 | bcoef | real | none | 1.0 | volume-depth coefficient for HRU impoundment |
| 10 | ccoef | real | none | 1.0 | volume-depth coefficient for HRU impoundment |
| 11 | frac | real | none | 0.5 | fraction of HRU that drains into the impoundment |

The reader fills defaults when fields are zero or non-positive:

- If `psa <= 0`, sets `psa = 0.08 * wet_hyd(ires)%pdep` (uses the previously initialized `wet_hyd`, not the just-read `wet_hyddb`).
- If `esa <= 0`, sets `esa = 1.5 * wet_hyd(ires)%psa`.
- If `evrsv <= 0`, sets `evrsv = 0.6`.

### Example

`refdata/Osu_1hru/hydrology.wet`:

```
hydrology.wet: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    hru_ps         dp_ps        hru_es         dp_es             k          evap   vol_area_co      vol_dp_a      vol_dp_b      hru_frac  
paddy			          1.00        150.00         1.00        150.00           0.5           0.75          1.00         1.00         1.00          1.0  
```

Editor headers `hru_ps`, `dp_ps`, `hru_es`, `dp_es`, `evap`, `vol_area_co`, `vol_dp_a`, `vol_dp_b`, `hru_frac` correspond to source fields `psa`, `pdep`, `esa`, `edep`, `evrsv`, `acoef`, `bcoef`, `ccoef`, `frac`. Column order is what matters.

## Related files

- [`reservoir.res`](../input-reference/res.md) and [`initial.res`](../input-reference/res.md). Shared tables. `wetland.wet` records point at `initial.res` names, and the sediment, nutrient, and weir lookups use the same databases as reservoirs.
- HRU connectivity. Each wetland is attached to an HRU; the geometry in `hydrology.wet` is expressed as fractions of HRU area.

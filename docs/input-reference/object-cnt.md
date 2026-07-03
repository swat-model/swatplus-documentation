---
title: object.cnt
description: Basin name, areas, and the count of every spatial object type in the project.
status: review
verified_against:
  - src/basin_read_objs.f90
  - src/basin_module.f90
  - src/hydrograph_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`object.cnt` declares the basin name, the landscape and total areas, and how many of each spatial object type (HRU, channel, aquifer, reservoir, and so on) the project contains. The model uses these counts to allocate the `ob`, `obcs`, `obcs_alloc`, and `obom` arrays before any object data is read.

If `object.cnt` is missing or set to `null` in `file.cio`, the model prints `Cannot find object.cnt input file` and stops.

## Source

- Reader: [`src/basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_read_objs.f90)
- Type definitions:
  - [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_module.f90), `type basin_inputs` (`bsn`)
  - [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90), `type spatial_objects` (`sp_ob`)

## Format

- Line 1: title line. Skipped.
- Line 2: header line. Skipped.
- Line 3: 21 values read into `bsn` and `sp_ob`, list-directed.

| # | Field | Maps to | Type | Description |
|---|-------|---------|------|-------------|
| 1 | name | `bsn%name` | char(25) | basin name (free-form) |
| 2 | ls_area | `bsn%area_ls_ha` | real | landscape area, hectares |
| 3 | tot_area | `bsn%area_tot_ha` | real | total area, hectares |
| 4 | objs | `sp_ob%objs` | int | total object count (sum of all object types) |
| 5 | hru | `sp_ob%hru` | int | number of HRUs |
| 6 | hru_lte | `sp_ob%hru_lte` | int | number of HRU-lte objects |
| 7 | ru | `sp_ob%ru` | int | number of routing units |
| 8 | gwflow | `sp_ob%gwflow` | int | number of gwflow cells |
| 9 | aqu | `sp_ob%aqu` | int | number of aquifer objects |
| 10 | chan | `sp_ob%chan` | int | number of legacy channels |
| 11 | res | `sp_ob%res` | int | number of reservoirs |
| 12 | recall | `sp_ob%recall` | int | number of recall objects |
| 13 | exco | `sp_ob%exco` | int | number of export-coefficient objects |
| 14 | dr | `sp_ob%dr` | int | number of delivery-ratio objects |
| 15 | canal | `sp_ob%canal` | int | number of canals |
| 16 | pump | `sp_ob%pump` | int | number of pumps |
| 17 | outlet | `sp_ob%outlet` | int | number of outlets |
| 18 | chandeg | `sp_ob%chandeg` | int | number of SWAT-deg channels (SWAT+ routing) |
| 19 | aqu2d | `sp_ob%aqu2d` | int | 2D aquifer count (currently not used per the type comment) |
| 20 | herd | `sp_ob%herd` | int | herd count (currently not used per the type comment) |
| 21 | wro | `sp_ob%wro` | int | water-rights object count (currently not used per the type comment) |

### gwflow side effect

After reading, if `bsn_cc%gwflow == 1` (set via `codes.bsn`), the reader looks for `gwflow.chancells`. If that file exists and contains river cells, the reader:

- sets `sp_ob%gwflow` to the number of river cells,
- recomputes `sp_ob%objs` to `sp_ob%objs + nriv - sp_ob%aqu`,
- sets `in_con%gwflow_con` to `gwflow.con`,
- sets `sp_ob%aqu` to 0 and `in_con%aqu_con` to `null`.

If `bsn_cc%gwflow == 1` but `gwflow.chancells` is missing or empty, gwflow is silently turned off.

## Example

`refdata/Ames_sub1/object.cnt`:

```
object.cnt:
name                   ls_area      tot_area       obj       hru      lhru       rtu       mfl       aqu       cha       res       rec      exco       dlr       can       pmp       out      lcha     aqu2d       hrd       wro
demo                      1.          1            12         12         0         0         0         0         0         0         0         0         0         0         0         0         0         0         0         0
```

Notes on the example:

- `name = demo`, `ls_area = 1` ha, `tot_area = 1` ha. The fields are floats; the trailing `.` makes that explicit in this dataset.
- `objs = 12` and `hru = 12`. Every spatial object in this project is an HRU.
- The header uses shortened labels (`obj`, `lhru`, `rtu`, `mfl`, `dlr`, `can`, `pmp`, `out`, `lcha`, `hrd`). These are tool conventions; the reader does not parse the header.

## Related files

- [`codes.bsn`](../input-reference/codes-bsn.md). Sets `bsn_cc%gwflow`, which triggers the gwflow side effect above.
- [`file.cio`](../input-reference/file-cio.md). The `simulation` category points to `object.cnt`.
- Object-specific connectivity files (`hru.con`, `chandeg.con`, `aquifer.con`, `reservoir.con`, ...). These must agree with the counts in `object.cnt`.

---
title: object.cnt
description: Basin name, basin areas and the number of spatial objects of each type in the project.
status: review
verified_against:
  - src/basin_read_objs.f90
  - src/basin_module.f90
  - src/hydrograph_module.f90
  - src/hyd_connect.f90
  - src/proc_bsn.f90
  - src/hru_fr_change.f90
  - src/lcu_read_softcal.f90
  - src/basin_aquifer_output.f90
  - src/gwflow_output.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`object.cnt` gives the basin name, the basin areas and the number of spatial objects of each type: HRUs, routing units, aquifers, channels, reservoirs, point sources and the others listed below. SWAT+ uses the counts to set up its list of objects before any connection file is read. The file is named in slot 4 of the `simulation` line of [`file.cio`](file-cio.md) (default `object.cnt`). It is required: if it is missing or `null`, SWAT+ prints `Cannot find object.cnt input file` and stops.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Line 3 contains 21 values in the order below. The reader does not match columns by header name.

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `name` | - | blank | Basin name, up to 25 characters. It appears in the name column of the basin output files. |
| 2 | `ls_area` | ha | 0 | Land area of the basin. |
| 3 | `tot_area` | ha | 0 | Total area of the basin, including reservoirs and other water bodies. |
| 4 | `obj` | count | 0 | Total number of spatial objects. Must equal the sum of columns 5 to 18. |
| 5 | `hru` | count | 0 | Number of HRUs ([`hru.con`](con.md)). |
| 6 | `lhru` | count | 0 | Number of HRU-lte objects ([`hru-lte.con`](../input-reference/con.md)). |
| 7 | `rtu` | count | 0 | Number of routing units ([`rout_unit.con`](../input-reference/con.md)). |
| 8 | `mfl` | count | 0 | Number of gwflow objects ([`gwflow.con`](../input-reference/gwflow.md#gwflowcon)). See [gwflow](#gwflow). |
| 9 | `aqu` | count | 0 | Number of aquifers ([`aquifer.con`](../input-reference/con.md)). |
| 10 | `cha` | count | 0 | Number of legacy channels ([`channel.con`](../input-reference/con.md)). |
| 11 | `res` | count | 0 | Number of reservoirs ([`reservoir.con`](../input-reference/con.md)). |
| 12 | `rec` | count | 0 | Number of recall objects: point sources and inlets ([`recall.con`](../input-reference/con.md)). |
| 13 | `exco` | count | 0 | Number of export coefficient objects ([`exco.con`](../input-reference/con.md)). |
| 14 | `dlr` | count | 0 | Number of delivery ratio objects ([`delratio.con`](../input-reference/con.md)). |
| 15 | `can` | count | 0 | Number of canals. No connection file is read for canals in 62.0.1. |
| 16 | `pmp` | count | 0 | Number of pumps. No connection file is read for pumps in 62.0.1. |
| 17 | `out` | count | 0 | Number of outlets ([`outlet.con`](../input-reference/con.md)). |
| 18 | `lcha` | count | 0 | Number of channels routed with the SWAT+ channel method ([`chandeg.con`](../input-reference/con.md)). |
| 19 | `aqu2d` | count | 0 | Number of 2D aquifers. Read and not used. |
| 20 | `hrd` | count | 0 | Number of herds. Read and not used. |
| 21 | `wro` | count | 0 | Number of water rights objects. Read and not used. |

The column headers are the ones the SWAT+ Editor writes. The old GitBook documentation calls column 8 `gwfl`. Only the order matters to SWAT+.

## Object counts

Each count must match the number of objects in the corresponding connection file named on the `connect` line of [`file.cio`](file-cio.md). SWAT+ numbers all objects in one list, in this order: HRUs, HRU-lte objects, routing units, gwflow objects, aquifers, legacy channels, reservoirs, recall objects, export coefficient objects, delivery ratio objects, canals, pumps, outlets and SWAT+ channels. The object list has `obj` entries, so `obj` must equal the sum of these counts. Counts for canals and pumps reserve places in the list, but no objects are read into them.

If line 3 ends early, the reader reaches the end of the file and the missing counts stay at zero. The `refdata/Osu_1hru` example uses this and leaves out `hrd` and `wro`. If the file has more lines after line 3, SWAT+ keeps reading them in groups of title, header and values, and the last complete group is the one used. A file with a single data line avoids this.

## Basin areas

`ls_area` and `tot_area` are not used to compute HRU or object areas; those come from the connection files. They are used in these places:

- `ls_area`: the HRU area when a decision table changes the fraction of the basin an HRU covers, and the HRU areas of the regions in soft calibration ([`water_balance.sft`](../calibration/soft-calibration.md), see [soft calibration](../calibration/soft-calibration.md)).
- `tot_area`: the area weights for the basin aquifer output (`basin_aqu_*` files), and the conversion of gwflow basin water balance volumes to depths.

## gwflow

When `gwflow = 1` in [`codes.bsn`](codes-bsn.md), SWAT+ looks for [`chancell.gw`](../input-reference/gwflow.md#chancellgw) in the run folder after reading `object.cnt`:

- If [`chancell.gw`](../input-reference/gwflow.md#chancellgw) exists and `mfl` is 0, SWAT+ counts the channel cell rows in [`chancell.gw`](../input-reference/gwflow.md#chancellgw) and uses that count as the number of gwflow objects. It adds that count to `obj`, removes the aquifers from `obj`, sets the aquifer count to 0 and reads the gwflow connections from [`gwflow.con`](../input-reference/gwflow.md#gwflowcon) in place of [`aquifer.con`](../input-reference/con.md).
- If [`chancell.gw`](../input-reference/gwflow.md#chancellgw) exists and `mfl` is already above 0, SWAT+ keeps `mfl` and `obj` as given and sets the aquifer count to 0. In that case `obj` should already leave out the aquifers.
- If [`chancell.gw`](../input-reference/gwflow.md#chancellgw) is missing or has no data after its header, SWAT+ turns gwflow off and the run uses the lumped aquifers.

In all three cases SWAT+ opens the `gwflow_record` log file. See [gwflow](gwflow.md) for the gwflow input files.

## Example

`refdata/Ames_sub1/object.cnt` in the SWAT+ repository:

```
object.cnt:
name                   ls_area      tot_area       obj       hru      lhru       rtu       mfl       aqu       cha       res       rec      exco       dlr       can       pmp       out      lcha     aqu2d       hrd       wro
demo                      1.          1            12         12         0         0         0         0         0         0         0         0         0         0         0         0         0         0         0         0
```

The basin is named `demo` and both areas are 1 ha. The project has 12 objects, all of them HRUs, so `obj` equals `hru`. There are no routing units, aquifers or channels.

`refdata/Osu_1hru/object.cnt` has 4 objects: one HRU, one routing unit, one aquifer and one SWAT+ channel (`lcha`). Its data line stops after `aqu2d`, and the `hrd` and `wro` counts are taken as zero.

## Related files

- [`file.cio`](file-cio.md): names this file and the connection files.
- [Connection files](con.md): one row per object; the number of rows must match the counts here.
- [`codes.bsn`](codes-bsn.md): its `gwflow` code starts the gwflow check above.
- [gwflow](gwflow.md): [`chancell.gw`](../input-reference/gwflow.md#chancellgw) and the other gwflow inputs.

??? quote "Sources"

    - Reader: [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90), called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90) after `codes.bsn`
    - Type definitions: `type basin_inputs` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90), `type spatial_objects` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Object numbering and connection files: [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - Uses of the areas: [`hru_fr_change.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_fr_change.f90), [`lcu_read_softcal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lcu_read_softcal.f90), [`basin_aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_aquifer_output.f90), [`gwflow_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_output.f90)
    - File name slot: `in_sim%object_cnt` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `bsn%name` |
    | `ls_area` | `bsn%area_ls_ha` |
    | `tot_area` | `bsn%area_tot_ha` |
    | `obj` | `sp_ob%objs` |
    | `hru` | `sp_ob%hru` |
    | `lhru` | `sp_ob%hru_lte` |
    | `rtu` | `sp_ob%ru` |
    | `mfl` | `sp_ob%gwflow` |
    | `aqu` | `sp_ob%aqu` |
    | `cha` | `sp_ob%chan` |
    | `res` | `sp_ob%res` |
    | `rec` | `sp_ob%recall` |
    | `exco` | `sp_ob%exco` |
    | `dlr` | `sp_ob%dr` |
    | `can` | `sp_ob%canal` |
    | `pmp` | `sp_ob%pump` |
    | `out` | `sp_ob%outlet` |
    | `lcha` | `sp_ob%chandeg` |
    | `aqu2d` | `sp_ob%aqu2d` |
    | `hrd` | `sp_ob%herd` |
    | `wro` | `sp_ob%wro` |

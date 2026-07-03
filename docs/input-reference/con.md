---
title: "*.con (connectivity files)"
description: Common format for hru.con, chandeg.con, aquifer.con, reservoir.con, rout_unit.con, recall.con, exco.con, delratio.con, outlet.con, gwflow.con, and related connectivity files.
status: review
verified_against:
  - src/hyd_read_connect.f90
  - src/hyd_connect.f90
  - src/hydrograph_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The `.con` files describe the spatial-object topology of the project. Every spatial object (HRU, channel, aquifer, reservoir, routing unit, recall, export coefficient, delivery ratio, outlet, gwflow cell) gets one row in its corresponding `.con` file. The row gives the object its sequential number, name, GIS id, drainage area, location, elevation, parameter pointers, weather station, optional constituent and overbank pointers, and the list of downstream objects that receive its outflow. The model uses these rows to build the routing graph in `hyd_connect`.

Each object type has its own `.con` file but every `.con` file is read by the same routine, `hyd_read_connect`, and is stored in the same array `ob`. The names of the files are listed in `type input_con` in `input_file_module.f90`:

| File | Object type passed to `hyd_read_connect` | Default name |
|------|------------------------------------------|--------------|
| `hru.con` | `hru` | `in_con%hru_con` |
| `hru-lte.con` | `hru_lte` | `in_con%hruez_con` |
| `rout_unit.con` | `ru` | `in_con%ru_con` |
| `gwflow.con` | `gwflow` | `in_con%gwflow_con` |
| `aquifer.con` | `aqu` | `in_con%aqu_con` |
| `channel.con` | `chan` | `in_con%chan_con` |
| `chandeg.con` | `chandeg` | `in_con%chandeg_con` |
| `reservoir.con` | `res` | `in_con%res_con` |
| `recall.con` | `recall` | `in_con%rec_con` |
| `exco.con` | `exco` | `in_con%exco_con` |
| `delratio.con` | `dr` | `in_con%delr_con` |
| `outlet.con` | `outlet` | `in_con%out_con` |

A 13th name, `aquifer2d.con` (`in_con%aqu2d_con`), is declared in `type input_con` but is not currently passed to `hyd_read_connect` from `hyd_connect.f90`.

## Source

- Reader: [`src/hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/main/src/hyd_read_connect.f90)
- Dispatcher: [`src/hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/main/src/hyd_connect.f90) (calls `hyd_read_connect` once per object type)
- Type definition: [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90) (`type object_connectivity`, array `ob`)
- File name pointers: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90) (`type input_con`)

## Format

- Line 1: title. Skipped.
- Line 2: header. Skipped.
- Line 3 and beyond: one record per object. The loop runs from `nspu1` to `nspu1 + nspu - 1`, where `nspu` is the count for this object type taken from `sp_ob` (set in `object.cnt`). The number of rows in the file must equal `nspu`.

Each record has a fixed leading block of 13 fields followed by `out_tot` connection tuples. The reader makes two list-directed reads of the same line: the first pass reads up to `src_tot`, then if `src_tot > 0` the reader backspaces and re-reads with the connection tuples appended.

### Fixed leading block

| # | Column (typical header) | Maps to | Type | Description |
|---|-------------------------|---------|------|-------------|
| 1 | id / NUMB | `ob(i)%num` | int | Object number within this object type. Sequential. Becomes the spatial-object pointer used everywhere else (`hru` column of `hru-data.hru`, channel id in `chandeg.con`, etc). |
| 2 | name / NAME | `ob(i)%name` | char(16) | Object name. Free-form. |
| 3 | gis_id / GIS_ID | `ob(i)%gis_id` | int*8 | GIS identifier from the source watershed delineation. |
| 4 | area / AREA_HA | `ob(i)%area_ha` | real (ha) | Drainage area. For HRU, routing unit, and recall objects this value is also copied into `ob(i)%area_ha_calc`. For other objects `area_ha_calc` is initialized to 0 and is filled in by `hyd_connect` from the routing topology. |
| 5 | lat / LAT | `ob(i)%lat` | real (deg) | Latitude. |
| 6 | lon / LONG | `ob(i)%long` | real (deg) | Longitude. |
| 7 | elev / ELEV | `ob(i)%elev` | real (m) | Elevation. |
| 8 | hru / aqu / lcha / rtu / RECALL | `ob(i)%props` | int | Pointer to the parameter record for this object. For `hru.con` it points into `hru-data.hru`; for `chandeg.con` into the SWAT-deg channel database; for `aquifer.con` into `aquifer.aqu`; and so on. |
| 9 | wst / WST | `ob(i)%wst_c` | char(50) | Weather station name. Resolved by `search(wst_n, db_mx%wst, wst_c, wst)` to the integer `ob(i)%wst` after the record is read. |
| 10 | cst / CONSTIT | `ob(i)%constit` | int | Pointer to constituent data (pesticides, pathogens, metals, salts). `0` means no constituent data. |
| 11 | ovfl / OVERFLOW | `ob(i)%props2` | int | Overbank-connectivity pointer to a landscape unit. `0` means no overbank connection. |
| 12 | rule / RULESET | `ob(i)%ruleset` | char(16) | Name of a decision table in `flo_con.dtl` that controls the outflow fraction. Empty string means no rule. |
| 13 | out_tot / OUT_TOT | `ob(i)%src_tot` | int | Number of downstream (source) connections that follow on this line. May be 0. |

### Per-connection tuple

If `out_tot > 0`, the reader expects `out_tot` groups of four values after column 13, all on the same line:

| Offset | Column (typical header) | Maps to | Type | Description |
|--------|-------------------------|---------|------|-------------|
| +1 | obj_typ / OBTYP_OUT | `ob(i)%obtyp_out(k)` | char(3) | Type of the downstream object. Values used in `hyd_connect`: `hru`, `ru`, `aqu`, `cha`, `sdc` (SWAT-deg channel), `res`, `rec`, `exc`, `dr`, `out`. |
| +2 | obj_id / HTYPNO_OUT | `ob(i)%obtypno_out(k)` | int | Sequential number of the downstream object within its type. |
| +3 | hyd_typ / HTYP_OUT | `ob(i)%htyp_out(k)` | char(3) | Which outflow hydrograph from this object flows to the target. Values include `tot` (total), `rhg` (recharge), `sur` (surface), `lat` (lateral), `til` (tile). The set depends on the source object type; see `type hd_tot` in `hydrograph_module.f90`. |
| +4 | frac / FRAC_OUT | `ob(i)%frac_out(k)` | real | Fraction of that hydrograph routed to the target. The fractions for one source object should sum to 1.0. The reader does not check this. |

If `out_tot == 0`, the reader allocates `ob(i)%obtypno_out(1)` and sets it to 0. No connections are recorded.

### gwflow side effect

After the connection block is read, if `bsn_cc%gwflow == 1` and any of the connections target an aquifer (`obtyp_out(k) == "aqu"`), the reader decrements `ob(i)%src_tot` by 1. The aquifer connection is left in the arrays but `src_tot` no longer counts it. This is part of the gwflow override that replaces standard aquifer routing with grid-cell routing (see [`object.cnt`](../input-reference/object-cnt.md), gwflow side effect).

## Example

`refdata/Osu_1hru/aquifer.con`:

```
aquifer.con: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                gis_id          area           lat           lon          elev       aqu               wst       cst      ovfl      rule   out_tot       obj_typ    obj_id       hyd_typ          frac  
       1  aqu001                   1      10.00000      35.64206     127.38513     322.26395         1    s35610n127290e         0         0         0         1          sdc         1           tot       1.00000  
```

Notes:

- One aquifer object, named `aqu001`, with `area_ha = 10.0` and `out_tot = 1`.
- The single connection sends `tot` (total) outflow from this aquifer to SWAT-deg channel number 1 (`sdc 1 tot 1.00000`), fraction 1.0.

`refdata/Osu_1hru/rout_unit.con` shows a row with `out_tot = 2`:

```
rout_unit.con: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                gis_id          area           lat           lon          elev       rtu               wst       cst      ovfl      rule   out_tot       obj_typ    obj_id       hyd_typ          frac  
       1  rtu001                   1       10.0000      35.52014     127.32787     113.51276         1    s35610n127290e         0         0         0         2           sdc         1           tot       1.00000           aqu         1           rhg       1.00000  
```

The routing unit `rtu001` sends total flow to SWAT-deg channel 1 (fraction 1.0) and recharge flow (`rhg`) to aquifer 1 (fraction 1.0). The two fractions need not sum to 1.0 because they apply to different hydrograph types (`tot` and `rhg`).

`refdata/Ames_sub1/hru.con` is the trivial case with `out_tot = 0` on every row:

```
hru.con: AMES
      id  name                gis_id          area           lat           lon          elev       hru               wst       cst      ovfl      rule   out_tot  
       1  hru0001                  1       1.005           41.20        -96.63         347.5         1            wgn_01         0         0         0         0    
       2  hru0002                  1       1.005           41.20        -96.63         347.5         2            wgn_01         0         0         0         0
```

When `out_tot = 0` the row stops at column 13 and no connection tuples follow. Routing for these HRUs is then expected to be supplied through a separate routing unit definition.

## Related files

- [`object.cnt`](../input-reference/object-cnt.md). Sets `sp_ob%hru`, `sp_ob%chan`, etc, which determine how many rows `hyd_read_connect` expects in each `.con` file.
- [`hru-data.hru`](../input-reference/hru.md). The `hru` column in `hru.con` points into the rows of this file.
- `hru-lte.hru`, `rout_unit.def`, `aquifer.aqu`, `channel.cha`, `chandeg.cha`, `reservoir.res`, `recall.rec`, `exco.exc`, `delratio.del`. Each `.con` file points into one of these property files via the `props` column.
- `flo_con.dtl`. Decision tables named in the `ruleset` column.
- `weather-sta.cli`. Source of the names in the `wst` column.
- `gwflow.chancells`. When `bsn_cc%gwflow == 1`, the aquifer connection is silently dropped from `src_tot` after reading.

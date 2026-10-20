---
title: "*.con (connectivity files)"
description: Common format for hru.con, rout_unit.con, aquifer.con, chandeg.con, reservoir.con, recall.con, exco.con, delratio.con, outlet.con, gwflow.con and hru-lte.con.
status: review
verified_against:
  - src/hyd_read_connect.f90
  - src/hyd_connect.f90
  - src/hydrograph_module.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/command.f90
  - src/hru_hyds.f90
  - src/aqu_1d_control.f90
  - src/hrudb_init.f90
  - src/topohyd_init.f90
  - src/cli_lapse.f90
  - src/cli_staread.f90
  - src/search.f90
  - src/time_control.f90
  - src/et_pot.f90
  - src/dtbl_flocon_read.f90
  - src/exco_read_om.f90
  - src/aqu2d_read.f90
  - src/proc_bsn.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The connect files describe how water and the material it moves travel from one spatial object to the next. Every spatial object (HRU, routing unit, aquifer, channel, reservoir, recall, export coefficient, delivery ratio, outlet, gwflow cell) has one row in the connect file for its object type. The row gives the object its number and name, its area, location and elevation, the record it uses in its property file, its weather station, and the list of objects that receive its outflow. SWAT+ builds the routing network and the order in which objects are run from these rows.

All connect files have the same format. The file names are given on the `connect` line of [`file.cio`](file-cio.md), in this order:

| Position on the `connect` line | Default name | Object | Count column in [`object.cnt`](object-cnt.md) | Property column header | Property file |
|---|---|---|---|---|---|
| 1 | `hru.con` | HRU | `hru` | `hru` | [`hru-data.hru`](hru.md) |
| 2 | `hru-lte.con` | HRU-lte | `lhru` | `hlt` | [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru) |
| 3 | `rout_unit.con` | Routing unit | `rtu` | `rtu` | [`rout_unit.rtu`](../input-reference/units.md#rout_unitrtu) |
| 4 | [`gwflow.con`](../input-reference/gwflow.md#gwflowcon) | gwflow cell | `mfl` | | see [gwflow](gwflow.md) |
| 5 | `aquifer.con` | Aquifer | `aqu` | `aqu` | [`aquifer.aqu`](aqu.md) |
| 6 | `aquifer2d.con` | 2-D aquifer | `aqu2d` | | not read in 62.0.1 |
| 7 | `channel.con` | Channel (legacy) | `cha` | | [`channel.cha`](cha.md) |
| 8 | `reservoir.con` | Reservoir | `res` | `res` | [`reservoir.res`](res.md) |
| 9 | `recall.con` | Recall (point source or inlet) | `rec` | `rec` | [`recall.rec`](recall.md) |
| 10 | `exco.con` | Export coefficient | `exco` | `exc` | [`exco.exc`](../input-reference/recall.md) |
| 11 | `delratio.con` | Delivery ratio | `dlr` | `dlr` | `delratio.del` |
| 12 | `outlet.con` | Outlet | `out` | `out` | none |
| 13 | `chandeg.con` | SWAT-DEG channel | `lcha` | `lcha` | [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha) |

A file is read only when the matching count in [`object.cnt`](../input-reference/object-cnt.md) is above zero. When a count is above zero the file has to exist, because nothing checks for it: a missing file leaves those objects without connection data. The file named in position 6 is never opened in 62.0.1.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one object. SWAT+ reads as many rows as the count for that object type in [`object.cnt`](../input-reference/object-cnt.md). It does not match columns by header name, so every row must give the values below in this order.

Each row has 13 leading values followed by `out_tot` groups of four values that describe the outflow connections, all on the same line.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Object number within its type. Number the rows 1, 2, 3 and so on in file order: the `obj_id` column of other connect files refers to an object by its row position, while SWAT+ uses `id` as the object number during the run. |
| 2 | `name` | - | Object name, up to 16 characters. It appears in the output files and is not used in any calculation. |
| 3 | `gis_id` | - | Object number in the GIS interface. Not used in calculations. The SWAT+ Editor renumbers objects consecutively when it writes the files, so `gis_id` and `id` often differ; use `id` when matching a channel to a stream gauge. |
| 4 | `area` | ha | Area of the object. See [Area, location and elevation](#area-location-and-elevation). |
| 5 | `lat` | decimal degrees | Latitude. |
| 6 | `lon` | decimal degrees | Longitude. Not used in calculations. |
| 7 | `elev` | m | Elevation. |
| 8 | property column (`hru`, `hlt`, `rtu`, `aqu`, `lcha`, `res`, `rec`, `exc`, `dlr`, `out`) | - | Row number in the property file listed in the table above. Called `obj` in earlier documentation. In `recall.con` this column is not used: a recall object uses the [`recall.rec`](../input-reference/recall.md#recallrec) record whose `id` equals the recall object's `id`. |
| 9 | `wst` | - | Weather station name from [`weather-sta.cli`](cli.md). See [Weather station lookup](#weather-station-lookup). |
| 10 | `cst` | - | Constituent pointer. Read but not used. |
| 11 | `ovfl` | - | Overbank flooding pointer. Read but has no effect in 62.0.1. |
| 12 | `rule` | - | Name of a flow-control decision table in [`flo_con.dtl`](../input-reference/dtl.md), or `null`. See [Flow-control rule](#flow-control-rule). |
| 13 | `out_tot` | - | Number of outflow connections that follow on the line. May be 0. |

For each of the `out_tot` connections, four values follow:

| Offset | Column | Units | Description |
|--------|--------|-------|-------------|
| +1 | `obj_typ` | - | Type code of the receiving object. See [Receiving object codes](#receiving-object-codes). |
| +2 | `obj_id` | - | Row number of the receiving object in its connect file. |
| +3 | `hyd_typ` | - | Which outflow hydrograph of this object is sent. See [Hydrograph codes](#hydrograph-codes). |
| +4 | `frac` | fraction | Fraction of that hydrograph sent to the receiving object. |

When `out_tot` is 0 the row ends after column 13 and the object sends no outflow through this file. HRUs that belong to a routing unit are usually written this way, because the routing unit collects their outflow (see [`rout_unit.def`](../input-reference/units.md#rout_unitdef) and [`rout_unit.ele`](../input-reference/units.md#rout_unitele)).

## Area, location and elevation

The `area` value is used in calculations for some object types only:

| Object | Use of `area` |
|--------|---------------|
| HRU | Area of the HRU. Converts depths (mm) to volumes (m³) and loads per hectare to totals. |
| Routing unit | Area of the routing unit. Converts inflow volumes to depths when water is routed across it. |
| Aquifer | Area of the aquifer. Converts recharge, storage and seepage between mm and m³. |
| HRU-lte | Area of the HRU-lte. Converts runoff and sediment to totals. |
| SWAT-DEG channel | Used with [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) to order the channels linked to an aquifer by drainage area, and to express aquifer inflow as a depth in the channel output. See [link files](link.md). |
| Other objects | Not used in calculations. |

At the start of the run SWAT+ also adds up the drainage area of every object from the areas of the HRUs, routing units and recall objects upstream of it, weighted by `frac`, and writes the computed and the input areas to `area_calc.out`. Comparing the two columns in that file is a quick check of the routing.

`elev` is used for every object to adjust precipitation and temperature for the difference in elevation between the object and its weather data. With the lapse rates `plaps` (mm per km) and `tlaps` (°C per km) from [`parameters.bsn`](parameters-bsn.md),

$$\Delta P = \mathrm{plaps}\,\frac{z_{obj} - z_{pcp}}{1000}, \qquad \Delta T = \mathrm{tlaps}\,\frac{z_{tmp} - z_{obj}}{1000}$$

where $z_{obj}$ is `elev` and $z_{pcp}$ and $z_{tmp}$ are the elevations of the precipitation and temperature gauges, or of the weather generator station when the variable is simulated. For HRUs `elev` is also the elevation used to compute atmospheric pressure for potential evapotranspiration, and it can be changed in calibration with the parameter `elev`.

`lat` matters only for HRUs: an HRU with a negative latitude is treated as being in the Southern Hemisphere, and its yearly reset of base heat units and of `skip` operations happens on day 181 instead of 31 December.

## Weather station lookup

The `wst` names are looked up in the list of stations read from [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) with a binary search. The search assumes the stations are listed in ascending order of name (character-code order). If the stations are not in that order, or the name is not in the file, the object uses the first station in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) and no message is written.

## Receiving object codes

`obj_typ` accepts these codes:

| Code | Receiving object | Notes |
|------|------------------|-------|
| `hru` | HRU | Inflow is routed across the HRU. See [Inflow to HRUs and routing units](#inflow-to-hrus-and-routing-units). |
| `hlt` | HRU-lte | |
| `ru` | Routing unit | The routing unit and each HRU in it are registered as receivers. |
| `aqu` | Aquifer | |
| `cha` | Channel in `channel.con` | 62.0.1 does not run these legacy channels, so flow sent to them does not continue downstream. Use `sdc` for SWAT-DEG channels. |
| `res` | Reservoir | |
| `exc` | Export coefficient | Export coefficient objects are not run as part of the routing, so inflow to them has no effect. |
| `dr` | Delivery ratio | The object multiplies its inflow by the ratios in `delratio.del`. |
| `out` | Outlet | |
| `sdc` | SWAT-DEG channel in `chandeg.con` | |

A recall object cannot receive flow. The routing code also has a branch for gwflow cells as receivers, but its code is longer than the three characters `obj_typ` can store, so no value in a connect file can select it. Any other code is not recognised and leaves the connection without a receiving object, which is likely to stop the run.

## Hydrograph codes

`hyd_typ` selects one of the outflow hydrographs of the sending object:

| Code | HRU, HRU-lte, routing unit | Aquifer | Channel, reservoir, recall, outlet, export coefficient, delivery ratio |
|------|----------------------------|---------|-------------------------------------------------|
| `tot` | Surface runoff + lateral flow + tile flow | Return flow (groundwater discharge) | Total outflow |
| `rhg` | Percolation out of the bottom of the soil profile (recharge) | Deep seepage | Not filled, sends nothing |
| `sur` | Surface runoff | not used | not used |
| `lat` | Lateral soil flow | not used | not used |
| `til` | Tile flow | not used | not used |

Any other code is not recognised. The usual connections are `tot` from an HRU or routing unit to a channel together with `rhg` to its aquifer, and `tot` from an aquifer to a channel.

`frac` is not checked. The fractions of one hydrograph type from one object should add up to 1, otherwise water is created or lost. Fractions of different types are independent, which is why a routing unit can send 100% of `tot` to a channel and 100% of `rhg` to an aquifer. Sending both `tot` and one of its parts (`sur`, `lat`, `til`) counts that part twice.

## Inflow to HRUs and routing units

An HRU or routing unit that receives flow keeps surface, lateral and tile inflow separate, so it can route each through the right part of the landscape:

- From another HRU, HRU-lte or routing unit with `tot`, the sender's surface runoff is added to surface runon, its lateral flow to lateral inflow and its tile flow to tile inflow.
- From another HRU, HRU-lte or routing unit with `sur`, `lat` or `til`, that hydrograph goes to surface runon, lateral inflow or tile inflow. An `rhg` connection to an HRU or routing unit is accepted, but the water is not added anywhere.
- From any other object (channel, aquifer, reservoir, recall and so on) the total outflow is added to surface runon, whatever `hyd_typ` says.

For all other receiving objects the selected hydrograph, multiplied by `frac`, is added to the object's inflow.

## Flow-control rule

A `rule` name other than `null` is matched against the decision tables in [`flo_con.dtl`](../input-reference/dtl.md) when the files are read. In 62.0.1 the match is stored but no routine uses it, so `rule` does not change the outflow fractions during the run.

## Export coefficient objects

In `exco.con` the `exc` column is the row number in [`exco.exc`](../input-reference/recall.md). The `om` name in that row selects a row of [`exco_om.exc`](../input-reference/recall.md), and that row becomes the object's outflow hydrograph. It is set once when the files are read and stays constant for the whole run. Send it on with `hyd_typ` `tot`.

## Groundwater flow (gwflow) models

When the gwflow module is active (`gwflow` = 1 in [`codes.bsn`](codes-bsn.md)) and [`object.cnt`](../input-reference/object-cnt.md) lists gwflow cells, any row that has at least one connection with `obj_typ` `aqu` has its connection count reduced by one after reading, because gwflow replaces the aquifer objects. The connection that is dropped is the last one on the line, which is the aquifer connection only when that connection is written last. Put aquifer connections at the end of the line in gwflow models.

## Routing loops

SWAT+ orders the objects so that every object runs after all objects that send it flow. If the connections contain a loop, the ordering cannot finish: after 5000 passes SWAT+ writes the objects that could not be ordered, with their inflow objects, to `looping.con`, prints an error and stops.

## Example

`refdata/Osu_1hru/aquifer.con` in the SWAT+ repository:

```
aquifer.con: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                gis_id          area           lat           lon          elev       aqu               wst       cst      ovfl      rule   out_tot       obj_typ    obj_id       hyd_typ          frac  
       1  aqu001                   1      10.00000      35.64206     127.38513     322.26395         1    s35610n127290e         0         0         0         1          sdc         1           tot       1.00000  
```

One aquifer of 10 ha that uses row 1 of [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) and sends all of its return flow (`tot`) to SWAT-DEG channel 1.

`refdata/Osu_1hru/rout_unit.con`:

```
rout_unit.con: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                gis_id          area           lat           lon          elev       rtu               wst       cst      ovfl      rule   out_tot       obj_typ    obj_id       hyd_typ          frac  
       1  rtu001                   1       10.0000      35.52014     127.32787     113.51276         1    s35610n127290e         0         0         0         2           sdc         1           tot       1.00000           aqu         1           rhg       1.00000  
```

The routing unit sends its surface, lateral and tile flow (`tot`) to SWAT-DEG channel 1 and its recharge (`rhg`) to aquifer 1, each with fraction 1.0. The `rule` value `0` does not name a table in [`flo_con.dtl`](../input-reference/dtl.md), so it has the same effect as `null`.

`refdata/Osu_1hru/hru.con`:

```
hru.con: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                gis_id          area           lat           lon          elev       hru               wst       cst      ovfl      rule   out_tot  
       1  hru0001                  1           10       35.65311     127.36763     350.96629         1    s35610n127290e         0         0         0         0  
```

The HRU has no connections in `hru.con` (`out_tot` = 0). Its outflow reaches the channel and the aquifer through the routing unit it belongs to.

## Related files

- [`object.cnt`](object-cnt.md): number of objects of each type, and so the number of rows read from each connect file.
- [`file.cio`](file-cio.md): names the connect files on its `connect` line.
- [`hru-data.hru`](hru.md), [`aquifer.aqu`](aqu.md), [`reservoir.res`](res.md), [`recall.rec`](recall.md) and the other property files named in the first table.
- [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin): read right after `aquifer.con` to link an aquifer to more than one channel.
- [`weather-sta.cli`](cli.md): station names used in `wst`.
- [Decision tables](dtl.md): [`flo_con.dtl`](../input-reference/dtl.md), named in `rule`.
- [`parameters.bsn`](parameters-bsn.md): lapse rates applied with `elev`.
- [Recall, export coefficient and delivery ratio objects](../model-theory/recall-point-sources.md) in the model theory.

??? quote "Sources"

    - Reader: [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90), called once per object type from [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90), which also resolves receiving objects, hydrograph codes, drainage areas and the run order
    - Type definitions: `type object_connectivity`, `type spatial_objects`, `type object_total_hydrographs` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - File names: `type input_con` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Inflow summing and hydrograph use: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90), [`hru_hyds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_hyds.f90), [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90)
    - Area, elevation and latitude: [`hrudb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hrudb_init.f90), [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90), [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90), [`et_pot.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_pot.f90), [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Weather station lookup: [`search.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/search.f90), station list from [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90)
    - Rule lookup: [`dtbl_flocon_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_flocon_read.f90)
    - Export coefficient hydrographs: [`exco_read_om.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_read_om.f90)
    - `aqu_cha.lin` reader: [`aqu2d_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu2d_read.f90)
    - `area_calc.out` unit opened in [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `id` | `ob(i)%num` |
    | `name` | `ob(i)%name` |
    | `gis_id` | `ob(i)%gis_id` |
    | `area` | `ob(i)%area_ha` |
    | `lat` | `ob(i)%lat` |
    | `lon` | `ob(i)%long` |
    | `elev` | `ob(i)%elev` |
    | property column | `ob(i)%props` |
    | `wst` | `ob(i)%wst_c` (resolved to `ob(i)%wst`) |
    | `cst` | `ob(i)%constit` |
    | `ovfl` | `ob(i)%props2` |
    | `rule` | `ob(i)%ruleset` (resolved to `ob(i)%flo_dtbl`) |
    | `out_tot` | `ob(i)%src_tot` |
    | `obj_typ` | `ob(i)%obtyp_out(k)` |
    | `obj_id` | `ob(i)%obtypno_out(k)` (resolved to `ob(i)%obj_out(k)`) |
    | `hyd_typ` | `ob(i)%htyp_out(k)` (resolved to `ob(i)%ihtyp_out(k)`) |
    | `frac` | `ob(i)%frac_out(k)` |

---
title: Recall and point sources
description: Recall objects, export coefficient objects and delivery ratios, which add measured or estimated loads to the routing network or scale loads from routing units.
status: review
verified_against:
  - src/recall_read.f90
  - src/recalldb_read.f90
  - src/recall_module.f90
  - src/command.f90
  - src/recall_nut.f90
  - src/exco_db_read.f90
  - src/exco_read_om.f90
  - src/exco_module.f90
  - src/dr_ru.f90
  - src/ru_read_elements.f90
  - src/ru_control.f90
  - src/hydrograph_module.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Three object types put water and loads into the routing network without simulating the land surface that produced them, or change how much of a load reaches the next object:

- Recall objects release a time series of flow and loads read from a file: measured inflow at a gauge, a wastewater treatment plant, an industrial discharge, or the output of another model. A negative flow represents a diversion.
- Export coefficient objects release the same daily flow and loads every day of the run.
- Delivery ratios scale the loads leaving the elements of a routing unit, or the loads passing through a delivery ratio object.

Recall, export coefficient and delivery ratio objects are connected to the network through [`recall.con`](../input-reference/con.md), [`exco.con`](../input-reference/con.md) and [`delratio.con`](../input-reference/con.md), like any other spatial object.

## Recall objects

### Input structure

[`recall.rec`](../input-reference/recall.md#recallrec) (the file named in the `recall` line of [`file.cio`](../input-reference/file-cio.md)) lists the recall objects. Each row has an id, a name, a time step code and the name of the data file:

| Code | Data file content | Value used each day |
|---|---|---|
| 0 | sub-daily values | the values of the day's time steps |
| 1 | daily values | the value of the day |
| 2 | monthly values | the value of the month, on every day of that month |
| 3 | annual values | the value of the year, on every day of that year |
| 4 | none; the file name is the name of an export coefficient record | the export coefficient record |

Each data file has a title line, a line with the number of years, a column header, and one row per day, month or year: day of year, month, day of month, year, object type, object name, and then the hydrograph values

`flo sed orgn sedp no3 solp chla nh3 no2 cbod dox sand silt clay sag lag gravel temp`

in m³ for flow, metric tons for sediment and its classes, kg for nutrients, chlorophyll-a, CBOD and oxygen, and °C for temperature. The values are daily amounts, also in monthly and annual files: a monthly value is released on every day of the month, so it must be the daily amount for that month.

Rows before the simulation start year are skipped, and reading stops after the simulation end year.

### Daily release

On each day inside the period covered by its file, a recall object sends the stored values for that day, month or year to the objects listed in [`recall.con`](../input-reference/con.md). Outside that period a daily or monthly recall object releases nothing.

When a daily value has negative flow, the object takes water out of the network (a diversion). Nutrients are then removed in proportion to the diverted volume at the concentration of the source, as are salts and constituents when they are simulated.

### Salts, constituents and pesticides

Salt and constituent loads for recall objects are read from separate salt and constituent recall files (see [Salts and constituents](salts-constituents.md)). Pesticide loads for recall objects are read from `pest.com` when that file is present.

### Recall database

[`recall_db.rec`](../input-reference/recall.md#recall_dbrec) is a separate index that names, for each source, the organic-mineral, pesticide, pathogen, heavy metal, salt and constituent data. Water allocation uses it to set the quality of water from outside sources, treatment plants and water uses, and reservoir release tables use it to find measured releases.

## Export coefficient objects

[`exco.exc`](../input-reference/recall.md) lists the export coefficient objects. Each row has a name followed by the names of its records in the organic-mineral ([`exco_om.exc`](../input-reference/recall.md)), pesticide, pathogen, heavy metal and salt files. Each row of [`exco_om.exc`](../input-reference/recall.md) has a name followed by the same hydrograph values as a recall file.

The hydrograph of an export coefficient object is set once at the start of the run and released unchanged every day, so the values in [`exco_om.exc`](../input-reference/recall.md) are daily amounts. An export coefficient can also be an element of a routing unit, in which case the routing unit's delivery ratio is applied to it.

## Delivery ratios

### Routing unit elements

Each element of a routing unit (an HRU, an HRU-lte, a channel or another routing unit) has a delivery ratio named in the `dlr` column of [`rout_unit.ele`](../input-reference/units.md#rout_unitele). The ratio multiplies the flow and loads the element contributes to the routing unit outflow.

| `dlr` value | Ratio |
|---|---|
| `calc` or `0` | Flow is delivered in full. Sediment and nutrients are multiplied by $\min\left(1,\;\sqrt{t_{c,elem}/t_{c,ru}}\right)$, the square root of the ratio of the element's time of concentration to the routing unit's, for HRU and HRU-lte elements. For `sdc` channel and routing unit elements the ratio is 1. Other element types, including legacy channels, take the ratio last calculated for an earlier element (0 if there is none). |
| `full` or `1` | Everything is delivered in full. |
| any other value | 0 for every variable, so the element delivers only its recharge. This includes the name of a [`delratio.del`](../input-reference/con.md) record: the names are looked up before [`delratio.del`](../input-reference/con.md) is read, so none is found. |

The details are on [Routing and landscape units](../input-reference/units.md#delivery-ratio).

Pesticide loads from routing unit elements are not scaled by the delivery ratio.

### Delivery ratio objects

A delivery ratio object placed in the routing network multiplies all of its incoming hydrograph by the ratios of its [`delratio.del`](../input-reference/con.md) record and passes the result on.

## Related pages

- [Recall inputs](../input-reference/recall.md) and [connection files](../input-reference/con.md)
- [Channels](channels.md) and [Reservoirs and wetlands](reservoirs-wetlands.md) for receiving objects
- [Water allocation](../input-reference/water-allocation.md)
- [Salts and constituents](salts-constituents.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Recall objects: [`src/recall_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read.f90) (reads `recall.rec`, the data files and `pest.com`); daily release in the `recall` case of [`src/command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90); diversions: [`src/recall_nut.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_nut.f90), [`src/recall_salt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_salt.f90), [`src/recall_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_cs.f90)
    - Recall database: [`src/recalldb_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recalldb_read.f90), type in [`src/recall_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_module.f90)
    - Export coefficients: [`src/exco_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_db_read.f90), [`src/exco_read_om.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_read_om.f90), type in [`src/exco_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_module.f90)
    - Delivery ratios: [`src/dr_ru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_ru.f90), [`src/ru_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_read_elements.f90), [`src/ru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_control.f90), [`src/dr_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_db_read.f90)
    - Hydrograph fields: `hyd_output` in [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)

    Variables:

    | Item | Variable |
    |---|---|
    | recall time step code, file, first and last year | `recall%typ`, `%filename`, `%start_yr`, `%end_yr` |
    | stored values | `recall%hd(day or month or 1, year)`, sub-daily flow in `recall%hyd_flo` |
    | `exco.exc` row | `exco_db` (`name`, `om_file`, `pest_file`, `path_file`, `hmet_file`, `salts_file`) |
    | `exco_om.exc` row | `exco_om_name`, `exco` (type `hyd_output`) |
    | element delivery ratio | `ru_elem%dr_name`, `ru_elem%dr` |

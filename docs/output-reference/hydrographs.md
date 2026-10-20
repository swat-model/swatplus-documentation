---
title: Hydrograph outputs
description: The hydin, hydout, deposition and ru files, which report water, sediment and nutrient loads passed between objects, and the hydcon.out connection list.
status: review
verified_against:
  - src/header_hyd.f90
  - src/header_write.f90
  - src/header_cs.f90
  - src/hydrograph_module.f90
  - src/hydin_output.f90
  - src/hydout_output.f90
  - src/hyddep_output.f90
  - src/ru_output.f90
  - src/ru_control.f90
  - src/hyd_connect_out.f90
  - src/hyd_connect.f90
  - src/hru_control.f90
  - src/hru_hyds.f90
  - src/rls_routesurf.f90
  - src/command.f90
  - src/proc_open.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

SWAT+ moves water and its loads between objects (HRUs, routing units, channels, reservoirs, aquifers and so on) as hydrographs: a record of water volume, sediment, nutrients and temperature for the day. The files on this page report those hydrographs.

| File | One row per | Content |
|------|-------------|---------|
| `hydout_*` | object and outgoing connection | What each object sends to each receiving object. |
| `hydin_*` | object and incoming connection | What each object receives from each source object. |
| `deposition_*` | HRU or routing unit that receives inflow | Material deposited from incoming water. |
| `ru_*` | routing unit | Sum of the hydrographs of the routing unit's elements. |
| `hydcon.out` | object | The routing order and connections, written once at the start of the run. |

`hydin`, `hydout` and `deposition` are switched on by the `hyd` row of [`print.prt`](../input-reference/print-prt.md), and `ru` by the `ru` row. Each `y` in the `daily`, `monthly`, `yearly` or `avann` column opens the `_day`, `_mon`, `_yr` or `_aa` file. `hydcon.out` is switched on by `hydcon` on the line after `csvout`. With `csvout` set to `y`, a `.csv` copy of each file is written as well.

The connections themselves are defined in the connection files (see [connection files](../input-reference/con.md)): each object lists the objects it sends water to, the hydrograph type it sends and the fraction.

## Hydrograph columns

All four time-step file groups end with the same 18 columns:

| Column | Units | Description |
|--------|-------|-------------|
| `flo` | m³ | Volume of water. |
| `sed` | tons | Sediment. |
| `orgn` | kg N | Organic nitrogen. |
| `sedp` | kg P | Organic (sediment-attached) phosphorus. |
| `no3` | kg N | Nitrate. |
| `solp` | kg P | Soluble mineral phosphorus. |
| `chla` | kg | Chlorophyll a. |
| `nh3` | kg N | Ammonium. |
| `no2` | kg N | Nitrite. |
| `cbod` | kg | Carbonaceous biochemical oxygen demand. |
| `dox` | kg | Dissolved oxygen. |
| `san` | tons | Sand. |
| `sil` | tons | Silt. |
| `cla` | tons | Clay. |
| `sag` | tons | Small aggregates. |
| `lag` | tons | Large aggregates. |
| `grv` | tons | Gravel. |
| `null` | °C | Water temperature. |

`flo` is a volume: m³ per day in the daily file, the total for the month or year in the monthly and yearly files, and the average yearly total in the average annual file. The units row of the files gives m³/s for `flo`. To convert a daily value to an average rate, divide by 86,400.

All other loads are totals for the step in the same way. The last column is headed `null` and is the water temperature; monthly, yearly and average annual values are flow-weighted averages.

## hydout files

| # | Column | Description |
|---|--------|-------------|
| 1 | `jday` | Day of the year of the last day in the print step. |
| 2 | `mon` | Month. |
| 3 | `day` | Day of the month. |
| 4 | `yr` | Calendar year. |
| 5 | `name` | Name of the source object. |
| 6 | `type` | Object type of the source object (`hru`, `hru_lte`, `ru`, `aqu`, `chandeg`, `res`, `recall`, `exco`, `dr`, `outlet`). |
| 7 | `objtyp` | Type code of the receiving object, as in the connection file (`hru`, `ru`, `aqu`, `sdc`, `res` and so on). |
| 8 | `typ_no` | Number of the receiving object within its type. |
| 9 | `hyd_typ` | Hydrograph type sent: `tot` (total), `rhg` (recharge), `sur` (surface runoff), `lat` (lateral flow) or `til` (tile flow). |
| 10 | `fraction` | Fraction of that hydrograph sent to this receiving object. |
| 11 to 28 | `flo` to `null` | The hydrograph sent, already multiplied by `fraction`. |

An object with three outgoing connections has three rows per print step. The rows of all objects follow the routing order, so the rows of one step are not sorted by object name.

## hydin files

The columns are those of `hydout`, seen from the receiving side:

| # | Column | Description |
|---|--------|-------------|
| 5 | `name` | Name of the receiving object. |
| 6 | `type` | Object type of the receiving object. |
| 7 | `objtyp` | Type code of the source object. |
| 8 | `typ_no` | Number of the source object within its type. |
| 9 | `hyd_typ` | Hydrograph type received. |
| 10 | `fraction` | Fraction of the source hydrograph received. |
| 11 to 28 | `flo` to `null` | The hydrograph received. |

Rows are written for every incoming connection, but values are filled only when the receiving object is not an HRU, HRU-LTE or routing unit. For those three receiving types the incoming water is split into surface, lateral and tile parts and routed inside the object, and the `hydin` rows stay zero. Use the `hydout` rows of the source object instead.

`hydin_yr.csv` has one more column than the other `hydin` files: the object number is written after `type`, so the later columns are shifted by one against the header.

## deposition files

`deposition_*` has `jday`, `mon`, `day`, `yr`, `name` and `type`, then the 18 hydrograph columns. It has a row for every HRU and routing unit that receives water from another object.

- For an HRU without a wetland, the `sed` column is the sediment deposited on the HRU from incoming surface runoff, in tons: the incoming sediment above the transport capacity of the runoff over the HRU. The other columns are zero.
- For an HRU with a wetland or rice paddy, incoming surface runoff and tile flow go into the wetland, and the row shows that inflow. In this case `flo` is in mm and the loads are per hectare.
- For a routing unit, the row shows the hydrograph of the last element processed in the routing unit. It does not measure deposition.

The deposition files are written from the start of the simulation, including the `nyskip` warm-up years, while the average annual value is divided by the number of printed years only.

## ru files

`ru_*` has `jday`, `mon`, `day`, `yr`, `name` and `type`, then the 18 hydrograph columns, with one row per routing unit.

Each value is the sum, over the elements of the routing unit, of every hydrograph type the element produces. For an HRU element that is the total hydrograph plus its recharge, surface, lateral and tile hydrographs, so `flo` and the loads are larger than the routing unit's outflow. The outflow of a routing unit is in the `hydout` rows of the routing unit, with `hyd_typ` `tot` for the total flow.

## hydcon.out

`hydcon.out` has no title or header line. It lists the objects in the order SWAT+ processes them, one line per object:

| Field | Description |
|-------|-------------|
| 1 | Sequence number in the routing order. |
| 2 | Object name. |
| 3 | Object type. |
| 4 | Number of the object's properties record in its data file. |
| 5 | Overbank connection pointer to landscape units (0 when none). |
| 6 | Number of outgoing connections. |
| 7 | Number of incoming connections. |
| 8 and on | For each outgoing connection: the receiving object numbers, the receiving type code, its number within the type and the hydrograph type. |

In 62.0.1 the receiving object numbers are written as the full list of all receiving objects for every outgoing connection, so lines for objects with more than one outgoing connection repeat that list.

## Constituent hydrographs

[`print.prt`](../input-reference/print-prt.md) and the source refer to hydrograph files for pesticides, pathogens, metals and salts (`hydin_pests_*`, `hydout_salts_*` and so on). SWAT+ 62.0.1 does not write them.

## Print timing

`hydin`, `hydout` and `ru` start after the `nyskip` warm-up years. Daily rows follow the daily print window and `interval` in [`print.prt`](../input-reference/print-prt.md). `deposition` is written from the first simulated year, as described above.

## Example

The column names of `hydout_day.txt` and `hydin_day.txt`:

```
jday  mon  day  yr  name  type  objtyp  typ_no  hyd_typ  fraction
flo  sed  orgn  sedp  no3  solp  chla  nh3  no2  cbod  dox  san  sil  cla  sag  lag  grv  null
```

A `hydout` row for an HRU sending 60% of its total flow to a routing unit has `type` `hru`, `objtyp` `ru`, `hyd_typ` `tot` and `fraction` 0.6, and its `flo` is 0.6 times the HRU's water yield in m³.

## Related files

- [`print.prt`](../input-reference/print-prt.md): the `hyd`, `ru` and `hydcon` switches.
- [Connection files](../input-reference/con.md): the connections these files report.
- [Recall outputs](recall.md): point source and inlet hydrographs, in the same column layout.
- [Channel and sediment outputs](channel-sediment-nutrient.md): channel inflow and outflow as rates.
- [Output naming convention](naming-convention.md): all output files.

??? quote "Sources"

    - File opening and headers: [`header_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_hyd.f90) (`hydin`, `hydout`, `deposition`, `hydcon.out`), [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90) (`ru`)
    - Header types: `hyd_header`, `hyd_header_time`, `hyd_header_obj`, `hyd_header_units`, `hyd_header_units2` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Writers: [`hydout_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydout_output.f90), [`hydin_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydin_output.f90), [`hyddep_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyddep_output.f90), [`ru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_output.f90), [`hyd_connect_out.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect_out.f90)
    - Values: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90) (incoming and outgoing hydrographs), [`ru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_control.f90), [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`rls_routesurf.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rls_routesurf.f90), [`hru_hyds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_hyds.f90)
    - Hydrograph type codes: [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `type` | `ob(icmd)%typ` |
    | `objtyp`, `typ_no`, `hyd_typ`, `fraction` (`hydout`) | `ob(icmd)%obtyp_out(iout)`, `obtypno_out`, `htyp_out`, `frac_out` |
    | `objtyp`, `typ_no`, `hyd_typ`, `fraction` (`hydin`) | `ob(icmd)%obtyp_in(iin)`, `obtypno_in`, `htyp_in`, `frac_in` |
    | hydrograph (`hydout`) | `ht1 = frac_out * ob(icmd)%hd(ihtyp_out)` |
    | hydrograph (`hydin`) | `ob(icmd)%hin_d(iin)` and the `hin_m`, `hin_y`, `hin_a` sums |
    | hydrograph (`deposition`) | `ht1` after `hru_control` or `ru_control`, summed into `ob(icmd)%hdep_m`, `hdep_y`, `hdep_a` |
    | hydrograph (`ru`) | `ru_d(iru)` and the `ru_m`, `ru_y`, `ru_a` sums |
    | `null` | `hyd_output%temp` |

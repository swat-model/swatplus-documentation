---
title: "Routing and landscape units"
description: rout_unit.def, rout_unit.ele and rout_unit.rtu define routing units and their elements; ls_unit.def and ls_unit.ele group HRUs into landscape units and the basin for output; aqu_catunit.ele switches on the basin aquifer output.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/main.f90.in
  - src/hyd_connect.f90
  - src/hyd_read_connect.f90
  - src/hydrograph_module.f90
  - src/ru_module.f90
  - src/ru_read.f90
  - src/ru_read_elements.f90
  - src/define_unit_elements.f90
  - src/ru_control.f90
  - src/dr_ru.f90
  - src/dr_db_read.f90
  - src/time_conc_init.f90
  - src/unit_hyd_ru_hru.f90
  - src/command.f90
  - src/lsu_read_elements.f90
  - src/calibration_data_module.f90
  - src/lsu_output.f90
  - src/lsu_carbon_output.f90
  - src/basin_output.f90
  - src/basin_sw_init.f90
  - src/time_control.f90
  - src/output_landscape_init.f90
  - src/lcu_read_softcal.f90
  - src/hru_fr_change.f90
  - src/actions.f90
  - src/gwflow_rech.f90
  - src/gwflow_gwet.f90
  - src/proc_cal.f90
  - src/aqu_read_elements.f90
  - src/basin_aquifer_output.f90
  - src/header_write.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A routing unit collects the outflow of a group of objects, usually the HRUs of one landscape unit, and routes the sum as a single object. Its row in [`rout_unit.con`](con.md) sends the result on, typically the total flow to a channel and the recharge to an aquifer. Three files describe routing units: `rout_unit.def` lists the elements of each unit, `rout_unit.ele` describes each element, and `rout_unit.rtu` gives each unit its topography and field records.

A landscape unit is a group of HRUs used only for output. `ls_unit.def` lists the elements of each landscape unit and `ls_unit.ele` gives each element its area fractions. The same element file also weights the HRUs in the basin output files. `aqu_catunit.ele` lists aquifer elements; in 62.0.1 its only effect is to switch on the data rows of the basin aquifer output.

The files are named in [`file.cio`](file-cio.md#categories-and-default-file-names):

| File | [`file.cio`](../input-reference/file-cio.md) line | Slot | Read |
|------|-----------------|------|------|
| `rout_unit.def` | `routing_unit` (line 8) | 1 | when the `rtu` count in [`object.cnt`](object-cnt.md) is above 0 |
| `rout_unit.ele` | `routing_unit` (line 8) | 2 | when the `rtu` count is above 0 |
| `rout_unit.rtu` | `routing_unit` (line 8) | 3 | when the `rtu` count is above 0 |
| `ls_unit.ele` | `regions` (line 26) | 1 | every run |
| `ls_unit.def` | `regions` (line 26) | 2 | every run |
| `aqu_catunit.ele` | `regions` (line 26) | 9 | every run, with the calibration inputs |

Slot 4 of the `routing_unit` line (`rout_unit.dr`) is read from [`file.cio`](../input-reference/file-cio.md) but never opened.

All six files are free format and whitespace-separated. The readers take the values in column order and do not check the header names.

For `rout_unit.rtu`, a name of `null` or a name that does not exist in the run folder means the file is not read. The other five files are skipped when the name is `null`. When the name is not `null` and the file does not exist, SWAT+ creates an empty file of that name in the run folder, reads nothing from it, and continues as if the name were `null`. What a missing file means for the run is given under each file.

## rout_unit.def

### Format

Line 1 is a title and line 2 is the column header; both are skipped. Each later line defines one routing unit. The line ends with a list of element numbers, and only the first number of that list has a header.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Number of the routing unit. Not used: the rows are taken in order, so row $n$ defines routing unit $n$. |
| 2 | `name` | - | Name of the routing unit. Not used. |
| 3 | `elem_tot` | - | Number of values in the element list that follows. When the list uses ranges, this is smaller than the number of elements. |
| 4 and on | `elements` | - | Element list: `id` values of rows in `rout_unit.ele`, written as described under [Element lists](#element-lists). |

### Element lists

`rout_unit.def` and `ls_unit.def` use the same list format. Each value is an element number, and a negative value closes a range that starts at the value before it. The list `1 -4 7` therefore means elements 1, 2, 3, 4 and 7, and `elem_tot` is 3 because the list has three values. A list with a single value gives one element. An `elem_tot` of 0 gives a unit with no elements.

A negative value must follow a positive one. Two negative values in a row, or a negative first value in a list of more than one value, put negative element numbers into the list.

### Behaviour

- Routing unit $n$ is the routing unit whose `id` in [`rout_unit.con`](../input-reference/con.md) is $n$. It uses row $n$ of `rout_unit.def`, counted from the first data line, whatever the `id` column says. SWAT+ reads as many rows as the `rtu` count in [`object.cnt`](../input-reference/object-cnt.md). Extra rows are ignored, and units without a row have no elements.
- The `define` column of `rout_unit.rtu` is not used to find the row. The routing unit ids in [`rout_unit.con`](../input-reference/con.md), the rows of `rout_unit.def` and the ids in `rout_unit.rtu` therefore have to run 1, 2, 3 in the same order. The SWAT+ Editor writes them that way.
- An object can be an element of one routing unit only. If two element rows of `rout_unit.ele` point to the same object and both are listed in `rout_unit.def` (in one unit or in two), SWAT+ stops at start-up with an allocation error.
- A routing unit with no elements produces no outflow, and no message is written.
- If `rout_unit.def` is missing or `null` in a project with routing units, every routing unit has no elements. The HRUs then reach the rest of the model only through their rows in [`hru.con`](../input-reference/con.md), and an HRU without outflow connections there loses its water.

### Example

`refdata/Osu_1hru/rout_unit.def` in the SWAT+ repository:

```
rout_unit.def: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id              name  elem_tot  elements  
       1             rtu001         1      1      
```

Routing unit 1 has one element, element 1 of `rout_unit.ele`.

## rout_unit.ele

### Format

Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one element.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Element number, used in the element lists of `rout_unit.def`. The rows can be in any order and the numbers do not have to be consecutive; the largest `id` sets the size of the table. |
| 2 | `name` | - | Name of the element. Not used. |
| 3 | `obj_typ` | - | Object type of the element, one of the codes below. |
| 4 | `obj_id` | - | Number of the object within its type: its `id` in the connection file of that type. |
| 5 | `frac` | fraction | Fraction of the element in the routing unit, used to scale the element's outflow. See [Expansion factor](#expansion-factor). |
| 6 | `dlr` | - | Delivery ratio: `0` or `calc`, `1` or `full`. See [Delivery ratio](#delivery-ratio). |

The object type codes SWAT+ recognises are:

| `obj_typ` | Object | Connection file |
|-----------|--------|-----------------|
| `hru` | HRU | [`hru.con`](../input-reference/con.md) |
| `hlt` | HRU-lte | [`hru-lte.con`](../input-reference/con.md) |
| `ru` | routing unit | [`rout_unit.con`](../input-reference/con.md) |
| `cha` | legacy channel | [`channel.con`](../input-reference/con.md) |
| `sdc` | SWAT+ channel | [`chandeg.con`](../input-reference/con.md) |
| `res` | reservoir | [`reservoir.con`](../input-reference/con.md) |
| `exc` | export coefficient | [`exco.con`](../input-reference/con.md) |
| `dr` | delivery ratio | [`delratio.con`](../input-reference/con.md) |
| `out` | outlet | [`outlet.con`](../input-reference/con.md) |

Any other code, including `aqu`, `rec` and `rtu`, is not recognised. No message is written, and the element is linked to object 1, the first object in the model (HRU 1 in a model with HRUs). Earlier documentation listed aquifers, recall objects and "another rtu" as possible elements; in 62.0.1 a routing unit inside a routing unit has the code `ru`.

### Expansion factor

Each day a routing unit adds up the hydrographs of its elements. Each element's hydrographs are multiplied by an expansion factor $e$ before they are added:

- HRU and HRU-lte elements with `frac` below 0.99999:

    $$e = \mathrm{frac}\;\frac{A_{ru}}{A_{obj}}$$

    where $A_{ru}$ is the routing unit's `area` in [`rout_unit.con`](../input-reference/con.md) and $A_{obj}$ the HRU's `area` in its connection file. When `frac` is the HRU's share of the routing unit area, $e$ is 1 and the whole HRU outflow is added.
- HRU and HRU-lte elements with `frac` of 0.99999 or more: $e = 1$, so the whole HRU outflow is added whatever the areas.
- Export coefficient elements: $e$ as for HRUs when the export coefficient object has an area above 0.01 ha, otherwise 1.
- All other elements: $e = \mathrm{frac}$, the fraction of the object's outflow that enters the routing unit.

The `frac` values are not checked. If they do not add up as intended, the routing unit outflow is scaled accordingly.

The factor and the delivery ratio apply to the total, surface, lateral and tile hydrographs. The recharge hydrograph is multiplied by the factor only. Pesticide, salt and constituent loads are added in full: 62.0.1 applies neither the expansion factor nor the delivery ratio to them.

When another object sends flow to a routing unit through its connection file, the inflow is shared among the unit's elements. Each element receives the sender's fraction multiplied by its `frac`. How an HRU uses that inflow is described under [Inflow to HRUs and routing units](con.md#inflow-to-hrus-and-routing-units).

### Delivery ratio

The `dlr` column sets a ratio for each hydrograph variable of the element:

| `dlr` | Ratio |
|-------|-------|
| `0` or `calc` | Flow 1. All other variables (sediment, nutrients, chlorophyll-a, CBOD, dissolved oxygen, sediment size classes) are multiplied by a calculated ratio, given below. |
| `1` or `full` | 1 for every variable. |
| any other value | 0 for every variable. |

For HRU and HRU-lte elements the calculated ratio is

$$DR = \min\left(1,\ \sqrt{\frac{t_{c,\mathrm{elem}}}{t_{c,ru}}}\right)$$

where $t_{c,\mathrm{elem}}$ is the HRU's time of concentration (see [Surface runoff lag](../model-theory/hydrology.md#surface-runoff-lag)), or for an HRU-lte the time of concentration of its [`hru-lte.hru`](../input-reference/hru-lte.md#hru-ltehru) record, and $t_{c,ru}$ is the routing unit's time of concentration (see [Time of concentration](#time-of-concentration)). For `sdc` and `ru` elements the calculated ratio is 1. For the other element types no ratio is calculated, and the element takes the ratio last calculated for an earlier element (0 if there is none).

A `dlr` value that names a record in [`delratio.del`](../input-reference/con.md) does not work in 62.0.1. The names are looked up when the routing units are set up, and [`delratio.del`](../input-reference/con.md) is read only after that, so no name is ever found. The ratio then stays at 0 for every variable, and the element contributes only its recharge hydrograph. The same happens for any other value, such as `null`. Use `0`, `calc`, `1` or `full`. The SWAT+ Editor writes `0`.

The decision table action `hru_fr_update` (see [decision tables](dtl.md#land-use-and-management-actions)) reads a replacement `rout_unit.ele` during the run. By then [`delratio.del`](../input-reference/con.md) has been read, so a `dlr` that names a [`delratio.del`](../input-reference/con.md) record does take that record's ratios from `dr_om.del`. Elements whose `dlr` is `0`, `calc`, `1`, `full` or an unknown name keep the ratios they had before.

### Behaviour

- `rout_unit.ele` is required in a project with routing units. If it is missing or `null`, the routing unit tables are never set up and the run fails during start-up.
- In sub-daily runs (time step below one day) with Green and Ampt infiltration (`gampt` = 1 in [`codes.bsn`](codes-bsn.md)), the routing unit's sub-daily flow is set from each HRU element in turn, so only the last HRU element in the list is kept, and the result is shifted by a fixed 2 hours instead of the routing unit's time of concentration.
- The `ru` row of [`print.prt`](print-prt.md#output-group-rows) writes the sum of the element hydrographs of each routing unit to the `ru_*` files (see [ru files](../output-reference/hydrographs.md#ru-files)).

### Example

`refdata/Osu_1hru/rout_unit.ele`:

```
rout_unit.ele: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                   obj_typ    obj_id          frac               dlr  
       1  hru0001                    hru         1            1                 0  
```

Element 1 is HRU 1. With `frac` = 1 the whole HRU outflow enters the routing unit. With `dlr` = 0 the water is delivered in full, and sediment and nutrients are multiplied by the calculated delivery ratio.

## rout_unit.rtu

### Format

Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one routing unit.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Number of the routing unit. Routing unit $n$ (the `id` in [`rout_unit.con`](../input-reference/con.md)) uses the row whose `id` is $n$. The ids must lie between 1 and the `rtu` count in [`object.cnt`](../input-reference/object-cnt.md). An `id` of 0 ends the file. |
| 2 | `name` | - | Name of the routing unit. Not used. |
| 3 | `define` | - | Name of the `rout_unit.def` row. Not used: routing unit $n$ always uses row $n$ of `rout_unit.def`. |
| 4 | `dlr` | - | Delivery ratio of the routing unit. Not used; delivery ratios are set per element in `rout_unit.ele`. |
| 5 | `topo` | - | Name of a record in [`topography.hyd`](hyd.md#topographyhyd). Its slope and slope length are used for the routing unit's time of concentration. |
| 6 | `field` | - | Name of a record in [`field.fld`](hyd.md#fieldfld). Its field length is used for the routing unit's time of concentration. |

### Time of concentration

The routing unit's time of concentration is the sum of an overland flow time and a channel flow time:

$$t_{ov} = \frac{0.0556\,(L_{slp}\,n)^{0.6}}{(slp + 0.001)^{0.3}}, \qquad t_{ch} = \frac{0.62\,L\,n^{0.75}}{A^{0.125}\,\left(0.5\,(slp + 0.001)\right)^{0.375}}, \qquad t_{c,ru} = t_{ov} + t_{ch}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $t_{ov}$, $t_{ch}$, $t_{c,ru}$ | overland, channel and total time of concentration | hr |
| $L_{slp}$ | slope length, `slp_len` of the `topo` record | m |
| $slp$ | average slope, `slp` of the `topo` record | m/m |
| $L$ | channel length, `len` of the `field` record divided by 1000 | km |
| $A$ | routing unit area, `area` in [`rout_unit.con`](../input-reference/con.md) | km² |
| $n$ | Manning's n for overland flow, averaged over the HRU elements | - |

The Manning's n is the area-weighted mean of the `ov_mann` values of the HRU elements' land uses (see [`landuse.lum`](lum.md)):

$$n = \frac{\sum_i n_i\,A_i}{A}$$

where $A_i$ is the full area of HRU element $i$; `frac` is not used. When the routing unit has an element that is not an HRU, the running sum is set to 0.1 at that element and the HRU elements after it are added to 0.1. The result then depends on the order of the elements.

The time of concentration is used for the calculated delivery ratio of the elements and, in sub-daily runs, for the unit hydrograph of the routing unit.

### Behaviour

- A `topo` name that is `null` or not found in [`topography.hyd`](../input-reference/hyd.md#topographyhyd) gives the first record of that file. A `field` name that is `null` or not found gives the built-in field length of 500 m. No message is written in either case.
- `rout_unit.rtu` is required in a project with routing units. If it is missing or `null`, no routing unit records are set up and the run fails during start-up.

### Example

`refdata/Osu_1hru/rout_unit.rtu`:

```
rout_unit.rtu: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id              name            define               dlr              topo             field  
       1            rtu01             rtu001              null        toportu011            fld011  
```

`fld011` is in [`field.fld`](../input-reference/hyd.md#fieldfld) with a length of 500 m. `toportu011` is not in this dataset's [`topography.hyd`](../input-reference/hyd.md#topographyhyd), so the routing unit uses its first record, `topohru0001` (slope 0.01078, slope length 10 m), without a message. `define` and `dlr` have no effect.

## ls_unit.def

### Format

Line 1 is a title, line 2 gives the number of landscape units, and line 3 is the column header. Each later line defines one landscape unit, and the line ends with an element list as in `rout_unit.def`.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Number of the landscape unit. Not used: row $n$ defines landscape unit $n$. |
| 2 | `name` | - | Name of the landscape unit, written in the `name` column of the landscape unit output files. |
| 3 | `area` | ha | Area of the landscape unit. Not used. |
| 4 | `elem_tot` | - | Number of values in the element list. 0 gives a landscape unit with no elements, whose output is all zeros. |
| 5 and on | `elements` | - | Element list: `id` values of rows in `ls_unit.ele`, written as described under [Element lists](#element-lists). |

SWAT+ reads as many rows as line 2 gives.

### Behaviour

- Landscape units are used for output only. Each one gets a row in the `lsunit_wb`, `lsunit_nb`, `lsunit_ls` and `lsunit_pw` files and in the landscape unit carbon files (`lsu_cb_gl`, `lsu_cb_trf`, `lsu_cb_plt`), switched on in [`print.prt`](print-prt.md#output-group-rows). Each value is the sum over the unit's elements of the HRU (or HRU-lte) value multiplied by the element's `sub_frac` in `ls_unit.ele`. See [Aggregation](../output-reference/water-balance.md#aggregation).
- The element number is used as the HRU number: element $n$ adds the output of HRU $n$ (or HRU-lte $n$), and its `obj_typ_no` is not consulted. The element ids in `ls_unit.ele` therefore have to equal the HRU numbers.
- In the output files, `unit` is the landscape unit number and `gis_id` is taken from the routing unit with the same number in [`rout_unit.con`](../input-reference/con.md).
- With [gwflow](gwflow.md) and landscape unit connection (`conn_type` 2, see [`lsucell.gw`](gwflow.md#lsucellgw)), the element lists also decide which HRUs pass recharge and remaining evapotranspiration to the cells of each landscape unit. Here too element $n$ is HRU $n$.
- `ls_unit.def` needs `ls_unit.ele`. If `ls_unit.def` is missing or `null`, the project has no landscape units and the landscape unit output files are not opened.

### Example

`refdata/Osu_1hru/ls_unit.def`:

```
ls_unit.def: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
1
      id              name          area  elem_tot  elements  
       1            rtu001       10.0000         1      1       
```

One landscape unit of 10 ha, named `rtu001` after the routing unit, with element 1 of `ls_unit.ele`.

## ls_unit.ele

### Format

Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one element. Six values are read from each line.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Element number, used in the element lists of `ls_unit.def`. The largest `id` sets the size of the table. Must equal the HRU number (see below). |
| 2 | `name` | - | Name of the element. Not used. |
| 3 | `obj_typ` | - | `hru` or `hlt`. Elements of any other type are skipped in the sums. |
| 4 | `obj_typ_no` | - | HRU or HRU-lte number. |
| 5 | `bsn_frac` | fraction | Fraction of the basin land area (`ls_area` in [`object.cnt`](../input-reference/object-cnt.md)) covered by the HRU. Weight of the HRU in the basin output files. |
| 6 | `sub_frac` | fraction | Fraction of the landscape unit area covered by the HRU. Weight of the HRU in the landscape unit output files. Called `lsu_frac` in earlier documentation; the `Ames_sub1` file labels it `RU_FRAC`. |

### Behaviour

- Basin output: the `basin_wb`, `basin_nb`, `basin_ls` and `basin_pw` files, including the starting soil water and snow in `basin_wb`, are the sums of the HRU values multiplied by `bsn_frac`. The fractions are used as given; if they do not add up to 1, the basin values are scaled by their sum.
- For each HRU number $n$, the basin sum reads row $n$, takes its `obj_typ_no` $m$, and then uses the `obj_typ` and `bsn_frac` of row $m$ with the output of HRU $m$. The sum is right when row $n$ describes HRU $n$, which is how the SWAT+ Editor writes the file. HRU-lte objects are summed the same way over the first rows of the file.
- Landscape unit output uses `sub_frac` (see [`ls_unit.def`](#ls_unitdef)).
- The soft calibration of the whole basin in [`water_balance.sft`](../calibration/soft-calibration.md) takes each HRU's area as `ls_area` times its `bsn_frac` (see [soft calibration](../calibration/soft-calibration.md)).
- The decision table action `hru_fr_update` reads a replacement `ls_unit.ele` during the run and sets the area of each `hru` element to `bsn_frac` times `ls_area`.
- If `ls_unit.ele` is missing or `null`, the basin landscape files are opened and get their headers, and no data rows are written. The routine that stores the basin's starting soil water at the end of the warm-up years still reads the element table, so a model with HRUs and no `ls_unit.ele` can stop with a memory error at that point. Treat the file as required in any model with HRUs.

### Example

`refdata/Ames_sub1/ls_unit.ele`:

```
lsu_unit.ele
          ID    NAME      OBJ_TYP  OBJ_TYP_NO    BSN_FRAC       RU_FRAC
           1    hru0001      hru           1     0.20           0.0
           2    hru0002      hru           2     0.20           0.0
           3    hru0003      hru           3     0.20           0.0
           4    hru0004      hru           4     0.20           0.0
           5    hru0005      hru           5     0.10           0.0
           6    hru0006      hru           6     0.10           0.0
           7    hru0007      hru           7     0.20           0.0
           8    hru0008      hru           8     0.20           0.0
           9    hru0009      hru           9     0.20           0.0
          10    hru0010      hru          10     0.20           0.0
          11    hru0011      hru          11     0.10           0.0
          12    hru0012      hru          12     0.10           0.0
```

This file is not in the SWAT+ Editor layout: it has six columns and upper-case headers. Each row describes the HRU of the same number, as the basin sums require. The `BSN_FRAC` values add up to 2.0, so every basin output of this dataset is twice the area-weighted HRU average. `Ames_sub1` has no `ls_unit.def`, so the `RU_FRAC` values of 0 are not used.

## aqu_catunit.ele

### Format

Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one element, and seven values are read from it. A line with fewer values takes the missing ones from the next line.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Element number. The largest `id` sets the size of the table. |
| 2 | `name` | - | Name of the element. |
| 3 | `obj_typ` | - | Object type, `aqu` in files written by the SWAT+ Editor. |
| 4 | `obj_typ_no` | - | Aquifer number. |
| 5 | `bsn_frac` | fraction | Fraction of the basin covered by the aquifer. |
| 6 | `sub_frac` | fraction | Fraction of the aquifer region covered by the element. |
| 7 | `reg_frac` | fraction | Fraction of the calibration region covered by the element. |

### Behaviour

- In 62.0.1 the file works as a switch. When it has at least one element, the basin aquifer files (`basin_aqu` row in [`print.prt`](print-prt.md#output-group-rows)) get one data row per interval. Without it they get headers only.
- The basin aquifer values are weighted by each aquifer's area divided by `tot_area` in [`object.cnt`](../input-reference/object-cnt.md) (see [aquifer output](../output-reference/aquifer-reservoir-plant.md#aquifer)). The columns of `aqu_catunit.ele` are not used for this.
- The columns are meant for aquifer regions defined in `aqu_catunit.def` and `aqu_reg.def`. SWAT+ 62.0.1 reads those files, but no calculation or output uses the regions.

### Example

The first rows of `refdata/Osu_1hru/aqu_catunit.ele`:

```
aqu_catunit.ele: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                   obj_typ  obj_typ_no      bsn_frac      sub_frac      reg_frac  
       1  aqu011                     aqu           1       0.00241       0.00000       0.00000  
       2  aqu012                     aqu           2       0.10460       0.00000       0.00000  
       3  aqu021                     aqu           3       0.01290       0.00000       0.00000  
```

The file has 21 elements, while the dataset has one aquifer. The rows have no effect beyond switching on the basin aquifer output. In `refdata/Ames_sub1` the file is empty, so that dataset writes no basin aquifer data rows.

## Columns in earlier documentation

- `ls_unit.ele`: the SWAT+ Editor writes a seventh column, `reg_frac`. SWAT+ 62.0.1 reads six values per line and ignores it.
- `ls_unit.def`: earlier documentation did not list the line with the number of landscape units (line 2) or the `area` column. Both are read, and a file without them is read out of step.

## Related files

- [`rout_unit.con`](con.md): the routing unit objects, their areas and their outflow connections.
- [`hru.con`](con.md) and [`hru-data.hru`](hru.md): the HRUs that are elements of routing and landscape units.
- [`object.cnt`](object-cnt.md): the `rtu` count, and `ls_area` and `tot_area` used with `bsn_frac` and the basin aquifer output.
- [`file.cio`](file-cio.md): names the files on the `routing_unit` and `regions` lines.
- [`topography.hyd` and `field.fld`](hyd.md): the `topo` and `field` records of `rout_unit.rtu`.
- [`aquifer.aqu`](aqu.md): the aquifers listed in `aqu_catunit.ele`.
- [`print.prt`](print-prt.md): switches for the `ru`, `lsunit_*`, `basin_*` and `basin_aqu` outputs.
- [Decision tables](dtl.md#land-use-and-management-actions): the `hru_fr_update` action.
- Outputs: [water balance](../output-reference/water-balance.md), [nutrient balance and losses](../output-reference/nutrient-balance.md), [hydrographs](../output-reference/hydrographs.md#ru-files), [aquifer output](../output-reference/aquifer-reservoir-plant.md#aquifer).
- [Delivery ratios](../model-theory/recall-point-sources.md#delivery-ratios) in the model theory.

??? quote "Sources"

    - File name slots: `type input_ru` and `type input_regions` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90); read order in [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) and [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - Routing unit readers: [`ru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_read.f90) (`rout_unit.rtu`), [`ru_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_read_elements.f90) (`rout_unit.ele`, `rout_unit.def`); element lists: [`define_unit_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/define_unit_elements.f90)
    - Routing unit types: `ru_parameters` in [`ru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_module.f90), `routing_unit_data` and `routing_unit_elements` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Routing unit linkage and inflow sharing: [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90), [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90)
    - Daily routing unit sum: [`ru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_control.f90), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)
    - Delivery ratios: [`dr_ru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_ru.f90), [`dr_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_db_read.f90)
    - Time of concentration and unit hydrographs: [`time_conc_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_conc_init.f90), [`unit_hyd_ru_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/unit_hyd_ru_hru.f90)
    - Landscape unit reader: [`lsu_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_read_elements.f90); types `landscape_units` and `landscape_elements` in [`calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90)
    - Landscape unit and basin output: [`lsu_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_output.f90), [`lsu_carbon_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_carbon_output.f90), [`basin_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_output.f90), [`basin_sw_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_sw_init.f90) (called from [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)), file opening in [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90)
    - Other uses of `ls_unit.ele` and `ls_unit.def`: [`lcu_read_softcal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lcu_read_softcal.f90), [`hru_fr_change.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_fr_change.f90) (action `hru_fr_update` in [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)), [`gwflow_rech.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_rech.f90), [`gwflow_gwet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_gwet.f90)
    - Aquifer elements: [`aqu_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_elements.f90), called from [`proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90); basin aquifer output in [`basin_aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_aquifer_output.f90), files opened in [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `rout_unit.def` | `id` | not stored |
    | `rout_unit.def` | `name` | `ru_def%name` |
    | `rout_unit.def` | `elem_tot` | `nspu` |
    | `rout_unit.def` | `elements` | `elem_cnt`, expanded into `ru_def%num` and `ru_def%num_tot` |
    | `rout_unit.ele` | `id` | index of `ru_elem` |
    | `rout_unit.ele` | `name` | `ru_elem%name` |
    | `rout_unit.ele` | `obj_typ` | `ru_elem%obtyp` |
    | `rout_unit.ele` | `obj_id` | `ru_elem%obtypno` (object number in `ru_elem%obj`) |
    | `rout_unit.ele` | `frac` | `ru_elem%frac` |
    | `rout_unit.ele` | `dlr` | `ru_elem%dr_name` (ratios in `ru_elem%dr`) |
    | `rout_unit.rtu` | `id` | index of `ru` |
    | `rout_unit.rtu` | `name` | `ru%name` |
    | `rout_unit.rtu` | `define` | `ru%dbsc%elem_def` |
    | `rout_unit.rtu` | `dlr` | `ru%dbsc%elem_dr` |
    | `rout_unit.rtu` | `topo` | `ru%dbsc%toposub_db` (index `ru%dbs%toposub_db`) |
    | `rout_unit.rtu` | `field` | `ru%dbsc%field_db` (index `ru%dbs%field_db`, values in `ru%field`) |
    | `ls_unit.def` | line 2 | `mlsu`, stored as `db_mx%lsu_out` |
    | `ls_unit.def` | `name` | `lsu_out%name` |
    | `ls_unit.def` | `area` | `lsu_out%area_ha` |
    | `ls_unit.def` | `elements` | `lsu_out%num`, `lsu_out%num_tot` |
    | `ls_unit.ele` | `obj_typ` | `lsu_elem%obtyp` |
    | `ls_unit.ele` | `obj_typ_no` | `lsu_elem%obtypno` |
    | `ls_unit.ele` | `bsn_frac` | `lsu_elem%bsn_frac` |
    | `ls_unit.ele` | `sub_frac` | `lsu_elem%ru_frac` |
    | `aqu_catunit.ele` | `obj_typ`, `obj_typ_no` | `acu_elem%obtyp`, `acu_elem%obtypno` |
    | `aqu_catunit.ele` | `bsn_frac`, `sub_frac`, `reg_frac` | `acu_elem%bsn_frac`, `acu_elem%ru_frac`, `acu_elem%reg_frac` |
    | `aqu_catunit.ele` | largest `id` | `db_mx%aqu_elem` |

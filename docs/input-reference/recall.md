---
title: recall (point sources and inlets)
description: Recall objects bring measured or externally computed flows and loads (point sources, inlets, diversions) into the SWAT+ routing. Format of recall.rec, the recall data files and the related recall_db.rec, salt, constituent and region files.
status: review
verified_against:
  - src/recall_read.f90
  - src/recalldb_read.f90
  - src/recall_module.f90
  - src/hydrograph_module.f90
  - src/main.f90.in
  - src/hyd_connect.f90
  - src/command.f90
  - src/recall_nut.f90
  - src/recall_salt.f90
  - src/recall_cs.f90
  - src/recall_read_salt.f90
  - src/recall_read_cs.f90
  - src/rec_read_elements.f90
  - src/proc_cal.f90
  - src/calibration_data_module.f90
  - src/res_hydro.f90
  - src/dtbl_res_read.f90
  - src/water_use_read.f90
  - src/water_treatment_read.f90
  - src/water_osrc_read.f90
  - src/wallo_use.f90
  - src/wallo_treatment.f90
  - src/wallo_start_day.f90
  - src/exco_db_read.f90
  - src/exco_read_om.f90
  - src/input_file_module.f90
  - src/header_write.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A recall object is a spatial object whose outflow is read from a file instead of simulated. It is used for point sources such as wastewater treatment plants, for inflow from outside the modelled area (an upstream gauge or another model), and for diversions. Each day the recall object sends the flow and loads for that day to the objects named in its row of [`recall.con`](con.md), in the same way an HRU or channel sends its outflow downstream.

A recall object needs three pieces of input:

1. A row in [`recall.con`](../input-reference/con.md), which gives its location and the receiving object (usually a channel, `sdc`).
2. A record in `recall.rec` with the same `id`, which gives the time step and the name of the data file.
3. The data file with the flows and loads.

The number of recall objects is the `rec` column of [`object.cnt`](object-cnt.md). `recall.rec` is named on the `recall` line of [`file.cio`](file-cio.md) (default `recall.rec`; `null` turns recall input off).

## recall.rec

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one recall record with four values. The header names are not checked; the example in `refdata/Osu_1hru` uses `NUM NAME TYPE FNAME`. Anything after the fourth value on a line is ignored.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Record number. A recall object uses the record whose `id` equals its `id` in [`recall.con`](../input-reference/con.md); the `rec` column of [`recall.con`](../input-reference/con.md) is not used. The largest `id` sets the size of the table. |
| 2 | `name` | - | Name of the record, up to 25 characters. |
| 3 | `typ` | - | Time step of the data: 0 = sub-daily, 1 = daily, 2 = monthly, 3 = yearly, 4 = constant taken from an export coefficient record. |
| 4 | `filename` | - | Name of the data file (up to 25 characters), or for `typ` 4 the name of a record in `exco.exc`. |

In revision 8a1edd4, recall objects were read from `recall_db.rec`, with six data file names (organic and mineral, pesticide, pathogen, heavy metal, salt and constituent) each followed by its units and a time step word (`sub`, `day`, `mo`, `yr`), and `recall.rec` was not read. In 62.0.1 recall objects are read from `recall.rec` with one data file and an integer time step per record. `recall_db.rec` is still read, with plain file names, but only for the uses listed under [recall_db.rec](#recall_dbrec).

## Recall data file

One data file per recall record, named in `recall.rec`.

- Line 1: title, skipped.
- Line 2: number of years in the file. Read but not used; SWAT+ works out the years from the rows.
- Line 3: column header, skipped.
- Each later line: one time step.

Each data line has six leading values followed by 18 values in this order:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `jday` | - | Day of year (1 to 366). Selects the day for daily data. |
| 2 | `mo` | - | Month (1 to 12). Selects the month for monthly data. |
| 3 | `day_mo` | - | Day of month. Not used. |
| 4 | `yr` | - | Year. |
| 5 | `ob_typ` | - | Object type label. Not used. |
| 6 | `ob_name` | - | Object name label. Not used. |
| 7 | `flo` | m³ | Water volume for one day. |
| 8 | `sed` | t | Sediment. |
| 9 | `orgn` | kg N | Organic N. |
| 10 | `sedp` | kg P | Organic P. |
| 11 | `no3` | kg N | Nitrate N. |
| 12 | `solp` | kg P | Soluble (mineral) P. |
| 13 | `chla` | kg | Chlorophyll-a. |
| 14 | `nh3` | kg N | Ammonium N. |
| 15 | `no2` | kg N | Nitrite N. |
| 16 | `cbod` | kg | Carbonaceous biological oxygen demand. |
| 17 | `dox` | kg | Dissolved oxygen. |
| 18 | `san` | t | Detached sand. |
| 19 | `sil` | t | Detached silt. |
| 20 | `cla` | t | Detached clay. |
| 21 | `sag` | t | Detached small aggregates. |
| 22 | `lag` | t | Detached large aggregates. |
| 23 | `grv` | t | Gravel. |
| 24 | `temp` | °C | Water temperature. |

The values are used as given, as the recall object's outflow for one day. For daily data this is the day's volume and loads. Monthly and yearly values are also applied on every day of their month or year, so give them as daily amounts: the mean daily volume and load for the month or year. A monthly or yearly total would be applied once for every day of the period. Pesticides, pathogens, heavy metals, salts and other constituents cannot be given in this file; their recall loads are zero.

### Time steps

| `typ` | Rows | Value used on a simulation day |
|-------|------|-------------------------------|
| 1, daily | One row per day | The row with that day of year (`jday`) in that year. |
| 2, monthly | One row per month | The row with that month (`mo`) in that year. |
| 3, yearly | One row per year | The row for that year. |
| 0, sub-daily | | Does not work, see below. |
| 4, constant | No data file | Does not work, see below. |

### Years

SWAT+ reads the first data row to find the first year in the file.

- If the file starts in or before the first simulation year, the rows before that year are skipped. The file must then contain the first simulation year: if it ends before that year, the reader keeps searching and the run does not get past reading the inputs.
- If the file starts after the first simulation year, its first year is placed at the matching simulation year and earlier years get no recall input.

From there each change of year in the file moves to the next simulation year, and reading stops at the last simulation year. A year missing from the middle of the file is not skipped over: the following years shift one year earlier. Give every year from the start of the data to the end without gaps.

For daily and monthly data, the recall object sends nothing on days outside the years covered by the file. For yearly data the test of the year range always passes, but years without data have zero values, so the effect is the same.

### Diversions

A negative `flo` in daily data removes water. When the recall object's first connection in [`recall.con`](../input-reference/con.md) is a channel with more than 10 m³ of water, SWAT+ also removes nitrate, soluble P, ammonium, nitrite, dissolved oxygen and organic N from that channel at the channel's concentration, limited to what is in the channel. Salt and constituent mass are handled in the same way when those modules are active.

### Sub-daily and constant records

Sub-daily records (`typ` 0) do not work in 62.0.1. The reader has no step that reads a sub-daily data line, so it keeps returning to the same line and never reaches the end of the file; a run with a sub-daily recall record does not get past reading the inputs.

Constant records (`typ` 4) are meant to take a fixed daily hydrograph from the `exco_om.exc` row of the `exco.exc` record named in `filename`. In 62.0.1 `recall.rec` is read before the export coefficient files, so the name is looked up in an empty list and the constant hydrograph stays zero. The daily recall step also has no branch for `typ` 4. A recall object with a `typ` 4 record therefore sends nothing. Use an export coefficient object in [`exco.con`](con.md#export-coefficient-objects) for a constant source instead.

## recall_db.rec

`recall_db.rec` is a second recall list, read when a file with this name is in the project folder. It is not named in [`file.cio`](../input-reference/file-cio.md). It is used by the [water allocation](water-allocation.md) files and by reservoir release decision tables, not by recall objects in the routing.

Line 1 is a title and line 2 the header; both are skipped. Each later line has nine values:

| # | Column | Description |
|---|--------|-------------|
| 1 | `id` | Record number. |
| 2 | `name` | Record name, up to 13 characters. |
| 3 | `org_min` | Organic and mineral data file name. |
| 4 | `pest` | Pesticide data file name. |
| 5 | `path` | Pathogen data file name. |
| 6 | `hmet` | Heavy metal data file name. |
| 7 | `salt` | Salt data file name. |
| 8 | `constit` | Other constituent data file name. |
| 9 | `descrip` | Description, one word or quoted. |

All nine values are required; a missing value makes the reader continue on the next line. The file names are stored as text only. None of these files is opened through `recall_db.rec`.

The two uses in 62.0.1:

- A reservoir release decision table action of type `meas` names a `recall_db.rec` record. The reservoir then releases the daily, monthly or yearly flow of the `recall.rec` record with the same number, without the year-range test used for recall objects. Keep the numbering of the two files the same.
- Water use, water treatment and outside-source entries in the water allocation files can take their water quality from a recall record by matching their name against `org_min`. The link from a `recall_db.rec` record to the recall data is never set in 62.0.1, so this option does not deliver the intended data.

## pest.com

If a file named `pest.com` is in the project folder, SWAT+ reads it as a list of pesticide recall files. The values it reads are stored in the flow and nutrient records of the recall objects with the same numbers, replacing the data read through `recall.rec`, and no pesticide load is set. Do not put a file with this name in the project folder.

## Salt and constituent recall files

`salt_recall.rec` and `cs_recall.rec` give salt-ion and constituent loads for recall objects when the salt or constituent modules are active. Their readers are in the source, but 62.0.1 does not call them, so these files are not read. The daily recall step still looks up salt and constituent recall data whenever salts or constituents are simulated. A model that simulates salts or constituents and has recall objects is therefore likely to stop with a memory error. See [salts](salt.md) and [constituents](cs.md).

For reference, the format the readers expect: a title, a header, then one row per recall object with `id`, `name`, `typ` (1 = daily, 2 = monthly, 3 = yearly, 4 = export coefficient) and `filename`. Each data file has a title (the word `Incoming` marks a source from outside the watershed), the number of years, a header, and rows of `jday`, `mo`, `day_mo`, `yr`, `ob_typ`, `ob_name` followed by one value per salt ion or constituent in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs).

## Region files

`rec_catunit.def`, `rec_reg.def` and `rec_catunit.ele` group recall objects into regions. They are named on the `regions` line of [`file.cio`](../input-reference/file-cio.md) and read when the calibration inputs are set up.

- `rec_catunit.def` and `rec_reg.def`: a title, the number of regions, a header, then per region `id`, `name`, `area` (ha), the number of elements, and the element numbers. With 0 elements a region contains every recall object.
- `rec_catunit.ele`: a title, a header, then per element `id`, `name`, `obj_typ`, `obj_typ_no`, `bsn_frac`, `sub_frac` and `reg_frac`.

In 62.0.1 these regions are not used for any output or calibration step, and the tables they fill are not set up before reading, so a definition file with one or more regions is likely to stop the run. Set these entries to `null` in [`file.cio`](../input-reference/file-cio.md).

## Output

Recall objects are printed to `recall_day.txt`, `recall_mon.txt`, `recall_yr.txt` and `recall_aa.txt` (and the matching `.csv` files), selected by the `recall` row of [`print.prt`](print-prt.md). The sum over all recall objects is printed to the `basin_psc` files. The columns are described in [recall outputs](../output-reference/recall.md).

## Columns in earlier documentation

Earlier documentation listed `recall.rec` with the columns `id`, `name`, `om_name`, `om_unit`, `om_tstep`, `pest_name`, `pest_unit`, `pest_tstep`, `path_name`, `path_unit`, `path_tstep`, `hmet_name`, `hmet_unit`, `hmet_tstep`, `salt_name`, `salt_unit`, `salt_tstep`, `cst_name`, `cst_unit` and `cst_tstep`. That is the layout recall objects used before 62.0.1. SWAT+ 62.0.1 no longer reads these columns: `recall.rec` has the four columns described above, and `recall_db.rec` has plain file names without units or time steps.

## Example

`refdata/Osu_1hru/recall.rec` in the SWAT+ repository:

```
recall.rec
NUM     NAME    TYPE     FNAME    OBJ_TYP     OBJ_NAME       flo     sed    orgn    sedp     no3    solp    chla     nh3      no2    cbod     dox     san     sil     cla     sag     lag     grv    temp
   1    PSTYR    3    	RECYR.        hru         hru1   12120.5       0       0       0       0       0       0        0       0       0       0       0       0       0       0       0       0       0
   1      1         1    2011        hru         hru2    9000.7       0       0       0       0       0       0        0       0       0       0       0       0       0       0       0       0       0
```

SWAT+ reads the four values `1 PSTYR 3 RECYR.`: record 1, named `PSTYR`, yearly data in a file named `RECYR.`. The rest of the line, and the second data line, are ignored, because the largest `id` is 1 and only one record is read. This dataset has `rec` = 0 in [`object.cnt`](../input-reference/object-cnt.md), so the file is not used in the run, and `RECYR.` is not included.

A daily data file for one recall record looks like this (illustrative values, columns 8 to 24 shortened):

```
daily point source, wastewater plant 1
2
jday  mo  day_mo    yr  ob_typ  ob_name      flo     sed    orgn    sedp     no3    solp  ...  temp
   1   1       1  2010  sdc     cha05     4320.0   0.050    1.20    0.30    8.50    1.10  ...  12.0
   2   1       2  2010  sdc     cha05     4410.0   0.050    1.25    0.31    8.60    1.12  ...  12.0
```

Each row gives the volume (m³) and loads (t, kg) discharged on that day, here about 0.05 m³/s.

## Related files

- [`recall.con`](con.md): location of each recall object and the objects that receive its outflow.
- [`object.cnt`](object-cnt.md): number of recall objects (`rec`).
- [`file.cio`](file-cio.md): names `recall.rec` on the `recall` line and the region files on the `regions` line.
- [`print.prt`](print-prt.md): recall output switches.
- [Recall outputs](../output-reference/recall.md): columns of the recall output files.
- [Decision tables](dtl.md): reservoir release action `meas`.
- [Water allocation](water-allocation.md): water quality from recall records.
- [Recall, export coefficient and delivery ratio objects](../model-theory/recall-point-sources.md) in the model theory.

??? quote "Sources"

    - Reader for `recall.rec`, the data files and `pest.com`: [`recall_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read.f90); reader for `recall_db.rec`: [`recalldb_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recalldb_read.f90). Both are called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in), after [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90) and before [`exco_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_db_read.f90)
    - Type definitions: `type recall_hydrograph_inputs` and `type hyd_output` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90); `type recall_databases` in [`recall_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_module.f90)
    - Daily use: `case ("recall")` in [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90); diversions in [`recall_nut.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_nut.f90), [`recall_salt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_salt.f90), [`recall_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_cs.f90)
    - Salt and constituent readers (not called): [`recall_read_salt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read_salt.f90), [`recall_read_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read_cs.f90)
    - Region files: [`rec_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rec_read_elements.f90), called from [`proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90); arrays in [`calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90)
    - Uses of `recall_db.rec`: [`dtbl_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_res_read.f90), [`res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90), [`water_use_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_use_read.f90), [`water_treatment_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_treatment_read.f90), [`water_osrc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_osrc_read.f90), [`wallo_use.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_use.f90), [`wallo_treatment.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_treatment.f90), [`wallo_start_day.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_start_day.f90)
    - Export coefficient lookup: [`exco_read_om.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_read_om.f90)
    - File names: `in_rec%recall_rec` and `in_regs%def_psc`, `def_psc_reg`, `ele_psc` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90); output files opened in [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | recall.rec | `id` | array index `i` of `recall` |
    | recall.rec | `name` | `recall(i)%name` |
    | recall.rec | `typ` | `recall(i)%typ` |
    | recall.rec | `filename` | `recall(i)%filename` |
    | data file | `flo` to `temp` | `recall(i)%hd(istep, iyrs)` (`type hyd_output`) |
    | recall_db.rec | `name`, `org_min`, `pest`, `path`, `hmet`, `salt`, `constit`, `descrip` | `recall_db(i)%name`, `%org_min`, `%pest`, `%path`, `%hmet`, `%salt`, `%constit`, `%descrip` |

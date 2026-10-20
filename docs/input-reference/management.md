---
title: Management schedule and minor inputs
description: management.sch, puddle.ops, transplant.ops, co2_yr.dat and co2.out, object.prt.
status: review
verified_against:
  - src/mgt_read_mgtops.f90
  - src/read_mgtops.f90
  - src/mgt_operatn.f90
  - src/mgt_sched.f90
  - src/mgt_operations_module.f90
  - src/proc_cond.f90
  - src/plant_init.f90
  - src/time_control.f90
  - src/hru_control.f90
  - src/actions.f90
  - src/mgt_read_puddle.f90
  - src/plant_transplant_read.f90
  - src/mgt_transplant.f90
  - src/plant_data_module.f90
  - src/co2_read.f90
  - src/basin_module.f90
  - src/object_read_output.f90
  - src/obj_output.f90
  - src/hydrograph_module.f90
  - src/input_file_module.f90
  - src/chg_par.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

The management schedules are in `management.sch`. Four small inputs referred to from other pages follow it: `puddle.ops`, `transplant.ops`, `co2_yr.dat` and `object.prt`.

## management.sch

`management.sch` contains the management schedules. Each schedule has a list of operations on fixed dates or heat-unit fractions, a list of automatic operations (decision tables in [`lum.dtl`](dtl.md)), or both. An HRU uses the schedule named in the `mgt` column of its land use in [`landuse.lum`](lum.md). The file name is the second entry on the `lum` line of [`file.cio`](file-cio.md) (default `management.sch`).

### Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Then, for each schedule:

1. The schedule line: `name`, `numb_ops`, `numb_auto`.
2. `numb_auto` lines, each naming one decision table in [`lum.dtl`](../input-reference/dtl.md).
3. `numb_ops` operation lines.

| Column | Description |
|--------|-------------|
| `name` | Schedule name, referenced by `mgt` in [`landuse.lum`](../input-reference/lum.md). |
| `numb_ops` | Number of scheduled operation lines. |
| `numb_auto` | Number of automatic operation lines. |

### Automatic operations

Each automatic operation line names a decision table in [`lum.dtl`](../input-reference/dtl.md). Every day, SWAT+ checks each listed table for every HRU that uses the schedule. A name that is not in [`lum.dtl`](../input-reference/dtl.md) is not reported.

Three generic tables can be shared by several schedules with different crops. For these, the crop name follows the table name on the same line, and the `plant`, `harvest` and `harvest_kill` actions of the table use it instead of their `option` column:

| Table name | Line content |
|------------|--------------|
| `pl_hv_summer1` | table name and one crop |
| `pl_hv_winter1` | table name and one crop |
| `pl_hv_summer2` | table name and two crops; the crop used is the one for the current rotation year |

### Operation lines

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `op_typ` | - | Operation code (see below). |
| 2 | `mon` | - | Month of the operation, or 0. |
| 3 | `day` | - | Day of the month, or 0. |
| 4 | `hu_sch` | fraction | Heat-unit fraction that triggers the operation, or 0. |
| 5 | `op_data1` | - | First name (see below). |
| 6 | `op_data2` | - | Second name (see below). |
| 7 | `op_data3` | varies | Number: amount, days or override (see below). |

| `op_typ` | Operation | `op_data1` | `op_data2` | `op_data3` |
|----------|-----------|------------|------------|------------|
| `plnt` | plant | plant name in the HRU's plant community | name in `transplant.ops` | > 0 to start from the transplant entry |
| `harv` | harvest | plant name, or `all` | name in [`harv.ops`](ops.md#harvops) | residue harvest efficiency (0 uses `harv_eff`) |
| `hvkl` | harvest and kill | plant name, or `all` | name in [`harv.ops`](../input-reference/ops.md#harvops) | residue harvest efficiency |
| `kill` | kill | plant name, or `all` | - | - |
| `till` | tillage | name in [`tillage.til`](til.md) | - | - |
| `fert` | fertilizer | name in [`fertilizer.frt`](frt.md) | name in [`chem_app.ops`](ops.md#chem_appops) | amount, kg/ha |
| `manu` | manure | name in [`manure_db.frt`](../input-reference/frt.md#manure_dbfrt) | name in [`chem_app.ops`](../input-reference/ops.md#chem_appops) | amount, kg/ha |
| `pest` | pesticide | pesticide name listed in [`constituents.cs`](../input-reference/cs.md#constituentscs) | name in [`chem_app.ops`](../input-reference/ops.md#chem_appops) | amount, kg/ha (multiplied by `app_eff`) |
| `graz` | grazing | name in [`graze.ops`](ops.md#grazeops) | - | number of grazing days |
| `burn` | burning | name in [`fire.ops`](ops.md#fireops) | - | - |
| `swep` | street sweeping | name in [`sweep.ops`](ops.md#sweepops) | - | - |
| `irrm` | irrigation | name in [`irr.ops`](ops.md#irrops) | - | - |
| `irpm` | irrigation of a rice paddy | name in [`irr.ops`](../input-reference/ops.md#irrops) | - | - |
| `irrp` | start, adjust or stop paddy irrigation | name in [`irr.ops`](../input-reference/ops.md#irrops) | water source: `cha`, `res`, `aqu` or `unlim` | target ponding depth, mm (see below) |
| `pudl` | puddling | name in [`tillage.til`](../input-reference/til.md) | name in `puddle.ops` | - |
| `weir` | set paddy weir height | weir name in [`weir.res`](../input-reference/res.md#weirres) | - | weir height, mm |
| `dwm` | drainage water management | - | - | tile drain depth, mm |
| `cnup` | change curve number | `absval`, `abschg`, `pctchg` or `relchg` | - | value |
| `mons` | monsoon season | - | - | 0 or 1 |
| `skip` | end of a rotation year | - | - | - |

Notes on individual operations:

- `plnt`, `harv`, `hvkl` and `kill` act on the plant in the HRU's plant community ([`plant.ini`](ini.md)) whose name equals `op_data1`. A plant that is already growing is not planted again; the event is logged as `PLANT_ALREADY_GROWING`.
- `fert` on an HRU with standing water puts the fertilizer into the water.
- `pest` looks the name up in the pesticide list of [`constituents.cs`](../input-reference/cs.md#constituentscs) when the operation runs, so the pesticide must be simulated as a constituent.
- `irrm` and `irpm` apply the depth in [`irr.ops`](../input-reference/ops.md#irrops) (see [`irr.ops`](ops.md#irrops)).
- `irrp` turns on automatic irrigation of a paddy: water is added whenever the ponding depth falls below 90% of the target. A positive `op_data3` is the target depth; a negative value uses `amt_mm` of the [`irr.ops`](../input-reference/ops.md#irrops) entry; zero turns paddy irrigation off. The [`irr.ops`](../input-reference/ops.md#irrops) entry also gives the efficiency, runoff fraction and salt and nitrate concentrations of the water.
- `cnup` changes the curve number for moisture condition II: set it to the value (`absval`), add the value (`abschg`), change it by the value in percent (`pctchg`), or multiply it by 1 + value (`relchg`). The result is kept between 35 and 95.
- `mons` applies to plants with a `moisture_gro` trigger in [`plants.plt`](../input-reference/plt.md). With `op_data3` 1 it marks the start of the monsoon season. With 0 it restarts the phenology of such plants that are not growing.
- Codes not in this table (for example `pcom` or `prtp`) are read but do nothing.

### Timing

Operations run in the order of the lines, one rotation year after another. A `skip` line ends a rotation year. After the last line the schedule starts again at the first line, so a schedule with $n$ `skip` lines is an $n$-year rotation.

An operation runs on the day its `mon` and `day` match the calendar date, or, when `hu_sch` is greater than 0, on the first day the heat-unit fraction exceeds `hu_sch`. The heat-unit fraction is that of the plant named in `op_data1` while it grows, and the base-zero fraction of the year otherwise. Give each operation either a date or a heat-unit fraction and set the other to 0. Within a rotation year, lines must be in chronological order: SWAT+ waits for the date of the current line before it moves on.

When the schedule reaches a `skip` line it waits there until the end of the year: 31 December for HRUs in the northern hemisphere, day 181 for HRUs in the southern hemisphere. At the start of the run, SWAT+ begins at the rotation year given by the plant community in [`plant.ini`](../input-reference/ini.md#plantini) and skips the operations dated before the first simulated day.

The operations performed are written to `mgt_out.txt` when `mgtout` is `y` in [`print.prt`](print-prt.md).

### Example

`refdata/Ames_sub1/management.sch` in the SWAT+ repository, first lines:

```
management.sch file AMES
                          NAME NUMB_OPS NUMB_AUTO OP_TYP        MON        DAY HU_SCH   OP_DATA1    OP_DATA2  OP_DATA3
mgt_01                              305         1
                                                irr_year_irr
                                                    till          4          1    0.0    chisplow        null     0.000
                                                    plnt          4         28    0.0        corn        null         0
                                                    irrm          5         15    0.0        sprinkler_ilm    null     0.000
                                                    fert          6          1    0.0        null      elem_n   181.400
                                                    hvkl         10          7    0.0        corn       grain     0.000
                                                    skip          0          0      0        null        null         0
```

Schedule `mgt_01` has 305 operation lines and one automatic operation, the `irr_year_irr` table of [`lum.dtl`](../input-reference/dtl.md) (see the [`*.dtl` example](dtl.md#example)). In the first rotation year it tills with `chisplow` on 1 April, plants `corn` on 28 April, irrigates once on 15 May, and harvests and kills the corn with the `grain` harvest operation on 7 October.

For a `fert` line, 62.0.1 reads the fertilizer name from `op_data1` and the application method from `op_data2`. The `fert` line above has `null` in `op_data1` and the fertilizer name `elem_n` in `op_data2`. No fertilizer is named `null`, so the line matches no entry in [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt) and applies nothing; no warning is written. Every `fert` line in this file has the same layout, so as written the Ames schedules apply no fertilizer in 62.0.1. A line that applies 181.4 kg/ha of `elem_n` in 62.0.1 reads `fert 6 1 0.0 elem_n broadcast 181.4`, with `broadcast` an entry in [`chem_app.ops`](../input-reference/ops.md#chem_appops).

Two schedules from `refdata/Osu_1hru/management.sch`, one using a scheduled `manu` operation together with decision tables and one using only decision tables:

```
rice140_rot    					  1           7
	 plow
	 weir60r
	 weir0
	 pad_irr_r
	 puddle
	 pl_hv_rice
	 fert_paddy
manu      5          1      0     beef_salt   broadcast  12.9927
agrl_rot                          0          2
    pl_hv_agro
	fert_stress
```

As shipped, the `manu` line finds `beef_salt` in [`manure_db.frt`](../input-reference/frt.md#manure_dbfrt) and `broadcast` in [`chem_app.ops`](../input-reference/ops.md#chem_appops), so 12.99 kg/ha of manure is applied on 1 May. The schedule has one operation line and no `skip`, so the line runs every year.

### Related files

- [`landuse.lum`](lum.md): selects a schedule by name in its `mgt` column.
- [`*.ops`](ops.md), [`tillage.til`](til.md), [`fertilizer.frt`](frt.md): databases the operation lines name.
- [`*.dtl`](dtl.md): the decision tables listed as automatic operations.
- [`plant.ini`](ini.md): plant community and initial rotation year.

## puddle.ops

Puddling parameters for rice paddies. A puddling operation (`pudl` in `management.sch`, or the `puddle` action in [`lum.dtl`](../input-reference/dtl.md)) mixes the soil with a tillage operation, lowers the hydraulic conductivity of the paddy's upper soil, and sets the sediment concentration of the ponded water. The file name is fixed.

Free format. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one entry, read by position.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Puddling operation name. |
| 2 | `hydcon_mm/h` | mm/h | Hydraulic conductivity of the upper soil after puddling. 0 leaves it unchanged. |
| 3 | `sed_ppm` | ppm | Sediment concentration of the ponded water after puddling. |
| 4 | `orgn_ppm` | ppm | Organic N concentration after puddling. Read but not used. |
| 5 | `sedp_ppm` | ppm | Organic P concentration after puddling. Read but not used. |
| 6 | `no3_ppm` | ppm | NO3-N concentration after puddling. Read but not used. |
| 7 | `solp_ppm` | ppm | Soluble P concentration after puddling. Read but not used. |
| 8 | `nh3_ppm` | ppm | NH3 concentration after puddling. Read but not used. |
| 9 | `no2_ppm` | ppm | NO2 concentration after puddling. Read but not used. |

The tillage operation is named in `op_data1` of the `pudl` line (or the `name` column of the `puddle` action). If the paddy has more than 1 mm of water, the mixing is done in the ponded water; otherwise it is ordinary tillage.

`refdata/Osu_1hru/puddle.ops` as shipped:

```
name                  hydcon_mm/h   sed_ppm      orgn_ppm      sedp_ppm     no3_ppm       solp_ppm       nh3_ppm  no2_ppm
high_eff              0.00000         10000       0.00000     800.00000     10.00000      20.00000       1.00000  1.00000
med_eff               0.00000         10000       0.00000     500.00000     10.00000      20.00000       1.00000  1.00000
low_eff               0.0         10000       0.00000     100.00000     10.00000      20.00000       1.00000  1.00000
```

The file has no title line. SWAT+ skips the column header as the title and the `high_eff` line as the header, so 62.0.1 reads only `med_eff` and `low_eff`. An operation that names `high_eff` finds no entry and uses an entry with all values zero: conductivity unchanged and no sediment added. The Osu dataset's `puddle` decision table names `med_eff`, so its puddling runs with a sediment concentration of 10000 ppm and unchanged conductivity (`hydcon_mm/h` is 0).

## transplant.ops

Transplant database. A planting can start a plant from a transplanted state instead of from seed: a `plnt` line in `management.sch` with a `transplant.ops` name in `op_data2` and `op_data3` greater than 0, or a `plant` action in [`lum.dtl`](../input-reference/dtl.md) with the name in its `fp` column. The file name is fixed. Up to revision 61 it was `transplant.plt`; 62.0.1 reads only `transplant.ops`, so a project with a `transplant.plt` file needs it renamed.

Free format. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one entry, read by position.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Transplant name. |
| 2 | `lai_ini` | m²/m² | Leaf area index at transplanting. Read but not used. |
| 3 | `bm_ini` | kg/ha | Plant biomass at transplanting. |
| 4 | `phu_acc_ini` | fraction | Fraction of potential heat units already accumulated. |
| 5 | `fr_yrmat` | fraction | Fraction of the years to maturity already reached (perennials). |
| 6 | `pop` | plants/m² | Plant population. Sets the maximum leaf area index through the population curve in [`plants.plt`](../input-reference/plt.md). 0 uses the maximum LAI in [`plants.plt`](../input-reference/plt.md). |

`refdata/Osu_1hru` contains the file under its old name:

```
transplant.plt
      NAME       LAI_INI	BM_INI   PHU_ACC_INI   FR_YRMAT   	POP
   tr_rice140        0.1       0.2     0.2     		1			100
```

62.0.1 does not open `transplant.plt`, so in this dataset the transplant database is empty. The `plant` actions in its [`lum.dtl`](../input-reference/dtl.md) that name `tr_rice140` find no entry, no message is written, and the rice is planted from seed with the initial values of an ordinary planting.

## co2_yr.dat and co2.out

Atmospheric CO2 concentration by year. `co2_yr.dat` is optional; its name is fixed. SWAT+ builds one CO2 value per simulation year and writes the series to `co2.out`.

`co2_yr.dat` layout:

| Line | Content |
|------|---------|
| 1 | title (skipped) |
| 2 | number of year records $n$ |
| 3 | header (skipped) |
| 4 to $n$ + 3 | calendar year and CO2 concentration (ppm), one year per line, consecutive years in increasing order |

How the series is built:

- If `co2_yr.dat` is missing or empty, every year uses `co2` from [`parameters.bsn`](parameters-bsn.md) (default 400 ppm).
- If the last record's year is at or before the first simulation year, every year uses the last record's value.
- Otherwise the records are aligned to the simulation by the first record's year. Years before the first record use the first value, and years after the last record repeat the last value.

The alignment counts records from the first one, so the years must be consecutive.

`co2.out` has the header `YR    CO2(ppm)` and one line per simulation year with the calendar year and the CO2 value used.

## object.prt

Hydrograph and state output for individual objects. Each line asks for one variable of one object, written daily to a separate file. The file name is the third entry on the `simulation` line of [`file.cio`](file-cio.md) (default `object.prt`; `null` for none).

Free format. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one request.

| # | Column | Description |
|---|--------|-------------|
| 1 | `id` | Sequence number, 1, 2, 3, ... in order. |
| 2 | `obj_typ` | Object type: `hru`, `hlt` (HRU-lte), `ru` (routing unit), `res`, `cha` (channel), `sdc` (SWAT-DEG channel), `exc` (export coefficient), `dr` (delivery ratio) or `out` (outlet). |
| 3 | `obj_typ_no` | Object number within its type. For `hru` with `sol_water` or `solnut_ly`, 0 writes every HRU. |
| 4 | `hyd_typ` | Variable (see below). |
| 5 | `filename` | Output file name, up to 26 characters. |

| `hyd_typ` | Output |
|-----------|--------|
| `tot` | total outflow hydrograph |
| `rhg` | recharge (percolation) hydrograph |
| `sur` | surface runoff hydrograph |
| `lat` | lateral flow hydrograph |
| `til` | tile flow hydrograph |
| `sol_water` | soil water of each layer |
| `solnut_ly` | soil N and P pools of each layer (no header line) |
| `solnut_pr` | soil N and P pools of the profile (no header line) |
| `plant` | plant status |
| `cha_fp` | channel and floodplain water balance |

Each requested file gets a header line (except `solnut_ly` and `solnut_pr`) and one line per day with day of year, month, day, year, object type and name, followed by the values.

??? quote "Sources"

    - `management.sch` readers: [`mgt_read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_mgtops.f90) (schedule and automatic operation lines), [`read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/read_mgtops.f90) (operation lines and name lookups)
    - Schedule types: [`mgt_operations_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operations_module.f90)
    - Running scheduled operations: [`mgt_operatn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operatn.f90), [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90), called from [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Starting operation and year-end `skip` handling: [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90), [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)
    - Automatic operation lookup: [`proc_cond.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cond.f90); generic crop tables: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Curve number change: [`chg_par.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/chg_par.f90)
    - `puddle.ops`: [`mgt_read_puddle.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_puddle.f90)
    - `transplant.ops`: [`plant_transplant_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_transplant_read.f90), [`mgt_transplant.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_transplant.f90), type `plant_transplant_db` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90)
    - CO2: [`co2_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/co2_read.f90), `bsn_prm%co2` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - `object.prt`: [`object_read_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/object_read_output.f90), [`obj_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/obj_output.f90), type `object_output` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - File name slots: `in_lum%management_sch` and `in_sim%object_prt` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `management.sch` | `numb_ops`, `numb_auto` | `sched%num_ops`, `sched%num_autos` |
    | `management.sch` | automatic operation line | `sched%auto_name`, `sched%auto_crop` |
    | `management.sch` | `op_typ`, `mon`, `day` | `mgt_ops%op`, `%mon`, `%day` |
    | `management.sch` | `hu_sch` | `mgt_ops%husc` |
    | `management.sch` | `op_data1`, `op_data2`, `op_data3` | `mgt_ops%op_char`, `%op_plant`, `%op3` |
    | `puddle.ops` | `hydcon_mm/h` | `pudl_db%wet_hc` |
    | `transplant.ops` | `lai_ini`, `bm_ini`, `phu_acc_ini` | `transpl%lai`, `%bioms`, `%phuacc` |
    | `co2_yr.dat` | year, CO2 | `co2_inc%co2_yr%iyr`, `%co2` |
    | `object.prt` | `obj_typ`, `obj_typ_no`, `hyd_typ` | `ob_out%obtyp`, `%obtypno`, `%hydtyp` |

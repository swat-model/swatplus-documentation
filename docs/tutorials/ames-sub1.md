---
title: Ames_sub1 walkthrough
description: A walk through the Ames_sub1 reference dataset at revision 62.0.1. Open each input group in file.cio, run the model, read the outputs.
status: review
verified_against:
  - swatplus/refdata/Ames_sub1
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

`Ames_sub1` is the reference dataset used to test SWAT+. It has twelve HRUs near Ames, Iowa, and 46 years of daily simulation (1975 to 2020), with no channels, aquifers or reservoirs. The folder is [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Ames_sub1) in the source repository.

The sections below go through the input files in the order of [`file.cio`](../input-reference/file-cio.md), then run the model and read the outputs, as a second pass after the [Quick start](../getting-started/quick-start-ames.md). Several inputs of this test dataset do not do what their names suggest. They are pointed out where they come up, because they are also the mistakes to look for in a new project.

## file.cio

[`file.cio`](../input-reference/file-cio.md) lists every other input file. Most lines in Ames_sub1 are `null`:

```text
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn    carbon.bsn
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli
connect           hru.con
hru               hru-data.hru
hydrology         hydrology.hyd     topography.hyd
structural        tiledrain.str     septic.str        filterstrip.str   grassedww.str     bmpuser.str
hru_parm_db       plants.plt        fertilizer.frt    tillage.til       pesticide.pes     ...   snow.sno
ops               harv.ops          graze.ops         irr.ops           chem_app.ops      fire.ops   sweep.ops
lum               landuse.lum       management.sch    cntable.lum       cons_practice.lum ovn_table.lum
init              plant.ini         soil_plant.ini
soils             soils.sol         nutrients.sol
decision_table    lum.dtl
regions           ls_unit.ele       ...  aqu_catunit.ele
```

The only spatial objects are HRUs ([`hru.con`](../input-reference/con.md)). There is no routing: each HRU's water, sediment and nutrients leave the model, and the results are read per HRU.

Reference: [file.cio](../input-reference/file-cio.md).

## Simulation settings

### time.sim

```text
day_start  yrc_start   day_end   yrc_end      step
       0      1975         0      2020         0
```

Day 0 at the start and end means 1 January of the first year and 31 December of the last. `step` 0 is a daily time step.

### print.prt

```text
nyskip      day_start  yrc_start  day_end   yrc_end   interval
0           0               1975         0     2020         1
...
objects                  daily       monthly        yearly         avann
hru_wb                       y             n             n             y
hru_nb                       y             n             n             y
hru_ls                       n             n             n             y
hru_pw                       y             n             n             y
hru_cb                       l             y             y             y
hru_cb_vars                  l             y             y             y
```

`nyskip` 0 means no warm-up years are left out of the outputs; for a real project set it to one to three years. Only HRU outputs are listed. Daily water balance, nutrient and plant output is on, and the carbon rows write daily output for each soil layer (`l`), which is what makes this run's output about 9 GB.

### object.cnt

Twelve HRUs and no other objects.

References: [time.sim](../input-reference/time-sim.md), [print.prt](../input-reference/print-prt.md), [object.cnt](../input-reference/object-cnt.md).

## Basin settings

### codes.bsn

```text
pet_file  wq_file  pet  event  crack  swift_out  sed_det  rte_cha  deg_cha  wq_cha  nostress  cn  c_fact  carbon  lapse  uhyd  sed_cha  tiledrain  wtable  soil_p  gampt  atmo_dep  stor_max  i_fpwet  gw_flow  idc_till
null      null     2    0      0      0          0        0        0        0       0         2   0       2       0      1     0        0          0       0       0      0         0         0        0        3
```

- `pet` 2: potential evapotranspiration by the Hargreaves method.
- `cn` 2: read but not used in 62.0.1; the curve number always follows soil water.
- `carbon` 2: the soil carbon model is on, with its parameters from [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md).
- `gampt` 0: curve number runoff (Green and Ampt infiltration is off).

### parameters.bsn and carbon.bsn

Basin-wide parameters and the carbon model coefficients. Ames_sub1 has `1.0` in column 7 of [`parameters.bsn`](../input-reference/parameters-bsn.md), which switches on temperature-dependent pesticide decay.

References: [codes.bsn](../input-reference/codes-bsn.md), [parameters.bsn](../input-reference/parameters-bsn.md), [carbon.bsn](../input-reference/carbon-bsn.md).

## Climate

[`weather-sta.cli`](../input-reference/cli.md#weather-stacli) defines one station:

```text
name        wgn       pcp        tmp        slr   hmd   wnd   wnd_dir   atmo_dep
wgn_sta1    wgn_001   ames.pcp   ames.tem   sim   sim   sim   null      null
```

Precipitation comes from `ames.pcp`. Solar radiation, humidity and wind are generated (`sim`) from the monthly statistics in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli).

Temperature does not come from a file. The station names `ames.tem`, but the temperature file list [`tmp.cli`](../input-reference/cli.md#observed-data-lists) contains only `ames.tmp`, an empty file. The model cannot match the name, writes `ames.tem file not found (tgage)` to `diagnostics.out`, and generates daily temperatures from [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli). The measured record in `ames.tem` is never read. With Hargreaves PET, which depends on temperature, this affects ET as well.

[`hru.con`](../input-reference/con.md) gives each HRU the station name `wgn_01`, which is not the name in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) (`wgn_sta1`). With a single station the model uses it anyway, without a message; in a project with several stations, check that these names match.

References: [weather-sta.cli](../input-reference/cli.md), [*.pcp](../input-reference/pcp.md), [*.tmp](../input-reference/tmp.md), [*.tem](../input-reference/tem.md).

## HRUs

### hru-data.hru

Each row names the records an HRU uses:

```text
id  name      topo          hydro     soil         lu_mgt            soil_plant_init  surf_stor  snow     field
 1  hru0001   topohru0001   hyd0001   soil_01-h1   cosy_lum          soilplant1       null       snow001  null
 2  hru0002   topohru0002   hyd0002   soil_02      mntill_corn_lum   soilplant1       null       snow001  null
...
12  hru0012   topohru0012   hyd0012   soil_12      cosy_lum          soilplant1       null       snow001  null
```

Eleven HRUs use `cosy_lum`, a corn and soybean rotation, and HRU 2 uses `mntill_corn_lum`, continuous corn with reduced tillage. Each HRU has a different soil.

### hydrology.hyd and topography.hyd

HRU hydrology parameters (lateral flow travel time, `esco`, `epco`, `cn3_swf`, `perco`, `latq_co`, ...) and slope, slope length and lateral flow length.

References: [hru-data.hru](../input-reference/hru.md), [hydrology.hyd and topography.hyd](../input-reference/hyd.md).

## Land use and management

[`landuse.lum`](../input-reference/lum.md) links each land use to a management schedule:

| Land use | Schedule in [`landuse.lum`](../input-reference/lum.md) | Used by |
|----------|---------------------------|---------|
| `cosy_lum` | `mgt_01` | HRUs 1 and 3 to 12 |
| `mntill_corn_lum` | `mgt_08` | HRU 2 |
| `cosy_lum2` | `mgt_01A` | no HRU |
| `agrr_lum`, `soyb_lum`, `oats_lum`, `wwht_lum` | `AGRR_rot`, `SOYB_rot`, `OATS_rot`, `WWHT_rot` | no HRU; the schedules are not in [`management.sch`](../input-reference/management.md#managementsch) |

[`management.sch`](../input-reference/management.md#managementsch) contains schedules `mgt_01` to `mgt_12` and `mgt_01A`, each a list of dated operations (tillage, planting, fertilizer, harvest). Two points about the shipped schedules at 62.0.1:

- The fertilizer name in the `fert` rows is one column to the right of where the model reads it, so the model finds no fertilizer and the rows apply nothing, without a message. The [management page](../input-reference/management.md) shows the expected layout.
- [`lum.dtl`](../input-reference/dtl.md) contains a decision table, `irr_year_irr`, meant to limit irrigation to 500 mm a year. At 62.0.1 the yearly total is not reset, so once 500 mm have been applied in total the table stops irrigation for the rest of the run.

References: [landuse.lum](../input-reference/lum.md), [management.sch](../input-reference/management.md), [*.dtl](../input-reference/dtl.md).

## Databases and initial conditions

- [`plants.plt`](../input-reference/plt.md), [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt), [`tillage.til`](../input-reference/til.md), [`pesticide.pes`](../input-reference/pes.md#pesticidepes), [`urban.urb`](../input-reference/str.md#urbanurb), [`septic.sep`](../input-reference/str.md#septicsep), [`snow.sno`](../input-reference/sno.md): parameter databases.
- [`harv.ops`](../input-reference/ops.md#harvops), [`graze.ops`](../input-reference/ops.md#grazeops), [`irr.ops`](../input-reference/ops.md#irrops), [`chem_app.ops`](../input-reference/ops.md#chem_appops), [`fire.ops`](../input-reference/ops.md#fireops), [`sweep.ops`](../input-reference/ops.md#sweepops): parameters of each type of operation.
- [`plant.ini`](../input-reference/ini.md#plantini): the plant community each HRU starts with.
- [`soil_plant.ini`](../input-reference/ini.md#soil_plantini): which nutrient record each HRU's soil starts with.
- [`soils.sol`](../input-reference/sol.md) and [`nutrients.sol`](../input-reference/ini.md#nutrientssol): soil layers and initial nutrient contents.

References: [plants.plt](../input-reference/plt.md), [fertilizer.frt](../input-reference/frt.md), [tillage.til](../input-reference/til.md), [*.ops](../input-reference/ops.md), [soils.sol](../input-reference/sol.md), [initial conditions](../input-reference/ini.md).

## Running the model

Check that there is about 10 GB of free space, or switch off the daily carbon output first (set the `daily` column of `hru_cb` and `hru_cb_vars` to `n` in [`print.prt`](../input-reference/print-prt.md)). Then, from inside the folder:

```bash
path/to/swatplus-62.0.1-gnu-lin_x86_64-Rel
```

The screen shows the date being simulated:

```text
  Original Simulation            1  14  1994 Yr   20 of   46 Time  12:37:36
```

The run took 4 minutes 20 seconds on a recent Linux workstation, most of it spent writing the daily carbon files.

## Outputs

### simulation.out

The last lines should be:

```text
  Original Simulation           12  31  2020 Yr   46 of   46 Time  12:40:12

 Execution successfully completed
```

If the completion line is missing, the run stopped early; the last date shows where.

### diagnostics.out

```text
 DIAGNOSTICS.OUT FILE
 agrr_lum      AGRR_rot      not found in management.sch
 soyb_lum      SOYB_rot      not found in management.sch
 oats_lum      OATS_rot      not found in management.sch
 wwht_lum      WWHT_rot      not found in management.sch
 ames.tem                    file not found (tgage)
```

The first four lines are land uses whose schedules are missing; no HRU uses them, so they do not affect the results. The last line is the temperature file described under [Climate](#climate).

Reference: [Checker and diagnostics](../output-reference/checker-diagnostics.md).

### checker.out

One row per HRU with the main soil and hydrology values the model ended up with:

```text
 sname        hydgrp       zmx    usle_k    sumfc     sumul   usle_p  usle_ls   esco   epco  cn3_swf  perco  latq_co  tiledrain
soil_01-h1    B         2000.0    0.0000  361.500   616.090   1.0000   0.3638 0.9500 1.0000   0.0000 0.5000   0.0100          0
soil_02       B         2000.0    0.0000  361.500   449.038   0.7500   0.3638 0.9500 1.0000   0.0000 0.5000   0.0100          0
soil_03-h3    B         2000.0    0.0000  361.500   610.323   1.0000   0.3638 0.9500 1.0000   0.0000 0.5000   0.0100          0
...
```

`usle_k` is 0 for every soil, so the HRUs produce no sediment. Checking this file for zeros and implausible values is a quick test of any new project.

### hru_wb_aa.txt

The average annual water balance of each HRU. For HRU 1:

| precip | snofall | surq_gen | latq | perc | et |
|--------|---------|----------|------|------|----|
| 952.6 mm | 110.3 mm | 34.7 mm | 0.1 mm | 0.0 mm | 932.5 mm |

Almost all precipitation leaves as ET and nothing percolates. For a real Iowa watershed, ET would be closer to two thirds of precipitation. Comparing the average annual water balance with regional estimates is the first check of any project, and [soft calibration](../calibration/soft-calibration.md) adjusts it.

Columns: [Water balance outputs](../output-reference/water-balance.md).

### Other outputs

- `hru_nb_*`, `hru_ncycle_*`: nutrient balance and nitrogen cycle per HRU.
- `hru_ls_aa.txt`: sediment and nutrient losses per HRU.
- `hru_pw_*`: plant growth and stress per HRU.
- `crop_yld_yr.txt`, `crop_yld_aa.txt`: yields by HRU and crop.
- `mgt_out.txt`: every management operation performed, by date and HRU. Use it to check that the schedules do what was intended.
- `hru_carbvars.txt`, `hru_cflux_stat.txt`, `hru_cpool_stat.txt` and the other carbon files: see [Carbon outputs](../output-reference/carbon.md).

The shipped folder also contains `basin_*` files and others that this run does not write. They are left from earlier model versions; see [Quick start](../getting-started/quick-start-ames.md#before-running).

## Changes to try

- Set `nyskip` to 2 in [`print.prt`](../input-reference/print-prt.md) and compare `hru_wb_aa.txt`.
- Rename `ames.tmp` to `ames.tem` in [`tmp.cli`](../input-reference/cli.md#observed-data-lists) so that the measured temperatures are used, and compare ET.
- Change the PET method in [`codes.bsn`](../input-reference/codes-bsn.md) (`pet` 0 for Priestley-Taylor, 1 for Penman-Monteith); both need solar radiation, humidity and wind, which are generated here. See the [cookbook](../tutorials/cookbook.md).
- Follow the [Carbon notebook](../tutorials/carbon-notebook.md) to plot the carbon output.

??? quote "Sources"

    - Dataset: [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Ames_sub1) at 62.0.1.
    - Run: the 62.0.1 `gnu-lin_x86_64` release executable, 20 October 2026. `diagnostics.out`, `checker.out`, `hru_wb_aa.txt` and the run time are from that run.
    - Fertilizer column: the `fert` case of [`src/mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90) uses `mgt%op1`, the fertilizer matched from `op_data1` (column 5); the Ames `fert` rows have `null` there and the name in `op_data2`. Details on [management.sch](../input-reference/management.md).
    - Station and file name lookups, and the irrigation decision table: see [weather-sta.cli](../input-reference/cli.md) and [decision tables](../input-reference/dtl.md).

---
title: Ames_sub1 walkthrough
description: A slow walk through the Ames_sub1 reference dataset. Open every input group in file.cio, run the model, read the outputs.
status: review
---

`Ames_sub1` is the smallest realistic SWAT+ project in the source tree. One subbasin near Ames, Iowa. Twelve HRUs. Forty-six years of daily climate (1975 to 2020). The folder is at [`swatplus/refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/main/refdata/Ames_sub1).

This page opens every file in the project, in the order SWAT+ reads them, explains what is in it, and then runs the model and reads the outputs. Use it as the second pass over a SWAT+ project after the [Quick start](../getting-started/quick-start-ames.md).

## Prerequisites

- A working SWAT+ executable. See [Install](../getting-started/install.md).
- A local copy of `refdata/Ames_sub1`.

## file.cio: the index of every other input

`file.cio` tells SWAT+ which other files exist. It is the first file the model reads. The literal token `null` means "this slot is not used in this project".

Open `Ames_sub1/file.cio`. The relevant rows for this project are:

```text
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli
connect           hru.con
hru               hru-data.hru
hydrology         hydrology.hyd     topography.hyd
hru_parm_db       plants.plt        fertilizer.frt    tillage.til       pesticide.pes     ...   snow.sno
ops               harv.ops          graze.ops         irr.ops           chem_app.ops      fire.ops   sweep.ops
lum               landuse.lum       management.sch    cntable.lum       cons_practice.lum ovn_table.lum
init              plant.ini         soil_plant.ini
soils             soils.sol         nutrients.sol
decision_table    lum.dtl
regions           ls_unit.ele       ...  aqu_catunit.ele
```

Most slots are `null`. Ames_sub1 has no channels, no reservoirs, no routing units, no aquifer file. It is a pure HRU water-balance run. The `connect` row points to `hru.con` only.

Reference: [file.cio](../input-reference/file-cio.md).

## simulation group

### time.sim

```text
day_start  yrc_start   day_end   yrc_end      step
       0      1975         0      2020         0
```

`step = 0` means a daily time step. `day_start = 0` and `day_end = 0` mean run from January 1 of `yrc_start` to December 31 of `yrc_end`.

Reference: [time.sim](../input-reference/time-sim.md).

### print.prt

The print configuration. The first block sets the warm-up and date window:

```text
nyskip      day_start  yrc_start  day_end   yrc_end   interval
0           0               1975         0     2020         1
```

`nyskip = 0` means no warm-up years are discarded from output. The objects table that follows toggles each output file. In Ames_sub1, every row is set to `aa` only:

```text
objects                  daily       monthly        yearly         avann
basin_wb                     n             n             n             y
hru_wb                       n             n             n             y
...
```

That is why the run produces `*_aa.txt` files and no daily or monthly outputs.

Reference: [print.prt](../input-reference/print-prt.md).

### object.cnt

Counts of objects to allocate. SWAT+ reads this once and sizes its arrays accordingly.

Reference: [object.cnt](../input-reference/object-cnt.md).

## basin group

### codes.bsn

Method switches that apply to the whole basin. Open `codes.bsn` and read row 3:

```text
pet  event  crack  swift_out  sed_det  rte_cha  deg_cha  wq_cha  nostress  cn  c_fact  carbon  lapse  uhyd  sed_cha  tiledrain  wtable  soil_p  gampt  atmo_dep  stor_max  i_fpwet  gw_flow  idc_till
  2      0      0          0        0        0        0       0         0   2       0       1      0     1        0          0       0       0      0         0         0        0        0        3
```

Notable settings for this project:

- `pet = 2`: Hargreaves PET.
- `carbon = 1`: reserved C-FARM slot, which runs no carbon model. The dynamic carbon model now activates on `carbon = 2`; this dataset must be changed to `carbon = 2` to run it.
- `uhyd = 1`: gamma-function unit hydrograph.
- `gampt = 0`: curve-number infiltration (the default).

Reference: [codes.bsn](../input-reference/codes-bsn.md).

### parameters.bsn

Numeric constants used basin-wide (sediment routing coefficients, plant-water-stress thresholds, surface-runoff lag, and so on). The defaults in this file are the same defaults a fresh QSWAT+ project produces.

Reference: [parameters.bsn](../input-reference/parameters-bsn.md).

## climate group

The Ames station has only two climate files: `ames.pcp` (precipitation) and `ames.tem` (temperature, legacy `.tem` extension). The `weather-sta.cli` file lists one station, `weather-wgn.cli` holds the monthly statistical generator for it, and `pcp.cli` and `tmp.cli` are index files that point at `ames.pcp` and `ames.tem` respectively.

PET is computed by Hargreaves (`pet = 2` above), so there is no PET file. Solar radiation, humidity, and wind are generated from the weather generator.

References: [*.cli](../input-reference/cli.md), [*.pcp](../input-reference/pcp.md), [*.tmp](../input-reference/tmp.md), [*.tem](../input-reference/tem.md).

## connect, hru, hydrology groups

### hru.con

The connectivity file for HRU objects. One row per HRU with its area, coordinates, elevation, and the object the HRU drains to. In Ames_sub1 every HRU drains to itself (`hyd_typ = tot` to a downstream object of `null`), so the basin output is the sum of HRU contributions with no routing.

Reference: [*.con](../input-reference/con.md).

### hru-data.hru

The pointer table. Twelve rows, one per HRU. Each row names the topography record, hydrology record, soil, land-use management, soil/plant initialization, surface storage, snow, and field for that HRU:

```text
id  name      topo          hydro     soil      lu_mgt           soil_plant_init  surf_stor  snow     field
 1  hru0001   topohru0001   hyd0001   soil_01-h1   cosy_lum      soilplant1       null       snow001  null
 2  hru0002   topohru0002   hyd0002   soil_02      mntill_corn_lum soilplant1     null       snow001  null
...
12  hru0012   topohru0012   hyd0012   soil_12      cosy_lum      soilplant1       null       snow001  null
```

Eleven of the twelve HRUs are `cosy_lum` (corn-soy rotation). HRU 2 is `mntill_corn_lum` (minimum-till continuous corn). That single contrast is the point of the dataset: the other HRUs differ only in soil.

Reference: [hru-data.hru](../input-reference/hru.md).

### hydrology.hyd, topography.hyd

Per-HRU hydrology and topography parameters. `hydrology.hyd` carries the curve number adjustment, lateral and tile flow coefficients, perco coefficient, ESCO, EPCO, and so on. `topography.hyd` carries slope, slope length, and field length.

## hru_parm_db, ops, lum groups

These are the parameter and operation databases the HRUs and management schedules look things up in.

- `plants.plt`: plant-growth parameters per land cover code.
- `fertilizer.frt`, `tillage.til`, `pesticide.pes`, `urban.urb`, `septic.sep`, `snow.sno`: input databases.
- `harv.ops`, `graze.ops`, `irr.ops`, `chem_app.ops`, `fire.ops`, `sweep.ops`: management operation databases.
- `landuse.lum`: each row binds one `lu_mgt` name (used in `hru-data.hru`) to a CN, a management schedule, a conservation practice, and an n-table.
- `management.sch`: ordered list of operations per management name. The Ames dataset has two: `cosy_lum` (corn-soy rotation) and one continuous-corn variant.
- `cntable.lum`, `cons_practice.lum`, `ovn_table.lum`: lookups referenced by `landuse.lum`.

References: [plants.plt](../input-reference/plt.md), [fertilizer.frt](../input-reference/frt.md), [tillage.til](../input-reference/til.md), [snow.sno](../input-reference/sno.md), [*.ops](../input-reference/ops.md), [landuse.lum](../input-reference/lum.md).

## init, soils, decision_table groups

- `plant.ini` and `soil_plant.ini`: starting conditions for plant biomass, residue, soil water content, soil nutrient pools.
- `soils.sol` and `nutrients.sol`: layered soil profiles and per-layer nutrient pools for each named soil.
- `lum.dtl`: decision tables that govern automatic operations (planting, harvesting) inside the management schedule.

References: [soils.sol](../input-reference/sol.md), [*.dtl](../input-reference/dtl.md).

## carbon database

The dataset ships `carbon = 1` in `codes.bsn`, which is now the reserved C-FARM slot and runs no carbon model. Set `carbon = 2` to activate the dynamic CENTURY/SWAT-C model; coefficients then come from `carbon.bsn` and `carbon_lyr.bsn`, and initial carbon pools from `soil_plant.ini`.

Reference: [carb_coefs.cbn](../input-reference/cbn.md).

## Run the model

From inside the `Ames_sub1` folder:

```bash
./swatplus-<version>-linux-x86_64
```

The console will fill with `Original Simulation  mm  dd  yyyy Yr N of 46`. The full run takes a few seconds on a recent laptop.

## Read the outputs

When the run finishes, the folder contains a new set of files. Start with:

### simulation.out

The last lines should be:

```text
Original Simulation       12  31  2020 Yr   46 of   46 Time   8:49:53

Execution successfully completed
```

If you do not see `Execution successfully completed`, the run aborted. Look at the last simulated day printed and check `diagnostics.out`.

### diagnostics.out

Every line here is a missing reference. The shipped run prints:

```text
DIAGNOSTICS.OUT FILE
corn_lum                CORN_rot     not found in management.sch
agrr_lum                AGRR_rot     not found in management.sch
soyb_lum                SOYB_rot     not found in management.sch
oats_lum                OATS_rot     not found in management.sch
wwht_lum                WWHT_rot     not found in management.sch
ames.tem                             file not found (tgage)
                                     file not found (basins_carbon.tes)
```

The first five lines are land-use entries in `landuse.lum` that reference schedules not present in `management.sch`. They are unused in the run (none of the HRUs use those `lu_mgt` names), so the outputs are still correct. The `ames.tem` line refers to a station gage slot in `weather-sta.cli` that was set; the file exists, but the reader did not match it to the `tgage` slot. `basins_carbon.tes` is an optional carbon test file.

Reference: [Checker and diagnostics](../output-reference/checker-diagnostics.md).

### checker.out

One row per HRU of the resolved soil parameters:

```text
sname     hydgrp  zmx(mm)  usle_k  sumfc(mm)  sumul(mm)  usle_p  usle_ls  esco   epco   cn3_swf  perco  latq_co  tiledrain
soil_01   B       2000.0   0.0     361.5      616.18     1.0     0.3638   0.95   1.0    0.0      0.5    0.01     0
soil_02   B       2000.0   0.0     361.5      445.67     1.0     0.3638   0.95   1.0    0.0      0.5    0.01     0
...
```

In this dataset `usle_k = 0.0` on every HRU. That is a known artifact of the Ames soil definitions; sediment yield will be zero. The `zmx` is 2000 mm on every HRU; the soil rooting depth is taken from `soils.sol`. The `tiledrain` flag is `0` on every HRU.

### basin_wb_aa.txt

The basin-average annual water balance. Columns are documented in [Water balance outputs](../output-reference/water-balance.md). A typical line for Ames_sub1:

```text
precip   snofall  snomlt   surq_gen  latq   wateryld  perc   et       pet
1905.2   220.7    219.997  59.5      0.06   59.6      0.003  1846.4   3464.5
```

Precipitation is 1905 mm, ET is 1846 mm, percolation is essentially zero, and surface runoff is 60 mm. The result is dominated by ET because the basin is small and well-drained and the simulation is at HRU scale only.

### Other outputs

- `hru_wb_aa.txt`: same fields as `basin_wb_aa.txt`, one row per HRU.
- `hru_nb_aa.txt`, `hru_ls_aa.txt`, `hru_pw_aa.txt`: nutrient balance, landscape balance, plant and water stress, per HRU.
- `crop_yld_aa.txt`: average annual yield by HRU and crop.
- `basin_carbon_aa.txt`, `hru_carbon_aa.txt`: carbon outputs (only when `carbon = 2` activates the carbon model).

## What to change next

- Switch the PET method by editing `codes.bsn` (`pet = 0` for Priestley-Taylor, `pet = 1` for Penman-Monteith). See the [cookbook](../tutorials/cookbook.md).
- Turn on daily output by setting `daily` to `y` in `print.prt` for the rows you care about.
- Change `nyskip` in `print.prt` to discard the first few years as warm-up.
- Read the [Carbon notebook](../tutorials/carbon-notebook.md) for plotting the carbon outputs.

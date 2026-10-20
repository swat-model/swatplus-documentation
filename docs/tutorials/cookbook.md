---
title: Cookbook recipes
description: Short edits to an existing SWAT+ project at revision 62.0.1. Change the simulation period, turn on an output, change the PET method, switch to Green-Ampt, add an HRU, switch on the carbon model.
status: review
verified_against:
  - src/time_read.f90
  - src/basin_print_codes_read.f90
  - src/basin_read_cc.f90
  - src/basin_read_objs.f90
  - src/hyd_read_connect.f90
  - src/hru_read.f90
  - src/proc_hru.f90
  - src/carbon_bsn_read.f90
  - src/readcio_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

Six common edits to a SWAT+ project that already runs. Each recipe names the file and the values to change, and what to check after the run. The input reference pages linked from each recipe give the full rules.

## Simulation period

Edit [`time.sim`](../input-reference/time-sim.md):

```text
day_start  yrc_start   day_end   yrc_end      step
       0      1975         0      2020         0
```

- `yrc_start` and `yrc_end` are the first and last calendar years.
- `day_start` is the day of the year the run starts; 0 is read as 1, 1 January.
- `day_end` is the day of the year the run ends in the last year; 0 means 31 December.

To leave warm-up years out of the outputs, keep [`time.sim`](../input-reference/time-sim.md) and set `nyskip` on line 3 of [`print.prt`](../input-reference/print-prt.md) to the number of years to skip. The skipped years are still simulated.

Days outside the measured weather records are generated from [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) without a message, so a period longer than the records still runs. Compare the period with the first and last dates in the `.pcp` and `.tmp` files before reading the results.

References: [time.sim](../input-reference/time-sim.md), [print.prt](../input-reference/print-prt.md#print-period-line-3), [weather outside the observed record](../input-reference/time-sim.md#weather-outside-the-observed-record).

## Daily or monthly output

Each object row of [`print.prt`](../input-reference/print-prt.md) has four switches, for daily, monthly, yearly and average annual files. Set the column to `y` to write that file, for example daily basin water balance:

```text
objects                  daily       monthly        yearly         avann
basin_wb                     y             n             y             y
```

How the rows are read depends on the second value on line 7 (`use_obj_lbls`, labelled `dbout` in files from older Editors):

- `y`: rows are matched by name. A row can be added, removed or moved, and the carbon and gwflow rows can be used.
- `n`: rows are read by position in a fixed order. Do not add, remove or reorder rows: every later row would apply to the wrong output, without a message.

Daily output of many objects over a long period can take several gigabytes, so check the free disk space before a long run. After the run, `files_out.out` lists every output file that was opened.

References: [print.prt](../input-reference/print-prt.md#output-group-rows), [Output naming convention](../output-reference/naming-convention.md).

## PET method

Edit `pet`, the third value in [`codes.bsn`](../input-reference/codes-bsn.md):

| `pet` | Method | Weather it uses |
|-------|--------|-----------------|
| 0 | Priestley-Taylor | temperature and solar radiation |
| 1 | Penman-Monteith | temperature, solar radiation, relative humidity and wind |
| 2 | Hargreaves | temperature |
| 3 | weather station PET | in 62.0.1 this gives Hargreaves PET (see below) |

The PET method does not change which weather files are read. A variable that the station takes from the weather generator (`sim` in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli)) is generated in every case, so Penman-Monteith with generated humidity and wind uses generated values. With `pet` = 3, 62.0.1 replaces the measured station PET with Hargreaves PET before the HRUs use it, so this code gives Hargreaves PET times `pet_co`.

After the run, compare `pet` and `et` in `hru_wb_aa.txt` or `basin_wb_aa.txt` with the earlier run.

References: [PET method](../input-reference/codes-bsn.md#pet-method), [weather-sta.cli](../input-reference/cli.md).

## Green-Ampt infiltration

Three files change:

1. [`codes.bsn`](../input-reference/codes-bsn.md): set `gampt`, the 21st value, to 1.
2. [`time.sim`](../input-reference/time-sim.md): set `step` to the number of time steps per day, for example 24 for hourly steps.
3. The precipitation files: give sub-daily records with the same number of values per day as `step`. With `step` above 1, 62.0.1 does not split a measured daily record over the time steps, so a daily `.pcp` file gives no rain in any time step.

Plant growth, soil water and nutrient cycling still run once a day.

After the run, compare `surq_gen` and `perc` in `basin_wb_aa.txt` with the curve number run.

References: [runoff method](../input-reference/codes-bsn.md#runoff-method), [time step](../input-reference/time-sim.md#time-step), [*.pcp](../input-reference/pcp.md).

## HRU addition

An HRU needs a row in several files. Copy the rows of an existing HRU and change them:

1. [`hru.con`](../input-reference/con.md): add a row with the next `id`. Rows must be numbered 1, 2, 3 and so on in file order. Set `area`, `lat`, `elev`, the `hru` column (the row number of the new HRU in [`hru-data.hru`](../input-reference/hru.md)) and `wst` (a station name in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli)).
2. [`hru-data.hru`](../input-reference/hru.md): add a row whose `topo`, `hydro`, `soil`, `lu_mgt`, `soil_plant_init`, `snow` and `field` names exist in the corresponding files. A misspelled name is not reported: the HRU uses the first record of that file.
3. The HRU's outflow: either give it outflow connections in [`hru.con`](../input-reference/con.md) (`out_tot` and the groups after it), or add it as an element of a routing unit in [`rout_unit.ele`](../input-reference/units.md#rout_unitele) and the element list in [`rout_unit.def`](../input-reference/units.md#rout_unitdef), as in [Osu_1hru](osu-1hru.md#hru-routing-unit-aquifer-and-channel). With neither, its water leaves the model.
4. [`ls_unit.ele`](../input-reference/units.md#ls_unitele) and [`ls_unit.def`](../input-reference/units.md#ls_unitdef), if the project has them: add the HRU as an element. The basin output files (`basin_wb` and the others) are added up from these elements with their `bsn_frac` values as given, so the `bsn_frac` values should add up to 1 after the change.
5. [`object.cnt`](../input-reference/object-cnt.md): add 1 to `hru` and to `obj`.

After the run, `checker.out` has one row per HRU, in HRU order, with the soil and hydrology values the new HRU ended up with. Check `diagnostics.out` for names that were not found, and remember that the `topo`, `hydro`, `soil`, `lu_mgt`, `soil_plant_init` and `snow` names are not checked there.

References: [*.con](../input-reference/con.md), [hru-data.hru](../input-reference/hru.md#name-lookup), [object.cnt](../input-reference/object-cnt.md#object-counts), [print.prt](../input-reference/print-prt.md#output-group-rows).

## Carbon model

The dynamic soil carbon model needs three changes:

1. [`codes.bsn`](../input-reference/codes-bsn.md): set `carbon`, the 14th value, to 2. The value 1 is reserved for C-FARM, which is not implemented, and runs the model with no organic matter cycling at all. Datasets from before revision 62 used 1 for the dynamic model and must be changed.
2. [`file.cio`](../input-reference/file-cio.md): name the carbon file as the third name on the `basin` line, for example `basin codes.bsn parameters.bsn carbon.bsn`.
3. Provide [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) in the project folder. `refdata/Ames_sub1` has both, and they can be copied as a start. SWAT+ stops with an error if either is missing. The old [`carb_coefs.cbn`](../input-reference/cbn.md) is no longer read.

For carbon output, [`print.prt`](../input-reference/print-prt.md) must use `use_obj_lbls` = `y`, and the carbon rows are added by name. The newer rows (`hru_cb_gl`, `hru_cb_lyr`, `hru_cb_cpool` and others) each switch one family of files, and the legacy rows `hru_cb` and `hru_cb_vars` switch the files the [carbon notebook](carbon-notebook.md) reads. Daily per-layer carbon output is large: in Ames_sub1 it makes up most of the 9 GB of a full run, so start with a short period.

After the run, `files_out.out` lists the carbon files that were opened, and [Carbon outputs](../output-reference/carbon.md) describes their columns.

References: [carbon model](../input-reference/codes-bsn.md#carbon-model), [carbon.bsn](../input-reference/carbon-bsn.md), [older file.cio files](../input-reference/file-cio.md#older-filecio-files), [carb_coefs.cbn](../input-reference/cbn.md).

??? quote "Sources"

    - Simulation period: [`time_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_read.f90) sets `time%day_start` to 1 when it is 0 or less.
    - Output rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90) reads the second value of line 7 into `pco%use_obj_labels` and the object rows by position or by name accordingly.
    - `codes.bsn`: [`basin_read_cc.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_cc.f90). Column positions: `pet` 3 (`bsn_cc%pet`), `carbon` 14 (`bsn_cc%cswat`), `gampt` 21 (`bsn_cc%gampt`). PET with `pet` = 3 and sub-daily precipitation: see the Sources sections of [codes.bsn](../input-reference/codes-bsn.md) and [time.sim](../input-reference/time-sim.md).
    - HRUs: connection rows are read by [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90), HRU rows and their name lookups by [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90), counts by [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90), and `checker.out` is written by [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90). Basin output weighting by `bsn_frac`: see [nutrient balance and losses](../output-reference/nutrient-balance.md).
    - Carbon: the `basin` line of `file.cio` is read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90), and `carbon.bsn` and `carbon_lyr.bsn` by [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90).

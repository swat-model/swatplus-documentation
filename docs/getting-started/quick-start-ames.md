---
title: "Quick start: Ames_sub1"
status: review
verified_against:
  - swatplus/refdata/Ames_sub1/file.cio
  - swatplus/refdata/Ames_sub1/print.prt
  - swatplus/refdata/Ames_sub1/time.sim
  - swatplus/refdata/Ames_sub1/object.cnt
  - swatplus/src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

Run a complete SWAT+ simulation with the small reference dataset that comes with the source code.

## The dataset

`Ames_sub1` is a test dataset of 12 HRUs near Ames, Iowa, with no channels, aquifers or reservoirs. It simulates 1 January 1975 to 31 December 2020 on a daily time step. It is used to test the model and has not been calibrated. The folder is in the SWAT+ source repository at [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Ames_sub1).

## Before running

You need:

- the SWAT+ executable (see [Install](install.md));
- a copy of the `Ames_sub1` folder, either from a clone of the source repository or downloaded from the link above;
- about 10 GB of free disk space. With the shipped [`print.prt`](../input-reference/print-prt.md) the run writes daily carbon output for every HRU, about 9 GB in 62.0.1. To keep the output small, change the `daily` column of the `hru_cb` and `hru_cb_vars` rows in [`print.prt`](../input-reference/print-prt.md) from `l` to `n` before running.

The shipped folder already contains output files from earlier model versions (for example `basin_wb_aa.txt`, written in 2024). A run with the shipped [`print.prt`](../input-reference/print-prt.md) does not rewrite them, so check the date in the first line of an output file, or delete the old outputs (`*_aa.txt`, `*_yr.txt`, `*_day.txt`, `*.out`) from your copy before running.

## Running

From a terminal, change into your copy of the folder and run the executable from there:

```bash
# Linux and macOS
cd path/to/Ames_sub1
path/to/swatplus-62.0.1-gnu-lin_x86_64-Rel
```

```bat
:: Windows
cd path\to\Ames_sub1
path\to\swatplus-62.0.1-gnu-win_amd64-Rel.exe
```

SWAT+ reads its inputs from the current folder, so always start it from inside the project folder. The run takes a few minutes; on a recent Linux workstation it took 4 minutes 20 seconds, most of it writing the daily carbon output.

## Output

While it runs, SWAT+ prints the simulation date to the screen:

```
  Original Simulation            1  14  1994 Yr   20 of   46 Time  12:37:36
```

At the end, the screen and `simulation.out` show:

```
 Execution successfully completed
```

and the same line is written to `success.fin`.

With the shipped [`print.prt`](../input-reference/print-prt.md), a 62.0.1 run writes:

| Files | Content |
|-------|---------|
| `hru_wb_day.txt`, `hru_wb_aa.txt` | HRU water balance, daily and average annual |
| `hru_nb_day.txt`, `hru_nb_aa.txt`, `hru_ncycle_day.txt`, `hru_ncycle_aa.txt` | HRU nutrient balance and nitrogen cycle |
| `hru_ls_aa.txt` | HRU sediment and nutrient losses, average annual |
| `hru_pw_day.txt`, `hru_pw_aa.txt` | HRU plant growth and stress |
| `crop_yld_yr.txt`, `crop_yld_aa.txt`, `basin_crop_yld_yr.txt`, `basin_crop_yld_aa.txt` | crop yields |
| `hru_carbvars.txt`, `hru_cbn_lyr.txt`, `hru_seq_lyr.txt`, `hru_cflux_stat.txt`, `hru_cpool_stat.txt`, `hru_n_p_pool_stat.txt`, `hru_org_*_vars.txt`, `hru_plc_stat.txt`, `basin_carbon_all.txt`, `hru_begsim_soil_prop.txt`, `hru_endsim_soil_prop.txt` | carbon and soil organic matter |
| `mgt_out.txt`, `lu_change_out.txt` | management operations performed, land use changes |
| `simulation.out`, `diagnostics.out`, `checker.out`, `erosion.out`, `files_out.out`, `co2.out` | run log, warnings, input summaries |

A few other files appear as well: `paddy_test.csv` (a rice paddy test output written on every run), [`wtps_wuses.wal`](../input-reference/water-allocation.md#wtps_wuseswal) and an empty file named `null`.

Open `hru_wb_aa.txt` to see the average annual water balance of each HRU. For the first HRU in this run:

| precip | surq_gen | latq | perc | et |
|--------|----------|------|------|----|
| 952.6 mm | 34.7 mm | 0.1 mm | 0.0 mm | 932.5 mm |

The columns are described in [Water balance outputs](../output-reference/water-balance.md).

## Warnings in diagnostics.out

`diagnostics.out` lists anything the model could not match while reading the inputs. For `Ames_sub1` at 62.0.1 it contains:

```
 agrr_lum      AGRR_rot      not found in management.sch
 soyb_lum      SOYB_rot      not found in management.sch
 oats_lum      OATS_rot      not found in management.sch
 wwht_lum      WWHT_rot      not found in management.sch
 ames.tem                    file not found (tgage)
```

The first four are land uses in [`landuse.lum`](../input-reference/lum.md) that name management schedules missing from [`management.sch`](../input-reference/management.md#managementsch); no HRU uses those land uses. The last line means the station's temperature file, `ames.tem` in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli), is not in the list in [`tmp.cli`](../input-reference/cli.md#observed-data-lists) (which names `ames.tmp`), so the model generates daily temperatures from the weather generator statistics in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli). The [Ames_sub1 walkthrough](../tutorials/ames-sub1.md#climate) explains both. Check this file after every first run of a new project.

## Troubleshooting

- `Cannot find object.cnt input file`: SWAT+ was started outside the project folder. Change into the folder first.
- `Permission denied` on Linux or macOS: run `chmod +x` on the executable.
- A command or the model stops with no message: check free disk space.
- The run stops early: read `simulation.out`, `diagnostics.out` and `checker.out` for the last message before the stop.

See [FAQ and troubleshooting](../faq-troubleshooting/index.md) for other errors.

## Next

- [Project folder anatomy](project-folder-anatomy.md) explains what each file in the folder does.
- The [Ames_sub1 walkthrough](../tutorials/ames-sub1.md) goes through the dataset file by file.
- [Your first watershed](first-watershed.md) builds a project for a new area.

??? quote "Sources"

    - Dataset: [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Ames_sub1) at 62.0.1 (`object.cnt`: 12 HRUs and no other objects; `time.sim`: 1975 to 2020, daily; `print.prt`: HRU rows only, with `hru_cb` and `hru_cb_vars` daily set to `l`).
    - Run: `swatplus-62.0.1-gnu-lin_x86_64-Rel` from the 62.0.1 release, 20 October 2026. Output size and file list are from that run.
    - Completion message and `success.fin`: [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in). `paddy_test.csv` is opened unconditionally in `main.f90.in` as a temporary paddy output.

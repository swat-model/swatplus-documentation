---
title: Cookbook recipes
description: Short edits to apply to an existing SWAT+ project. Add an HRU, switch PET, switch to Green-Ampt, change the simulation period, enable carbon.
status: review
---

Five common edits to a working SWAT+ project. Each recipe lists the file to open, the line to change, and what to check after running. Every recipe assumes you start from a project that already runs successfully.

## Add a new HRU

You need a new entry in `hru.con`, `hru-data.hru`, and a row in any companion table the new HRU points to that does not yet contain the records (`topography.hyd`, `hydrology.hyd`, `soils.sol`, ...).

1. Open `hru.con`. Append a new row, copying an existing row and bumping the `id`. Edit `area`, `lat`, `lon`, `elev`, and `hru` (the HRU index). Keep `wst` pointed at an existing weather station.
2. Open `hru-data.hru`. Append a row with the same `id` and a new `name`. Point its `topo`, `hydro`, `soil`, `lu_mgt`, `soil_plant_init`, `surf_stor`, `snow`, `field` columns at names that exist in the corresponding tables.
3. Open `object.cnt` and update the `hru` count and `obj` count to reflect the new total.
4. Run. After the run, check `checker.out` for a new row matching the soil name. If `usle_k`, `zmx`, `sumfc` look wrong, your `soils.sol` row is incomplete.

References: [hru-data.hru](../input-reference/hru.md), [*.con](../input-reference/con.md), [object.cnt](../input-reference/object-cnt.md).

## Swap the PET method

`codes.bsn`, field 3 (`pet`):

- `0`: Priestley-Taylor.
- `1`: Penman-Monteith.
- `2`: Hargreaves.
- `3`: read from `pet.cli`.

Edit the value, save, run.

Penman-Monteith needs solar radiation, relative humidity, and wind. If those climate files are absent, the weather generator will fill them in, and the result will not match a station-driven Penman-Monteith run.

Hargreaves needs only minimum and maximum temperature. It is the right choice for sites with minimal climate data.

If you set `pet = 3`, also point `pet_file` (field 1 of `codes.bsn`) at a valid `pet.cli` and provide the daily-PET file it references.

Reference: [codes.bsn](../input-reference/codes-bsn.md).

## Switch to Green-Ampt infiltration

`codes.bsn`, field 21 (`gampt`):

- `0`: curve-number infiltration (default).
- `1`: Green-Ampt with Mein-Larson.

Green-Ampt runs on a sub-daily time step. Set `step` in `time.sim` to a non-zero value (the source supports `step = 24` for hourly). Your precipitation file must contain sub-daily values; a daily `.pcp` will not be disaggregated for you.

After the run, look at `basin_wb_aa.txt`. The split between `surq_gen` and `perc` shifts when the method changes; if it does not, the run is still using curve number.

References: [codes.bsn](../input-reference/codes-bsn.md), [time.sim](../input-reference/time-sim.md).

## Change the simulation period

`time.sim`:

```text
day_start  yrc_start  day_end  yrc_end  step
       0       1975        0     2020       0
```

- `day_start = 0`: start January 1 of `yrc_start`.
- `day_start = N > 0`: start on Julian day N of `yrc_start`.
- `day_end = 0`: end December 31 of `yrc_end`.
- `day_end = N > 0`: end on Julian day N of `yrc_end`.

To shorten a run, change `yrc_start` and `yrc_end`. To set a warm-up that is excluded from the average-annual outputs, leave `time.sim` alone and set `nyskip` in `print.prt`.

Your climate files must contain data for every day of the simulation period. If they do not, SWAT+ writes a "file not found" or runs off the end of the file.

References: [time.sim](../input-reference/time-sim.md), [print.prt](../input-reference/print-prt.md).

## Enable the carbon model

`codes.bsn`, field 14 (`carbon`):

- `0`: static (legacy mineralization).
- `1`: C-FARM.
- `2`: Century.

For `1` or `2`, also:

1. Provide a `carb_coefs.cbn` file in the project folder. The Ames_sub1 dataset ships one you can copy. If `cswat /= 0` and no `carb_coefs.cbn` is present, SWAT+ uses internal defaults and writes a notice to `diagnostics.out`.
2. Confirm `soil_plant.ini` (or `soils.sol`, depending on tool version) carries initial organic carbon by layer. Without realistic initial pools, the first decade of output is transient as pools spin up.
3. Turn on carbon outputs in `print.prt`. Set `hru_cb` and the per-pool outputs (`hru_cbn_lyr`, `hru_cpool_stat`, `hru_cflux_stat`, ...) to `daily` if you want to use the [carbon notebook](../tutorials/carbon-notebook.md).

After the run, `basin_carbon_aa.txt`, `hru_carbon_aa.txt`, and the per-pool files appear in the output folder. If they are missing, the print switches were not on.

References: [codes.bsn](../input-reference/codes-bsn.md), [carb_coefs.cbn](../input-reference/cbn.md), [print.prt](../input-reference/print-prt.md).

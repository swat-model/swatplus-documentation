---
title: Your first watershed
status: review
verified_against:
  - swatplus/src/input_file_module.f90
  - swatplus/src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

The steps below build a SWAT+ project for an area of your choice, run it and look at the output, with what each step produces. They do not go through QSWAT+ screen by screen.

## Requirements

Data:

- A digital elevation model (DEM) covering your area, in a projected coordinate system, with no holes.
- A soil map, either SSURGO (US), HWSD (global), or a custom raster paired with a soil property lookup table.
- A land use map, either NLCD (US), ESA WorldCover (global), or a custom raster paired with a SWAT+ land use lookup table.
- A daily climate record (precipitation and temperature at minimum, optionally solar radiation, wind, humidity) from one or more stations covering the simulation period.
- An outlet point (the gauge or stream location you want to drain to).

Software:

- QGIS with the QSWAT+ plugin, SWAT+ Editor and, for calibration, SWAT+ Toolbox. See [Install](install.md).

## Step 1: Delineate the watershed (QSWAT+)

In QGIS, create a new QSWAT+ project and load the DEM. QSWAT+ will:

1. Fill sinks in the DEM.
2. Compute flow direction and accumulation.
3. Build the stream network at a threshold drainage area you choose.
4. Subdivide the watershed into subbasins at stream junctions.
5. Snap your outlet point to the stream network.

Output: a polygon layer of subbasins and a polyline layer of channels (reaches).

## Step 2: Create HRUs

Overlay the land use map, soil map, and a slope class layer on the subbasins. Each unique combination of (subbasin, land use, soil, slope class) is a candidate HRU. QSWAT+ writes the HRUs and the connectivity files.

You can keep all candidate HRUs (high spatial detail, slow run) or filter by area threshold (faster, less detail).

Output: HRU definitions and `*.con` connectivity files.

## Step 3: Build the input files (SWAT+ Editor)

Open the project in SWAT+ Editor. The editor will:

1. Import climate station data and write the `.cli`, `.pcp`, `.tmp`, and [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) files. Stations without data get filled by the weather generator.
2. Populate soil layer parameters from the soil property table.
3. Populate plant, fertiliser, tillage, and pesticide databases.
4. Let you assign management schedules to each land use.
5. Write the final input folder.

Set the simulation period and choose the outputs. Start the simulation one to three years before the period you want to analyse, and set the number of warm-up years in `nyskip` of [`print.prt`](../input-reference/print-prt.md) so they are left out of the outputs.

Output: a folder of plain-text SWAT+ inputs, ready to run.

## Step 4: Run

Run the model from SWAT+ Editor, or from a terminal inside the project's `TxtInOut` folder:

```bash
cd path/to/your/project/Scenarios/Default/TxtInOut
path/to/swatplus-62.0.1-gnu-lin_x86_64-Rel
```

Watch for the `Execution successfully completed` message. Then read `diagnostics.out`: it lists every name that could not be matched (a management schedule, a weather station, a plant) and every missing file. Fix those before looking at results.

## Step 5: Look at output

Start with the basin water balance:

```
basin_wb_aa.txt
```

The annual-average precipitation, evapotranspiration, surface runoff, lateral flow, percolation, and water yield should be in the range you expect for your climate. If precipitation is far from the expected value, the weather stations are probably assigned wrongly. If ET takes up nearly all of the precipitation, check land use and plant parameters.

Then look at the channel output (`basin_sd_cha_aa.txt` or the per-channel `channel_sd_aa.txt`) for streamflow.

If you have measured streamflow at the outlet, compare to `channel_sd_day.txt` for the gauge channel.

## Step 6: Calibrate

The first run is rarely a good match to observed data. Move on to [Calibration](../calibration/index.md) to adjust parameters and improve the fit.

## Common first-run problems

- No precipitation anywhere: the climate station coordinates are outside the watershed extent, so QSWAT+ assigned every HRU to the weather generator instead of the station. Check [`weather-sta.cli`](../input-reference/cli.md#weather-stacli).
- Crops never grow: the management schedule is not assigned, or the planting date is outside the simulation period.
- All flow is surface runoff: curve numbers are too high. Check [`cntable.lum`](../input-reference/lum-tables.md#cntablelum) and the soil hydrologic group.
- Streamflow is zero downstream: a channel object has no upstream connection in [`chandeg.con`](../input-reference/con.md) or [`hru.con`](../input-reference/con.md). Inspect the connectivity.

??? quote "Sources"

    - File names and groups: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90). Completion message: [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in).

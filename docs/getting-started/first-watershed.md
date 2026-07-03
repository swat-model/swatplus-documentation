---
title: Your first watershed
status: review
---

This walks through the workflow to build a SWAT+ project for an area of your own, run it, and look at the output. It does not click through QSWAT+ screen by screen. It covers the steps and what each one produces so you know what to expect.

## What you need

Data:

- A digital elevation model (DEM) covering your area, in a projected coordinate system, with no holes.
- A soil map, either SSURGO (US), HWSD (global), or a custom raster paired with a soil property lookup table.
- A land use map, either NLCD (US), ESA WorldCover (global), or a custom raster paired with a SWAT+ land use lookup table.
- A daily climate record (precipitation and temperature at minimum, optionally solar radiation, wind, humidity) from one or more stations covering the simulation period.
- An outlet point (the gauge or stream location you want to drain to).

Software:

- QGIS with the QSWAT+ plugin. See [Install](install.md).
- SWAT+ Editor.
- The SWAT+ executable.

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

1. Import climate station data and write the `.cli`, `.pcp`, `.tmp`, and `weather-wgn.cli` files. Stations without data get filled by the weather generator.
2. Populate soil layer parameters from the soil property table.
3. Populate plant, fertiliser, tillage, and pesticide databases.
4. Let you assign management schedules to each land use.
5. Write the final input folder.

Set the simulation period in `time.sim` (typically include a one- to three-year warm-up at the start) and the output toggles in `print.prt`.

Output: a folder of plain-text SWAT+ inputs, ready to run.

## Step 4: Run

Copy the SWAT+ executable into the project folder. From a terminal:

```bash
cd path/to/your/project
./swatplus-<version>-gnu-lin_x86_64
```

Watch `simulation.out` for the `Execution successfully completed` message. Check `diagnostics.out` and `checker.out` for warnings.

## Step 5: Look at output

Start with the basin water balance:

```
basin_wb_aa.txt
```

The annual-average precipitation, evapotranspiration, surface runoff, lateral flow, percolation, and water yield should be in the range you expect for your climate. If precipitation is wildly off, your climate file mapping is wrong. If ET dominates everything, check land use and plant parameters.

Then look at the channel output (`basin_sd_cha_aa.txt` or the per-channel `channel_sd_aa.txt`) for streamflow.

If you have measured streamflow at the outlet, compare to `channel_sd_day.txt` for the gauge channel.

## Step 6: Calibrate

The first run is rarely a good match to observed data. Move on to [Calibration](../calibration/index.md) to adjust parameters and improve the fit.

## Common first-run problems

- **No precipitation anywhere.** The climate station coordinates are outside the watershed extent, so QSWAT+ assigned every HRU to the weather generator instead of the station. Check `weather-sta.cli`.
- **Crops never grow.** The management schedule is not assigned, or the planting date is outside the simulation period.
- **All flow is surface runoff.** Curve numbers are too high. Check `cntable.lum` and the soil hydrologic group.
- **Streamflow is zero downstream.** A channel object has no upstream connection in `chandeg.con` or `hru.con`. Inspect the connectivity.

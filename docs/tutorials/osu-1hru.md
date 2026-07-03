---
title: Osu_1hru walkthrough
description: A slow walk through the Osu_1hru reference dataset. A single rice-paddy HRU in Korea, run end to end.
status: review
---

`Osu_1hru` is the smallest SWAT+ project that exercises every input group. One HRU, ten hectares, near Osu, Korea. The land use is `rice140_lum` (a 140-day rice rotation). The folder is at [`swatplus/refdata/Osu_1hru`](https://github.com/swat-model/swatplus/tree/main/refdata/Osu_1hru).

Use this dataset when you want to see every input file in `file.cio` populated, but only one HRU to track.

## Prerequisites

- A working SWAT+ executable. See [Install](../getting-started/install.md).
- A local copy of `refdata/Osu_1hru`.

## file.cio: every group used

Unlike Ames_sub1, this project populates almost every slot. Open `Osu_1hru/file.cio`:

```text
simulation        time.sim          print.prt         null              object.cnt
basin             codes.bsn         parameters.bsn
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli           slr.cli           null              wnd.cli
connect           hru.con           null              rout_unit.con     null              aquifer.con       null              null              null      recall.con              null              null              null              chandeg.con
channel           initial.cha       null              null              null              nutrients.cha     channel-lte.cha   hyd-sed-lte.cha
reservoir         initial.res       null              null              sediment.res      nutrients.res     weir.res          wetland.wet       hydrology.wet
routing_unit      rout_unit.def     rout_unit.ele     rout_unit.rtu
hru               hru-data.hru
aquifer           initial.aqu       aquifer.aqu
hydrology         hydrology.hyd     topography.hyd    field.fld
```

The project has channels, aquifers, routing units, reservoirs, recall, and a wetland. Most of those tables are populated with template entries from the SWAT+ Editor; the single HRU in `hru.con` is what actually runs.

Reference: [file.cio](../input-reference/file-cio.md).

## time.sim and print.prt

`time.sim`:

```text
day_start  yrc_start   day_end   yrc_end      step
       1      2010       365      2023         0
```

January 1 2010 through December 31 2023, daily.

`print.prt` has `nyskip = 3`, so the first three years are discarded. The objects table sets `basin_wb` to `yearly` and `avann`. Every other object is `avann` only.

References: [time.sim](../input-reference/time-sim.md), [print.prt](../input-reference/print-prt.md).

## codes.bsn

```text
pet  event  crack  rtu_wq  sed_det  rte_cha  deg_cha  wq_cha  nostress  cn  c_fact  carbon  lapse  uhyd  sed_cha  tiledrain  wtable  soil_p  gampt  atmo_dep  stor_max  i_fpwet
  1      0      0       1        0        0        0       1         0   0       0       0      0     1        0          0       0       0      0          a        0        0
```

Settings worth noting:

- `pet = 1`: Penman-Monteith PET. Needed because the climate has solar radiation, humidity, and wind.
- `rtu_wq = 1`: routing-unit water quality on.
- `wq_cha = 1`: in-stream water quality on.
- `carbon = 0`: legacy static mineralization (no C-FARM, no Century).
- `gampt = 0`: curve-number infiltration.

Reference: [codes.bsn](../input-reference/codes-bsn.md).

## climate

Five climate files for the Imsil station:

- `Imsilpcp.pcp`: daily precipitation.
- `Imsiltmp.tmp`: daily max and min temperature.
- `Imsilsol.slr`: daily solar radiation.
- `Imsilwind.wnd`: daily wind speed.

(Relative humidity is generated from the weather generator.) The index files `pcp.cli`, `tmp.cli`, `slr.cli`, `wnd.cli` each list one filename, and `weather-sta.cli` binds those four index files to the station `s35610n127290e`.

References: [*.cli](../input-reference/cli.md), [*.pcp](../input-reference/pcp.md), [*.tmp](../input-reference/tmp.md).

## hru.con: a single HRU

```text
id  name     gis_id  area  lat       lon         elev    hru  wst              cst  ovfl  rule  out_tot
 1  hru0001       1    10  35.65311  127.36763   350.97   1   s35610n127290e   0    0     0     0
```

Area is 10 ha. `hru = 1` and `wst = "s35610n127290e"` bind this row to HRU 1 and to the weather station. `out_tot = 0` means no downstream routing object: the run produces HRU-scale outputs only.

Reference: [*.con](../input-reference/con.md).

## hru-data.hru

The single HRU points at:

```text
id  name      topo          hydro      soil        lu_mgt        soil_plant_init  surf_stor   snow     field
 1  hru0001   topohru0001   hyd0001    PadHOEGOG   rice140_lum   soilplant1       paddy0001   snow001  null
```

- `soil = PadHOEGOG`: a paddy soil. See `soils.sol`.
- `lu_mgt = rice140_lum`: maps in `landuse.lum` to plant community `rice140_comm` and management schedule `rice140_rot`.
- `surf_stor = paddy0001`: surface-storage record for ponded water. This is what makes it a paddy.

Reference: [hru-data.hru](../input-reference/hru.md).

## landuse.lum and management.sch

`landuse.lum` row for `rice140_lum` binds the HRU to:

- `plnt_com = rice140_comm` (plant community in `plant.ini`).
- `mgt = rice140_rot` (management schedule in `management.sch`).
- `cn2 = rc_strow_g` (curve-number table entry in `cntable.lum`).
- `cons_prac = cross_slope`.
- `ov_mann = convtill_res`.

`management.sch` then describes the 140-day rice rotation: paddy-fill, transplant, fertilize, harvest, drain.

Reference: [landuse.lum](../input-reference/lum.md).

## aquifer.aqu and aquifer.con

`aquifer.aqu` defines twenty shallow aquifer records (`aqu011` through `aqu102`) plus one deep aquifer (`aqu_deep010`). They share identical parameters. The single HRU links to one of them through `aquifer.con` so the percolation has somewhere to go.

Reference: [*.aqu](../input-reference/aqu.md).

## channel-lte.cha and hyd-sed-lte.cha

A template channel table is present so the file structure validates, but with `out_tot = 0` on the HRU, no flow reaches a channel and the channel outputs will be zero.

Reference: [*.cha](../input-reference/cha.md).

## Run the model

```bash
cd path/to/Osu_1hru
./swatplus-<version>-linux-x86_64
```

The run takes a few seconds because there is only one HRU. Watch the console for `Original Simulation` lines.

## Read the outputs

### simulation.out

The last line should be `Execution successfully completed`.

### diagnostics.out

Every line is a missing reference. Expect a long list because the Editor wrote many template channel and aquifer rows whose companion property records do not all exist. The HRU run itself is unaffected.

Reference: [Checker and diagnostics](../output-reference/checker-diagnostics.md).

### checker.out

A single row for `PadHOEGOG`. Confirm `zmx`, `sumfc`, `sumul`, `hydgrp` are reasonable for a paddy.

### basin_wb_aa.txt and basin_wb_yr.txt

Annual and average-annual water balance for the basin. Because there is one HRU, basin equals HRU. Compare `basin_wb_yr.txt` (per-year values) to `basin_wb_aa.txt` (the average over years 4 through 14, since `nyskip = 3`).

### hru_wb_aa.txt

The water-balance row for HRU 1. Look at `irr` (irrigation depth, large for a paddy), `surq_gen` (surface runoff), `et`, `perc`.

### Plant outputs

`crop_yld_aa.txt` reports rice yields by HRU and crop. `hru_pw_aa.txt` carries plant biomass and water-stress days.

## What to change next

- Switch to Hargreaves PET (`pet = 2` in `codes.bsn`). The model will stop reading the solar, humidity, and wind files.
- Turn on daily output for `basin_wb` to inspect the paddy fill and drain pattern through the season.
- Change the simulation period in `time.sim` to a single year for a fast iteration loop.

See the [cookbook](../tutorials/cookbook.md) for these edits.

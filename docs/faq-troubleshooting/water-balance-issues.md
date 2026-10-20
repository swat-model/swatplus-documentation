---
title: Water balance issues
description: Causes of an implausible SWAT+ 62.0.1 water balance, by term: precipitation, runoff, ET, management, percolation, lateral and tile flow, and basin totals.
status: review
verified_against:
  - src/climate_control.f90
  - src/cli_precip_control.f90
  - src/cli_staread.f90
  - src/hru_read.f90
  - src/hru_module.f90
  - src/landuse_read.f90
  - src/basin_output.f90
  - src/lsu_output.f90
  - src/read_mgtops.f90
  - src/mgt_sched.f90
  - src/topohyd_init.f90
  - src/swr_percmicro.f90
  - src/hru_output.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

When a run completes but `basin_wb_aa.txt` or `hru_wb_aa.txt` looks wrong, the cause is usually in the climate inputs, the curve numbers, the management, the soil and hydrology parameters, or the way the basin totals are weighted. This page goes through the water balance term by term. Many of the causes leave no message, so the checks below name the file and column to look at.

Before changing parameters, read `diagnostics.out` and `checker.out` (see [Checker and diagnostics](../output-reference/checker-diagnostics.md#checks-after-a-run)) and the list of [names matched without a message](common-runtime-errors.md#names-matched-without-a-message). An HRU that silently uses the first record of [`landuse.lum`](../input-reference/lum.md), [`soils.sol`](../input-reference/sol.md) or [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) gives a water balance that no parameter change will fix.

## Balance check

For an HRU, landscape unit or the basin, the average annual water balance should close:

$$P + I + Q_{\mathrm{runon}} \approx ET + WYLD + PERC + \Delta SW + \Delta SNO$$

where $P$ is `precip`, $I$ is `irr`, $Q_{\mathrm{runon}}$ is `surq_runon` + `latq_runon`, $ET$ is `et`, $WYLD$ is `wateryld` (`surq_gen` + `latq` + `qtile`), $PERC$ is `perc`, and $\Delta SW$ and $\Delta SNO$ are the changes in soil water and snow over the period. The columns are described in [Water balance outputs](../output-reference/water-balance.md). A large gap points to wetland storage, gwflow exchange or water held in the surface runoff lag. A term that is far from what the climate and land cover suggest points to one of the sections below.

## Precipitation

The `precip` column does not match the observed rainfall.

- **Weather station of the HRU.** Each HRU takes its station from the `wst` column of [`hru.con`](../input-reference/con.md). A name that is not in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli), or a [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) whose stations are not in ascending order of name, gives the HRU the first station in the file, with no message. See [Weather station lookup](../input-reference/con.md#weather-station-lookup).
- **Data file of the station.** A line `file not found (pgage)` in `diagnostics.out` means the station names a precipitation file that is not listed in [`pcp.cli`](../input-reference/cli.md#observed-data-lists), and SWAT+ generates the rainfall from the weather generator on every day. See [Weather station names](common-runtime-errors.md#weather-station-names).
- **Simulation period.** Days before the start or after the end of the record, and days flagged as missing, are generated. See [Weather outside the observed record](../input-reference/time-sim.md#weather-outside-the-observed-record).
- **Sub-daily runs.** With `step` above 1 in [`time.sim`](../input-reference/time-sim.md), a station with daily precipitation records gets no rainfall in its time steps. A sub-daily run needs sub-daily records or generated precipitation. See [Time step](../input-reference/time-sim.md#time-step).

`hru_pw` files and the `precip` column of `hru_wb` show what each HRU received, so compare a few HRUs with the station file before looking further.

## Surface runoff

`surq_gen` is too high or too low.

- **Curve numbers.** The `cn2` column of [`landuse.lum`](../input-reference/lum.md) names a record in [`cntable.lum`](../input-reference/lum-tables.md#cntablelum), and the soil group in [`soils.sol`](../input-reference/sol.md) picks one of its four values. A name that is not found is reported as `not found in cntable.lum`, and the HRU uses the built-in values 30, 55, 70 and 77 for groups A to D. The `hydgrp` column of `checker.out` shows the soil group each HRU uses.
- **Moisture adjustment.** `cn3_swf` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) places the curve number for wet conditions between field capacity (0) and saturation (1). See [Curve number soil water factor](../input-reference/hyd.md#curve-number-soil-water-factor).
- **Runoff method.** `gampt` in [`codes.bsn`](../input-reference/codes-bsn.md) selects the curve number method (0) or Green-Ampt (1), which is meant for sub-daily runs. See [Runoff method](../input-reference/codes-bsn.md#runoff-method).
- **Lag.** `surq_gen` is the runoff after the surface runoff lag and `surq_cont` the runoff generated on the day. A large difference between them in yearly totals means water is held in the lag.

## Evapotranspiration

`et` is too high or too low.

- **PET method.** `pet` in [`codes.bsn`](../input-reference/codes-bsn.md#pet-method): 0 Priestley-Taylor, 1 Penman-Monteith, 2 Hargreaves, 3 the PET file of the station. Penman-Monteith uses solar radiation, humidity and wind, which are generated when the station has no records for them. Compare the `pet` column of the water balance file with a regional estimate.
- **Compensation factors.** `esco` and `epco` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) set how far down the profile soil evaporation and plant uptake can reach. `checker.out` lists the values each HRU uses. See [Soil evaporation](../input-reference/hyd.md#soil-evaporation).
- **Plant cover.** If plants do not grow, `eplant` stays low and more water leaves as soil evaporation, runoff and percolation. Check biomass and LAI in the `hru_pw` files and yields in `crop_yld_aa.txt` (see [Plant and weather](../output-reference/aquifer-reservoir-plant.md#plant-and-weather)).

## Management

Crops do not grow, or grow without fertilizer or harvest.

- A land use whose `mgt` schedule is not in [`management.sch`](../input-reference/management.md#managementsch) is reported as `not found in management.sch`, and its HRUs get no operations. The `Ames_sub1` reference dataset has four such land uses.
- Several operation names are not reported when they are not found: a fertilizer name gives no fertilizer, a harvest operation no harvest, a tillage name no mixing, and a transplant name a plant started from seed. In the `Ames_sub1` reference dataset, the fertilizer names of every `fert` line are in the wrong column, so the dataset applies no mineral fertilizer in 62.0.1. See the [management.sch example](../input-reference/management.md#example).
- Set `mgtout` to `y` in [`print.prt`](../input-reference/print-prt.md) to write `mgt_out.txt`, the log of every operation and decision table action that ran. An operation missing from the log did not happen.

## Percolation

`perc` is close to zero.

`perco` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) limits percolation out of the bottom of the soil profile, and the relation is strongly non-linear: 0.5 lets about 0.5 % of the potential percolation through, 0.9 about 3 %, and only values close to 1 allow free drainage. The value 0.5, used for every HRU in `Ames_sub1`, therefore leaves almost nothing to percolate. See [Percolation from the soil profile](../input-reference/hyd.md#percolation-from-the-soil-profile).

Also check `sumfc` and `sumul` in `checker.out`, the water held at field capacity and saturation over the profile. Values that are the same for every HRU can mean the HRUs all use the first record of [`soils.sol`](../input-reference/sol.md) because their soil names did not match.

## Lateral and tile flow

`latq` or `qtile` is out of range.

- **Lateral flow.** `latq_co` and `lat_ttime` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) scale and delay lateral flow. See [Lateral flow](../input-reference/hyd.md#lateral-flow).
- **Tile drains.** An HRU has a tile drain when the `tile` column of its land use names a record in [`tiledrain.str`](../input-reference/str.md#tiledrainstr). The `tiledrain` column of `checker.out` shows 1 for those HRUs. A decision table `tile_install` action has no effect on an HRU whose land use had no tile record at the start. A tile `lag` of 0.01 h or less keeps tile water in the lag store, so `qtile` stays at zero. See [Tile flow methods](../input-reference/str.md#tile-flow-methods).
- **Septic systems.** In 62.0.1 a septic system adds no water or nutrients to the soil. See [Septic simulation in 62.0.1](../input-reference/str.md#septic-simulation-in-6201).

## Basin totals

The basin or landscape unit values do not match the HRU values.

Basin rows are sums of the HRU values weighted by the `BSN_FRAC` column of [`ls_unit.ele`](../input-reference/units.md#ls_unitele), and landscape unit rows by `RU_FRAC`. 62.0.1 uses these fractions as given, without scaling them to add up to 1. In the `Ames_sub1` reference dataset the 12 `BSN_FRAC` values add up to 2, so every basin water balance, nutrient balance, losses and plant file shows twice the area-weighted HRU average. Set each fraction to the HRU area divided by the basin area, and check that they add up to 1. The basin sum also assumes [`ls_unit.ele`](../input-reference/units.md#ls_unitele) lists one element per HRU, in HRU order. See [Aggregation](../output-reference/water-balance.md#aggregation) and [Nutrient balance and losses](../output-reference/nutrient-balance.md#aggregation).

Routing unit hydrograph files (`ru_*`) add up every hydrograph type of every element: total flow plus the recharge, surface, lateral and tile parts. Their `flo` is therefore larger than the routing unit's outflow, which is in the `hydout` files. See [ru files](../output-reference/hydrographs.md#ru-files).

`flo` in the hydrograph files is a volume in m³ per print step, although the units row gives m³/s. Divide a daily value by 86,400 to compare it with a gauge record. See [Hydrograph columns](../output-reference/hydrographs.md#hydrograph-columns).

## Related files

- [Common runtime errors](common-runtime-errors.md): messages and the names matched without a message.
- [Water balance outputs](../output-reference/water-balance.md): the columns and how they are aggregated.
- [Ames_sub1 tutorial](../tutorials/ames-sub1.md): a worked look at the reference dataset's water balance.
- [Soft calibration](../calibration/soft-calibration.md): adjusting the water balance towards regional targets, once the inputs are right.

??? quote "Sources"

    - Weather station and gage lookup: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90), [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90), [`cli_precip_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_precip_control.f90)
    - HRU and land use name lookup: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90), [`hru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_module.f90), [`landuse_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_read.f90)
    - Operation name lookup and execution: [`read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/read_mgtops.f90), [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90)
    - Percolation: `perco` conversion in [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90), use in [`swr_percmicro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmicro.f90)
    - Basin and landscape unit weighting: [`basin_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_output.f90), [`lsu_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_output.f90)

    | Item | Fortran |
    |------|---------|
    | `BSN_FRAC`, `RU_FRAC` in `ls_unit.ele` | `lsu_elem%bsn_frac`, `lsu_elem%ru_frac` |
    | `perco` | `hyd_db%perco`, converted to `hru%hyd%perco_lim` |
    | HRU name pointers | `hru_db%dbs` (`type hru_databases`, initialised to 1) |

---
title: gwflow
description: Output files of the gridded groundwater module (gwflow), the switches in the gwflow input files and print.prt that control them, and their columns and units.
status: review
verified_against:
  - src/gwflow_output.f90
  - src/gwflow_read.f90
  - src/gwflow_module.f90
  - src/gwflow_simulate.f90
  - src/gwflow_pond.f90
  - src/gwflow_canal_div.f90
  - src/basin_print_codes_read.f90
  - src/basin_read_objs.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The gwflow module simulates groundwater on a grid of cells and replaces the one-dimensional aquifers. It runs when `gw_flow = 1` in [`codes.bsn`](../input-reference/codes-bsn.md) and writes the output files described here. The input files are described on the [gwflow input page](../input-reference/gwflow.md).

The files fall into these groups:

- basin and cell water balance (`gwflow_basin_wb_*`, `gwflow_cell_wb_*`)
- heat and solute balances (`gwflow_basin_heat_*`, `gwflow_basin_sol_*`)
- observation wells (`gwflow_obs_*`)
- HRU pumping (`gwflow_hru_pump_*`)
- diagnostic files for canals, ponds, tiles and channels
- channel hydrograph separation (`gwflow_chan_hydsep_day.txt`)
- the cell definition and the run log, which are always written

## Output switches

The `write_day`, `write_mon`, `write_yr` and `write_aa` flags in [`codes.gw`](../input-reference/gwflow.md#codesgw) (1 on, 0 off) switch the water balance files. The heat and solute balance files follow the same flags, and the hydrograph separation file follows `write_day`. Observation well, pumping and diagnostic output is on by default.

[`print.prt`](../input-reference/print-prt.md) can override these settings with six rows, each with the usual daily, monthly, yearly and average annual flags. The rows are recognised only when [`print.prt`](../input-reference/print-prt.md) uses object labels (`use_obj_lbls = y`). A row that is present replaces the default; a row that is absent leaves it as it is. All overrides are applied before any gwflow output file is opened, so a file that is switched off is not created.

| [`print.prt`](../input-reference/print-prt.md) row | Effect |
|-----------------|--------|
| `gwflow_wb` | each flag switches the water balance file for that interval; heat, solute and hydrograph separation files follow it unless their rows are present |
| `gwflow_heat` | each flag switches the heat balance file for that interval (there is no monthly heat file) |
| `gwflow_solute` | each flag switches the solute balance files for that interval |
| `gwflow_obs` | each flag switches the observation well file for that interval |
| `gwflow_pump` | any flag set to `y` switches on all HRU pumping files |
| `gwflow_flux` | the daily or yearly flag switches on the canal, pond, tile and channel diagnostic files |

Example rows that keep only the monthly water balance and the daily observation wells:

```
objects                  daily       monthly        yearly         avann
gwflow_wb                    n             y             n             n
gwflow_obs                   y             n             n             n
gwflow_pump                  n             n             n             n
gwflow_flux                  n             n             n             n
```

## Basin water balance

`gwflow_basin_wb_day.txt`, `_mon.txt`, `_yr.txt` and `_aa.txt` give the water balance of the whole grid. Volumes are summed over all active cells and divided by the watershed area, so they are in mm over the watershed. Line 1 is a title, line 2 the column header and line 3 the units. The seven leading columns are `jday`, `mon`, `day`, `yr`, `unit`, `gis_id` and `name` (the project name).

The daily file has these columns after the leading ones:

| Column | Units | Description |
|--------|-------|-------------|
| `ts` | day | gwflow time step |
| `vbef` | mm | groundwater volume at the start of the day |
| `vaft` | mm | groundwater volume at the end of the day |
| `recharge` | mm | recharge from the soil profile |
| `gw_et` | mm | groundwater evapotranspiration |
| `gw_sw` | mm | groundwater discharge to channels |
| `sw_gw` | mm | channel seepage to groundwater |
| `sat_excess` | mm | saturation excess flow to the land surface |
| `soil` | mm | groundwater moved into the soil profile |
| `lateral` | mm | net lateral flow between cells |
| `boundary` | mm | exchange across the grid boundary |
| `pump_allo` | mm | pumping for water allocation (irrigation) |
| `pump_ext` | mm | pumping specified in [`pumpex.gw`](../input-reference/gwflow.md#pumpexgw) |
| `tile` | mm | tile drain outflow |
| `reservoir` | mm | exchange with reservoirs |
| `wetland` | mm | exchange with wetlands |
| `canal` | mm | canal seepage |
| `floodplain` | mm | exchange with floodplains |
| `pond` | mm | recharge pond seepage |
| `phytorem` | mm | phreatophyte transpiration |
| `error` | % | volume balance error |
| `sat_frac` | fraction | fraction of active cells with saturation excess flow that day |
| `wt_depth` | m | average depth to the water table (see the note below) |
| `pump_def` | mm | allocation pumping demand that could not be met |

The monthly, yearly and average annual files replace `ts`, `vbef` and `vaft` with `dvol` (change in storage, mm) and drop `error`, `sat_frac` and `wt_depth`. They end with `pump_def` after `phytorem`.

The daily `wt_depth` is the average over the active cells. In the average annual file, `dvol` is the total change in storage over the run divided by the number of years, and every flux is the run total divided by the number of years.

## Cell water balance

`gwflow_cell_wb_day.txt`, `_mon.txt`, `_yr.txt` and `_aa.txt` have one row per active cell per interval. Lines 1 and 2 are notes on units; line 3 is the column header.

| Column | Units | Description |
|--------|-------|-------------|
| `jday`, `mon`, `day`, `yr` | - | date of the row |
| `unit` | - | cell number in the gwflow grid |
| `gis_id` | - | cell ID from the `gis_id` column of [`cells.gw`](../input-reference/gwflow.md#cellsgw) (the gwflow cell shapefile ID) |
| `name` | - | cell name from [`cells.gw`](../input-reference/gwflow.md#cellsgw), such as `cell0001` (first 12 characters) |
| `head` | m | groundwater head |
| `wt_depth` | m | land surface elevation of the cell minus the head |
| `recharge` | m³/day | recharge |
| `gw_et` | m³/day | groundwater evapotranspiration |
| `gw_sw` | m³/day | discharge to channels |
| `sw_gw` | m³/day | channel seepage |
| `sat_excess` | m³/day | saturation excess flow |
| `soil` | m³/day | transfer to the soil profile |
| `lateral` | m³/day | net lateral flow |
| `pump_allo` | m³/day | allocation pumping |
| `pump_ext` | m³/day | specified pumping |
| `tile` | m³/day | tile drain outflow |
| `reservoir` | m³/day | reservoir exchange |
| `wetland` | m³/day | wetland exchange |
| `floodplain` | m³/day | floodplain exchange |
| `canal` | m³/day | canal seepage |
| `pond` | m³/day | recharge pond seepage |
| `phytorem` | m³/day | phreatophyte transpiration |

The monthly, yearly and average annual files give the average daily rate over the interval, so all fluxes stay in m³/day.

`wt_depth` is measured from the cell's land surface elevation, which on a coarse grid represents the valley and not the streambed. Cells along channels can therefore show a deep water table while the head is close to the channel level. This comes from the grid resolution; the head itself is not affected.

## Heat balance

When heat transport is on (`heat = 1` in [`codes.gw`](../input-reference/gwflow.md#codesgw)), `gwflow_basin_heat_day.txt`, `_yr.txt` and `_aa.txt` are written. They follow the daily, yearly and average annual water balance switches, or the `gwflow_heat` row of [`print.prt`](../input-reference/print-prt.md) when it is present; there is no monthly heat file. Values are in MJ.

The daily file has `ts`, `hbef` and `haft` (heat stored at the start and end of the day), then `recharge`, `gw_et`, `gw_sw`, `sw_gw`, `sat_excess`, `soil`, `lateral`, `dispersion`, `boundary`, `pump_allo`, `pump_ext`, `tile`, `reservoir`, `wetland`, `canal`, `floodplain`, `pond`, then `error` (%) and `tavg` (average groundwater temperature, °C). The yearly and average annual files start with `hdel` (change in heat stored) and end at `pond`.
## Solute balances

When solute transport is on (`solute = 1` in [`codes.gw`](../input-reference/gwflow.md#codesgw)), one file per solute and interval is written, named `gwflow_basin_sol_<solute>_<interval>.txt`. Nitrate (`no3`) and phosphorus (`p`) are always included; with salts in the model, `so4`, `ca`, `mg`, `na`, `k`, `cl`, `co3` and `hco3` are added; with constituents, `seo4` and `seo3`. Values are in kg. The interval files follow the water balance switches, or the `gwflow_solute` row of [`print.prt`](../input-reference/print-prt.md) when it is present.

The daily file has `ts`, `mbef` and `maft` (solute mass at the start and end of the day), then `recharge`, `gw_sw`, `sw_gw`, `sat_excess`, `soil`, `advection`, `dispersion`, `react_in`, `react_out`, `mineral`, `sorption`, `pump_allo`, `pump_ext`, `tile`, `reservoir`, `wetland`, `canal`, `floodplain`, `pond` and `error` (%). The monthly, yearly and average annual files start with `delm` (change in mass) and end at `pond`.

## Observation wells

Observation cells are listed as `observation_cell` lines in [`outputs.gw`](../input-reference/gwflow.md#outputsgw). The files `gwflow_obs_day.txt`, `_mon.txt`, `_yr.txt` and `_aa.txt` have one row per observation cell:

| Column | Units | Description |
|--------|-------|-------------|
| `unit` | - | observation well number, in the order listed in [`outputs.gw`](../input-reference/gwflow.md#outputsgw) |
| `gis_id` | - | cell number of the observation cell |
| `name` | - | `obs_0001`, `obs_0002`, ... |
| `head` | m | groundwater head |
| `wt_depth` | m | land surface elevation minus head |
| `temperature` | °C | groundwater temperature; `-99` when heat transport is off |
| `no3` | mg/L | nitrate concentration; `-99` when solute transport is off |
| `p` | mg/L | phosphorus concentration; `-99` when solute transport is off |

The monthly and yearly files give averages over the interval, and the average annual file the average over the run.

## HRU pumping

When pumping for water allocation is simulated, `gwflow_hru_pump_day.txt`, `_mon.txt`, `_yr.txt` and `_aa.txt` report the groundwater pumped for each HRU in the `pump_allo` column. The daily file is in m³/day and lists only HRUs that pumped that day; the monthly and yearly files give totals in m³, and the average annual file m³/yr.

When [`hru_pump.gw`](../input-reference/gwflow.md#hru_pumpgw) lists HRUs to observe, `gwflow_cell_wb_ppag_obs_day.txt` gives their daily pumping in m³, one column per listed HRU. It is written under the same switch as the other pumping files.

## Diagnostic files

These files are written when the related feature is in use and diagnostic output is on (`gwflow_flux`):

| File | Content |
|------|---------|
| `gwflow_canal_wb_day.txt` | daily canal water balance in m³: `diversion`, `storage`, `pond_xfer`, `seepage` |
| `gwflow_canal_sol_day.txt` | daily canal solute balance in kg: `div_mass`, `storage`, `pond_mass`, `seep_mass` for each solute |
| `gwflow_pond_wb_day.txt` | daily recharge pond water balance: `area` (m²), `storage`, `rain`, `div_added`, `evap`, `recharge`, `div_spec`, `div_unsat` (m³) |
| `gwflow_pond_sol_day.txt` | daily pond solute balance: `area`, `storage`, `solute`, `mass`, `div_added`, `recharge` (kg) |
| `gwflow_pond_mass_day.txt`, `gwflow_pond_conc_day.txt` | daily solute mass (kg) and concentration (g/m³), one column per pond |
| `gwflow_tile_group_day.txt` | daily tile flow (m³/s) for each group of tile cells |
| `gwflow_gwsw_group_day.txt` | daily groundwater and channel exchange (m³) for each channel cell group in [`sw_group.gw`](../input-reference/gwflow.md#sw_groupgw) |
| `gwflow_chan_obs_flow_day.txt` | daily groundwater and channel exchange (m³) at the channel cells flagged in [`chancell.gw`](../input-reference/gwflow.md#chancellgw) |
| `gwflow_chan_obs_no3_day.txt` | the same for nitrate (g), when solute transport is on |

When `gwflow.wbgroups` is present, one daily water balance file per cell group is also written, named `gwflow_group_wb_day_` followed by the group number as two characters (a space and the digit for groups 1 to 9). Its columns follow the daily basin file, in m³.

## Hydrograph separation

`gwflow_chan_hydsep_day.txt` is written when daily water balance output is on. It gives, for each channel and day, the flow from each source in m³/s: `surf_runoff`, `lateral`, `gw_discharge`, `stream_seep`, `satex_gw`, `satex_sw` and `tile_drain`.

## Files always written

| File | Content |
|------|---------|
| `gwflow_record` | run log: which input files were found, which features are active, which [`print.prt`](../input-reference/print-prt.md) rows changed the output switches, and error messages from reading |
| `gwflow_cell_definition.txt` | one line per cell: `cell_id`, `row`, `col`, `x_coord`, `y_coord`, `zone`, `status`, `area` |

When [`transit.gw`](../input-reference/gwflow.md#transitgw) is present on a structured grid, `gwflow_transit_cell`, `gwflow_transit_chan` and (with tiles) `gwflow_transit_tile` give travel times in days.

The `head_output_time` lines in [`outputs.gw`](../input-reference/gwflow.md#outputsgw) are still read but no longer produce output; cell heads are in the cell water balance files.

## Related files

- [gwflow input files](../input-reference/gwflow.md)
- [`codes.bsn`](../input-reference/codes-bsn.md): `gw_flow` switch
- [`print.prt`](../input-reference/print-prt.md): output rows
- [Aquifer theory](../model-theory/aquifers.md)

??? quote "Sources"

    - Output file setup and basin, cell, heat, solute and observation writers: [`gwflow_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_output.f90) (`gwflow_output_init`, `gwflow_output_day`, the monthly, yearly and average annual routines, `gwflow_write_celldef`)
    - `codes.gw` flags, `print.prt` overrides, pumping, diagnostic and hydrograph separation file setup: [`gwflow_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_read.f90)
    - Flags and unit numbers: [`gwflow_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_module.f90)
    - Daily simulation, pumping output and the call to the average annual output: [`gwflow_simulate.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_simulate.f90); pond and canal diagnostics in [`gwflow_pond.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_pond.f90) and [`gwflow_canal_div.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_canal_div.f90)
    - `print.prt` rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90); `gwflow_record` opened in [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90)

    | Switch | Fortran variable |
    |--------|------------------|
    | `write_day`, `write_mon`, `write_yr`, `write_aa` in `codes.gw`, or the `gwflow_wb` row | `gwflag_day`, `gwflag_mon`, `gwflag_yr`, `gwflag_aa` |
    | `gwflow_heat` row (default: water balance flags) | `gwflag_heat_day`, `gwflag_heat_yr`, `gwflag_heat_aa` |
    | `gwflow_solute` row (default: water balance flags) | `gwflag_solute_day`, `gwflag_solute_mon`, `gwflag_solute_yr`, `gwflag_solute_aa` |
    | `gwflow_obs` row (default: all on) | `gwflag_obs_day`, `gwflag_obs_mon`, `gwflag_obs_yr`, `gwflag_obs_aa`, and `gwflag_obs` as their maximum |
    | `gwflow_pump`, `gwflow_flux` rows (default: on) | `gwflag_pump`, `gwflag_flux` |
    | hydrograph separation | `hydsep_flag`, set from `gwflag_day` |
    | `heat`, `solute` in `codes.gw` | `gw_heat_flag`, `gw_solute_flag` |

    | Cell file column | Fortran variable |
    |------------------|------------------|
    | `gis_id`, `name` | `cell_gis_id(i)`, `cell_name(i)` (written with `a12`) |
    | `recharge` ... `phytorem` | `gw_hyd_ss(i)%rech`, `gwet`, `gwsw`, `swgw`, `satx`, `soil`, `latl`, `ppag`, `ppex`, `tile`, `resv`, `wetl`, `fpln`, `canl`, `pond`, `phyt` |

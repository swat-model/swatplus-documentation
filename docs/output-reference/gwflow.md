---
title: gwflow
description: 2D groundwater module outputs. Written when codes.bsn enables gwflow and print.prt toggles the gwflow rows.
status: review
verified_against:
  - src/gwflow_output.f90
  - src/gwflow_module.f90
  - src/gwflow_simulate.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The gwflow module writes its own set of output files when `bsn_cc%gwflow = 1` in [`codes.bsn`](../input-reference/codes-bsn.md). Outputs are toggled in [`print.prt`](../input-reference/print-prt.md) via six rows: `gwflow_wb`, `gwflow_flux`, `gwflow_heat`, `gwflow_solute`, `gwflow_obs`, `gwflow_pump`. Each row has the standard daily/monthly/yearly/average-annual flags.

## Source

- Writer: [`src/gwflow_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/gwflow_output.f90)
- Types: [`src/gwflow_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/gwflow_module.f90), `type groundwater_ss` for fluxes
- Simulation-time writes (cell-level): `src/gwflow_simulate.f90`

## Output files

### Water balance

| File | Scope | Aggregation |
|---|---|---|
| `gwflow_basin_wb_day.txt` | basin total | daily |
| `gwflow_basin_wb_mon.txt` | basin total | monthly |
| `gwflow_basin_wb_yr.txt` | basin total | yearly |
| `gwflow_basin_wb_aa.txt` | basin total | annual average |
| `gwflow_cell_wb_day.txt` | per cell | daily |
| `gwflow_cell_wb_mon.txt` | per cell | monthly |
| `gwflow_cell_wb_yr.txt` | per cell | yearly |
| `gwflow_cell_wb_aa.txt` | per cell | annual average |

Columns (in declaration order from `type groundwater_ss`, units `m^3`):

| # | Name | Description |
|---|------|-------------|
| 1 | chng | change in storage (grid summaries only) |
| 2 | rech | recharge |
| 3 | gwet | groundwater ET |
| 4 | gwsw | groundwater discharge to channels |
| 5 | swgw | channel seepage to groundwater |
| 6 | satx | saturation excess flow |
| 7 | soil | groundwater added to the soil profile |
| 8 | latl | lateral flow between cells |
| 9 | disp | dispersion (heat and solute transport) |
| 10 | bndr | boundary exchange |
| 11 | ppag | allocation-driven pumping (irrigation) |
| 12 | ppdf | pumping deficit (unmet demand) |
| 13 | ppex | external pumping |
| 14 | tile | tile drainage outflow |
| 15 | resv | reservoir exchange |
| 16 | wetl | wetland exchange |
| 17 | fpln | floodplain exchange |
| 18 | canl | canal exchange |
| 19 | pond | recharge pond seepage |
| 20 | phyt | phreatophyte transpiration |
| 21 | totl | sum of inputs and outputs |

Per-cell files prepend a cell id and timestamp; basin files aggregate across all cells. The full per-cell water-balance header (`gwflow_cell_wb_*`), verified against `gwflow_output.f90`, is:

```
jday mon day yr unit gis_id name head wt_depth recharge gw_et gw_sw sw_gw sat_excess soil lateral pump_allo pump_ext tile reservoir wetland floodplain canal pond phytorem
```

- `gis_id` is the authoritative cell id carried from the QSWAT+ shapefile; `name` is `cellNNNN` (a 12-character field).
- `head` and `wt_depth` are in metres; the flux columns (`recharge` through `phytorem`) are in m³/day for daily files (monthly files carry the monthly-average daily rate).
- `wt_depth` = cell land-surface elevation − head (depth of the water table below the cell's representative ground surface). It can look deeper at channel/river cells on coarse grids: the cell surface represents the valley, not the streambed, so the depth is measured from the valley rim while the head sits near the channel. This is a grid-resolution reporting effect, not a model error; the head field itself is correct.

### Observation wells

`gwflow_obs_{day,mon,yr,aa}.txt` report state at each observation cell (set via the observation list) for every timestep. Columns:

| Column | Units | Meaning |
|--------|-------|---------|
| `head` | m | Groundwater head |
| `wt_depth` | m | Water-table depth below ground (land-surface elevation − head) |
| `temp` | degC | Groundwater temperature, `-99` when heat transport is off |
| `no3` | mg/L | Nitrate concentration, `-99` when solute transport is off |
| `p` | mg/L | Phosphorus concentration, `-99` when solute transport is off |

### Heat

When the heat transport sub-module is active (`gwflow.heat` is present), the following are written:

| File | Aggregation |
|---|---|
| `gwflow_basin_heat_day.txt` | daily |
| `gwflow_basin_heat_yr.txt` | yearly |
| `gwflow_basin_heat_aa.txt` | annual average |

Columns are the same fields as water balance, reinterpreted as heat fluxes (the writer reuses `type groundwater_ss`). Refer to the model theory page on Aquifers for the heat transport equations.

### Solutes

When solute transport is active (`gwflow.solutes` listing constituents), per-species water-balance-style files are written. Six species are emitted directly by the writer:

| Species | Files |
|---|---|
| Calcium (`ca`) | `gwflow_basin_sol_ca_{day,mon,yr,aa}.txt` |
| Chloride (`cl`) | `gwflow_basin_sol_cl_{day,mon,yr,aa}.txt` |
| Potassium (`k`) | `gwflow_basin_sol_k_{day,mon,yr,aa}.txt` |
| Magnesium (`mg`) | `gwflow_basin_sol_mg_{day,mon,yr,aa}.txt` |
| Sodium (`na`) | `gwflow_basin_sol_na_{day,mon,yr,aa}.txt` |
| Phosphorus (`p`) | `gwflow_basin_sol_p_{day,mon,yr,aa}.txt` |

Columns follow the same `groundwater_ss` field set, interpreted as solute mass fluxes (kg).

### Cell definition

`gwflow_cell_definition.txt` is written once at the start of the run. It maps the grid coordinates to cell IDs and is the key for interpreting any per-cell output.

### Always-on log

`gwflow_record` is a plain-text log opened when `bsn_cc%gwflow = 1`. The simulation banner and per-feature notes are written there. Useful for confirming the gwflow module activated and which sub-features (pumps, ponds, tiles, etc.) loaded.

## print.prt toggles

| Toggle | Files produced |
|---|---|
| `gwflow_wb` | basin and cell water balance |
| `gwflow_flux` | gwflow canal, pond, tile, gwsw, channel observation diagnostics |
| `gwflow_heat` | basin heat balance |
| `gwflow_solute` | basin solute balance for each species |
| `gwflow_obs` | observation well output (when `gwflow.hru_pump_observe` or observation file is set) |
| `gwflow_pump` | per-HRU pumping output |

The aggregation flags on each row (`d`, `m`, `y`, `a`) control which suffix variants are written.

## Related pages

- [`gwflow` input reference](../input-reference/gwflow.md)
- [`codes.bsn`](../input-reference/codes-bsn.md) (`gwflow` switch)
- [`print.prt`](../input-reference/print-prt.md) (output toggles)
- [Model theory: Aquifers](../model-theory/aquifers.md)

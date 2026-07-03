---
title: Overview and Water Balance
description: Land-phase water balance equation used by SWAT+ and where each term is computed.
status: review
---

## Overview

SWAT+ solves a daily water balance for every hydrologic response unit (HRU). The land-phase balance partitions precipitation into surface runoff, lateral flow, percolation, evapotranspiration, and change in soil water storage. Channel routing, aquifer recharge, and reservoir storage build on top of this HRU-level balance. The HRU loop in `hru_control.f90` is the entry point for the daily land-phase calculation.

## Process equations

The daily water balance for an HRU is

```
P = Q_surf + Q_lat + Q_perc + ET + dS
```

| Term | Meaning |
|------|---------|
| `P` | Daily precipitation reaching the soil surface (after canopy interception and snow processes) |
| `Q_surf` | Surface runoff routed to the channel during the day |
| `Q_lat` | Lateral subsurface flow leaving the soil profile |
| `Q_perc` | Percolation below the bottom of the soil profile (recharge to the shallow aquifer) |
| `ET` | Actual evapotranspiration (canopy evaporation, transpiration, soil evaporation, sublimation) |
| `dS` | Change in soil profile water storage for the day |

Subsidiary terms that the model also tracks at the HRU level and accounts for in the balance:

- Tile flow `Q_tile`, computed in the percolation pass.
- Wetland and pothole storage changes (`wet_control`, ponded HRU types).
- Snow water equivalent, accumulated and melted in `sq_snom.f90`.
- Surface runoff stored over one day through the `surlag` lag (`sq_surfst.f90`).

The HRU water balance feeds the basin-scale and channel-scale balances. Outputs at HRU, landscape unit (LSU), and basin levels are written by the `*_output.f90` modules.

## Switches and parameters

| Switch / parameter | File | Effect |
|--------------------|------|--------|
| `bsn_cc%pet` | [`codes.bsn`](../input-reference/codes-bsn.md) | Selects PET method (see [Climate and Weather](climate-weather.md)) |
| `bsn_cc%gampt` | [`codes.bsn`](../input-reference/codes-bsn.md) | Curve number vs Green-Ampt infiltration (see [Hydrology](hydrology.md)) |
| `bsn_cc%rte` | [`codes.bsn`](../input-reference/codes-bsn.md) | Channel routing method |
| `bsn_prm%surlag` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Surface runoff lag, default 4.0 days |
| `bsn_prm%ffcb` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Initial soil water as fraction of field capacity, default 0.0 |
| `hyd_db%esco`, `hyd_db%epco` | `hydrology.hyd` | Soil evap and plant uptake compensation factors |
| `hyd_db%canmx` | `hydrology.hyd` | Maximum canopy storage (mm) |
| `hyd_db%lat_ttime` | `hydrology.hyd` | Lateral flow travel time |

## Implementation

Source modules in `swatplus/src/` that implement the land-phase water balance:

- `hru_control.f90` orchestrates the daily HRU loop: canopy interception, snow, PET, surface runoff, percolation, lateral storage, evapotranspiration, and output accumulation.
- `sq_canopyint.f90` computes canopy interception storage.
- `sq_snom.f90` accumulates and melts snowpack.
- `sq_volq.f90` dispatches to curve number (`sq_daycn.f90`) or Green-Ampt (`sq_greenampt.f90`) for surface runoff.
- `swr_percmain.f90` is the master driver for layered soil percolation and lateral flow; it calls `swr_percmicro.f90`, `swr_percmacro.f90`, and `swr_satexcess.f90`.
- `swr_substor.f90` lags lateral and tile flow on the way to the channel.
- `sq_surfst.f90` applies `surlag` to delay surface runoff over more than one day.
- `et_pot.f90` and `et_act.f90` compute potential and actual evapotranspiration.
- `stor_surfstor.f90` updates surface storage from the depression-storage routine.
- `basin_output.f90`, `hru_output.f90`, and the `*_output.f90` family write the per-object water balance to `output.std` and the individual `*_wb` files.

## Related pages

- [Hydrology](hydrology.md) for surface runoff, lateral flow, percolation, and channel routing.
- [Climate and Weather](climate-weather.md) for the precipitation and PET inputs that drive the balance.
- [Soil Water and Temperature](soil-water-temperature.md) for soil profile storage.
- [Aquifers](aquifers.md) for what happens to `Q_perc` after it leaves the soil profile.
- [`codes.bsn`](../input-reference/codes-bsn.md) and [`parameters.bsn`](../input-reference/parameters-bsn.md) for switches and coefficients.
- [Water balance output](../output-reference/water-balance.md) for the corresponding output files.

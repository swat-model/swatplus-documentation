---
title: Hydrology
description: Surface runoff, lateral flow, percolation, return flow, and channel routing in SWAT+.
status: review
---

## Overview

The hydrology cluster is what moves water from precipitation through HRUs and along the channel network. Each HRU produces surface runoff, lateral subsurface flow, and percolation. Surface runoff and lateral flow lag through storage terms before reaching the receiving channel. Channels route the inflow to the outlet using one of two routing schemes selected by `bsn_cc%rte`.

## Process equations

### Surface runoff: curve number vs Green-Ampt

The infiltration / runoff partition is set by `bsn_cc%gampt` in `codes.bsn`. The dispatch lives in `sq_volq.f90`:

```fortran
if (bsn_cc%gampt == 0) then
  call sq_daycn
else
  call sq_greenampt
end if
```

**Curve number (`bsn_cc%gampt = 0`, daily time step).** The SCS curve number method computed in `sq_daycn.f90`:

```
S = 25400 / CN - 254
Ia = 0.2 * S
Q_surf = (P - Ia)^2 / (P + 0.8 * S)   when P > Ia
       = 0                            otherwise
```

`CN` is updated daily for soil moisture in `sq_dailycn.f90`. The retention `S` shape is set per HRU by `hyd_db%cn3_swf` (soil water at curve number condition III, where 0 = field capacity and 0.99 = near saturation). A separate frozen-soil adjustment uses `bsn_prm%cn_froz` (default 0.000862). For urban HRUs, an impervious-area curve number of 98 is mixed by the impervious fraction `fcimp`.

**Green-Ampt (`bsn_cc%gampt = 1`, sub-daily).** Used when sub-daily precipitation is available. The infiltration rate at cumulative infiltration `F` is

```
f = K * (1 + psi * dtheta / F)
```

with hydraulic conductivity `K`, wetting-front suction `psi`, and initial moisture deficit `dtheta`. The implementation iterates on cumulative infiltration each sub-daily time step in `sq_greenampt.f90`. Initial abstraction for urban HRUs is capped at `bsn_prm%urb_init_abst` (default 1.0 mm).

Surface runoff lag. Generated runoff `Q_surf` is held by `sq_surfst.f90` so that only a fraction reaches the channel on the day of the event:

```
brt = 1 - exp(-surlag / t_conc)
qday = (lagged_storage + Q_surf) * brt
```

`bsn_prm%surlag` (default 4.0 days) and the HRU time of concentration `t_conc` together set `brt`.

### Lateral subsurface flow

Lateral flow is computed layer by layer in `swr_percmicro.f90` from the gravity-drained water above field capacity. Each layer produces a lateral component `latlyr` and a vertical percolation component `sepday`. The layer values are summed into `latq(j)` in `swr_percmain.f90`:

```fortran
latq(j) = latq(j) + latlyr
```

Lateral flow is then lagged across the basin via `swr_substor.f90`:

```
latq_out = lagged_storage * lat_ttime
```

where `hyd_db%lat_ttime` is the lateral travel-time factor read from `hydrology.hyd`. A linear adjustment `hyd_db%latq_co` (default 0.3) scales daily lateral flow.

### Percolation and return flow

The master driver `swr_percmain.f90` walks the soil profile from top to bottom. For each layer:

1. Add gravity-drained water from the overlying layer.
2. Compute `sw_excess = st - fc` (storage above field capacity).
3. Compute layer percolation `sepday` and lateral flow `latlyr` using a storage routing formula with characteristic time `TT = (sat - fc) / K_sat`. The implementation is in `swr_percmicro.f90`; macropore flow is handled in `swr_percmacro.f90`.
4. Subtract `sepday`, `latlyr`, and tile flow from layer storage.

Percolation from the bottom of the soil profile (`sepbtm`) recharges the shallow aquifer. Return flow (baseflow back to the channel) is computed in the aquifer module from the shallow aquifer storage. See [Aquifers](aquifers.md).

Tile drainage from the layer is computed with `swr_drains.f90` (DRAINMOD equations, `bsn_cc%tdrn = 1`) or `swr_origtile.f90` (drawdown-days equation, `bsn_cc%tdrn = 0`). Saturated profile redistribution sits in `swr_satexcess.f90`.

### Channel routing: variable storage vs Muskingum

`bsn_cc%rte` selects the channel routing method:

| `bsn_cc%rte` | Method |
|--------------|--------|
| 0 | Variable storage coefficient |
| 1 | Muskingum |

Both methods run in `ch_rtmusk.f90` (it dispatches on `bsn_cc%rte` inside its sub-daily loop, despite the file name).

**Variable storage.** Outflow at the sub-step is

```
scoef = bsn_prm%scoef * 2 * dt / (2 * ttime + dt)
outflow = scoef * tot_storage
```

The travel time `ttime` is interpolated from the rating curve at the current inflow and outflow. `bsn_prm%scoef` (default 1.0) is the channel storage coefficient.

**Muskingum.** The classical three-coefficient form:

```
O2 = c1 * I2 + c2 * I1 + c3 * O1
```

with `c1`, `c2`, `c3` derived from the Muskingum storage time constant `Km` and weighting factor `X`. `bsn_prm%msk_co1` (default 0.75), `bsn_prm%msk_co2` (default 0.25), and `bsn_prm%msk_x` (default 0.20) control the calibration of `Km` from the bankfull and low-flow reach response times.

Transmission losses are subtracted after routing using the channel bed hydraulic conductivity `sd_ch%chk` over the reach length and wetted perimeter. Reach evaporation uses `bsn_prm%evrch` (default 0.60).

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_cc%gampt` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = curve number; 1 = Green-Ampt |
| `bsn_cc%rte` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = variable storage; 1 = Muskingum |
| `bsn_cc%tdrn` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = drawdown-days tile flow; 1 = DRAINMOD |
| `bsn_cc%wtdn` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | Shallow water table method |
| `bsn_cc%crk` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 1 = compute crack flow |
| `bsn_cc%sed_det` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | Peak rate method (NRCS UH vs half-hour rainfall) |
| `bsn_prm%surlag` | 4.0 days | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Surface runoff lag |
| `bsn_prm%scoef` | 1.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Variable-storage channel coefficient |
| `bsn_prm%msk_co1` | 0.75 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum bankfull storage coefficient |
| `bsn_prm%msk_co2` | 0.25 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum low-flow storage coefficient |
| `bsn_prm%msk_x` | 0.20 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum weighting factor |
| `bsn_prm%evrch` | 0.60 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Reach evaporation adjustment |
| `bsn_prm%cn_froz` | 0.000862 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Frozen soil CN adjustment |
| `bsn_prm%urb_init_abst` | 1.0 mm | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Urban max initial abstraction (Green-Ampt) |
| `bsn_prm%adj_pkr` | 1.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Subbasin peak rate adjustment |
| `bsn_prm%prf` | 484.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Peak rate factor for peak rate equation |
| `bsn_prm%uhalpha` | 1.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Gamma-UH alpha coefficient |
| `hyd_db%cn3_swf` | per HRU | `hydrology.hyd` | Soil water at CN3 |
| `hyd_db%lat_ttime` | per HRU | `hydrology.hyd` | Lateral flow travel time |
| `hyd_db%latq_co` | 0.3 | `hydrology.hyd` | Lateral flow linear adjustment |
| `hyd_db%perco` | per HRU | `hydrology.hyd` | Percolation linear adjustment |

## Implementation

Source modules in `swatplus/src/`:

- `sq_volq.f90` dispatches surface runoff calculation.
- `sq_daycn.f90` computes daily curve-number runoff; `sq_dailycn.f90` adjusts CN for soil moisture each day.
- `sq_greenampt.f90` computes sub-daily Green-Ampt infiltration and runoff.
- `sq_surfst.f90` applies the surface runoff lag.
- `sq_canopyint.f90` removes canopy interception before infiltration.
- `swr_percmain.f90` is the percolation master; `swr_percmicro.f90` handles micropore flow, `swr_percmacro.f90` macropore flow.
- `swr_substor.f90` lags lateral and tile flow.
- `swr_satexcess.f90` redistributes water above saturation.
- `swr_drains.f90` and `swr_origtile.f90` compute tile flow.
- `ch_rtday.f90` routes daily channel flow (older path).
- `ch_rtmusk.f90` runs the sub-daily Muskingum and variable-storage routing.
- `sd_channel_control3.f90` is the master channel control routine.
- `cn2_init.f90` and `cn2_init_all.f90` initialise the curve number per HRU.

## Related pages

- [`codes.bsn`](../input-reference/codes-bsn.md) for routing and runoff switches.
- [`parameters.bsn`](../input-reference/parameters-bsn.md) for routing coefficients.
- [`hru`](../input-reference/hru.md) for HRU pointers to `hydrology.hyd`.
- [Aquifers](aquifers.md) for what happens to percolation after it leaves the soil.
- [Channels](channels.md) for channel geometry and rating curves.
- [Soil Water and Temperature](soil-water-temperature.md) for the soil profile representation.
- [Water balance output](../output-reference/water-balance.md).

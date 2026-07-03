---
title: Aquifers
description: 1D recession aquifer and 2D gwflow cell-based groundwater in SWAT+.
status: review
---

## Overview

The aquifer cluster receives percolation from HRU soil profiles and returns it to channels as baseflow, sends a fraction to deep seepage, and supports root uptake (revap) when the water table is shallow. Two implementations are available. The default is a 1D lumped recession aquifer with one storage per aquifer object. The alternative is the `gwflow` module, a grid-cell groundwater model with explicit head and lateral exchange. `bsn_cc%gwflow` in `codes.bsn` switches between them.

## Process equations

### 1D recession aquifer (`bsn_cc%gwflow = 0`)

The default aquifer object holds a single storage. Each day the recharge from the soil profile is added to storage, then the water table depth, return flow, deep seepage, and revap are computed in `aqu_1d_control.f90`.

**Water table depth.** Storage converts to a water table depth using specific yield:

```
dep_wt = dep_bot - stor / (1000 * spyld)
```

`dep_bot` is the aquifer bottom depth (m), `spyld` is specific yield (m^3/m^3), and `stor` is storage in mm.

**Return flow.** When the water table is at or above the threshold `flo_min`, return flow follows a recession with lag factor `alpha`:

```
flo_new = flo_prev * exp(-alpha) + rchrg * (1 - exp(-alpha))
```

`alpha_e = exp(-alpha)` is precomputed once. Return flow is capped at the available storage. Below the threshold (`dep_wt > flo_min`) return flow is zero.

**Deep seepage.** A fixed fraction of the daily recharge seeps to the deep aquifer:

```
seep = rchrg * seep_frac
```

where `seep_frac` is `aqu_dat%seep` from `aquifer.aqu`.

**Revap.** When the water table is shallower than `revap_min`, plant uptake and evaporation from the aquifer is

```
revap = pet * revap_co
```

capped at storage. Above the threshold revap is zero. `revap_co` and `revap_min` are read from `aquifer.aqu`.

**Nitrate.** Nitrate in recharge water mixes with the aquifer pool. Return flow nitrate is the storage-weighted concentration. A first-order decay uses the half-life `hlife_n` (default 30 days) read from `aquifer.aqu`. Nitrate seepage uses the same concentration applied to the seepage volume.

### 2D gwflow (`bsn_cc%gwflow = 1`)

When `bsn_cc%gwflow = 1` the lumped 1D aquifer is replaced by a cell-based groundwater model. The watershed is discretised into a grid (structured or unstructured) where each active cell carries a head, hydraulic conductivity, specific yield, and a list of connections to neighbour cells. The model couples to channels, reservoirs, wetlands, tile drains, pumping wells, and HRU recharge.

Per-cell state (in `gwflow_module.f90`):

- `head` current simulated head (m)
- `hydc` aquifer hydraulic conductivity (m/day)
- `spyd` specific yield (m^3/m^3)
- `exdp` groundwater ET extinction depth (m)
- `thck` aquifer thickness, `botm` bedrock elevation, `elev` surface elevation
- `stor` available groundwater storage (m^3)

Each day the model:

1. Computes recharge from HRU or LSU connections (`gwflow_rech.f90`).
2. Computes groundwater ET and phreatophyte transpiration (`gwflow_gwet.f90`, `gwflow_phreatophyte.f90`).
3. Exchanges flow with channels using the Darcian conductance derived from the channel bed (`gwflow_channel_exch.f90`).
4. Handles flow to and from reservoirs and ponds (`gwflow_reservoir.f90`, `gwflow_pond.f90`).
5. Handles wetland exchange (`gwflow_wetland.f90`).
6. Handles tile drain capture (`gwflow_tile.f90`).
7. Handles floodplain exchange when channels overflow (`gwflow_floodplain.f90`).
8. Handles canal diversions and external inflows (`gwflow_canal.f90`, `gwflow_canal_div.f90`, `gwflow_canal_ext.f90`).
9. Handles pumping (`gwflow_pump_allo.f90`, `gwflow_pump_ext.f90`).
10. Solves the head at each cell from neighbour conductances and storage change (`gwflow_simulate.f90`).
11. Redistributes saturation-excess water if a cell head exceeds the surface (`gwflow_satexcess.f90`).
12. Routes solutes and heat through cells (`gwflow_solute.f90`, `gwflow_chem.f90`, `gwflow_heat.f90`).

Aquifer-to-channel mapping for the geomorphic baseflow option uses `aqu2d_init.f90` to sort channels by drainage area, allocate flow to channels by length and area, and `aqu2d_read.f90` to read the `aquifer_cha.con` link file.

Boundary conditions are set per cell (`gw_state(i)%stat`): 0 inactive, 1 active, 2 boundary. Constant-head and no-flow types are selected by `bc_type` in the gwflow inputs.

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_cc%gwflow` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = 1D recession aquifer; 1 = `gwflow` grid model |
| `aqu_dat%flo` | 0.05 mm | [`aqu`](../input-reference/aqu.md) | Initial flow from aquifer |
| `aqu_dat%dep_bot` | per aquifer | [`aqu`](../input-reference/aqu.md) | Depth to aquifer bottom (m) |
| `aqu_dat%dep_wt` | per aquifer | [`aqu`](../input-reference/aqu.md) | Initial water table depth (m) |
| `aqu_dat%bf_max` | 0.0 mm | [`aqu`](../input-reference/aqu.md) | Maximum daily baseflow |
| `aqu_dat%alpha` | per aquifer | [`aqu`](../input-reference/aqu.md) | Recession lag factor (1/days) |
| `aqu_dat%revap_co` | per aquifer | [`aqu`](../input-reference/aqu.md) | Revap coefficient |
| `aqu_dat%revap_min` | per aquifer | [`aqu`](../input-reference/aqu.md) | Water table depth threshold for revap (m) |
| `aqu_dat%flo_min` | per aquifer | [`aqu`](../input-reference/aqu.md) | Water table depth threshold for return flow (m) |
| `aqu_dat%seep` | per aquifer | [`aqu`](../input-reference/aqu.md) | Fraction of recharge to deep seepage |
| `aqu_dat%spyld` | per aquifer | [`aqu`](../input-reference/aqu.md) | Specific yield (m^3/m^3) |
| `aqu_dat%hlife_n` | 30 days | [`aqu`](../input-reference/aqu.md) | Half-life of nitrate in groundwater |
| `aqu_dat%no3` | per aquifer | [`aqu`](../input-reference/aqu.md) | Initial NO3-N concentration (ppm) |
| `aqu_dat%minp` | per aquifer | [`aqu`](../input-reference/aqu.md) | Initial mineral P concentration (ppm) |
| `gw_state%hydc` | per cell | gwflow inputs | Hydraulic conductivity (m/day) |
| `gw_state%spyd` | per cell | gwflow inputs | Specific yield (m^3/m^3) |
| `gw_state%exdp` | per cell | gwflow inputs | ET extinction depth (m) |
| `conn_type` | 0 | gwflow inputs | 1 = HRU recharge connections; 2 = LSU |
| `bc_type` | 0 | gwflow inputs | 1 = constant head; 2 = no-flow |

TODO: verify exact column order and defaults in `aquifer.aqu` and the gwflow input files against the corresponding `*_read.f90` readers.

## Implementation

Source modules in `swatplus/src/`:

- `aqu_1d_control.f90` is the master daily driver for the 1D aquifer object. Adds recharge, computes water table, return flow, deep seepage, revap, and nitrate transport.
- `aqu_read.f90` reads `aquifer.aqu` into the `aqudb` and `aqu_dat` arrays.
- `aqu_read_init.f90`, `aqu_read_init_cs.f90` read initial conditions.
- `aqu_initial.f90` and `aqu_initial` set up storage and pre-compute `alpha_e`.
- `aquifer_module.f90` defines `aquifer_database`, `aquifer_data_parameters`, and `aquifer_dynamic` derived types.
- `aquifer_output.f90`, `aqu_pesticide_output.f90`, `aqu_salt_output.f90`, `aqu_cs_output.f90` print aquifer state and constituent outputs.
- `aqu2d_init.f90` orders channels by drainage area and sets up the aquifer-to-channel mapping for the geomorphic baseflow option.
- `aqu2d_read.f90` reads the `aquifer_cha.con` link file.
- `gwflow_module.f90` defines all gwflow state types and arrays.
- `gwflow_read.f90` reads the gwflow grid and parameters.
- `gwflow_simulate.f90` is the daily driver: assembles fluxes and solves for new heads.
- `gwflow_rech.f90` distributes HRU or LSU recharge to cells.
- `gwflow_channel_exch.f90`, `gwflow_chan_read.f90` handle cell-channel exchange.
- `gwflow_floodplain.f90` handles overland exchange with the channel flood plain.
- `gwflow_reservoir.f90`, `gwflow_wetland.f90`, `gwflow_pond.f90` handle waterbody exchange.
- `gwflow_tile.f90` handles tile drainage capture.
- `gwflow_canal.f90`, `gwflow_canal_div.f90`, `gwflow_canal_ext.f90` handle canal networks.
- `gwflow_pump_allo.f90`, `gwflow_pump_ext.f90` handle pumping.
- `gwflow_lateral.f90` handles lateral inflow from non-grid sources.
- `gwflow_soil.f90` couples grid cells back into HRU soil profiles.
- `gwflow_satexcess.f90` handles saturation-excess water when head reaches the surface.
- `gwflow_gwet.f90`, `gwflow_phreatophyte.f90` handle groundwater ET.
- `gwflow_solute.f90`, `gwflow_chem.f90` handle nitrate, salt, and constituent transport.
- `gwflow_heat.f90` handles heat transport.
- `gwflow_output.f90` writes daily, monthly, yearly, and average-annual gwflow output.

## Related pages

- [`codes.bsn`](../input-reference/codes-bsn.md) for the `gwflow` switch.
- [`aqu`](../input-reference/aqu.md) for the 1D aquifer input file.
- [Hydrology](hydrology.md) for percolation that becomes aquifer recharge.
- [Channels](channels.md) for baseflow return to streams.
- [Aquifer, reservoir, and plant output](../output-reference/aquifer-reservoir-plant.md).

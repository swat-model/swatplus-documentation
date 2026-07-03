---
title: Soil Water and Temperature
description: Soil profile representation, available water capacity, and daily soil temperature in SWAT+.
status: review
---

## Overview

Every HRU has a discretised soil profile of up to ten layers. Each layer holds physical properties (depth, bulk density, hydraulic conductivity, sand-silt-clay-rock fractions, organic content) and state variables (water storage, temperature, layer chemistry). The soil profile is the central reservoir for the HRU water balance: surface runoff is partitioned at the top of layer 1, percolation drains the bottom, and lateral and tile flow leave each layer between. Soil temperature is updated daily for each layer and is used to gate decomposition, nitrification, and biological processes.

## Process equations

### Soil layers

The layer geometry is held in `soil_module.f90` (`type soil_profile`). Each layer carries:

- `d` (mm) cumulative depth from surface
- `thick` (mm) layer thickness
- `bd` (Mg/m^3) bulk density (default 1.3, bounded to 2.0)
- `k` (mm/hr) saturated hydraulic conductivity (defaulted by hydrologic group A=50, B=20, C=5, D=2 when missing)
- `awc` (mm/mm) available water capacity, bounded to `[0.005, 0.8]`
- `clay`, `silt`, `sand`, `rock` fractions
- `wp`, `up`, `por`, `fc`, `st` water content terms (see below)

Initialisation lives in `soil_phys_init.f90`. Defaults applied there:

```fortran
wp  = 0.4 * clay * bd / 100         ! wilting point (m^3/m^3)
up  = wp + awc                      ! upper limit (field capacity, m^3/m^3)
por = 1 - bd / 2.65                 ! porosity from bulk density
fc  = thick * (up - wp)             ! field capacity water in mm
st  = fc * ffc                      ! initial layer water as fraction of FC
```

The basin-wide initial soil water fraction `bsn_prm%ffcb` (default 0.0) seeds layer storage at the start of the run.

### Available water capacity

The available water capacity of a layer is the water held between field capacity and wilting point:

```
AWC_layer (mm) = thick * (up - wp) = thick * awc
```

The profile sum is `soil(j)%s%sumfc`. This drives plant water uptake (compared against `epco`) and soil evaporation (compared against `esco`).

### Daily soil water balance

For each layer, the daily update is

```
st(t+1) = st(t) + inflow - percolation - lateral - tile - soil_evap - transpiration
```

Inflow to layer 1 is infiltration `P - Q_surf`. Inflow to deeper layers is percolation from the layer above. Gravity drainage is allowed when `st > fc`. The implementation runs in `swr_percmain.f90` and `swr_percmicro.f90` (see [Hydrology](hydrology.md)).

### Soil temperature

Soil temperature at the centre of each layer is computed daily in `stmp_solt.f90` from the soil surface temperature, an annual mean air temperature, and a depth-dependent damping function.

Maximum damping depth (mm), from bulk density:

```
f  = avbd / (avbd + 686 * exp(-5.63 * avbd))
dp = 1000 + 2500 * f
```

Soil water scaling factor:

```
ww = 0.356 - 0.144 * avbd
wc = sw / (ww * d_bottom)
```

Daily damping depth:

```
b  = ln(500 / dp)
dd = dp * exp(b * ((1 - wc) / (1 + wc))^2)
```

Bare soil surface temperature:

```
st0   = (solrad * (1 - albedo) - 14) / 20
tbare = tave + 0.5 * (tmax - tmin) * st0
```

Cover lagging factor (residue, biomass, snow):

```
cover = above_ground_mass + residue_mass
bcv   = cover / (cover + exp(7.563 - 1.297e-4 * cover))
```

If `sno_mm > 0`, `bcv` is taken as the maximum of the residue and snow lagging factors. Surface temperature with cover:

```
tcov           = bcv * tmp_layer2 + (1 - bcv) * tbare
soil%tmp_srf   = 0.5 * (tbare + tcov)
```

Layer temperature with the lag coefficient `tlag = 0.8`:

```
zd  = depth_center / dd
df  = zd / (zd + exp(-0.8669 - 2.0775 * zd))
tmp = tlag * tmp_prev + (1 - tlag) * (df * (tmp_an - tmp_srf) + tmp_srf)
```

where `tmp_an` is the long-term annual mean air temperature for the WGN station. Layer temperature feeds frozen-soil flags, decomposition rates, and septic system temperature corrections.

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_prm%ffcb` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Initial soil water as fraction of field capacity |
| `bsn_prm%cn_froz` | 0.000862 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Frozen soil CN adjustment for infiltration |
| `bsn_cc%wtdn` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | Shallow water table depth algorithm |
| `hyd_db%esco` | per HRU | `hydrology.hyd` | Soil evaporation compensation factor (0-1) |
| `hyd_db%epco` | per HRU | `hydrology.hyd` | Plant water uptake compensation factor (0-1) |
| `hyd_db%canmx` | per HRU | `hydrology.hyd` | Maximum canopy storage |
| Layer fields `bd`, `awc`, `k`, `clay`, `silt`, `sand`, `rock`, `cbn` | per layer | [`sol`](../input-reference/sol.md) | Soil layer physical properties |

## Implementation

Source modules in `swatplus/src/`:

- `soil_module.f90` defines the `soil_profile` derived type and per-layer physical and chemical fields.
- `soil_phys_init.f90` initialises layer water-retention parameters (wp, up, por, fc, st) and applies the hydrologic-group default conductivities.
- `solt_db_read.f90` reads the soil temperature lookup data.
- `swr_percmain.f90` updates layer water storage through the daily percolation pass.
- `swr_satexcess.f90` redistributes water above saturation.
- `stmp_solt.f90` computes daily soil layer temperatures.
- `basin_sw_init.f90` initialises soil water using `ffcb` at simulation start.
- `et_act.f90` removes soil evaporation from layers using `esco`.
- `albedo.f90` updates surface albedo, which feeds the bare soil temperature.

## Related pages

- [`sol`](../input-reference/sol.md) for the soil layer input file.
- [Hydrology](hydrology.md) for percolation and lateral flow that change layer storage.
- [Plant growth and land use management](plant-growth-lum.md) for transpiration, which removes layer water.
- [Nutrient cycling](nutrient-cycling.md) for layer chemistry and temperature dependence of mineralisation.
- [Carbon](carbon.md) for the Century-style organic matter pools driven by soil temperature.

---
title: Erosion and Sediment
description: HRU sediment yield with MUSLE and channel sediment transport in SWAT+.
status: review
---

## Overview

Soil loss at the HRU is computed with the Modified Universal Soil Loss Equation (MUSLE). The HRU sediment yield is then routed through the channel network, where each reach can erode its bed and banks or deposit suspended sediment. The peak runoff rate that drives MUSLE comes from one of two methods set by `bsn_cc%sed_det`. Channel sediment processes use the rating curve and reach geometry from the SWAT+ degradation channel.

## Process equations

### MUSLE for HRU sediment yield

The MUSLE form used in `ero_ysed.f90`:

```
sed = 10 * (Q_surf * q_peak * A_ha) ^ 0.56 * cklsp
```

| Symbol | Meaning |
|--------|---------|
| `sed` | Daily sediment yield (t) |
| `Q_surf` | Daily surface runoff volume (mm) |
| `q_peak` | Peak runoff rate (m^3/s) |
| `A_ha` | HRU area (ha) |
| `cklsp` | Combined cover (C), management (P), topographic (LS), and soil erodibility (K) factor |

`cklsp` is built per HRU as `cklsp = usle_cfac * usle_mult`, where `usle_mult = K * LS * P * 11.8` is set up at HRU initialisation and `usle_cfac` is the dynamic cover factor from `ero_cfactor.f90`.

The sediment yield is reduced under snow cover using:

```
sed = sed / exp(3 * sno_mm / 25.4)
```

and is set to zero when the snowpack exceeds 100 mm.

For reference, USLE itself is computed alongside for output as `usle = 1.292 * usle_ei * cklsp / 11.8`, where `usle_ei` is the rainfall erosivity from `ero_eiusle.f90`.

### Peak runoff rate

The peak flow `q_peak` is selected by `bsn_cc%sed_det` in `ero_pkq.f90`:

- `bsn_cc%sed_det = 0` (default): NRCS dimensionless unit hydrograph with peak rate factor `bsn_prm%prf` (default 484.0).
- `bsn_cc%sed_det = 1`: half-hour rainfall intensity method using `precip_half_hr` from the climate or WGN data.

NRCS form (default):

```
q_peak (cfs) = prf / 6578.6 * A_ha * qday / tconc
q_peak (cms) = q_peak (cfs) / 35.3
```

Half-hour form:

```
altc      = 1 - exp(2 * tconc * ln(1 - alpha_half))
q_peak    = altc * qday / tconc * A_km^2 / 3.6   (m^3/s)
```

with `alpha_half = precip_half_hr` as a fraction of daily rainfall.

`bsn_prm%adj_pkr` (default 1.0) is the subbasin peak rate adjustment factor.

### Sediment in lateral and tile flow

`swr_latsed.f90` adds a sediment load to the HRU yield from lateral and tile flow:

```
sed_lat = lat_sed * (Q_lat + Q_tile) * A_ha / 100000
```

with `hyd_db%lat_sed` (g/L) read from `hydrology.hyd`. Particle size split (sand, silt, clay, small aggregate, large aggregate) follows the soil texture detachment fractions.

### Overland sediment routing

`ero_ovrsed.f90` partitions HRU sediment yield by particle size class and applies an enrichment ratio. When `bsn_cc%gampt > 0` (sub-daily simulations), the routine also distributes sediment in time using the sub-daily runoff pattern.

### Channel sediment transport

Channel sediment processes run in `sd_channel_sediment3.f90` (the active routine for SWAT+ degradation channels). Two erosion sources and one deposition sink are computed each day.

**Critical velocity for bank erosion** is built from a clay cohesion term and a vegetation cover term:

```
cohesion  = -87.1 + 42.82 * ch_clay - 0.261 * ch_clay^2 + 0.029 * ch_clay^3
veg       = exp(-5 * chd) * 4500 * cov
bd_fac    = max(0.001, 0.03924 * ch_bd * 1000 - 1000)
cohes_fac = 0.021 * cohesion + veg
v_cr      = vcr_coef * log10(2200 * chd) * sqrt(0.0004 * (bd_fac + cohes_fac))
```

with `ch_clay` (channel clay percent), `ch_bd` (channel bed bulk density), `chd` (channel depth), and `cov` (channel cover). The mean reach velocity adjusted for meander curvature is

```
rad_curv = (12 * chw) * sinu^1.5 / (13 * (sinu - 1)^0.5)
v_bend   = v * (1 / rad_curv + 1)
v_rch    = 0.33 * v_bend + 0.66 * v
```

**Bank erosion** is computed when `v_rch > v_cr`:

```
ebank_m = 1 / (1 / v_vc + 1 / m_exhaust)
ebank_t = 1000 * ebank_m * chd * arc_len * ch_bd
```

with `arc_len = 0.25 * chl` and `m_exhaust = 0.0002 * chw`.

**Bed erosion** is allowed when channel slope exceeds an equilibrium slope. Critical shear comes from the median bed particle `d50`. Acting shear is

```
shear_btm = 9800 * dep * chs   (Pa)
```

with `dep` the flow depth and `chs` the channel slope.

**Channel deposition** is taken as a bedload fraction of bank erosion:

```
ch_dep_sed = wash_bed_fr * bank_ero_sed
```

Suspended sediment in the routed hydrograph carries associated organic N and P using channel-specific concentrations (`n_conc`, `p_conc`) and enrichment factors (`n_dep_enr`, `p_dep_enr`).

Note: the legacy `bsn_prm%spcon` and `bsn_prm%spexp` parameters are listed in `basin_module.f90` as "not used". The active sediment routing in `sd_channel_sediment3.f90` is based on the velocity and shear formulation above, not on a sediment transport capacity power law.

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_cc%sed_det` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = NRCS UH peak rate, 1 = half-hour intensity |
| `bsn_cc%gampt` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | Triggers sub-daily sediment distribution when > 0 |
| `bsn_prm%prf` | 484.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Peak rate factor for the NRCS method |
| `bsn_prm%adj_pkr` | 1.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Subbasin peak rate adjustment |
| `bsn_prm%eros_spl` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Splash erosion coefficient (0.9-3.1) |
| `bsn_prm%rill_mult` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Rill erosion coefficient |
| `bsn_prm%eros_expo` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Exponent for overland flow erosion |
| `bsn_prm%c_factor` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Scaling for overland C-factor |
| `bsn_prm%ch_d50` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Median particle diameter of main channel (mm) |
| `hyd_db%lat_sed` | per HRU | `hydrology.hyd` | Sediment concentration in lateral flow (g/L) |
| `hyd_db%erorgn`, `hyd_db%erorgp` | per HRU | `hydrology.hyd` | Organic N and P enrichment ratios |
| `sd_ch%ch_clay`, `ch_bd`, `cov`, `d50`, `vcr_coef`, `wash_bed_fr` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel sediment properties |

## Implementation

Source modules in `swatplus/src/`:

- `ero_ysed.f90` implements MUSLE for HRU daily sediment yield.
- `ero_pkq.f90` computes the peak runoff rate used by MUSLE.
- `ero_cfactor.f90` updates the dynamic cover and management factor.
- `ero_eiusle.f90` computes rainfall erosivity for the reference USLE.
- `ero_ovrsed.f90` distributes sediment in time and by particle size class for sub-daily simulations.
- `swr_latsed.f90` adds sediment from lateral and tile flow to the HRU yield.
- `sd_channel_sediment3.f90` is the active channel sediment routine: bank erosion, bed erosion, deposition, and associated nutrients.
- `sd_channel_control3.f90` is the channel master that calls the sediment routine.
- `nut_psed.f90` handles sediment-bound phosphorus on land.

## Related pages

- [Hydrology](hydrology.md) for surface runoff and peak rate.
- [Channels](channels.md) for reach geometry, rating curve, and routing.
- [`sd-channel`](../input-reference/sd-channel.md) for channel sediment properties.
- [`parameters.bsn`](../input-reference/parameters-bsn.md) for basin-level erosion coefficients.
- [Channel sediment output](../output-reference/channel-sediment-nutrient.md) for the corresponding output.

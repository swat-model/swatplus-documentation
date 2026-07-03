---
title: Climate and Weather
description: Climate inputs, weather generator, and potential evapotranspiration methods in SWAT+.
status: review
---

## Overview

SWAT+ drives the land phase with daily values of precipitation, maximum and minimum temperature, solar radiation, relative humidity, and wind speed. Each variable can come from a gauge file, from the weather generator, or from a mix of the two on a per-station basis. Potential evapotranspiration can be computed inside the model from three methods or read from a daily file.

## Process equations

### Inputs from gauge files

Each weather station listed in `weather-sta.cli` names up to six measured-data files: precipitation (`*.pcp`), temperature (`*.tmp`), solar radiation (`*.slr`), humidity (`*.hmd`), wind (`*.wnd`), and a precomputed PET file (`*.pet`). The strings `null` or a missing file fall back to weather-generator output for that variable. The master index of each measured variable across all stations is held in `pcp.cli`, `tmp.cli`, `slr.cli`, `hmd.cli`, `wnd.cli`, and `pet.cli`.

### Weather generator

Stochastic weather is generated from monthly statistics held in `weather-wgn.cli` (one block per WGN station). Generation routines:

- Precipitation occurrence and amount: `cli_pgen.f90`, sub-daily disaggregation in `cli_pgenhr.f90`.
- Air temperature: `cli_tgen.f90`.
- Solar radiation: `cli_slrgen.f90`.
- Relative humidity: `cli_rhgen.f90`.
- Wind speed: `cli_wndgen.f90`.
- Driver and initialisation: `cli_clgen.f90`, `cli_initwgn.f90`, `cli_weatgn.f90`.

Optional elevation lapsing of precipitation and temperature is applied in `cli_lapse.f90` when `bsn_cc%lapse = 1`, using `bsn_prm%plaps` (mm/km, default 0.0) and `bsn_prm%tlaps` (deg C/km, default 6.5).

### Potential evapotranspiration

The PET method is selected by `bsn_cc%pet` in `codes.bsn`. The dispatch is in `et_pot.f90`:

| `bsn_cc%pet` | Method |
|--------------|--------|
| 0 | Priestley-Taylor |
| 1 | Penman-Monteith |
| 2 | Hargreaves |
| 3 | Read daily PET from file |

Priestley-Taylor (`case (0)` in `et_pot.f90`) uses

```
PET = alpha * (D / (D + g)) * Rn / lambda
```

with `alpha = 1.28`, slope of saturation vapour pressure curve `D`, psychrometric constant `g`, net radiation `Rn`, and latent heat of vaporization `lambda`. Net radiation is built from incoming solar radiation, albedo (with a snow adjustment when `sno_mm > 0.5 mm`), and a net long-wave term.

Penman-Monteith (`case (1)`) uses

```
PET = (D * Rn + rho * g * VPD / rv) / (lambda * (D + g * (1 + rc / rv)))
```

with aerodynamic resistance `rv`, canopy resistance `rc`, air density `rho`, and vapour pressure deficit `VPD`. For the reference PET, `rv = 114 / (u * (170/1000)**0.2)` and `rc = 49 / (1.4 - 0.4 * CO2 / 330)`. Maximum plant ET is computed separately using canopy-specific resistance values.

Hargreaves (`case (2)`) uses

```
PET = 0.0023 * (Ra / lambda) * (Tave + 17.8) * sqrt(Tmax - Tmin)
```

with extraterrestrial radiation `Ra = solradmx * 37.59 / 30`.

The read-in option (`case (3)`) takes the daily PET value from the gauge file pointed to by the station and applies no further computation in this routine. When `bsn_cc%pet == 3`, `pet.cli` is opened in `basin_read_cc.f90`.

A final scaling `pet_day = hru(j)%hyd%pet_co * pet_day` is applied at the bottom of `et_pot.f90`. The basin-level multiplier `bsn_prm%petco_pmpt` (default 100.0, percent) is used during calibration for Penman-Monteith and Priestley-Taylor.

Actual ET (canopy evaporation, transpiration, soil evaporation) is then partitioned in `et_act.f90` against `PET`, `esco`, and `epco`.

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_cc%pet` | 0 (Priestley-Taylor) | [`codes.bsn`](../input-reference/codes-bsn.md) | PET method |
| `bsn_cc%lapse` | 0 (off) | [`codes.bsn`](../input-reference/codes-bsn.md) | Apply elevation lapse to precipitation and temperature |
| `bsn_cc%petfile` | `pet.cli` | [`codes.bsn`](../input-reference/codes-bsn.md) | Name of the PET index file when `pet = 3` |
| `bsn_prm%plaps` | 0.0 mm/km | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Precipitation lapse rate |
| `bsn_prm%tlaps` | 6.5 deg C/km | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Temperature lapse rate |
| `bsn_prm%petco_pmpt` | 100.0 % | [`parameters.bsn`](../input-reference/parameters-bsn.md) | PET adjustment for Penman-Monteith and Priestley-Taylor |
| `bsn_prm%igen` | 5 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Random seed selection for the weather generator |
| `hyd_db%pet_co` | 1.0 | `hydrology.hyd` | Per-HRU PET multiplier |

## Implementation

Source modules in `swatplus/src/`:

- `cli_staread.f90` reads `weather-sta.cli` (the index of weather stations and their measured-data filenames).
- `cli_wgnread.f90` reads `weather-wgn.cli` (the index of WGN station parameter sets).
- `cli_pmeas.f90`, `cli_tmeas.f90`, `cli_smeas.f90`, `cli_hmeas.f90`, `cli_wmeas.f90`, `cli_petmeas.f90` read the measured `*.pcp`, `*.tmp`, `*.slr`, `*.hmd`, `*.wnd`, and `*.pet` files for each station.
- `cli_clgen.f90`, `cli_initwgn.f90`, `cli_weatgn.f90` drive the weather generator. Variable generators: `cli_pgen.f90`, `cli_tgen.f90`, `cli_slrgen.f90`, `cli_rhgen.f90`, `cli_wndgen.f90`.
- `cli_lapse.f90` applies elevation lapsing.
- `cli_precip_control.f90` coordinates daily and sub-daily precipitation steps.
- `et_pot.f90` computes potential ET (Priestley-Taylor, Penman-Monteith, Hargreaves, read).
- `et_act.f90` computes actual ET and partitions soil evaporation across layers.
- `basin_read_cc.f90` opens the PET index file when `bsn_cc%pet == 3`.

## Related pages

- [`codes.bsn`](../input-reference/codes-bsn.md) for PET and lapse switches.
- [`parameters.bsn`](../input-reference/parameters-bsn.md) for lapse rates and PET adjustment.
- [`pcp`](../input-reference/pcp.md), [`tmp`](../input-reference/tmp.md), [`cli`](../input-reference/cli.md) for climate input file formats.
- [Overview and Water Balance](overview-water-balance.md) for how PET feeds the daily HRU balance.

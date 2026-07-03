---
title: Pesticides
description: Pesticide application, foliar and soil decay, partitioning to runoff and percolation.
status: review
---

## Overview

SWAT+ tracks a configurable set of pesticides as constituents. Each pesticide is described by sorption, solubility, half-lives, and (optionally) one or more daughter products. Applications are scheduled by the management table and split between the canopy and the top two soil layers. Once in the system the pesticide decays exponentially on foliage and in the soil, washes off the canopy in rain, leaches with percolation, partitions to runoff water and sediment, and may be taken up by plants. Daughter products are accumulated as the parent decays.

## Process equations

### Application

Per application, ground cover is

```
gc = (1.99532 - erfc(1.333 * lai_sum - 2)) / 2.1
```

clamped to [0, 1]. Of the applied mass `pest_kg`:

- `gc * pest_kg` goes to plant foliage, partitioned among plants in proportion to their LAI
- `(1 - gc) * surf_frac * pest_kg` goes to soil layer 1
- `(1 - gc) * (1 - surf_frac) * pest_kg` goes to soil layer 2

`surf_frac` is the surface application fraction read from `chem_app.ops`. Source: `pest_apply.f90`.

### Decay

First-order decay in soil and on foliage:

```
decay_s = exp(-ln(2) / soil_hlife)
decay_f = exp(-ln(2) / foliar_hlife)
pest(t+1) = pest(t) * decay
```

The decay coefficients `pestcp(k)%decay_s` and `pestcp(k)%decay_f` are pre-computed once from `soil_hlife` and `foliar_hlife` in `pesticide.pst`. Daughter pesticides accumulate decayed mass scaled by the molecular weight ratio:

```
metab_decay = pst_decay * soil_fr * (mol_wt_daughter / mol_wt_parent)
```

Source: `pest_decay.f90`.

### Foliar washoff

Each rain day, a fraction `washoff` of the pesticide on each plant's foliage is washed to soil layer 1:

```
pest_soil = washoff * pl_on
```

`washoff` is per pesticide in `pesticide.pst`. Source: `pest_washp.f90`.

### Soil partitioning

In each layer, the pesticide is split between adsorbed and dissolved phases using a `Kd` partition computed from soil organic carbon:

```
kd   = koc * cbn / 100
zdb1 = ul + kd * bd * thick
```

`koc` is the organic-carbon-normalised partition coefficient. `zdb1` is the effective partitioning depth in mm. The dissolved concentration available for transport is

```
co = pest * (1 - exp(-vf / zdb1)) / vf
co = min(solub / 100, co)
```

where `vf` is total flow through the layer (`prk + flat`, plus `surfq` in layer 1 and `qtile` in the tile layer). Source: `pest_lch.f90`.

### Surface runoff, lateral flow, tile flow, percolation

Surface runoff carries

```
csurf = percop * co
surq  = csurf * surfq
```

Lateral and tile flow use `co` directly (layer 1 lateral uses `csurf`). Percolation moves `co * prk` to the next layer or out of the profile at the bottom layer. `percop` is the basin percolation coefficient (`parameters.bsn`, default 0.5). Source: `pest_lch.f90`.

### Sediment-attached transport

For the top layer, sediment-attached pesticide is

```
conc = 100 * kd * pest / (zdb1 + 1e-10)
sed_pest = 0.001 * sedyld * conc * er / area_ha
```

The enrichment ratio `er` is either the channel-specific `erorgn` or the CREAMS-derived value from `pest_enrsb.f90`. Source: `pest_pesty.f90`.

### Plant uptake

Daily uptake from each layer is proportional to water uptake by the plant:

```
pest_up = pl_uptake * uptake(ly) / st(ly) * pest(ly)
```

`pl_uptake` is the per-pesticide fraction in `pesticide.pst`. Pesticide on the plant is removed in harvest in proportion to the harvested biomass fraction. Source: `pest_pl_up.f90`, `mgt_harvgrain.f90`.

### In-channel and in-aquifer

Channel pesticide reactions use aquatic and benthic half-lives, settling and resuspension velocities, burial, volatilisation, and benthic decay. Source: `ch_rtpest.f90`, `ch_pesticide_module.f90`, `aqu_pesticide_module.f90`, `pest_cha_res_read.f90`.

## Switches and parameters

| File | Field | Default | Effect |
|------|-------|---------|--------|
| `parameters.bsn` | `percop` | 0.5 | Pesticide percolation coefficient (0-1). 0 = no pesticide in surface runoff |
| `pesticide.pst` | `koc` | per pest | Organic-carbon-normalised partition (mL/g) |
| `pesticide.pst` | `washoff` | per pest | Fraction washed from foliage per rain day |
| `pesticide.pst` | `foliar_hlife` | per pest | Foliar half-life (days) |
| `pesticide.pst` | `soil_hlife` | per pest | Soil half-life (days) |
| `pesticide.pst` | `aq_hlife`, `ben_hlife` | per pest | Aquatic and benthic half-lives (days) |
| `pesticide.pst` | `solub` | per pest | Water solubility (mg/L) |
| `pesticide.pst` | `pl_uptake` | per pest | Fraction taken up by plant |
| `pesticide.pst` | `aq_volat`, `aq_resus`, `aq_settle`, `ben_bury` | per pest | Channel kinetics |
| `chem_app.ops` | `surf_frac` | per op | Surface application fraction (rest to layer 2) |
| `pest_hru_aqu.ini` | initial mass | per HRU | Initial pesticide mass per HRU and layer |

## Implementation

Land phase: `pest_apply.f90`, `pest_decay.f90`, `pest_washp.f90`, `pest_lch.f90`, `pest_pesty.f90`, `pest_pl_up.f90`, `pest_enrsb.f90`, `pest_soil_tot.f90`.

Inputs: `pest_parm_read.f90`, `pest_hru_aqu_read.f90`, `pest_metabolite_read.f90`, `pesticide_data_module.f90`.

Constituent driver: `constituent_mass_module.f90`, `cs_db%num_pests` controls activation.

HRU output: `hru_pesticide_output.f90`.

Channel and aquifer: `ch_rtpest.f90`, `ch_pesticide_module.f90`, `aqu_pesticide_module.f90`, `aqu_pest_output_init.f90`, `aqu_pesticide_output.f90`, `pest_cha_res_read.f90`, `cha_pesticide_output.f90`.

The driver in `hru_control.f90` calls (in order) `pest_apply` (via management), then daily: `pest_washp`, `pest_decay`, `pest_lch`, `pest_pesty`, `pest_pl_up`.

## Related pages

- [`parameters.bsn`](../input-reference/parameters-bsn.md)
- [`management.sch`](../input-reference/ops.md)
- [Plant growth](../model-theory/plant-growth-lum.md)
- [Channels](../model-theory/channels.md)
- [Erosion and sediment](../model-theory/erosion-sediment.md)

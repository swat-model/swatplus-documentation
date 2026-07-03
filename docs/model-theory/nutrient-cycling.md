---
title: Nutrient Cycling (N and P)
description: Soil N and P transformations, plant uptake, leaching, fixation, and in-stream nutrient routing with QUAL2E.
status: review
---

## Overview

Nitrogen and phosphorus in SWAT+ move among organic, mineral, and plant pools in each soil layer and are transported to channels by surface runoff, lateral flow, tile drainage, and percolation. Once in a channel they are transformed by the QUAL2E in-stream water quality routines. The legacy soil P model (one stable pool) and the Vadas and White (2010) model (multiple pools) are selectable through `bsn_cc%sol_p_model`.

## Process equations

### Soil pools

Each soil layer carries the following N pools:

- nitrate `mn(k)%no3`
- ammonium `mn(k)%nh4`
- active organic humus N `hact(k)%n`
- stable organic humus N `hsta(k)%n`
- fresh organic residue N (per plant) `pl(ipl)%rsd(k)%n`

P pools per layer:

- labile mineral `mp(k)%lab`
- active mineral `mp(k)%act`
- stable mineral `mp(k)%sta`
- humus organic P `hsta(k)%p`
- fresh residue P `pl(ipl)%rsd(k)%p`

### Combined temperature and moisture factor

Most rates are scaled by a combined factor `csf = sqrt(cdg * sut)` where

```
sut = max(0.05, 0.1 + 0.9 * sqrt(st/fc))
cdg = max(0.1, 0.9 * tmp / (tmp + exp(9.93 - 0.312*tmp)) + 0.1)
```

`st` is soil water, `fc` field capacity, `tmp` layer temperature. Mineralisation only occurs when `tmp > 0`. Source: `nut_nminrl.f90`.

### Humus mineralisation

A fixed fraction `nactfr = 0.02` of organic N is held in the active pool. Flow between the active and stable pools maintains that fraction:

```
rwn = 1e-5 * (hact*n * (1/nactfr - 1) - hsta*n)
```

Active humus N mineralises to nitrate:

```
hmn = cmn * csf * hact%n
```

with `cmn` from `parameters.bsn` (default 0.003). Mineralised P from humus:

```
hmp = 1.4 * hmn * hsta%p / (hsta%n + hact%n)
```

Source: `nut_nminrl.f90`.

### Residue decomposition

For each plant residue pool in each layer:

```
cnr  = rsd%c / rsd%n              # C:N ratio (capped at 500)
cnrf = exp(-0.693 * (cnr - 25)/25)
cpr  = rsd%c / rsd%p              # C:P ratio (capped at 5000)
cprf = exp(-0.693 * (cpr - 200)/200)
ca   = min(cnrf, cprf, 1)
decr = max(decr_min, min(1, rsdco_pl * ca * csf))
decomp = decr * rsd
```

80% of decomposed residue N and P goes to mineral pools (NO3 and labile P), 20% to humus. `rsdco_pl` is per plant (`plants.plt`); `decr_min` is in `parameters.bsn`. Source: `nut_nminrl.f90`, `cbn_rsd_decomp.f90`.

### Nitrification and ammonia volatilisation

Computed in `nut_nitvol.f90`. Temperature factor `tf = 0.41 * (tmp - 5) / 10` activates when `tf >= 0.001`. The water factor `swf` ramps from 0 at wilting point to 1 at field capacity + 25%. The depth factor `dpf = 1 - dmid/(dmid + exp(4.706 - 0.0305*dmid))` increases nitrification with depth and decreases volatilisation. Combined coefficients:

```
akn = tf * swf                 # nitrification
akv = tf * dpf * cecf          # volatilisation (cecf = 0.15)
rnv = nh4 * (1 - exp(-akn - akv))
rnit = rnv * (1 - exp(-akn)) / [(1 - exp(-akn)) + (1 - exp(-akv))]
rvol = rnv - rnit
```

NO3 increases by `rnit`, NH4 decreases by `rnit + rvol`.

### Denitrification

In `nut_nminrl.f90`:

```
if (sut >= sdnco):
    wdn = no3 * (1 - exp(-cdn * cdg * cbn/100))
```

where `cbn` is layer organic carbon (%), `cdn` is the exponential rate coefficient and `sdnco` is the saturation threshold, both in `parameters.bsn`. Defaults: `cdn = 1.40`, `sdnco = 1.30`.

### Nitrate leaching and surface transport

In `nut_nlch.f90`, the layer mixes nitrate with mobile water:

```
vv = perc + flat + (surfq if layer 1) + (qtile if tile layer)
co = no3 * (1 - exp(-vv / (porosity_term))) / vv
```

Surface runoff carries `nperco * co * surfq`, lateral flow carries `co * flat`, tile flow uses `nperco_lchtile * co`, and the remainder percolates to the next layer. `nperco` and `nperco_lchtile` come from `parameters.bsn` (defaults 0.10 and 0.50).

### Organic N and P transport with sediment

`nut_orgn.f90` and `nut_orgnc.f90` compute sediment-bound organic N. Concentration in the surface 10 mm is multiplied by `sedyld` and an enrichment ratio. The default enrichment ratio uses the CREAMS form

```
enratio = 0.78 * (0.1 * sedyld / (area * surfq)) ^ -0.2468
```

clipped to 3.0 (`pest_enrsb.f90`). Sediment-attached labile P comes from `nut_psed.f90`.

### Soluble P loss and leaching

`nut_solp.f90` partitions surface labile P between water and soil via `phoskd` (`parameters.bsn`, default 175):

```
surqsolp = lab * surfq / (bd * d * phoskd + 1)
```

Leaching uses a similar partition with `pperco` (default 10.0):

```
vap  = -prk / (0.01 * st + 0.1 * pperco * bd)
plch = 0.001 * lab * (1 - exp(vap))
```

### Mineral P transformations

`nut_pminrl.f90` (legacy model, `sol_p_model = 0`) flows P among labile, active, and stable pools to maintain the ratio `psp / (1 - psp)` between labile and active. Slow active-to-stable flow uses `bk = 0.01`. `nut_pminrl2.f90` is the Vadas and White (2010) reformulation, selected by `sol_p_model = 1`.

### Plant N fixation

See [plant growth](../model-theory/plant-growth-lum.md). Fixation only kicks in when soil supply is below demand and the plant has `nfix_co > 0`. Capped daily by `nfixmx` (`parameters.bsn`, default 20 kg N/ha).

### Atmospheric N deposition

Added daily through `nut_nrain.f90` using ammonium and nitrate concentrations in precipitation.

### Plant uptake distribution

Uptake from a layer follows an exponential function of depth controlled by `n_updis` and `p_updis` in `parameters.bsn` (defaults 20). The plant fixes any unmet demand if it is a legume.

## In-stream nutrient routing (QUAL2E)

When `bsn_cc%qual2e = 0`, channels use the full QUAL2E water quality formulation in `ch_watqual4.f90`. Simulated state variables are:

- Algae as chlorophyll-a
- Organic N, ammonia, nitrite, nitrate
- Organic P, dissolved P
- CBOD and dissolved oxygen

First-order rates and Arrhenius temperature corrections (theta factors) follow QUAL2E:

```
rate(T) = rate(20) * theta^(T - 20)
```

Default theta values applied in `ch_watqual4.f90`:

| Process | Symbol | Theta |
|---------|--------|-------|
| Algal growth, respiration | thgra, thrho | 1.047 |
| Settling | thrs1-thrs5 | 1.024 to 1.074 |
| Biological constants | thbc1-thbc4 | 1.047 to 1.083 |
| Reaeration / decay | thrk1-thrk4 | 1.024 to 1.060 |

Key channel nutrient parameters (`channel-nut.cha`):

- `rs1..rs5` settling rates (organic N, organic P, NH4, alg)
- `bc1..bc4` biological rate constants (NH4 to NO2, NO2 to NO3, organic to ammonia hydrolysis, organic P to dissolved P)
- `rk1..rk4` reaeration / BOD decay / SOD
- `ai0, ai1, ai2` stoichiometric ratios for algae
- `lambda0, lambda1, lambda2` light extinction
- `mumax, rhoq` algal growth and respiration

When `bsn_cc%qual2e = 1`, the channel uses simplified transformations.

## Switches and parameters

| File | Field | Default | Effect |
|------|-------|---------|--------|
| `codes.bsn` | `sol_p_model` | 0 | 0 = original P model, 1 = Vadas and White (2010) |
| `codes.bsn` | `qual2e` | 0 | 0 = full QUAL2E, 1 = simplified transformations |
| `parameters.bsn` | `cmn` | 0.003 | Active organic N mineralisation rate |
| `parameters.bsn` | `cdn` | 1.40 | Denitrification exponential rate |
| `parameters.bsn` | `sdnco` | 1.30 | Saturation threshold for denitrification (frac of FC) |
| `parameters.bsn` | `nperco` | 0.10 | Nitrate percolation/runoff partition |
| `parameters.bsn` | `nperco_lchtile` | 0.50 | Nitrate coefficient for tile and bottom-layer leaching |
| `parameters.bsn` | `phoskd` | 175 | P soil partitioning coefficient |
| `parameters.bsn` | `pperco` | 10.0 | P percolation coefficient |
| `parameters.bsn` | `psp` | 0.40 | P availability index |
| `parameters.bsn` | `rsdco` | 0.05 | Residue decomposition coefficient |
| `parameters.bsn` | `decr_min` | 0.01 | Minimum daily residue decay |
| `parameters.bsn` | `n_updis`, `p_updis` | 20 | Plant uptake depth distribution |
| `parameters.bsn` | `nfixmx` | 20 | Maximum daily N fixation (kg/ha) |

## Implementation

Soil N: `nut_nminrl.f90`, `nut_nitvol.f90`, `nut_nlch.f90`, `nut_orgn.f90`, `nut_orgnc.f90`, `nut_orgnc2.f90`, `nut_nrain.f90`, `nut_denit.f90`, `nut_np_flow.f90`.

Soil P: `nut_pminrl.f90`, `nut_pminrl2.f90`, `nut_solp.f90`, `nut_psed.f90`.

Plant uptake and fixation: `pl_nup.f90`, `pl_pup.f90`, `pl_nupd.f90`, `pl_pupd.f90`, `pl_nfix.f90`, `pl_nut_demand.f90`.

Soil pool transfer: `solt_db_read.f90`, `cbn_rsd_decomp.f90`, `cbn_rsd_transfer.f90`, `cbn_surfrsd_decomp.f90`.

In-stream: `ch_watqual4.f90`, `ch_rtday.f90`, `ch_read_nut.f90`, `channel_module.f90`.

Enrichment: `pest_enrsb.f90`.

## Related pages

- [`parameters.bsn`](../input-reference/parameters-bsn.md)
- [`codes.bsn`](../input-reference/codes-bsn.md)
- [`fertilizer.frt`](../input-reference/frt.md)
- [Carbon](../model-theory/carbon.md)
- [Plant growth](../model-theory/plant-growth-lum.md)
- [Channels](../model-theory/channels.md)

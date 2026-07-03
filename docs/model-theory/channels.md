---
title: Channels
description: Channel flow routing, sediment transport, and in-stream nutrient processes in SWAT+.
status: review
---

## Overview

Channels move water, sediment, and constituents along the drainage network from upstream HRUs and aquifers to the outlet. Each channel object has a geometry (width, depth, slope, length, side slope, Manning's n) read from `hydrology-cha.cha` and `sd_channel.cha`, and a rating curve built from that geometry. Daily inflow is the sum of all upstream object outflows. Daily outflow is computed by one of two routing methods selected by `bsn_cc%rte`. After routing, the channel runs sediment transport, in-stream water quality, and optional pesticide, salt, and constituent routines.

## Process equations

### Channel routing: variable storage vs Muskingum

`bsn_cc%rte` in `codes.bsn` selects the method:

| `bsn_cc%rte` | Method |
|--------------|--------|
| 0 | Variable storage coefficient |
| 1 | Muskingum |

Both run inside `ch_rtmusk.f90` (the file name reflects history; the routine dispatches on `bsn_cc%rte` inside its sub-step loop). The older daily-only path in `ch_rtday.f90` uses the variable storage coefficient and is retained for the legacy channel object.

**Variable storage.** At each sub-step the outflow fraction is

```
scoef = bsn_prm%scoef * 2 * dt / (2 * ttime + dt)
outflow = scoef * total_storage
```

where `ttime` is the travel time interpolated from the channel rating curve at the current flow rate. `bsn_prm%scoef` (default 1.0) calibrates the storage coefficient.

**Muskingum.** The three-coefficient form:

```
O2 = c1 * I2 + c2 * I1 + c3 * O1
```

with `c1`, `c2`, `c3` derived from the storage time constant `Km` and the weighting factor `X`. `Km` is computed from the bankfull and low-flow reach response times scaled by `bsn_prm%msk_co1` (default 0.75) and `bsn_prm%msk_co2` (default 0.25). `X = bsn_prm%msk_x` (default 0.20). The number of sub-daily steps and stability sub-steps is `sd_ch(jrch)%msk%nsteps` and `sd_ch(jrch)%msk%substeps`.

After routing, transmission losses are subtracted using the channel bed conductivity `sd_ch%chk` (mm/h) applied over the wetted perimeter and reach length. Reach evaporation uses `bsn_prm%evrch` (default 0.60) applied to PET over the channel surface area.

### Sediment transport: legacy vs sd_channel

Two sediment routines exist.

**Legacy stream power transport (`channel_module.f90`).** Older channels carry the maximum sediment concentration as a power function of the peak flow velocity:

```
conc_max = spcon * v_peak ^ spexp
```

`spcon` and `spexp` live in `bsn_prm` as legacy parameters; in current `basin_module.f90` they are flagged as not used by the modern routine. TODO: verify whether the legacy channel path still references these.

**Velocity and shear (`sd_channel_sediment3.f90`).** The current `sd_channel` path computes:

1. Peak channel flow rate from the daily flow and a peak ratio `sd_ch%pk_rto` adjusted for drainage area.
2. Channel velocity from Manning's equation at the peak rate, using the rating curve to get cross-section area and hydraulic radius.
3. Critical bank velocity `vel_cr` from the bank cohesion and bulk density factors, combined with the side-slope geometry.
4. Bank erosion as a function of the ratio `vel / vel_cr` raised to `sd_chd1%bed_exp` (default 1.5), distributed along the meander arc length scaled by `sd_chd1%arc_len_fr` (default 1.2).
5. Bed erosion from a critical shear stress comparison using the median bed particle diameter `sd_chd%d50` and the bulk density `sd_chd%ch_bd`.
6. Deposition computed in the flood plain when the flow exceeds bankfull, with a trap efficiency `trap_eff` set by the flood plain Manning's n `sd_chd%fpn` and slope `sd_chd%fps`.

Eroded sediment is split between channel and bank; a fraction `sd_chd1%wash_bed_fr` (default 0.1) of bank erosion is washload that leaves the reach. Particle-class fractions (silt, clay, sand, large aggregates, gravel) follow the bed composition.

### In-stream water quality (QUAL2E)

Nutrient transformations are computed in `ch_watqual4.f90`. The implementation is the QUAL2E equation set: algal growth limited by light, nutrient availability, and temperature; oxygen balance between algal photosynthesis, respiration, BOD decay, nitrification, and reaeration; nitrogen cycling from organic N to ammonium to nitrite to nitrate; phosphorus cycling from organic P to mineral P with settling and benthic sources.

Temperature corrections use the standard theta factors hard-coded in the routine (`thgra = 1.047`, `thrho = 1.047`, `thbc1 = 1.083`, etc.). Reaeration uses `bc1`, `bc2`, `bc3`, `bc4`, `rs1` through `rs5`, and `rk1` through `rk4` read from `nutrients-cha.nut`.

When `bsn_cc%qual2e = 1`, a simplified soluble-to-particulate transformation is applied after `ch_watqual4` runs, overriding the QUAL2E organic and mineral exchange:

```
delta_orgn = (1 - exp(-n_sol_part * ttime)) * orgn_in
delta_orgp = (1 - exp(-p_sol_part * ttime)) * sedp_in
```

`n_sol_part` and `p_sol_part` come from `sd_channel.cha` (defaults 0.01 each). `ttime` is the channel travel time from the rating curve.

### Pesticides, salts, constituents

After water quality, the channel runs `ch_rtpest.f90` for pesticides and the salt and constituent routines if those modules are active. See [Pesticides](pesticides.md) and [Salts and constituents](salts-constituents.md).

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `bsn_cc%rte` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = variable storage; 1 = Muskingum |
| `bsn_cc%qual2e` | 0 | [`codes.bsn`](../input-reference/codes-bsn.md) | 1 = simplified N and P sol-to-part overrides QUAL2E |
| `bsn_prm%scoef` | 1.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Variable-storage channel coefficient |
| `bsn_prm%msk_co1` | 0.75 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum bankfull storage coefficient |
| `bsn_prm%msk_co2` | 0.25 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum low-flow storage coefficient |
| `bsn_prm%msk_x` | 0.20 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum weighting factor |
| `bsn_prm%evrch` | 0.60 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Reach evaporation factor |
| `bsn_prm%spcon` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Legacy stream power coefficient (not used by sd_channel) |
| `bsn_prm%spexp` | 0.0 | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Legacy stream power exponent (not used by sd_channel) |
| `bsn_prm%ch_d50` | 0.0 mm | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Basin-wide channel median particle size |
| `sd_chd%chw` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel width (m) |
| `sd_chd%chd` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel depth (m) |
| `sd_chd%chs` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel slope (m/m) |
| `sd_chd%chl` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel length (km) |
| `sd_chd%chn` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel Manning's n |
| `sd_chd%chk` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel bottom conductivity (mm/h) |
| `sd_chd%cov` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel cover factor (0-1) |
| `sd_chd%d50` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Channel median sediment size (mm) |
| `sd_chd%ch_bd` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Bed and bank bulk density (t/m^3) |
| `sd_chd%ch_clay` | per channel | [`sd-channel`](../input-reference/sd-channel.md) | Bed and bank clay percent |
| `sd_chd1%pk_rto` | 1.0 | [`sd-channel`](../input-reference/sd-channel.md) | Ratio of peak to mean daily flow |
| `sd_chd1%n_setl` | 0.5 | [`sd-channel`](../input-reference/sd-channel.md) | N settling ratio to sediment settling |
| `sd_chd1%p_setl` | 0.5 | [`sd-channel`](../input-reference/sd-channel.md) | P settling ratio to sediment settling |
| `sd_chd1%n_sol_part` | 0.01 | [`sd-channel`](../input-reference/sd-channel.md) | Simplified soluble to particulate N rate |
| `sd_chd1%p_sol_part` | 0.01 | [`sd-channel`](../input-reference/sd-channel.md) | Simplified soluble to particulate P rate |
| `sd_chd1%bed_exp` | 1.5 | [`sd-channel`](../input-reference/sd-channel.md) | Bed erosion exponential coefficient |
| `sd_chd1%arc_len_fr` | 1.2 | [`sd-channel`](../input-reference/sd-channel.md) | Fraction of arc length where bank erodes |
| `sd_chd1%wash_bed_fr` | 0.1 | [`sd-channel`](../input-reference/sd-channel.md) | Washload fraction of bank erosion |

## Implementation

Source modules in `swatplus/src/`:

- `sd_channel_control3.f90` is the master control routine for an `sd_channel` object. It receives the daily inflow, calls routing, sediment, water quality, pesticide, salt, and constituent routines, and updates output structures.
- `ch_rtmusk.f90` runs the sub-daily routing loop. It dispatches on `bsn_cc%rte` and computes outflow, transmission loss, and reach evaporation.
- `ch_rtday.f90` is the daily variable-storage routing used by the legacy `channel` object.
- `sd_channel_sediment3.f90` computes channel velocity, critical velocity, bank and bed erosion, and flood plain deposition for the `sd_channel` path.
- `ch_watqual4.f90` performs the QUAL2E in-stream nutrient and oxygen calculations.
- `ch_rtpest.f90` routes pesticides through the channel.
- `ch_temp.f90` computes channel water temperature.
- `channel_module.f90` defines the legacy `channel` derived types and storage arrays.
- `sd_channel_module.f90` defines the `sd_channel` derived types: hydsed data (`sd_chd`), sediment-nutrient data (`sd_chd1`), sediment budget output, and morphology output.
- `channel_data_module.f90` holds channel parameter arrays read from input.
- `channel_velocity_module.f90` stores the rating curve and velocity bookkeeping.
- `ch_rchinit.f90` initialises the channel state at the start of simulation.
- `ch_ttcoef.f90` builds the Muskingum coefficients from the channel geometry.

## Related pages

- [`codes.bsn`](../input-reference/codes-bsn.md) for `rte` and `qual2e`.
- [`parameters.bsn`](../input-reference/parameters-bsn.md) for Muskingum and storage coefficients.
- [`sd-channel`](../input-reference/sd-channel.md) for channel geometry and sediment parameters.
- [`cha`](../input-reference/cha.md) for the legacy channel object.
- [Channel sediment and nutrient output](../output-reference/channel-sediment-nutrient.md).
- [Hydrology](hydrology.md) for the upstream HRU inflow.
- [Aquifers](aquifers.md) for return flow to channels.

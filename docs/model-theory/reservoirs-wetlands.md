---
title: Reservoirs and wetlands
description: Reservoir water balance and release rules, sediment and nutrient processes, and HRU wetlands in SWAT+.
status: review
---

## Overview

Reservoirs are standalone water body objects in the routing network. They receive inflow from upstream channels, HRUs, or recall objects, store it, and release it according to a decision table in `res_rel.dtl`. Each reservoir runs sediment settling, in-pond nutrient processes, and optional pesticide, salt, and constituent processes.

Wetlands are a separate object type linked to individual HRUs. They sit on the HRU surface, intercept surface runoff before it reaches the channel, and run a similar water balance and sediment-nutrient set as reservoirs. Wetland storage is configured per HRU in `wetland.wet`.

## Process equations

### Reservoir water balance

The daily water balance for a reservoir in `res_control.f90` is

```
stor_new = stor_prev + inflow + precip - outflow - evap - seep - irrig
```

where:

- `inflow` is the upstream hydrograph (`ht1`).
- `precip` is precipitation onto the water surface from the assigned weather station, using the current surface area.
- `outflow` is the release computed by `res_hydro.f90`.
- `evap` is potential evaporation times the water surface area, optionally adjusted by the reservoir evaporation coefficient.
- `seep` is seepage through the bed, computed from the bed hydraulic conductivity over the surface area.
- `irrig` is water withdrawn for irrigation through the water allocation module.

Surface area as a function of storage is interpolated from the principal volume `pvol_m3` and emergency volume `evol_m3` defined for the reservoir.

### Release rules via `res_rel.dtl`

Releases are not hard-coded. Each reservoir points to a decision table in `res_rel.dtl`. The table lists conditions (volume above principal, day of year, downstream demand, ...) and corresponding actions (weir release, target release, percent of volume, irrigation supply, ...). At each daily step `res_hydro.f90`:

1. Walks the action list (`d_tbl%acts`).
2. For each action, evaluates whether all condition alternatives are satisfied (`d_tbl%act_hit`).
3. Fires the corresponding release equation.

Release types include:

- `weir_release` for a weir of height `wbody_prm%weir_hgt` and width `wbody_prm%weir_wid`. The discharge over time follows the weir equation with the daily volume above the weir crest as the head source.
- `pvol_release` and `evol_release` for releases triggered when storage exceeds the principal or emergency volume.
- Doell-style storage-based release with coefficient `kr` and exponent `alpha` (Jose T 2025 extension in `res_hydro.f90`).
- Hanazaki monthly-target release using monthly inflow and demand.
- HYPE seasonal sine and linear storage modulation for hydropower-style operations.

The weir branch calls `res_weir_release.f90` to integrate over sub-daily steps.

### Reservoir sediment

`res_sediment.f90` computes settling using a first-order rate. If the in-reservoir sediment concentration (ppm) exceeds the equilibrium concentration `wbody_prm%sed%nsed`, the excess is reduced by the settling coefficient `wbody_prm%sed_stlr_co`:

```
sed_ppm_new = (sed_ppm - nsed) * sed_stlr_co + nsed
```

After settling, sand, large aggregates, silt, clay, and gravel are recomputed; all of the sand-sized fraction is assumed to deposit. Outflow sediment leaves at the post-settling concentration.

### Reservoir nutrients

`res_nutrient.f90` runs an in-pond nutrient set: settling of organic N and organic P, mineralisation, nitrification, and algal growth limited by light and nutrients. Soluble nutrients track storage-weighted concentration and leave at the outflow concentration. Settling rates are read from `nutrients-res.nut`.

### Reservoir pesticides, salts, constituents

`res_pest.f90`, `res_salt.f90`, and `res_cs.f90` run when those constituent modules are active. See [Pesticides](pesticides.md) and [Salts and constituents](salts-constituents.md).

### Wetlands on HRUs

Wetlands are configured per HRU via `wet_initial.f90` and `wetland.wet`. Each wetland has:

- Principal volume `wet_ob%pvol` (m^3) computed from `wet_hyd%pdep` (principal depth, mm) times the HRU area.
- Emergency volume `wet_ob%evol` (m^3) from `wet_hyd%edep`.
- Principal and emergency surface areas `psa` and `esa`.
- Optional weir geometry `weir_hgt` and `weir_wid` read from `weir.res`.

The wetland state `wet(iihru)` is the same `water_body` type used for reservoirs. In `hru_control.f90` the HRU surface runoff is routed into the wetland (`wet(j) = wet(j) + ht1`), the wetland runs its water balance and release (using the same `res_hydro` machinery on a wetland), and the outflow is added to the HRU outgoing hydrograph. Storage to depth uses a quadratic relation from `wet_hyd%bcoef` and `wet_hyd%ccoef`:

```
depth^2 * ccoef + depth * bcoef = (1 - flo / pvol)
```

with the positive root taken.

Wetlands run their own sediment, nutrient, pesticide, salt, and constituent routines using the same module code paths as reservoirs.

## Switches and parameters

| Switch / parameter | Default | File | Effect |
|--------------------|---------|------|--------|
| `res_hyd%iyres` | per reservoir | `hydrology-res.res` | Year reservoir comes online |
| `res_hyd%mores` | per reservoir | `hydrology-res.res` | Month reservoir comes online |
| `pvol_m3` | per reservoir | `hydrology-res.res` | Principal volume (m^3) |
| `evol_m3` | per reservoir | `hydrology-res.res` | Emergency volume (m^3) |
| `wbody_prm%sed%nsed` | per reservoir | `sediment-res.sed` | Equilibrium sediment concentration (ppm) |
| `wbody_prm%sed_stlr_co` | per reservoir | `sediment-res.sed` | Sediment settling coefficient |
| `wbody_prm%weir_hgt` | per reservoir | `weir.res` | Weir height (m) |
| `wbody_prm%weir_wid` | per reservoir | `weir.res` | Weir width (m) |
| `res_ob%release_dtl` | per reservoir | [`dtl`](../input-reference/dtl.md) (`res_rel.dtl`) | Decision table name for release rules |
| `wet_hyd%pdep` | per HRU wetland | `wetland.wet` | Principal depth (mm) |
| `wet_hyd%edep` | per HRU wetland | `wetland.wet` | Emergency depth (mm) |
| `wet_hyd%psa` | per HRU wetland | `wetland.wet` | Principal surface area fraction of HRU |
| `wet_hyd%esa` | per HRU wetland | `wetland.wet` | Emergency surface area fraction of HRU |
| `wet_hyd%bcoef` | per HRU wetland | `wetland.wet` | Storage-depth quadratic coefficient |
| `wet_hyd%ccoef` | per HRU wetland | `wetland.wet` | Storage-depth quadratic coefficient |

TODO: verify default values in `hydrology-res.res`, `sediment-res.sed`, `nutrients-res.nut`, `weir.res`, and `wetland.wet` against their respective `_read.f90` readers.

## Implementation

Source modules in `swatplus/src/`:

- `res_control.f90` is the master daily driver for a reservoir object. Adds inflow, computes the water balance, calls release, sediment, nutrient, pesticide, salt, and constituent routines.
- `res_hydro.f90` evaluates the release decision table and computes outflow. Houses weir, principal-volume, emergency-volume, Doell, Hanazaki, and HYPE release branches.
- `res_weir_release.f90` integrates weir discharge over sub-daily steps.
- `res_rel_conds.f90` evaluates release conditions specific to reservoirs.
- `res_sediment.f90` computes in-reservoir sediment settling.
- `res_nutrient.f90` runs in-reservoir nutrient transformations.
- `res_pest.f90` handles reservoir pesticides.
- `res_salt.f90`, `res_cs.f90` handle salts and constituents.
- `res_initial.f90`, `res_allo.f90`, `res_objects.f90` set up reservoir state at simulation start.
- `res_read.f90`, `res_read_hyd.f90`, `res_read_sed.f90`, `res_read_nut.f90`, `res_read_weir.f90`, `res_read_init.f90`, `res_read_conds.f90`, `res_read_elements.f90`, `res_read_csdb.f90`, `res_read_saltdb.f90`, `res_read_salt_cs.f90` read the reservoir input files.
- `reservoir_module.f90` defines reservoir types including `wet_ob` for wetlands.
- `reservoir_data_module.f90` and `reservoir_conditions_module.f90` hold parameter and conditions arrays.
- `reservoir_output.f90`, `res_pesticide_output.f90`, `res_salt_output.f90`, `res_cs_output.f90` write reservoir outputs.
- `wet_initial.f90` initialises a wetland on each flagged HRU.
- `wet_all_initial.f90` initialises all wetlands at simulation start.
- `wet_fp_init.f90` sets up the wetland-floodplain link to channels.
- `wet_read.f90`, `wet_read_hyd.f90`, `wet_read_salt_cs.f90` read wetland input files.
- `wet_irrp.f90` handles irrigation withdrawal from a wetland.
- `wet_cs.f90`, `wet_cs_output.f90`, `wet_salt.f90`, `wet_salt_output.f90` handle wetland constituents and salts.

## Related pages

- [Decision tables](decision-tables.md) for how release rules are evaluated.
- [`dtl`](../input-reference/dtl.md) for the decision table input file format.
- [`res`](../input-reference/res.md) for the reservoir input files.
- [`wet`](../input-reference/wet.md) for the wetland input files.
- [Channels](channels.md) for downstream routing.
- [Aquifer, reservoir, and plant output](../output-reference/aquifer-reservoir-plant.md).

---
title: Plant Growth and Land Use Management
description: Heat-unit plant growth, biomass accumulation, LAI, stress factors, and how land use, management, and decision tables drive operations.
status: review
---

## Overview

SWAT+ grows one or more plants in a community on each HRU. Daily potential biomass is a function of intercepted photosynthetically active radiation. That potential is reduced by water, temperature, nitrogen, phosphorus, and aeration stresses. Phenology is tracked by accumulated plant heat units (PHU). The plants on an HRU are scheduled by `management.sch`, and land use plus structural BMPs are assigned through `landuse.lum`. Decision tables (`lum.dtl`) drive conditional operations such as auto-irrigation, auto-fertilisation, and land use change.

## Process equations

### Heat unit accumulation

Each plant accumulates a fraction of total heat units to maturity per day:

```
delg   = max(0, (tave - t_base) / phumat)
phuacc = phuacc + delg
```

`t_base` is the plant's minimum growth temperature (`plants.plt`), `phumat` is the heat units to maturity. When `phuacc` reaches 1.0 the plant is mature. `phuacc_p` is the perennial counterpart. Source: `pl_nut_demand.f90`.

### Biomass accumulation

Daily potential biomass is

```
bioday = beadj * par
```

where `par` is intercepted PAR (MJ/m^2) and `beadj` is radiation use efficiency adjusted for CO2 and vapour pressure deficit. The CO2 adjustment uses the two-point curve described by `bio_e`, `bioehi`, `co2hi` in `plants.plt`. When vapour pressure deficit exceeds 1.0 kPa, RUE declines at the plant-specific rate `wavp`, with a floor of `0.27 * bio_e`. Realised biomass is

```
bm_grow = bioday * reg
reg     = min(strsw, strst, strsn, strsp, strsa[, strss])
```

`reg` is the most limiting stress factor. Plant carbon mass is fixed at `0.42 * biomass`. Source: `pl_biomass_gro.f90`.

### Leaf area index

LAI follows a two-point optimal curve defined by `(frgrw1, laimx1)` and `(frgrw2, laimx2)` from `plants.plt`. The model computes a fraction `f` of maximum LAI from `phuacc`:

```
f = phuacc / (phuacc + exp(leaf1 - leaf2 * phuacc))
```

`leaf1` and `leaf2` are shape parameters fitted from the two points. Before `phuacc` reaches `dlai` (fraction of season at which leaves decline), LAI grows toward `laimax`:

```
deltaLAI = (f - laimxfr) * laimax * (1 - exp(5*(LAI - laimax))) * sqrt(strsw)
```

After `phuacc > dlai`, LAI declines following `dlai_rate`. Canopy height is `chtmx * sqrt(f)`. For perennials, LAI is scaled by tree age through `laixco_tree` and `mat_yrs`. Source: `pl_leaf_gro.f90`, `pl_leaf_senes.f90`.

### Water stress and uptake

Potential transpiration `epmax(ipl)` is distributed through the rooting depth using an exponential extraction function with parameters `uptake%water_dis` and `uptake%water_norm`. Water uptake from each layer is

```
sum = epmax * (1 - exp(-water_dis * gx / root_dep)) / water_norm
wuse = sum - sump * (1 - epco)
```

where `gx` is depth to the bottom of the current layer. Layers below the root zone do not contribute. The compensation factor `epco` (0-1) controls how much a deeper layer can compensate when a shallower layer is dry. Water stress is

```
strsw = sum_wuse / epmax
```

Aeration stress activates when soil water exceeds field capacity:

```
satco = (sw - sumfc) / (sumul - sumfc)
strsa = 1 - scparm / (scparm + exp(2.9014 - 0.03867*scparm))
```

where `scparm = 100 * (satco - aeration) / (1.0001 - aeration)`. Source: `pl_waterup.f90`.

### Temperature stress

```
rto   = (tave - t_base) / (t_opt - t_base)
strst = sin(pi/2 * rto)
```

`strst = 0` if `tave <= t_base` or if `tmin <= annual mean - 15`. Source: `pl_tstr.f90`.

### Nitrogen and phosphorus stress and uptake

Plant N and P demands follow optimal concentration curves with `pltnfr1`, `pltnfr2`, `pltnfr3` and `pltpfr1`, `pltpfr2`, `pltpfr3` (see `plants.plt`). N and P are taken from soil layers with a depth-distribution function controlled by `n_updis` and `p_updis` in `parameters.bsn`. If supply is below demand, `strsn` and `strsp` reduce growth. Legumes fix N when soil supply is short:

```
fxr   = min(1, fxw, fxn) * fxg
fixn  = nfix_co * fxr * deficit + (1 - nfix_co) * deficit
fixn  = min(nfixmx, fixn)
```

`nfix_co` is the legume coefficient (0.5 for legumes, 0 for non-legumes). `nfixmx` (default 20 kg N/ha/day, `parameters.bsn`) caps daily fixation. Source: `pl_nup.f90`, `pl_pup.f90`, `pl_nfix.f90`, `pl_nupd.f90`, `pl_pupd.f90`.

### Harvest

Yield is `harveff * seed_mass`. The harvest index is bounded below by `wsyf` and accumulates from zero up to `hvsti` as `phuacc` increases past 0.5. Harvest types in `harv.ops` are `grain`, `biomass`, `residue`, `tree`, `tuber`, `peanuts`, `stripper`, `picker`. Pesticide is removed in yield in proportion to `pl_yield%m / pl_mass(j)%tot(ipl)%m`. Source: `mgt_harvgrain.f90`, `mgt_harvbiomass.f90`, `mgt_harvresidue.f90`, `mgt_harvtuber.f90`, `mgt_killop.f90`.

## Land use management

### `landuse.lum`

Each HRU points to a row in `landuse.lum`. That row carries the plant community name, curve number group, USLE conservation practice, tillage practice, and pointers to the management schedule, tile drainage code, septic code, filter strip, grass waterway, and BMP user practice. `hru_lum_init.f90` copies these pointers onto each HRU at the start of simulation. Source: `hru_lum_init.f90`, `landuse_data_module.f90`.

### `management.sch`

For each schedule, operations are listed in calendar or PHU-trigger order. Operation codes used by `mgt_sched.f90` include:

| Code | Operation |
|------|-----------|
| `plnt` | Plant a single species (or community) |
| `harv` | Harvest (grain / biomass / residue / tree / tuber etc.) |
| `kill` | Kill the plant, transfer all biomass to residue |
| `hvkl` | Harvest and kill in the same operation |
| `till` | Tillage, mixes residue and pools using `till.til` |
| `irrm` | Irrigation, applies depth from `irr.ops` |
| `fert` | Mineral or organic fertiliser (`fertilizer.frt`) |
| `manu` | Manure application |
| `pest` | Pesticide application |
| `graz` | Grazing |
| `cnup` | Curve number update |
| `burn` | Prescribed burn |
| `swep` | Street sweeping |
| `dwm`  | Drainage water management depth |
| `weir` | Set or adjust weir height |
| `mons` | Begin or end monsoon trigger window |

PHU-triggered operations fire when `phuacc` of the plant in column `op2` crosses the value in column `phu`. Date-triggered operations fire on the given month and day. Source: `mgt_sched.f90`, `mgt_operations_module.f90`.

### Decision tables (`lum.dtl`)

Each row in `landuse.lum` may also reference one or more decision tables in `lum.dtl`. Decision tables are conditional rule sets that fire actions when their conditions are met. Each table has `conds` conditions, `alts` alternative outcomes, and `acts` actions. On each day in `hru_control.f90` the model loops over the HRU's `num_autos` auto operations and calls `conditions` then `actions` for each. Typical actions include auto-irrigation, auto-fertilisation, planting based on PHU triggers, and land use change. The decision table reader is `dtbl_lum_read.f90`; the run-time logic is in `conditions.f90` and `actions.f90`.

See the [Decision tables](decision-tables.md) theory page for the rule grammar.

## Switches and parameters

| File | Field | Effect |
|------|-------|--------|
| `codes.bsn` | `nostress` | 0 = all stresses applied, 1 = no stress, 2 = no N/P stress |
| `codes.bsn` | `cswat` | Selects soil carbon model. The dynamic CENTURY/SWAT-C model (=2) changes residue and tillage routines |
| `parameters.bsn` | `co2` | Ambient CO2 concentration (ppm), default 400 |
| `parameters.bsn` | `nfixmx` | Maximum daily N fixation (kg/ha), default 20 |
| `parameters.bsn` | `n_updis`, `p_updis` | Depth-distribution shape for plant N/P uptake |
| `parameters.bsn` | `evlai` | LAI above which only transpiration occurs, default 3.0 |
| `plants.plt` | `bio_e`, `bioehi`, `co2hi`, `wavp` | RUE and its CO2 / VPD response |
| `plants.plt` | `blai`, `frgrw1`, `laimx1`, `frgrw2`, `laimx2`, `dlai`, `dlai_rate` | LAI development curve |
| `plants.plt` | `t_base`, `t_opt` | Temperature response |
| `plants.plt` | `hvsti`, `wsyf` | Harvest index and water-stress floor |
| `plants.plt` | `chtmx`, `rdmx` | Maximum canopy height and root depth |
| `plants.plt` | `aeration` | Aeration stress threshold (fraction above FC) |
| `plants.plt` | `pltnfr1..3`, `pltpfr1..3` | N and P optimal concentration curves |
| `plants.plt` | `nfix_co` | Legume coefficient |
| `plants.plt` | `mat_yrs`, `laixco_tree`, `bmx_peren`, `leaf_tov_min`, `leaf_tov_max` | Perennial / tree parameters |

## Implementation

Plant growth: `pl_grow.f90`, `pl_biomass_gro.f90`, `pl_leaf_gro.f90`, `pl_leaf_senes.f90`, `pl_root_gro.f90`, `pl_seed_gro.f90`, `pl_partition.f90`, `pl_community.f90`, `pl_waterup.f90`, `pl_tstr.f90`, `pl_nut_demand.f90`, `pl_nup.f90`, `pl_pup.f90`, `pl_nupd.f90`, `pl_pupd.f90`, `pl_nfix.f90`, `pl_dormant.f90`, `pl_mortality.f90`, `pl_rootfr.f90`.

Plant data and initialisation: `plant_data_module.f90`, `plant_module.f90`, `plant_parm_read.f90`, `plant_init.f90`, `plant_all_init.f90`, `plant_transplant_read.f90`.

Management operations: `mgt_sched.f90`, `mgt_operatn.f90`, `mgt_plantop.f90`, `mgt_harvgrain.f90`, `mgt_harvbiomass.f90`, `mgt_harvresidue.f90`, `mgt_harvtuber.f90`, `mgt_killop.f90`, `mgt_biomix.f90`, `mgt_newtillmix_cswat0.f90`, `mgt_newtillmix_cswat1.f90`, `mgt_newtillmix_wet.f90`, `mgt_tillfactor.f90`, `mgt_transplant.f90`, `mgt_operations_module.f90`, `mgt_read_*.f90`.

Plant operation utilities: `pl_fert.f90`, `pl_fert_wet.f90`, `pl_manure.f90`, `pl_graze.f90`, `pl_burnop.f90`.

Land use: `hru_lum_init.f90`, `hru_lum_init_all.f90`, `landuse_data_module.f90`, `lum_read*.f90`.

Decision tables: `dtbl_lum_read.f90`, `conditions.f90`, `actions.f90`, `conditional_module.f90`.

## Related pages

- [`landuse.lum`](../input-reference/lum.md)
- [`plants.plt`](../input-reference/plt.md)
- [`fertilizer.frt`](../input-reference/frt.md)
- [`management.sch`](../input-reference/ops.md)
- [`lum.dtl`](../input-reference/dtl.md)
- [`codes.bsn`](../input-reference/codes-bsn.md)
- [`parameters.bsn`](../input-reference/parameters-bsn.md)
- [Decision tables](../model-theory/decision-tables.md)
- [Nutrient cycling](../model-theory/nutrient-cycling.md)
- [Carbon](../model-theory/carbon.md)

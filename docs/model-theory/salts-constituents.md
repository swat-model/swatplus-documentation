---
title: Salts and Constituents
description: Salt ion and trace constituent transport, chemistry, and effect on plants in SWAT+.
status: review
---

## Overview

SWAT+ tracks two optional families of conservative-but-reactive constituents:

- Salt ions (`rtb salt`): SO4, Ca, Mg, Na, K, Cl, CO3, HCO3 (eight ions)
- Trace constituents (`rtb cs`): SeO4, SeO3, boron

Both families share the same flow paths as nitrate: surface runoff, lateral flow, tile drainage, percolation, plant uptake, rainfall and dry deposition, irrigation, and fertiliser/amendment inputs. Salt ions are subject to equilibrium chemistry (precipitation-dissolution of CaCO3, MgCO3, CaSO4, MgSO4, NaCl and cation exchange between Na, Ca, Mg, K). Selenium and boron use simple linear sorption and a first-order reaction term. Salinity stress can reduce crop water uptake.

These modules are active only when their respective databases are present, controlled by `cs_db%num_salts` and `cs_db%num_cs` (set during `cs_read_*` setup).

## Process equations

### Soil-water transport

For both salts and trace constituents the layer-level transport routine mirrors `nut_nlch.f90`. For each salt ion (or cs species) `m`:

```
vv = perc + flat + (surfq if layer 1) + (qtile if tile layer)
co = mass * (1 - exp(-vv / ul)) / vv
surq_mass  = co * surfq             # layer 1 only
latq_mass  = co * flat
tile_mass  = co * qtile             # at tile layer
perc_mass  = co * prk               # next layer or out of profile
```

Lateral, tile, and percolation are first-order in mobile water with porosity `ul`. No partition coefficient is applied to salt ions; sorbed selenium and boron use `cs_sorb_hru.f90`. Source: `salt_lch.f90`, `cs_lch.f90`.

### Salt chemistry in soil

`salt_chem_hru.f90` and `salt_chem_soil_single.f90` solve equilibrium speciation per layer using:

- Activity coefficients via ionic strength (Davies / extended Debye-Huckel form)
- Precipitation-dissolution of five minerals: CaCO3 (Ksp = 3.07e-9), MgCO3 (4.79e-6), CaSO4 (7.89e-5), MgSO4 (7.24e-3), NaCl (37.3)
- Complexation reactions (CaCO3, MgCO3, CaSO4, MgSO4, NaCl)
- Cation exchange between Na, Ca, Mg, K through `cationexchange`

These run iteratively until ion concentrations converge. The same scheme is applied to the aquifer in `salt_chem_aqu.f90` using a separate set of Ksp values (currently the same defaults).

### Salinity stress on plants

When `salt_tol_sim = 1` and at least one salt ion is simulated, `pl_waterup.f90` computes a salinity reduction factor per layer using the FAO yield-vs-ECe relationship:

```
soil_TDS_sat = sum(soil_salt_conc) at saturation
soil_ECe = soil_TDS_sat / salt_tds_ec
if (soil_ECe > a):
    reduc_salt = (100 - b * (soil_ECe - a)) / 100
```

`a` is the salt tolerance threshold (dS/m), `b` is the slope (yield loss per dS/m above the threshold). Both are per-plant parameters read from `salt_plants.slt`. If `salt_soil_type = 1` (CaSO4 / gypsiferous), the threshold is increased by 2 dS/m. The minimum `reduc_salt` across rooted layers becomes the plant salt stress factor `strss`.

`salt_effect = 1` applies salinity stress after the other stresses are minimised; `salt_effect = 2` (default) includes it in the joint minimum.

### Salt uptake by plants

When `salt_uptake_on = 1`, daily salt removal by plants is read from a user file (`salt_uptake.slt`) and applied through `salt_uptake.f90`. Otherwise no plant uptake of salt occurs.

### Trace constituent reactions and sorption

`cs_rctn_hru.f90` applies first-order reactions to SeO4, SeO3, and boron. Coefficients come from `cs_reactions.cs`. `cs_sorb_hru.f90` runs an equilibrium linear sorption between dissolved and solid-phase pools per layer, parameterised by partition coefficients in `cs_data_module.f90`. Constituent uptake follows the nitrate-style uptake routine `cs_uptake.f90`.

### Salt and constituent inputs

- Atmospheric: wet deposition (`salt_rain.f90`, `cs_rain.f90`) and dry deposition (read from `atmodep_salt`, `atmodep_cs`), monthly or annual
- Fertiliser: salt-bearing fertilisers from `salt_fert.f90`, `cs_fert.f90` (read into `fert_salt`, `fert_cs`)
- Road salt: `salt_roadsalt.f90`, applied seasonally per HRU
- Irrigation: salt and cs concentrations in irrigation water (`salt_irrig.f90`, `cs_irrig.f90`)
- Initial soil conditions: `salt_hru_init.f90`, `cs_hru_init.f90`

### In-channel and aquifer

Channels route salt ions through `ch_salt_module.f90` and `ch_salt_output.f90`; constituents through `ch_cs_module.f90` and `ch_cs_output.f90`. Aquifer fluxes are handled in `salt_aquifer.f90`, `salt_chem_aqu.f90`, `cs_aquifer.f90`, `cs_rctn_aqu.f90`, `cs_sorb_aqu.f90`. Reservoirs and wetlands have parallel implementations (`res_salt.f90`, `wet_salt.f90`).

## Switches and parameters

### Salts

| File | Field | Default | Effect |
|------|-------|---------|--------|
| `salt_module.f90` | `salt_uptake_on` | 0 | 1 = enable user-defined daily salt uptake |
| `salt_data_module.f90` | `salt_tol_sim` | 0 | 1 = salinity stress on plant water uptake |
| `salt_data_module.f90` | `salt_soil_type` | 0 | 1 = CaSO4 (gypsiferous), 2 = NaCl |
| `salt_data_module.f90` | `salt_effect` | 0 | 1 = applied after other stresses, 2 = joint minimum |
| `salt_data_module.f90` | `salt_tds_ec` | input | TDS-to-EC conversion factor |
| `salt_data_module.f90` | `Ksp11..Ksp51` | see source | Soil mineral solubility products |
| `salt_data_module.f90` | `Ksp12..Ksp52` | same defaults | Aquifer mineral solubility products |
| `salt_plants.slt` | `a`, `b` per plant | input | Salt tolerance threshold and slope |
| `salt_recall.slt` and other recall files | input | Constituent loads on point sources |

### Constituents (cs)

| File | Field | Effect |
|------|-------|--------|
| `cs_data_module.f90` | partition coefficients | Linear sorption per constituent |
| `cs_reactions.cs` | first-order rate coefficients | Constituent reaction rates |
| `cs_uptake.cs` | uptake fractions per plant | Plant uptake of cs |
| `cs_fert.cs` | constituent loads in fertiliser | Inputs from fertiliser |
| `cs_irrig.cs` | constituent concentration in irrigation | Inputs from irrigation |

## Implementation

### Salts

Soil and HRU: `salt_balance.f90`, `salt_lch.f90`, `salt_chem_hru.f90`, `salt_chem_soil_single.f90`, `salt_uptake.f90`, `salt_rain.f90`, `salt_fert.f90`, `salt_fert_wet.f90`, `salt_irrig.f90`, `salt_roadsalt.f90`, `salt_hru_init.f90`.

Inputs: `salt_aqu_read.f90`, `salt_cha_read.f90`, `salt_fert_read.f90`, `salt_hru_read.f90`, `salt_irr_read.f90`, `salt_plant_read.f90`, `salt_roadsalt_read.f90`, `salt_uptake_read.f90`, `salt_urban_read.f90`.

Modules: `salt_module.f90`, `salt_data_module.f90`.

Channel and water bodies: `ch_salt_module.f90`, `ch_salt_output.f90`, `res_salt.f90`, `res_salt_module.f90`, `res_salt_output.f90`, `res_read_salt_cs.f90`, `res_read_saltdb.f90`, `wet_salt.f90`, `wet_salt_output.f90`, `wet_read_salt_cs.f90`.

Aquifer: `salt_aquifer.f90`, `salt_chem_aqu.f90`, `aqu_salt_output.f90`.

Climate, recall, export coefficients, delivery ratios: `cli_read_atmodep_salt.f90`, `recall_read_salt.f90`, `recall_salt.f90`, `dr_read_salt.f90`, `exco_read_salt.f90`, `header_salt.f90`.

Output: `hru_salt_output.f90`, `ru_salt_output.f90`, `output_ls_salt_module.f90`.

### Trace constituents (cs)

Soil and HRU: `cs_balance.f90`, `cs_lch.f90`, `cs_rctn_hru.f90`, `cs_sorb_hru.f90`, `cs_uptake.f90`, `cs_rain.f90`, `cs_fert.f90`, `cs_fert_wet.f90`, `cs_irrig.f90`, `cs_hru_init.f90`.

Inputs: `cs_aqu_read.f90`, `cs_cha_read.f90`, `cs_fert_read.f90`, `cs_hru_read.f90`, `cs_irr_read.f90`, `cs_plant_read.f90`, `cs_reactions_read.f90`, `cs_uptake_read.f90`, `cs_urban_read.f90`.

Modules: `cs_module.f90`, `cs_data_module.f90`.

Channel: `ch_cs_module.f90`, `ch_cs_output.f90`, `cs_str_output.f90`.

Aquifer: `cs_aquifer.f90`, `cs_rctn_aqu.f90`, `cs_sorb_aqu.f90`, `aqu_cs_output.f90`.

Reservoirs and wetlands: `res_cs_module.f90`, `res_cs_output.f90`, `wet_cs_output.f90`.

HRU and RU output: `hru_cs_output.f90`, `ru_cs_output.f90`.

## Related pages

- [Nutrient cycling](../model-theory/nutrient-cycling.md)
- [Plant growth](../model-theory/plant-growth-lum.md)
- [Aquifers](../model-theory/aquifers.md)
- [Channels](../model-theory/channels.md)
- [Recall and point sources](../model-theory/recall-point-sources.md)

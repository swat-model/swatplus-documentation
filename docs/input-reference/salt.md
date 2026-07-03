---
title: salt module (rtb salt)
description: Per-object salt parameters and initial conditions for the rtb-salt module.
status: review
verified_against:
  - src/salt_module.f90
  - src/salt_data_module.f90
  - src/salt_aqu_read.f90
  - src/salt_cha_read.f90
  - src/salt_fert_read.f90
  - src/salt_hru_read.f90
  - src/salt_irr_read.f90
  - src/salt_plant_read.f90
  - src/salt_roadsalt_read.f90
  - src/salt_uptake_read.f90
  - src/salt_urban_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The rtb-salt module simulates the eight salt ions (so4, ca, mg, na, k, cl, co3, hco3) across the soil profile, plant, channel, aquifer, urban, irrigation, fertilizer, atmospheric, and road-salt pathways. Each input file listed below feeds one piece of that state: initial concentrations, applied loads, or per-plant tolerance parameters.

## Activation

Salt simulation is gated by the master constituent file [`constituents.cs`](cs.md) referenced from `file.cio` (`in_sim%cs_db`, default `constituents.cs`). The number of salt ions in that file is held in `cs_db%num_salts`. If `num_salts = 0`, salt readers that test it (`salt_roadsalt_read`, `salt_uptake_read`, `salt_urban_read`) skip silently. The remaining readers test only for file existence and read whatever is present.

All readers are called from `proc_read.f90` except `salt_cha_read`, which is called later from `main.f90`.

## Files

### salt_hru.ini

Initial salt ion concentrations and mineral fractions for HRU soils and plants.

- Reader: [`src/salt_hru_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_hru_read.f90)
- Type: `salt_soil_ini` (`type cs_soil_init_concentrations`) in [`src/constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/constituent_mass_module.f90)
- Format: 4 header lines, then for each entry three lines: name, then `num_salts + 5` soil values, then `num_salts + 5` plant values. First `num_salts` values are ion concentrations (ppm), next 5 are salt mineral fractions.

### salt_aqu.ini

Initial salt ion concentrations and mineral fractions for aquifers.

- Reader: [`src/salt_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_aqu_read.f90)
- Type: `salt_aqu_ini` (`type salt_aqu_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `conc(num_salts)` in g/m3, `frac(5)` mineral fractions.
- Format: 4 header lines, then one line per aquifer init record: `name`, `num_salts` concentrations, 5 mineral fractions.

### salt_channel.ini

Initial salt ion concentrations for channels.

- Reader: [`src/salt_cha_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_cha_read.f90)
- Type: `salt_cha_ini` (`type salt_cha_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `conc(num_salts)` in g/m3.
- Format: 2 header lines, then one line per record: `name`, `num_salts` concentrations.

### salt_irrigation

Salt ion concentrations for irrigation water sourced from outside the watershed.

- Reader: [`src/salt_irr_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_irr_read.f90)
- Type: `salt_water_irr` (`type cs_irrigation_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `water(num_salts)` in ppm.
- Format: 2 header lines, then one line per source: `name`, `num_salts` concentrations.

### salt_plants

Plant salt-tolerance parameters and stress control switches.

- Reader: [`src/salt_plant_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_plant_read.f90)
- Targets in [`src/salt_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_data_module.f90):

| Field | Type | Units | Description |
|-------|------|-------|-------------|
| salt_tds_ec | real | none | TDS to electrical conductivity conversion factor |
| salt_tol_sim | int | flag | 0 = off, 1 = simulate salt effect on plant growth |
| salt_soil_type | int | code | 1 = CaSO4 soils, 2 = NaCl soils |
| salt_effect | int | code | 1 = applied after other stresses, 2 = combined with other stresses via min |
| salt_stress_a(plantparm) | real | none | a parameter in the salinity relative-yield equation |
| salt_stress_b(plantparm) | real | none | b parameter in the salinity relative-yield equation |

Format: title line, header, `salt_tds_ec`, blank, `salt_tol_sim`, `salt_soil_type`, `salt_effect`, four skipped lines, header, then one line per plant in plant database order with `name, a, b`.

### salt_road

Road salt loadings (kg/ha) per atmospheric deposition station.

- Reader: [`src/salt_roadsalt_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_roadsalt_read.f90)
- Target: `rdapp_salt(:)%salt(:)` (`%road`, `%roadmo`, `%roadyr`, `%roadday`). Allocated for `0:atmodep_cont%num_sta` stations.
- Format: 4 commentary lines skipped, then per station and per salt ion either an annual value (`aa`), a monthly series (`mo`), or a yearly series (`yr`). For `yr`, the reader internally splits the annual mass to daily loadings on days with precipitation and sub-zero temperature.

### salt_uptake

Specified daily salt uptake (kg/ha) per plant community per ion.

- Reader: [`src/salt_uptake_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_uptake_read.f90)
- Targets in `src/salt_module.f90`: `salt_uptake_kg(plantparm, num_salts)`, `salt_uptake_on` (flag set to 1 when the file is present).
- Format: 3 header lines, then one line per plant: `name`, `num_salts` uptake values.

### salt_urban

Salt ion concentration in suspended solids from urban impervious areas (mg salt / kg sediment).

- Reader: [`src/salt_urban_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_urban_read.f90)
- Target: `salt_urban_conc(urban, num_salts)` in `src/salt_module.f90`.
- Format: 2 header lines, then one line per urban land-use type: `urb_type`, `num_salts` concentrations. The urban name must match an entry in `urban.urb`.

### salt_fertilizer.frt

Per-fertilizer salt ion loading (kg/ha).

- Reader: [`src/salt_fert_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/salt_fert_read.f90)
- Type: `fert_salt(fertparm)` (`type fert_db_salt`) in `src/salt_module.f90`. Sets `fert_salt_flag = 1`.

| # | Field | Units | Description |
|---|-------|-------|-------------|
| 1 | fertnm | - | fertilizer name |
| 2 | so4 | kg/ha | sulfate loading |
| 3 | ca | kg/ha | calcium loading |
| 4 | mg | kg/ha | magnesium loading |
| 5 | na | kg/ha | sodium loading |
| 6 | k | kg/ha | potassium loading |
| 7 | cl | kg/ha | chloride loading |
| 8 | co3 | kg/ha | carbonate loading |
| 9 | hco3 | kg/ha | bicarbonate loading |

Format: title, header, then one line per fertilizer in the fertilizer database order.

## Related

- [`constituents.cs`](cs.md). Master constituent list. Sets `num_salts` and the ion names.
- [`fertilizer.frt`](frt.md). The base fertilizer database. `salt_fertilizer.frt` must have the same row count.
- [`urban.urb`](../input-reference/index.md). Source of urban land-use names referenced by `salt_urban`.
- [`atmodep.cli`](cli.md). Defines the atmospheric deposition stations used by `salt_road`.

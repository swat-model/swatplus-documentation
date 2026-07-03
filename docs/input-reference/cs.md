---
title: constituent module (rtb cs)
description: Master constituent database and per-object initial conditions for the rtb-cs module.
status: review
verified_against:
  - src/constit_db_read.f90
  - src/constituent_mass_module.f90
  - src/cs_module.f90
  - src/cs_data_module.f90
  - src/cs_aqu_read.f90
  - src/cs_cha_read.f90
  - src/cs_fert_read.f90
  - src/cs_hru_read.f90
  - src/cs_irr_read.f90
  - src/cs_plant_read.f90
  - src/cs_reactions_read.f90
  - src/cs_uptake_read.f90
  - src/cs_urban_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The rtb-cs module simulates user-listed water-quality constituents (selenium SeO4 and SeO3, boron, and additional species defined in the constituent database). It runs in parallel with [`rtb-salt`](salt.md) and shares the same master file, `constituents.cs`.

## Activation

`constituents.cs` is the master file referenced from `file.cio` as `in_sim%cs_db` (default `constituents.cs`). It lists the pesticides, pathogens, metals, salt ions, and other constituents in the simulation, and populates `cs_db%num_pests`, `cs_db%num_paths`, `cs_db%num_metals`, `cs_db%num_salts`, and `cs_db%num_cs`. The cs and salt readers downstream allocate their arrays from these counts.

The readers `cs_roadsalt_read` does not exist for cs. The cs readers `cs_uptake_read`, `cs_urban_read`, and `cs_reactions_read` only proceed when `cs_db%num_cs > 0`; the remaining readers test only for file existence.

All cs readers are called from `proc_read.f90` except `cs_cha_read`, which is called later from `main.f90`.

## Files

### constituents.cs

Master list of constituents.

- Reader: [`src/constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/constit_db_read.f90)
- Type: `cs_db` (`type cs_db_type`) in [`src/constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/constituent_mass_module.f90).
- Format: title, then five pairs of `count` followed by `count` names, in order: pesticides, pathogens, metals, salts, other constituents. The metals block is read but is unused downstream (the matching loop is commented out in the source). The salt names are matched against the database in [`salt_plants`](salt.md) by plant-parameter index, not by name.

### cs_hru.ini

Initial constituent concentrations for HRU soils and plants.

- Reader: [`src/cs_hru_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_hru_read.f90)
- Type: `cs_soil_ini` (`type cs_soil_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `soil(2*num_cs)`, `plt(2*num_cs)` in ppm.
- Format: 4 header lines, then for each entry three lines: name, soil values, plant values.

### cs_aqu.ini

Initial constituent concentrations for aquifers.

- Reader: [`src/cs_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_aqu_read.f90)
- Type: `cs_aqu_ini` (`type cs_aqu_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `aqu(2*num_cs)` (dissolved plus sorbed).
- Format: 3 header lines, then one line per entry: `name`, `2*num_cs` values.

### cs_channel.ini

Initial constituent concentrations for channels.

- Reader: [`src/cs_cha_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_cha_read.f90)
- Type: `cs_cha_ini` (`type cs_cha_init_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `conc(num_cs)` in g/m3.
- Format: 2 header lines, then one line per record: `name`, `num_cs` concentrations.

The same reader also processes the optional `cs_streamobs` file, which lists channels for which daily concentration and load output is written to `cs_streamobs_output`.

### cs_irrigation

Constituent concentrations for irrigation water sourced from outside the watershed.

- Reader: [`src/cs_irr_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_irr_read.f90)
- Type: `cs_water_irr` (`type cs_irrigation_concentrations`) in `src/constituent_mass_module.f90`. Fields: `name`, `water(num_cs)` in ppm.
- Format: 2 header lines, then one line per source: `name`, `num_cs` concentrations.

### cs_plants_boron

Plant boron tolerance parameters.

- Reader: [`src/cs_plant_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_plant_read.f90)
- Targets in [`src/cs_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_data_module.f90):

| Field | Type | Units | Description |
|-------|------|-------|-------------|
| bor_tol_sim | int | flag | 0 = off, 1 = simulate boron effect on plant growth |
| bor_stress_a(plantparm) | real | none | a parameter in the boron relative-yield equation |
| bor_stress_b(plantparm) | real | none | b parameter in the boron relative-yield equation |

Format: title, blank, `bor_tol_sim`, four header lines, then one line per plant in plant database order with `name, a, b`.

### cs_uptake

Specified daily constituent uptake (kg/ha) per plant community per constituent.

- Reader: [`src/cs_uptake_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_uptake_read.f90)
- Targets in [`src/cs_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_module.f90): `cs_uptake_kg(plantparm, num_cs)`, `cs_uptake_on` (flag set to 1 when the file is present).
- Format: 3 header lines, then one line per plant: `name`, `num_cs` uptake values.

### cs_reactions

Selenium and boron chemical reaction parameters for soils and aquifers, organised by reaction group and shale geology.

- Reader: [`src/cs_reactions_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_reactions_read.f90)
- Type: `cs_rct_soil(sp_ob%hru)` and `cs_rct_aqu(sp_ob%aqu)` (`type constituent_rct`) in `src/cs_data_module.f90`. Also fills the module-level arrays `rct(num_rct, num_groups)` and `rct_shale(num_geol_shale, 3)`.
- Format: title, header, `num_rct num_groups`, `num_rct` lines of group values, header, `num_geol_shale`, `num_geol_shale` lines of three shale parameters, header, one line per HRU (`hru_id, group, shale_fractions...`), header, one line per aquifer (`aqu_id, group, shale_fractions...`). The eight `rct` rows hold (in order): inorganic-N to Se ratio, soil oxygen, aquifer oxygen, kd_seo4, kd_seo3, kd_boron, kseo4 in soil, kseo4 in aquifer. See the source for the full assignment table.

### cs_urban

Constituent concentration in suspended solids from urban impervious areas (mg cs / kg sediment).

- Reader: [`src/cs_urban_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_urban_read.f90)
- Target: `cs_urban_conc(urban, num_cs)` in `src/cs_module.f90`.
- Format: 2 header lines, then one line per urban land-use type: `urb_type`, `num_cs` concentrations. The urban name must match an entry in `urban.urb`.

### fertilizer.frt_cs

Per-fertilizer constituent loading (kg/ha).

- Reader: [`src/cs_fert_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/cs_fert_read.f90)
- Type: `fert_cs(fertparm)` (`type fert_db_cs`) in `src/cs_module.f90`. Sets `fert_cs_flag = 1`.

| # | Field | Units | Description |
|---|-------|-------|-------------|
| 1 | fertnm | - | fertilizer name |
| 2 | seo4 | kg/ha | selenate loading |
| 3 | seo3 | kg/ha | selenite loading |
| 4 | boron | kg/ha | boron loading |

Format: title, header, then one line per fertilizer in the fertilizer database order.

## Related

- [`salt module`](salt.md). The salt readers share `constituents.cs` for ion counts and use the same per-object pattern.
- [`fertilizer.frt`](frt.md). Base fertilizer database. `fertilizer.frt_cs` must have the same row count.
- [`urban.urb`](../input-reference/index.md). Source of urban land-use names for `cs_urban`.
- [`atmodep.cli`](cli.md). Atmospheric deposition stations used by the cs deposition reader `cli_read_atmodep_cs`.

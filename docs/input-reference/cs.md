---
title: Constituent inputs
description: The constituents.cs master list and the input files of the constituent module, which simulates selenate, selenite and boron.
status: review
verified_against:
  - src/constit_db_read.f90
  - src/cs_hru_read.f90
  - src/cs_aqu_read.f90
  - src/cs_cha_read.f90
  - src/cs_irr_read.f90
  - src/cs_plant_read.f90
  - src/cs_uptake_read.f90
  - src/cs_reactions_read.f90
  - src/cs_urban_read.f90
  - src/cs_fert_read.f90
  - src/res_read_csdb.f90
  - src/res_read_salt_cs.f90
  - src/cs_hru_init.f90
  - src/cs_fert.f90
  - src/cs_fert_wet.f90
  - src/cs_irrig.f90
  - src/cs_uptake.f90
  - src/cs_sorb_hru.f90
  - src/cs_sorb_aqu.f90
  - src/se_reactions_soil.f90
  - src/se_reactions_aquifer.f90
  - src/res_cs.f90
  - src/cs_module.f90
  - src/cs_data_module.f90
  - src/res_cs_module.f90
  - src/constituent_mass_module.f90
  - src/aqu_read_init_cs.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_init.f90
  - src/soil_plant_init.f90
  - src/pl_biomass_gro.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`constituents.cs` lists the pesticides, pathogens, heavy metals, salt ions and other constituents that a run simulates. The last group, the other constituents, is the constituent module: selenate (SeO₄), selenite (SeO₃) and boron in soils, aquifers, channels, reservoirs and wetlands. The module simulates sorption, selenium reduction and selenium release from shale, and the constituents move with water like the other dissolved substances.

The salt ion files are described on the [salt inputs](salt.md) page. Apart from `constituents.cs`, which is named in [`file.cio`](file-cio.md), the files are not listed in [`file.cio`](../input-reference/file-cio.md); SWAT+ looks for them by name in the run directory.

## constituents.cs

The master list, named on the simulation line of [`file.cio`](file-cio.md) (default `constituents.cs`). If the file is missing or named `null`, no pesticides, pathogens, salts or other constituents are simulated.

Line 1 is a title. Then come five groups, each as a count followed by that many names:

| Group | Count | Names |
|-------|-------|-------|
| 1 | number of pesticides | pesticide names, matched by name to [`pesticide.pes`](pes.md) |
| 2 | number of pathogens | pathogen names, matched by name to [`pathogens.pth`](pth.md) |
| 3 | number of heavy metals | metal names, not matched to any database (see [metals](mtl.md)) |
| 4 | number of salt ions | salt ion names, in the order given on the [salt inputs](salt.md#activation) page |
| 5 | number of other constituents | constituent names |

Each count is read from a separate line and the names that follow are read as one list, starting on the next line, so they can be on one line or several. A count of 0 still needs its names line: SWAT+ skips one line after the count, so leave a blank line (or any text) there. A pesticide or pathogen name that is not in its database is kept in the list but gets no parameters.

The constituent module uses the position of each constituent and not its name. Fertilizer input, selenium reactions and the reservoir parameters assume this order:

| Position | Constituent |
|----------|-------------|
| 1 | `seo4` (selenate) |
| 2 | `seo3` (selenite) |
| 3 | `boron` |

## File overview

| File | Content | Linked to objects by |
|------|---------|----------------------|
| `cs_hru.ini` | Initial dissolved and sorbed constituents in HRU soils | `cs` column of [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) |
| `cs_aqu.ini` | Initial dissolved and sorbed constituents in aquifers | `cs` column of `initial.aqu_cs` |
| `cs_channel.ini` | Initial concentrations in channels | `cs` column of `initial.cha_cs` |
| `cs_res` | Reservoir and wetland parameters and initial concentrations | `cs` column of `reservoir.res_cs` and `wetland.wet_cs` |
| `cs_irrigation` | Concentrations in irrigation water from outside the model | position, see below |
| `fertilizer.frt_cs` | Constituent content of fertilizers and manures | position in the fertilizer list |
| `cs_reactions` | Reaction parameters for soils and aquifers | HRU and aquifer order |
| `cs_uptake` | Daily constituent uptake by each plant | position in [`plants.plt`](../input-reference/plt.md) |
| [`cs_atmo.cli`](../input-reference/cli.md#cs_atmocli) | Concentration in rainfall and dry deposition | atmospheric deposition stations, see [climate inputs](cli.md) |
| `cs_recall.rec` | Loads from point sources | see [recall inputs](recall.md) |
| `cs_plants_boron` | Boron tolerance of plants | read but not used |
| `cs_urban` | Constituent content of sediment from impervious areas | read but not used |
| `cs_streamobs` | Channels for daily concentration output | not read |

## Missing files

`cs_hru.ini`, `cs_aqu.ini` and `cs_channel.ini` are opened whether or not they exist. If one is missing, SWAT+ creates an empty file of that name in the run directory and reads no records from it. An empty file, whether created this way or supplied, is read the same way.

The test project `refdata/Ames_sub1` in the SWAT+ repository contains empty `cs_hru.ini`, `cs_aqu.ini` and `cs_channel.ini` files created by earlier runs. It gives `null` for the constituent file in [`file.cio`](../input-reference/file-cio.md), so no constituents are simulated and the empty files have no effect on the results. If constituents are listed in `constituents.cs`, an empty file behaves as follows:

- Empty `cs_hru.ini`: there is no record for the HRUs, but HRU setup still reads record 1, which does not exist. Give at least one record.
- Empty `cs_aqu.ini`: when `initial.aqu_cs` is present, the aquifer search runs over the number of records in `cs_irrigation` and reads `cs_aqu.ini` records that do not exist. Give at least as many records as `cs_irrigation` has.
- Empty `cs_channel.ini`: there is no record for the channels, but channel setup still reads record 1, which does not exist. Give at least one record.

Two files are needed as soon as other constituents are listed in `constituents.cs`, because they are read for every HRU without a check that they were found:

- `cs_irrigation` is read for every HRU during setup.
- `cs_uptake` is read every day for every HRU with a growing plant.

Provide both whenever constituents are simulated, with zero values if there is nothing to add.

## cs_hru.ini

Initial constituents in HRU soils. Lines 1 to 5 are skipped. Each record then takes three lines:

| Line of record | Content |
|----------------|---------|
| 1 | Record name |
| 2 | Soil values: one dissolved concentration (mg/L) per constituent, then one sorbed concentration (mg/kg of soil) per constituent |
| 3 | Plant values: the same number of values, read but not used |

An HRU uses the record named in the `cs` column of its [`soil_plant.ini`](ini.md) record; if the name is not found, the first record is used. [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) has the `cs` column only when `event` in [`codes.bsn`](codes-bsn.md) is not 0. With `event` at 0, the column is not read and every HRU uses the first record of `cs_hru.ini`. Every soil layer starts with the same values.

## cs_aqu.ini

Initial constituents in aquifers. Lines 1 to 3 are skipped. Each later line is one record: name, one dissolved concentration (mg/L) per constituent, then one sorbed concentration (mg/kg) per constituent. The sorbed mass is calculated with an assumed aquifer bulk density of 2000 kg/m³.

Aquifers find their record through `initial.aqu_cs` (title, header, then rows with `name`, `pest`, `path`, `hmet`, `salt`, `cs`). Aquifer $n$ uses row $n$ of `initial.aqu_cs`, whatever the row's name, and the `cs` column of that row names a record in `cs_aqu.ini`. See [salt inputs](salt.md#salt_aquini) for the same link used by salts.

## cs_channel.ini

Initial concentrations in channel water. Lines 1 and 2 are skipped. Each later line is one record: name and one concentration (mg/L) per constituent. Channels find their record through `initial.cha_cs` as described for [`salt_channel.ini`](salt.md#salt_channelini), using its `cs` column.

## cs_res

Constituent parameters and initial concentrations for reservoirs and wetlands. Lines 1 to 15 are skipped (two title lines, twelve comment lines and a header). The file is ignored when the reservoir nutrient file in [`file.cio`](../input-reference/file-cio.md) is `null`. Each later line is one record:

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `name` | - | - | Record name, named in the `cs` column of `reservoir.res_cs` or `wetland.wet_cs`. |
| 2 | `v_seo4` | m/day | 0.001 | Settling velocity of selenate. |
| 3 | `v_seo3` | m/day | 0.001 | Settling velocity of selenite. |
| 4 | `v_born` | m/day | 0.001 | Settling velocity of boron. |
| 5 | `k_seo4` | 1/day | 0.05 | First-order loss rate of selenate. |
| 6 | `k_seo3` | 1/day | 0.03 | First-order loss rate of selenite. |
| 7 | `k_born` | 1/day | 0.0 | First-order loss rate of boron. |
| 8 | `theta_seo4` | - | 1.08 | Temperature factor for the selenate rate. |
| 9 | `theta_seo3` | - | 1.08 | Temperature factor for the selenite rate. |
| 10 | `theta_born` | - | 1.08 | Temperature factor for the boron rate. |
| 11 | `c_seo4` | mg/L | 0.0 | Initial selenate concentration. |
| 12 | `c_seo3` | mg/L | 0.0 | Initial selenite concentration. |
| 13 | `c_born` | mg/L | 0.0 | Initial boron concentration. |

All 13 values must be given; a short line takes its remaining values from the next line. A reservoir without a `cs_res` record starts with no constituents and uses the default rates in the table. `reservoir.res_cs` and `wetland.wet_cs` are described under [`salt_res`](salt.md#salt_res).

## cs_irrigation

Concentrations in irrigation water from outside the model. Lines 1 and 2 are skipped. Each later line is one record: name and one concentration (mg/L) per constituent.

An HRU uses the record at the same position as the `cs_hru.ini` record it uses; the name is not used. In 62.0.1 the transfer of constituents with irrigation water is switched off in water allocation, so these concentrations do not change the constituent balance.

## fertilizer.frt_cs

Constituent content of each fertilizer. Line 1 is a title and line 2 a header. Then one row per record of [`fertilizer.frt`](frt.md), in the same order and with the same number of rows:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Fertilizer name. Not checked against [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt). |
| 2 | `seo4` | kg/kg | Selenate per kg of material applied. |
| 3 | `seo3` | kg/kg | Selenite per kg of material applied. |
| 4 | `boron` | kg/kg | Boron per kg of material applied. |

The mass added (kg/ha) is the amount applied (kg/ha) times the value in the table. Constituents are added in the same cases as salts (see [`salt_fertilizer.frt`](salt.md#salt_fertilizerfrt)): with manure operations and decision-table `manure` actions whose manure has an `org_min` entry other than the first record of [`manure_om.frt`](../input-reference/frt.md#manure_omfrt), and with fertilizer operations on HRUs with standing water. For manure, the whole amount goes into the top soil layer.

## cs_reactions

Reaction parameters for soils and aquifers, organised in reaction groups and shale formations. Every HRU and every aquifer must have a row.

| Section | Content |
|---------|---------|
| Line 1, 2 | Title and header, skipped |
| Line 3 | Number of parameters $n_p$ and number of reaction groups $n_g$ |
| next $n_p$ lines | One parameter per line, with one value per reaction group |
| next line | Header, skipped |
| next line | Number of shale formations $n_s$ |
| next $n_s$ lines | Per shale formation: S/Se ratio of the shale, rate constant for autotrophic reduction of oxygen (1/day), rate constant for autotrophic reduction of nitrate (1/day) |
| next line | Header, skipped |
| next lines | One line per HRU, in HRU order: HRU number, reaction group, $n_s$ shale fractions (fraction of the HRU area over each shale formation) |
| next line | Header, skipped (only when the model has aquifers) |
| next lines | One line per aquifer, in aquifer order: aquifer number, reaction group, $n_s$ shale fractions |

The parameter lines are used in this order:

| Line | Parameter | Units | Used for |
|------|-----------|-------|----------|
| 1 | Selenium reduction inhibition factor for nitrate | - | soils, aquifers |
| 2 | Oxygen concentration in soil water | mg/L | soils |
| 3 | Oxygen concentration in groundwater | mg/L | aquifers |
| 4 | Sorption coefficient $K_d$ of selenate | L/kg | soils, aquifers |
| 5 | Sorption coefficient $K_d$ of selenite | L/kg | soils, aquifers |
| 6 | Sorption coefficient $K_d$ of boron | L/kg | soils, aquifers |
| 7 | Rate constant for selenate reduction in soil | 1/day | soils |
| 8 | Rate constant for selenate reduction in groundwater | 1/day | aquifers |

The first value of the HRU and aquifer lines is not checked; the line position decides. Further parameter lines are read but not used by soils and aquifers. The rate constant for selenite reduction is not read for soils or aquifers and stays 0, so selenite is not reduced there.

## cs_uptake

Specified daily constituent uptake by plants. Lines 1 to 3 are skipped. Then one row per plant in [`plants.plt`](../input-reference/plt.md), in the same order: name and one uptake value (kg/ha per day) per constituent. The plant name is not checked. While a plant has roots, its daily uptake of each constituent is split between the soil layers in proportion to the root mass in each layer and is limited to the mass in the layer.

## cs_plants_boron

Boron tolerance of plants. Line 1 is a title and line 2 is skipped, line 3 is a switch (0 = off, 1 = on), lines 4 to 7 are skipped, and then one row per plant in [`plants.plt`](../input-reference/plt.md): name, threshold $a$ and slope $b$. In 62.0.1 the values are read but no routine uses them, so boron has no effect on plant growth.

## cs_urban

Constituent content of sediment washed from impervious areas. Lines 1 and 2 are skipped. Each later line is an urban type name from [`urban.urb`](../input-reference/str.md#urbanurb) and one concentration (mg per kg of sediment) per constituent. In 62.0.1 the values are read but not used.

## cs_streamobs

A list of channels for daily concentration and load output to `cs_streamobs_output`: a title line, the number of channels, then one channel number per line. In 62.0.1 the switch that would read it is never set, so the file is not read and the output is not written.

## Example

`constituents.cs` for a run with one pesticide, the eight salt ions and the three constituents:

```
constituents.cs: constituent list
1
atrazine
0

0

8
so4 ca mg na k cl co3 hco3
3
seo4 seo3 boron
```

There are no pathogens or heavy metals, so their counts are 0 and each is followed by an empty names line.

A matching `cs_aqu.ini` record with 0.005 mg/L selenate in groundwater and 0.2 mg/kg sorbed selenate, values illustrative:

```
cs_aqu.ini: initial constituents in aquifers
seo4 seo3 boron: dissolved (mg/L), then sorbed (mg/kg)
name          seo4     seo3    boron   seo4_s   seo3_s  boron_s
aqu_cs1      0.005    0.001    0.100    0.200    0.050    1.000
```

## Related files

- [salt inputs](salt.md): the salt ions listed in `constituents.cs`, and the link files `initial.aqu_cs`, `initial.cha_cs`, `reservoir.res_cs` and `wetland.wet_cs`.
- [`file.cio`](file-cio.md): names `constituents.cs`.
- [`soil_plant.ini`](ini.md): names the `cs_hru.ini` record for each HRU.
- [`codes.bsn`](codes-bsn.md): `event` decides whether [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) has the `cs` column.
- [`fertilizer.frt`](frt.md): sets the row order of `fertilizer.frt_cs`.
- [`pesticide.pes`](pes.md), [`pathogens.pth`](pth.md), [metals](mtl.md): the other groups in `constituents.cs`.
- [`cs_atmo.cli`](cli.md) and [`cs_recall.rec`](recall.md): deposition and point-source loads.
- [gwflow inputs](gwflow.md): constituents become groundwater solutes when gwflow solute transport is on.

??? quote "Sources"

    - Master list: [`constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constit_db_read.f90); type `cs_db_type` in [`constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constituent_mass_module.f90)
    - Readers: [`cs_hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_hru_read.f90), [`cs_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_aqu_read.f90), [`cs_cha_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_cha_read.f90), [`res_read_csdb.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_csdb.f90), [`cs_irr_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_irr_read.f90), [`cs_fert_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_fert_read.f90), [`cs_reactions_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_reactions_read.f90), [`cs_uptake_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_uptake_read.f90), [`cs_plant_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_plant_read.f90), [`cs_urban_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_urban_read.f90)
    - Link files and initialisation: [`soil_plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_plant_init.f90), [`cs_hru_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_hru_init.f90), [`aqu_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init_cs.f90), [`sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`res_read_salt_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_salt_cs.f90)
    - Processes: [`cs_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_fert.f90), [`cs_fert_wet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_fert_wet.f90), [`cs_irrig.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_irrig.f90), [`cs_uptake.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_uptake.f90) (called from [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90)), [`cs_sorb_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_sorb_hru.f90), [`cs_sorb_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_sorb_aqu.f90), [`se_reactions_soil.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/se_reactions_soil.f90), [`se_reactions_aquifer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/se_reactions_aquifer.f90), [`res_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_cs.f90)
    - Types and variables: [`cs_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_module.f90), [`cs_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_data_module.f90), [`res_cs_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_cs_module.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | `constituents.cs` counts | `cs_db%num_pests`, `%num_paths`, `%num_metals`, `%num_salts`, `%num_cs` |
    | `constituents.cs` names | `cs_db%pests`, `%paths`, `%metals`, `%salts`, `%cs` |
    | `cs_hru.ini` soil and plant lines | `cs_soil_ini%soil`, `cs_soil_ini%plt` |
    | `cs_aqu.ini` | `cs_aqu_ini%aqu` |
    | `cs_channel.ini` | `cs_cha_ini%conc` |
    | `cs_res` | `res_cs_data` (`type reservoir_cs_data`) |
    | `cs_irrigation` | `cs_water_irr%water`, copied to `cs_irr%csc` |
    | `fertilizer.frt_cs` | `fert_cs` (`type fert_db_cs`) |
    | `cs_reactions` parameter lines 1 to 8 | `rct(1:8, group)`, copied to `se_ino3`, `oxy_soil`, `oxy_aqu`, `kd_seo4`, `kd_seo3`, `kd_born`, `kseo4` of `cs_rct_soil` and `cs_rct_aqu` |
    | `cs_reactions` shale lines | `rct_shale(:,1:3)`, copied to `sseratio`, `ko2a`, `kno3a` |
    | `cs_uptake` | `cs_uptake_kg` |
    | `cs_plants_boron` | `bor_tol_sim`, `bor_stress_a`, `bor_stress_b` |
    | `cs_urban` | `cs_urban_conc` |
    | `cs_streamobs` | `cs_str_obs` |

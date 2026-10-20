---
title: Salt inputs
description: Input files of the salt module, which simulates eight major salt ions in soils, plants, aquifers, channels, reservoirs and wetlands.
status: review
verified_against:
  - src/constit_db_read.f90
  - src/salt_hru_read.f90
  - src/salt_aqu_read.f90
  - src/salt_cha_read.f90
  - src/salt_irr_read.f90
  - src/salt_plant_read.f90
  - src/salt_roadsalt_read.f90
  - src/salt_uptake_read.f90
  - src/salt_urban_read.f90
  - src/salt_fert_read.f90
  - src/salt_hru_init.f90
  - src/salt_fert.f90
  - src/salt_fert_wet.f90
  - src/salt_irrig.f90
  - src/salt_roadsalt.f90
  - src/salt_uptake.f90
  - src/salt_chem_soil_single.f90
  - src/salt_chem_aqu.f90
  - src/salt_module.f90
  - src/salt_data_module.f90
  - src/constituent_mass_module.f90
  - src/aqu_read_init_cs.f90
  - src/ch_read_init_cs.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_init.f90
  - src/res_read_saltdb.f90
  - src/res_read_salt_cs.f90
  - src/wet_read_salt_cs.f90
  - src/res_initial.f90
  - src/wet_initial.f90
  - src/soil_plant_init.f90
  - src/hru_read.f90
  - src/pl_waterup.f90
  - src/pl_biomass_gro.f90
  - src/mgt_sched.f90
  - src/actions.f90
  - src/wallo_pou_deliv.f90
  - src/hru_control.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The salt module tracks eight salt ions in soil water, groundwater, channels, reservoirs and wetlands, together with five salt minerals in soils and aquifers that dissolve and precipitate. Salt enters from initial conditions, fertilizer and manure, road salt, atmospheric deposition and point sources, and leaves with plant uptake, runoff, percolation and flow. High soil salinity can reduce plant growth.

The salt files are not listed in [`file.cio`](file-cio.md); SWAT+ looks for them by name in the run directory. The constituent module, which uses the same master file, is on the [constituent inputs](cs.md) page.

## Activation

Salt simulation is switched on by listing salt ions in the salt block of [`constituents.cs`](cs.md#constituentscs). With no salt ions listed, or without [`constituents.cs`](../input-reference/cs.md#constituentscs), the salt files are ignored.

The ions must be listed in this order, because several routines use the position of an ion and not its name:

| Position | Ion |
|----------|-----|
| 1 | `so4` (sulfate) |
| 2 | `ca` (calcium) |
| 3 | `mg` (magnesium) |
| 4 | `na` (sodium) |
| 5 | `k` (potassium) |
| 6 | `cl` (chloride) |
| 7 | `co3` (carbonate) |
| 8 | `hco3` (bicarbonate) |

Every file below that has one value per ion gives the values in this order. Files with mineral fractions give five values in this order: CaCO₃, MgCO₃, CaSO₄, MgSO₄, NaCl.

## File overview

| File | Content | Linked to objects by |
|------|---------|----------------------|
| `salt_hru.ini` | Initial ion concentrations and mineral fractions in HRU soils | `salt` column of [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) |
| `salt_aqu.ini` | Initial ion concentrations and mineral fractions in aquifers | `salt` column of `initial.aqu_cs` |
| `salt_channel.ini` | Initial ion concentrations in channels | `salt` column of `initial.cha_cs` |
| `salt_res` | Initial ion concentrations in reservoirs and wetlands | `salt` column of `reservoir.res_cs` and `wetland.wet_cs` |
| `salt_irrigation` | Ion concentrations in irrigation water from outside the model | position, see below |
| `salt_fertilizer.frt` | Ion content of fertilizers and manures | position in the fertilizer list |
| `salt_road` | Road salt applied to the land surface | atmospheric deposition stations |
| [`salt_atmo.cli`](../input-reference/cli.md#salt_atmocli) | Ion concentration in rainfall and dry deposition | atmospheric deposition stations, see [climate inputs](cli.md) |
| `salt_recall.rec` | Ion loads from point sources | see [recall inputs](recall.md) |
| `salt_plants` | Salt tolerance of each plant | position in [`plants.plt`](../input-reference/plt.md) |
| `salt_uptake` | Daily ion uptake by each plant | position in [`plants.plt`](../input-reference/plt.md) |
| `salt_urban` | Ion content of sediment from impervious areas | urban type name in [`urban.urb`](../input-reference/str.md#urbanurb) |

## Missing files

`salt_hru.ini`, `salt_aqu.ini` and `salt_channel.ini` are opened whether or not they exist. If one is missing, SWAT+ creates an empty file of that name in the run directory and reads no records from it. An empty file, whether created this way or supplied, is read the same way: SWAT+ finds no title line and no records.

The test projects `refdata/Ames_sub1` and `refdata/Osu_1hru` in the SWAT+ repository contain empty `salt_hru.ini`, `salt_aqu.ini` and `salt_channel.ini` files created by earlier runs. Both projects give `null` for the constituent file in [`file.cio`](../input-reference/file-cio.md), so no salt ions are simulated and the empty files have no effect on the results. If salt ions are listed in [`constituents.cs`](../input-reference/cs.md#constituentscs), an empty file behaves as follows:

- Empty `salt_hru.ini`: there is no record for the HRUs, but HRU setup still reads record 1, which does not exist. Give at least one record.
- Empty `salt_aqu.ini`: no aquifer finds a record, so aquifers start with no salt ions and no salt minerals.
- Empty `salt_channel.ini`: there is no record for the channels, but channel setup still reads record 1, which does not exist. Give at least one record.

Some files are needed as soon as salt ions are listed, because the setup reads from them for every object without checking that they were found:

- `salt_irrigation` is read for every HRU during setup.
- `salt_road` is read every day for every HRU when [`atmodep.cli`](cli.md) is in use.

Provide these files whenever salts are simulated, with zero values if there is nothing to add.

## salt_hru.ini

Initial salt in HRU soils. Lines 1 to 5 are skipped. Each record then takes three lines:

| Line of record | Content |
|----------------|---------|
| 1 | Record name |
| 2 | Soil values: 8 ion concentrations in soil water (mg/L), then 5 mineral fractions (percent) |
| 3 | Plant values: 13 numbers, read but not used |

An HRU uses the record named in the `salt` column of its [`soil_plant.ini`](ini.md) record. If the name is not found, the first record is used. Every soil layer starts with the same values. The ion mass in a layer is the concentration times the water stored in the layer at the start of the run.

## salt_aqu.ini

Initial salt in aquifers. Lines 1 to 4 are skipped. Each later line is one record: name, 8 ion concentrations in groundwater (mg/L), and 5 mineral fractions (percent).

Aquifers find their record through `initial.aqu_cs`, which has a title line, a header line and one row per aquifer with the columns `name`, `pest`, `path`, `hmet`, `salt` and `cs`. The `salt` column names a record in `salt_aqu.ini`. For salts, aquifer $n$ uses row $n$ of `initial.aqu_cs`, whatever the row's name, so the rows must be in aquifer order. The ion mass is the concentration times the groundwater stored at the start of the run.

## salt_channel.ini

Initial salt in channel water. Lines 1 and 2 are skipped. Each later line is one record: name and 8 ion concentrations (mg/L).

Channels find their record through `initial.cha_cs` (title, header, then rows with `name`, `pest`, `path`, `hmet`, `salt`, `cs`). A channel uses the `initial.cha_cs` row at the same position as the [`initial.cha`](cha.md) row it selects by name; the `salt` column of that row names a record in `salt_channel.ini`. If the name is not found, the first record is used.

## salt_res

Initial salt in reservoirs and wetlands. Lines 1 to 11 are skipped (two title lines, eight comment lines and a header). Each later line is one record: name and 8 ion concentrations (mg/L). The file is ignored when the reservoir nutrient file in [`file.cio`](../input-reference/file-cio.md) is `null`.

Reservoirs find their record through `reservoir.res_cs` and wetlands through `wetland.wet_cs`. Both have two header lines and one row per reservoir (or wetland) data record with the columns `id`, `pest`, `weir`, `salt` and `cs`. `id` is the position of the record in [`reservoir.res`](res.md) or [`wetland.wet`](../input-reference/wet.md#wetlandwet), and `salt` names a record in `salt_res`. A wetland without a matching record starts with no salt.

## salt_irrigation

Ion concentrations in irrigation water taken from outside the model. Lines 1 and 2 are skipped. Each later line is one record: name and 8 ion concentrations (mg/L).

An HRU uses the record at the same position as the `salt_hru.ini` record it uses (record 3 of `salt_hru.ini` goes with record 3 of `salt_irrigation`); the name is not used. In 62.0.1 the transfer of salt with irrigation water is switched off in water allocation, so these concentrations do not change the salt balance.

## salt_fertilizer.frt

Ion content of each fertilizer. Line 1 is a title and line 2 a header. Then one row per record of [`fertilizer.frt`](frt.md), in the same order and with the same number of rows:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Fertilizer name. Not checked against [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt). |
| 2 | `so4` | kg/kg | Sulfate per kg of material applied. |
| 3 | `ca` | kg/kg | Calcium per kg of material applied. |
| 4 | `mg` | kg/kg | Magnesium per kg of material applied. |
| 5 | `na` | kg/kg | Sodium per kg of material applied. |
| 6 | `k` | kg/kg | Potassium per kg of material applied. |
| 7 | `cl` | kg/kg | Chloride per kg of material applied. |
| 8 | `co3` | kg/kg | Carbonate per kg of material applied. |
| 9 | `hco3` | kg/kg | Bicarbonate per kg of material applied. |

The salt added (kg/ha) is the amount applied (kg/ha) times the value in the table.

Where salt is added in 62.0.1:

- A manure operation in a management schedule or a `manure` action in a decision table adds salt, split between the top two soil layers by the surface fraction of the application method in [`chem_app.ops`](../input-reference/ops.md#chem_appops). The row used is the row at the position of the manure in [`manure_db.frt`](../input-reference/frt.md#manure_dbfrt), and salt is added only when the manure's `org_min` entry matches a record in [`manure_om.frt`](../input-reference/frt.md#manure_omfrt) other than the first.
- A fertilizer operation in a management schedule adds salt only when the HRU has standing water, and the salt goes into the ponded water.
- A fertilizer operation on dry soil adds no salt.

Salt from a fertilizer whose name in [`fertilizer.frt`](../input-reference/frt.md#fertilizerfrt) starts with `a` is reported as a soil amendment in the salt balance output; other fertilizers are reported as fertilizer.

## salt_road

Road salt applied to the soil surface. The file is organised by the atmospheric deposition stations of [`atmodep.cli`](cli.md) and uses the same time step as that file. Lines 1 to 4 are skipped. Then, for each station in the order of [`atmodep.cli`](../input-reference/cli.md#atmodepcli), one line with the station name followed by one line per ion (8 lines), each starting with the ion name:

| [`atmodep.cli`](../input-reference/cli.md#atmodepcli) time step | Values on each ion line | Daily application |
|-------------------------|-------------------------|-------------------|
| `aa` | 1 value, kg/ha per year | the value / 365, every day |
| `mo` | 1 value per month of the deposition record, kg/ha per month | the month's value / days in the month |
| `yr` | 1 value per year of the deposition record, kg/ha per year | spread over the days with precipitation and a mean temperature below 0 °C, in proportion to the day's precipitation |

Each HRU receives the road salt of the deposition station of its weather station, on its whole area, into the top soil layer. For the `yr` time step the precipitation and temperature used to spread the salt come from the weather station at the same position in the station list as the deposition station.

## salt_plants

Salt tolerance of plants and switches for salt stress.

| Line | Content |
|------|---------|
| 1, 2 | Title and header, skipped |
| 3 | Conversion factor from total dissolved solids (mg/L) to electrical conductivity (dS/m) |
| 4 | Skipped |
| 5 | Salt stress switch: 0 = off, 1 = on |
| 6 | Soil type: 1 = gypsiferous (CaSO₄) soils, 2 = NaCl soils |
| 7 | Stress method: 1 = salt stress applied after the other stresses, 2 = salt stress included with the other stresses |
| 8 to 11 | Skipped |
| 12 | Header, skipped |
| 13+ | One row per plant in [`plants.plt`](../input-reference/plt.md), in the same order: name, threshold $a$ (dS/m), slope $b$ (% per dS/m) |

The plant name is not checked; the row position decides.

### Salt stress

When the switch is on, SWAT+ computes for each soil layer within the root zone the total dissolved solids of the soil water at saturation, after mineral dissolution, and converts it to the electrical conductivity of the saturation extract $EC_e$ with the factor on line 3. The relative yield for that layer is

$$Y_r = \frac{100 - b\,(EC_e - a)}{100} \qquad \text{for } EC_e > a$$

limited to 0 to 1, and 1 when $EC_e \le a$. For gypsiferous soils 2 dS/m is added to $a$. A plant with $a = 0$ has no salt stress. The salt stress of the plant is the smallest $Y_r$ over its root zone layers.

With stress method 1, plant growth is multiplied by the salt stress after the smallest of the water, temperature, nitrogen, phosphorus and aeration stresses has been applied. With method 2, the salt stress is one of the stresses and the smallest of them is used.

## salt_uptake

Specified daily salt uptake by plants. Lines 1 to 3 are skipped. Then one row per plant in [`plants.plt`](../input-reference/plt.md), in the same order: name, and 8 uptake values (kg/ha per day). The plant name is not checked.

While a plant has roots, its daily uptake of each ion is split between the soil layers in proportion to the root mass in each layer and is limited to the ion mass in the layer. Without the file, plants take up no salt.

## salt_urban

Ion content of sediment washed from impervious areas. Lines 1 and 2 are skipped. Each later line is an urban type name from [`urban.urb`](hru.md) and 8 concentrations (mg of ion per kg of sediment). In 62.0.1 the values are read but not used.

## Example

`salt_plants` in the layout SWAT+ Editor writes, with salt stress on and illustrative values:

```
salt_plants: written by SWAT+ editor
conversion factor from TDS --> EC (EC=TDS/factor)
640.0
plant salinity tolerance
1            flag (0 = off; 1 = on)
2            flag (1=caso4 soils; 2=nacl soils)
1            flag (1=salt stress applied after other stresses applied; 2=included with other stresses)
NOTE: a and b values are for nacl soils
NOTE: if a and b values = 0, no salt impact
a = EC_sat threshold for impact on crop yield
b = slope of salinity impact on crop yield
            name           a           b
            agrl        1.70       12.00
            corn        1.70       12.00
```

TDS is divided by 640 to give $EC_e$. For corn, with $EC_e$ = 4 dS/m in a layer, the relative yield is $(100 - 12 \times (4 - 1.7))/100 = 0.72$. The rows after the header continue for every plant in [`plants.plt`](../input-reference/plt.md).

## Related files

- [`constituents.cs`](cs.md#constituentscs): lists the salt ions and switches the salt module on.
- [`soil_plant.ini`](ini.md): names the `salt_hru.ini` record for each HRU.
- [`fertilizer.frt`](frt.md): sets the row order of `salt_fertilizer.frt`.
- [`atmodep.cli`, `salt_atmo.cli`](cli.md): deposition stations and salt deposition.
- [`salt_recall.rec`](recall.md): salt loads from point sources.
- [gwflow inputs](gwflow.md): salt ions become groundwater solutes when gwflow solute transport is on.
- [constituent inputs](cs.md): the selenium and boron module.

??? quote "Sources"

    - Master list: [`constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constit_db_read.f90)
    - Readers: [`salt_hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_hru_read.f90), [`salt_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_aqu_read.f90), [`salt_cha_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_cha_read.f90), [`res_read_saltdb.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_saltdb.f90), [`salt_irr_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_irr_read.f90), [`salt_fert_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_fert_read.f90), [`salt_roadsalt_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_roadsalt_read.f90), [`salt_plant_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_plant_read.f90), [`salt_uptake_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_uptake_read.f90), [`salt_urban_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_urban_read.f90)
    - Link files: [`aqu_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init_cs.f90) (`initial.aqu_cs`), [`ch_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_init_cs.f90) (`initial.cha_cs`) with [`sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90), [`res_read_salt_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_salt_cs.f90), [`wet_read_salt_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_read_salt_cs.f90), [`soil_plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_plant_init.f90) and [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90)
    - Initialisation: [`salt_hru_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_hru_init.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90), [`wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90)
    - Processes: [`salt_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_fert.f90), [`salt_fert_wet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_fert_wet.f90) (called from [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90) and [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)), [`salt_irrig.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_irrig.f90), [`salt_roadsalt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_roadsalt.f90), [`salt_uptake.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_uptake.f90), [`salt_chem_soil_single.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_chem_soil_single.f90), [`salt_chem_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_chem_aqu.f90), salt stress in [`pl_waterup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_waterup.f90) and [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90)
    - Types and variables: [`constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constituent_mass_module.f90), [`salt_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_module.f90), [`salt_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_data_module.f90), [`res_salt_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_salt_module.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | `salt_hru.ini` soil and plant lines | `salt_soil_ini%soil`, `salt_soil_ini%plt` |
    | `salt_aqu.ini` | `salt_aqu_ini%conc`, `salt_aqu_ini%frac` |
    | `salt_channel.ini` | `salt_cha_ini%conc` |
    | `salt_res` | `res_salt_data%c_init` |
    | `salt_irrigation` | `salt_water_irr%water`, copied to `cs_irr%saltc` |
    | `salt_fertilizer.frt` | `fert_salt` (`type fert_db_salt`) |
    | `salt_road` | `rdapp_salt%salt%road`, `%roadmo`, `%roadyr`, `%roadday` |
    | `salt_plants` lines 3, 5, 6, 7 | `salt_tds_ec`, `salt_tol_sim`, `salt_soil_type`, `salt_effect` |
    | `salt_plants` columns $a$, $b$ | `salt_stress_a`, `salt_stress_b` |
    | `salt_uptake` | `salt_uptake_kg` |
    | `salt_urban` | `salt_urban_conc` |
    | `initial.aqu_cs` | `aqu_init_dat_c_cs` |
    | `initial.cha_cs` | `ch_init_cs` |
    | `reservoir.res_cs`, `wetland.wet_cs` | `res_dat_c_cs`, `wet_dat_c_cs` |

---
title: pesticide.pes and pesticide initial conditions
description: Pesticide parameter database (pesticide.pes), initial pesticide in soils, plants, channels, reservoirs and aquifers (pest_hru.ini, pest_water.ini), and the metabolite chain (pest_metabolite.pes).
status: review
verified_against:
  - src/pest_parm_read.f90
  - src/pesticide_data_module.f90
  - src/pest_hru_aqu_read.f90
  - src/pest_cha_res_read.f90
  - src/pest_metabolite_read.f90
  - src/constit_db_read.f90
  - src/constituent_mass_module.f90
  - src/pesticide_init.f90
  - src/sd_hydsed_init.f90
  - src/res_initial.f90
  - src/aqu_read_init_cs.f90
  - src/pest_tempdecay_module.f90
  - src/pest_decay.f90
  - src/pest_washp.f90
  - src/pest_lch.f90
  - src/pest_pl_up.f90
  - src/mgt_harvbiomass.f90
  - src/mgt_harvtuber.f90
  - src/ch_rtpest.f90
  - src/res_pest.f90
  - src/aqu_1d_control.f90
  - src/hru_control.f90
  - src/basin_module.f90
  - src/basin_read_prm.f90
  - src/cal_parm_select.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

SWAT+ simulates the pesticides listed in [`constituents.cs`](cs.md). It follows each one on plant foliage, in the soil layers, in surface runoff, lateral flow, tile flow and percolation, in channel water and bed sediment, in reservoirs and in aquifers. Four files describe them:

| File | Named in | Content |
|------|----------|---------|
| `pesticide.pes` | `hru_parm_db` line of [`file.cio`](file-cio.md) (default `pesticide.pes`) | Properties of each pesticide. |
| `pest_hru.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | Initial pesticide in soils and on plants. |
| `pest_water.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | Initial pesticide in channels, reservoirs and aquifers. |
| `pest_metabolite.pes` | fixed name, not in [`file.cio`](../input-reference/file-cio.md) | Degradation products (daughters) of each parent pesticide. |

Every pesticide named in [`constituents.cs`](../input-reference/cs.md#constituentscs) must have a row in `pesticide.pes` with the same name. The database can contain many more pesticides than the run simulates. Pesticide applications in [`management.sch`](management.md) and decision tables name rows of `pesticide.pes`, and the application method comes from [`chem_app.ops`](ops.md).

## pesticide.pes

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one pesticide with 17 values and a description, in the order below. The reader does not match columns by header name, so every value must be present and in this order.

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Name of the pesticide, up to 16 characters. Must be unique. |
| 2 | `soil_ads` | (mg/kg)/(mg/L) | 1 to 10⁹ | Soil adsorption coefficient normalized for soil organic carbon ($K_{oc}$). |
| 3 | `frac_wash` | fraction | 0 to 1 | Fraction of the pesticide on foliage washed off by a rainfall event. |
| 4 | `hl_foliage` | days | 0 to 10,000 | Half-life on foliage. 0 means no decay. |
| 5 | `hl_soil` | days | 0 to 100,000 | Half-life in the soil. 0 means no decay. |
| 6 | `solub` | mg/L | - | Solubility in water. Upper limit of the concentration in water leaving a soil layer. |
| 7 | `aq_hlife` | days | - | Half-life in channel, reservoir and aquifer water. 0 means no decay. Earlier documentation had `aq_reac` here, a reaction rate in 1/day; the column is now a half-life in days. |
| 8 | `aq_volat` | m/day | - | Volatilization coefficient in channel and reservoir water. |
| 9 | `mol_wt` | g/mol | - | Molecular weight. Used for the water and sediment mixing velocity and for the mass of metabolites. |
| 10 | `aq_resus` | m/day | - | Resuspension velocity of pesticide sorbed to bed sediment. |
| 11 | `aq_settle` | m/day | - | Settling velocity of pesticide sorbed to suspended sediment. |
| 12 | `ben_act_dep` | m | - | Depth of the active bed sediment layer. |
| 13 | `ben_bury` | m/day | - | Burial velocity in bed sediment. |
| 14 | `ben_hlife` | days | - | Half-life in bed sediment. 0 means no decay. Earlier documentation had `ben_reac` here, a reaction rate in 1/day; the column is now a half-life in days. |
| 15 | `pl_uptake` | - | 0 and up | Transpiration stream concentration factor (TSCF): ratio of the concentration in the water taken up by roots to the dissolved concentration in the soil. 0 turns plant uptake off. |
| 16 | `harvest_sink` | 0 or 1 | 0, 1 | 1: pesticide taken up by the plant leaves the system. 0: it stays in the plant and returns to the soil with the residue when the plant is harvested or killed. |
| 17 | `resistance_n` | fraction | 0 to 1 | Soil water used for the dissolved concentration in plant uptake. 0 uses the actual soil water, 1 uses field capacity, values in between blend the two. |
| 18 | `description` | - | - | Free text, one word. |

Columns 15 to 17 are new in 62.0.1. Files written for earlier revisions have 14 values (name and 13 numbers) and then a description. With such a file the first 14 values of each row are read correctly, and the read of the row stops with an error when it meets the description where `pl_uptake` is expected. No message is written and the next row is read normally. The three new columns keep their built-in values (`pl_uptake` = 0, `harvest_sink` = 1, `resistance_n` = 1), so there is no plant uptake, which is the behaviour of earlier revisions. To use plant uptake, add the three columns before the description.

### Half-lives and decay

Each day the pesticide in a compartment decays by first-order kinetics. The fraction left after one day is

$$f = \exp\left(-\frac{0.693}{t_{1/2}}\right)$$

where $t_{1/2}$ is the half-life of that compartment (`hl_foliage`, `hl_soil`, `aq_hlife` or `ben_hlife`). The half-life entered is a lumped value covering volatilization, photolysis, hydrolysis, biological degradation and other reactions. In channels the decay is scaled by the travel time through the reach, up to one day.

For most pesticides the foliar half-life is much shorter than the soil half-life because of volatilization and photodecomposition. If no foliar value is available, a common estimate is 0.25 to 0.5 times the soil half-life, lower for pesticides with a vapor pressure below 10⁻⁵ mm Hg, and at most 30 days.

### Temperature-dependent decay

Column 7 of [`parameters.bsn`](parameters-bsn.md) switches temperature-dependent decay on. The SWAT+ Editor writes this column under the header `exp_sed`. When its value is 1, each half-life is taken as the value at 25 °C and adjusted with a Q10 of 2.58:

$$t_{1/2}(T) = t_{1/2,25}\; 2.58^{(25 - T)/10}$$

The temperature $T$ is the soil layer temperature for soil, the top soil layer temperature for foliage, and the water temperature for channel water and bed sediment. For aquifers the temperature is 0 °C in 62.0.1, so aquifer half-lives are about 10.7 times the 25 °C value. Reservoirs do not use the adjustment.

Any other value in that column gives the constant decay above. Check this column when a model is moved to 62.0.1: editor files commonly have 1.0 there, which switches the adjustment on.

### Sorption and transport

The soil adsorption coefficient of a layer is

$$K_d = K_{oc}\,\frac{OC}{100}$$

where $OC$ is the organic carbon content of the layer in percent. The pesticide in a layer is split between the soil and the water flowing through it according to $K_d$. The concentration in water leaving a layer is limited to `solub`. The concentration in surface runoff is the concentration in percolate times `pest_perc` of [`parameters.bsn`](../input-reference/parameters-bsn.md).

On a day with at least 2.54 mm of precipitation, `frac_wash` of the pesticide on each plant's foliage is washed off to the top soil layer.

### Plant uptake

When `pl_uptake` is above 0, growing plants take up pesticide from each soil layer with the water they transpire:

$$U = \mathrm{TSCF}\;\frac{W_{up}}{\theta_{eff} + W_{up} + K_d\,\rho_b\,h}\;M$$

where $W_{up}$ is the water taken up from the layer (mm), $\theta_{eff}$ is the soil water blended toward field capacity by `resistance_n`, $\rho_b$ the bulk density, $h$ the layer thickness (mm) and $M$ the pesticide in the layer (kg/ha). Uptake is reported as `pl_uptake` in the pesticide output. With `harvest_sink` = 0, the pesticide kept in the plant returns to the soil when the plant is harvested or killed.

### Metabolites

When a parent pesticide decays, a daughter listed in `pest_metabolite.pes` receives

$$M_{daughter} = \Delta M_{parent}\; f_{frac}\;\frac{MW_{daughter}}{MW_{parent}}$$

where $f_{frac}$ is the daughter fraction for that compartment and $MW$ the `mol_wt` values. Foliage uses `foliar_fr`, soil uses `soil_fr`, channel water uses `aq_fr` and channel bed sediment uses `ben_fr`. In 62.0.1 reservoirs (water and bed) and aquifers use `soil_fr`.

### Calibration

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md): `pst_koc`, `pst_washoff`, `pst_foliar_hlife`, `pst_soil_hlife`, `pst_solub`, `pst_aq_hlife`, `pst_aq_volat`, `pst_aq_settle`, `pst_aq_resus`, `pst_ben_hlife`, `pst_ben_bury` and `pst_ben_act_dep`. The daily decay factors are computed from the half-lives when `pesticide.pes` is read, so a calibration change to a half-life only has an effect when temperature-dependent decay is on.

### pesticide.pes example

The first rows of `refdata/Osu_1hru/pesticide.pes` in the SWAT+ repository, as shipped:

```
pesticide.pes: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  soil_ads     frac_wash    hl_foliage       hl_soil         solub      aq_hlife      aq_volat        mol_wt      aq_resus     aq_settle   ben_act_dep      ben_bury     ben_hlife  description
245-tp              2600.00000       0.40000       5.00000      20.00000       2.50000       0.00700       0.00001       0.10000       0.00200       0.50000       0.30000       0.00200       0.05000  Silvex_Amine
2plus2                20.00000       0.95000      10.00000      21.00000  660000.00000       0.00700       0.00001       0.10000       0.00200       0.50000       0.30000       0.00200       0.05000  Mecoprop
```

The file was written for revision 60.5.4 and has no `pl_uptake`, `harvest_sink` or `resistance_n` columns. As described above, each row is read up to `ben_hlife`, the description is not stored, and the three new columns take their built-in values, so no pesticide is taken up by plants.

Silvex (`245-tp`) sorbs strongly ($K_{oc}$ of 2600) and has a soil half-life of 20 days. Mecoprop (`2plus2`) is very soluble and hardly sorbs.

Every row has `aq_hlife` = 0.007 and `ben_hlife` = 0.05. These match the reaction coefficients in 1/day of the older database format, but 62.0.1 reads them as half-lives in days. A half-life of 0.007 days leaves a fraction $\exp(-0.693/0.007) \approx 10^{-43}$ after one day, and 0.05 days leaves about $10^{-6}$. Osu_1hru has 1 in column 7 of [`parameters.bsn`](../input-reference/parameters-bsn.md), so the half-lives are adjusted for temperature (except in reservoirs), which lengthens them at temperatures below 25 °C but not enough to change the result. Any of these pesticides that reached channel water, bed sediment, a reservoir or an aquifer would be almost entirely gone within a day. Osu_1hru has no [`constituents.cs`](../input-reference/cs.md#constituentscs), so in that model no pesticide is simulated and the file is read without effect.

## pest_hru.ini

Initial pesticide in the soil and on plants of HRUs. An HRU selects a record by name in the `pest` column of [`soil_plant.ini`](ini.md).

The file is read in two passes that expect different layouts:

- The first pass counts records. It expects a title line, then for each record a header line, a name line and one line per pesticide.
- The second pass reads the values. It expects a title line and one header line, then for each record a name line and one line per pesticide.

A file with one record satisfies both. With more than one record the second pass reads the header line of record 2 as its name and the values that follow are shifted, so use one record.

Each pesticide line has three values, one line per pesticide in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs):

| Value | Units | Description |
|-------|-------|-------------|
| name | - | Pesticide name, for readability. Not checked. |
| soil | mg/kg | Concentration in the soil. The same concentration is given to every soil layer. |
| plant | kg/ha | Pesticide on the foliage. It is shared among the plants by leaf area; if there is no leaf area at the start, nothing is put on the foliage. |

## pest_water.ini

Initial pesticide in channels, reservoirs, wetlands and aquifers. Channels, reservoirs and wetlands select a record by name in their initial condition files ([`initial.cha`](sd-channel.md), [`initial.res`](res.md)), and aquifers in [`initial.aqu`](aqu.md).

Line 1 is a title and line 2 a header. Each record starts with a name line. The values follow as one list: a label, then the water value of each pesticide, then the bed sediment value of each pesticide, in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs). Line breaks within the list are free, but the counting pass expects two lines per pesticide after the name line. For two pesticides:

```
pest_water.ini: initial pesticide in water
name
ch_init
atrazine  0.002
0.001
0.05
0.02
```

Here `atrazine` is the label, the water values are 0.002 and 0.001, and the bed sediment values 0.05 and 0.02.

| Value | Units | Description |
|-------|-------|-------------|
| water | mg/L | Concentration in the water. Channels multiply it by the initial channel water volume. Aquifers read it as mg/kg of aquifer material over the aquifer depth with a bulk density of 2.0 t/m³. |
| benthic | mg/kg | Concentration in the active bed sediment layer. Channels multiply it by the volume of the active bed layer. |

Reservoirs use both values as given, without a conversion by volume.

## pest_metabolite.pes

The degradation products of each parent pesticide. SWAT+ reads it if a file of this name exists in the run directory.

Line 1 is a title and line 2 a header. For each parent there is one line with the parent name and the number of daughters, followed by one line per daughter:

| Value | Units | Description |
|-------|-------|-------------|
| `name` | - | Daughter pesticide name. Must also be listed in [`constituents.cs`](../input-reference/cs.md#constituentscs) and `pesticide.pes`. |
| `foliar_fr` | fraction | Fraction of the parent decayed on foliage that becomes this daughter. |
| `soil_fr` | fraction | Fraction of the parent decayed in the soil that becomes this daughter. Also used in reservoirs and aquifers. |
| `aq_fr` | fraction | Fraction of the parent decayed in channel water that becomes this daughter. |
| `ben_fr` | fraction | Fraction of the parent decayed in channel bed sediment that becomes this daughter. |

The parent name must match a row of `pesticide.pes`. If it does not, its daughter lines are not skipped and the rest of the file is read out of step.

```
pest_metabolite.pes: metabolites
parent        num_metab
aatrex        1
deethyl_atr   0.2   0.3   0.1   0.1
```

Atrazine (`aatrex`) has one daughter. 30% of the atrazine decayed in the soil, adjusted by the ratio of molecular weights, becomes `deethyl_atr`.

## Related files

- [`constituents.cs`](cs.md): the list of pesticides simulated.
- [`soil_plant.ini`](ini.md): links HRUs to `pest_hru.ini` records.
- [`initial.cha`](sd-channel.md), [`initial.res`](res.md), [`initial.aqu`](aqu.md): link channels, reservoirs and aquifers to `pest_water.ini` records.
- [`chem_app.ops`](ops.md) and [`management.sch`](management.md): pesticide applications.
- [`parameters.bsn`](parameters-bsn.md): `pest_perc` and the temperature-dependent decay switch in column 7.
- [Pathogens](pth.md) and [heavy metals](mtl.md) use the same initial condition layout.

??? quote "Sources"

    - Readers: [`pest_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_parm_read.f90), [`pest_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_hru_aqu_read.f90), [`pest_cha_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_cha_res_read.f90), [`pest_metabolite_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_metabolite_read.f90)
    - Types: `type pesticide_db`, `type pesticide_cp`, `type daughter_decay_fractions` in [`pesticide_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pesticide_data_module.f90); `type cs_soil_init_concentrations` and `type cs_water_init_concentrations` in [`constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constituent_mass_module.f90)
    - Pesticide list crosswalk: [`constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constit_db_read.f90)
    - Initial conditions: [`pesticide_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pesticide_init.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90), [`aqu_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init_cs.f90)
    - Landscape processes: [`pest_decay.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_decay.f90), [`pest_washp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_washp.f90), [`pest_lch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_lch.f90), [`pest_pl_up.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_pl_up.f90), [`mgt_harvbiomass.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvbiomass.f90), [`mgt_harvtuber.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvtuber.f90)
    - Temperature adjustment: [`pest_tempdecay_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_tempdecay_module.f90)
    - Channels, reservoirs and aquifers: [`ch_rtpest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpest.f90), [`res_pest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_pest.f90), [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90)
    - Switch in parameters.bsn: `bsn_prm%temp_decay` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - Calibration parameters: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `pestdb%name` |
    | `soil_ads` | `pestdb%koc` |
    | `frac_wash` | `pestdb%washoff` |
    | `hl_foliage` | `pestdb%foliar_hlife` |
    | `hl_soil` | `pestdb%soil_hlife` |
    | `aq_hlife`, `aq_volat`, `aq_resus`, `aq_settle` | `pestdb%` same names |
    | `ben_act_dep`, `ben_bury`, `ben_hlife` | `pestdb%` same names |
    | `pl_uptake`, `harvest_sink`, `resistance_n` | `pestdb%` same names |
    | `description` | `pestdb%descrip` |
    | parameters.bsn column 7 (`exp_sed`) | `bsn_prm%temp_decay` |
    | pest_hru.ini record | `pest_soil_ini%name`, `%soil`, `%plt` |
    | pest_water.ini record | `pest_init_name`, `pest_water_ini%water`, `%benthic` |
    | pest_metabolite.pes daughter | `pestcp%daughter` |

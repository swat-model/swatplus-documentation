---
title: Initial conditions (*.ini)
description: Initial plant communities (plant.ini), soil initialization links (soil_plant.ini), initial soil nutrients (nutrients.sol) and initial water quality of channels, reservoirs and wetlands (om_water.ini).
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_read.f90
  - src/proc_db.f90
  - src/main.f90.in
  - src/readpcom.f90
  - src/plant_data_module.f90
  - src/plant_init.f90
  - src/pl_root_gro.f90
  - src/soil_plant_init.f90
  - src/hru_module.f90
  - src/hru_read.f90
  - src/solt_db_read.f90
  - src/soil_data_module.f90
  - src/soil_nutcarb_init.f90
  - src/carbon_bsn_read.f90
  - src/hydro_init.f90
  - src/om_water_init.f90
  - src/hydrograph_module.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_init.f90
  - src/res_read.f90
  - src/res_initial.f90
  - src/wet_initial.f90
  - src/aqu_read_init.f90
  - src/salt_hru_read.f90
  - src/salt_aqu_read.f90
  - src/salt_cha_read.f90
  - src/cs_hru_read.f90
  - src/cs_aqu_read.f90
  - src/cs_cha_read.f90
  - src/hmet_hru_aqu_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The initialization files set the state of plants, soils and water bodies on the first day of the run. The general ones are:

- `plant.ini`: plant communities, with the starting state of each plant. A land use in [`landuse.lum`](lum.md) names a community in its `plnt_com` column.
- `soil_plant.ini`: for each HRU, links to the records that initialize soil nutrients, pesticides, pathogens, salts, heavy metals and constituents. An HRU names a record in the `soil_plant_init` column of [`hru-data.hru`](hru.md).
- `nutrients.sol`: initial soil nitrate, labile phosphorus and humus properties, named in the `nutrients` column of `soil_plant.ini`.
- `om_water.ini`: initial water, sediment and nutrient concentrations of channels, reservoirs and wetlands, named in the `org_min` column of their initial files.

## Initialization files

The `init` line of [`file.cio`](file-cio.md) has eleven file names. `nutrients.sol` is the second name on the `soils` line. Several salt and constituent files are opened under fixed names, whatever [`file.cio`](../input-reference/file-cio.md) says.

| File | How the name is set | Status in 62.0.1 | Documented in |
|------|---------------------|------------------|---------------|
| `plant.ini` | `init` line, name 1 | Read | [plant.ini](#plantini) |
| `soil_plant.ini` | `init` line, name 2 | Read | [soil_plant.ini](#soil_plantini) |
| `om_water.ini` | `init` line, name 3 | Read | [om_water.ini](#om_waterini) |
| [`pest_hru.ini`](../input-reference/pes.md#pest_hruini) | `init` line, name 4 | Read | [pesticides](pes.md) |
| [`pest_water.ini`](../input-reference/pes.md#pest_waterini) | `init` line, name 5 | Read | [pesticides](pes.md) |
| [`path_hru.ini`](../input-reference/pth.md#path_hruini) | `init` line, name 6 | Read | [pathogens](pth.md) |
| [`path_water.ini`](../input-reference/pth.md#path_waterini) | `init` line, name 7 | Read | [pathogens](pth.md) |
| [`hmet_hru.ini`](../input-reference/mtl.md#hmet_hruini) | `init` line, name 8 | Read, values not used | [heavy metals](mtl.md) |
| `hmet_water.ini` | `init` line, name 9 | Not read | [heavy metals](mtl.md) |
| [`salt_hru.ini`](../input-reference/salt.md#salt_hruini) | `init` line, name 10 | The [`file.cio`](../input-reference/file-cio.md) name is not used. SWAT+ opens a file called [`salt_hru.ini`](../input-reference/salt.md#salt_hruini). | [salts](salt.md) |
| `salt_water.ini` | `init` line, name 11 | Not read. Water bodies take their initial salts from [`salt_aqu.ini`](../input-reference/salt.md#salt_aquini) and [`salt_channel.ini`](../input-reference/salt.md#salt_channelini) (fixed names) and from the reservoir salt file. | [salts](salt.md) |
| [`salt_aqu.ini`](../input-reference/salt.md#salt_aquini), [`salt_channel.ini`](../input-reference/salt.md#salt_channelini) | Fixed names, not in [`file.cio`](../input-reference/file-cio.md) | Read | [salts](salt.md) |
| [`cs_hru.ini`](../input-reference/cs.md#cs_hruini), [`cs_aqu.ini`](../input-reference/cs.md#cs_aquini), [`cs_channel.ini`](../input-reference/cs.md#cs_channelini) | Fixed names, not in [`file.cio`](../input-reference/file-cio.md) | Read | [constituents](cs.md) |
| `nutrients.sol` | `soils` line, name 2 | Read | [nutrients.sol](#nutrientssol) |

All of these files are free format and whitespace-separated, with a title on line 1 and a column header on line 2, both skipped. Columns are read by position. Names are matched case-sensitively.

## plant.ini

Each plant community is a block: one community line, then one line for each plant in the community. A community can be plants growing together (a mixed stand) or the crops of a rotation, of which only some are growing at the start.

If `plant.ini` is missing or named `null`, no community exists, and every land use whose `plnt_com` is not `null` is reported in `diagnostics.out` as `<landuse> <community> not found in plant.ini`.

### Community line

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `pcom_name` | - | Community name, up to 40 characters, matched against `plnt_com` in [`landuse.lum`](../input-reference/lum.md). Names must be unique. |
| 2 | `plt_cnt` | - | Number of plant lines that follow, called `plnt_cnt` in earlier documentation. The reader counts communities with this number, so it must equal the number of plant lines. |
| 3 | `rot_yr_ini` | - | Year of the rotation in which the run starts. SWAT+ steps through the management schedule, counting a new year at each `skip` operation or each drop in day of year, and starts at the first operation of this rotation year on or after the start day of the run. Decision tables see it as the current rotation year. |

### Plant lines

| # | Column | Units | Range | Description |
|---|--------|-------|-------|-------------|
| 1 | `plt_name` | - | - | Plant name in [`plants.plt`](plt.md), called `plnt_name` in earlier documentation. |
| 2 | `lc_status` | - | `y`, `n` | Land cover status at the start: `y` growing, `n` not growing (it starts when a planting operation names it). |
| 3 | `lai_init` | m²/m² | 0 to 8 | Initial leaf area index. Used only when `lc_status` is `y`. |
| 4 | `bm_init` | kg/ha | 0 and up | Initial total plant biomass. It is set whatever `lc_status` is; its N and P contents follow from the plant's nutrient fractions at the starting stage of growth. |
| 5 | `phu_init` | fraction | 0 to 1 | Fraction of the heat units to maturity already accumulated at the start of the current growing season. |
| 6 | `plnt_pop` | plants/m² | - | Plant population. Read but not used: the maximum LAI is always the `lai_pot` of [`plants.plt`](../input-reference/plt.md), with no population adjustment. |
| 7 | `yrs_init` | fraction | 0 to 1 | For trees and other perennials, the current age as a fraction of the years to maturity (`mat_yrs` in [`plants.plt`](../input-reference/plt.md)). 0.5 for a tree with `mat_yrs` = 30 means a 15-year-old stand. Not used for annuals. |
| 8 | `rsd_init` | kg/ha | 0 to 10 000 | Initial surface residue from this plant. |

### Starting state

For each plant in the community, SWAT+ sets at the start of the run:

- Heat units to maturity, from `days_mat` in [`plants.plt`](../input-reference/plt.md) and the weather generator temperatures (see [plants.plt](plt.md)).
- Maturity stage: `phu_init` for annuals; `yrs_init` for perennials, whose year of growth is $\max(1, \lfloor \mathrm{yrs\_init} \times \mathrm{mat\_yrs} \rfloor)$ and whose lifetime heat unit fraction is $\mathrm{yrs\_init} + \mathrm{phu\_init} / \mathrm{mat\_yrs}$.
- Canopy height: $\mathrm{yrs\_init} \times h_{max}$ for perennials; for annuals $h_{max}\sqrt{f}$, where $f$ is the fraction of maximum LAI that the LAI curve of [`plants.plt`](../input-reference/plt.md) gives for `phu_init`.
- LAI from `lai_init` and biomass from `bm_init`. If the plant is growing, its root depth, root mass and seed mass are also set from the maturity stage.
- Surface residue from `rsd_init`, with carbon 42% of the residue mass, a C:N ratio of 10 and a C:P ratio of 100. The residue of all plants in the community is added together, so a two-crop rotation with 10 000 kg/ha each starts with 20 000 kg/ha.

In 62.0.1 a perennial that starts the run growing gets its lifetime heat unit fraction from `yrs_init` and `phu_init` before its roots are set. Earlier revisions left it at zero, which kept the starting root depth of perennials at the 25.4 mm minimum whatever their age.

A plant name that is not in [`plants.plt`](../input-reference/plt.md) is not reported. The reader's check for a missing name can never trigger, and the plant silently takes the parameters of the first plant in [`plants.plt`](../input-reference/plt.md). Check plant names in `plant.ini` against [`plants.plt`](../input-reference/plt.md) by hand.

### Example

`refdata/Ames_sub1/plant.ini` in the SWAT+ repository, first communities, with the spacing reduced:

```
plant.ini:
pcom_name  plt_cnt  rot_yr_ini  plt_name  lc_status  lai_init  bm_init      phu_init  plnt_pop  yrs_init  rsd_init
cosy_comm        2           1
                                corn      n          0.00000   0.00000      0.00000   0.00000   0.00000   10000.00000
                                soyb      n          0.00000   0.00000      0.00000   0.00000   0.00000   10000.00000
corn_comm        1           1
                                corn      n          0.00000   0.00000      0.00000   0.00000   0.00000   10000.00000
wetw_comm        1           1
                                wetw      y          2.00000   50000.00000  0.00000   0.00000   1.00000   10000.00000
```

`cosy_comm` is a corn and soybean rotation in which neither crop is growing at the start; the schedule plants them. Its two plant lines give 20 000 kg/ha of starting surface residue. `wetw_comm` is a wetland forest that starts growing, mature (`yrs_init` = 1), with LAI 2 and 50 000 kg/ha of biomass.

## soil_plant.ini

Each line links an HRU to its soil initialization records. [`hru-data.hru`](../input-reference/hru.md) names a record in its `soil_plant_init` column.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Record name, up to 40 characters. |
| 2 | `sw_frac` | fraction | Initial soil water as a fraction of field capacity. Read but not used; initial soil water comes from `sw_init` in [`parameters.bsn`](parameters-bsn.md) (see [soils.sol](sol.md#initial-soil-water)). |
| 3 | `nutrients` | - | Record in [nutrients.sol](#nutrientssol). |
| 4 | `pest` | - | Record in [`pest_hru.ini`](../input-reference/pes.md#pest_hruini) ([pesticides](pes.md)). |
| 5 | `path` | - | Record in [`path_hru.ini`](../input-reference/pth.md#path_hruini) ([pathogens](pth.md)). |
| 6 | `salt` | - | Record in [`salt_hru.ini`](../input-reference/salt.md#salt_hruini) ([salts](salt.md)). |
| 7 | `hmet` | - | Record in [`hmet_hru.ini`](../input-reference/mtl.md#hmet_hruini) ([heavy metals](mtl.md)). |
| 8 | `cs` | - | Record in [`cs_hru.ini`](../input-reference/cs.md#cs_hruini) ([constituents](cs.md)). Read only when the `event` column of [`codes.bsn`](codes-bsn.md#extra-input-columns) is not 0. |

The model reads column 6 as the salt record and column 7 as the heavy metal record. Some SWAT+ Editor versions write the header as `... path hmet salt`, the other way round. A salt record name placed in the column the Editor labels `salt` is then read as a heavy metal name, and the HRU uses the first [`salt_hru.ini`](../input-reference/salt.md#salt_hruini) record instead. Put the salt name in column 6 when salts are simulated.

Without a constituent column (the usual case), constituent runs use the first [`cs_hru.ini`](../input-reference/cs.md#cs_hruini) record for every HRU.

### Name matching

When [`hru-data.hru`](../input-reference/hru.md) is read, each HRU's `soil_plant_init` name is matched, and then the names in that record are matched against their files. When a name is not found:

- `nutrients`: the HRU uses the built-in values in the [nutrients.sol](#nutrientssol) table.
- `pest`, `path`, `salt`, `hmet`, `cs`: the HRU uses the first record of that file.
- `soil_plant_init` itself: nothing is reported (the check for a missing name can never trigger), and the HRU uses the first record of `soil_plant.ini`.

A project needs a `soil_plant.ini` file. If the file named in [`file.cio`](../input-reference/file-cio.md) is missing, SWAT+ creates an empty file of that name and the soil initialization has no record to use.

### Example

`refdata/Osu_1hru/soil_plant.ini`:

```
soil_plant.ini: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   sw_frac         nutrients              pest              path              hmet              salt
soilplant1             0.00000          soilnut1              null              null              null              null
```

One record, `soilplant1`, with soil nutrients from `soilnut1` in `nutrients.sol` and no pesticide, pathogen, heavy metal or salt records. This file has the Editor's `hmet salt` header order.

## nutrients.sol

Initial soil nitrogen and phosphorus and the humus properties of the static carbon model. Each record is one line. `soil_plant.ini` names a record in its `nutrients` column.

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | `default` | Record name, up to 16 characters. A longer name in `soil_plant.ini` does not match. |
| 2 | `exp_co` | 1/mm | 0.001 | Depth coefficient for the decrease of nitrate and labile P with depth. Values above 0.005 are replaced by 0.001. |
| 3 | `lab_p` | mg/kg | 5.0 | Labile (soluble) P concentration at the soil surface. 5.0 is used if 0. |
| 4 | `nitrate` | mg/kg | 7.0 | Nitrate N concentration at the soil surface. 7.0 is used if 0. |
| 5 | `fr_hum_act` | fraction | 0.02 | Fraction of humus in the active pool. 0.02 is used if 0. Static carbon model only. |
| 6 | `hum_c_n` | ratio | 10.0 | Humus C:N ratio (8 to 12). Static carbon model only; must not be 0. |
| 7 | `hum_c_p` | ratio | 80.0 | Humus C:P ratio (70 to 90). Static carbon model only; must not be 0. |
| 8 | `inorgp` | mg/kg | 0.5 | Inorganic P. Read but not used. |
| 9 | `watersol_p` | mg/kg | 0.15 | Water-soluble P. Read but not used. |
| 10 | `h3a_p` | mg/kg | 0.25 | H3A-extractable P. Read but not used. |
| 11 | `mehlich_p` | mg/kg | 1.2 | Mehlich-extractable P. Read but not used. |
| 12 | `bray_strong_p` | mg/kg | 0.85 | Strong Bray-extractable P. Read but not used. |

The SWAT+ Editor also writes a `description` column, which is not read. The built-in values apply to HRUs whose `nutrients` name is `null` or not found, and to all HRUs when `nutrients.sol` is missing or named `null` in [`file.cio`](../input-reference/file-cio.md).

### Initial mineral nitrogen and phosphorus

The concentrations at the surface decrease exponentially with the depth $z$ (mm) to the bottom of each soil layer, and are converted to mass with the layer's bulk density $\rho_b$ (Mg/m³) and thickness $h$ (mm):

$$NO3_{ly} = \mathrm{nitrate}\; e^{-\mathrm{exp\_co}\,z}\;\frac{\rho_b\,h}{100}, \qquad P_{lab,ly} = \mathrm{lab\_p}\; e^{-\mathrm{exp\_co}\,z}\;\frac{\rho_b\,h}{100}$$

in kg/ha. The active mineral P pool is $P_{lab}\,(1 - PSP)/PSP$, with the phosphorus availability index $PSP$ from `psp` in [`parameters.bsn`](parameters-bsn.md), and the stable pool is four times the active pool. With the Vadas and White phosphorus model (`soil_p` = 1 in [`codes.bsn`](../input-reference/codes-bsn.md)), $PSP$ (0.1 to 0.7) and the stable to active ratio (1 to 7) are instead estimated from each layer's clay, organic carbon and labile P.

### Initial organic pools

The organic carbon of each layer comes from the `carbon` column of [`soils.sol`](sol.md#carbon-and-nutrients): $C_{ly} = 10\,000\,h\,\rho_b \times \mathrm{carbon}/100$ kg/ha, with organic N and P at C:N 10 and C:P 100 before the split into pools. The split depends on the `carbon` column of [`codes.bsn`](codes-bsn.md#carbon-model):

- Static carbon model (0): the active humus pool gets `fr_hum_act` of the organic matter and the stable pool the rest. The N and P of both pools are their carbon divided by `hum_c_n` and `hum_c_p`.
- CENTURY model (2): the share `init_seq` of [`carbon.bsn`](carbon-bsn.md#initial-carbon-pools) goes to the passive humus, slow humus and microbial pools, and the rest to metabolic and structural litter. Fixed C:N and C:P ratios are used; `fr_hum_act`, `hum_c_n` and `hum_c_p` are not. The slow humus pool follows the `mathers_method` switch of [`carbon.bsn`](../input-reference/carbon-bsn.md).

In 62.0.1 the CENTURY pools are set up for carbon model 2 (earlier revisions tested for 1), the litter share is $1 - \mathrm{init\_seq}$ from [`carbon.bsn`](../input-reference/carbon-bsn.md) instead of a fixed 5%, and a non-lignin structural pool is also initialized.

### Example

`refdata/Osu_1hru/nutrients.sol`:

```
nutrients.sol: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    exp_co         lab_p       nitrate    fr_hum_act       hum_c_n       hum_c_p        inorgp    watersol_p         h3a_p     mehlich_p  bray_strong_p  description
soilnut1               0.00050       5.00000       7.00000       0.02000      10.00000      80.00000       3.50000       0.15000       0.25000       1.20000       0.85000
```

Surface nitrate 7 mg/kg and labile P 5 mg/kg. With `exp_co` = 0.0005, the concentrations fall to $e^{-0.5} = 61\%$ of the surface value at 1000 mm.

## om_water.ini

Initial water and water quality of channels, reservoirs and wetlands. Each line is one record; the `org_min` column of [`initial.cha`](cha.md) (channels) or [`initial.res`](res.md) (reservoirs and wetlands) names a record.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Record name, up to 16 characters. |
| 2 | `vol` | fraction | Initial water. Channels: fraction of bankfull depth; values above 1 put water on the flood plain. Reservoirs and wetlands: fraction of the principal spillway volume. |
| 3 | `sed` | mg/L | Suspended sediment. |
| 4 | `part_n` | mg/L | Organic N. |
| 5 | `part_p` | mg/L | Organic P. |
| 6 | `no3` | mg/L | Nitrate N. |
| 7 | `solp` | mg/L | Soluble mineral P. |
| 8 | `chl_a` | mg/L | Chlorophyll a. |
| 9 | `nh3` | mg/L | Ammonia N. |
| 10 | `no2` | mg/L | Nitrite N. |
| 11 | `cbn_bod` | mg/L | Carbonaceous biochemical oxygen demand. |
| 12 | `dis_ox` | mg/L | Dissolved oxygen. |
| 13 | `sand` | mg/L | Sand. |
| 14 | `silt` | mg/L | Silt. |
| 15 | `clay` | mg/L | Clay. |
| 16 | `sm_ag` | mg/L | Small aggregates. |
| 17 | `l_ag` | mg/L | Large aggregates. |
| 18 | `gvl` | mg/L | Gravel. |
| 19 | `tmp` | °C | Water temperature. |

The header names are those of the SWAT+ Editor; the reader does not use them. All values except `vol` and `tmp` are concentrations: SWAT+ converts them to masses (kg, or tonnes for sediment) with the initial water volume. A reservoir is filled only if it is already built at the start of the run (by its year and month operational); otherwise it starts empty.

If an `org_min` name is not found, the object uses the first record of `om_water.ini`. Projects with channels, reservoirs or wetlands therefore need the file. Aquifers do not use it in 62.0.1: the `org_min` column of [`initial.aqu`](aqu.md) is read but no aquifer value is set from it.

### Example

`refdata/Osu_1hru/om_water.ini`, with the spacing reduced:

```
om_water.ini: added to match initial.cha org_min 'no_init' (channel water init)
name     flo  sed  orgn sedp no3  solp chl_a nh3  no2  cbn_bod dis_ox san  sil  cla  sag  lag  grv  tmp
no_init  0.0  0.0  0.0  0.0  0.0  0.0  0.0   0.0  0.0  0.0     0.0    0.0  0.0  0.0  0.0  0.0  0.0  0.0
```

One record, `no_init`, named by both [`initial.cha`](../input-reference/cha.md#initialcha) and [`initial.res`](../input-reference/res.md#initialres) in that project: channels and wetlands start empty. The header here uses the model's short names (`flo`, `orgn`, `sedp`, ...) instead of the Editor's; only the order matters.

## Related files

- [`landuse.lum`](lum.md): names a `plant.ini` community in its `plnt_com` column.
- [`hru-data.hru`](hru.md): names a `soil_plant.ini` record in its `soil_plant_init` column.
- [`plants.plt`](plt.md): plant parameters for every `plt_name`.
- [`management.sch`](management.md): the schedule in which `rot_yr_ini` picks the starting year.
- [`soils.sol`](sol.md): soil layers, organic carbon and bulk density used with `nutrients.sol`.
- [`codes.bsn`](codes-bsn.md), [`parameters.bsn`](parameters-bsn.md) and [`carbon.bsn`](carbon-bsn.md): carbon model, phosphorus model, `psp` and initial carbon pool fractions.
- [`initial.cha`](cha.md), [`initial.res`](res.md) and [`initial.aqu`](aqu.md): name `om_water.ini` records.
- [Pesticides](pes.md), [pathogens](pth.md), [heavy metals](mtl.md), [salts](salt.md) and [constituents](cs.md): the other initialization files.
- [Nutrient cycling](../model-theory/nutrient-cycling.md) and [carbon](../model-theory/carbon.md).

??? quote "Sources"

    - File names: `type input_init` and `type input_soils` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - `plant.ini`: reader [`readpcom.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readpcom.f90) (called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90)); `type plant_community_db` and `type plant_init_db` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90); use in [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90) and [`pl_root_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_root_gro.f90)
    - `soil_plant.ini`: reader [`soil_plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_plant_init.f90) (called from [`proc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_read.f90)); `type soil_plant_initialize` in [`hru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_module.f90); name matching in [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90)
    - `nutrients.sol`: reader [`solt_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/solt_db_read.f90); `type soiltest_db` in [`soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_data_module.f90); use in [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90) (called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)) with [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90)
    - `om_water.ini`: reader [`om_water_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_water_init.f90); `type hyd_output`, `res_convert_mass` and `hyd_convert_conc_to_mass` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90); name matching in [`sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90), [`res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read.f90), [`wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90), [`aqu_read_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init.f90); use in [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90), [`wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90)
    - Fixed-name salt and constituent files: [`salt_hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_hru_read.f90), [`salt_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_aqu_read.f90), [`salt_cha_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_cha_read.f90), [`cs_hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_hru_read.f90), [`cs_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_aqu_read.f90), [`cs_cha_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_cha_read.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | `plant.ini` `pcom_name`, `plt_cnt`, `rot_yr_ini` | `pcomdb%name`, `%plants_com`, `%rot_yr_ini` |
    | `plt_name`, `lc_status` | `pcomdb%pl%cpnm` (index `%db_num`), `%igro` |
    | `lai_init`, `bm_init`, `phu_init` | `pcomdb%pl%lai`, `%bioms`, `%phuacc` |
    | `plnt_pop`, `yrs_init`, `rsd_init` | `pcomdb%pl%pop`, `%fr_yrmat`, `%rsdin` |
    | `soil_plant.ini` `name`, `sw_frac` | `sol_plt_ini%name`, `%sw_frac` |
    | `nutrients`, `pest`, `path` | `sol_plt_ini%nutc`, `%pestc`, `%pathc` (indices `%nut`, `%pest`, `%path`) |
    | columns 6, 7, 8 | `sol_plt_ini%saltc`, `%hmetc`, `%csc` (indices `%salt`, `%hmet`, `%cs`) |
    | `nutrients.sol` columns 1 to 12 | `solt_db%name`, `%exp_co`, `%lab_p`, `%nitrate`, `%fr_hum_act`, `%hum_c_n`, `%hum_c_p`, `%inorgp`, `%watersol_p`, `%h3a_p`, `%mehlich_p`, `%bray_strong_p` |
    | `om_water.ini` `name` | `om_init_name` |
    | `om_water.ini` columns 2 to 19 | `om_init_water%flo`, `%sed`, `%orgn`, `%sedp`, `%no3`, `%solp`, `%chla`, `%nh3`, `%no2`, `%cbod`, `%dox`, `%san`, `%sil`, `%cla`, `%sag`, `%lag`, `%grv`, `%temp` |

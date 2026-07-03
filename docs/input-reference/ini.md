---
title: Initial conditions (*.ini)
description: General initial conditions for plant communities, soil water, residue, and organic matter.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readpcom.f90
  - src/plant_data_module.f90
  - src/soil_plant_init.f90
  - src/hru_module.f90
  - src/om_water_init.f90
  - src/hydrograph_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The initial-conditions files set the starting state of land and water objects before the first simulation day. The general files are:

- `plant.ini`. Named plant communities. One community is a list of plants with initial LAI, biomass, heat-unit accumulation, plant population, fraction of years to maturity, and residue cover. Land-use entries in `landuse.lum` point at a community name through the `plant_cov` field.
- `soil_plant.ini`. Named soil and plant initial-state records combining a starting soil-water fraction with names of nutrient, pesticide, pathogen, salt, heavy-metal, and constituent initial-condition records. `hru-data.hru` references one row of this file per HRU through `soil_plant_init`.
- `om_water.ini`. Initial organic matter and water properties for water bodies (aquifers, channels, ponds, reservoirs, wetlands). One row per named initialisation record.

The solute-specific initial-condition files (`pest_hru.ini`, `pest_water.ini`, `path_hru.ini`, `path_water.ini`, `hmet_hru.ini`, `hmet_water.ini`, `salt_hru.ini`, `salt_water.ini`, `cs_hru.ini`, `cs_aqu.ini`, `cs_channel.ini`) are declared in the same `type input_init` block but documented on the module pages linked at the bottom.

## Source

Filename strings: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_init`.

| File | Reader | Type populated |
|------|--------|----------------|
| `plant.ini` | [`src/readpcom.f90`](https://github.com/swat-model/swatplus/blob/main/src/readpcom.f90) | `type plant_community_db` (with `type plant_init_db` array) in `src/plant_data_module.f90` |
| `soil_plant.ini` | [`src/soil_plant_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/soil_plant_init.f90) | `type soil_plant_initialize` in `src/hru_module.f90` |
| `om_water.ini` | [`src/om_water_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/om_water_init.f90) | `type hyd_output` in `src/hydrograph_module.f90` |

All three readers skip line 1 (title) and line 2 (header), then read records list-directed. Column positions in the reference examples are cosmetic indentation. If the file is missing or the filename in `file.cio` is `null`, the reader allocates an empty array and continues.

## plant.ini

Each plant community is a header record followed by `plt_cnt` plant records.

### Community record (3 fields)

Read into `pcomdb(icom)`.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "frsd_frsd" | community name. Referenced from `landuse.lum` (`plant_cov`) |
| 2 | plants_com | int | none | 1 | number of plant records that follow |
| 3 | rot_yr_ini | int | none | 1 | starting year in the rotation |

### Plant record (8 fields, repeated `plants_com` times)

Read into `pcomdb(icom)%pl(iplt)` (`type plant_init_db`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | cpnm | char(40) | none | "frsd" | plant name. Must match a row in `plants.plt`. The reader looks the name up in `pldb` and stores the index in `db_num`. If the name is not found a message is written to `9001` (`diagnostics.out`) |
| 2 | igro | char(1) | none | "y" | land cover status. `y` = growing, `n` = not growing |
| 3 | lai | real | m^2/m^2 | 0.0 | initial leaf area index |
| 4 | bioms | real | kg/ha | 0.0 | initial above-ground biomass |
| 5 | phuacc | real | fraction | 0.0 | fraction of plant heat units accumulated at simulation start |
| 6 | pop | real | plants/m^2 | 0.0 | plant population |
| 7 | fr_yrmat | real | fraction | 1.0 | fraction of current year of growth to years to maturity. Used for perennial trees |
| 8 | rsdin | real | kg/ha | 10000.0 | initial surface residue |

### Example

From `refdata/Ames_sub1/plant.ini`. First two communities, indentation trimmed for width:

```
plant.ini:
pcom_name   plt_cnt  rot_yr_ini  plt_name  lc_status  lai_init  bm_init  phu_init  plnt_pop  yrs_init  rsd_init
cosy_comm         2           1
                              corn        n   0.00000      0.00000   0.00000   0.00000   0.00000   10000.00000
                              soyb        n   0.00000      0.00000   0.00000   0.00000   0.00000   10000.00000
corn_comm         1           1
                              corn        n   0.00000      0.00000   0.00000   0.00000   0.00000   10000.00000
```

## soil_plant.ini

One row per initialisation record. Rows are referenced by name from `hru-data.hru` through the `soil_plant_init` field.

The number of fields read depends on `bsn_cc%nam1`. When `nam1 == 0` (the default) the reader reads 7 fields. When `nam1 /= 0` it reads an eighth field (`csc`) for the constituent-side initial-condition record. `nam1` is declared in `basin_module.f90` as "not used", so in practice the 7-field form is what is written.

### Row (7 fields, or 8 with constituents)

Read into `sol_plt_ini(ii)` (`type soil_plant_initialize`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "" | record name. Referenced from `hru-data.hru` |
| 2 | sw_frac | real | fraction | 0.0 | initial soil water content as a fraction of field capacity |
| 3 | nutc | char(40) | none | "" | name of an initial nutrient record (links to soil nutrient initialisation) |
| 4 | pestc | char(40) | none | "" | name of an initial pesticide record. See [`pest_hru.ini`](pes.md) |
| 5 | pathc | char(40) | none | "" | name of an initial pathogen record. See [`path_hru.ini`](pth.md) |
| 6 | saltc | char(40) | none | "" | name of an initial salt record. See [`salt_hru.ini`](salt.md) |
| 7 | hmetc | char(40) | none | "" | name of an initial heavy-metal record. See [`hmet_hru.ini`](mtl.md) |
| 8 | csc | char(40) | none | "" | name of an initial constituent record. Read only when `bsn_cc%nam1 /= 0`. See [`cs_hru.ini`](cs.md) |

Use `null` for any solute-side column that is not active.

### Example

From `refdata/Ames_sub1/soil_plant.ini`:

```
soil_plt_ini
       NAME     SW_FRAC    NUT       PEST   PATH   SALT   HMET
soilplant1         0.5    soilnut1   null   null   null   null
```

## om_water.ini

One row per named record. Rows are referenced by name from the connectivity files of water bodies (aquifers in `aqu_read_init.f90`, channels, reservoirs, ponds, wetlands).

### Row (19 fields)

The reader calls `read (..., om_init_name(ichi), om_init_water(ichi))`. The first field is the name. The remaining 18 fields fill all members of `type hyd_output` in declaration order.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(16) | none | "" | record name |
| 2 | flo | real | m^3 (or fraction for some objects) | 0.0 | water volume |
| 3 | sed | real | metric tons | 0.0 | sediment |
| 4 | orgn | real | kg N | 0.0 | organic N (PART_N in writer header) |
| 5 | sedp | real | kg P | 0.0 | organic P (PART_P) |
| 6 | no3 | real | kg N | 0.0 | NO3-N |
| 7 | solp | real | kg P | 0.0 | mineral soluble P |
| 8 | chla | real | kg | 0.0 | chlorophyll-a |
| 9 | nh3 | real | kg N | 0.0 | NH3 |
| 10 | no2 | real | kg N | 0.0 | NO2 |
| 11 | cbod | real | kg | 0.0 | carbonaceous biological oxygen demand |
| 12 | dox | real | kg | 0.0 | dissolved oxygen |
| 13 | san | real | tons | 0.0 | detached sand |
| 14 | sil | real | tons | 0.0 | detached silt |
| 15 | cla | real | tons | 0.0 | detached clay |
| 16 | sag | real | tons | 0.0 | detached small aggregates |
| 17 | lag | real | tons | 0.0 | detached large aggregates |
| 18 | grv | real | tons | 0.0 | gravel |
| 19 | temp | real | deg C | 0.0 | water temperature |

The `flo` field is interpreted as a fraction of principal storage for reservoirs and ponds, and as an absolute volume for channels. The interpretation is made by the consumer (`cal_allo_init.f90` and related routines), not the reader.

### Example

From `SWATPlusWaterAllocation/documents/wro_test/om_water.ini`:

```
om_wat_ini Generated from ...
       NAME    VOL    SED  PART_N  PART_P    NO3   SOLP  CHL_A    NH3    NO2  CBN_BOD  DIS_OX   SAND   SILT   CLAY  SM_AG   L_AG    GRV    TMP
 aqu_default     1      0       0       0      2      0      0      0      0        0       0      0      0      0      0      0      0     15
 cha_default   0.1   1000      95       0     70      0      0      5      5        0       0      0      0      0      0      0      0     25
pond_default   0.8    100       1     0.1      1   0.03      0    0.1   0.01        0       0      0      0     25      0      0      0     15
 res_default     1    100       1     0.1      1   0.03      0    0.1   0.01        0       0      0      0     25      0      0      0     15
 wet_default   0.5      0       0       0      2      0      0      0      0        0       0      0      0      0      0      0      0     15
```

## Related files

- [`hru-data.hru`](hru.md). Per-HRU pointer into `soil_plant.ini` through `soil_plant_init`.
- [`landuse.lum`](lum.md). Land-use entries point at a `plant.ini` community through `plant_cov`.
- [`plants.plt`](plt.md). Plant parameter database. Every `cpnm` in `plant.ini` must resolve here.
- [`aquifer.aqu`, `initial.aqu`](aqu.md). Aquifers reference `om_water.ini` records for initial storage.
- [`*.res`](res.md), [`*.wet`](wet.md), [`sd_channel`](sd-channel.md). Water bodies reference `om_water.ini` for initial state.
- Solute-side initial conditions: [`pesticide module`](pes.md), [`pathogen module`](pth.md), [`metals module`](mtl.md), [`salt module`](salt.md), [`cs module`](cs.md).

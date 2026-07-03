---
title: soils.sol
description: Soil profile and per-layer physical properties for every soil class in the watershed.
status: review
verified_against:
  - src/soil_db_read.f90
  - src/soil_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`soils.sol` defines every soil class used in the watershed. Each class has a profile header (name, number of layers, hydrologic group, rooting depth, anion exclusion fraction, crack volume, texture string) and one row per soil layer describing depth, bulk density, available water capacity, saturated hydraulic conductivity, organic carbon, particle-size fractions, rock content, albedo, USLE K, electrical conductivity, calcium carbonate, and pH. HRUs reference these classes through `hru-data.hru`. Values feed `soil_phys_init`, `soil_nutcarb_init`, runoff, percolation, erosion, and plant uptake routines.

## Source

- Reader: [`src/soil_db_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/soil_db_read.f90)
- Type definition: [`src/soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/soil_data_module.f90), `type soil_database` (which holds `type soil_profile_db` plus an allocatable array of `type soilayer_db`)

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Each soil is a multi-record block:
  - One profile record with 7 fields.
  - `nly` layer records that follow, each with 14 fields. `nly` is read from the second field of the profile record and used to allocate the layer array.
- Records are list-directed (free format). Column positions in the reference example are cosmetic indentation only; the reader does not depend on them.

### Profile record (7 fields)

Read into `soildb(i)%s` (`type soil_profile_db`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | snam | char(20) | none | blank | soil class name. Referenced from `hru-data.hru` |
| 2 | nly | int | none | 1 | number of soil layers that follow this record |
| 3 | hydgrp | char(16) | none | "A" | hydrologic soil group (A, B, C, or D) |
| 4 | zmx | real | mm | 1500.0 | maximum rooting depth |
| 5 | anion_excl | real | fraction | 0.5 | fraction of porosity from which anions are excluded |
| 6 | crk | real | fraction | 0.01 | crack volume potential of the soil |
| 7 | texture | char(16) | none | blank | texture descriptor string (free-form label) |

### Layer record (14 fields, repeated `nly` times)

Read into `soildb(i)%ly(j)` (`type soilayer_db`) for `j = 1..nly`.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | z | real | mm | 1500.0 | depth from soil surface to the bottom of the layer |
| 2 | bd | real | Mg/m^3 | 1.3 | moist bulk density |
| 3 | awc | real | mm H2O / mm soil | 0.2 | available water capacity |
| 4 | k | real | mm/hr | 10.0 | saturated hydraulic conductivity |
| 5 | cbn | real | % | 2.0 | organic carbon content of the layer |
| 6 | clay | real | % | 10.0 | clay fraction of mineral material |
| 7 | silt | real | % | 60.0 | silt fraction of mineral material |
| 8 | sand | real | % | 30.0 | sand fraction of mineral material |
| 9 | rock | real | % | 0.0 | rock fragment content of the layer |
| 10 | alb | real | none | 0.1 | moist soil albedo |
| 11 | usle_k | real | none | 0.2 | USLE soil erodibility (K) factor |
| 12 | ec | real | dS/m | 0.0 | electrical conductivity |
| 13 | cal | real | % | 0.0 | CaCO3 content |
| 14 | ph | real | none | 0.0 | soil pH |

The reader applies one fix-up after reading: if the first layer is thinner than 20 mm and either the profile has only one layer or the second layer is deeper than 20 mm, the depth of layer 1 is forced to 20 mm.

## Example

Excerpt from `refdata/Ames_sub1/soils.sol`. The first soil class has four layers:

```
soils.sol Ames
   name               NLY  HYD_GRP        ZMX    ANION_EXCL     CRK       TEXTURE        DEPTH        BD       AWC        K        CBN      CLAY      SILT      SAND      ROCK       ALB     USLE_K       EC       CAL        PH
soil_01                 4        B   2000.000        0.500    0.500       L- L- L- L
                                                                                          50.00     1.260     0.210   33.010     1.980    21.000    34.000    45.000     8.000     0.160     0.240     0.000     0.000     5.670
                                                                                         150.00     1.420     0.180   33.010     1.330    21.000    34.000    45.000     8.000     0.160     0.280     0.000     0.000     5.660
                                                                                         840.00     1.500     0.180   33.010     0.750    21.000    34.000    45.000     8.000     0.160     0.320     0.000     0.000     6.600
                                                                                        2000.00     1.600     0.180   33.010     0.250    15.000    36.000    49.000     8.000     0.160     0.370     0.000     0.000     8.000
```

Notes:

- The profile record `soil_01 4 B 2000.000 0.500 0.500 "L- L- L- L"` declares 4 layers. The next four physical lines are the layer records.
- Each layer record has 14 numeric values. The `TEXTURE` token on the profile line (`L- L- L- L` here) is one space-separated token only because the reader reads `texture` as a single character field; the writer pads it with hyphen-separated horizon codes.
- Header tokens in the file (`DEPTH`, `BD`, `AWC`, `K`, `CBN`, `CLAY`, `SILT`, `SAND`, `ROCK`, `ALB`, `USLE_K`, `EC`, `CAL`, `PH`) are read past as a single skipped line. The column order is fixed by the source.

## Related files

- [`hru-data.hru`](../input-reference/hru.md). Each HRU points to a soil class name in `soils.sol`.
- [`nutrients.sol`](../input-reference/sol.md). Soil chemistry initialization paired with a soil class.
- [`plants.plt`](../input-reference/plt.md). Rooting depth in `soils.sol` (`zmx`) caps plant root depth.

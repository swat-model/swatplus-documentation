---
title: "*.aqu (aquifer)"
description: Aquifer property database and initial constituent pointers for shallow and deep aquifer objects.
status: review
verified_against:
  - src/aqu_read.f90
  - src/aqu_read_init.f90
  - src/aquifer_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The aquifer group has two input files declared in `type input_aqu` (`src/input_file_module.f90`):

- `aquifer.aqu` defines one record per aquifer object. Each record sets baseflow recession parameters, initial water table depth, initial chemistry, and the recharge and revap controls used by the lumped (non-gwflow) aquifer module. Records are read into `aqudb` (an array of `type aquifer_database`).
- `initial.aqu` is a small table of named initial-condition pointers. Each entry points to organic-mineral, pesticide, pathogen, heavy-metal, and salt initialization files. The `init` column of each row in `aquifer.aqu` selects one of these names.

## Source

- Readers: [`src/aqu_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/aqu_read.f90), [`src/aqu_read_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/aqu_read_init.f90)
- Type definitions: [`src/aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/aquifer_module.f90), `type aquifer_database` and `type aquifer_init_data_char`
- Filename declarations: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_aqu`

## aquifer.aqu

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per aquifer with list-directed I/O. The first integer on each record is the aquifer id; the reader uses it as the index into `aqudb`. The remaining columns are read into the fields of `type aquifer_database` in declaration order.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | id | int | none | - | aquifer id. Used as the array index into `aqudb` |
| 2 | aqunm | char(16) | none | "" | aquifer name |
| 3 | aqu_ini | char(16) | none | "" | initial-condition pointer. Cross-walks with `name` in `initial.aqu` |
| 4 | flo | real | mm | 0.05 | flow from aquifer in the current time step |
| 5 | dep_bot | real | m | 0.0 | depth from mid-slope surface to bottom of aquifer |
| 6 | dep_wt | real | m | 0.0 | initial depth from mid-slope surface to water table |
| 7 | no3 | real | ppm N | 0.0 | initial nitrate-N concentration in aquifer |
| 8 | minp | real | ppm P | 0.0 | initial mineral phosphorus concentration in aquifer |
| 9 | cbn | real | percent | 0.5 | initial organic carbon in aquifer |
| 10 | flo_dist | real | m | 50.0 | average flow distance to stream or downstream object |
| 11 | bf_max | real | mm | 0.0 | maximum daily baseflow when all channels are contributing |
| 12 | alpha | real | 1/day | 0.0 | lag factor for the groundwater recession curve |
| 13 | revap_co | real | none | 0.0 | revap coefficient. `evap = pet * revap_co` |
| 14 | seep | real | fraction | 0.0 | fraction of recharge that seeps from the aquifer to the deep store |
| 15 | spyld | real | m^3/m^3 | 0.0 | specific yield of the aquifer |
| 16 | hlife_n | real | days | 30.0 | half-life of nitrogen in groundwater |
| 17 | flo_min | real | m | 0.0 | water table depth above which return flow occurs |
| 18 | revap_min | real | m | 0.0 | water table depth above which revap occurs |

### Example

`refdata/Osu_1hru/aquifer.aqu`:

```
aquifer.aqu: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                          init        gw_flo       dep_bot        dep_wt         no3_n         sol_p        carbon      flo_dist        bf_max      alpha_bf         revap       rchg_dp      spec_yld       hl_no3n       flo_min     revap_min  
       1  aqu011                    initaqu1       0.05000      10.00000       6.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.95000       0.02000       0.01000       0.05000       0.00000       5.00000       5.00000  
       2  aqu012                    initaqu1       0.05000      10.00000       6.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.95000       0.02000       0.01000       0.05000       0.00000       5.00000       5.00000  
      21  aqu_deep010               initaqu1       0.00000      10.00000      20.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.91000       0.00000       0.00000       0.03000       0.00000       0.00000       0.00000  
```

Notes:

- The tool header names (`gw_flo`, `no3_n`, `sol_p`, `carbon`, `alpha_bf`, `revap`, `rchg_dp`, `spec_yld`, `hl_no3n`) differ from the source field names (`flo`, `no3`, `minp`, `cbn`, `alpha`, `revap_co`, `seep`, `spyld`, `hlife_n`). Column order is what matters.
- The `init` column points to `initaqu1`, which must exist as a row in `initial.aqu`.
- In this dataset all shallow aquifers share the same property values. The last record (`aqu_deep010`) represents the deep aquifer with no baseflow (`flo = 0`, `flo_min = 0`, `revap_min = 0`).

## initial.aqu

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per initial-condition set with list-directed I/O. Records are read into `aqu_init_dat_c` (an array of `type aquifer_init_data_char`).

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | name | char(16) | initial set name. Cross-walks with `aqu_ini` in `aquifer.aqu` |
| 2 | org_min | char(16) | name of organic-mineral initial-state record |
| 3 | pest | char(16) | name of pesticide initial-state record |
| 4 | path | char(16) | name of pathogen initial-state record |
| 5 | hmet | char(16) | name of heavy-metal initial-state record |
| 6 | salt | char(16) | name of salt initial-state record |

The literal `null` is accepted in slots that have no initial-state file.

### Example

`refdata/Osu_1hru/initial.aqu`:

```
initial.aqu: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description       
initaqu1                   no_init              null              null              null              null  null              
```

Notes:

- The tool writes a trailing `description` column. The source type has no `description` field. List-directed reads consume tokens left to right, so the extra trailing token is harmless. Do not rely on the description being read.
- `no_init` is itself a name that must resolve in the organic-mineral initial file. `null` is treated as "no file".

## Related files

- [`aquifer.con`](../input-reference/con.md). Connectivity entries that map each aquifer id to its spatial location and downstream object.
- `aqu_catunit.ele` and `aqu_catunit.def`. Catchment-unit elements that group aquifers.
- Organic-mineral, pesticide, pathogen, heavy-metal, and salt initial-state files referenced by `initial.aqu`.

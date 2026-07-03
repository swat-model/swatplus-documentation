---
title: "*.res (reservoir)"
description: Reservoir object table and the hydrology, sediment, nutrient, weir, and initial-condition databases it references.
status: review
verified_against:
  - src/res_read.f90
  - src/res_read_hyd.f90
  - src/res_read_sed.f90
  - src/res_read_nut.f90
  - src/res_read_init.f90
  - src/res_read_weir.f90
  - src/reservoir_data_module.f90
  - src/input_file_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The reservoir group has six input files declared in `type input_res` (`src/input_file_module.f90`):

- `reservoir.res` is the object table. One record per reservoir, naming the hydrology, sediment, nutrient, release, and initial-condition records that apply.
- `initial.res` is a table of named initial-condition pointers (organic-mineral, pesticide, pathogen, heavy-metal, salt) shared with the wetland module.
- `hydrology.res` is the hydrology database. One record per named hydrology profile.
- `sediment.res` is the sediment-quality database.
- `nutrients.res` is the nutrient settling and loss-rate database.
- `weir.res` is the weir outflow database for reservoirs that release through a weir.

All five database files are referenced by name from `reservoir.res`. Names are not positional. The reader builds an index after all files are loaded.

## Source

- Readers:
  - [`src/res_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read.f90)
  - [`src/res_read_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read_init.f90)
  - [`src/res_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read_hyd.f90)
  - [`src/res_read_sed.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read_sed.f90)
  - [`src/res_read_nut.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read_nut.f90)
  - [`src/res_read_weir.f90`](https://github.com/swat-model/swatplus/blob/main/src/res_read_weir.f90)
- Type definitions: [`src/reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/reservoir_data_module.f90)
- Filename declarations: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_res`

## reservoir.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per reservoir with list-directed I/O. The first integer on each record is the reservoir id; the reader uses it as the index into `res_dat_c`. The remaining columns are read into `type reservoir_data_char_input` in declaration order.

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | id | int | reservoir id. Used as the array index into `res_dat_c` |
| 2 | name | char(25) | reservoir name |
| 3 | init | char(25) | initial-state pointer. Cross-walks with `init` in `initial.res` |
| 4 | hyd | char(25) | hydrology pointer. Cross-walks with `name` in `hydrology.res` |
| 5 | release | char(25) | release rule pointer. Either a decision-table name in `res_rel.dtl`, or a name prefixed with `ctbl_` for a conditional table |
| 6 | sed | char(25) | sediment pointer. Cross-walks with `name` in `sediment.res` |
| 7 | nut | char(25) | nutrient pointer. Cross-walks with `name` in `nutrients.res` |

The `release` lookup branches on the literal prefix `ctbl_`. If present, the name is matched against `ctbl(:)%name` and the release mode is set to `c`. Otherwise it is matched against `dtbl_res(:)%name` and the release mode is set to `d`.

## initial.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per initial-condition set with list-directed I/O. Records are read into `res_init_dat_c` (an array of `type reservoir_init_data_char`).

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | init | char(25) | initial set name. Cross-walks with `init` in `reservoir.res` (and `wetland.wet`) |
| 2 | org_min | char(25) | name of organic-mineral initial-state record |
| 3 | pest | char(25) | name of pesticide initial-state record |
| 4 | path | char(25) | name of pathogen initial-state record |
| 5 | hmet | char(25) | name of heavy-metal initial-state record |
| 6 | salt | char(25) | name of salt initial-state record |

The literal `null` is accepted in slots that have no initial-state file.

### Example

`refdata/Osu_1hru/initial.res`:

```
initial.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description       
initwet1                   no_init              null              null              null              null  null              
```

The first column header in the example is `name` but the source field is `init` (the value it must match in `reservoir.res`). The source uses position. The editor also writes a trailing `description` column that is not read.

## hydrology.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per hydrology profile with list-directed I/O. Records are read into `res_hyddb` (an array of `type reservoir_hyd_data`) in declaration order.

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(25) | none | "default" | hydrology profile name |
| 2 | iyres | int | none | 0 | simulation year the reservoir becomes operational |
| 3 | mores | int | none | 0 | month the reservoir becomes operational |
| 4 | psa | real | ha | 0.0 | surface area when filled to principal spillway |
| 5 | pvol | real | ha-m | 0.0 | volume needed to fill to principal spillway. Converted to m^3 by `res_initial` |
| 6 | esa | real | ha | 0.0 | surface area when filled to emergency spillway |
| 7 | evol | real | ha-m | 0.0 | volume needed to fill to emergency spillway. Converted to m^3 by `res_initial` |
| 8 | k | real | mm/hr | 0.01 | hydraulic conductivity of the reservoir bottom |
| 9 | evrsv | real | none | 0.7 | lake evaporation coefficient |
| 10 | br1 | real | none | 0.0 | volume-surface area coefficient (estimated by the model if zero) |
| 11 | br2 | real | none | 0.0 | volume-surface area coefficient (estimated by the model if zero) |

The reader fills in defaults when fields are zero or non-positive:

- If `pvol + evol > 0` and `pvol <= 0`, sets `pvol = 0.9 * evol`.
- If both are zero or negative, sets `pvol = 60000.0`.
- If `evol <= 0`, sets `evol = 1.11 * pvol`.
- If `psa <= 0`, sets `psa = 0.08 * pvol`.
- If `esa <= 0`, sets `esa = 1.5 * psa`.
- If `evrsv <= 0`, sets `evrsv = 0.6`.

Note the default for `evrsv` in the type definition is `0.7`, but the runtime default applied when the field is zero or negative is `0.6`.

## sediment.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per sediment profile with list-directed I/O. Records are read into `res_sed` (an array of `type reservoir_sed_data`).

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | name | char(25) | none | sediment profile name |
| 2 | nsed | real | mg/L | normal amount of sediment in the reservoir |
| 3 | d50 | real | um | median particle size of suspended and benthic sediment |
| 4 | carbon | real | percent | organic carbon in suspended and benthic sediment |
| 5 | bd | real | t/m^3 | bulk density of benthic sediment |
| 6 | sed_stlr | real | none | sediment settling rate |
| 7 | velsetlr | real | m/day | sediment settling velocity |

### Example

`refdata/Osu_1hru/sediment.res`:

```
sediment.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   sed_amt           d50        carbon            bd       sed_stl       stl_vel  
sedwet1                  10.00           5.00       0.04            0.8          0.15       0.0002
```

The editor writes `sed_amt`, `sed_stl`, `stl_vel`; the source fields are `nsed`, `sed_stlr`, `velsetlr`. Column order is what matters.

## nutrients.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per nutrient profile with list-directed I/O. Records are read into `res_nut` (an array of `type reservoir_nut_data`). After reading, the reader divides the four `setlr` rates and the two `solr` rates by 365 (m/yr to m/day).

| # | Field | Type | Units (file) | Description |
|---|-------|------|-------|-------------|
| 1 | name | char(25) | none | nutrient profile name |
| 2 | ires1 | int | day of year | start of mid-year settling season |
| 3 | ires2 | int | day of year | end of mid-year settling season |
| 4 | nsetlr1 | real | m/year | nitrogen mass loss rate, mid-year period |
| 5 | nsetlr2 | real | m/year | nitrogen mass loss rate, remainder of year |
| 6 | psetlr1 | real | m/year | phosphorus mass loss rate, mid-year period |
| 7 | psetlr2 | real | m/year | phosphorus mass loss rate, remainder of year |
| 8 | nsolr | real | m/year | loss rate for soluble nitrogen (NO3, NH3, NO2) |
| 9 | psolr | real | m/year | loss rate for soluble phosphorus |
| 10 | theta_n | real | none | temperature adjustment for nitrogen settling |
| 11 | theta_p | real | none | temperature adjustment for phosphorus settling |
| 12 | conc_nmin | real | ppm | minimum nitrogen concentration for settling |
| 13 | conc_pmin | real | ppm | minimum phosphorus concentration for settling |

### Example

`refdata/Osu_1hru/nutrients.res`:

```
nutrients.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name              mid_start   mid_end     mid_n_stl         n_stl     mid_p_stl         p_stl       chla_co     secchi_co       theta_n       theta_p     n_min_stl     p_min_stl  
nutwet1                  5        10       5.50000       5.50000      10.00000      10.00000       1.00000       1.00000       1.00000       1.00000       0.10000       0.01000  
```

Notes:

- Editor headers `mid_n_stl`, `n_stl`, `mid_p_stl`, `p_stl` correspond to source fields `nsetlr1`, `nsetlr2`, `psetlr1`, `psetlr2`.
- Editor headers `chla_co` and `secchi_co` correspond to source fields `nsolr` and `psolr` by position. These are the soluble nitrogen and phosphorus loss rates, not chlorophyll or Secchi-depth coefficients.

## weir.res

Header lines: 2. The reader skips a title line and a column-header line, then reads one record per weir profile with list-directed I/O. Records are read into `res_weir` (an array of `type reservoir_weir_outflow`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | name | char(25) | none | "" | weir profile name |
| 2 | c | real | none | 1.84 | weir discharge linear coefficient |
| 3 | k | real | none | 2.6 | weir discharge exponential coefficient |
| 4 | w | real | m | 2.5 | weir width |
| 5 | h | real | m | 0.0 | height of the weir above the bottom of the impoundment |

### Example

`refdata/Osu_1hru/weir.res`:

```
weir.res: Reservoir weir inputs - asdf;lj
NAME   Linear_C    Exp_K     Width(m)	Depth(m) 
weir1   1.83 	   1.50   	 5.00 		0.0
```

## Related files

- [`reservoir.con`](../input-reference/con.md). Connectivity entries that place each reservoir in the routing topology.
- `res_rel.dtl`. Decision tables referenced from the `release` column of `reservoir.res`.
- [`wetland.wet`](../input-reference/wet.md). Wetlands share the `initial.res` table and the `hydrology.wet`, `sediment.res`, `nutrients.res`, and `weir.res` databases.

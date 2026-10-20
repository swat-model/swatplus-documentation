---
title: pathogens.pth and pathogen initial conditions
description: Pathogen parameter database (pathogens.pth) and initial pathogens in soils, plants, channels, reservoirs and aquifers (path_hru.ini, path_water.ini).
status: review
verified_against:
  - src/path_parm_read.f90
  - src/pathogen_data_module.f90
  - src/path_hru_aqu_read.f90
  - src/path_cha_res_read.f90
  - src/constit_db_read.f90
  - src/constituent_mass_module.f90
  - src/hru_read.f90
  - src/pathogen_init.f90
  - src/sd_hydsed_init.f90
  - src/res_initial.f90
  - src/aqu_read_init_cs.f90
  - src/path_ls_process.f90
  - src/path_ls_runoff.f90
  - src/path_ls_swrouting.f90
  - src/ch_rtpath.f90
  - src/theta.f90
  - src/hru_control.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

SWAT+ can follow pathogens (bacteria and other microorganisms) listed in [`constituents.cs`](cs.md). Three files describe them:

| File | Named in | Content |
|------|----------|---------|
| `pathogens.pth` | `hru_parm_db` line of [`file.cio`](file-cio.md) (default `pathogens.pth`) | Die-off, growth and transport properties of each pathogen. |
| `path_hru.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | Initial pathogens in soils and on plants. |
| `path_water.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | Initial pathogens in channels, reservoirs and aquifers. |

Every pathogen named in [`constituents.cs`](../input-reference/cs.md#constituentscs) should have a row in `pathogens.pth` with the same name.

The pathogen code in 62.0.1 does not yet work as a complete model. Several columns are read but not used, and the landscape and channel routines have the limitations listed in [Behaviour in 62.0.1](#behaviour-in-6201). Read that section before using pathogen results.

## pathogens.pth

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one pathogen with the 18 values below in this order. The reader does not match columns by header name.

| # | Column | Units | Used in 62.0.1 | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | yes | Pathogen name, up to 16 characters. |
| 2 | `do_soln` | 1/day | yes | Die-off factor in soil solution at 20 °C. |
| 3 | `gr_soln` | 1/day | yes | Growth factor in soil solution at 20 °C. |
| 4 | `do_sorb` | 1/day | no | Die-off factor for pathogens sorbed to soil particles at 20 °C. |
| 5 | `gr_sorb` | 1/day | no | Growth factor for pathogens sorbed to soil particles at 20 °C. |
| 6 | `kd` | - | yes | Partition coefficient between solution and sorbed phases. |
| 7 | `t_adj` | - | yes | Temperature adjustment factor for die-off and growth. |
| 8 | `washoff` | fraction | yes | Fraction of the pathogens on foliage washed off by a rainfall event. |
| 9 | `do_plnt` | 1/day | yes | Die-off factor on foliage at 20 °C. |
| 10 | `gr_plnt` | 1/day | yes | Growth factor on foliage at 20 °C. |
| 11 | `fr_manure` | fraction | no | Fraction of manure containing active colony forming units. |
| 12 | `perco` | - | yes | Percolation coefficient: ratio of the concentration in percolate to the concentration in the surface layer solution. |
| 13 | `det_thrshd` | cfu/m² | no | Detection threshold below which soil pathogens would be set to zero. |
| 14 | `do_stream` | 1/day | yes | Die-off factor in streams at 20 °C. |
| 15 | `gr_stream` | 1/day | no | Growth factor in streams at 20 °C. |
| 16 | `do_res` | 1/day | no | Die-off factor in reservoirs at 20 °C. |
| 17 | `gr_res` | 1/day | no | Growth factor in reservoirs at 20 °C. |
| 18 | `conc_min` | cfu/m² | yes | Minimum pathogen level on foliage and in the soil surface layer. |

### Die-off and growth

On foliage and in the top soil layer the pathogen count $N$ changes each day by the net die-off rate, adjusted for the mean air temperature $T$:

$$N_d = N_{d-1}\,\exp\!\left(-(k_{die} - k_{grow})\,\theta^{\,T - 20}\right) - c_{min}$$

where $k_{die}$ and $k_{grow}$ are `do_plnt` and `gr_plnt` on foliage, or `do_soln` and `gr_soln` in the soil, $\theta$ is `t_adj` and $c_{min}$ is `conc_min`. The result is not allowed to fall below `conc_min`.

On a day with at least 2.54 mm of precipitation, `washoff` of the pathogens on each plant's foliage moves to the top soil layer.

## path_hru.ini

Initial pathogens in the soil and on plants of HRUs. An HRU selects a record by name in the `path` column of [`soil_plant.ini`](ini.md).

Line 1 is a title. Each record has a header line, a name line, and then the values as one list: a label, the soil value of each pathogen, then the plant value of each pathogen, in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs). Line breaks within the list are free, but the list must take one line per pathogen so that the records are counted correctly. For two pathogens:

```
path_hru.ini: initial pathogens
name
hru_init
ecoli  1000.  500.
50.  10.
```

Here `ecoli` is the label, the soil values are 1000 and 500 and the plant values 50 and 10.

| Value | Units | Description |
|-------|-------|-------------|
| soil | cfu/m² | Pathogens in the top soil layer. |
| plant | cfu/m² | Pathogens on the foliage. |

## path_water.ini

Initial pathogens in channels, reservoirs and aquifers. Reservoirs and channels select a record by name in their initial condition files ([`initial.res`](res.md), [`initial.cha`](sd-channel.md)), and aquifers in [`initial.aqu`](aqu.md).

Line 1 is a title and line 2 a header. The record has a name line and then the values as one list: a label, the water value of each pathogen, then the bed sediment value of each pathogen. The list must take two lines per pathogen. Use one record (see below).

| Value | Units | Description |
|-------|-------|-------------|
| water | - | Pathogens in the water. The value is used as given, without conversion, so give it in the units of the pathogen loads in the model. |
| benthic | - | Pathogens in the bed sediment, used as given. |

## Behaviour in 62.0.1

- Columns `do_sorb`, `gr_sorb`, `fr_manure`, `det_thrshd`, `gr_stream`, `do_res` and `gr_res` are not used.
- The landscape routines (die-off, wash-off, runoff and percolation) do not look up each pathogen's row by name. They use the row of `pathogens.pth` whose position equals the position of the HRU's record in `path_hru.ini`, and use that one row for every pathogen.
- Each day the runoff step removes all pathogens left in the top soil layer after percolation and reports them as lost in surface runoff, whether or not there is runoff that day.
- Initial soil pathogens from `path_hru.ini` are set to zero again for any soil with more than one layer. Initial plant pathogens are written to the balance output but not put on the foliage.
- `path_water.ini` is read with a header line before each record in the reading pass and without one in the counting pass, so only a file with one record is read correctly.
- Channels take their initial pathogens from the `path_water.ini` record in the position of the channel's pesticide initial record, not its pathogen record. Aquifers take the name match from `path_water.ini` but the values from the `path_hru.ini` soil column of the record in the same position. Reservoirs use their `path_water.ini` record.
- The channel die-off step does not identify the channel being routed, so `do_stream` does not act on the routed water.

## Related files

- [`constituents.cs`](cs.md): the list of pathogens simulated.
- [`soil_plant.ini`](ini.md): links HRUs to `path_hru.ini` records.
- [`initial.cha`](sd-channel.md), [`initial.res`](res.md), [`initial.aqu`](aqu.md): link channels, reservoirs and aquifers to `path_water.ini` records.
- [Pesticides](pes.md) and [heavy metals](mtl.md) use a similar initial condition layout.

??? quote "Sources"

    - Readers: [`path_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_parm_read.f90), [`path_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_hru_aqu_read.f90), [`path_cha_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_cha_res_read.f90)
    - Types: `type pathogen_db` in [`pathogen_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pathogen_data_module.f90); `type cs_soil_init_concentrations` and `type cs_water_init_concentrations` in [`constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constituent_mass_module.f90)
    - Pathogen list crosswalk: [`constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constit_db_read.f90); `soil_plant.ini` link: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90)
    - Initial conditions: [`pathogen_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pathogen_init.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90), [`aqu_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init_cs.f90)
    - Landscape processes: [`path_ls_swrouting.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_swrouting.f90), [`path_ls_runoff.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_runoff.f90), [`path_ls_process.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/path_ls_process.f90), called from [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Channel: [`ch_rtpath.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpath.f90); temperature function: [`theta.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/theta.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `path_db%pathnm` |
    | other pathogens.pth columns | `path_db%` same names |
    | path_hru.ini record | `path_soil_ini%name`, `%soil`, `%plt` |
    | path_water.ini record | `path_init_name`, `path_water_ini%water`, `%benthic` |

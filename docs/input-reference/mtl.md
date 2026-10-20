---
title: metals.mtl and heavy metal initial conditions
description: Heavy metal inputs. The metals.mtl and hmet_water.ini slots in file.cio have no reader in 62.0.1; hmet_hru.ini is read but its values are not used.
status: review
verified_against:
  - src/hmet_hru_aqu_read.f90
  - src/constituent_mass_module.f90
  - src/constit_db_read.f90
  - src/input_file_module.f90
  - src/proc_read.f90
  - src/exco_read_hmet.f90
  - src/dr_read_hmet.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Heavy metals listed in [`constituents.cs`](cs.md) can be routed through the network as loads. In 62.0.1 they enter the model only through export coefficients (`exco_hmet.exc`) and delivery ratios (`dr_hmet.del`) and are routed with the water. There is no metal property database, and soils, plants, channels and reservoirs have no metal processes.

[`file.cio`](../input-reference/file-cio.md) has slots for four metal files:

| File | Named in | Status in 62.0.1 |
|------|----------|------------------|
| `metals.mtl` | `hru_parm_db` line of [`file.cio`](file-cio.md) | No reader. The file is not opened. |
| `hmet_hru.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | Read, but the values are not used. |
| `hmet_water.ini` | `init` line of [`file.cio`](../input-reference/file-cio.md) | No reader. The file is not opened. |
| `exco_hmet.exc`, `dr_hmet.del` | export coefficient and delivery ratio lines of [`file.cio`](../input-reference/file-cio.md) | Read. Metal loads from routing objects. |

Set `metals.mtl`, `hmet_hru.ini` and `hmet_water.ini` to `null` in [`file.cio`](../input-reference/file-cio.md) unless a later revision uses them. The `hmet` columns of [`initial.cha`](cha.md) and [`initial.aqu`](aqu.md) name records of these files and have no effect.

## hmet_hru.ini

Initial heavy metals in the soil and on plants of HRUs. The reader expects this layout:

- Line 1: title.
- For each record: a header line, a name line, then for each metal in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs) two lines, `label soil` and then `label plant`.

The counting pass expects one line per metal instead of two, so files with more than one record are miscounted. The values (soil and plant concentrations in mg/kg) are stored but no part of the model uses them.

## Related files

- [`constituents.cs`](cs.md): the list of metals.
- [`file.cio`](file-cio.md): the file name slots.
- [Pesticides](pes.md) and [pathogens](pth.md): the constituents with full process models.

??? quote "Sources"

    - Reader: [`hmet_hru_aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hmet_hru_aqu_read.f90), called from [`proc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_read.f90)
    - Type: `type cs_soil_init_concentrations` (`hmet_soil_ini`) in [`constituent_mass_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constituent_mass_module.f90)
    - File name slots: `in_parmdb%hmetcom_db`, `in_init%hmet_soil`, `in_init%hmet_water` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)
    - Metal list: [`constit_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/constit_db_read.f90)
    - Metal loads: [`exco_read_hmet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/exco_read_hmet.f90), [`dr_read_hmet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_read_hmet.f90)

    | Item | Fortran variable |
    |------|------------------|
    | hmet_hru.ini record name | `hmet_soil_ini%name` |
    | soil value | `hmet_soil_ini%soil` |
    | plant value | `hmet_soil_ini%plt` |
    | metals.mtl slot | `in_parmdb%hmetcom_db` |

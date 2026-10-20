---
title: Nutrient balance and losses outputs
description: The nutrient balance (`*_nb`) and losses (`*_ls`) output files for HRUs, HRU-lte, landscape units and the basin, with their columns, units and print.prt switches.
status: review
verified_against:
  - src/output_landscape_module.f90
  - src/output_landscape_init.f90
  - src/hru_output.f90
  - src/hru_control.f90
  - src/hru_lte_output.f90
  - src/hru_lte_control.f90
  - src/lsu_output.f90
  - src/basin_output.f90
  - src/lsu_read_elements.f90
  - src/basin_print_codes_read.f90
  - src/nut_pminrl.f90
  - src/nut_nminrl.f90
  - src/nut_nrain.f90
  - src/nut_solp.f90
  - src/pl_nup.f90
  - src/pl_pup.f90
  - src/ero_ysed.f90
  - src/pl_manure.f90
  - src/rsd_decomp.f90
  - src/cbn_zhang2.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Two groups of output files report nutrients on the land:

- The nutrient balance files (`*_nb_*`) give the N and P added to, moved within and removed from the soil and plants: grazing and fertiliser inputs, fixation, atmospheric deposition, mineralisation and other transfers between soil pools, denitrification and plant uptake.
- The losses files (`*_ls_*`) give the sediment and nutrients that leave the land with surface runoff, lateral flow, tile flow and percolation.

All values are amounts per unit area summed over the print interval. Each group has a row in [`print.prt`](../input-reference/print-prt.md) for each scope, with daily, monthly, yearly and average annual flags.

## Files and switches

| Scope | Nutrient balance row | Nutrient balance files | Losses row | Losses files |
|-------|----------------------|------------------------|------------|--------------|
| HRU | `hru_nb` | `hru_nb_{day,mon,yr,aa}.txt` | `hru_ls` | `hru_ls_{day,mon,yr,aa}.txt` |
| HRU-lte | `hru-lte_nb` | none (see below) | `hru-lte_ls` | `hru-lte_ls_{day,mon,yr,aa}.txt` |
| Landscape unit | `lsunit_nb` | `lsunit_nb_{day,mon,yr,aa}.txt` | `lsunit_ls` | `lsunit_ls_{day,mon,yr,aa}.txt` |
| Basin | `basin_nb` | `basin_nb_{day,mon,yr,aa}.txt` | `basin_ls` | `basin_ls_{day,mon,yr,aa}.txt` |

Each file also gets a `.csv` copy when `csvout = y`. Notes on the switches:

- [`print.prt`](../input-reference/print-prt.md) also accepts `hru-lte_nb`, `region_nb` and `region_ls` rows, but 62.0.1 writes no files for them.
- The `hru_nb` row also opens `hru_ncycle_{day,mon,yr,aa}.txt`, a nutrient cycling file with the columns `lab_min_p`, `act_sta_p`, `act_nit_n`, `act_sta_n`, `org_lab_p`, `rsd_hs_c`, `rsd_nitrorg_n` and `rsd_laborg_p`. In 62.0.1 these files contain only their header lines. The same transfers are in the `hru_nb` files.
- Landscape unit files are written only when the model defines landscape units in [`ls_unit.def`](../input-reference/units.md#ls_unitdef).

Line 1 of every file is the project name and version, line 2 the column header and line 3 the units. The first seven columns are `jday`, `mon`, `day`, `yr`, `unit`, `gis_id` and `name`; see [Naming convention](naming-convention.md).

## Nutrient balance columns

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `grzn` | kg N/ha | nitrogen added to the soil in manure from grazing |
| 2 | `grzp` | kg P/ha | phosphorus added to the soil in manure from grazing |
| 3 | `lab_min_p` | kg P/ha | net phosphorus flow from the labile mineral pool to the active mineral pool; negative when the flow goes the other way |
| 4 | `act_sta_p` | kg P/ha | net phosphorus flow from the active mineral pool to the stable mineral pool; negative when the flow goes the other way |
| 5 | `fertn` | kg N/ha | nitrogen applied with fertiliser and manure (mineral and organic) |
| 6 | `fertp` | kg P/ha | phosphorus applied with fertiliser and manure (mineral and organic) |
| 7 | `fixn` | kg N/ha | nitrogen added to plant biomass by fixation |
| 8 | `denit` | kg N/ha | nitrogen lost from the nitrate pool by denitrification |
| 9 | `act_nit_n` | kg N/ha | nitrogen moved from the active organic pool to the nitrate pool (mineralisation) |
| 10 | `act_sta_n` | kg N/ha | nitrogen moved from the active organic pool to the stable organic pool |
| 11 | `org_lab_p` | kg P/ha | phosphorus moved from the organic pool to the labile pool (mineralisation) |
| 12 | `rsd_nitorg_n` | kg N/ha | nitrogen moved from fresh residue to the nitrate (80%) and active organic (20%) pools |
| 13 | `rsd_laborg_p` | kg P/ha | phosphorus moved from fresh residue to the labile (80%) and organic (20%) pools |
| 14 | `no3atmo` | kg N/ha | nitrate added to the soil by atmospheric deposition, wet and dry |
| 15 | `nh4atmo` | kg N/ha | ammonium added to the soil by atmospheric deposition, wet and dry |
| 16 | `nuptake` | kg N/ha | nitrogen taken up by plants |
| 17 | `puptake` | kg P/ha | phosphorus taken up by plants |
| 18 | `gwsoiln` | kg N/ha | nitrate added to the soil from groundwater (gwflow module only) |
| 19 | `gwsoilp` | kg P/ha | phosphorus added to the soil from groundwater (gwflow module only) |

The units line writes `kgha` for every column. The HRU files add `plant_cov` and `mgt_ops` at the end of each row: the plant community and management schedule of the HRU's land use. The landscape unit and basin files have the same two labels in their header but write no values under them.

Columns 9 to 13 (`act_nit_n` to `rsd_laborg_p`) are filled only with the static carbon model, `carbon = 0` in [`codes.bsn`](../input-reference/codes-bsn.md). With `carbon = 2` they stay at zero, and the corresponding flows are in the [carbon outputs](carbon.md). `denit` and the mineral P columns 3 and 4 are filled under both settings.

## Losses columns

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `sedyld` | t/ha | sediment yield leaving the land by water erosion |
| 2 | `sedorgn` | kg N/ha | organic nitrogen attached to sediment in surface runoff |
| 3 | `sedorgp` | kg P/ha | organic phosphorus attached to sediment in surface runoff |
| 4 | `surqno3` | kg N/ha | nitrate in surface runoff |
| 5 | `lat3no3` | kg N/ha | nitrate in lateral flow |
| 6 | `surqsolp` | kg P/ha | soluble phosphorus in surface runoff |
| 7 | `usle` | t/ha | soil loss predicted by the USLE (the units line says `tons`) |
| 8 | `sedminp` | kg P/ha | mineral phosphorus (active and stable) attached to sediment |
| 9 | `tileno3` | kg N/ha | nitrate in tile flow |
| 10 | `lchlabp` | kg P/ha | soluble (labile) phosphorus leached below the soil profile |
| 11 | `tilelabp` | kg P/ha | soluble (labile) phosphorus in tile flow |
| 12 | `satexn` | kg N/ha | nitrate in saturation excess runoff; always 0 in 62.0.1 |

The HRU files add `plant_cov`, `mgt_ops` and `percn` at the end of each row. `percn` (kg N/ha) is the nitrate leached below the soil profile, the same value as `percn` in the [plant and weather files](aquifer-reservoir-plant.md#plant-and-weather). The HRU-lte, landscape unit and basin files have these three labels in their header but write no values under them.

In the HRU-lte files only `sedyld` is calculated; the other columns are always zero.

## Aggregation

Every column is a sum. The monthly and yearly files add up the daily values, and the average annual file divides the run total by the number of printed years. Nothing is averaged over days.

Landscape unit values are the sum of the HRU (and HRU-lte) values, each multiplied by its `RU_FRAC` in [`ls_unit.ele`](../input-reference/units.md#ls_unitele). Basin values are the sum of the HRU and HRU-lte values, each multiplied by its `BSN_FRAC` in [`ls_unit.ele`](../input-reference/units.md#ls_unitele). The fractions are used as given and are not checked: when they do not add up to 1, the basin and landscape unit values are scaled by the same factor. In the `Ames_sub1` reference dataset the `BSN_FRAC` values add up to 2, so its basin values are twice the area-weighted HRU average.

## Example

`hru_nb_yr.txt` and `hru_ls_yr.txt` from a two-year run of the `Ames_sub1` reference dataset with 62.0.1, header, units and first data row:

```
  jday   mon   day    yr    unit  gis_id  name            grzn        grzp        lab_min_p   act_sta_p       fertn            fertp            fixn             denit            act_nit_n        act_sta_n        org_lab_p        rsd_nitorg_n     rsd_laborg_p    no3atmo          nh4atmo          nuptake          puptake          gwsoiln          gwsoilp      plant_cov       mgt_ops
                                                          kgha        kgha        kgha        kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha             kgha
   365    12    31  1975       1       1  hru0001        0.000       0.000     911.096     721.581            0.000            0.000            0.000            0.000            0.000            0.000            0.000            0.000            0.000            0.000            0.000           84.343           29.796            0.000            0.000       cosy_comm       mgt_01
```

```
   jday   mon   day    yr   unit  gis_id  name                      sedyld          sedorgn          sedorgp          surqno3          lat3no3         surqsolp             usle          sedminp          tileno3          lchlabp         tilelabp           satexn    plant_cov       mgt_ops                          percn
                                                                       tha             kgha             kgha             kgha             kgha             kgha             tons             kgha             kgha             kgha             kgha             kgha                                                      kgha
   365    12    31  1975       1       1  hru0001                     0.033            0.172            0.000            0.000            0.002            0.029            6.519            0.013            0.000            0.000            0.000            0.000   cosy_comm       mgt_01                                    0.000
```

This dataset runs the dynamic carbon model (`carbon = 2`), so columns 9 to 13 of the nutrient balance are zero.

## Related files

- [`print.prt`](../input-reference/print-prt.md): output switches.
- [Water balance outputs](water-balance.md): the runoff, lateral flow, tile flow and percolation volumes.
- [Aquifer, reservoir, and plant outputs](aquifer-reservoir-plant.md): plant N and P and leached nitrate.
- [Carbon outputs](carbon.md): soil carbon and the N and P in the carbon pools.
- [Nutrient cycling theory](../model-theory/nutrient-cycling.md).

??? quote "Sources"

    - Column types and headers: `type output_nutbal`, `type output_losses`, `output_nutbal_header`, `output_losses_header` and their units types in [`output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_module.f90)
    - File opening: [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90) (HRU units 2020 to 2037, `hru_ncycle` 3333 to 3340, basin 2060 to 2077, landscape unit 2150 to 2167, HRU-lte losses 2440 to 2447)
    - Writers: [`hru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_output.f90), [`hru_lte_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_output.f90), [`lsu_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_output.f90), [`basin_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_output.f90)
    - Daily values: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`hru_lte_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_control.f90), [`nut_pminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_pminrl.f90), [`nut_nminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nminrl.f90), [`nut_nrain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nrain.f90), [`nut_solp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_solp.f90), [`pl_nup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_nup.f90), [`pl_pup.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_pup.f90), [`ero_ysed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ysed.f90), [`pl_manure.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_manure.f90), [`rsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rsd_decomp.f90), [`cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90)
    - Weights: `BSN_FRAC` and `RU_FRAC` read in [`lsu_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_read_elements.f90)
    - `print.prt` rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)

    | Output column | Fortran variable |
    |---------------|------------------|
    | `grzn`, `grzp` | `hnb_d%grazn`, `hnb_d%grazp` |
    | `lat3no3` | `hls_d%latno3` |
    | `sedminp` | `hls_d%sedminp` = `sedminpa + sedminps` |
    | `sedyld` | `sedyld / hru%area_ha` |
    | `percn` (losses, HRU) | `hpw_d%percn` (`percn_aa` = `hpw_a%percn / yrs_prt` in the `_aa` file) |
    | landscape unit rows | `runb_*`, `ruls_*` built with `lsu_elem%ru_frac` |
    | basin rows | `bnb_*`, `bls_*` built with `lsu_elem%bsn_frac` |

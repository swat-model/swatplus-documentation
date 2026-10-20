---
title: Water balance outputs
description: The hru_wb, hru-lte_wb, lsunit_wb and basin_wb files. Landscape water fluxes and storages in mm, by day, month, year and average annual.
status: review
verified_against:
  - src/output_landscape_module.f90
  - src/output_landscape_init.f90
  - src/hru_control.f90
  - src/sq_surfst.f90
  - src/wetland_control.f90
  - src/hru_output.f90
  - src/hru_lte_output.f90
  - src/lsu_output.f90
  - src/basin_output.f90
  - src/basin_print_codes_read.f90
  - src/time_control.f90
  - src/time_module.f90
  - src/command.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The water balance files report the daily water budget of the land surface: precipitation and snow, evapotranspiration, surface runoff, lateral and tile flow, percolation, soil water and snowpack storage, and where the runoff goes. Every flux is a depth of water in mm over the area of the object, so objects of different size can be compared directly.

Four scopes are written, each switched on by a row in [`print.prt`](../input-reference/print-prt.md):

| [`print.prt`](../input-reference/print-prt.md) row | Files | One row per |
|-----------------|-------|-------------|
| `hru_wb` | `hru_wb_day.txt`, `hru_wb_mon.txt`, `hru_wb_yr.txt`, `hru_wb_aa.txt` | HRU |
| `hru-lte_wb` | `hru-lte_wb_day.txt`, `hru-lte_wb_mon.txt`, `hru-lte_wb_yr.txt`, `hru-lte_wb_aa.txt` | HRU-LTE |
| `lsunit_wb` | `lsunit_wb_day.txt`, `lsunit_wb_mon.txt`, `lsunit_wb_yr.txt`, `lsunit_wb_aa.txt` | landscape unit |
| `basin_wb` | `basin_wb_day.txt`, `basin_wb_mon.txt`, `basin_wb_yr.txt`, `basin_wb_aa.txt` | the whole basin (one row) |

Each `y` in the `daily`, `monthly`, `yearly` or `avann` column of a row opens the matching file. With `csvout` set to `y`, a comma-separated `.csv` copy of each file is written as well.

[`print.prt`](../input-reference/print-prt.md) also accepts a `region_wb` row, but 62.0.1 writes no region files, so the row has no effect. Routing units have no water balance file: the `ru` row writes routing unit hydrographs (`ru_day.txt` and so on; see [Hydrograph outputs](hydrographs.md)).

## Format

- Line 1: the project name from [`file.cio`](../input-reference/file-cio.md) and the SWAT+ version banner.
- Line 2: column headers.
- Line 3: units.
- Lines 4 and on: one row per object per print step.

The first seven columns are the same in every landscape output file:

| # | Column | Description |
|---|--------|-------------|
| 1 | `jday` | Day of the year of the last day in the print step (for example 31 for a January row of a monthly file). |
| 2 | `mon` | Month. |
| 3 | `day` | Day of the month. |
| 4 | `yr` | Calendar year. |
| 5 | `unit` | Sequence number of the object (HRU number, landscape unit number). The basin file always shows 1. |
| 6 | `gis_id` | GIS identifier of the object from its connection file. The basin file always shows 1. |
| 7 | `name` | Object name. The basin file shows the project name. |

The remaining columns, in file order:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 8 | `precip` | mm | Precipitation, rain and snow, before canopy interception. |
| 9 | `snofall` | mm | Precipitation that fell as snow. |
| 10 | `snomlt` | mm | Snowmelt. |
| 11 | `surq_gen` | mm | Surface runoff that leaves the HRU on the day, after the surface runoff lag. |
| 12 | `latq` | mm | Lateral flow out of the soil profile. |
| 13 | `wateryld` | mm | Water yield: `surq_gen` + `latq` + `qtile`. |
| 14 | `perc` | mm | Percolation out of the bottom of the soil profile. |
| 15 | `et` | mm | Actual evapotranspiration: `ecanopy` + `eplant` + `esoil`. |
| 16 | `ecanopy` | mm | Evaporation of water intercepted by the canopy. |
| 17 | `eplant` | mm | Plant transpiration. |
| 18 | `esoil` | mm | Soil evaporation, including evaporation of ponded water. |
| 19 | `surq_cont` | mm | Surface runoff generated on the HRU on the day, before the surface runoff lag. For an HRU with a wetland, this is the wetland outflow. |
| 20 | `cn` | - | Curve number used for the day. |
| 21 | `sw_init` | mm | Soil water content at the start of the print step. |
| 22 | `sw_final` | mm | Soil water content at the end of the print step. |
| 23 | `sw_ave` | mm | Average soil water content over the print step. |
| 24 | `sw_300` | mm | Soil water content of the top 300 mm of soil. |
| 25 | `sno_init` | mm | Snow water content at the start of the print step. |
| 26 | `sno_final` | mm | Snow water content at the end of the print step. |
| 27 | `snopack` | mm | Average snow water content over the print step. |
| 28 | `pet` | mm | Potential evapotranspiration. |
| 29 | `qtile` | mm | Tile drain flow. |
| 30 | `irr` | mm | Irrigation water applied. |
| 31 | `surq_runon` | mm | Surface runoff received from upslope objects. |
| 32 | `latq_runon` | mm | Lateral flow received from upslope objects. |
| 33 | `overbank` | mm | Overbank flood water received from channels. |
| 34 | `surq_cha` | mm | Surface runoff sent to channels. |
| 35 | `surq_res` | mm | Surface runoff sent to reservoirs. |
| 36 | `surq_ls` | mm | Surface runoff sent to other landscape objects. |
| 37 | `latq_cha` | mm | Lateral flow sent to channels. |
| 38 | `latq_res` | mm | Lateral flow sent to reservoirs. |
| 39 | `latq_ls` | mm | Lateral flow sent to other landscape objects. |
| 40 | `gwsoilq` | mm | Groundwater moved into the soil profile when the water table rises into it (gwflow only). |
| 41 | `satex` | mm | Saturation excess flow from a high water table (gwflow only). |
| 42 | `satex_chan` | mm | Saturation excess flow that reaches a channel (gwflow only). |
| 43 | `sw_change` | mm | Change in soil water content over the day. |
| 44 | `lagsurf` | mm | Surface runoff held back by the lag and still on its way to the channel. |
| 45 | `laglatq` | mm | Lateral flow held back by the lag and still on its way to the channel. |
| 46 | `lagsatex` | mm | Saturation excess flow held back by the lag and still on its way to the channel. |
| 47 | `wet_evap` | mm | Evaporation from the wetland water surface. |
| 48 | `wet_oflo` | mm | Wetland outflow (spill). |
| 49 | `wet_stor` | mm | Water stored in the wetland. |
| 50 | `plant_cov` | text | Plant community of the HRU's land use, from [`landuse.lum`](../input-reference/lum.md). |
| 51 | `mgt_ops` | text | Management schedule of the HRU's land use, from [`landuse.lum`](../input-reference/lum.md). |

The columns `surq_cha` to `latq_ls` split the HRU's generated surface runoff and lateral flow by receiving object, using the fractions in the HRU's connection file. They are filled for HRUs only and stay zero in HRU-LTE rows.

### Trailing columns

The header line lists `plant_cov` and `mgt_ops` in every file, but only the `hru_wb` files write them. The other files end after `wet_stor`, except `basin_wb_aa.txt`, which ends with the soft calibration label and the adjustment value: `Original Simulation` and `0.000` when no soft calibration is run. The label is two words, so a tool that splits on spaces finds one more value than the header has names.

## Aggregation

- Daily rows are written for days inside the [`print.prt`](../input-reference/print-prt.md) daily window (`day_start` of `yrc_start` to `day_end` of `yrc_end`), every `interval` days.
- Monthly, yearly and average annual rows start after the `nyskip` warm-up years.
- Fluxes (every column except the storages listed below) are summed over the month or year. The average annual value is the sum over the printed years divided by the number of printed years.
- `cn`, `sw_ave`, `sw_300`, `snopack` and `wet_stor` are averaged over the days in the step. In the average annual file they are averaged over all printed days.
- `sw_init` and `sno_init` give the value at the start of the step, and `sw_final` and `sno_final` the value at the end. In `*_aa.txt`, `sw_final` and `sno_final` are the values on the last day of the simulation.

Landscape unit and basin rows are area-weighted averages of their HRUs and HRU-LTEs, using the area fractions in [`ls_unit.ele`](../input-reference/units.md#ls_unitele).

## Example

The header line of `hru_wb_aa.txt` as 62.0.1 writes it, split here over several lines:

```
 jday   mon   day    yr    unit  gis_id  name            precip     snofall      snomlt    surq_gen
        latq    wateryld        perc          et     ecanopy      eplant       esoil   surq_cont
          cn     sw_init    sw_final      sw_ave      sw_300    sno_init   sno_final     snopack
         pet       qtile         irr  surq_runon  latq_runon    overbank    surq_cha    surq_res
     surq_ls    latq_cha    latq_res     latq_ls     gwsoilq       satex  satex_chan   sw_change
     lagsurf     laglatq    lagsatex    wet_evap    wet_oflo    wet_stor   plant_cov       mgt_ops
```

To check an average annual HRU row, compare `precip` + `irr` + `surq_runon` + `latq_runon` with `et` + `wateryld` + `perc` plus the change in soil water and snow storage. A large gap usually points to wetland storage, gwflow exchange or water held in the runoff lag.

The reference outputs in `refdata/Ames_sub1` of the SWAT+ repository were written by revision 61.0.1, and their header has no `plant_cov` and `mgt_ops` names.

## Related files

- [`print.prt`](../input-reference/print-prt.md): switches each file on or off and sets the print window.
- [Output naming convention](naming-convention.md): every output file and the [`print.prt`](../input-reference/print-prt.md) row that controls it.
- [Channel and sediment outputs](channel-sediment-nutrient.md): where the water leaving the landscape goes next.
- [Post-processing helpers](post-processing.md): reading these files with Python.

??? quote "Sources"

    - File opening and header writes: [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90)
    - Record, header and units types, and the add and average operators: `output_waterbal`, `output_waterbal_header` and `output_waterbal_header_units` in [`output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_module.f90)
    - Daily values: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), with the runoff lag in [`sq_surfst.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_surfst.f90) and wetland outflow in [`wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90)
    - Writers: [`hru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_output.f90), [`hru_lte_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_output.f90), [`lsu_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lsu_output.f90), [`basin_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_output.f90)
    - `print.prt` reader: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)
    - Print window and step flags: [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `surq_gen` | `qday` (after `sq_surfst`) |
    | `wateryld` | `qdr(j)` |
    | `perc` | `sepbtm(j)` |
    | `et` | `etday` |
    | `ecanopy` | `canev` |
    | `eplant` | `ep_day` |
    | `esoil` | `es_day` |
    | `surq_cont` | `surfq(j)` |
    | `cn` | `cnday(j)` |
    | `sw_ave` | `output_waterbal%sw` |
    | `pet` | `pet_day` |
    | `irr` | `irrig(j)%applied` |
    | `surq_runon` | `ls_overq` |
    | `latq_runon` | `latqrunon` |
    | `overbank` | `hru(j)%wet_obank_in` |
    | `gwsoilq` | `output_waterbal%gwsoil`, from `gwsoilq(j)` |
    | `sw_change` | `output_waterbal%delsw` |
    | `lagsurf`, `laglatq`, `lagsatex` | `surf_bs(1,j)`, `bss(1,j)`, `bss_ex(1,j)` |
    | `wet_oflo` | `output_waterbal%wet_out` |
    | `wet_stor` | `wet(j)%flo / (10 * area_ha)` |

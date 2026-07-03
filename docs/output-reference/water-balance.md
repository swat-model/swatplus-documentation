---
title: Water balance outputs
description: The hru_wb, lsunit_wb, basin_wb, and ru_wb files. Columns of the output_waterbal type with units.
status: review
verified_against:
  - src/hru_output.f90
  - src/lsu_output.f90
  - src/basin_output.f90
  - src/output_landscape_module.f90
  - src/output_landscape_init.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

Water balance files report the major flows and storages of the HRU-to-channel hydrology: precipitation, snow, ET, surface runoff, lateral and tile flow, percolation, soil-water storage, and snow pack. One file is written per scope (`hru`, `hru-lte`, `lsunit`, `ru`, `region`, `basin`) per interval (`day`, `mon`, `yr`, `aa`), toggled in `print.prt`.

## Source

- HRU writer: [`src/hru_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_output.f90), units 2000 (day), 2001 (mon), 2002 (yr), 2003 (aa).
- Landscape unit writer: [`src/lsu_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/lsu_output.f90).
- Routing unit writer: [`src/ru_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/ru_output.f90).
- Basin writer: [`src/basin_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_output.f90).
- Region writer: [`src/lsreg_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/lsreg_output.f90).
- File opening and header writes: [`src/output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_init.f90).
- Record type: [`src/output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_module.f90), `type output_waterbal`.

## Format

- Line 1: title (project name, version banner).
- Line 2: column header (`wb_hdr`).
- Line 3: units (`wb_hdr_units`).
- Lines 4+: data records. One record per object (HRU, lsunit, ...) per timestep.

The leading seven columns are the same for every landscape output:

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | jday | int | Julian day of year |
| 2 | mon | int | calendar month |
| 3 | day | int | day of month |
| 4 | yr | int | calendar year |
| 5 | unit | int | spatial id (HRU number, lsunit number, ...) |
| 6 | gis_id | int | GIS id from the object table |
| 7 | name | char | object name (`ob(iob)%name`) |

The remaining columns come from `output_waterbal`, in declaration order. All flows are mm of water depth over the unit area; CN is dimensionless.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 8 | precip | mm | precipitation (rain + snow) |
| 9 | snofall | mm | precipitation falling as snow, sleet, or freezing rain |
| 10 | snomlt | mm | snow or melting ice |
| 11 | surq_gen | mm | surface runoff generated on the landscape |
| 12 | latq | mm | lateral soil flow |
| 13 | wateryld | mm | water yield (surq + latq + tile) |
| 14 | perc | mm | percolation out of soil profile into vadose zone |
| 15 | et | mm | actual evapotranspiration |
| 16 | ecanopy | mm | canopy evaporation (not reported in this column in current source) |
| 17 | eplant | mm | plant transpiration |
| 18 | esoil | mm | soil evaporation |
| 19 | surq_cont | mm | surface runoff leaving the landscape |
| 20 | cn | none | average curve number for the timestep |
| 21 | sw_init | mm | soil water content at start of timestep |
| 22 | sw_final | mm | soil water content at end of timestep |
| 23 | sw_ave | mm | average soil water content over the timestep |
| 24 | sw_300 | mm | final soil water content in upper 300 mm |
| 25 | sno_init | mm | snow water equivalent at start of timestep |
| 26 | sno_final | mm | snow water equivalent at end of timestep |
| 27 | snopack | mm | average snow water equivalent over the timestep |
| 28 | pet | mm | potential evapotranspiration |
| 29 | qtile | mm | subsurface tile flow leaving the landscape |
| 30 | irr | mm | irrigation water applied |
| 31 | surq_runon | mm | surface runoff received from upland landscape |
| 32 | latq_runon | mm | lateral flow received from upland landscape |
| 33 | overbank | mm | overbank flooding from channels |
| 34 | surq_cha | mm | surface runoff flowing into channels |
| 35 | surq_res | mm | surface runoff flowing into reservoirs |
| 36 | surq_ls | mm | surface runoff flowing onto a landscape element |
| 37 | latq_cha | mm | lateral flow into channels |
| 38 | latq_res | mm | lateral flow into reservoirs |
| 39 | latq_ls | mm | lateral flow into a landscape element |
| 40 | gwsoilq | mm | groundwater transferred to soil profile (gwflow) |
| 41 | satex | mm | saturation excess flow developed from high water table (gwflow) |
| 42 | satex_chan | mm | saturation excess flow reaching the main channel (gwflow) |
| 43 | sw_change (delsw) | mm | change in soil water volume |
| 44 | lagsurf | mm | surface runoff in transit to channel |
| 45 | laglatq | mm | lateral flow in transit to channel |
| 46 | lagsatex | mm | saturation excess flow in transit to channel |
| 47 | wet_evap | mm | evaporation from wetland surface |
| 48 | wet_out (wet_oflo) | mm | outflow (spill) from wetland |
| 49 | wet_stor | mm | wetland storage at end of timestep |

The HRU writer also appends two trailing string fields after the numeric columns, written by `hru_output.f90`:

| Trailing | Description |
|----------|-------------|
| plant_cov | name of the plant community from `lum.dtl` |
| mgt_ops | name of the management schedule from `lum.dtl` |

## Aggregation

- Daily (`_day`): values for the day. Files use unit 2000 (HRU), 2050 (basin), 2140 (lsunit).
- Monthly (`_mon`): daily values summed; `sw`, `sno`, and `cn` reset their initial/final markers at month boundaries. Unit 2001 (HRU), 2051 (basin), 2141 (lsunit).
- Yearly (`_yr`): monthly values summed; storage variables divided by 12 where appropriate. Unit 2002 (HRU), 2052 (basin), 2142 (lsunit).
- Annual average (`_aa`): yearly values divided by `time%yrs_prt`. Unit 2003 (HRU), 2053 (basin), 2143 (lsunit).

## Example

`refdata/Ames_sub1/basin_wb_aa.txt`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
  jday   mon   day    yr    unit  gis_id  name                  precip     snofall      snomlt    surq_gen        latq    wateryld        perc          et     ecanopy      eplant       esoil   surq_cont          cn     sw_init    sw_final      sw_ave      sw_300    sno_init   sno_final     snopack         pet       qtile         irr  surq_runon  latq_runon    overbank    surq_cha    surq_res     surq_ls    latq_cha    latq_res     latq_ls     gwsoilq       satex  satex_chan   sw_change     lagsurf     laglatq    lagsatex    wet_evap    wet_oflo    wet_stor
                                                                  mm            mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm         ---          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm          mm
   366    12    31  2020         1       1  demo                1905.214     220.690     219.997      59.541       0.063      59.605       0.003    1846.421       0.000    1004.690     841.731      59.541     131.079      93.191      55.764     103.800      37.446       0.000       0.000       0.910    3464.533       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000      -0.813       0.302       1.796       0.000       0.000       0.000       0.000 Original Simulation                 0.000
```

The 42 numeric columns after `name` map one-to-one onto fields 8 to 49 above. The trailing `Original Simulation` token is the scenario name (basin scope substitutes it for the HRU `plant_cov`/`mgt_ops` pair).

## Related files

- [Naming convention](../output-reference/naming-convention.md).
- [Channel and sediment outputs](../output-reference/channel-sediment-nutrient.md).
- `print.prt`. Toggles each file group on or off.

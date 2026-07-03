---
title: Aquifer, reservoir, and plant outputs
description: Columns for aquifer_*.txt, reservoir_*.txt, crop_yld_*.txt, and the plant and water stress *_pw_*.txt files.
status: review
verified_against:
  - src/aquifer_output.f90
  - src/basin_aquifer_output.f90
  - src/aquifer_module.f90
  - src/reservoir_output.f90
  - src/reservoir_module.f90
  - src/water_body_module.f90
  - src/hydrograph_module.f90
  - src/hru_output.f90
  - src/output_landscape_module.f90
  - src/output_landscape_init.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

This page covers four output families:

- Aquifer storage and fluxes (`aquifer_*.txt`, `basin_aqu_*.txt`).
- Reservoir storage and fluxes (`reservoir_*.txt`, `basin_res_*.txt`).
- Crop yields (`crop_yld_aa.txt`, `crop_yld_yr.txt`, `basin_crop_yld_*.txt`).
- Plant and weather (`hru_pw_*.txt`, `lsunit_pw_*.txt`, `basin_pw_*.txt`).

## Aquifer

### Source

- Writer: [`src/aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/aquifer_output.f90), units 2520 (day), 2521 (mon), 2522 (yr), 2523 (aa).
- Basin sum: [`src/basin_aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_aquifer_output.f90), units 2090-2093.
- File opening: [`src/header_aquifer.f90`](https://github.com/swat-model/swatplus/blob/main/src/header_aquifer.f90), [`src/header_write.f90`](https://github.com/swat-model/swatplus/blob/main/src/header_write.f90).
- Record type: [`src/aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/aquifer_module.f90), `type aquifer_dynamic`.

### Format

Seven leading columns (jday, mon, day, yr, unit, gis_id, name), then the 17 fields of `aquifer_dynamic` in declaration order.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | flo | mm | lateral flow from aquifer |
| 2 | dep_wt | m | average depth from surface elevation to water table |
| 3 | stor | mm | average water storage in aquifer in timestep |
| 4 | rchrg | mm | recharge entering aquifer from other objects |
| 5 | seep | mm | seepage from bottom of aquifer |
| 6 | revap | mm | plant water uptake plus evaporation from aquifer |
| 7 | no3_st | kg/ha N | current total NO3-N mass in aquifer |
| 8 | minp | kg/ha P | mineral P transported in return (lateral) flow |
| 9 | cbn (header label: `orgn`) | percent | organic carbon in aquifer (static). Header mislabels this column. |
| 10 | orgn (header label: `orgp`) | kg/ha N | organic nitrogen in aquifer (static). Header mislabels this column. |
| 11 | no3_rchg | kg/ha N | NO3-N flowing into aquifer from another object |
| 12 | no3_loss | kg/ha | NO3-N loss |
| 13 | no3_lat | kg/ha N | nitrate load to reach in groundwater |
| 14 | no3_seep | kg/ha N | nitrate seepage to next object |
| 15 | flo_cha | mm | aquifer return flow into channels |
| 16 | flo_res | mm | aquifer return flow into reservoirs |
| 17 | flo_ls | mm | aquifer return flow into a landscape element |

### Example header

`refdata/Ames_sub1/basin_aqu_aa.txt`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
   jday   mon   day    yr   unit  gis_id  name                       flo          dep_wt            stor          rchrg           seep          revap         no3_st           minp           orgn           orgp       no3_rchg       no3_loss        no3_lat       no3_seep        flo_cha        flo_res         flo_ls
                                                                       mm              m              mm             mm             mm             mm        kg/ha_N        kg/ha_P        kg/ha_N        kg/ha_P        kg/ha_N        kg/ha_N        kg/ha_N        kg/ha_N             mm             mm             mm
```

The `aqu_header` strings in `aquifer_module.f90` declare columns `orgn` (position 9) and `orgp` (position 10), but the `aquifer_dynamic` type fields in those positions are `cbn` (organic carbon percent) and `orgn` (organic nitrogen). The writer pushes whole records in declaration order, so the column under the header `orgn` is carbon and the column under `orgp` is organic nitrogen.

### Aggregation

- Daily, monthly, yearly, annual average. Aggregation rules: monthly `stor`, `dep_wt`, `no3_st` are divided by the number of days in the month so they remain averages; yearly divides those three by 12; annual average divides everything by `time%yrs_prt`.

## Reservoir

### Source

- Writer: [`src/reservoir_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/reservoir_output.f90), units 2540 (day), 2541 (mon), 2542 (yr), 2543 (aa).
- Basin sum: [`src/basin_reservoir_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_reservoir_output.f90).
- File opening: [`src/header_reservoir.f90`](https://github.com/swat-model/swatplus/blob/main/src/header_reservoir.f90).
- Record types: `type water_body` in [`src/water_body_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/water_body_module.f90), `type hyd_output` in [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90).

### Format

The writer call is:

```fortran
write (2540,100) time%day, time%mo, time%day_mo, time%yrc, j, ob(iob)%gis_id, ob(iob)%name, &
  res_wat_d(j), res(j), res_in_d(j), res_out_d(j)
```

Seven leading columns, then four blocks. Each `hyd_output` block contributes its 18 fields. `res(j)` is the full `reservoir` derived type and contributes the storage fields written into the `_stor` columns.

| Block | Source | Columns |
|-------|--------|---------|
| 1 | `res_wat_d(j)` (`water_body`) | area (ha), precip (m^3), evap (m^3), seep (m^3) |
| 2 | `res(j)` storage as `hyd_output` (`_stor` columns) | 18 storage fields: flo, sed, orgn, sedp, no3, solp, chla, nh3, no2, cbod, dox, san, sil, cla, sag, lag, grv, temp |
| 3 | `res_in_d(j)` (`hyd_output`, `_in` columns) | 18 inflow fields |
| 4 | `res_out_d(j)` (`hyd_output`, `_out` columns) | 18 outflow fields |

See [Channel and sediment outputs](../output-reference/channel-sediment-nutrient.md) for the 18 fields of `hyd_output` and their units; the layout is identical to the sd_channel writer (inflow is `m^3/s`, outflow is `m^3/s`, storage is `m^3`).

### Example header

`refdata/Ames_sub1/basin_res_aa.txt`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
   jday   mon   day    yr     unit   gis_id   name                  area         precip           evap           seep          flo_stor       sed_stor      orgn_stor      sedp_stor       no3_stor      solp_stor      chla_stor       nh3_stor       no2_stor      cbod_stor       dox_stor       san_stor       sil_stor       cla_stor       sag_stor       lag_stor       grv_stor           null         flo_in         sed_in        orgn_in        sedp_in         no3_in        solp_in        chla_in         nh3_in         no2_in        cbod_in         dox_in         san_in         sil_in         cla_in         sag_in         lag_in         grv_in           null        flo_out        sed_out       orgn_out       sedp_out        no3_out       solp_out       chla_out        nh3_out        no2_out       cbod_out        dox_out        san_out        sil_out        cla_out        sag_out        lag_out        grv_out           null
```

The basin-level reservoir output uses `m^3` for the inflow / outflow columns instead of the `m^3/s` used by `basin_sd_cha_aa.txt`, because the reservoir code does not divide by seconds. The header reports `m^3` accordingly.

## Crop yield

### Source

- Writer: bottom block of [`src/hru_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_output.f90), units 4008 (aa) and 4010 (yr). Triggered only at `time%end_sim == 1` (for `_aa`) or `time%end_yr == 1` (for `_yr`).
- Basin variant: `basin_crop_yld_*.txt`, written in the basin output path.
- File opening: [`src/output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_init.f90).

### Format

Different shape from the other output files: each line is one HRU per plant, not one HRU per timestep.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | jday | int | last simulated day |
| 2 | mon | int | last simulated month |
| 3 | day | int | day of month |
| 4 | yr | int | year |
| 5 | unit | int | HRU number |
| 6 | PLANTNM | char | plant name (`pldb(idp)%plantnm`) |
| 7 | MASS | kg/ha | total yield mass (dry weight) |
| 8 | C | kg/ha | carbon in yield |
| 9 | N | kg/ha | nitrogen in yield |
| 10 | P | kg/ha | phosphorus in yield |

`crop_yld_aa.txt` reports the per-harvest average (yield divided by number of harvests). `crop_yld_yr.txt` reports the yield for that year.

### Example

`refdata/Ames_sub1/crop_yld_aa.txt`:

```
 demo
  SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328

                                                                            --YIELD (kg/ha)--
  jday   mon   day    yr    unit PLANTNM                         MASS          C           N           P
   366    12    31  2020       1    corn                                             3358.149    1511.167      33.529       5.295
   366    12    31  2020       1    soyb                                                0.000       0.000       0.000       0.000
```

Switched on in `print.prt` by the `crop_yld` row (`a` for annual average only, `y` for yearly only, `b` for both).

## Plant and weather

### Source

- HRU writer: [`src/hru_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/hru_output.f90), units 2040 (day), 2041 (mon), 2042 (yr), 2043 (aa).
- File opening: [`src/output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_init.f90).
- Record type: [`src/output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/output_landscape_module.f90), `type output_plantweather`.

### Format

Seven leading columns, then the 25 fields of `output_plantweather` in declaration order.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | lai | m^2/m^2 | leaf area index |
| 2 | bioms | kg/ha | total plant biomass |
| 3 | yield | kg/ha | harvested biomass yield (dry weight) |
| 4 | residue | kg/ha | surface residue cover |
| 5 | sol_tmp | deg C | temperature of soil layer 2 |
| 6 | strsw | days | water stress (drought) |
| 7 | strsa | days | excess water stress (aeration) |
| 8 | strstmp | days | temperature stress |
| 9 | strsn | days | nitrogen stress |
| 10 | strsp | days | phosphorus stress |
| 11 | strss | days | salinity stress |
| 12 | nplnt | kg N/ha | plant N uptake |
| 13 | percn | kg N/ha | NO3-N leached past soil profile |
| 14 | pplnt | kg P/ha | plant P uptake |
| 15 | tmx | deg C | maximum air temperature |
| 16 | tmn | deg C | minimum air temperature |
| 17 | tmpav | deg C | average air temperature |
| 18 | solrad | MJ/m^2 | solar radiation |
| 19 | wndspd | m/s | windspeed |
| 20 | rhum | none | relative humidity |
| 21 | phubase0 | deg C/deg C | base-zero potential heat units |
| 22 | lai_max | m^2/m^2 | maximum LAI during timestep |
| 23 | bm_max | kg/ha | maximum total biomass during timestep |
| 24 | bm_grow | kg/ha | total biomass growth during timestep |
| 25 | c_gro | kg/ha | total plant carbon growth during timestep |

The HRU writer appends `plant_cov` and `mgt_ops` as trailing string fields, just like the water-balance writer.

### Aggregation

- Daily values come straight from `hpw_d`.
- Monthly: daily values summed, then divided by days-in-month for the columns that represent averages (`lai`, `tmpav`, etc.), preserving running max for `bm_max` and `lai_max`.
- Yearly: same pattern at year boundary.
- Annual average: divided by `time%yrs_prt` at end of simulation.

## Related files

- [Water balance outputs](../output-reference/water-balance.md).
- [Channel and sediment outputs](../output-reference/channel-sediment-nutrient.md).

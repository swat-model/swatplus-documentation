---
title: Aquifer, reservoir, and plant outputs
description: Columns of the aquifer, reservoir, crop yield, and plant and weather output files, with units and how each column is summed or averaged over the print interval.
status: review
verified_against:
  - src/aquifer_module.f90
  - src/aquifer_output.f90
  - src/basin_aquifer_output.f90
  - src/header_aquifer.f90
  - src/header_write.f90
  - src/aqu_1d_control.f90
  - src/aqu_initial.f90
  - src/reservoir_output.f90
  - src/basin_reservoir_output.f90
  - src/header_reservoir.f90
  - src/water_body_module.f90
  - src/hydrograph_module.f90
  - src/hru_output.f90
  - src/hru_control.f90
  - src/output_landscape_module.f90
  - src/output_landscape_init.f90
  - src/header_yield.f90
  - src/time_control.f90
  - src/basin_print_codes_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

This page covers four groups of output files:

- aquifer storage and fluxes (`aquifer_*.txt`, `basin_aqu_*.txt`)
- reservoir storage and fluxes (`reservoir_*.txt`, `basin_res_*.txt`)
- crop yields (`crop_yld_*.txt`, `basin_crop_yld_*.txt`)
- plant growth, stress and weather (`hru_pw_*.txt`, `hru-lte_pw_*.txt`, `lsunit_pw_*.txt`, `basin_pw_*.txt`)

Each file is switched on in [`print.prt`](../input-reference/print-prt.md). The suffix gives the print interval: `_day`, `_mon`, `_yr` or `_aa` (average annual). When `csvout` is `y`, a `.csv` copy with the same columns is written beside each `.txt` file. The first seven columns of every file except the crop yield files are `jday`, `mon`, `day`, `yr`, `unit`, `gis_id` and `name`; see [Naming convention](naming-convention.md).

## Aquifer

### Files and switches

| File | [`print.prt`](../input-reference/print-prt.md) row | Scope |
|------|-----------------|-------|
| `aquifer_day.txt`, `aquifer_mon.txt`, `aquifer_yr.txt`, `aquifer_aa.txt` | `aquifer` | one row per aquifer per interval |
| `basin_aqu_day.txt`, `basin_aqu_mon.txt`, `basin_aqu_yr.txt`, `basin_aqu_aa.txt` | `basin_aqu` | one row per interval for the whole basin |

The aquifer files report the one-dimensional aquifers defined in [`aquifer.aqu`](../input-reference/aqu.md) and are opened only when the model has such aquifers. When the gwflow module replaces the aquifers, use the [gwflow outputs](gwflow.md) instead.

### Columns

Line 1 is the project name and version, line 2 the column header and line 3 the units. After the seven leading columns come 17 value columns:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `flo` | mm | return flow leaving the aquifer |
| 2 | `dep_wt` | m | depth from the ground surface to the water table |
| 3 | `stor` | mm | water stored in the aquifer |
| 4 | `rchrg` | mm | recharge entering the aquifer from other objects |
| 5 | `seep` | mm | deep seepage from the bottom of the aquifer |
| 6 | `revap` | mm | water removed by plant uptake and evaporation (revap) |
| 7 | `no3_st` | kg N/ha | nitrate-N stored in the aquifer |
| 8 | `minp` | kg P | mineral P sent out with the return flow (see the notes) |
| 9 | `orgn` (header) | % | organic carbon content of the aquifer (see the notes) |
| 10 | `orgp` (header) | kg N/ha | organic N in the aquifer (see the notes) |
| 11 | `no3_rchg` | kg N/ha | nitrate-N entering with recharge; `rchrgn` in earlier documentation |
| 12 | `no3_loss` | kg N/ha | nitrate-N lost in the aquifer (decay); `nloss` in earlier documentation |
| 13 | `no3_lat` | kg N/ha | nitrate-N leaving with the return flow; `no3gw` in earlier documentation |
| 14 | `no3_seep` | kg N/ha | nitrate-N leaving with deep seepage; `seepno3` in earlier documentation |
| 15 | `flo_cha` | mm | part of `flo` routed to channels |
| 16 | `flo_res` | mm | part of `flo` routed to reservoirs |
| 17 | `flo_ls` | mm | part of `flo` routed to other aquifers |

Notes on individual columns:

- Columns 9 and 10 are mislabelled. The header says `orgn` (kg/ha_N) and `orgp` (kg/ha_P), but column 9 is the organic carbon content from the `carbon` column of [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu), constant through the run, and column 10 is organic N, which 62.0.1 never updates, so it stays zero.
- `minp` is the mineral P concentration from the `sol_p` column of [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) multiplied by the day's recharge volume. The value is a mass in kg for the whole aquifer; the units line gives kg/ha_P. It is computed from the recharge volume and leaves the aquifer with the return flow.
- `flo_cha`, `flo_res` and `flo_ls` split `flo` by the outflow fractions in the aquifer's connection file. Only outflows of type `tot` are counted, so the three columns add up to `flo` only when every outflow is of that type.

### Aggregation

Fluxes are summed over the interval. Three state columns are averaged instead: the monthly file divides `stor`, `dep_wt` and `no3_st` by the number of days in the month, and the yearly file divides the sum of the monthly averages by 12. The average annual file divides the yearly values by the number of printed years. Column 9 is never summed: every interval reports the starting value.

The basin file is the area-weighted average of all aquifers, each weighted by its share of the basin area.

### Example header

`basin_aqu_yr.txt` from the `Ames_sub1` reference dataset run with 62.0.1:

```
   jday   mon   day    yr   unit  gis_id  name                       flo          dep_wt            stor          rchrg           seep          revap         no3_st           minp           orgn           orgp       no3_rchg       no3_loss        no3_lat       no3_seep        flo_cha        flo_res         flo_ls
                                                                       mm              m              mm             mm             mm             mm        kg/ha_N        kg/ha_P        kg/ha_N        kg/ha_P        kg/ha_N        kg/ha_N        kg/ha_N        kg/ha_N             mm             mm             mm
```

## Reservoir

### Files and switches

| File | [`print.prt`](../input-reference/print-prt.md) row | Scope |
|------|-----------------|-------|
| `reservoir_day.txt`, `reservoir_mon.txt`, `reservoir_yr.txt`, `reservoir_aa.txt` | `reservoir` | one row per reservoir per interval |
| `basin_res_day.txt`, `basin_res_mon.txt`, `basin_res_yr.txt`, `basin_res_aa.txt` | `basin_res` | all reservoirs added together |

The reservoir files are opened only when the model has reservoirs.

### Columns

After the seven leading columns come four blocks: 4 water body columns, then 18 storage, 18 inflow and 18 outflow columns.

| Block | Columns | Units |
|-------|---------|-------|
| Water body | `area`, `precip`, `evap`, `seep` | ha, m³, m³, m³ |
| Storage at the end of the interval | `flo_stor`, `sed_stor`, `orgn_stor`, `sedp_stor`, `no3_stor`, `solp_stor`, `chla_stor`, `nh3_stor`, `no2_stor`, `cbod_stor`, `dox_stor`, `san_stor`, `sil_stor`, `cla_stor`, `sag_stor`, `lag_stor`, `grv_stor`, `null` | see below |
| Inflow during the interval | the same 18 names ending in `_in` | see below |
| Outflow during the interval | the same 18 names ending in `_out` | see below |

Units of the 18 constituent columns, which repeat in the storage, inflow and outflow blocks:

| Constituent | Units | Description |
|-------------|-------|-------------|
| `flo` | m³ | water volume |
| `sed` | t | sediment |
| `orgn` | kg N | organic N |
| `sedp` | kg P | organic (sediment-attached) P |
| `no3` | kg N | nitrate-N |
| `solp` | kg P | soluble mineral P |
| `chla` | kg | chlorophyll-a |
| `nh3` | kg N | ammonium-N |
| `no2` | kg N | nitrite-N |
| `cbod` | kg | carbonaceous biochemical oxygen demand |
| `dox` | kg | dissolved oxygen |
| `san`, `sil`, `cla`, `sag`, `lag`, `grv` | t | sand, silt, clay, small aggregates, large aggregates and gravel |
| `null` | °C | water temperature (the header gives `null` and no unit) |

The inflow columns are `flo_in`, `sed_in`, `orgn_in`, `sedp_in`, `no3_in`, `solp_in`, `chla_in`, `nh3_in`, `no2_in`, `cbod_in`, `dox_in`, `san_in`, `sil_in`, `cla_in`, `sag_in`, `lag_in`, `grv_in` and `null`. The outflow columns are `flo_out`, `sed_out`, `orgn_out`, `sedp_out`, `no3_out`, `solp_out`, `chla_out`, `nh3_out`, `no2_out`, `cbod_out`, `dox_out`, `san_out`, `sil_out`, `cla_out`, `sag_out`, `lag_out`, `grv_out` and `null` (the last column of each block is headed `null`).

Inflow and outflow are volumes and masses for the interval, in m³, t and kg. The storage block is the reservoir content when the line is written, so in the monthly, yearly and average annual files it is the storage on the last day of the interval.

### Aggregation

Inflow, outflow, precipitation, evaporation and seepage are summed over the interval, and the average annual file divides the totals by the number of printed years. The surface `area` is averaged over the days of the month, and the yearly value is the average of the monthly values.

`reservoir_mon.csv` has one extra line after the units line, `RES  reservoir_mon.csv`, which the other reservoir files do not have.

## Crop yield

### Files and switches

The `crop_yld` column of [`print.prt`](../input-reference/print-prt.md) controls all crop yield files: `y` gives yearly files, `a` average annual files, `b` both, and `n` none.

| File | Written when `crop_yld` is | Content |
|------|----------------------------|---------|
| `crop_yld_aa.txt` | `a` or `b` | one row per HRU and plant at the end of the run |
| `crop_yld_yr.txt` | `y` or `b` | header lines only (see below) |
| `basin_crop_yld_yr.txt` | `y` or `b` | one row per plant per year for the whole basin |
| `basin_crop_yld_aa.txt` | `y` or `b` | one row per plant at the end of the run |

With `crop_yld = a`, only `crop_yld_aa.txt` is produced; the basin files need `y` or `b`. In 62.0.1 no data rows are written to `crop_yld_yr.txt` (or its `.csv`). For yearly yields use `basin_crop_yld_yr.txt`, or `yield.out` (switched on by `mgtout`) for every harvest.

### HRU columns

`crop_yld_aa.txt` has a title line, a line `--YIELD (kg/ha)--`, the column header, and one row per plant in each HRU:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `jday` | - | day of year of the last simulated day |
| 2 | `mon` | - | month |
| 3 | `day` | - | day of month |
| 4 | `yr` | - | year |
| 5 | `unit` | - | HRU number |
| 6 | `PLANTNM` | - | plant name from [`plants.plt`](../input-reference/plt.md) |
| 7 | `MASS` | kg/ha | dry mass of the harvested yield |
| 8 | `C` | kg/ha | carbon in the yield |
| 9 | `N` | kg/ha | nitrogen in the yield |
| 10 | `P` | kg/ha | phosphorus in the yield |

The values are the total yield over the whole run divided by the number of harvests of that plant, that is, the average yield per harvest. A plant that was never harvested reports zero. The `.csv` header lists a single `yield` column, while each data row contains the four values `MASS`, `C`, `N` and `P`.

### Basin columns

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `year` | - | calendar year (the last year in the `_aa` file) |
| 2 | `plant_no` | - | plant number in the basin plant list |
| 3 | `plant_name` | - | plant name |
| 4 | `harv_area(ha)` | ha | area harvested; an HRU harvested twice in a year counts twice |
| 5 | `yld(t)` | t | total dry yield |
| 6 | `yld(t/ha)` | t/ha | `yld(t)` divided by `harv_area(ha)` |

The yearly file skips the years before `nyskip`. In the average annual file, area and yield are divided by the number of printed years, and `yld(t/ha)` is total yield divided by total harvested area.

### Example

`crop_yld_aa.txt` and `basin_crop_yld_aa.txt` from a two-year run of the `Ames_sub1` reference dataset with 62.0.1:

```
                                                                            --YIELD (kg/ha)--
  jday   mon   day    yr    unit PLANTNM                         MASS          C           N           P
   366    12    31  1976       1    corn                                             3692.158    1661.471      36.748       5.907
   366    12    31  1976       1    soyb                                                0.000       0.000       0.000       0.000
```

```
       year      plant_no   plant_name       harv_area(ha)     yld(t)          yld(t/ha)
        1976           1 corn                                       12.04350       47.48362       3.942675
        1976           2 soyb                                      0.0000000E+00  0.0000000E+00  0.0000000E+00
```

## Plant and weather

### Files and switches

| File | [`print.prt`](../input-reference/print-prt.md) row | Scope |
|------|-----------------|-------|
| `hru_pw_day.txt` to `hru_pw_aa.txt` | `hru_pw` | one row per HRU |
| `hru-lte_pw_day.txt` to `hru-lte_pw_aa.txt` | `hru-lte_pw` | one row per HRU-lte |
| `lsunit_pw_day.txt` to `lsunit_pw_aa.txt` | `lsunit_pw` | one row per landscape unit |
| `basin_pw_day.txt` to `basin_pw_aa.txt` | `basin_pw` | whole basin |

All use the columns below. The HRU files add `plant_cov` and `mgt_ops` at the end of each row: the plant community and the management schedule of the HRU's land use.

### Columns

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `lai` | m²/m² | leaf area index |
| 2 | `bioms` | kg/ha | total plant biomass |
| 3 | `yield` | kg/ha | harvested yield (dry mass) |
| 4 | `residue` | kg/ha | surface residue |
| 5 | `sol_tmp` | °C | temperature of soil layer 2 |
| 6 | `strsw` | days | water (drought) stress days |
| 7 | `strsa` | days | aeration (excess water) stress days |
| 8 | `strstmp` | days | temperature stress days |
| 9 | `strsn` | days | nitrogen stress days |
| 10 | `strsp` | days | phosphorus stress days |
| 11 | `strss` | days | salinity stress days |
| 12 | `nplt` | kg N/ha | nitrogen in the plant biomass |
| 13 | `percn` | kg N/ha | nitrate-N leached below the soil profile |
| 14 | `pplnt` | kg P/ha | phosphorus in the plant biomass |
| 15 | `tmx` | °C | maximum air temperature |
| 16 | `tmn` | °C | minimum air temperature |
| 17 | `tmpav` | °C | mean air temperature |
| 18 | `solarad` | MJ/m² | solar radiation |
| 19 | `wndspd` | m/s | wind speed |
| 20 | `rhum` | fraction | relative humidity |
| 21 | `phubas0` | °C | accumulated base-zero heat units |
| 22 | `lai_max` | m²/m² | maximum leaf area index (always 0 in 62.0.1) |
| 23 | `bm_max` | kg/ha | maximum total biomass during the interval |
| 24 | `bm_grow` | kg/ha | biomass growth |
| 25 | `c_gro` | kg C/ha | plant carbon growth |

The units line writes `kgha` for columns 2 to 4 and 12 to 14 and `----` for the stress columns.

### Aggregation

| Columns | Monthly | Yearly | Average annual |
|---------|---------|--------|----------------|
| `yield`, stress days, `percn` | sum | sum | yearly sum averaged over the printed years |
| `nplt`, `pplnt` | plant N and P at the end of the month | at the end of the year | at the end of the run |
| `bm_max` | maximum in the month | maximum in the year | maximum in the run |
| all other columns | daily average | daily average | daily average |

`nplt` and `pplnt` are the N and P contents of the standing plants. They do not report uptake during the interval. After a harvest or kill they drop to zero, so yearly and average annual values are often zero for annual crops.

### Example

`hru_pw_mon.txt`, `Ames_sub1` run with 62.0.1 (header, units and first data row):

```
   jday   mon   day    yr   unit  gis_id  name                     lai       bioms       yield     residue     sol_tmp       strsw       strsa     strstmp       strsn       strsp       strss        nplt       percn       pplnt         tmx         tmn       tmpav     solarad      wndspd        rhum     phubas0     lai_max      bm_max     bm_grow       c_gro   plant_cov       mgt_ops
                                                             m**2/m**2        kgha        kgha        kgha        degc        ----        ----        ----        ----        ----        ----        kgha        kgha        kgha        degc        degc        degc      mj/m^2         m/s        frac        degc   m**2/m**2       kg/ha       kg/ha       kg/ha
    31     1    31  1975       1       1  hru0001                0.000       0.000       0.000   17278.244      -0.192       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       0.000       5.747      -8.777      -1.515      10.390       5.431       0.653       0.004       0.000       0.000       0.000       0.000   cosy_comm       mgt_01
```

## Related files

- [`print.prt`](../input-reference/print-prt.md): switches for every file on this page.
- [`aquifer.aqu`](../input-reference/aqu.md) and [`reservoir.res`](../input-reference/res.md): the objects reported here.
- [Water balance outputs](water-balance.md) and [Channel and sediment outputs](channel-sediment-nutrient.md).
- [gwflow outputs](gwflow.md): groundwater output when gwflow replaces the aquifers.

??? quote "Sources"

    - Aquifer: [`aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aquifer_output.f90) (units 2520 to 2527), [`basin_aquifer_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_aquifer_output.f90) (units 2090 to 2097), headers and arithmetic in [`aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aquifer_module.f90), file opening in [`header_aquifer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_aquifer.f90) and [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90), values set in [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90) and [`aqu_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_initial.f90)
    - Reservoir: [`reservoir_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_output.f90) (units 2540 to 2547), [`basin_reservoir_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_reservoir_output.f90), [`header_reservoir.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_reservoir.f90), water body type in [`water_body_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_body_module.f90), constituent headers in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Crop yield: [`hru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_output.f90) (unit 4008), file opening in [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90) (units 4008 to 4011) and [`header_yield.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_yield.f90), basin rows in [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90) (units 5100 and 5101)
    - Plant and weather: [`hru_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_output.f90) (units 2040 to 2047), daily values in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), type, header and operators in [`output_landscape_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_module.f90)
    - `print.prt` rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)

    | Output column | Fortran variable |
    |---------------|------------------|
    | aquifer column 9 (`orgn` in the header) | `aqu_d%cbn` (from `aqu_dat%cbn`) |
    | aquifer column 10 (`orgp` in the header) | `aqu_d%orgn` |
    | aquifer `minp` | `aqu_d%minp` |
    | reservoir water body block | `res_wat_d` (`type water_body`) |
    | reservoir storage block | `res(j)` (`type hyd_output`) |
    | reservoir inflow and outflow blocks | `res_in_d`, `res_out_d` |
    | `crop_yld_aa` `MASS`, `C`, `N`, `P` | `pl_mass%yield_tot(ipl)` divided by `pcom%plcur(ipl)%harv_num` |
    | plant and weather `nplt`, `pplnt` | `hpw_d%nplnt`, `hpw_d%pplnt`, both copied from `pl_mass%tot_com` |
    | plant and weather `solarad`, `phubas0` | `hpw_d%solrad`, `hpw_d%phubase0` |

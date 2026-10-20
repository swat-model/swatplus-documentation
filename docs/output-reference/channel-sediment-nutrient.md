---
title: Channel and sediment outputs
description: Channel flow, sediment and nutrient files (channel_sd, channel_sdmorph, sd_chanbud), the sediment budget files new in 62.0.1 (ch_sedbud, chanbud_order, sedbud), their basin sums, and the legacy channel files.
status: review
verified_against:
  - src/header_sd_channel.f90
  - src/header_write.f90
  - src/header_channel.f90
  - src/sd_channel_output.f90
  - src/sd_chanmorph_output.f90
  - src/sd_chanbud_output.f90
  - src/ch_sedbud_output.f90
  - src/chord_sedbud_output.f90
  - src/basin_sedbud_output.f90
  - src/basin_sdchannel_output.f90
  - src/basin_chanmorph_output.f90
  - src/basin_chanbud_output.f90
  - src/basin_channel_output.f90
  - src/channel_output.f90
  - src/sd_channel_module.f90
  - src/hydrograph_module.f90
  - src/water_body_module.f90
  - src/channel_module.f90
  - src/basin_module.f90
  - src/sd_channel_control3.f90
  - src/sd_channel_sediment3.f90
  - src/ch_temp.f90
  - src/hru_control.f90
  - src/res_control.f90
  - src/wetland_control.f90
  - src/command.f90
  - src/time_control.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

These files report what happens in the channel network: flow, sediment and nutrients entering, leaving and stored in each channel, channel geometry and erosion, and sediment budgets for each channel, each stream order and the whole basin.

SWAT+ routes channels defined in the channel files of the SWAT+ Editor (see [Channels](../input-reference/cha.md) and [channel-lte](../input-reference/sd-channel.md)). Two rows of [`print.prt`](../input-reference/print-prt.md) control all of the channel files:

| [`print.prt`](../input-reference/print-prt.md) row | Files opened |
|-----------------|--------------|
| `channel_sd` | `channel_sd_*`, `channel_sdmorph_*`, `sd_chanbud_*`, and the sediment budget files `ch_sedbud_*`, `chanbud_order_*` and `sedbud_*`. With a sub-daily time step and `daily` set to `y`, also `channel_sd_subday.txt`. |
| `basin_sd_cha` | `basin_sd_cha_*`, `basin_sd_chamorph_*`, `basin_sd_chanbud_*` |

Each `y` in the `daily`, `monthly`, `yearly` or `avann` column of a row opens the matching file. Most files use the suffixes `_day`, `_mon`, `_yr` and `_aa`. The `ch_sedbud` and `chanbud_order` files use `_d`, `_m`, `_y` and `_a`. With `csvout` set to `y`, a `.csv` copy of each file is written as well.

The channel files are opened only when the project has at least one channel, except `sd_chanbud_*`, which is opened whenever its switch is on.

The `channel` and `basin_cha` rows open the legacy channel files described at the end of this page.

## Files at a glance

| File | One row per | Content |
|------|-------------|---------|
| `channel_sd_*` | channel | Water surface, storage, inflow and outflow of water, sediment and nutrients, and stream temperature. |
| `channel_sdmorph_*` | channel | Flow rates, sediment transport and erosion, and channel width, depth and slope. |
| `sd_chanbud_*` | channel | Sediment and nutrient budget: inflow, outflow, deposition and erosion. |
| `ch_sedbud_*` | channel | Bank and bed erosion, floodplain deposition, channel size. |
| `chanbud_order_*` | stream order (1 to 12) | The `ch_sedbud` values summed over all channels of each stream order. |
| `sedbud_*` | basin (one row) | Basin sediment budget: upland yield, bank and bed erosion, floodplain, reservoir and wetland deposition. |
| `basin_sd_cha_*` | basin | `channel_sd` summed over all channels. |
| `basin_sd_chamorph_*` | basin | `channel_sdmorph` summed over all channels. |
| `basin_sd_chanbud_*` | basin | `sd_chanbud` summed over all channels. |
| `channel_sd_subday.txt` | channel and time step | Outflow for each sub-daily time step. |

## Leading columns

Files with one row per channel start with seven columns:

| # | Column | Description |
|---|--------|-------------|
| 1 | `jday` | Day of the year of the last day in the print step. |
| 2 | `mon` | Month. |
| 3 | `day` | Day of the month. |
| 4 | `yr` | Calendar year. |
| 5 | `unit` | Channel number. |
| 6 | `gis_id` | GIS identifier of the channel. |
| 7 | `name` | Channel name. |

The basin files have the same seven columns with `unit` and `gis_id` set to 1 and the project name in `name`. In `ch_sedbud_*` the same three columns are labelled `ichan`, `ob` and `name`. `chanbud_order_*` has `iord` (the stream order) in place of all three, and `sedbud_*` has only the four date columns.

## channel_sd files

After the leading columns come four values for the water surface, then three blocks of 18 values (storage, inflow, outflow) and a final stream temperature.

| Column | Units | Description |
|--------|-------|-------------|
| `area` | ha | Water surface area of the channel. |
| `precip` | m³ | Precipitation falling on the water surface. |
| `evap` | m³ | Evaporation from the water surface. |
| `seep` | m³ | Seepage through the channel bed. |

Each block has the same 18 quantities. The column names end in `_stor`, `_in` or `_out`:

| Quantity | Storage units | Inflow and outflow units | Description |
|----------|---------------|--------------------------|-------------|
| `flo` | m³ | m³/s | Water: volume stored, or average flow rate. |
| `sed` | tons | tons | Sediment. |
| `orgn` | kg N | kg N | Organic nitrogen. |
| `sedp` | kg P | kg P | Organic (sediment-attached) phosphorus. |
| `no3` | kg N | kg N | Nitrate. |
| `solp` | kg P | kg P | Soluble mineral phosphorus. |
| `chla` | kg | kg | Chlorophyll a. |
| `nh3` | kg N | kg N | Ammonium. |
| `no2` | kg N | kg N | Nitrite. |
| `cbod` | kg | kg | Carbonaceous biochemical oxygen demand. |
| `dox` | kg | kg | Dissolved oxygen. |
| `san` | tons | tons | Sand. |
| `sil` | tons | tons | Silt. |
| `cla` | tons | tons | Clay. |
| `sag` | tons | tons | Small aggregates. |
| `lag` | tons | tons | Large aggregates. |
| `grv` | tons | tons | Gravel. |
| `null` | °C | °C | Water temperature. |

The 18th column of each block is headed `null` and has no unit in the units row. It is the water temperature of the stored water, the inflow and the outflow. The outflow temperature is the stream temperature from the heat balance calculation.

The last column, `water_temp` (°C), is not the heat balance temperature. It is $5 + 0.75\,\bar{T}$, where $\bar{T}$ is the mean air temperature of the day at the weather station of the channel that was routed last. All channels therefore show the same value for a given day. Use the `null` column of the outflow block for the stream temperature of each channel.

### Aggregation

- The storage block is the storage at the end of the print step, also in the monthly, yearly and average annual files.
- Inflow and outflow rates (`flo_in`, `flo_out`) are averaged over the days of the step. All other inflow and outflow quantities are totals for the step; the average annual file gives the average yearly total.
- Water temperatures in the inflow and outflow blocks are flow-weighted averages.
- `precip`, `evap` and `seep` are totals for the step. `area` is the average daily area in the monthly and yearly files.

## channel_sdmorph files

| Column | Units | Description |
|--------|-------|-------------|
| `flo_in` | m³/s | Inflow rate. |
| `geo_bf` | m³/s | Base flow from the geomorphic aquifer method. |
| `flo_out` | m³/s | Outflow rate. |
| `peakr` | m³/s | Peak flow rate. |
| `sed_in` | tons | Sediment entering the channel. |
| `sed_out` | tons | Sediment leaving the channel. |
| `washld` | tons | Wash load (suspended sediment) leaving the channel. |
| `bedld` | tons | Sediment deposited in the channel. |
| `dep` | tons | Sediment deposited on the floodplain. |
| `deg_btm` | tons | Bed erosion. |
| `deg_bank` | tons | Bank erosion. |
| `hc_sed` | tons | Sediment from gully headcut erosion. |
| `width` | m | Bankfull top width at the end of the step. |
| `depth` | m | Bankfull depth at the end of the step. |
| `slope` | m/m | Channel slope at the end of the step. |
| `deg_btm` | m | Bed downcutting. |
| `deg_bank` | m | Bank widening. |
| `hc_len` | m | Headcut retreat. |
| `flo_in_mm` | mm | Inflow as a depth over the channel's drainage area. |
| `aqu_in_mm` | mm | Geomorphic base flow as a depth over the drainage area. |
| `flo_out_mm` | mm | Outflow as a depth over the drainage area. |
| `sed_stor` | tons | Sediment stored in the channel. |
| `n_tot` | kg N | Total nitrogen leaving the channel (organic N, nitrate, ammonium and nitrite). |
| `p_tot` | kg P | Total phosphorus leaving the channel (organic and soluble P). |
| `dep_bf` | m | Flow depth at bankfull. |
| `velav_bf` | m/s | Average velocity at bankfull. |

`deg_btm` and `deg_bank` each appear twice, first in tons and then in m; read them by position. The units row labels `n_tot` as kg_N, `p_tot` as kg_P and `dep_bf` as m/s; `dep_bf` is a depth in m.

In the monthly and yearly files, the flow rates, `sed_stor`, `n_tot`, `p_tot`, `dep_bf` and `velav_bf` are daily averages; the tons, mm and m erosion columns are totals; and `width`, `depth` and `slope` are the values at the end of the step. The average annual file gives daily averages for the first group and average yearly totals for the second.

## sd_chanbud files

| Column | Description |
|--------|-------------|
| `in_sed`, `out_sed` | Sediment entering and leaving the channel. |
| `fp_dep` | Sediment deposited on the floodplain. |
| `ch_dep` | Sediment deposited in the channel. |
| `bank_ero` | Bank erosion. |
| `bed_ero` | Bed erosion. |
| `in_no3`, `in_orgn`, `out_no3`, `out_orgn` | Nitrate and organic nitrogen entering and leaving. |
| `fp_no3` | Nitrate lost on the floodplain. |
| `bank_no3`, `bed_no3` | Nitrate gained from bank and bed erosion. |
| `fp_orgn`, `ch_orgn` | Organic nitrogen deposited on the floodplain and in the channel. |
| `bank_orgn`, `bed_orgn` | Organic nitrogen gained from bank and bed erosion. |
| `in_solp`, `in_orgp`, `out_solp`, `out_orgp` | Soluble and organic phosphorus entering and leaving. |
| `fp_solp` | Soluble phosphorus lost on the floodplain. |
| `bank_solp`, `bed_solp` | Soluble phosphorus gained from bank and bed erosion. |
| `fp_orgp`, `ch_orgp` | Organic phosphorus deposited on the floodplain and in the channel. |
| `bank_orgp`, `bed_orgp` | Organic phosphorus gained from bank and bed erosion. |
| `no3_orgn` | Nitrate converted to organic nitrogen in the channel. |
| `solp_orgp` | Soluble phosphorus converted to organic phosphorus in the channel. |

The sediment columns (`in_sed` to `bed_ero`) are in tons. The nitrogen and phosphorus columns are in kg, although the units row shows tons for every column. All values are totals for the print step; the average annual file gives the average yearly total.

## Sediment budget files

These three file groups are new in 62.0.1. They use the same channel erosion and deposition values, summed in different ways. Their rows are written in free format (list-directed), so column widths vary.

### ch_sedbud files (per channel)

| Column | Units | Description |
|--------|-------|-------------|
| `num` | - | Number of days in the step on which the channel had inflow. |
| `wid` | m | Bankfull width, summed over those days. |
| `dep` | m | Bankfull depth, summed over those days. |
| `fp_km2` | km² | Floodplain area, summed over those days. The floodplain is taken as five times the channel width over the channel length. |
| `ebank_t` | tons | Bank erosion. |
| `ebtm_t` | tons | Bed erosion. |
| `ebank_m` | m | Bank erosion as a width. |
| `ebtm_m` | m | Bed erosion as a depth. |
| `fp_t` | tons | Floodplain deposition. |
| `fp_mm` | mm | Floodplain deposition as a depth over the floodplain, assuming a bulk density of 1 t/m³. |

`wid`, `dep` and `fp_km2` are summed over days, so divide them by `num` to get the average width, depth and floodplain area in the daily, monthly and yearly files. In the average annual file the sums are divided by the number of printed years but `num` is not, so the ratio is too small by that factor.

### chanbud_order files (per stream order)

One row for each stream order from 1 to 12 in every step, with the `ch_sedbud` columns summed over all channels of that order. `num` is then the number of channel-days with inflow, and `wid` / `num` and `dep` / `num` give the average width and depth for the order. `fp_mm` is summed over channels and is not a depth for the order as a whole. The stream order of each channel comes from the `order` column of the channel database.

### sedbud files (basin)

| Column | Units | Description |
|--------|-------|-------------|
| `upland_t` | tons | Sediment yield from all HRUs. |
| `ebank_t` | tons | Bank erosion in all channels. |
| `ebtm_t` | tons | Bed erosion in all channels. |
| `fp_t` | tons | Floodplain deposition in all channels. |
| `res_dep_t` | tons | Net deposition in all reservoirs (sediment in minus sediment out). |
| `wet_dep_t` | tons | Net deposition in all wetlands. |

Deposition inside the channels themselves is not part of this file; it is in the `ch_dep` column of `sd_chanbud`.

### Print timing

The three sediment budget file groups start after the `nyskip` warm-up years, like the other files. Their daily files have a row for every day after that and do not follow the daily print window (`day_start` to `day_end`, `interval`) in [`print.prt`](../input-reference/print-prt.md).

## Basin files

`basin_sd_cha_*`, `basin_sd_chamorph_*` and `basin_sd_chanbud_*` have the same columns as `channel_sd_*`, `channel_sdmorph_*` and `sd_chanbud_*`, with one row for the basin. Each value is the sum over all channels in the basin. Flows are summed along the whole network, so `flo_out` in `basin_sd_cha` is not the flow leaving the basin; use the outlet channel's row in `channel_sd` for that. `basin_sd_cha` has no `water_temp` column, and in `basin_sd_chamorph` the `width`, `depth` and `slope` columns are those of the last channel.

## Sub-daily outflow

When the simulation uses a sub-daily time step and the `channel_sd` row has `y` in `daily`, `channel_sd_subday.txt` has one row per channel per time step: `jday`, `mon`, `day`, `yr`, `unit`, `gis_id`, `tstep` (time step number), `name` and `flo_out`. `flo_out` is the volume of water (m³) leaving the channel in that time step, although the header gives m³/s. The units row and the header of the `.csv` copy are those of the `channel_sdmorph` file.

## Legacy channel files

The `channel` and `basin_cha` rows of [`print.prt`](../input-reference/print-prt.md) open `channel_*.txt` and `basin_cha_*.txt` for legacy channel objects (`chan` in [`object.cnt`](../input-reference/object-cnt.md)). Their 59 columns cover flow, sediment, nutrients, pesticides, bacteria, metals, sediment size classes and erosion:

```
flo_in flo_out evap tloss sed_in sed_out sed_conc orgn_in orgn_out orgp_in orgp_out
no3_in no3_out nh4_in nh4_out no2_in no2_out solp_in solp_out chla_in chla_out
cbod_in cbod_out dis_in dis_out solpst_in solpst_out sorbpst_in sorbpst_out react
volat setlpst resuspst difus reactb bury sedpest bacp baclp met1 met2 met3 sand_in
sand_out silt_in silt_out clay_in clay_out smag_in smag_out lag_in lag_out grvl_in
grvl_out bnk_ero ch_deg ch_dep fp_dep tot_ssed
```

SWAT+ 62.0.1 does not route legacy channels (the routing call is disabled), so these files contain only zeros. Projects built with the SWAT+ Editor use the channels described above.

## Example

The columns of every `chanbud_order_*` file:

```
jday  mon  day  yr  iord  num  wid  dep  fp_km2  ebank_t  ebtm_t  ebank_m  ebtm_m  fp_t  fp_mm
```

Take 40 first-order channels, each 5 m wide, that have flow on every day of a 10-year print period. In `chanbud_order_y.txt` the row with `iord` 1 has `num` = 40 × 365 = 14,600 and `wid` = 73,000, so `wid` / `num` gives the 5 m average width. In `chanbud_order_a.txt` the same row has `num` = 146,000 (the count over all ten years) and `wid` = 73,000 (the ten-year sum divided by 10), so the average width is 10 × `wid` / `num`.

The reference outputs in `refdata/Ames_sub1` of the SWAT+ repository were written by revision 61.0.1 and contain none of the sediment budget files.

## Related files

- [`print.prt`](../input-reference/print-prt.md): switches each file on or off.
- [Channels](../input-reference/cha.md) and [channel-lte](../input-reference/sd-channel.md): channel inputs, including the stream `order` column.
- [Water balance outputs](water-balance.md): the landscape water that reaches the channels.
- [Aquifer, reservoir, plant outputs](aquifer-reservoir-plant.md): reservoir and wetland files.
- [Output naming convention](naming-convention.md): all output files.

??? quote "Sources"

    - File opening and headers: [`header_sd_channel.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_sd_channel.f90), [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90), [`header_channel.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_channel.f90)
    - Header and record types: [`sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_module.f90), [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90), [`water_body_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_body_module.f90), [`channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/channel_module.f90), `basin_sediment_budget` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - Channel writers: [`sd_channel_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_output.f90), [`sd_chanmorph_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_chanmorph_output.f90), [`sd_chanbud_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_chanbud_output.f90)
    - Sediment budget writers: [`ch_sedbud_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_sedbud_output.f90), [`chord_sedbud_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/chord_sedbud_output.f90), [`basin_sedbud_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_sedbud_output.f90)
    - Basin writers: [`basin_sdchannel_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_sdchannel_output.f90), [`basin_chanmorph_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_chanmorph_output.f90), [`basin_chanbud_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_chanbud_output.f90), [`basin_channel_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_channel_output.f90)
    - Values: [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90), [`sd_channel_sediment3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_sediment3.f90), [`ch_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_temp.f90); upland, reservoir and wetland terms in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), [`wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90)
    - Call order: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)

    | File | Header type | Record |
    |------|-------------|--------|
    | `channel_sd_*` | `ch_wbod_hdr`, `hyd_stor_hdr`, `hyd_in_hdr`, `hyd_out_hdr`, `wtmp_hdr` | `ch_wat_*`, `ch_stor`, `ch_in_*`, `ch_out_*`, `wtemp` |
    | `channel_sdmorph_*` | `sdch_hdr` | `chsd_*` (`sd_ch_output`) |
    | `sd_chanbud_*` | `sdch_bud_hdr` | `ch_sed_bud*` (`channel_sediment_budget_output`) |
    | `ch_sedbud_*` | `ch_sedbud_hdr` | `ch_morph*` (`channel_morphology_output`) |
    | `chanbud_order_*` | `ch_bud_order_hdr` | `ch_morph_ord*` |
    | `sedbud_*` | `ch_sed_bud_hdr` | `bsn_sedbud*` (`basin_sediment_budget`) |
    | `channel_sd_subday.txt` | `sdch_hdr_subday` | `ob%hyd_flo(1,ii)` |

    | Column | Fortran variable |
    |--------|------------------|
    | `geo_bf` | `sd_ch_output%aqu_in` |
    | `hc_len` | `sd_ch_output%hc_m` |
    | `flo_out_mm` | `sd_ch_output%flo_mm` |
    | second `deg_btm`, `deg_bank` | `deg_btm_m`, `deg_bank_m` |
    | `null` (each block) | `hyd_output%temp` |
    | `water_temp` | module variable `wtemp` |
    | `ob` (`ch_sedbud`) | `ob(iob)%gis_id` |

---
title: Channel and sediment outputs
description: The channel_*.txt (legacy) and channel_sd_*.txt (sd_channel) files. Columns for routed flow, sediment, and nutrients.
status: review
verified_against:
  - src/channel_output.f90
  - src/sd_channel_output.f90
  - src/basin_channel_output.f90
  - src/basin_sdchannel_output.f90
  - src/channel_module.f90
  - src/water_body_module.f90
  - src/hydrograph_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

SWAT+ supports two channel-routing implementations, each with its own output set.

- **Legacy channel** (`channel_*.txt`, `basin_cha_*.txt`). One row per channel object, holding inflow / outflow of water, sediment, sediment by particle size, nutrients, pesticides, bacteria, and conservative metals.
- **sd_channel** (`channel_sd_*.txt`, `basin_sd_cha_*.txt`). Storage-and-discharge routing. Three blocks of columns: a `water_body` block (area, precip, evap, seep, storage), followed by an inflow `hyd_output` record and an outflow `hyd_output` record.

The channel sediment budget and morphology have their own writers (`sd_chanbud_output.f90`, `sd_chanmorph_output.f90`) and produce `*_chanbud_*.txt` and `*_chamorph_*.txt`.

## Legacy channel files

### Source

- Writer: [`src/channel_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/channel_output.f90), units 2480 (day), 2481 (mon), 2482 (yr), 2483 (aa).
- Basin sum: [`src/basin_channel_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_channel_output.f90).
- File opening: [`src/header_channel.f90`](https://github.com/swat-model/swatplus/blob/main/src/header_channel.f90).
- Record type: [`src/channel_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/channel_module.f90), `type ch_output`.

### Format

Each line is the seven leading columns (jday, mon, day, yr, unit, gis_id, name), then the 60 fields of `ch_output` in declaration order.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | flo_in | ha-m | streamflow into reach |
| 2 | flo_out | ha-m | streamflow out of reach |
| 3 | evap | m^3/s | rate of water loss by evaporation |
| 4 | tloss | m^3/s | rate of transmission loss through streambed |
| 5 | sed_in | tons | sediment transported into reach |
| 6 | sed_out | tons | sediment transported out of reach |
| 7 | sed_conc | mg/L | sediment concentration in reach |
| 8 | orgn_in | kg N | organic nitrogen in |
| 9 | orgn_out | kg N | organic nitrogen out |
| 10 | orgp_in | kg P | organic phosphorus in |
| 11 | orgp_out | kg P | organic phosphorus out |
| 12 | no3_in | kg N | nitrate in |
| 13 | no3_out | kg N | nitrate out |
| 14 | nh4_in | kg | ammonium in |
| 15 | nh4_out | kg | ammonium out |
| 16 | no2_in | kg | nitrite in |
| 17 | no2_out | kg | nitrite out |
| 18 | solp_in | kg P | soluble phosphorus in |
| 19 | solp_out | kg P | soluble phosphorus out |
| 20 | chla_in | kg | chlorophyll-a in |
| 21 | chla_out | kg | chlorophyll-a out |
| 22 | cbod_in | kg | carbonaceous BOD in |
| 23 | cbod_out | kg | carbonaceous BOD out |
| 24 | dis_in | kg | dissolved oxygen in |
| 25 | dis_out | kg | dissolved oxygen out |
| 26 | solpst_in | mg pst | soluble pesticide in |
| 27 | solpst_out | mg pst | soluble pesticide out |
| 28 | sorbpst_in | mg pst | sorbed pesticide in |
| 29 | sorbpst_out | mg pst | sorbed pesticide out |
| 30 | react | mg pst | pesticide loss by reaction in water |
| 31 | volat | mg | pesticide loss by volatilization |
| 32 | setlpst | mg pst | pesticide settling from water to bed |
| 33 | resuspst | mg | pesticide resuspended from bed |
| 34 | difus | mg | pesticide diffused from water to bed |
| 35 | reactb | mg | pesticide reaction loss in bed |
| 36 | bury | mg | pesticide buried |
| 37 | sedpest | mg | pesticide in bed sediment |
| 38 | bacp | # cfu/100mL | persistent bacteria out |
| 39 | baclp | # cfu/100mL | less persistent bacteria out |
| 40 | met1 | kg | conservative metal #1 out |
| 41 | met2 | kg | conservative metal #2 out |
| 42 | met3 | kg | conservative metal #3 out |
| 43 | sand_in | tons | sand in |
| 44 | sand_out | tons | sand out |
| 45 | silt_in | tons | silt in |
| 46 | silt_out | tons | silt out |
| 47 | clay_in | tons | clay in |
| 48 | clay_out | tons | clay out |
| 49 | smag_in | tons | small aggregate in |
| 50 | smag_out | tons | small aggregate out |
| 51 | lag_in | tons | large aggregate in |
| 52 | lag_out | tons | large aggregate out |
| 53 | grvl_in | tons | gravel in |
| 54 | grvl_out | tons | gravel out |
| 55 | bnk_ero | tons | bank erosion |
| 56 | ch_deg | tons | channel degradation |
| 57 | ch_dep | tons | channel deposition |
| 58 | fp_dep | tons | floodplain deposition |
| 59 | tot_ssed | mg/L | total suspended sediments |

### Example header

`refdata/Ames_sub1/basin_cha_aa.txt`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
  jday    mon   day   yr    unit  gis_id  name                 flo_in        flo_out            evap        tloss           sed_in        sed_out       sed_conc       orgn_in        orgn_out         orgp_in        orgp_out        no3_in        no3_out          nh4_in        nh4_out         no2_in        no2_out       solp_in       solp_out         chla_in       chla_out        cbod_in       cbod_out         dis_in        dis_out    solpst_in      solpst_out    sorbpst_in     sorbpst_out       react             volat     setlpst          resuspst       difus         reactb          bury            sedpest             bacp          baclp           met1           met2           met3        sand_in       sand_out        silt_in       silt_out        clay_in       clay_out        smag_in       smag_out         lag_in        lag_out        grvl_in       grvl_out        bnk_ero         ch_deg         ch_dep         fp_dep       tot_ssed
                                                                 ha-m           ha-m            ha-m         ha-m             tons           tons           mg/L           kgN             kgN             kgP             kgP           kgN            kgN              kg             kg             kg             kg           kgP            kgP              kg             kg             kg             kg             kg             kg       mg_pst          mg_pst        mg_pst          mg_pst      mg_pst                mg      mg_pst                mg      mg_pst             mg            mg                 mg
```

The header reports `evap` and `tloss` units as `ha-m`, but `ch_output` carries them as `m^3/s` (rate). The unit row in the file does not match the source comment.

## sd_channel files

### Source

- Writer: [`src/sd_channel_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/sd_channel_output.f90), units 2500 (day), 2501 (mon), 2502 (yr), 2503 (aa); subdaily on unit 2508.
- Basin sum: [`src/basin_sdchannel_output.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_sdchannel_output.f90).
- File opening: [`src/header_sd_channel.f90`](https://github.com/swat-model/swatplus/blob/main/src/header_sd_channel.f90).
- Record types: [`src/water_body_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/water_body_module.f90), `type water_body`, and [`src/hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/hydrograph_module.f90), `type hyd_output`.

### Format

Each record is the seven leading columns, then four blocks of fields written in this order by `sd_channel_output.f90`:

```fortran
write (2500,100) time%day, time%mo, time%day_mo, time%yrc, ichan, ob(iob)%gis_id, ob(iob)%name, &
  ch_wat_d(ichan)%area_ha, ch_wat_d(ichan)%precip, ch_wat_d(ichan)%evap, ch_wat_d(ichan)%seep, &
  ch_stor(ichan), ch_in_d(ichan), ch_out_d(ichan), wtemp
```

**Block 1: water body status (4 fields).**

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | area | ha | channel water surface area |
| 2 | precip | m^3 | precipitation on water surface |
| 3 | evap | m^3 | evaporation from water surface |
| 4 | seep | m^3 | seepage from streambed |

**Block 2: channel storage `ch_stor` (one `hyd_output` record, 18 fields).** These are the `_stor` columns in the file header.

**Block 3: inflow `ch_in_d` (one `hyd_output` record, 18 fields).** These are the `_in` columns.

**Block 4: outflow `ch_out_d` (one `hyd_output` record, 18 fields).** These are the `_out` columns.

**Block 5: water temperature `wtemp`** (deg C), one trailing scalar.

The 18 fields of `hyd_output`, in declaration order:

| Field | Units | Description |
|-------|-------|-------------|
| flo | m^3 (storage), m^3/s (in / out flow rate) | volume or flow rate |
| sed | metric tons | sediment |
| orgn | kg N | organic N |
| sedp | kg P | organic P |
| no3 | kg N | NO3-N |
| solp | kg P | soluble P |
| chla | kg | chlorophyll-a |
| nh3 | kg N | NH3 |
| no2 | kg N | NO2 |
| cbod | kg | carbonaceous BOD |
| dox | kg | dissolved oxygen |
| san | tons | detached sand |
| sil | tons | detached silt |
| cla | tons | detached clay |
| sag | tons | detached small aggregate |
| lag | tons | detached large aggregate |
| grv | tons | gravel |
| temp | deg C | temperature |

The line ends with `wtemp` after the `out` block.

### Example header

`refdata/Ames_sub1/basin_sd_cha_aa.txt`:

```
 demo                      SWAT+ 2024-08-27        MODULAR Rev 2024.61.0.1-33-g68b1328
   jday   mon   day    yr     unit   gis_id   name                  area         precip           evap           seep          flo_stor       sed_stor      orgn_stor      sedp_stor       no3_stor      solp_stor      chla_stor       nh3_stor       no2_stor      cbod_stor       dox_stor       san_stor       sil_stor       cla_stor       sag_stor       lag_stor       grv_stor           null         flo_in         sed_in        orgn_in        sedp_in         no3_in        solp_in        chla_in         nh3_in         no2_in        cbod_in         dox_in         san_in         sil_in         cla_in         sag_in         lag_in         grv_in           null        flo_out        sed_out       orgn_out       sedp_out        no3_out       solp_out       chla_out        nh3_out        no2_out       cbod_out        dox_out        san_out        sil_out        cla_out        sag_out        lag_out        grv_out           null
                                                                      ha            m^3            m^3            m^3             m^3           tons            kgN            kgP            kgN            kgP             kg            kgN            kgN             kg             kg           tons           tons           tons           tons           tons           tons                         m^3/s           tons            kgN            kgP            kgN            kgP             kg            kgN            kgN             kg             kg           tons           tons           tons           tons           tons           tons                         m^3/s           tons            kgN            kgP            kgN            kgP             kg            kgN            kgN             kg             kg           tons           tons           tons           tons           tons           tons
```

Each block ends with a `null`-labelled column. That column is the `temp` field of `hyd_output`. The writer passes `ch_in_d(ichan)`, `ch_out_d(ichan)`, and `ch_stor(ichan)` as whole records, so the 18th field of each block is `temp`. The basin-wide water temperature is the trailing `wtemp` scalar written after the outflow block.

## Channel sediment budget and morphology

- `sd_chanbud_*.txt`. Sediment budget per channel: bank erosion, bed erosion, deposition. Writer: `src/sd_chanbud_output.f90`. Basin sum in `src/basin_chanbud_output.f90`.
- `sd_chamorph_*.txt`. Channel morphology: width, depth, slope. Writer: `src/sd_chanmorph_output.f90`. Basin sum in `src/basin_chanmorph_output.f90`.

## Related files

- [Aquifer, reservoir, plant outputs](../output-reference/aquifer-reservoir-plant.md).
- [Water balance outputs](../output-reference/water-balance.md).

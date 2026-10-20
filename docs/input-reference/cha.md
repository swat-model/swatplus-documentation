---
title: "Channel group files (*.cha)"
description: The files on the channel line of file.cio, which of them SWAT+ 62.0.1 uses, initial channel contents (initial.cha), stream temperature (temperature.cha) and the legacy channel files.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_cha.f90
  - src/proc_read.f90
  - src/command.f90
  - src/ch_read.f90
  - src/ch_read_init.f90
  - src/ch_read_init_cs.f90
  - src/ch_read_hyd.f90
  - src/ch_read_sed.f90
  - src/ch_read_nut.f90
  - src/ch_read_temp.f90
  - src/ch_initial.f90
  - src/channel_data_module.f90
  - src/sd_channel_module.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_init.f90
  - src/sd_channel_control3.f90
  - src/sd_channel_sediment3.f90
  - src/ch_temp.f90
  - src/shade_factor_read.f90
  - src/hydrograph_module.f90
  - src/om_water_init.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The `channel` line of [`file.cio`](file-cio.md) names eight channel input files. The table below gives the use of each in 62.0.1. `initial.cha` (initial channel contents), `temperature.cha` (stream temperature) and the legacy files `channel.cha`, `hydrology.cha` and `sediment.cha` are described below; the other files are on the [chandeg channel page](sd-channel.md).

SWAT+ has two channel objects. The channels listed in [`chandeg.con`](con.md) (SWAT-DEG or "lte" channels) are the ones 62.0.1 routes; their parameter files are on the [chandeg channel page](sd-channel.md). The legacy channel object listed in [`channel.con`](../input-reference/con.md) is set up at the start of a run, but its daily routing is switched off in 62.0.1, so water sent to it does not leave it. Build channel networks with [`chandeg.con`](../input-reference/con.md).

## Files on the channel line

Each slot can be `null`. A missing file is treated like `null`.

| Slot | Default name | Used in 62.0.1 for | Documented on |
|------|--------------|--------------------|---------------|
| 1 | `initial.cha` | Initial water, sediment, nutrients and pesticides in chandeg channels. | [initial.cha](#initialcha) |
| 2 | `channel.cha` | Legacy channel object only. No effect on results. | [legacy files](#legacy-channel-files) |
| 3 | `hydrology.cha` | Legacy channel object only. No effect on results. | [legacy files](#legacy-channel-files) |
| 4 | `sediment.cha` | Legacy channel object only. No effect on results. | [legacy files](#legacy-channel-files) |
| 5 | [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha) | In-stream water quality of chandeg channels. | [chandeg channels](sd-channel.md#nutrientscha) |
| 6 | [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha) | One row per chandeg channel, pointing to the other files. | [chandeg channels](sd-channel.md#channel-ltecha) |
| 7 | [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha) | Geometry, hydraulics and sediment properties of chandeg channels. | [chandeg channels](sd-channel.md#hyd-sed-ltecha) |
| 8 | `temperature.cha` | Read, but the stream temperature calculation uses only built-in values. | [temperature.cha](#temperaturecha) |

Three more channel files have fixed names and are read when present in the run folder: `initial.cha_cs` (initial pathogens, salts and constituents, [below](#initialcha_cs)), [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) ([chandeg channels](sd-channel.md#sed_nutcha)) and `shade_factor.shf` ([below](#shade-factor-file)).

## initial.cha

Named sets of initial conditions for chandeg channels. Each row of [`channel-lte.cha`](sd-channel.md#channel-ltecha) selects a set by name in its `cha_ini` column. Free format: two header lines are skipped, then one set per line. There is no `id` column, so the first value on each line is the name. The Editor adds a trailing `description` value, which the reader ignores.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Name of the set, matched against `cha_ini` in [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha). |
| 2 | `org_min` | Name of a row in [`om_water.ini`](ini.md): initial water, sediment and nutrient concentrations. |
| 3 | `pest` | Name of a row in [`pest_water.ini`](pes.md): initial pesticide in the water and the bed. |
| 4 | `path` | Read but not used. Initial pathogens come from `initial.cha_cs`. |
| 5 | `hmet` | Read but not used. |
| 6 | `salt` | Read but not used. Initial salts come from `initial.cha_cs`. |

A `cha_ini` name not found in `initial.cha`, or an `org_min` or `pest` name not found in its file, falls back to row 1 of that file without a message. Keep `initial.cha` and an [`om_water.ini`](../input-reference/ini.md#om_waterini) in any model with chandeg channels.

### Initial water and constituents

The `flo` value of the [`om_water.ini`](../input-reference/ini.md#om_waterini) row is the initial water depth as a fraction of the bankfull depth `dp`. The channel starts with the volume the [rating curve](sd-channel.md#channel-geometry-and-rating-curve) gives at that depth, and the concentrations of the row are converted to masses with that volume. With `flo` of 1 or less all of it is channel storage. Above 1 the volume is split between channel and floodplain in proportion to their volumes on the rating curve. Channels 0.001 km (1 m) long or shorter start empty.

Initial pesticides in the water are the [`pest_water.ini`](../input-reference/pes.md#pest_waterini) concentration (mg/kg) times the stored water; pesticides in the bed are the benthic concentration times the volume of the active bed layer (width times length times the pesticide's active bed depth).

## initial.cha_cs

An optional file with a fixed name, read when present, with initial pathogens, salts and other constituents for chandeg channels. Two header lines are skipped, then one row per line:

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Name of the row. Not checked. |
| 2 | `pest` | Read but not used. Pesticides come from `initial.cha`. |
| 3 | `path` | Name of a row in [`path_water.ini`](pth.md). |
| 4 | `hmet` | Read but not used. |
| 5 | `salt` | Name of a row in [`salt_channel.ini`](salt.md): initial salt ion concentrations (g/m³). |
| 6 | `cs` | Name of a row in [`cs_channel.ini`](cs.md): initial constituent concentrations (g/m³). |

Rows are paired with `initial.cha` by position: row 3 of `initial.cha_cs` applies to channels that use row 3 of `initial.cha`, whatever its name. Keep the two files in the same order with the same number of rows. Salt and constituent masses are the concentrations times the initial water volume.

In 62.0.1 the pathogen pointer is resolved, but the initial pathogen values are then read from the [`path_water.ini`](../input-reference/pth.md#path_waterini) row with the position of the channel's [`pest_water.ini`](../input-reference/pes.md#pest_waterini) row.

## temperature.cha

Parameters of the stream temperature calculation for chandeg channels. Free format: two header lines are skipped, then one set per line with 15 values. The name is limited to 13 characters.

| # | Column | Units | Built-in value | Typical range | Description |
|---|--------|-------|----------------|---------------|-------------|
| 1 | `name` | - | - | - | Name of the set (up to 13 characters). |
| 2 | `sno_mlt` | - | 1.0 | - | Weight of the snowmelt contribution. |
| 3 | `gw` | - | 1.0 | - | Weight of the groundwater contribution. |
| 4 | `sur_lat` | - | 1.0 | - | Weight of the surface runoff and lateral flow contributions. |
| 5 | `sno_lag` | days | 2 | 1 to 3 | Air temperature averaging period for snowmelt. |
| 6 | `gw_lag` | days | 250 | 200 to 365 | Air temperature averaging period for groundwater. |
| 7 | `surf_lag` | days | 5 | 2 to 5 | Air temperature averaging period for surface runoff. |
| 8 | `lat_lag` | days | 10 | 5 to 10 | Air temperature averaging period for lateral flow. |
| 9 | `lat_lag_coef` | - | 0.75 | - | Multiplier on the lagged air temperature for lateral flow. |
| 10 | `surf_lag_coef` | - | 0.75 | - | Multiplier on the lagged air temperature for surface runoff and snowmelt. |
| 11 | `gw_lag_coef` | - | 0.75 | - | Multiplier on the lagged air temperature for groundwater. |
| 12 | `hex_coef1` | - | 0.75 | - | Multiplier on the dew point temperature in the heat exchange. |
| 13 | `hex_coef2` | - | 1.5 | - | Divisor on the channel depth when the flow depth for heat exchange is calculated. |
| 14 | `sf_on` | - | 0 | 0 or 1 | Shade factor source: `1` daily values from `shade_factor.shf`, `0` the single value `ssff`. Integer. |
| 15 | `ssff` | fraction | 0.5 | 0 to 1 | Shade factor: the fraction of solar radiation kept off the water surface. |

**In 62.0.1 the rows of `temperature.cha` have no effect.** The reader stores them, but the temperature calculation always uses the built-in values in the table, whether or not the file exists, for every channel. With the built-in `sf_on` of 0, `shade_factor.shf` is not used either. The stream temperature calculation itself runs every day for every chandeg channel.

### Stream temperature

The temperature of the water leaving a channel is calculated in three steps. Values in this section are the built-in values above.

**Local inflow.** For the routing units that drain directly into the channel, the day's HRU snowmelt $Q_{sno}$, surface runoff $Q_{sur}$, lateral flow $Q_{lat}$ and water yield $Q_{wyld}$ are summed (mm), and the groundwater inflow $Q_{gw}$ (m³/s, at most 10) is taken from the channel's hydrograph separation. Each component gets an air temperature averaged over its lag period: $T_x$ is the mean of the daily $(T_{max} + T_{min})/2$ over the last `surf_lag`, `lat_lag`, `gw_lag` or `sno_lag` days, at least 0.01 °C, and for snowmelt at most 2.5 °C. In the first simulation year the lag is limited to the day of the year. Then

$$T_{loc} = \frac{a_{sno} k_{sur} T_{sno} Q_{sno} + a_{gw} k_{gw} T_{gw} Q_{gw} + a_{sl} k_{lat} T_{lat} Q_{lat} + a_{sl} k_{sur} T_{sur} Q_{sur}}{Q_{wyld}}$$

with $a_{sno}$ = `sno_mlt`, $a_{gw}$ = `gw`, $a_{sl}$ = `sur_lat`, and $k_{sur}$, $k_{lat}$ and $k_{gw}$ the lag coefficients `surf_lag_coef`, `lat_lag_coef` and `gw_lag_coef`. With gwflow active the groundwater term is left out. If $T_{loc}$ differs from the previous day's outflow temperature by more than 5 °C, or the weather station has no temperature gauge, $T_{loc} = 5 + 0.75\,\bar{T}$ with $\bar{T}$ the day's mean air temperature.

**Mixing with upstream water.** Water from upstream channels arrives at their flow-weighted outflow temperature $T_{up}$ (or $5 + 0.75\,\bar{T}$ for a channel without upstream channels). It is weighted by $q$, the outflow of the channel itself for the day (m³/s):

$$T_0 = \frac{T_{up}\,q + T_{loc}\,Q_{wyld}}{q + Q_{wyld}}$$

or $T_0 = T_{loc}$ when the outflow is zero.

**Heat exchange.** Following Edinger et al. (1974), with dew point $T_d = \min(h_1\,T_{dew},\ \bar{T})$, $h_1$ = `hex_coef1`, $T_m = (T_0 + T_d)/2$ and wind speed $U$ (m/s),

$$\beta = 0.35 + 0.015\,T_m + 0.0012\,T_m^2, \qquad K_e = 4.48 + 0.05\,T_0 + (\beta + 0.47)(9.2 + 0.46\,U^2)$$

The short-wave input is $H_s = 0.97 \times 11.57\,R_s\,(1 - SF)$ W/m², with $R_s$ the solar radiation (MJ/m²/day) and $SF$ the shade factor `ssff`. The long-wave input is $H_a = 0.96\,\varepsilon\,\sigma\,(\bar{T} + 273.15)^4$ with $\varepsilon = 0.74 + 0.0065\,e_a\,(1 + 0.17\,C^2)$, $e_a$ the vapour pressure (hPa) and $C = 0.9\,R_s/R_{s,max} + 0.1$ the cloud factor. The equilibrium temperature is

$$T_{eq} = T_d + \frac{H_s + H_a - 305.5 - 4.48\,T_d}{K_e}$$

and the outflow temperature is

$$T = T_0 + \frac{K_e\,(T_{eq} - T_0)\,t}{\rho\,c_p\,d_f/86400}, \qquad T \ge 0.001$$

where $t$ is the travel time through the channel (days) at the day's peak flow, $\rho c_p = 4.186 \times 10^6$ J/m³/°C and $d_f$ the flow depth (m). The flow depth comes from a triangular section with depth-to-width ratio $(D/h_2)/W$, $h_2$ = `hex_coef2`, that passes the day's outflow at the channel velocity; it is at least 0.1 m and at most $2D$.

The result is the outflow temperature passed downstream and reported in the outflow block of the `channel_sd` output (see [channel outputs](../output-reference/channel-sediment-nutrient.md)). The in-stream water quality and the `water_temp` column of `channel_sd` use $5 + 0.75\,\bar{T}$ instead.

### Shade factor file

`shade_factor.shf` has a fixed name. Two header lines are skipped, then one record per line with three values: day of year, channel number (the chandeg channel's sequence number) and shade factor (fraction). It would be used with `sf_on` = 1 on day 1 to 365 (day 366 uses 0.5); in 62.0.1 `sf_on` is always the built-in 0.

## Legacy channel files

`channel.cha`, `hydrology.cha` and `sediment.cha` describe the legacy channel object of [`channel.con`](../input-reference/con.md). SWAT+ 62.0.1 reads them and sets up those channels at the start of the run, but does not route water through them, so the values have no effect on results. The formats are given for existing models. Two header lines are skipped in each file and the reader does not match columns by header name; the column names below are the names the reader uses.

### channel.cha

| # | Column | Description |
|---|--------|-------------|
| 1 | `id` | Channel number. |
| 2 | `name` | Channel name. |
| 3 | `init` | Name of a row in `initial.cha`. |
| 4 | `hyd` | Name of a row in `hydrology.cha`. |
| 5 | `sed` | Name of a row in `sediment.cha`. |
| 6 | `nut` | Name of a row in [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha). |

Names that are not found are written to `diagnostics.out` as `<name> not found (hydrology.cha)` and similar.

### hydrology.cha

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name of the set. |
| 2 | `w` | m | 2.0 | Average width of the main channel. |
| 3 | `d` | m | 0.5 | Average depth of the main channel. |
| 4 | `s` | m/m | 0.01 | Average slope. Values of 0 or less become 0.0001. |
| 5 | `l` | km | 0.1 | Length. Values of 0 or less become 0.001. |
| 6 | `n` | - | 0.05 | Manning's n, limited to 0.01 to 0.70. |
| 7 | `k` | mm/h | 0.01 | Effective hydraulic conductivity of the channel alluvium. |
| 8 | `wdr` | m/m | 6.0 | Width-to-depth ratio. Values of 0 or less become 3.5. |
| 9 | `alpha_bnk` | days | 0.03 | Bank storage recession factor, stored as $e^{-\alpha}$. |
| 10 | `side` | - | 0.0 | Side slope (horizontal per unit rise). Values of 10⁻⁶ or less become 2.0. |

### sediment.cha

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name of the set. |
| 2 | `eqn` | - | 0 | Sediment routing method: `0` original SWAT, `1` Bagnold, `2` Kodatie, `3` Molinas and Wu, `4` Yang. |
| 3 | `cov1` | - | 0.1 | Channel erodibility factor. Limited to 0 to 1 for `eqn` 0; for the other methods, values of 0 or less become 1 and values above 25 become 25. |
| 4 | `cov2` | - | 0.1 | Channel cover factor, with the same limits as `cov1`. |
| 5 | `bnk_bd` | g/cm³ | 0 | Bank bulk density. Values near 0 become 1.40. |
| 6 | `bed_bd` | g/cm³ | 0 | Bed bulk density. Values near 0 become 1.50. |
| 7 | `bnk_kd` | cm³/N/s | 0 | Bank erodibility from a jet test. Values near 0 become $0.2/\sqrt{\tau_c}$, or 0.2 without a critical shear stress. |
| 8 | `bed_kd` | cm³/N/s | 0 | Bed erodibility, as `bnk_kd`. |
| 9 | `bnk_d50` | µm | 0 | Bank median particle size. Values near 0 become 50; at most 10000. |
| 10 | `bed_d50` | µm | 0 | Bed median particle size. Values near 0 become 500; at most 10000. |
| 11 | `tc_bnk` | N/m² | 0 | Critical shear stress of the bank. |
| 12 | `tc_bed` | N/m² | 0 | Critical shear stress of the bed. |
| 13 to 24 | `erod(1)` to `erod(12)` | - | 0 | Monthly erodibility, 0 non-erosive to 1 no resistance. If all twelve are zero, all are set to `cov1`. |

## Example

`refdata/Osu_1hru` in the SWAT+ repository, [`file.cio`](../input-reference/file-cio.md) channel line and `initial.cha`:

```
channel           initial.cha       null              null              null              nutrients.cha     channel-lte.cha   hyd-sed-lte.cha   null
```

```
initial.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description
initcha1                   no_init              null              null              null              null  null
```

The model uses only chandeg channels: slots 2 to 4 and 8 are `null`. All channels use the initial set `initcha1`, whose `org_min` points to the row `no_init` of [`om_water.ini`](../input-reference/ini.md#om_waterini); that row has all values zero, so the channels start empty. The `pest`, `path`, `hmet` and `salt` pointers are `null`. No reference dataset includes `temperature.cha`, `initial.cha_cs`, `channel.cha`, `hydrology.cha` or `sediment.cha`.

## Related files

- [Chandeg channel files](sd-channel.md): [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha), [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) and [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha).
- [`chandeg.con` and `channel.con`](con.md): the two channel object types.
- [`file.cio`](file-cio.md): the `channel` line.
- [`om_water.ini`](ini.md), [`pest_water.ini`](pes.md), [`path_water.ini`](pth.md), [`salt_channel.ini`](salt.md), [`cs_channel.ini`](cs.md): initial contents referenced from `initial.cha` and `initial.cha_cs`.
- [`tmp.cli`](tmp.md): the daily maximum and minimum temperatures used for the lagged air temperatures.
- [Channel outputs](../output-reference/channel-sediment-nutrient.md) and [channels](../model-theory/channels.md) in the model theory.

??? quote "Sources"

    - File name slots: `type input_cha` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90); `in_shf` in the same module
    - Read order: [`proc_cha.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cha.f90); `temperature.cha` and `shade_factor.shf` from [`proc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_read.f90)
    - Readers: [`ch_read_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_init.f90), [`ch_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_init_cs.f90), [`ch_read_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_temp.f90), [`shade_factor_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/shade_factor_read.f90), [`ch_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read.f90), [`ch_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_hyd.f90), [`ch_read_sed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_sed.f90)
    - Type definitions: [`channel_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/channel_data_module.f90) (`channel_init_datafiles`, `channel_init_datafiles_cs`, `water_temperature_data`, `channel_data_char_input`, `channel_hyd_data`, `channel_sed_data`); `swatdeg_init_datafiles` in [`sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_module.f90); `shade_factor_data` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Initial pointers and contents: [`sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`om_water_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_water_init.f90)
    - Stream temperature: [`ch_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_temp.f90), called from [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90); travel time and velocity from [`sd_channel_sediment3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_sediment3.f90)
    - Legacy object: set-up in [`ch_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_initial.f90); the `"chan"` case is commented out in [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | `initial.cha` row | `ch_init(i)` (`name`, `org_min`, `pest`, `path`, `hmet`, `salt`) |
    | `initial.cha_cs` row | `ch_init_cs(i)` (`name`, `pest`, `path`, `hmet`, `salt`, `cs`) |
    | resolved pointers | `sd_init(i)%org_min`, `%pest`, `%path`, `%salt`, `%cs` |
    | `temperature.cha` row | `w_temp(i)`, components as the column names |
    | `shade_factor.shf` row | `shf_db(i)%jday`, `%cha`, `%value` |
    | `channel.cha` row | `ch_dat_c(i)` -> `ch_dat(i)` |
    | `hydrology.cha` row | `ch_hyd(i)` |
    | `sediment.cha` row | `ch_sed(i)` |

---
title: "*.cli (climate files)"
description: Weather stations, weather generator statistics, lists of observed climate data files, and atmospheric deposition inputs.
status: review
verified_against:
  - src/cli_staread.f90
  - src/cli_wgnread.f90
  - src/cli_initwgn.f90
  - src/cli_pmeas.f90
  - src/cli_tmeas.f90
  - src/cli_smeas.f90
  - src/cli_hmeas.f90
  - src/cli_wmeas.f90
  - src/cli_petmeas.f90
  - src/climate_control.f90
  - src/cli_clgen.f90
  - src/cli_tgen.f90
  - src/et_pot.f90
  - src/cli_read_atmodep.f90
  - src/cli_atmodep_time_control.f90
  - src/cli_read_atmodep_salt.f90
  - src/cli_read_atmodep_cs.f90
  - src/nut_nrain.f90
  - src/salt_rain.f90
  - src/cs_rain.f90
  - src/search.f90
  - src/hyd_read_connect.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/climate_module.f90
  - src/basin_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The climate files tell SWAT+ where each spatial object gets its weather. Every object names a weather station in the `wst` column of its connect file (for example [`hru.con`](con.md)). The weather station, a row of `weather-sta.cli`, names a weather generator station and, for each weather variable, either an observed data file or `sim` to generate the variable.

The files below are named on the `climate` line of [`file.cio`](file-cio.md), in this order:

| Position | Default name | Contents |
|----------|--------------|----------|
| 1 | `weather-sta.cli` | Weather stations. |
| 2 | `weather-wgn.cli` | Weather generator statistics. |
| 3 | `pet.cli` | List of observed potential evapotranspiration files. |
| 4 | `pcp.cli` | List of precipitation files ([`*.pcp`](pcp.md)). |
| 5 | `tmp.cli` | List of temperature files ([`*.tmp`](tmp.md)). |
| 6 | `slr.cli` | List of solar radiation files. |
| 7 | `hmd.cli` | List of relative humidity files. |
| 8 | `wnd.cli` | List of wind speed files. |
| 9 | `atmodep.cli` | Atmospheric deposition of nitrogen. |

Two more deposition files, `salt_atmo.cli` and `cs_atmo.cli`, have fixed names and are not listed in [`file.cio`](../input-reference/file-cio.md).

A position set to `null`, or naming a file that does not exist, is skipped. A model needs `weather-sta.cli` and, for any generated variable or missing value, `weather-wgn.cli`. SWAT+ 62.0.1 reads climate input only from these text files; it has no netCDF climate input.

## Common rules

All climate files are free format, with values separated by spaces or tabs. The first line is a title and is skipped; most files also skip a column header line, as described for each file.

Names (stations, files) can be up to 50 characters and are matched with upper and lower case distinguished. A name that contains a slash, a comma or a space must be put in quotes.

SWAT+ looks names up with a binary search, so every list that is searched must be in ascending order by character code (digits before upper-case letters, upper case before lower case). This applies to the station names in `weather-sta.cli` and `weather-wgn.cli`, the file names in each observed data list, and the station names in `atmodep.cli`. A list out of order can make SWAT+ miss names that are present.

### Path prefixes

The last lines of [`file.cio`](../input-reference/file-cio.md) give an optional folder for each type of observed data file: `pcp_path`, `tmp_path`, `slr_path`, `hmd_path` and `wnd_path`. When the value is `null`, the data files are opened from the project folder. Otherwise the value is put in front of each file name with nothing added in between, so it must end with a path separator (for example `C:\weather\pcp\`), and it can be up to 80 characters. A path containing a forward slash must be put in quotes, because an unquoted slash ends a free-format value. There is no path line for PET files; they are always opened from the project folder.

## weather-sta.cli

One line per weather station. Line 1 is a title and line 2 is the column header; both are skipped. Each later line has nine values in the order below.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Weather station name, referenced by the `wst` column of the connect files. |
| 2 | `wgn` | Name of a weather generator station in `weather-wgn.cli`. |
| 3 | `pcp` | Name of a precipitation file listed in `pcp.cli`, or `sim` to generate precipitation. |
| 4 | `tmp` | Name of a temperature file listed in `tmp.cli`, or `sim` to generate maximum and minimum temperature. |
| 5 | `slr` | Name of a solar radiation file listed in `slr.cli`, or `sim`. |
| 6 | `hmd` | Name of a relative humidity file listed in `hmd.cli`, or `sim`. |
| 7 | `wnd` | Name of a wind speed file listed in `wnd.cli`, or `sim`. |
| 8 | `wnd_dir` | Read as the name of a PET file listed in `pet.cli`, or `null` for none. SWAT+ Editor labels this column `wnd_dir`; SWAT+ 62.0.1 has no wind direction input. |
| 9 | `atmo_dep` | Name of a deposition station in `atmodep.cli`, or `null`. |

A tenth value on a line is ignored, so a PET file name placed after `atmo_dep` is not read.

### Unmatched names

| Column | Name not found | Message in `diagnostics.out` |
|--------|----------------|------------------------------|
| `pcp`, `tmp`, `slr`, `hmd`, `wnd` | The variable is generated for the whole run. | `<name> file not found (pgage)`, `(tgage)`, `(sgage)`, `(hgage)` or `(wgage)`, unless the value is `sim` |
| `wnd_dir` (PET) | No observed PET for the station. | `<name> file not found (petgage)`, unless the value is `null`; `sim` gives the message |
| `atmo_dep` | See [deposition stations](#deposition-stations). | `<name> file not found (atmodep)`, unless the value is `null` |
| `wgn` | The station uses the first station in `weather-wgn.cli`. | none |

An object whose `wst` name is not in `weather-sta.cli` uses the first weather station, also without a message.

The six-day air temperature record used for stream temperature starts each station with the same value, the mean of the January `tmp_min_ave` and `tmp_max_sd` of the first station in `weather-wgn.cli`. It is replaced by the daily mean temperatures of the run within the first six days.

### Example

`refdata/Ames_sub1/weather-sta.cli` in the SWAT+ repository:

```
weather-sta.cli:
name                           wgn               pcp                tmp                slr              hmd             wnd         wnd_dir          atmo_dep
wgn_sta1                   wgn_001            ames.pcp           ames.tem              sim              sim             sim            null              null
```

One station, `wgn_sta1`, with measured precipitation from `ames.pcp` and generated solar radiation, humidity and wind. Two names do not match. The generator station in `weather-wgn.cli` is called `wgn001`, so `wgn_001` is not found and the first (and only) generator station is used without a message. `tmp.cli` lists `ames.tmp`, so `ames.tem` is not found and temperature is generated for the whole run (see [`*.tem`](tem.md)).

## weather-wgn.cli

Monthly weather statistics for the weather generator. Each weather station uses its generator station to generate the variables set to `sim`, to fill missing days in the observed files, and for quantities that depend on location. Line 1 is a title. Each generator station then takes 14 lines:

1. a station line with five values (no header line above it),
2. a column header line, which is skipped,
3. twelve monthly lines, January to December, with 14 values each.

The number of stations is set by the length of the file.

### Station line

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Generator station name, referenced by the `wgn` column of `weather-sta.cli`. |
| 2 | `lat` | decimal degrees | Latitude. Sets day length, maximum possible solar radiation and the day length at which plants go dormant for every weather station that uses this generator station, also when all variables are observed. When SWAT+ estimates plant start dates, a latitude of 0 or less is treated as the Southern Hemisphere. |
| 3 | `lon` | decimal degrees | Longitude. Not used by SWAT+. |
| 4 | `elev` | m | Elevation. Used for the [elevation adjustment](pcp.md#elevation-adjustment) of generated precipitation and temperature. |
| 5 | `rain_yrs` | years | Number of years of record used to find `pcp_hhr`. A value below 1 is replaced by 10. Called `yrs_pcp` in earlier documentation. |

### Monthly lines

The column headers below are those SWAT+ Editor writes; older files use the upper-case names in the second column. SWAT+ reads by position only.

| # | Column | Older header | Units | Typical range | Description |
|---|--------|--------------|-------|---------------|-------------|
| 1 | `tmp_max_ave` | `TMPMX` | °C | -30 to 50 | Mean daily maximum air temperature for the month. |
| 2 | `tmp_min_ave` | `TMPMN` | °C | -40 to 40 | Mean daily minimum air temperature for the month. |
| 3 | `tmp_max_sd` | `TMPSTDMX` | °C | 0.1 to 100 | Standard deviation of daily maximum air temperature in the month. |
| 4 | `tmp_min_sd` | `TMPSTDMN` | °C | 0.1 to 30 | Standard deviation of daily minimum air temperature in the month. |
| 5 | `pcp_ave` | `PCPMM` | mm | 0 to 600 | Mean total precipitation for the month. |
| 6 | `pcp_sd` | `PCPSTD` | mm/day | 0.1 to 50 | Standard deviation of daily precipitation in the month, with dry days included. |
| 7 | `pcp_skew` | `PCPSKW` | - | 0.2 to 20 | Skew coefficient of daily precipitation in the month, with dry days included. Values below 0.2 are replaced by 0.2. |
| 8 | `wet_dry` | `PR_WD` | fraction | 0 to 0.95 | Probability of a wet day following a dry day in the month. |
| 9 | `wet_wet` | `PR_WW` | fraction | 0 to 0.95 | Probability of a wet day following a wet day in the month. |
| 10 | `pcp_days` | `PCPD` | days | 0 to 31 | Mean number of days with precipitation in the month. |
| 11 | `pcp_hhr` | `RAINHMX` | mm | 0 to 125 | Largest 0.5-hour rainfall in the month over the `rain_yrs` years of record. |
| 12 | `slr_ave` | `SOLARAV` | MJ/m²/day | 0 to 40 | Mean daily solar radiation for the month. |
| 13 | `dew_ave` | `DEWPT` | °C or fraction | -50 to 25 | Mean daily dew point temperature for the month, or mean relative humidity as a fraction. |
| 14 | `wnd_ave` | `WINDAV` | m/s | 0 to 100 | Mean daily wind speed for the month. |

The statistics count a day as wet when it has more than 0 mm of precipitation. During the run, the generator counts a day as wet, for the next day's wet-day probability, when it has at least 0.1 mm.

### Checks and derived values

SWAT+ checks and completes the monthly values for each generator station when it reads the file.

**Wet-day probabilities and wet days.** If `wet_wet` is not greater than `wet_dry`, or `wet_dry` is 0 or less, the two probabilities are estimated from `pcp_days` (at least 0.1 day):

$$P(W/D) = 0.75\,\frac{d_{wet}}{N}, \qquad P(W/W) = 0.25 + P(W/D)$$

where $d_{wet}$ is `pcp_days` and $N$ the number of days in the month. Otherwise `pcp_days` is not used as given and is recalculated from the probabilities:

$$d_{wet} = \frac{N\,P(W/D)}{1 - P(W/W) + P(W/D)}$$

**Mean precipitation per wet day.** The generator draws daily amounts around $\mu = \mathrm{pcp\_ave} / d_{wet}$. `pcp_ave` must therefore be the mean monthly total. A mean daily value in this column makes generated precipitation far too small.

**Dew point or humidity.** If all twelve `dew_ave` values are between 0 and 1, they are taken as relative humidity (fraction). If any value is outside that range, all twelve are taken as dew point temperature in °C.

**Half-hour rainfall.** `pcp_hhr` is smoothed over three months (the month and its two neighbours, December and January wrapping round) and turned into the mean fraction of daily rain that falls in the wettest half hour:

$$\alpha_{0.5} = \mathrm{adj\_pkr}\left[1 - \exp\left(\frac{\bar{R}_{0.5}}{\mu\,\ln\left(\dfrac{0.5}{\mathrm{rain\_yrs}\; d_{wet}}\right)}\right)\right]$$

limited to 0.1 to 0.95, where $\bar{R}_{0.5}$ is the smoothed `pcp_hhr` and `adj_pkr` is the peak rate adjustment factor (`adj_pkrt` in the [`parameters.bsn`](parameters-bsn.md) header). Each day's fraction is drawn at random around this monthly value and is used for peak runoff rates, erosion and the generated distribution of rain within the day.

The generator equations themselves are described in [Climate and weather](../model-theory/climate-weather.md#weather-generator).

### Example

Start of `refdata/Ames_sub1/weather-wgn.cli` in the SWAT+ repository:

```
weather-wgn.cli: Ames
wgn001      37.48     -100.83   887.00    10
   TMPMX   TMPMN  TMPSTDMX TMPTDMN  PCPMM  PCPSTD  PCPSKW   PR_WD   PR_WW   PCPD  RAINHMX SOLARAV  DEWPT   WINDAV
    7.61   -8.13    8.06    5.99     7.4     3.3    0.19    0.07    0.25    2.65     5.1   10.39   -8.14    5.71
   11.07   -5.53    8.06    5.34    10.2     5.1    2.67    0.08    0.27    2.86     1.8   13.41   -5.58    6.03
   15.22   -1.87    7.99    5.22    28.1     8.9    1.64    0.11    0.34    4.43     7.6   17.85   -4.71    6.83
...
```

One generator station, `wgn001`, at 37.48° N and 887 m, with 10 years of half-hour rainfall record; ten more monthly lines follow. The January skew of 0.19 is raised to 0.2. The `DEWPT` values go below 0, so the column is read as dew point temperature.

## Observed data lists

`pcp.cli`, `tmp.cli`, `slr.cli`, `hmd.cli`, `wnd.cli` and `pet.cli` all have the same layout: a title line, a header line (SWAT+ Editor writes `filename`), and one data file name per line. Each name is both the file to open and the name that the matching column of `weather-sta.cli` refers to. Every file listed is read, whether or not a station uses it.

| List | `weather-sta.cli` column | Records in each data file | Units |
|------|--------------------------|---------------------------|-------|
| `pcp.cli` | `pcp` | year, day, precipitation (or six values for sub-daily data) | mm ([`*.pcp`](pcp.md)) |
| `tmp.cli` | `tmp` | year, day, maximum, minimum temperature | °C ([`*.tmp`](tmp.md)) |
| `slr.cli` | `slr` | year, day, solar radiation | MJ/m²/day |
| `hmd.cli` | `hmd` | year, day, relative humidity | fraction, 0 to 1 |
| `wnd.cli` | `wnd` | year, day, wind speed | m/s, at 10 m height |
| `pet.cli` | `wnd_dir` | year, day, potential evapotranspiration | mm |

Example, `refdata/Osu_1hru/pcp.cli`:

```
pcp.cli: Precipitation file names - file written by SWAT+ editor 2023-03-22 04:22:29.020522
filename
Imsilpcp.pcp
```

### Solar radiation, humidity, wind and PET files

These data files have the layout of a daily [precipitation file](pcp.md#format): a title line, a header line (`nbyr tstep lat lon elev`), a gauge line with those five values, and one record per day with year, day of year (called `jday` in earlier documentation) and the value. Only `nbyr` is used from the gauge line. The records follow the same rules for order, storage, values of -97 or less, and days outside the record as daily precipitation. A missing solar radiation, humidity or wind value is generated from the weather generator station.

Relative humidity is limited to 0.01 to 0.99 every day after it is read or generated, so a file in percent gives 0.99 on every day. Solar radiation below 0 is set to 0.

### Observed PET

A PET file is read when it is listed in `pet.cli`, and a station uses it when its `wnd_dir` column names it. With `pet` = 3 in [`codes.bsn`](codes-bsn.md#pet-method), HRUs take their potential evapotranspiration from the station. In 62.0.1 the station value is replaced by a Hargreaves estimate (at least 0.01 mm) later in the same daily step, for every station, so the values in the PET files do not reach the HRUs and `pet` = 3 gives Hargreaves PET. A missing PET value is also replaced by a Hargreaves estimate. Channel and reservoir evaporation and aquifer revap use the same station value under every `pet` setting.

## atmodep.cli

Atmospheric deposition of ammonium and nitrate, as average annual, monthly or yearly values for one or more stations. Earlier documentation calls this file `atmo.cli`. The deposition values are in this file; it does not point to data files. The `atmo_dep` column of [`codes.bsn`](codes-bsn.md) is not used; the time step comes from this file.

Line 1 is a title and line 2 a column header; both are skipped. Line 3 is the control line:

| # | Column | Description |
|---|--------|-------------|
| 1 | `num_sta` | Number of deposition stations in the file. |
| 2 | `timestep` | `aa` average annual, `mo` monthly, `yr` yearly. |
| 3 | `mo_init` | First month of the series (1 to 12). Used with `mo`. |
| 4 | `yr_init` | First year of the series. Used with `mo` and `yr`. |
| 5 | `num_aa` | Number of months (`mo`) or years (`yr`) in each series. Not used with `aa`. |

Each station then takes five lines:

| Line | Contents | Units |
|------|----------|-------|
| 1 | Station name, referenced by the `atmo_dep` column of `weather-sta.cli`. | - |
| 2 | Ammonium concentration in rain. | mg N/L |
| 3 | Nitrate concentration in rain. | mg N/L |
| 4 | Ammonium dry deposition. | kg N/ha per year (`aa`, `yr`) or per month (`mo`) |
| 5 | Nitrate dry deposition. | kg N/ha per year (`aa`, `yr`) or per month (`mo`) |

With `aa` each of lines 2 to 5 has one value. With `mo` or `yr` each has `num_aa` values, one per month or year from `mo_init`/`yr_init` on.

### Daily deposition

Every day, each HRU receives in its top soil layer, for ammonium and nitrate separately,

$$N_{wet} = 0.01\,C\,P, \qquad N_{dry} = \frac{D}{365} \;\; (\texttt{aa}, \texttt{yr}), \qquad N_{dry} = \frac{D}{N_{mo}} \;\; (\texttt{mo})$$

where $N_{wet}$ and $N_{dry}$ are in kg N/ha, $C$ is the concentration in rain (mg/L), $P$ the HRU precipitation for the day (mm), $D$ the dry deposition value and $N_{mo}$ the number of days in the month.

### Monthly and yearly series

SWAT+ starts the series at the entry for the first month or year of the simulation. If the series starts later than the simulation, deposition begins when its first month or year is reached. Before the series starts and after its last entry, HRUs receive no deposition. The entry used moves on at the last day of each month (`mo`) or year (`yr`), so the last day of a month already uses the next month's values.

When the series starts before the simulation and `mo_init` is not 1, the first entry used is `mo_init` - 1 months later than the simulation start month, and the whole series is shifted by that amount.

### Deposition stations

A weather station with `atmo_dep` set to `null`, or to a name not in the file, uses a built-in station. With `aa` this station gives 1.0 mg/L ammonium and 0.2 mg/L nitrate in rain and no dry deposition. With `mo` or `yr` the built-in station has no series, and its values are undefined; give every weather station a deposition station in that case.

### Example

Average annual deposition for one station:

```
atmodep.cli
num_sta  timestep  mo_init  yr_init  num_aa
      1        aa        0        0       0
station_001
1.0
0.2
0.0
0.0
```

## Salt and constituent deposition

Wet and dry deposition of salt ions and of other constituents, used with the [salt](salt.md) and [constituent](cs.md) inputs. Both files have fixed names and are read from the project folder only when `atmodep.cli` is present and the corresponding ions or constituents are defined in [`constituents.cs`](../input-reference/cs.md#constituentscs). They have no control line: the number of stations, the time step and the series length come from `atmodep.cli`. Stations are matched by position, so they must be in the same order as in `atmodep.cli`.

### salt_atmo.cli

The first six lines are skipped. For each station:

- a line with the station name,
- one line per salt ion, in the order of [`constituents.cs`](../input-reference/cs.md#constituentscs), with the ion label followed by the concentration in rain (mg/L), one value for `aa` or `num_aa` values for `mo` and `yr`,
- one line per salt ion with the ion label followed by the dry deposition, in the same units as nitrogen dry deposition.

### cs_atmo.cli

The first three lines are skipped. For each station:

- a station line, which is read as a number, so it must contain a number such as the station's position (a text name stops the run with a read error),
- one line per constituent with the concentration in rain (mg/L), without a label,
- one line per constituent with the dry deposition, without a label.

For both files, the daily amounts are calculated as for nitrogen and added to the top soil layer.

## Related files

- [`file.cio`](file-cio.md): names the climate files and the data path prefixes.
- [`hru.con` and the other connect files](con.md): assign a weather station to each object in the `wst` column.
- [`*.pcp`](pcp.md), [`*.tmp`](tmp.md), [`*.tem`](tem.md): observed precipitation and temperature.
- [`time.sim`](time-sim.md): simulation period and number of steps per day.
- [`codes.bsn`](codes-bsn.md): PET method and `lapse` switch.
- [`parameters.bsn`](parameters-bsn.md): lapse rates and `adj_pkrt`.
- [Salt inputs](salt.md) and [constituent inputs](cs.md): ion and constituent lists for the deposition files.
- [Climate and weather](../model-theory/climate-weather.md): weather generator and PET methods.

??? quote "Sources"

    - File name slots: `type input_cli` and the `in_path_*` types in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Type definitions: `weather_station`, `weather_codes_station_char`, `weather_generator_db`, `climate_measured_data`, `atmospheric_deposition`, `atmospheric_deposition_control` in [`climate_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_module.f90)
    - `weather-sta.cli`: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90); name lookup [`search.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/search.f90); station lookup from connect files [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90)
    - `weather-wgn.cli`: [`cli_wgnread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_wgnread.f90), [`cli_initwgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_initwgn.f90), [`cli_clgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_clgen.f90), [`cli_tgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tgen.f90)
    - Observed data lists: [`cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pmeas.f90), [`cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tmeas.f90), [`cli_smeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_smeas.f90), [`cli_hmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_hmeas.f90), [`cli_wmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_wmeas.f90), [`cli_petmeas.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_petmeas.f90)
    - Daily climate step, missing values, PET recalculation and humidity limits: [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90); HRU PET [`et_pot.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_pot.f90)
    - `atmodep.cli`: [`cli_read_atmodep.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_read_atmodep.f90), [`cli_atmodep_time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_atmodep_time_control.f90), [`nut_nrain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nrain.f90)
    - `salt_atmo.cli` and `cs_atmo.cli`: [`cli_read_atmodep_salt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_read_atmodep_salt.f90), [`cli_read_atmodep_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_read_atmodep_cs.f90), [`salt_rain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_rain.f90), [`cs_rain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_rain.f90)
    - `atmo_dep` code in `codes.bsn`: `bsn_cc%atmo` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `weather-sta.cli` | `name` | `wst(i)%name` |
    | `weather-sta.cli` | `wgn` | `wst(i)%wco_c%wgn` |
    | `weather-sta.cli` | `pcp` | `wst(i)%wco_c%pgage` |
    | `weather-sta.cli` | `tmp` | `wst(i)%wco_c%tgage` |
    | `weather-sta.cli` | `slr` | `wst(i)%wco_c%sgage` |
    | `weather-sta.cli` | `hmd` | `wst(i)%wco_c%hgage` |
    | `weather-sta.cli` | `wnd` | `wst(i)%wco_c%wgage` |
    | `weather-sta.cli` | `wnd_dir` | `wst(i)%wco_c%petgage` |
    | `weather-sta.cli` | `atmo_dep` | `wst(i)%wco_c%atmodep` |
    | `weather-wgn.cli` | `name` | `wgn_n(i)` |
    | `weather-wgn.cli` | `rain_yrs` | `wgn(i)%rain_yrs` |
    | `weather-wgn.cli` | `tmp_max_ave`, `tmp_min_ave` | `wgn(i)%tmpmx`, `wgn(i)%tmpmn` |
    | `weather-wgn.cli` | `tmp_max_sd`, `tmp_min_sd` | `wgn(i)%tmpstdmx`, `wgn(i)%tmpstdmn` |
    | `weather-wgn.cli` | `pcp_ave`, `pcp_sd`, `pcp_skew` | `wgn(i)%pcpmm`, `wgn(i)%pcpstd`, `wgn(i)%pcpskw` |
    | `weather-wgn.cli` | `wet_dry`, `wet_wet`, `pcp_days` | `wgn(i)%pr_wd`, `wgn(i)%pr_ww`, `wgn(i)%pcpd` |
    | `weather-wgn.cli` | `pcp_hhr` | `wgn(i)%rainhmx` |
    | `weather-wgn.cli` | `slr_ave`, `dew_ave`, `wnd_ave` | `wgn(i)%solarav`, `wgn(i)%dewpt`, `wgn(i)%windav` |
    | observed lists | file name | `pcp_n`, `tmp_n`, `slr_n`, `hmd_n`, `wnd_n`, `petm_n` and `%filename` |
    | `atmodep.cli` | control line | `atmodep_cont%num_sta`, `%timestep`, `%mo_init`, `%yr_init`, `%num` |
    | `atmodep.cli` | `aa` lines 2 to 5 | `atmodep(i)%nh4_rf`, `%no3_rf`, `%nh4_dry`, `%no3_dry` |
    | `atmodep.cli` | `mo` lines 2 to 5 | `atmodep(i)%nh4_rfmo`, `%no3_rfmo`, `%nh4_drymo`, `%no3_drymo` |
    | `atmodep.cli` | `yr` lines 2 to 5 | `atmodep(i)%nh4_rfyr`, `%no3_rfyr`, `%nh4_dryyr`, `%no3_dryyr` |

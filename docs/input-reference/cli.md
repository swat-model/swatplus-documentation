---
title: "*.cli (climate index files)"
description: Index files that name the weather stations, generators, and per-variable climate inputs SWAT+ should use.
status: review
verified_against:
  - src/cli_staread.f90
  - src/cli_wgnread.f90
  - src/cli_pmeas.f90
  - src/cli_tmeas.f90
  - src/cli_smeas.f90
  - src/cli_hmeas.f90
  - src/cli_wmeas.f90
  - src/cli_petmeas.f90
  - src/cli_read_atmodep.f90
  - src/cli_read_atmodep_cs.f90
  - src/cli_read_atmodep_salt.f90
  - src/input_file_module.f90
  - src/climate_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

The `.cli` files are index files. Each one names a set of climate inputs that SWAT+ should load. They sit between [`file.cio`](../input-reference/file-cio.md), which names the index files themselves, and the actual time series files (`*.pcp`, `*.tmp`, `*.slr`, `*.hmd`, `*.wnd`, `*.pet`, weather-generator stations, atmospheric deposition).

The full set of index files is defined by `type input_cli` in `src/input_file_module.f90`:

| Slot | Default name | Reader | Purpose |
|------|--------------|--------|---------|
| `weat_sta` | `weather-sta.cli` | `cli_staread.f90` | Weather stations: one row per station, columns are pointers to a `wgn` station and to per-variable gages. |
| `weat_wgn` | `weather-wgn.cli` | `cli_wgnread.f90` | Weather generator parameters: location plus 12 monthly statistics. |
| `pet_cli`  | `pet.cli`         | `cli_petmeas.f90` | List of measured PET station files. |
| `pcp_cli`  | `pcp.cli`         | `cli_pmeas.f90` | List of measured precipitation station files. |
| `tmp_cli`  | `tmp.cli`         | `cli_tmeas.f90` | List of measured temperature station files. |
| `slr_cli`  | `slr.cli`         | `cli_smeas.f90` | List of measured solar radiation station files. |
| `hmd_cli`  | `hmd.cli`         | `cli_hmeas.f90` | List of measured relative humidity station files. |
| `wnd_cli`  | `wnd.cli`         | `cli_wmeas.f90` | List of measured wind speed station files. |
| `atmo_cli` | `atmodep.cli`     | `cli_read_atmodep.f90` | Atmospheric N deposition: control record plus one or more stations. |

In `file.cio` the slot value is either a filename or the literal token `null`. Every reader skips its work when the slot is `null` or when the file does not exist. The per-variable readers (`pcp.cli`, `tmp.cli`, `slr.cli`, `hmd.cli`, `wnd.cli`, `pet.cli`) all have the same shape: title, header, then one filename per line. The actual time-series files are documented separately.

All readers skip a title line and a header line at the top of the file. Records are list-directed (free format), so columns are separated by whitespace.

## weather-sta.cli

One record per weather station. Each row binds a station name to a weather generator and to gage names for each climate variable.

### Source

- Reader: [`src/cli_staread.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_staread.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type weather_station` (column 1) and `type weather_codes_station_char` (columns 2 to 9)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: 9 fields per record, list-directed.

The reader call is `read (107,*,iostat=eof) wst(i)%name, wst(i)%wco_c`. The fields of `wco_c` are filled in declaration order.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | name    | char(50) | Weather station name. Referenced by [`hru.con`](../input-reference/con.md) and other spatial-object files. |
| 2 | wgn     | char(50) | Name of the weather generator station in `weather-wgn.cli`. |
| 3 | pgage   | char(50) | Name of the precipitation gage in `pcp.cli`, or `sim` to generate. |
| 4 | tgage   | char(50) | Name of the temperature gage in `tmp.cli`, or `sim` to generate. |
| 5 | sgage   | char(50) | Name of the solar radiation gage in `slr.cli`, or `sim` to generate. |
| 6 | hgage   | char(50) | Name of the relative humidity gage in `hmd.cli`, or `sim` to generate. |
| 7 | wgage   | char(50) | Name of the wind speed gage in `wnd.cli`, or `sim` to generate. |
| 8 | petgage | char(50) | Name of the measured PET station in `pet.cli`, or `null`. |
| 9 | atmodep | char(50) | Name of the atmospheric deposition station in `atmodep.cli`, or `null`. |

Each gage name is matched against the station list of the corresponding `.cli` file. A missing match (and a value other than `sim` for the generated variables, or `null` for pet/atmodep) is written to the error log at unit 9001.

### Example

`refdata/Ames_sub1/weather-sta.cli`:

```
weather-sta.cli: 
name                           wgn               pcp                tmp                slr              hmd             wnd         wnd_dir          atmo_dep  
wgn_sta1                   wgn_001            ames.pcp           ames.tem              sim              sim             sim            null              null  
```

The header column at position 8 is labelled `wnd_dir` by SWAT+ Editor. The reader stores that value in `petgage` (the PET gage slot).

## weather-wgn.cli

One record per weather generator station. Each record is a station header line plus a 12-row monthly statistics block.

### Source

- Reader: [`src/cli_wgnread.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_wgnread.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type weather_generator_db`

### Format

- Line 1: title (skipped).
- Per station, 14 lines:
  - Line A: station name, latitude, longitude, elevation, rain_yrs.
  - Line B: header for the monthly block (skipped).
  - Lines C1..C12: one line per month, 14 values each.

Number of stations is determined by reading to end of file.

Station header line:

| # | Field    | Type      | Units    | Description |
|---|----------|-----------|----------|-------------|
| 1 | name     | char      | -        | Generator station name. Matched by `wgn` in `weather-sta.cli`. |
| 2 | lat      | real      | degrees  | Latitude of the generator station. |
| 3 | long     | real      | degrees  | Longitude of the generator station. |
| 4 | elev     | real      | m        | Elevation of the generator station. |
| 5 | rain_yrs | real      | years    | Number of years of record used to compute `rainhmx`. |

Monthly block, 12 rows (Jan to Dec), 14 columns:

| # | Field    | Type | Units      | Description |
|---|----------|------|------------|-------------|
| 1 | tmpmx    | real | deg C      | Average daily maximum air temperature. |
| 2 | tmpmn    | real | deg C      | Average daily minimum air temperature. |
| 3 | tmpstdmx | real | deg C      | Standard deviation of daily maximum air temperature. |
| 4 | tmpstdmn | real | deg C      | Standard deviation of daily minimum air temperature. |
| 5 | pcpmm    | real | mm         | Total precipitation in the month. |
| 6 | pcpstd   | real | mm/day     | Standard deviation of daily precipitation. |
| 7 | pcpskw   | real | none       | Skew coefficient of daily precipitation. |
| 8 | pr_wd    | real | none       | Probability of a wet day after a dry day. |
| 9 | pr_ww    | real | none       | Probability of a wet day after a wet day. |
| 10 | pcpd    | real | days       | Average number of days of precipitation in the month. |
| 11 | rainhmx | real | mm         | Maximum 0.5-hour rainfall in the month. |
| 12 | solarav | real | MJ/m^2/day | Average daily solar radiation. |
| 13 | dewpt   | real | deg C      | Average daily dew point temperature. |
| 14 | windav  | real | m/s        | Average daily wind speed. |

### Example

`refdata/Ames_sub1/weather-wgn.cli`:

```
weather-wgn.cli: Ames                          
wgn001      37.48     -100.83   887.00    10
   TMPMX   TMPMN  TMPSTDMX TMPTDMN  PCPMM  PCPSTD  PCPSKW   PR_WD   PR_WW   PCPD  RAINHMX SOLARAV  DEWPT   WINDAV
    7.61   -8.13    8.06    5.99     7.4     3.3    0.19    0.07    0.25    2.65     5.1   10.39   -8.14    5.71
   11.07   -5.53    8.06    5.34    10.2     5.1    2.67    0.08    0.27    2.86     1.8   13.41   -5.58    6.03
   15.22   -1.87    7.99    5.22    28.1     8.9    1.64    0.11    0.34    4.43     7.6   17.85   -4.71    6.83
   21.42    4.12    6.42    4.82    32.0     7.9    1.65    0.14    0.34    5.25    24.6    21.7    0.93    6.84
   25.97    9.93    5.68    4.29    83.7    12.4    1.71    0.21    0.42    8.24    26.9   23.09    7.81    6.44
   31.78   15.51    4.96    3.62    71.6    13.0     0.9    0.17    0.41    6.71    40.4   26.15   12.49    6.65
   34.28   18.34    3.68    2.51    65.0    12.4    1.25    0.18    0.33    6.56    37.3   25.85   14.72    6.01
   33.17   17.22    3.89    2.59    65.0    13.0    1.26    0.19    0.27     6.4    32.0   22.54   14.29     5.9
   29.04   12.36    5.12    4.25    43.5    13.5    3.71    0.13    0.31    4.76    18.0   20.32    9.38    6.24
   23.43    5.54    6.17    4.63    29.8    11.9    1.31    0.08    0.32    3.26    10.4   15.04    3.48    6.01
   14.34   -1.71    6.76    4.75    20.1     6.9    0.58    0.09    0.34     3.6    10.4   15.46   -2.96    5.95
    9.17   -6.26    7.09    5.01     8.0     3.6    1.24    0.07    0.24    2.61    16.3    9.76   -6.38    5.87
```

This file holds one generator station (`wgn001`).

## pcp.cli

List of measured precipitation station files. Each row points to one `*.pcp` file in the project directory (or under the path set by `in_path_pcp%pcp`).

### Source

- Reader: [`src/cli_pmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_pmeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`pcp` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.pcp` time-series file. The same string is used as the station key (`pcp_n(i)`) that `weather-sta.cli` matches against. |

The reader makes two passes over the file. The first pass reads the field into `pcp_n(i)` (the lookup name). The second pass reads the same field into `pcp(i)%filename` and opens that file.

### Example

`refdata/Ames_sub1/pcp.cli`:

```
pcp.cli 
FILENAME
ames.pcp 
```

One station, file `ames.pcp` in the project directory.

## tmp.cli

List of measured temperature station files.

### Source

- Reader: [`src/cli_tmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_tmeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`tmp` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.tmp` time-series file. Used as the station key (`tmp_n(i)`). |

Optional weather path prefix from `in_path_tmp%tmp` (see `file.cio`).

### Example

`refdata/Ames_sub1/tmp.cli`:

```
tmp.cli
FILENAME
ames.tmp 
```

## slr.cli

List of measured solar radiation station files.

### Source

- Reader: [`src/cli_smeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_smeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`slr` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.slr` time-series file. Used as the station key (`slr_n(i)`). |

### Example

```
slr.cli
FILENAME
ames.slr
```

The reference dataset `refdata/Ames_sub1` does not ship a `slr.cli` because the weather-station rows use `sim` for solar radiation. The example shape above is what the reader expects when the file is present.

## hmd.cli

List of measured relative humidity station files.

### Source

- Reader: [`src/cli_hmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_hmeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`hmd` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.hmd` time-series file. Used as the station key (`hmd_n(i)`). |

### Example

```
hmd.cli
FILENAME
ames.hmd
```

## wnd.cli

List of measured wind speed station files.

### Source

- Reader: [`src/cli_wmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_wmeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`wnd` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.wnd` time-series file. Used as the station key (`wnd_n(i)`). |

### Example

```
wnd.cli
FILENAME
ames.wnd
```

## pet.cli

List of measured potential ET station files. Used when [`codes.bsn`](../input-reference/codes-bsn.md) sets `pet = 3`.

### Source

- Reader: [`src/cli_petmeas.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_petmeas.f90)
- Type: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type climate_measured_data` (`petm` array)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one field per record.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | filename | char(50) | Name of a `*.pet` time-series file. Used as the station key (`petm_n(i)`). |

### Example

```
pet.cli
FILENAME
ames.pet
```

## atmodep.cli

Atmospheric N deposition for one or more stations. Unlike the per-variable index files, this file contains the deposition values themselves, not pointers to data files.

### Source

- Reader: [`src/cli_read_atmodep.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_read_atmodep.f90)
- Types: [`src/climate_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/climate_module.f90), `type atmospheric_deposition_control` (line 3) and `type atmospheric_deposition` (per-station block)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Line 3: control record, 5 fields.
- Then, per station, a block whose layout depends on `timestep`.

Control record (line 3):

| # | Field    | Type    | Description |
|---|----------|---------|-------------|
| 1 | num_sta  | int     | Number of deposition stations to read. |
| 2 | timestep | char(2) | `aa` (average annual, scalar values), `mo` (monthly time series), or `yr` (annual time series). |
| 3 | mo_init  | int     | First month of the time series (1 to 12). Used when `timestep = mo`. |
| 4 | yr_init  | int     | First year of the time series. Used for `mo` and `yr`. |
| 5 | num      | int     | Number of records per station (length of the time series). Set to `1` for `aa`. |

For `timestep = aa`, each station occupies 5 lines:

| Line | Type | Description |
|------|------|-------------|
| 1 | char(50) | Station name (used as `atmo_n(i)`). |
| 2 | real     | `nh4_rf`  - average annual ammonia concentration in rainfall (mg/L). |
| 3 | real     | `no3_rf`  - average annual nitrate concentration in rainfall (mg/L). |
| 4 | real     | `nh4_dry` - average annual ammonia dry deposition (kg/ha/yr). |
| 5 | real     | `no3_dry` - average annual nitrate dry deposition (kg/ha/yr). |

For `timestep = mo`, each station occupies 5 lines (name plus four monthly series of length `num`):

| Line | Description |
|------|-------------|
| 1 | Station name. |
| 2 | `nh4_rfmo(1..num)` - ammonia in rainfall by month (mg/L). |
| 3 | `no3_rfmo(1..num)` - nitrate in rainfall by month (mg/L). |
| 4 | `nh4_drymo(1..num)` - ammonia dry deposition by month (kg/ha/yr). |
| 5 | `no3_drymo(1..num)` - nitrate dry deposition by month (kg/ha/yr). |

For `timestep = yr`, each station occupies 5 lines (name plus four annual series of length `num`):

| Line | Description |
|------|-------------|
| 1 | Station name. |
| 2 | `nh4_rfyr(1..num)` - ammonia in rainfall by year (mg/L). |
| 3 | `no3_rfyr(1..num)` - nitrate in rainfall by year (mg/L). |
| 4 | `nh4_dryyr(1..num)` - ammonia dry deposition by year (kg/ha/yr). |
| 5 | `no3_dryyr(1..num)` - nitrate dry deposition by year (kg/ha/yr). |

When `num_sta = 0` (no stations) or the file is named `null` in `file.cio` or absent, the reader allocates an empty array and skips deposition.

### Example

Minimal `aa` form, one station:

```
atmodep.cli
num_sta  timestep  mo_init  yr_init  num
      1        aa        1     2000    1
station_001
1.0
0.2
0.0
0.0
```

## Atmospheric deposition

Three readers populate the atmospheric deposition state. They share the per-station list set up by `atmodep.cli` and the control record `atmodep_cont` (`type atmospheric_deposition_control`). The three files cover N, salts, and other constituents.

### atmodep.cli (nitrogen)

Documented above. Read by [`src/cli_read_atmodep.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_read_atmodep.f90). Fills `atmodep(0:num_sta)` (`type atmospheric_deposition`) with NH4 and NO3 wet (rainfall) concentrations and dry deposition rates. The reader also computes `atmodep_cont%ts` (the index into the time series corresponding to the first simulation step) for `mo` and `yr` time steps, and sets `atmodep_cont%first = 0` once aligned.

### salt_atmo.cli (salt ions)

Read by [`src/cli_read_atmodep_salt.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_read_atmodep_salt.f90) when `cs_db%num_salts > 0`. Per-station wet and dry deposition for each salt ion in `constituents.cs`. Filled into `atmodep_salt(iadep)%salt(isalt)` (`type atmospheric_deposition_cs` within `type object_deposition_cs`).

Layout:

- Lines 1 to 6: skipped. The reader consumes six lines as commentary before processing stations.
- Per station, block layout depends on `atmodep_cont%timestep` (set by `atmodep.cli`):

For `timestep = aa`:

| Line | Description |
|------|-------------|
| 1 | Station name (character, ignored for cross-matching; positional). |
| 2..1+num_salts | `salt_ion_label`, then one real: `rf` (rainfall concentration, mg/L) for each ion. |
| ...next num_salts | `salt_ion_label`, then one real: `dry` (dry deposition, kg/ha/yr) for each ion. |

For `timestep = mo`:

| Line | Description |
|------|-------------|
| 1 | Station name. |
| 2..1+num_salts | `salt_ion_label`, then `num` reals: monthly wet concentrations (mg/L). |
| ...next num_salts | `salt_ion_label`, then `num` reals: monthly dry deposition (kg/ha/yr). |

For `timestep = yr`: same shape as monthly with annual series of length `num`.

When the file exists, the reader sets the module-level flag `salt_atmo = "y"`. When `cs_db%num_salts = 0` or the file is missing, salt deposition is skipped.

### cs_atmo.cli (other constituents)

Read by [`src/cli_read_atmodep_cs.f90`](https://github.com/swat-model/swatplus/blob/main/src/cli_read_atmodep_cs.f90) when `cs_db%num_cs > 0`. Same shape as `salt_atmo.cli` but without per-ion labels.

Layout:

- Lines 1 to 3: skipped.
- Per station:

For `timestep = aa`:

| Line | Description |
|------|-------------|
| 1 | Station name (real-typed scratch read; positional). |
| 2..1+num_cs | One real per line: wet concentration (mg/L) for each constituent. |
| ...next num_cs | One real per line: dry deposition (kg/ha) for each constituent. |

For `timestep = mo` and `timestep = yr`, each constituent gets one line of `num` reals for wet, and one line of `num` reals for dry, in the same order as `constituents.cs`.

When the file exists, the reader sets `cs_atmo = "y"`.

## Related files

- [`file.cio`](../input-reference/file-cio.md). Names every `.cli` file via `type input_cli`.
- [`codes.bsn`](../input-reference/codes-bsn.md). `pet = 3` triggers reading `pet.cli`.
- `*.pcp`, `*.tmp`, `*.slr`, `*.hmd`, `*.wnd`, `*.pet`. The actual time-series files listed in the per-variable `.cli` files.
- [`salt module`](../input-reference/salt.md), [`cs module`](../input-reference/cs.md). Define the salt and other-constituent lists that drive `salt_atmo.cli` and `cs_atmo.cli`.

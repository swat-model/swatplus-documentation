---
title: "*.cha (legacy channel)"
description: Legacy channel input files. Pointer files and parameter tables for the original SWAT-style reach routing and the SWAT+ deg variant.
status: review
verified_against:
  - src/input_file_module.f90
  - src/ch_read.f90
  - src/ch_read_init.f90
  - src/ch_read_temp.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_read.f90
  - src/channel_data_module.f90
  - src/sd_channel_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

This page documents the legacy channel input files: `channel.cha` (original reach pointer), `channel-lte.cha` (SWAT+ deg routing pointer), `hyd-sed-lte.cha` (combined hydrology and sediment table used by the deg routine), `initial.cha` (initial-state pointer), and `temperature.cha` (water temperature parameters). All file names are set in `type input_cha` in `src/input_file_module.f90`. Each file is independently optional: if the slot in `file.cio` is `null` or the file is missing, the reader allocates an empty array and skips on.

The three companion tables that these pointer files reference (`hydrology.cha`, `sediment.cha`, `nutrients.cha`) are documented on the [sd_channel page](../input-reference/sd-channel.md).

## Source

- File names: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_cha`
- Readers:
  - [`src/ch_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read.f90) (`channel.cha`)
  - [`src/sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/sd_channel_read.f90) (`channel-lte.cha`)
  - [`src/sd_hydsed_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/sd_hydsed_read.f90) (`hyd-sed-lte.cha`)
  - [`src/ch_read_init.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read_init.f90) (`initial.cha`)
  - [`src/ch_read_temp.f90`](https://github.com/swat-model/swatplus/blob/main/src/ch_read_temp.f90) (`temperature.cha`)
- Type definitions: [`src/channel_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/channel_data_module.f90), [`src/sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/sd_channel_module.f90)

Every reader skips two header lines, then reads one record per channel definition.

## channel.cha

Pointer file for the original SWAT-style reach routing. Each record names a channel and points to entries in `initial.cha`, `hydrology.cha`, `sediment.cha`, and `nutrients.cha`. Read into `ch_dat_c` (`type channel_data_char_input`).

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | id   | int  | record number (echoed back) |
| 2 | name | char(16) | channel name |
| 3 | init | char(16) | name of an `initial.cha` entry, or `null` |
| 4 | hyd  | char(16) | name of a `hydrology.cha` entry, or `null` |
| 5 | sed  | char(16) | name of a `sediment.cha` entry, or `null` |
| 6 | nut  | char(16) | name of a `nutrients.cha` entry, or `null` |

After reading, the reader resolves each character pointer to an integer index by scanning `ch_init`, `ch_hyd`, `ch_sed`, and `ch_nut`. Missing names are written to the diagnostics file (unit 9001) with messages like `"<name> not found (hydrology.cha)"`. The reader does not abort; the index is left at 0 and downstream code uses the default record.

No example dataset shipping with SWAT+ uses `channel.cha`. The two reference datasets at `refdata/Osu_1hru` and (if present) `refdata/Ames_sub1` configure this slot as `null` in `file.cio` and use `channel-lte.cha` instead.

## channel-lte.cha

Pointer file for SWAT+ deg routing. Listed under `chandeg.con`. Each record points to entries in `initial.cha`, `hyd-sed-lte.cha`, an optional sediment table, and `nutrients.cha`. Read into `sd_dat` (`type swatdeg_datafiles`).

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | id      | int  | record number used to position the array element |
| 2 | name    | char(16) | channel name |
| 3 | cha_ini | char(16) | name of an `initial.cha` entry, or `null` |
| 4 | cha_hyd | char(16) | name of a `hyd-sed-lte.cha` entry, or `null` |
| 5 | cha_sed | char(16) | name of a sediment-nutrient entry (resolved against `sed_nut.cha` when present) |
| 6 | cha_nut | char(16) | name of a `nutrients.cha` entry, or `null` |

The `cha_hyd` column is matched against names in both `sd_chd` (`hyd-sed-lte.cha`) and `sd_chd1` (`sed_nut.cha`). The `cha_sed` column is read but not resolved to an index by `sd_channel_read`; sediment behaviour follows the `hyd-sed-lte.cha` parameters.

Example from `refdata/Osu_1hru/channel-lte.cha`:

```
channel-lte.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                       cha_ini           cha_hyd           cha_sed           cha_nut
       1  cha01                     initcha1          hydcha01              null           nutcha1
       2  cha03                     initcha1          hydcha03              null           nutcha1
       3  cha04                     initcha1          hydcha04              null           nutcha1
```

## hyd-sed-lte.cha

Combined hydrology and bank-erosion parameters for the SWAT+ deg routing routine. One record per channel hydrology profile. Read into `sd_chd` (`type swatdeg_hydsed_data`).

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(25) | none | "" | parameter set name (referenced by `channel-lte.cha`) |
| 2 | order | int | none | 0 | stream order |
| 3 | chw | real | m | 0.0 | channel width |
| 4 | chd | real | m | 0.0 | channel depth |
| 5 | chs | real | m/m | 0.0 | channel slope |
| 6 | chl | real | km | 0.0 | channel length |
| 7 | chn | real | none | 0.0 | channel Manning's n |
| 8 | chk | real | mm/hr | 0.0 | channel bottom hydraulic conductivity |
| 9 | bank_exp | real | none | 0.0 | bank erosion exponent (column `erod_fact` in editor output) |
| 10 | cov | real | 0..1 | 0.0 | channel cover factor |
| 11 | sinu | real | none | 0.0 | sinuosity (channel length / straight-line length) |
| 12 | vcr_coef | real | none | 0.0 | critical velocity coefficient (column `eq_slp` in editor output) |
| 13 | d50 | real | mm | 0.0 | median sediment diameter |
| 14 | ch_clay | real | percent | 0.0 | clay percent of bank and bed |
| 15 | carbon | real | percent | 0.0 | carbon percent of bank and bed |
| 16 | ch_bd | real | t/m^3 | 0.0 | dry bulk density |
| 17 | chss | real | none | 0.0 | channel side slope |
| 18 | bankfull_flo | real | m^3/s | 0.0 | bank-full flow rate (column `bed_load` in editor output) |
| 19 | fps | real | m/m | 0.000001 | flood plain slope |
| 20 | fpn | real | none | 0.1 | flood plain Manning's n |
| 21 | n_conc | real | mg/kg | 0.0 | nitrogen concentration in channel bank |
| 22 | p_conc | real | mg/kg | 0.0 | phosphorus concentration in channel bank |
| 23 | p_bio | real | fraction | 0.0 | fraction of bank P that is bioavailable |

Example from `refdata/Osu_1hru/hyd-sed-lte.cha`:

```
hyd-sed-lte.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                         order            wd            dp           slp           len          mann             k     erod_fact      cov_fact        wd_rto        eq_slp           d50          clay        carbon        dry_bd      side_slp      bed_load           fps           fpn        n_conc        p_conc         p_bio  description
hydcha01                         4      27.17726       0.99164       0.00146       3.42760       0.05000       5.00000       0.01000       0.00500      27.40638       0.00100      12.00000      50.00000       0.04000       1.00000       0.50000       0.50000       0.00001       0.10000       0.00000       0.00000       0.00000
```

Editor column names differ from source field names. The reader uses position only.

## initial.cha

Initial state pointer file. Each record names a set of initial-condition files for organic-mineral mass, pesticides, pathogens, heavy metals, and salts. Read into `ch_init` (`type channel_init_datafiles`).

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | name    | char(16) | initial-state set name |
| 2 | org_min | char(16) | initial organic-mineral input file name, or `null` |
| 3 | pest    | char(16) | initial pesticide input file name, or `null` |
| 4 | path    | char(16) | initial pathogen input file name, or `null` |
| 5 | hmet    | char(16) | initial heavy metals input file name, or `null` |
| 6 | salt    | char(16) | initial salt input file name, or `null` |

The reader uses unformatted list-directed reads with no leading integer id column. The record is read directly into the derived type, so the first token on each line is the `name`.

Example from `refdata/Osu_1hru/initial.cha`:

```
initial.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description
initcha1                   no_init              null              null              null              null  null
```

A separate file `initial.cha_cs` is read by `ch_read_init_cs` for salt and conservative-species initial conditions. The file name is hard-coded in the reader (not in `type input_cha`).

## temperature.cha

Water temperature parameters used by the channel temperature routine. Read into `w_temp` (`type water_temperature_data`). The `name` field is `character(len=13)` in the source; longer names will be truncated.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(13) | none | "" | parameter set name |
| 2 | sno_mlt | real | none | 1.0 | coefficient on snowmelt temperature contribution |
| 3 | gw | real | none | 1.0 | coefficient on groundwater temperature contribution |
| 4 | sur_lat | real | none | 1.0 | coefficient on surface and lateral flow temperature contribution |
| 5 | sno_lag | real | days | 2.0 | air temperature lag to snowmelt (1..3) |
| 6 | gw_lag | real | days | 250.0 | air temperature lag to groundwater flow (200..365) |
| 7 | surf_lag | real | days | 5.0 | air temperature lag to surface runoff (2..5) |
| 8 | lat_lag | real | days | 10.0 | air temperature lag to lateral flow (5..10) |
| 9 | lat_lag_coef | real | none | 0.75 | lateral air-lag coefficient |
| 10 | surf_lag_coef | real | none | 0.75 | surface air-lag coefficient (also used for snow) |
| 11 | gw_lag_coef | real | none | 0.75 | groundwater air-lag coefficient |
| 12 | hex_coef1 | real | none | 0.75 | dew point calibration |
| 13 | hex_coef2 | real | none | 1.5 | channel geometry calibration |
| 14 | sf_on | int | none | 0 | shade factor file activation. `1` = read from file, `0` = use value from calibration file |
| 15 | ssff | real | 0..1 | 0.5 | shade factor value (used when `sf_on = 0`) |

No example dataset in `refdata/` contains `temperature.cha`. The slot is `null` in `file.cio` for the included reference datasets.

## Related files

- [`file.cio`](../input-reference/file-cio.md). The `channel` line selects which of these files are read.
- [`chandeg.con`](../input-reference/con.md). Connectivity file that references `channel-lte.cha` entries by name.
- [`channel.con`](../input-reference/con.md). Connectivity file that references `channel.cha` entries by name.
- [sd_channel companion tables (`hydrology.cha`, `sediment.cha`, `nutrients.cha`)](../input-reference/sd-channel.md).

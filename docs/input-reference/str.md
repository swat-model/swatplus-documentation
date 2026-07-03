---
title: structural BMPs
description: Structural best-management-practice files: tile drains, septic systems, filter strips, grassed waterways, user-defined BMPs, urban areas.
status: review
verified_against:
  - src/input_file_module.f90
  - src/sdr_read.f90
  - src/sep_read.f90
  - src/septic_parm_read.f90
  - src/scen_read_filtstrip.f90
  - src/scen_read_grwway.f90
  - src/scen_read_bmpuser.f90
  - src/sat_buff_read.f90
  - src/urban_parm_read.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

This page documents the structural BMP parameter files referenced by HRUs and landscape units: `tiledrain.str`, `septic.str`, `filterstrip.str`, `grassedww.str`, and `bmpuser.str`. File names for the first five are set in `type input_structural` in `src/input_file_module.f90`. The page also covers two closely related files declared elsewhere: `septic.sep` (effluent quality, named in `type input_parameter_databases`), `urban.urb` (urban land-cover parameters, same type), and `satbuffer.str` (saturated buffer, file name hard-coded in the reader).

Each file is optional. If the slot in `file.cio` is `null` or the file is missing, the reader allocates a zero-length array and skips on. Every reader skips two header lines, then reads one record per parameter set.

Records in `tiledrain.str`, `filterstrip.str`, `grassedww.str`, and `bmpuser.str` are referenced by name from `hru-data.hru` (columns `tiledrain`, `vfsfield`, `grassww`, `bmpuser`). Records in `septic.str` are referenced from the management schedule when a septic operation is scheduled.

## Source

- File names: [`src/input_file_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/input_file_module.f90), `type input_structural`, `type input_parameter_databases`
- Readers:
  - [`src/sdr_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/sdr_read.f90) (`tiledrain.str`)
  - [`src/sep_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/sep_read.f90) (`septic.str`)
  - [`src/septic_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/septic_parm_read.f90) (`septic.sep`)
  - [`src/scen_read_filtstrip.f90`](https://github.com/swat-model/swatplus/blob/main/src/scen_read_filtstrip.f90) (`filterstrip.str`)
  - [`src/scen_read_grwway.f90`](https://github.com/swat-model/swatplus/blob/main/src/scen_read_grwway.f90) (`grassedww.str`)
  - [`src/scen_read_bmpuser.f90`](https://github.com/swat-model/swatplus/blob/main/src/scen_read_bmpuser.f90) (`bmpuser.str`)
  - [`src/sat_buff_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/sat_buff_read.f90) (`satbuffer.str`)
  - [`src/urban_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/urban_parm_read.f90) (`urban.urb`)

## tiledrain.str

Subsurface drain parameter sets. Read into `sdr` (`type subsurface_drainage_parameters` in `src/hru_module.f90`). Referenced by the `tiledrain` column of `hru-data.hru`.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "null" | parameter set name |
| 2 | depth | real | mm | 0.0 | depth of drain tube from soil surface |
| 3 | time | real | hours | 0.0 | time to drain soil to field capacity |
| 4 | lag | real | hours | 0.0 | drain tile lag time |
| 5 | radius | real | mm | 0.0 | effective radius of drains |
| 6 | dist | real | mm | 0.0 | distance between two drain tubes or tiles |
| 7 | drain_co | real | mm/day | 0.0 | drainage coefficient |
| 8 | pumpcap | real | mm/hr | 0.0 | pump capacity |
| 9 | latksat | real | none | 0.0 | multiplication factor for lateral saturated hydraulic conductivity |

Example from `refdata/Osu_1hru/tiledrain.str`:

```
tiledrain.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                        dp          t_fc           lag           rad          dist         drain          pump      lat_ksat  
mw24_1000           1000.00000      24.00000      96.00000     100.00000      30.00000      10.00000       1.00000       2.00000
```

Editor column names (`dp`, `t_fc`, `rad`, `drain`, `pump`, `lat_ksat`) differ from source field names. The reader uses position only.

## septic.str

Per-HRU septic system parameter sets (geometry, biozone properties, decay coefficients). Read into `sep` (`type septic_system` in `src/septic_data_module.f90`).

| # | Column | Type | Units | Description |
|---|--------|------|-------|-------------|
| 1 | name | char(13) | none | parameter set name |
| 2 | typ | int | none | septic system type |
| 3 | yr | int | year | year the septic system became operational |
| 4 | opt | int | none | operation flag (1 = active, 2 = failing, 0 = not operated) |
| 5 | cap | real | none | number of permanent residents |
| 6 | area | real | m^2 | average drainfield area per septic system |
| 7 | tfail | int | days | time until failing system gets fixed |
| 8 | z | real | mm | depth to top of biozone layer |
| 9 | thk | real | mm | thickness of biozone layer |
| 10 | strm_dist | real | km | distance to stream |
| 11 | density | real | per km^2 | number of septic systems per square kilometre |
| 12 | bd | real | kg/m^3 | density of biomass |
| 13 | bod_dc | real | m^3/day | BOD decay rate coefficient |
| 14 | bod_conv | real | none | mass conversion factor between bacterial growth and BOD degraded |
| 15 | fc1 | real | none | linear coefficient for biozone field capacity |
| 16 | fc2 | real | none | exponential coefficient for biozone field capacity |
| 17 | fecal | real | m^3/day | fecal coliform decay rate coefficient |
| 18 | plq | real | none | plaque conversion factor from TDS |
| 19 | mrt | real | none | mortality rate coefficient |
| 20 | rsp | real | none | respiration rate coefficient |
| 21 | slg1 | real | none | slough-off calibration parameter |
| 22 | slg2 | real | none | slough-off calibration parameter |
| 23 | nitr | real | none | nitrification rate coefficient |
| 24 | denitr | real | none | denitrification rate coefficient |
| 25 | pdistrb | real | L/kg | linear P sorption distribution coefficient |
| 26 | psorpmax | real | mg P/kg soil | maximum P sorption capacity |
| 27 | solpslp | real | none | slope of linear effluent soluble P equation |
| 28 | solpintc | real | none | intercept of linear effluent soluble P equation |

Example from `refdata/Osu_1hru/septic.str`:

```
septic.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   typ        yr  operation     residents          area    t_fail       dp_bioz      thk_bioz      cha_dist      sep_dens       bm_dens     bod_decay      bod_conv        fc_lin        fc_exp   fecal_decay      tds_conv          mort          resp       slough1       slough2           nit         denit        p_sorp    p_sorp_max      solp_slp      solp_int  
standard                 1         0         0       2.50000     100.00000        70     500.00000      50.00000       0.50000       1.50000    1000.00000       0.50000       0.32000      30.00000       0.80000       1.30000       0.10000       0.50000       0.16000       0.30000       0.50000       1.50000       0.32000     128.00000     850.00000       0.04000       3.10000
failing                  1         0         0       2.50000     100.00000         1     500.00000      50.00000       0.50000       1.50000    1000.00000       0.50000       0.32000      30.00000       0.80000       1.30000       0.10000       0.50000       0.16000       0.30000       0.50000       1.50000       0.32000     128.00000     850.00000       0.04000       3.10000
```

## septic.sep

Effluent quality database. One record per effluent type. Records are referenced by index from elsewhere (no name resolution in the reader). Read into `sepdb` (`type septic_db` in `src/septic_data_module.f90`). File name is in `in_parmdb%septic_sep`.

| # | Column | Type | Units | Description |
|---|--------|------|-------|-------------|
| 1 | sepnm | char(20) | none | effluent set name |
| 2 | qs | real | m^3/day | flow rate per capita |
| 3 | bodconcs | real | mg/L | biological oxygen demand |
| 4 | tssconcs | real | mg/L | total suspended solids |
| 5 | nh4concs | real | mg/L | NH4-N concentration |
| 6 | no3concs | real | mg/L | NO3-N concentration |
| 7 | no2concs | real | mg/L | NO2-N concentration |
| 8 | orgnconcs | real | mg/L | organic N concentration |
| 9 | minps | real | mg/L | mineral P concentration |
| 10 | orgps | real | mg/L | organic P concentration |
| 11 | fcolis | real | mg/L | fecal coliform concentration |

The source comment on `nh4concs` reads "concentration of total phosphorus"; the field is the NH4-N concentration based on column position and downstream use. Example from `refdata/Osu_1hru/septic.sep` (first two records shown):

```
septic.sep: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    q_rate           bod           tss         nh4_n         no3_n         no2_n         org_n         min_p         org_p         fcoli  description
gcon                   0.22700     170.00000      75.00000      42.40000       0.00000       0.00000      10.00000       6.00000       1.00000  10000000.00000  1Generic
gadv                   0.22700      22.00000      14.00000      18.90000       9.60000       0.00000       3.00000       5.10000       0.90000     543.00000  2Generic
```

## filterstrip.str

Vegetative filter strip parameter sets. Read into `filtstrip_db` (`type filtstrip_operation` in `src/mgt_operations_module.f90`). Referenced by the `vfsfield` column of `hru-data.hru`.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "" | parameter set name |
| 2 | vfsi | int | none | 0 | on/off flag for vegetative filter strip |
| 3 | vfsratio | real | none | 0.0 | drainage-area to filter-strip-area ratio |
| 4 | vfscon | real | none | 0.0 | fraction of total runoff from the entire field |
| 5 | vfsch | real | none | 0.0 | fraction of flow entering the most concentrated 10% of the VFS that is fully channelized |

Example from `refdata/Osu_1hru/filterstrip.str`:

```
filterstrip.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag       fld_vfs       con_vfs         cha_q  description
field_border             0       0.10000       0.00300       0.20000  Field_border
high_engineered          0       0.10000       0.00100       0.05000  Highly_engineered_low_channelized
```

## grassedww.str

Grassed waterway parameter sets. Read into `grwaterway_db` (`type grwaterway_operation` in `src/mgt_operations_module.f90`). Referenced by the `grassww` column of `hru-data.hru`.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "" | parameter set name |
| 2 | grwat_i | int | none | 0 | on/off flag for waterway simulation |
| 3 | grwat_n | real | none | 0.0 | Manning's n for grassed waterway |
| 4 | grwat_spcon | real | none | 0.0 | sediment transport coefficient |
| 5 | grwat_d | real | m | 0.0 | depth of grassed waterway |
| 6 | grwat_w | real | m | 0.0 | width of grassed waterway |
| 7 | grwat_l | real | km | 0.0 | length of grassed waterway |
| 8 | grwat_s | real | m/m | 0.0 | slope of grassed waterway |

Example from `refdata/Osu_1hru/grassedww.str`:

```
grassedww.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag          mann        sed_co            dp            wd           len           slp  description
grwway_high              0       0.05000       0.02000       1.00000       4.00000       0.50000       0.10000  Slope_>8
grwway_med               0       0.05000       0.02000       0.75000       3.00000       0.75000       0.03500  Slope_2-5
grwway_low               0       0.05000       0.02000       0.50000       2.00000       1.00000       0.01000  Slope_0-2
```

## bmpuser.str

User-defined upland BMP removal-efficiency sets. Read into `bmpuser_db` (`type bmpuser_operation` in `src/mgt_operations_module.f90`). Referenced by the `bmpuser` column of `hru-data.hru`.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | name | char(40) | none | "" | parameter set name |
| 2 | bmp_flag | int | none | 0 | on/off flag |
| 3 | bmp_sed | real | percent | 0.0 | sediment removal |
| 4 | bmp_pp | real | percent | 0.0 | particulate P removal |
| 5 | bmp_sp | real | percent | 0.0 | soluble P removal |
| 6 | bmp_pn | real | percent | 0.0 | particulate N removal |
| 7 | bmp_sn | real | percent | 0.0 | soluble N removal |
| 8 | bmp_bac | real | percent | 0.0 | bacteria removal |

Example from `refdata/Osu_1hru/bmpuser.str`:

```
bmpuser.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag       sed_eff      ptlp_eff      solp_eff      ptln_eff      soln_eff      bact_eff  description
bmpusr1                  1       0.20000       0.20000       0.20000       0.20000       0.20000       0.20000
```

Note: a second type `bmpuser_operation1` in the same module exposes a wider parameter set (surface, subsurface, tile flow and constituents). The reader populates `bmpuser_db` (`bmpuser_operation`); the wider type is not read here.

## satbuffer.str

Saturated buffer source-receiver pairs. Read into `satbuff_db` (`type saturated_buffer_parameters` in `src/hru_module.f90`). The file name is hard-coded as `"satbuffer.str"` in the reader, not listed in `type input_structural`. The file is loaded only when it exists.

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | name | char(40) | parameter set name |
| 2 | hru_src | int | source HRU contributing tile inflow |
| 3 | frac_src | real | fraction of source HRU contributing to tile flow |
| 4 | flocon_dtbl | char(40) | flow-control decision table name (resolved against `dtbl_flo`) |
| 5 | hru_rcv | int | receiving (buffer) HRU |
| 6 | lyr | int | soil layer for incoming tile flow (0 = surface) |

After reading, the reader copies the parameter set into `hru(hru_src)%sb%sb_db` and `hru(hru_rcv)%sb%sb_db`, then resolves `flocon_dtbl` against the loaded flow-control decision tables (`dtbl_flo`) to set `hru(hru_src)%sb%dtbl`.

## urban.urb

Urban land-cover parameter database (build-up, wash-off, percent impervious, urban CN). Read into `urbdb` (`type urban_db` in `src/urban_data_module.f90`). File name is in `in_parmdb%urban_urb`. Urban parameter sets are referenced from `landuse.lum` for HRUs flagged as urban.

| # | Column | Type | Units | Default | Description |
|---|--------|------|-------|---------|-------------|
| 1 | urbnm | char(16) | none | "" | urban land-cover name |
| 2 | fimp | real | fraction | 0.05 | fraction of HRU area that is impervious |
| 3 | fcimp | real | fraction | 0.05 | fraction of HRU classified as directly connected impervious |
| 4 | curbden | real | km/ha | 0.0 | curb length density |
| 5 | urbcoef | real | 1/mm | 0.0 | wash-off coefficient for removal of constituents from an impervious surface |
| 6 | dirtmx | real | kg/curb-km | 1000.0 | maximum amount of solids allowed to build up on impervious surfaces |
| 7 | thalf | real | days | 1.0 | time for solids on impervious areas to build up to half the maximum |
| 8 | tnconc | real | mg N / kg sed | 0.0 | total nitrogen concentration in suspended-solid load from impervious areas |
| 9 | tpconc | real | mg P / kg sed | 0.0 | total phosphorus concentration in suspended-solid load from impervious areas |
| 10 | tno3conc | real | mg NO3-N / kg sed | 0.0 | NO3-N concentration in suspended-solid load from impervious areas |
| 11 | urbcn2 | real | none | 98.0 | moisture condition II curve number for impervious areas |

Example from `refdata/Osu_1hru/urban.urb` (first three records shown):

```
urban.urb: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  frac_imp   frac_dc_imp      curb_den      urb_wash      dirt_max     t_halfmax     conc_totn     conc_totp     conc_no3n        urb_cn  description
urhd                   0.60000       0.44000       0.24000       0.18000     225.00000       0.75000     550.00000     223.00000       7.20000      98.00000  Residential-High Density
urmd                   0.38000       0.30000       0.24000       0.18000     225.00000       0.75000     550.00000     223.00000       7.20000      98.00000  Residential-Medium Density
urml                   0.20000       0.17000       0.24000       0.18000     225.00000       0.75000     460.00000     196.00000       6.00000      98.00000  Residential-Med/Low Density
```

## Related files

- [`file.cio`](../input-reference/file-cio.md). The `structural` and `hru_parm_db` lines select which of these files are read.
- [`hru-data.hru`](../input-reference/hru.md). References `tiledrain.str`, `filterstrip.str`, `grassedww.str`, and `bmpuser.str` by name.
- [`landuse.lum`](../input-reference/lum.md). References `urban.urb` entries for urban HRUs.

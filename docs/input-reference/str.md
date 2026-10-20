---
title: structural BMPs
description: Structural practice files (tile drains, septic systems, filter strips, grassed waterways, user-defined BMPs), the septic effluent and urban databases, and saturated buffers.
status: review
verified_against:
  - src/input_file_module.f90
  - src/proc_db.f90
  - src/sdr_read.f90
  - src/sep_read.f90
  - src/septic_parm_read.f90
  - src/scen_read_filtstrip.f90
  - src/scen_read_grwway.f90
  - src/scen_read_bmpuser.f90
  - src/sat_buff_read.f90
  - src/urban_parm_read.f90
  - src/landuse_read.f90
  - src/hru_lum_init.f90
  - src/structure_init.f90
  - src/proc_hru.f90
  - src/structure_set_parms.f90
  - src/hru_module.f90
  - src/mgt_operations_module.f90
  - src/septic_data_module.f90
  - src/urban_data_module.f90
  - src/swr_percmain.f90
  - src/swr_origtile.f90
  - src/swr_drains.f90
  - src/swr_substor.f90
  - src/smp_filter.f90
  - src/smp_grass_wway.f90
  - src/smp_bmpfixed.f90
  - src/hru_control.f90
  - src/soils_init.f90
  - src/sep_biozone.f90
  - src/sq_daycn.f90
  - src/hru_urban.f90
  - src/plant_init.f90
  - src/actions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Structural practices are field-scale conservation structures attached to a land use. Five files contain their parameter sets: `tiledrain.str`, `septic.str`, `filterstrip.str`, `grassedww.str` and `bmpuser.str`. They are named on the `structural` line of [`file.cio`](file-cio.md). Two databases on the `hru_parm_db` line belong with them: `septic.sep` (septic tank effluent quality) and `urban.urb` (urban land types). The saturated buffer file `satbuffer.str` is read from the run folder under that fixed name; it is not listed in [`file.cio`](../input-reference/file-cio.md).

Each record in a structural file has a name. A land use in [`landuse.lum`](lum.md) points to records by name in its `tile`, `sep`, `vfs`, `grww` and `bmp` columns, and an urban land use points to `urban.urb` in its `urban` column. Every HRU that uses that land use gets the practice. Write `null` in a [`landuse.lum`](../input-reference/lum.md) column for no practice. A name that is not found in the structural file is reported in `diagnostics.out` as `<landuse> <name> not found (landuse-tiledr)` (or `landuse-septic`, `landuse-fstrip`, `landuse-grassww`, `landuse-bmpuser`), and the HRU then gets no practice of that kind.

Practices can also be added during a run with the decision table actions `tile_install`, `septic_install`, `fstrip_install`, `grassww_install`, `grassww_uninstall` and `user_def_bmp`, which name a record in the matching file. See [decision tables](dtl.md).

All files are optional. If a file is missing, or named `null` in [`file.cio`](../input-reference/file-cio.md), it is treated as empty.

## File layout

All of these files share one layout. Line 1 is a title and line 2 is a column header; both are skipped. Each later line is one record, read as free-format values separated by spaces. The reader takes the values by position and ignores the header text, so every column must be present and in the order shown. Text after the last numeric column (the `description` column written by SWAT+ Editor) is ignored.

## tiledrain.str

Subsurface (tile) drain parameter sets, referenced from the `tile` column of [`landuse.lum`](../input-reference/lum.md).

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Name of the tile drain record. |
| 2 | `dp` | mm | 0 to 6000 | Depth of the drain tube below the soil surface. 0 means no drain: the HRU produces no tile flow. |
| 3 | `t_fc` | hours | 0 to 100 | Time to drain the soil to field capacity. Used only by the drawdown method (`tiledrain` = 0 in [`codes.bsn`](../input-reference/codes-bsn.md)). |
| 4 | `lag` | hours | 0 to 100 | Drain tile lag time. Tile flow is held in a lag store that releases a fraction $1 - \exp(-24/\mathrm{lag})$ each day. |
| 5 | `rad` | mm | 3 to 40 | Effective radius of the drains. DRAINMOD method only. |
| 6 | `dist` | mm | 5000 to 100000 | Distance between two drain tubes or tiles. DRAINMOD method only. |
| 7 | `drain` | mm/day | 10 to 51 | Drainage coefficient: the largest daily tile flow the drains can take. Used by both methods. |
| 8 | `pump` | mm/hr | 0 to 10 | Pump capacity for subirrigation. DRAINMOD method only. |
| 9 | `lat_ksat` | - | 0.01 to 4 | Multiplier on the saturated hydraulic conductivity of each soil layer (`k` in the soil file) to give its lateral conductivity. DRAINMOD method only. |

### Tile flow methods

Tile flow is computed only when the HRU's land use names a tile drain record with `dp` greater than 0, the soil temperature of the second layer is above 0 °C and the shallow water table is above the drains. The `tiledrain` column of [`codes.bsn`](codes-bsn.md) selects the method, and its `wtable` column selects how the water table depth is found.

With `tiledrain` = 0 (drawdown method), the water above field capacity drains at a rate set by `t_fc`:

$$q_{tile} = \frac{h_{wt} - h_d}{h_{wt}}\,(SW - FC)\,\left(1 - \exp\!\left(\frac{-24}{t_{fc}}\right)\right)$$

where $h_{wt}$ is the height of the water table above the bottom of the soil profile, $h_d$ is the height of the drains above the bottom of the profile (profile depth minus `dp`), $SW$ is the soil water content and $FC$ the water content at field capacity, all in mm. If $t_{fc}$ is below 1 hour the exponential factor is left out. The result is limited to `drain`.

With `tiledrain` = 1 (DRAINMOD method), the drainage flux comes from the Hooghoudt and Kirkham equations used in DRAINMOD, which use `rad`, `dist`, `lat_ksat`, `drain` and `pump`. When the water table is below the drains the same equations give a subirrigation flux, limited by `pump`.

In both methods the day's tile flow then passes through the lag store described under `lag`. If `lag` is 0.01 hours or less, the release fraction is zero and tile water stays in the lag store for the rest of the run.

`dist`, `rad` and `dp` enter the DRAINMOD equations together with the soil depth, all in millimetres, so `dist` must be given in millimetres. The SWAT+ Editor default record (example below) has `dist` = 30, which the model reads as 30 mm.

```
tiledrain.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                        dp          t_fc           lag           rad          dist         drain          pump      lat_ksat
mw24_1000           1000.00000      24.00000      96.00000     100.00000      30.00000      10.00000       1.00000       2.00000
```

A decision table can change the drain depth during a run with `tiledep_control` (drainage water management).

## septic.str

On-site septic system parameter sets, adapted from Siegrist et al. (2005): system type, biozone geometry, biomass properties and reaction coefficients in the biozone. A record is meant to be referenced from the `sep` column of [`landuse.lum`](../input-reference/lum.md).

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the septic system record. |
| 2 | `typ` | - | Septic system type: the record number (row position, starting at 1) of the effluent type in `septic.sep`, given as an integer. |
| 3 | `yr` | year | Year the system starts operating. 0 means it operates from the start of the simulation. |
| 4 | `operation` | - | Operation flag: 0 not operating, 1 active, 2 failing. An active system becomes failing when the biozone clogs; a failing system returns to active after `t_fail` days. |
| 5 | `residents` | - | Number of permanent residents per house. A typical US value is 2.5. |
| 6 | `area` | m² | Average drainfield area of one septic system. About 40 to 70 m² per person is usual; 100 m² for a household of 2.5. |
| 7 | `t_fail` | days | Time until a failing system is fixed (0 to 150). |
| 8 | `dp_bioz` | mm | Depth to the top of the biozone layer from the ground surface. |
| 9 | `thk_bioz` | mm | Thickness of the biozone layer, the thin soil layer under the effluent distribution chamber where pollutants are degraded by live bacteria. |
| 10 | `cha_dist` | km | Distance from the septic system to the stream. |
| 11 | `sep_dens` | per km² | Number of septic systems per square kilometre. |
| 12 | `bm_dens` | kg/m³ | Density of biomass. |
| 13 | `bod_decay` | m³/day | BOD decay rate coefficient in the biozone. |
| 14 | `bod_conv` | - | Ratio of bacterial growth to BOD degraded in the septic tank effluent. |
| 15 | `fc_lin` | - | Linear coefficient for field capacity in the biozone. |
| 16 | `fc_exp` | - | Exponential coefficient for field capacity in the biozone. |
| 17 | `fecal_decay` | m³/day | Fecal coliform decay rate coefficient. |
| 18 | `tds_conv` | - | Conversion factor for plaque from total dissolved solids. |
| 19 | `mort` | - | Mortality rate coefficient. |
| 20 | `resp` | - | Respiration rate coefficient. |
| 21 | `slough1` | - | Linear coefficient for the rate of biomass sloughing. |
| 22 | `slough2` | - | Exponential coefficient for the rate of biomass sloughing. |
| 23 | `nit` | - | Nitrification rate coefficient. |
| 24 | `denit` | - | Denitrification rate coefficient. |
| 25 | `p_sorp` | L/kg | Linear P sorption distribution coefficient. |
| 26 | `p_sorp_max` | mg P/kg soil | Maximum P sorption capacity. |
| 27 | `solp_slp` | - | Slope of the linear effluent soluble P equation. |
| 28 | `solp_int` | - | Intercept of the linear effluent soluble P equation. |

### Septic simulation in 62.0.1

In revision 62.0.1 septic systems run, but receive no effluent:

- The `sep` column of [`landuse.lum`](lum.md#septic-systems) assigns the named `septic.str` record to every HRU with that land use before the soil layers are set up. If `operation` is not 0, a biozone layer is added to the soil profile at `dp_bioz` with thickness `thk_bioz`, and from year `yr` the biozone routine runs on each day the biozone layer is above freezing. Unknown names are reported in `diagnostics.out`.
- The daily septic tank effluent volume is never computed and stays at zero. No effluent water reaches the biozone, and the effluent concentrations in `septic.sep`, which are multiplied by that volume, add no nitrogen, phosphorus or BOD to the soil. The biozone routine works only on the water and nutrients already in the layer. `residents`, `area`, `cha_dist`, `sep_dens` and the `q_rate` column of `septic.sep` are read but not used.
- The decision table action `septic_install` assigns a `septic.str` record to an HRU during the run. The biozone layer is placed only when the soils are set up at the start of the run, so an HRU that gets a septic system this way has no biozone layer.

```
septic.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   typ        yr  operation     residents          area    t_fail       dp_bioz      thk_bioz      cha_dist      sep_dens       bm_dens     bod_decay      bod_conv        fc_lin        fc_exp   fecal_decay      tds_conv          mort          resp       slough1       slough2           nit         denit        p_sorp    p_sorp_max      solp_slp      solp_int
standard                 1         0         0       2.50000     100.00000        70     500.00000      50.00000       0.50000       1.50000    1000.00000       0.50000       0.32000      30.00000       0.80000       1.30000       0.10000       0.50000       0.16000       0.30000       0.50000       1.50000       0.32000     128.00000     850.00000       0.04000       3.10000
```

## septic.sep

Septic tank effluent quality database. Each record describes the effluent of one type of on-site wastewater system (from Siegrist et al., 2005; McCray et al., 2005). A `septic.str` record selects a row by its position through `typ`.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the effluent type (for example `gcon`, generic conventional system). |
| 2 | `q_rate` | m³/capita/day | Septic tank effluent flow rate per person. McCray et al. (2005) give 0.227 as the US median. Not used. |
| 3 | `bod` | mg/L | 7-day biological oxygen demand of the effluent. Typically 170 for a conventional system. |
| 4 | `tss` | mg/L | Total suspended solids in the effluent. Typically 75 for a conventional system. |
| 5 | `nh4_n` | mg N/L | Ammonium nitrogen in the effluent. Typically 60 (17 to 78) for a conventional system. |
| 6 | `no3_n` | mg N/L | Nitrate nitrogen in the effluent. 0 to 1.94 for a conventional system. |
| 7 | `no2_n` | mg N/L | Nitrite nitrogen in the effluent. Usually very low. |
| 8 | `org_n` | mg N/L | Organic nitrogen in the effluent. 9.4 to 15 for a conventional system. |
| 9 | `min_p` | mg P/L | Mineral phosphorus in the effluent. |
| 10 | `org_p` | mg P/L | Organic phosphorus in the effluent. Typically 1 for a conventional system. |
| 11 | `fcoli` | cfu/100 mL | Fecal coliform in the effluent. Typically 1E7 for a conventional system. |

Values vary widely between system types; Table A-1 of Siegrist et al. (2005) lists them. The database distributed with SWAT+ Editor has 28 types, from generic conventional (`gcon`) and advanced (`gadv`) systems to sand filters, constructed wetlands, biofilters and textile filters.

```
septic.sep: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    q_rate           bod           tss         nh4_n         no3_n         no2_n         org_n         min_p         org_p         fcoli  description
gcon                   0.22700     170.00000      75.00000      42.40000       0.00000       0.00000      10.00000       6.00000       1.00000  10000000.00000  1Generic
gadv                   0.22700      22.00000      14.00000      18.90000       9.60000       0.00000       3.00000       5.10000       0.90000     543.00000  2Generic
```

## filterstrip.str

Vegetative filter strip parameter sets, referenced from the `vfs` column of [`landuse.lum`](../input-reference/lum.md). A filter strip is a strip of dense vegetation at the field edge that intercepts runoff from upslope. It slows overland flow so particles settle, and it infiltrates part of the runoff. The model follows White and Arnold (2009). It reduces sediment, organic N, nitrate, particulate and soluble P, and pesticides in surface runoff leaving the HRU. The runoff volume itself is not changed.

| # | Column | Units | Range used | Description |
|---|--------|-------|------------|-------------|
| 1 | `name` | - | - | Name of the filter strip record. |
| 2 | `flag` | - | 0 or 1 | On/off switch. The filter strip is simulated only when `flag` is greater than 0. |
| 3 | `fld_vfs` | ratio | above 0, up to 300 | Ratio of field area to filter strip area. Values of 30 to 60 are most common. Values above 300 are set to 300. |
| 4 | `con_vfs` | fraction | 0.1 to 0.95 | Fraction of the field runoff that enters the most concentrated 10% of the strip. Runoff is rarely spread evenly: 10% of the strip often receives 25 to 75% of the runoff. A value of 0 or less is replaced by 0.5; other values are kept between 0.1 and 0.95. |
| 5 | `cha_q` | fraction | 0 to 0.95 | Fraction of the flow in the most concentrated 10% of the strip that is fully channelized. Channelized flow passes the strip without filtering or infiltration. Values above 0.95 are set to 0.95. |

`fld_vfs` divides the field area to give the strip area, so it must be greater than 0 when the strip is switched on.

```
filterstrip.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag       fld_vfs       con_vfs         cha_q  description
field_border             0       0.10000       0.00300       0.20000  Field_border
high_engineered          0       0.10000       0.00100       0.05000  Highly_engineered_low_channelized
```

Both records in this example have `flag` = 0, so a land use pointing to either one gets no filter strip.

## grassedww.str

Grassed waterway parameter sets, referenced from the `grww` column of [`landuse.lum`](../input-reference/lum.md). A grassed waterway is a broad, shallow vegetated channel that takes runoff away from a field. The vegetation slows the flow, which protects the channel from scour and lets sediment and attached pollutants settle. SWAT+ simulates it as a trapezoidal channel with 8:1 side slopes.

| # | Column | Units | Typical range | Default used when 0 | Description |
|---|--------|-------|---------------|---------------------|-------------|
| 1 | `name` | - | - | - | Name of the grassed waterway record. |
| 2 | `flag` | - | - | - | Read but not used. The waterway is simulated whenever the land use names a record. |
| 3 | `mann` | - | 0.001 to 0.5 | 0.35 | Manning's n of the waterway. |
| 4 | `sed_co` | - | 0 to 1 | 0.005 | Sediment transport coefficient, used to compute the transport capacity of the waterway. |
| 5 | `dp` | m | 0 to 10 | 3/64 of `wd` | Depth of the waterway. |
| 6 | `wd` | m | 0 to 1000 | - | Top width of the waterway. |
| 7 | `len` | km | 0 to 10000 | square root of the HRU area | Length of the waterway. |
| 8 | `slp` | m/m | 0 to 1 | 0.75 × HRU slope | Slope of the waterway. |

Values of 0 or less in `mann`, `sed_co`, `dp`, `len` and `slp` are replaced by the defaults shown. If `dp` and `wd` together cannot form a trapezoid with 8:1 side slopes (the bottom width would be zero or negative), `dp` is reset to 3/64 of `wd`.

```
grassedww.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag          mann        sed_co            dp            wd           len           slp  description
grwway_high              0       0.05000       0.02000       1.00000       4.00000       0.50000       0.10000  Slope_>8
grwway_med               0       0.05000       0.02000       0.75000       3.00000       0.75000       0.03500  Slope_2-5
grwway_low               0       0.05000       0.02000       0.50000       2.00000       1.00000       0.01000  Slope_0-2
```

## bmpuser.str

User-defined BMP removal efficiencies, referenced from the `bmp` column of [`landuse.lum`](../input-reference/lum.md). Many conservation practices are not modelled explicitly in SWAT+ but have published removal efficiencies. This record applies fixed reductions to the loads leaving the HRU. Surface runoff volume is not reduced, which keeps the water balance closed.

| # | Column | Units | Range | Description |
|---|--------|-------|-------|-------------|
| 1 | `name` | - | - | Name of the user BMP record. |
| 2 | `flag` | - | - | Read but not used. The BMP is applied whenever the land use names a record. |
| 3 | `sed_eff` | fraction | 0 to 1 | Sediment removal. |
| 4 | `ptlp_eff` | fraction | 0 to 1 | Particulate P removal (organic P and sorbed mineral P). |
| 5 | `solp_eff` | fraction | 0 to 1 | Soluble P removal in surface runoff. |
| 6 | `ptln_eff` | fraction | 0 to 1 | Particulate (organic) N removal. |
| 7 | `soln_eff` | fraction | 0 to 1 | Soluble N removal: nitrate in surface runoff and in lateral flow. |
| 8 | `bact_eff` | fraction | 0 to 1 | Bacteria removal. Read but not used. |

Each load is multiplied by $(1 - \mathrm{eff})$, so the efficiencies are fractions: 0.2 removes 20%. A value of 20 would give a negative load.

```
bmpuser.str: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  flag       sed_eff      ptlp_eff      solp_eff      ptln_eff      soln_eff      bact_eff  description
bmpusr1                  1       0.20000       0.20000       0.20000       0.20000       0.20000       0.20000
```

## satbuffer.str

Saturated buffer links. A saturated buffer diverts part of the tile flow from a source HRU into the soil of a receiving (buffer) HRU. Each record links one source to one receiver. The file is read only if a file named `satbuffer.str` is present in the run folder.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the buffer record. |
| 2 | `hru_src` | - | Number of the source HRU whose tile flow feeds the buffer. |
| 3 | `frac_src` | fraction | Fraction of the source HRU contributing tile flow to the buffer. |
| 4 | `flocon_dtbl` | - | Name of the flow control decision table (in the flow control decision table file) that sets how much tile flow goes into the buffer. |
| 5 | `hru_rcv` | - | Number of the receiving (buffer) HRU. |
| 6 | `lyr` | - | Soil layer of the receiving HRU that takes the diverted tile flow (0 = surface). |

## urban.urb

Urban land type database, referenced from the `urban` column of [`landuse.lum`](../input-reference/lum.md). The `urb_ro` column of [`landuse.lum`](../input-reference/lum.md) selects the urban load method: `usgs_reg` (USGS regression equations) or `buildup_washoff` (build-up and wash-off of solids from impervious surfaces).

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name of the urban land type. |
| 2 | `frac_imp` | fraction | 0.05 | Fraction of the HRU area that is impervious. |
| 3 | `frac_dc_imp` | fraction | 0.05 | Fraction of the HRU area that is directly connected impervious area. |
| 4 | `curb_den` | km/ha | 0 | Curb length density. |
| 5 | `urb_wash` | 1/mm | 0 | Wash-off coefficient for removal of constituents from impervious surfaces. |
| 6 | `dirt_max` | kg/curb km | 1000 | Maximum amount of solids that can build up on impervious surfaces. |
| 7 | `t_halfmax` | days | 1 | Time for solids on impervious surfaces to build up to half of `dirt_max`. |
| 8 | `conc_totn` | mg N/kg sed | 0 | Total nitrogen concentration in suspended solids from impervious areas. |
| 9 | `conc_totp` | mg P/kg sed | 0 | Total phosphorus concentration in suspended solids from impervious areas. |
| 10 | `conc_no3n` | mg N/kg sed | 0 | Nitrate nitrogen concentration in suspended solids from impervious areas. |
| 11 | `urb_cn` | - | 98 | Curve number for impervious areas (moisture condition II). Read but not used: 62.0.1 uses a fixed curve number of 98 for impervious areas. |

With the curve number method, surface runoff from an urban HRU is a weighted mix of runoff from the pervious part (the HRU's daily curve number) and from the directly connected impervious part (curve number 98), with `frac_dc_imp` as the weight. `frac_imp` is the weight for urban sediment and nutrient loads in both urban load methods.

```
urban.urb: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                  frac_imp   frac_dc_imp      curb_den      urb_wash      dirt_max     t_halfmax     conc_totn     conc_totp     conc_no3n        urb_cn  description
urhd                   0.60000       0.44000       0.24000       0.18000     225.00000       0.75000     550.00000     223.00000       7.20000      98.00000  Residential-High Density
urmd                   0.38000       0.30000       0.24000       0.18000     225.00000       0.75000     550.00000     223.00000       7.20000      98.00000  Residential-Medium Density
```

## References

- McCray, J.E., Kirkland, S.L., Siegrist, R.L. and Thyne, G.D. (2005). Model parameters for simulating fate and transport of on-site wastewater nutrients. Ground Water 43(4), 628–639.
- Siegrist, R.L., McCray, J., Weintraub, L., Chen, C., Bagdol, J., Lemonds, P., Van Cuyk, S., Lowe, K., Goldstein, R. and Rada, J. (2005). Quantifying site-scale processes and watershed-scale cumulative effects of decentralized wastewater systems. Project No. WU-HT-00-27, National Decentralized Water Resources Capacity Development Project, Washington University, St. Louis, MO.
- White, M.J. and Arnold, J.G. (2009). Development of a simplistic vegetative filter strip model for sediment and nutrient retention at the field scale. Hydrological Processes 23, 1602–1616. doi:10.1002/hyp.7291

## Related files

- [`file.cio`](file-cio.md): the `structural` line names the five `.str` files; the `hru_parm_db` line names `urban.urb` and `septic.sep`.
- [`landuse.lum`](lum.md): points to records in all of these files.
- [`codes.bsn`](codes-bsn.md): `tiledrain` and `wtable` select the tile flow and water table methods.
- [Decision tables](dtl.md): actions that install practices or change drain depth during a run.

??? quote "Sources"

    - Readers, called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90):
        - [`sdr_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sdr_read.f90) (`tiledrain.str`)
        - [`sep_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sep_read.f90) (`septic.str`)
        - [`septic_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/septic_parm_read.f90) (`septic.sep`)
        - [`scen_read_filtstrip.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/scen_read_filtstrip.f90) (`filterstrip.str`)
        - [`scen_read_grwway.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/scen_read_grwway.f90) (`grassedww.str`)
        - [`scen_read_bmpuser.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/scen_read_bmpuser.f90) (`bmpuser.str`)
        - [`sat_buff_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sat_buff_read.f90) (`satbuffer.str`)
        - [`urban_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/urban_parm_read.f90) (`urban.urb`)
    - File name slots: `type input_structural` and `type input_parameter_databases` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)
    - Type definitions: `subsurface_drainage_parameters` and `saturated_buffer_parameters` in [`hru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_module.f90); `septic_system` and `septic_db` in [`septic_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/septic_data_module.f90); `filtstrip_operation`, `grwaterway_operation` and `bmpuser_operation` in [`mgt_operations_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operations_module.f90); `urban_db` in [`urban_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/urban_data_module.f90)
    - Name lookup and assignment to HRUs: [`landuse_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/landuse_read.f90), [`hru_lum_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lum_init.f90), [`structure_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/structure_init.f90), [`structure_set_parms.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/structure_set_parms.f90), [`plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_init.f90) (urban)
    - Tile flow: [`swr_percmain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmain.f90), [`swr_origtile.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_origtile.f90), [`swr_drains.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_drains.f90), [`swr_substor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_substor.f90)
    - Septic: [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90), [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90), [`sep_biozone.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sep_biozone.f90), [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Filter strip, waterway, user BMP: [`smp_filter.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_filter.f90), [`smp_grass_wway.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_grass_wway.f90), [`smp_bmpfixed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/smp_bmpfixed.f90)
    - Urban: [`sq_daycn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_daycn.f90), [`hru_urban.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_urban.f90)
    - Decision table actions: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `tiledrain.str` | `dp`, `t_fc`, `lag`, `rad`, `dist`, `drain`, `pump`, `lat_ksat` | `sdr%depth`, `%time`, `%lag`, `%radius`, `%dist`, `%drain_co`, `%pumpcap`, `%latksat` |
    | `septic.str` | `operation`, `residents`, `t_fail`, `dp_bioz`, `thk_bioz`, `cha_dist`, `sep_dens`, `bm_dens` | `sep%opt`, `%cap`, `%tfail`, `%z`, `%thk`, `%strm_dist`, `%density`, `%bd` |
    | `septic.str` | `bod_decay`, `fc_lin`, `fc_exp`, `fecal_decay`, `tds_conv`, `mort`, `resp`, `slough1`, `slough2` | `sep%bod_dc`, `%fc1`, `%fc2`, `%fecal`, `%plq`, `%mrt`, `%rsp`, `%slg1`, `%slg2` |
    | `septic.str` | `nit`, `denit`, `p_sorp`, `p_sorp_max`, `solp_slp`, `solp_int` | `sep%nitr`, `%denitr`, `%pdistrb`, `%psorpmax`, `%solpslp`, `%solpintc` |
    | `septic.sep` | `name`, `q_rate`, `bod`, `tss`, `nh4_n`, `no3_n`, `no2_n`, `org_n`, `min_p`, `org_p`, `fcoli` | `sepdb%sepnm`, `%qs`, `%bodconcs`, `%tssconcs`, `%nh4concs`, `%no3concs`, `%no2concs`, `%orgnconcs`, `%minps`, `%orgps`, `%fcolis` |
    | `filterstrip.str` | `flag`, `fld_vfs`, `con_vfs`, `cha_q` | `filtstrip_db%vfsi`, `%vfsratio`, `%vfscon`, `%vfsch` |
    | `grassedww.str` | `flag`, `mann`, `sed_co`, `dp`, `wd`, `len`, `slp` | `grwaterway_db%grwat_i`, `%grwat_n`, `%grwat_spcon`, `%grwat_d`, `%grwat_w`, `%grwat_l`, `%grwat_s` |
    | `bmpuser.str` | `flag`, `sed_eff`, `ptlp_eff`, `solp_eff`, `ptln_eff`, `soln_eff`, `bact_eff` | `bmpuser_db%bmp_flag`, `%bmp_sed`, `%bmp_pp`, `%bmp_sp`, `%bmp_pn`, `%bmp_sn`, `%bmp_bac` |
    | `urban.urb` | `name`, `frac_imp`, `frac_dc_imp`, `curb_den`, `urb_wash`, `dirt_max`, `t_halfmax` | `urbdb%urbnm`, `%fimp`, `%fcimp`, `%curbden`, `%urbcoef`, `%dirtmx`, `%thalf` |
    | `urban.urb` | `conc_totn`, `conc_totp`, `conc_no3n`, `urb_cn` | `urbdb%tnconc`, `%tpconc`, `%tno3conc`, `%urbcn2` |
    | `landuse.lum` | `tile`, `sep`, `vfs`, `grww`, `bmp`, `urban` | `lum%tiledrain`, `%septic`, `%fstrip`, `%grassww`, `%bmpuser`, `%urb_lu` |

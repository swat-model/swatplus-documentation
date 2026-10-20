---
title: "Channel files for chandeg channels (channel-lte.cha, hyd-sed-lte.cha, sed_nut.cha, nutrients.cha)"
description: Geometry, hydraulic, sediment and water quality parameters of the channels that SWAT+ 62.0.1 routes, the chandeg channels listed in chandeg.con.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_cha.f90
  - src/sd_channel_read.f90
  - src/sd_hydsed_read.f90
  - src/ch_read_nut.f90
  - src/sd_channel_module.f90
  - src/channel_data_module.f90
  - src/sd_hydsed_init.f90
  - src/sd_rating_curve.f90
  - src/qman.f90
  - src/command.f90
  - src/sd_channel_control3.f90
  - src/sd_channel_sediment3.f90
  - src/ch_rtmusk.f90
  - src/ch_watqual4.f90
  - src/ch_rtpest.f90
  - src/hyd_read_connect.f90
  - src/cal_parm_select.f90
  - src/actions.f90
  - src/conditions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

SWAT+ 62.0.1 routes water, sediment, nutrients and other constituents through the channels listed in [`chandeg.con`](con.md). These are often called SWAT-DEG or "lte" channels, and their outputs are the `channel_sd` files. They use these parameter files:

- `channel-lte.cha`: one row per channel, pointing by name to the other files.
- `hyd-sed-lte.cha`: channel geometry, hydraulics, bank and bed properties.
- `sed_nut.cha`: optional extra sediment and nutrient coefficients. The SWAT+ Editor does not write it.
- `nutrients.cha`: in-stream water quality (QUAL2E) rate constants.

Initial channel contents come from [`initial.cha`](cha.md#initialcha), described on the [channel group page](cha.md) together with [`temperature.cha`](../input-reference/cha.md#temperaturecha) and the legacy files [`channel.cha`](../input-reference/cha.md#channelcha), [`hydrology.cha`](../input-reference/cha.md#hydrologycha) and [`sediment.cha`](../input-reference/cha.md#sedimentcha). The legacy channel object of [`channel.con`](../input-reference/con.md) is not routed in 62.0.1, so those legacy files have no effect on the results.

## Links between the files

The `lcha` column of [`chandeg.con`](../input-reference/con.md) gives the `id` of a row in `channel-lte.cha`. That row names one row in each of the other files:

| `channel-lte.cha` column | Matched against | If the name is not found |
|---|---|---|
| `cha_ini` | `name` in [`initial.cha`](../input-reference/cha.md#initialcha) | row 1 of [`initial.cha`](../input-reference/cha.md#initialcha) |
| `cha_hyd` | `name` in `hyd-sed-lte.cha`, and `name` in `sed_nut.cha` | row 1 of each file (or the built-in values of `sed_nut.cha` when that file is absent) |
| `cha_sed` | not used | |
| `cha_nut` | `name` in `nutrients.cha` | row 1 of `nutrients.cha` |

An unmatched name writes no message to `diagnostics.out`; the channel takes row 1 without warning. Check the names before a run.

The file names of `channel-lte.cha`, `hyd-sed-lte.cha`, `nutrients.cha` and [`initial.cha`](../input-reference/cha.md#initialcha) are set on the `channel` line of [`file.cio`](file-cio.md) (slots 6, 7, 5 and 1). `sed_nut.cha` has a fixed name and is read when a file of that name is in the run folder.

## channel-lte.cha

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one channel with six values in this order.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Channel number. [`chandeg.con`](../input-reference/con.md) refers to the row by this number in its `lcha` column. |
| 2 | `name` | - | Channel name. |
| 3 | `cha_ini` | - | Name of a row in [`initial.cha`](../input-reference/cha.md#initialcha). |
| 4 | `cha_hyd` | - | Name of a row in `hyd-sed-lte.cha`, and of a row in `sed_nut.cha` when that file is used. |
| 5 | `cha_sed` | - | Read but not used. The Editor writes `null`. |
| 6 | `cha_nut` | - | Name of a row in `nutrients.cha`. |

Number the rows 1, 2, 3 and so on in file order. The row is stored under its `id`, but the name lookups are applied to the row's position in the file, so rows whose `id` differs from their position get the wrong parameter sets.

## hyd-sed-lte.cha

Free format. Two header lines are skipped, then one parameter set per line with 23 values in this order. The reader does not match columns by header name. The Editor adds a `description` header with no values under it, which the reader ignores.

Several column headers written by the Editor do not describe what SWAT+ 62.0.1 does with the value. The table gives the Editor header and the use in 62.0.1.

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Name of the parameter set, matched against `cha_hyd` in `channel-lte.cha`. |
| 2 | `order` | - | 1 to 12 | Stream order (integer). Groups channels in the `chanbud_order` output and is tested by the decision table condition `ch_order`. Use 1 to 12: values outside that range fall outside the order budget table. |
| 3 | `wd` | m | from QSWAT+ | Bankfull top width of the channel, calculated by QSWAT+ from the drainage area. |
| 4 | `dp` | m | from QSWAT+ | Bankfull depth, from the top of the bank to the channel bottom, calculated by QSWAT+ from the drainage area. |
| 5 | `slp` | m/m | from QSWAT+ | Average channel slope along its length, from the DEM. Values below 10⁻⁹ are raised to 10⁻⁶. |
| 6 | `len` | km | from QSWAT+ | Channel length. A channel of 0.001 km (1 m) or less passes its inflow through unchanged. |
| 7 | `mann` | - | 0.025 to 0.15 | Manning's n of the channel. Values below 0.01 are raised to 0.01. Chow (1959) gives about 0.03 for clean straight channels, 0.04 to 0.05 for winding channels with pools, weeds or stones, and 0.07 to 0.15 for sluggish or very weedy reaches. |
| 8 | `k` | mm/h | 0 to 130 | Effective hydraulic conductivity of the channel bed, used for transmission losses. Lane (1983) gives more than 127 mm/h for very clean gravel and large sand, 51 to 127 for clean sand and gravel, 25 to 76 for sand and gravel with little silt and clay, 6 to 25 for sand and gravel with much silt and clay, and 0.025 to 2.5 for consolidated beds with high silt and clay. Use 0 for perennial streams fed by groundwater. |
| 9 | `erod_fact` | - | - | Bank erosion exponent. Read but not used. |
| 10 | `cov_fact` | - | 0 to 1 | Channel cover factor. It adds a vegetation term to the critical velocity for bank erosion, so a larger value protects the banks more. See [Bank erosion](#bank-erosion). |
| 11 | `wd_rto` | - | 1.05 and up | Read as the channel sinuosity (channel length over straight-line length), although the header and the values the Editor writes are a width-to-depth ratio. Values below 1.05 are raised to 1.05. Used for the bend velocity in bank erosion. |
| 12 | `eq_slp` | - | about 1 | Critical velocity coefficient: a multiplier on the calculated critical velocity for bank erosion. The header name suggests an equilibrium slope; 62.0.1 has no such parameter. |
| 13 | `d50` | mm | - | Median bed sediment size. Read, but replaced by 1.0 mm at the start of every day's sediment calculation, so the value in the file has no effect. |
| 14 | `clay` | % | 0 to 100 | Clay content of bank and bed. Sets the bank cohesion. |
| 15 | `carbon` | % | 0 to 100 | Organic carbon content of the bed. Sets the pesticide sorption coefficient in the channel. |
| 16 | `dry_bd` | t/m³ | 1.1 to 1.9 | Dry bulk density of bank and bed. Converts bank and bed erosion from metres to tonnes, and sets the bed porosity for pesticide mixing. |
| 17 | `side_slp` | - | - | Channel side slope. See [Channel geometry and rating curve](#channel-geometry-and-rating-curve). |
| 18 | `bed_load` | - | - | Read as the bankfull flow multiplier, the ratio of the flow at which overbank flooding starts to the bankfull flow. Replaced by 1.5 at the start of every day's sediment calculation, so the value in the file has no effect. |
| 19 | `fps` | m/m | 0.00001 to `slp` | Lateral slope of the floodplain away from the channel (rise over run). Values above `slp` are lowered to `slp`; values of 10⁻⁶ or less are set to 10⁻⁵. |
| 20 | `fpn` | - | 0.025 to 0.16 | Manning's n of the floodplain. Chow (1959) gives 0.025 to 0.05 for pasture and cultivated land, 0.035 to 0.16 for brush and 0.08 to 0.2 for trees. |
| 21 | `n_conc` | mg/kg | - | Nitrogen content of eroded bank sediment, added to the flow as organic N. |
| 22 | `p_conc` | mg/kg | - | Phosphorus content of eroded bank sediment. |
| 23 | `p_bio` | fraction | 0 to 1 | Fraction of the bank phosphorus that enters the flow as soluble P. The rest enters as sediment-bound P. |

There are no built-in values for this file. A channel whose `cha_hyd` name is not found uses row 1. Without `hyd-sed-lte.cha` the chandeg channels have no parameters, so the file is required whenever [`chandeg.con`](../input-reference/con.md) lists channels.

## sed_nut.cha

An optional table with extra coefficients for the chandeg sediment and nutrient calculations. It is read only when a file named `sed_nut.cha` is present. Rows are matched by the same `cha_hyd` name as `hyd-sed-lte.cha`. Two header lines are skipped, then 13 values per line:

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name, matched against `cha_hyd` in `channel-lte.cha`. |
| 2 | `order` | - | - | Text field, read and not used. |
| 3 | `pk_rto` | ratio | 1.0 | Multiplier on the peak-to-mean daily flow ratio. See [Peak flow](#peak-flow). |
| 4 | `fp_inun_days` | days | 5.0 | Days the floodplain stays inundated after a flood. Replaced by 1.0 at the start of every day's sediment calculation, so neither the file value nor the built-in value has an effect. |
| 5 | `n_setl` | ratio | 0.5 | Ratio of N settling to sediment settling. Not used. |
| 6 | `p_setl` | ratio | 0.5 | Ratio of P settling to sediment settling. Not used. |
| 7 | `n_sol_part` | 1/h | 0.01 | Rate of nitrate conversion to organic N, used only with the simplified transformations. See [Nutrients](#nutrients). |
| 8 | `p_sol_part` | 1/h | 0.01 | Rate of soluble P conversion to sediment-bound P, used only with the simplified transformations. |
| 9 | `n_dep_enr` | ratio | 0.5 | Enrichment ratio for organic N deposited with sediment on the floodplain and in the channel. |
| 10 | `p_dep_enr` | ratio | 0.5 | Enrichment ratio for sediment-bound P deposited with sediment. |
| 11 | `arc_len_fr` | fraction | 1.2 | Fraction of the meander arc length where banks erode. Read but not used in the erosion mass in 62.0.1. |
| 12 | `bed_exp` | - | 1.5 | Exponent of the bed erosion equation. Replaced by 1.0 at the start of every day's sediment calculation. |
| 13 | `wash_bed_fr` | fraction | 0.1 | Fraction of bank erosion deposited in the channel bed. See [Channel deposition](#channel-deposition). |

Without `sed_nut.cha`, every channel uses the built-in values. With the file present, a channel whose name is not found uses row 1.

## nutrients.cha

Free format. Two header lines are skipped, then one parameter set per line with 39 values in this order. The reader does not match columns by header name. Every value of zero or less in the columns that have a value in the "Replacement" column is replaced by that value.

All rates are for 20 °C and are adjusted to the water temperature in the calculation. The water temperature used here is $5 + 0.75\,\bar{T}$, where $\bar{T}$ is the day's mean air temperature at the channel's weather station, with a minimum of 0.1 °C. The stream temperature from the heat balance (see [`temperature.cha`](cha.md#temperaturecha)) sets only the outflow temperature.

| # | Column | Units | Replacement | Typical range | Description |
|---|--------|-------|-------------|---------------|-------------|
| 1 | `name` | - | - | - | Name, matched against `cha_nut` in `channel-lte.cha`. |
| 2 | `plt_n` | ppm | - | 0 to 100 | Organic N concentration. Not used. |
| 3 | `ptl_p` | ppm | - | 0 to 100 | Organic P concentration, called `plt_p` in earlier documentation. Not used. |
| 4 | `alg_stl` | m/day | 1.0 | 0.15 to 1.82 | Algal settling rate. |
| 5 | `ben_disp` | mg P/m²/day | 0.05 | 0.001 to 0.1 | Benthic source rate for dissolved P. |
| 6 | `ben_nh3n` | mg N/m²/day | 0.5 | 0 to 1 | Benthic source rate for ammonium N. |
| 7 | `ptln_stl` | 1/day | 0.05 | 0.001 to 0.1 | Organic N settling rate. |
| 8 | `ptlp_stl` | 1/day | 0.05 | 0.001 to 0.1 | Organic P settling rate. |
| 9 | `cst_stl` | 1/day | 2.5 | 0.01 to 10 | Settling rate of an arbitrary non-conservative constituent. Not used. |
| 10 | `ben_cst` | mg/m²/day | 2.5 | 0.01 to 10 | Benthic source rate of an arbitrary non-conservative constituent. Not used. |
| 11 | `cbn_bod_co` | 1/day | 1.71 | 0.02 to 3.4 | CBOD deoxygenation rate. |
| 12 | `air_rt` | 1/day | 1.0 | 0 to 100 | Reaeration rate (Fickian diffusion). |
| 13 | `cbn_bod_stl` | 1/day | none | -0.36 to 0.36 | Rate of CBOD loss by settling. A value of zero or less is kept. |
| 14 | `ben_bod` | mg O₂/m²/day | 2.0 | 0 to 100 | Sediment oxygen demand. |
| 15 | `bact_die` | 1/day | 2.0 | 0.05 to 4 | Coliform die-off rate. Not used; pathogen die-off comes from the pathogen database. |
| 16 | `cst_decay` | 1/day | 1.71 | 0 to 10 | Decay rate of an arbitrary non-conservative constituent. Not used. |
| 17 | `nh3n_no2n` | 1/day | 0.55 | 0.1 to 1 | Rate of biological oxidation of NH₃ to NO₂. |
| 18 | `no2n_no3n` | 1/day | 1.1 | 0.2 to 2 | Rate of biological oxidation of NO₂ to NO₃. |
| 19 | `ptln_nh3n` | 1/day | 0.21 | 0.2 to 0.4 | Rate of hydrolysis of organic N to ammonium. |
| 20 | `ptlp_solp` | 1/day | 0.35 | 0.01 to 0.7 | Rate of mineralisation of organic P to dissolved P. |
| 21 | `q2e_lt` | - | 2 | 1 to 4 | QUAL2E light averaging option. Not used. |
| 22 | `q2e_alg` | - | 2 | 1 to 3 | Algal growth limitation: `1` multiplicative ($\mu_{max} f_L f_N f_P$), `2` limiting nutrient ($\mu_{max} f_L \min(f_N, f_P)$), `3` harmonic mean of $f_N$ and $f_P$. Integer. |
| 23 | `chla_alg` | µg chl-a/mg algae | 50 | 10 to 100 | Ratio of chlorophyll-a to algal biomass. |
| 24 | `alg_n` | mg N/mg algae | 0.08 | 0.07 to 0.09 | Fraction of algal biomass that is N. |
| 25 | `alg_p` | mg P/mg algae | 0.015 | 0.01 to 0.02 | Fraction of algal biomass that is P. |
| 26 | `alg_o2_prod` | mg O₂/mg algae | 1.6 | 1.4 to 1.8 | O₂ production per unit of algal photosynthesis. |
| 27 | `alg_o2_resp` | mg O₂/mg algae | 2.0 | 1.6 to 2.3 | O₂ uptake per unit of algal respiration. |
| 28 | `o2_nh3n` | mg O₂/mg N | 3.5 | 3 to 4 | O₂ uptake per unit of NH₃ oxidised. |
| 29 | `o2_no2n` | mg O₂/mg N | 1.07 | 1 to 1.4 | O₂ uptake per unit of NO₂ oxidised. |
| 30 | `alg_grow` | 1/day | 2.0 | 1 to 3 | Maximum specific algal growth rate. |
| 31 | `alg_resp` | 1/day | 2.5 | 0.05 to 5 | Algal respiration rate. |
| 32 | `slr_act` | fraction | 0.3 | 0 to 1 | Fraction of solar radiation that is photosynthetically active. |
| 33 | `lt_co` | kJ/m²/min | 0.75 | - | Half-saturation coefficient for light. Multiplied by 0.06 on reading, which converts kJ/m²/min to MJ/m²/h. |
| 34 | `const_n` | mg N/L | 0.02 | 0.01 to 0.3 | Michaelis-Menten half-saturation constant for N. |
| 35 | `const_p` | mg P/L | 0.025 | 0.001 to 0.05 | Michaelis-Menten half-saturation constant for P. |
| 36 | `lt_nonalg` | 1/m | 1.0 | 0 to 10 | Non-algal part of the light extinction coefficient. |
| 37 | `alg_shd_l` | 1/(m·µg chl-a/L) | 0.03 | 0.006 to 0.065 | Linear algal self-shading coefficient. |
| 38 | `alg_shd_nl` | (1/m)(µg chl-a/L)^-2/3 | 0.054 | 0 to 1 | Non-linear algal self-shading coefficient. |
| 39 | `nh3_pref` | - | 0.5 | 0 to 1 | Algal preference for ammonium over nitrate. |

Units of the half-saturation coefficient for light differ between sources: the old GitBook pages give `lt_co` in MJ/m²/h with a range of 0.223 to 1.135, while the 62.0.1 reader treats the value as kJ/m²/min and multiplies it by 0.06. A file value of 0.75 is used as 0.045 MJ/m²/h.

In sub-daily runs the reader divides the rates in columns 4 to 8, 11 to 14, 17 to 20, 30 and 31 by the number of time steps per day, while the water quality calculation still runs once per day. Sub-daily runs therefore use smaller effective rates than daily runs with the same file.

When `nutrients.cha` is missing, the chandeg channels have no water quality parameters, so keep the file in any model with channels.

## Channel geometry and rating curve

At the start of the run each channel gets a trapezoidal cross-section and a rating curve at four depths: 0.1 and 1.0 times the bankfull depth `dp`, and 1.2 and 2.0 times `dp` with water on the floodplain. Flow, velocity, area, volume and travel time at any other flow are interpolated between these points.

With top width $W$ (`wd`), bankfull depth $D$ (`dp`), side slope $z$ (`side_slp`), length $L$ (`len`, km), slope $S$ (`slp`) and roughness $n$ (`mann`), the bottom width is

$$b = W - 2\,D\,z$$

If this is zero or negative, $b$ is set to $W/2$ and $z$ is reset to $W/(4D)$. For a flow depth $d$ up to bankfull,

$$P = b + 2\,d\,\sqrt{1 + 1/z^2}, \qquad A = b\,d + d/z, \qquad R = A/P$$

$$v = \frac{R^{2/3}\,S^{1/2}}{n + 0.001}, \qquad Q = A\,v, \qquad TT = \frac{L}{3.6\,v}$$

where $P$ is the wetted perimeter (m), $A$ the flow area (m²), $v$ the velocity (m/s), $Q$ the flow (m³/s) and $TT$ the travel time (h). The channel volume is $1000\,A\,L$ (m³).

The bottom width treats `side_slp` as horizontal distance per unit rise, while the perimeter and area treat it as rise per unit horizontal distance. The side term of the area, $d/z$, is the area of two side triangles with slope $z$ (rise over run) only at $d = 1$ m. These are the expressions SWAT+ 62.0.1 uses.

Above bankfull, with $h$ the depth above the bank (0.2 $D$ and 1.0 $D$) and $s_{fp}$ the floodplain slope `fps`,

$$P = P_{bf} + 2\,h\,\sqrt{1 + 1/s_{fp}^2}, \qquad A = A_{bf} + b\,h + h^2/s_{fp}, \qquad W_{fp} = W + 2\,h/s_{fp}$$

The floodplain volume is $1000\,W_{fp}\,h\,L$, and flow and velocity use `fpn` in place of `mann`, with the channel slope `slp`.

A smaller `fps` gives a wider, flatter floodplain that stores more water at a given depth.

## Flow routing

Each day the inflow from upstream objects is first increased by any water allocation transfer into the channel, aquifer flow from [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin), gwflow exchange when [gwflow](gwflow.md) is active, and, on days with inflow, precipitation on the channel surface ($P\,L\,W$ m³, with $P$ in mm, $L$ in km and $W$ in m). Water is then routed with one of two methods, chosen by `rte_cha` in [`codes.bsn`](codes-bsn.md).

### Variable storage method

With `rte_cha` = 0, the outflow in each time step is a fraction of the stored water:

$$O = c\,V_{stor}, \qquad c = \min\!\left(1,\ \frac{2\,s_c\,\Delta t}{2\,TT + \Delta t}\right)$$

where $s_c$ is `scoef` in [`parameters.bsn`](parameters-bsn.md), $\Delta t$ the time step (h) and $TT$ the travel time (h) at the previous step's outflow rate.

### Muskingum method

With `rte_cha` = 1, outflow follows the Muskingum equation

$$O_2 = C_1 I_2 + C_2 I_1 + C_3 O_1$$

The storage constant is a weighted mean of the travel times at bankfull and 0.1 bankfull depth, each computed with the kinematic wave celerity $5v/3$:

$$K = \frac{\mathrm{msk\_co1}\,K_{bf} + \mathrm{msk\_co2}\,K_{0.1}}{\mathrm{msk\_co1} + \mathrm{msk\_co2}}$$

With $X$ = `msk_x` (all three in [`parameters.bsn`](../input-reference/parameters-bsn.md)), the coefficients are

$$C_1 = \frac{\Delta t - 2KX}{2K(1-X) + \Delta t}, \quad C_2 = \frac{\Delta t + 2KX}{2K(1-X) + \Delta t}, \quad C_3 = \frac{2K(1-X) - \Delta t}{2K(1-X) + \Delta t}$$

$C_1$ is kept at zero or above, and the three are scaled to sum to 1. When $\Delta t > 2K(1-X)$ the coefficients are computed for a shorter sub-step that meets this limit. Sub-steps are used only in sub-daily runs; a daily run routes once per day with the sub-step coefficients.

Stored water above the bankfull channel volume is counted as floodplain storage.

### Water losses

After routing, transmission losses and evaporation are taken from the water left in the channel:

$$TL = 24\,k\,L\,W \quad (\mathrm{m^3/day}), \qquad E = \mathrm{evrch}\;PET\;L\,W$$

where $k$ is `k` (mm/h), $L$ is in km, $W$ in m, $PET$ is the potential evapotranspiration of the weather station (mm), and `evrch` is the reach evaporation factor (`evap_adj` in [`parameters.bsn`](../input-reference/parameters-bsn.md)). Both use the bankfull top width over the full channel length, and neither can exceed the stored volume. With gwflow active, gwflow also calculates an exchange with the channel; the transmission loss above is still taken from the channel, but the channel output reports it as zero seepage.

## Sediment

Sediment calculations run once per day for channels with inflow. In 62.0.1 four inputs are replaced at the start of each day's calculation: the bankfull flow multiplier by 1.5, the floodplain inundation days by 1.0, the bed `d50` by 1.0 mm and the bed erosion exponent by 1.0. The file values of `bed_load`, `d50`, `fp_inun_days` and `bed_exp`, and any calibration changes to them, therefore have no effect.

### Peak flow

The day's peak flow is

$$q_{pk} = \mathrm{pk\_rto}\left(1 + 2.66\,A_{km^2}^{-0.3}\right)\frac{Q_{day}}{86400}$$

(Fuller's equation), where $A_{km^2}$ is the `area` of the channel in [`chandeg.con`](../input-reference/con.md) converted to km² and $Q_{day}$ is the day's inflow (m³). The peak sets the velocity $v$ from the rating curve, which is used for erosion and the travel time.

### Floodplain deposition

When $q_{pk}$ exceeds 1.5 times the bankfull flow, the floodplain traps a fraction of the incoming sediment (Dynamic SedNet, 2017):

$$TE = \min\!\left(1,\ N_{inun}\,\frac{q_{fp}}{\bar{q}}\left(1 - e^{-0.0001\,A_{fp}/q_{fp}}\right)\right)$$

with $N_{inun}$ = 1 day, $q_{fp}$ the rating curve flow at the peak, $\bar{q}$ the mean daily flow (m³/s) and $A_{fp} = 5\,W\,L$ the floodplain area (m², $L$ in m). Organic N and sediment-bound P are deposited with $TE$ times `n_dep_enr` and `p_dep_enr`. Overbank water then fills wetlands of HRUs linked to the channel's floodplain up to their emergency volume.

### Bank erosion

Banks erode when the reach velocity exceeds a critical velocity. The cohesion from the clay content $C$ (`clay`, %) is

$$c = \max\!\left(1000,\ -87.1 + 42.82\,C - 0.261\,C^2 + 0.029\,C^3\right)$$

and the critical velocity is

$$v_{cr} = \mathrm{eq\_slp}\;\log_{10}(2200\,D)\,\sqrt{0.0004\left(f_{bd} + 0.021\,c + 4500\,\mathrm{cov}\,e^{-5D}\right)}$$

where $f_{bd} = \max(0.001,\ 39.24\,\rho_b - 1000)$ with $\rho_b$ the bulk density `dry_bd` (t/m³). For bulk densities below 25.5 t/m³, which covers all real sediments, $f_{bd}$ stays at 0.001, so `dry_bd` does not change $v_{cr}$.

The velocity at the bends uses the radius of curvature from the sinuosity $\sigma$ (column `wd_rto`):

$$r_c = \frac{12\,W\,\sigma^{1.5}}{13\,\sqrt{\sigma - 1}}, \qquad v_{rch} = 0.33\,v\left(1 + 1/r_c\right) + 0.66\,v$$

If $v_{rch} > v_{cr}$, the bank retreat for the day (m) is

$$e_{bank} = \left(\frac{1}{v_c} + \frac{1}{0.0002\,W}\right)^{-1}, \qquad v_c = \frac{0.0001\,A_{km^2}^{-0.0858}\,W}{1 + e^{-4\,(v_{rch}/v_{cr} - 1)}}$$

and the eroded mass is $1000\,e_{bank}\,D\,(0.25\,L)\,\rho_b$ tonnes, with $L$ in km. The bank sediment brings organic N at `n_conc` and P at `p_conc`; the fraction `p_bio` of that P is soluble.

### Channel deposition

A fraction `wash_bed_fr` of the bank erosion is deposited in the channel bed and removed from the flow, with organic N and sediment-bound P scaled by `n_dep_enr` and `p_dep_enr`.

### Bed erosion

For channels steeper than 10⁻⁶, bed erosion occurs when $v > 0.293\sqrt{d_{50}}$, which is 0.293 m/s with $d_{50}$ = 1 mm:

$$e_{bed} = 0.0001\left(\frac{v}{0.293}\right) \ \mathrm{m}, \qquad M_{bed} = 1000\,e_{bed}\,W\,L\,\rho_b \ \mathrm{t}$$

In 62.0.1, $e_{bed}$ and $M_{bed}$ appear in the channel morphology and sediment budget outputs, but the eroded bed sediment is not added to the flow.

## Nutrients

For channels with inflow, the day's water quality follows the QUAL2E kinetics with the rates of `nutrients.cha`, applied over the travel time (at most one day). This covers algae and chlorophyll-a, CBOD, dissolved oxygen, the nitrogen chain from organic N through ammonium and nitrite to nitrate, and organic and soluble P. See [Channels](../model-theory/channels.md) in the model theory.

When column 24 of [`codes.bsn`](codes-bsn.md) (headed `i_fpwet` by the Editor) is 1, a simplified transformation then replaces the organic N, nitrate, sediment-bound P and soluble P of the outflow:

$$\Delta N_{org} = \min\!\left(NO_3,\ \left(1 - e^{-k_N\,TT}\right) N_{org}\right)$$

with $k_N$ = `n_sol_part` and $TT$ the travel time (h). $\Delta N_{org}$ is added to organic N and taken from nitrate. Phosphorus follows the same form with `p_sol_part`, moving soluble P to sediment-bound P.

## Pesticides

In the channel, pesticide sorption uses $K_d = K_{oc}\,\mathrm{carbon}/100$, with $K_{oc}$ from [`pesticide.pes`](pes.md) and `carbon` from `hyd-sed-lte.cha`. The mixing velocity between water and bed uses the bed porosity $1 - \rho_b/2.65$. Pesticides and pathogens are routed only on days with inflow.

## Calibration and decision tables

Parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md) (see [parameter change files](../calibration/parameter-change-files.md)), using these names:

- `hyd-sed-lte.cha`: `chw` (`wd`), `chd` (`dp`), `chs` (`slp`), `chl` (`len`), `chn` (`mann`), `chk` (`k`), `bank_exp` (`erod_fact`), `cov` (`cov_fact`), `vcr_coef` (`eq_slp`), `d50`, `ch_clay` (`clay`), `carbon`, `ch_bd` (`dry_bd`), `chss` (`side_slp`), `bankfull_flo` (`bed_load`), `fps`, `fpn`, `ch_n_conc`, `ch_p_conc`, `ch_p_bio`.
- `sed_nut.cha`: `pk_rto`, `fp_inun_days`, `n_setl`, `p_setl`, `n_sol_part`, `p_sol_part`, `n_dep_enr`, `p_dep_enr`, `arc_len_fr`, `bed_exp`, `wash_bed_fr`.
- `nutrients.cha`: `rs1` to `rs7`, `rk1` to `rk4`, `rk6`, `bc1` to `bc4`, `mumax`. The parameter name `rk5` changes `ben_disp` (the same column as `rs2`); no calibration name changes `bact_die`.

Calibration changes are applied after the rating curve and Muskingum coefficients are set, and these are not recalculated. Changes to `chw`, `chd`, `chs`, `chn`, `chss`, `fps` and `fpn` therefore do not change the rating curve or the routing coefficients; they change only the other calculations that use the values directly (transmission losses, evaporation, erosion). Changes to `bankfull_flo`, `fp_inun_days`, `d50` and `bed_exp` are overwritten each day (see [Sediment](#sediment)). The `nutrients.cha` changes are applied to the row whose position equals the channel number.

The decision table action `chan_change` sets a channel's cover factor to the action's first constant and its stream order to the second. The condition `ch_order` tests a channel's stream order. See [decision tables](dtl.md).

## Example

`refdata/Osu_1hru` in the SWAT+ repository, first rows of each file:

```
channel-lte.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                       cha_ini           cha_hyd           cha_sed           cha_nut
       1  cha01                     initcha1          hydcha01              null           nutcha1
       2  cha03                     initcha1          hydcha03              null           nutcha1
```

```
hyd-sed-lte.cha: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name        order       wd       dp      slp      len     mann        k  erod_fact  cov_fact   wd_rto   eq_slp      d50     clay   carbon   dry_bd side_slp bed_load      fps      fpn   n_conc   p_conc    p_bio  description
hydcha01        4 27.17726  0.99164  0.00146  3.42760  0.05000  5.00000    0.01000   0.00500 27.40638  0.00100 12.00000 50.00000  0.04000  1.00000  0.50000  0.50000  0.00001  0.10000  0.00000  0.00000  0.00000
```

(columns narrowed for display)

Channel `cha01` is a fourth-order channel 27.2 m wide, 0.99 m deep and 3.43 km long, with Manning's n of 0.05 and bed conductivity of 5 mm/h. Some values in this file are read differently from what the Editor header suggests:

- `wd_rto` = 27.4 is the width-to-depth ratio, but SWAT+ reads it as a sinuosity of 27.4. The bends then have a large radius of curvature, and the bend velocity is close to the mean velocity.
- `eq_slp` = 0.001 multiplies the critical velocity for bank erosion by 0.001, so bank erosion occurs on almost every day with flow.
- `d50` = 12 and `bed_load` = 0.5 are replaced by 1.0 mm and 1.5 during the run.
- `fps` = 0.00001 gives a very flat, wide floodplain.

`nutrients.cha` in the same dataset has one set, `nutcha1`, with `air_rt` = 50 and `cbn_bod_stl` = 0.36. The other values are the replacement values in the table above, or zero for the two unused concentrations.

## Related files

- [`chandeg.con`](con.md): lists the channels and points to `channel-lte.cha` rows in its `lcha` column.
- [`initial.cha`](cha.md#initialcha): initial water, sediment and constituents in each channel, through [`om_water.ini`](ini.md), [`pest_water.ini`](pes.md), [`salt_channel.ini`](salt.md) and [`cs_channel.ini`](cs.md).
- [`temperature.cha`](cha.md#temperaturecha): stream temperature parameters.
- [`codes.bsn`](codes-bsn.md) (`rte_cha`, column 24) and [`parameters.bsn`](parameters-bsn.md) (`msk_co1`, `msk_co2`, `msk_x`, `evap_adj`, `scoef`): routing switches and coefficients.
- [`file.cio`](file-cio.md): the `channel` line names the files.
- Outputs: [channel, sediment and nutrient files](../output-reference/channel-sediment-nutrient.md) (`channel_sd`, `channel_sdmorph`, `sd_chanbud`, `ch_sedbud`, `chanbud_order`).
- [Channels](../model-theory/channels.md) and [erosion and sediment](../model-theory/erosion-sediment.md) in the model theory.

??? quote "Sources"

    - File name slots: `type input_cha` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90); read order in [`proc_cha.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cha.f90)
    - Readers: [`sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90) (`channel-lte.cha`), [`sd_hydsed_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_read.f90) (`hyd-sed-lte.cha`, `sed_nut.cha`), [`ch_read_nut.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_nut.f90) (`nutrients.cha`)
    - Type definitions: `swatdeg_datafiles`, `swatdeg_hydsed_data`, `swatdeg_sednut_data` and `swatdeg_channel_dynamic` in [`sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_module.f90); `channel_nut_data` in [`channel_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/channel_data_module.f90)
    - Initialisation, limits, rating curve and Muskingum coefficients: [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`sd_rating_curve.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_rating_curve.f90), [`qman.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/qman.f90)
    - Daily channel calculation: [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90); sediment in [`sd_channel_sediment3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_sediment3.f90); routing and losses in [`ch_rtmusk.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtmusk.f90); water quality in [`ch_watqual4.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_watqual4.f90); pesticides in [`ch_rtpest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtpest.f90)
    - `chandeg.con` pointer column: [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90); decision tables: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90), [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90)

    `channel-lte.cha`:

    | Column | Fortran variable |
    |--------|------------------|
    | `id` | index of `sd_dat` |
    | `name` | `sd_dat%name` |
    | `cha_ini` | `sd_dat%initc` -> `sd_dat%init` |
    | `cha_hyd` | `sd_dat%hydc` -> `sd_dat%hyd`, `sd_dat%sednut` |
    | `cha_sed` | `sd_dat%sedc` (unused) |
    | `cha_nut` | `sd_dat%nutc` -> `sd_dat%nut` |

    `hyd-sed-lte.cha` (copied to `sd_ch` in `sd_hydsed_init`):

    | Column | Fortran variable |
    |--------|------------------|
    | `order` | `sd_chd%order` |
    | `wd` | `sd_chd%chw` |
    | `dp` | `sd_chd%chd` |
    | `slp` | `sd_chd%chs` |
    | `len` | `sd_chd%chl` |
    | `mann` | `sd_chd%chn` |
    | `k` | `sd_chd%chk` |
    | `erod_fact` | `sd_chd%bank_exp` |
    | `cov_fact` | `sd_chd%cov` |
    | `wd_rto` | `sd_chd%sinu` |
    | `eq_slp` | `sd_chd%vcr_coef` |
    | `d50` | `sd_chd%d50` |
    | `clay` | `sd_chd%ch_clay` |
    | `carbon` | `sd_chd%carbon` |
    | `dry_bd` | `sd_chd%ch_bd` |
    | `side_slp` | `sd_chd%chss` |
    | `bed_load` | `sd_chd%bankfull_flo` |
    | `fps`, `fpn`, `n_conc`, `p_conc`, `p_bio` | `sd_chd%` same names |

    `sed_nut.cha` columns map to `sd_chd1%` components of the same names.

    `nutrients.cha`:

    | Columns | Fortran variables (`ch_nut%`) |
    |---------|-------------------------------|
    | `plt_n`, `ptl_p` | `onco`, `opco` |
    | `alg_stl` to `ben_cst` | `rs1` to `rs7` |
    | `cbn_bod_co`, `air_rt`, `cbn_bod_stl`, `ben_bod`, `bact_die`, `cst_decay` | `rk1` to `rk6` |
    | `nh3n_no2n` to `ptlp_solp` | `bc1` to `bc4` |
    | `q2e_lt`, `q2e_alg` | `lao`, `igropt` |
    | `chla_alg` to `o2_no2n` | `ai0` to `ai6` |
    | `alg_grow`, `alg_resp`, `slr_act` | `mumax`, `rhoq`, `tfact` |
    | `lt_co`, `const_n`, `const_p` | `k_l`, `k_n`, `k_p` |
    | `lt_nonalg`, `alg_shd_l`, `alg_shd_nl`, `nh3_pref` | `lambda0`, `lambda1`, `lambda2`, `p_n` |

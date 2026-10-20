---
title: Channels
description: Flow routing, transmission losses, evaporation, floodplain storage, bank and bed erosion, water quality and temperature in SWAT+ channels.
status: review
verified_against:
  - src/sd_channel_control3.f90
  - src/ch_rtmusk.f90
  - src/sd_hydsed_init.f90
  - src/sd_hydsed_read.f90
  - src/sd_channel_read.f90
  - src/sd_channel_module.f90
  - src/sd_channel_sediment3.f90
  - src/ch_watqual4.f90
  - src/ch_temp.f90
  - src/ch_read_temp.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Channels move water, sediment and dissolved and particulate constituents from upstream objects to the watershed outlet. A SWAT+ channel is defined by its geometry (width, depth, slope, length, side slope, Manning's n) in [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), from which a rating curve of depth, area, wetted perimeter, top width, velocity and travel time against flow rate is built at the start of the run.

Each day a channel:

1. adds rain falling on the channel surface to the inflow;
2. checks for overbank flow, traps sediment on the floodplain and fills floodplain wetlands;
3. computes bank and bed erosion;
4. routes the water through channel and floodplain storage;
5. removes transmission losses and evaporation;
6. runs in-stream water quality, pesticides, pathogens, salts and constituents;
7. computes water temperature.

When gwflow is active, the channel also exchanges water with the groundwater cells it crosses (see [Aquifers](aquifers.md)).

## Rating curve

The rating curve is computed for a trapezoidal main channel with a floodplain above bankfull. For a given flow rate it gives flow depth, cross-section area, wetted perimeter, hydraulic radius, velocity (Manning's equation), and travel time $TT = L / (3.6\,v)$ in hours, with $L$ the channel length (km) and $v$ the velocity (m/s).

## Flow routing

Inflow is added to channel storage on each routing step. The routing method is set by `rte_cha` in [`codes.bsn`](../input-reference/codes-bsn.md).

### Variable storage (`rte_cha = 0`, default)

$$
q_{out} = \min\left(1,\;\frac{2\,\Delta t\;C_{st}}{2\,TT + \Delta t}\right) V_{stor}
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $q_{out}$ | outflow during the step | m³ | |
| $\Delta t$ | routing step | h | |
| $TT$ | travel time at the previous step's outflow rate | h | |
| $C_{st}$ | storage coefficient multiplier | - | `scoef` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $V_{stor}$ | water in channel and floodplain storage | m³ | |

With a daily time step there is one routing step per day.

### Muskingum (`rte_cha = 1`)

$$
O_2 = C_1 I_2 + C_2 I_1 + C_3 O_1
$$

$$
C_1 = \frac{\Delta t - 2KX}{2K(1 - X) + \Delta t}, \quad C_2 = \frac{\Delta t + 2KX}{2K(1 - X) + \Delta t}, \quad C_3 = \frac{2K(1 - X) - \Delta t}{2K(1 - X) + \Delta t}
$$

$C_1$ is not allowed to fall below 0, and the three coefficients are scaled to sum to 1. The storage time constant is a weighted mean of the travel times at bankfull depth and at 0.1 × bankfull depth (using the kinematic wave celerity, 5/3 of the velocity):

$$
K = \frac{c_1\,K_{bf} + c_2\,K_{0.1bf}}{c_1 + c_2}
$$

| Symbol | Meaning | Input |
|---|---|---|
| $I$, $O$ | inflow and outflow volumes at the start (1) and end (2) of the step | |
| $K$ | storage time constant (h) | |
| $X$ | weighting factor | `msk_x` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $c_1$, $c_2$ | weights for bankfull and low flow | `msk_co1`, `msk_co2` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |

When $\Delta t$ exceeds $2K(1 - X)$, the step is divided into sub-steps so that the method stays stable.

### Floodplain storage

After each routing step, the part of storage above the bankfull channel volume becomes floodplain storage and the rest stays as channel storage. Both drain through the routing equation.

## Transmission losses and evaporation

Once a day, after routing, water is removed from channel storage:

$$
TL = 24\,K_{ch}\,L\,W, \qquad E_{ch} = \eta\,E_o\,L\,W
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $TL$ | transmission loss | m³ | |
| $K_{ch}$ | effective hydraulic conductivity of the channel bed | mm/h | `k` in [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha) |
| $L$, $W$ | channel length and bankfull width | km, m | `len`, `wd` |
| $E_{ch}$ | evaporation from the channel | m³ | |
| $\eta$ | evaporation coefficient | - | `evap_adj` in [`parameters.bsn`](../input-reference/parameters-bsn.md) |
| $E_o$ | potential evapotranspiration | mm | |

Both are limited to the water in channel storage and use the full bankfull width, whatever the flow. Transmission losses are reported as channel seepage. In SWAT, transmission losses used the wetted perimeter and could recharge the shallow aquifer; in SWAT+ the loss leaves channel storage and is not routed anywhere unless gwflow is used.

## Sediment

### Overbank flow and floodplain deposition

The daily peak flow is estimated from the mean daily inflow with a peak rate factor that decreases with drainage area:

$$
q_{pk} = r_{pk}\left[1 + 2.66\left(\frac{A}{100}\right)^{-0.3}\right]\frac{Q_{day}}{86400}
$$

where $r_{pk}$ is `pk_rto` in [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) (default 1) and $A$ the drainage area (ha). When the peak exceeds 1.5 times the bankfull flow rate, part of the sediment, organic N and particulate P is trapped on the floodplain:

$$
\varepsilon_{fp} = \min\left(1,\;\frac{q_{pk}}{\bar{q}}\left[1 - \exp\left(-10^{-4}\,\frac{A_{fp}}{q_{pk}}\right)\right]\right)
$$

with $\bar q$ the mean daily flow rate and $A_{fp}$ a floodplain area of five channel widths times the channel length (m²). Organic N and particulate P are trapped with the enrichment ratios `n_dep_enr` and `p_dep_enr`. Overbank water also fills the wetlands of HRUs that lie on the floodplain.

### Bank erosion

Banks erode when the reach velocity, raised to account for flow around bends, exceeds a critical velocity that depends on bank cohesion (from clay content), vegetation cover and bulk density:

$$
v_{cr} = c_{vcr}\,\log_{10}(2200\,D)\,\sqrt{0.0004\,(f_{bd} + 0.021\,\tau_{coh} + f_{veg})}
$$

$$
f_{veg} = 4500\,c_{cov}\,e^{-5D}, \qquad \tau_{coh} = \max\left(1000,\;-87.1 + 42.82\,cl - 0.261\,cl^2 + 0.029\,cl^3\right)
$$

The bank retreat rate (m/day) follows a logistic function of $v/v_{cr}$, scaled by channel width and a duration factor that decreases with drainage area, and limited by an exhaustion rate of $0.0002\,W$. Eroded bank mass is retreat × depth × a quarter of the channel length × bulk density. Bank material adds organic N and P at the concentrations `n_conc` and `p_conc`, with a share `p_bio` of the P as soluble P. A fraction `wash_bed_fr` of the eroded bank material is deposited in the channel; the rest moves downstream.

| Symbol | Meaning | Input |
|---|---|---|
| $D$ | bankfull depth (m) | `dp` |
| $c_{cov}$ | bank cover factor | `cov_fact` |
| $cl$ | bank clay content (%) | `clay` |
| $f_{bd}$ | bulk density factor, $\max(0.001,\;39.24\,\rho_b - 1000)$ | `dry_bd` |
| $c_{vcr}$ | critical velocity coefficient | 12th value, labelled `eq_slp` in Editor files |

### Bed erosion

Bed erosion is computed when the velocity exceeds $0.293\sqrt{d_{50}}$ m/s, as $10^{-4}(v/v_{cr})$ m/day of bed lowering. It is reported in the channel morphology output but is not added to the sediment in the flow.

## Water quality

In-stream nitrogen, phosphorus, algae, dissolved oxygen and carbonaceous BOD follow the QUAL2E kinetics (Brown and Barnwell, 1987), with rate constants from [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha). The calculation runs once a day for every channel with inflow, on the concentrations of the day's inflow.

### Temperature and solution method

Every rate is given for 20 °C and corrected to the water temperature $T_w$:

$$k_T = k_{20}\,\theta^{\,T_w - 20}, \qquad T_w = 5 + 0.75\,\bar{T}_{air}$$

with $T_w$ at least 0.1 °C and $\bar{T}_{air}$ the day's mean air temperature at the channel's weather station.

| Process | $\theta$ |
|---|---|
| Algal growth and respiration; organic N hydrolysis; nitrite oxidation; organic P mineralisation; CBOD decay | 1.047 |
| Algal, organic N and organic P settling; CBOD settling; reaeration (also used for ammonium oxidation) | 1.024 |
| Benthic P and ammonium sources | 1.074 |

The channel is treated as a mixed reach with a residence time $\tau$, the travel time through the channel in days (at most 1). For each constituent with inflow concentration $C_{in}$, a constant source or sink $M$ (mg/L/day) and a first-order rate $K$ (1/day), the outflow concentration is

$$C_{out} = C_{in}\,e^{-a} + \frac{C_{in}/\tau + M}{1/\tau - K}\left(1 - e^{-a}\right), \qquad a = \left(\frac{1}{\tau} - K\right)\Delta t$$

with $\Delta t$ = 1 day.

A first-order transformation from one constituent to another (for example organic N to ammonium) is converted into the equivalent constant term, so the mass removed from one constituent is added to the next.

### Algae

Algal biomass $A$ (mg/L) is computed from chlorophyll-a with `chla_alg`. The growth rate combines light and nutrient limitation:

$$\mu = \mu_{max}\,f_L\,f_{NP}, \qquad f_N = \frac{N}{N + K_N}, \qquad f_P = \frac{P_{sol}}{P_{sol} + K_P}$$

where $f_{NP}$ is $f_N f_P$, $\min(f_N, f_P)$ or $2/(1/f_N + 1/f_P)$ for `q2e_alg` 1, 2 or 3. The light factor averages light over the water depth $d$:

$$f_L = 0.92\,\frac{T_L}{24}\,\frac{1}{\lambda\,d}\,\ln\!\left(\frac{K_L + I}{K_L + I\,e^{-\lambda d}}\right), \qquad I = \frac{f_{PAR}\,H_{day}}{T_L}$$

| Symbol | Meaning | Input |
|---|---|---|
| $\mu_{max}$ | Maximum specific growth rate (1/day) | `alg_grow` |
| $\rho$ | Respiration rate (1/day) | `alg_resp` |
| $\sigma_1$ | Settling rate (m/day) | `alg_stl` |
| $K_N$, $K_P$ | Half-saturation constants for N and P (mg/L) | `const_n`, `const_p` |
| $K_L$ | Half-saturation constant for light (MJ/m²/h) | `lt_co` × 0.06 |
| $\lambda$ | Light extinction coefficient (1/m) | `lt_nonalg` |
| $f_{PAR}$ | Fraction of solar radiation that is photosynthetically active | `slr_act` |
| $H_{day}$ | Solar radiation of the day (MJ/m²) | weather |
| $N$ | Ammonium plus nitrate in the channel storage (mg/L) | |
| $T_L$ | Hours used as the day length (see the list below) | |

The net growth $\mu - \rho$ is the source term for algae and settling at $\sigma_1/d$ the first-order loss. Biomass is kept between 0 and 5000 mg/L. Algal growth takes up soluble P at `alg_p` per unit of biomass.

### Nitrogen, phosphorus, CBOD and oxygen

| Constituent | Sources and sinks | Inputs |
|---|---|---|
| CBOD | decay at $\kappa_1$; settling at $\kappa_3/d$ | `cbn_bod_co`, `cbn_bod_stl` |
| Organic N | hydrolysis to ammonium at $2\beta_3$; settling at $\sigma_4/d$ | `ptln_nh3n`, `ptln_stl` |
| Ammonium | gain from organic N hydrolysis; oxidation to nitrite at $\kappa_2$ | `air_rt` |
| Nitrite | gain from ammonium oxidation; oxidation to nitrate at $\beta_2$ | `no2n_no3n` |
| Nitrate | gain from nitrite oxidation | |
| Organic P | mineralisation to soluble P at $\beta_4$; settling at $\sigma_5/d$ | `ptlp_solp`, `ptlp_stl` |
| Soluble P | gain $\beta_4 P_{org} + \sigma_2/d_{ch}$; loss to algal growth | `ben_disp` |
| Dissolved oxygen | reaeration $\kappa_2 (O_{sat} - O)$; CBOD decay; $\alpha_5$ per unit of ammonium and $\alpha_6$ per unit of nitrite oxidised; a loss of $\sigma_4/d$ | `air_rt`, `o2_nh3n`, `o2_no2n` |

Soluble P is updated directly, $P_{out} = P_{in} + (\beta_4 P_{org} + \sigma_2/d_{ch} - \alpha_2\,\mu\,A)\,\tau$, with $d_{ch}$ the bankfull depth of the channel and $\alpha_2$ = `alg_p`. The oxygen saturation concentration (mg/L) depends on the water temperature $T_K$ in kelvin:

$$\ln O_{sat} = -139.34410 + \frac{1.575701\times10^{5}}{T_K} - \frac{6.642308\times10^{7}}{T_K^2} + \frac{1.243800\times10^{10}}{T_K^3} - \frac{8.621949\times10^{11}}{T_K^4}$$

Reaeration uses `air_rt` directly; the stream reaeration formulas of QUAL2E and reaeration over dams are not computed. The inflow oxygen concentration is limited to between 0.001 and 30 mg/L before the calculation.

### Behaviour in 62.0.1

Several parts of the in-stream calculation differ from QUAL2E:

- $T_L$ is the day-length threshold for plant dormancy (`dorm_hr` in [`parameters.bsn`](../input-reference/parameters-bsn.md), or a value of at most 1 hour derived from latitude), not the day length. At latitudes below 20° with `dorm_hr` = 0 it is zero or negative, the light intensity is set to almost zero, and algae do not grow.
- The extinction coefficient never exceeds `lt_nonalg`, so algal self-shading (`alg_shd_l`, `alg_shd_nl`) has no effect.
- Ammonium is oxidised at the reaeration rate `air_rt`; `nh3n_no2n` has no effect. Organic N hydrolysis uses twice `ptln_nh3n`.
- Algal uptake of ammonium and nitrate and algal oxygen production and respiration are computed but not applied.
- Sediment oxygen demand (`ben_bod`) is not taken from dissolved oxygen; the organic N settling term $\sigma_4/d$ is subtracted instead. The benthic ammonium source (`ben_nh3n`) only enters the inflow concentration used to compute ammonium oxidation.
- The benthic P source is added as `ben_disp` (mg/m²/day) divided by the depth in m, which gives mg/m³ per day, but is added to a concentration in mg/L.

When the 24th value of [`codes.bsn`](../input-reference/codes-bsn.md) is 1 (the column Editor files label `i_fpwet`; the `wq_cha` column is not used), a simplified exchange replaces the QUAL2E results for nitrate, organic N, soluble P and particulate P. Over the travel time $TT$ (h), soluble N and P are converted to particulate forms:

$$
\Delta N = \min\left(NO_3,\;\left[1 - e^{-k_N TT}\right] N_{org}\right), \qquad \Delta P = \min\left(P_{sol},\;\left[1 - e^{-k_P TT}\right] P_{sed}\right)
$$

with $k_N$ and $k_P$ from `n_sol_part` and `p_sol_part` in [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) (default 0.01).

## Water temperature

When the channel's weather station has measured temperatures, water temperature is built from:

- the flow-weighted temperature of upstream channels;
- local inflows from the routing units draining to the channel (snowmelt, surface runoff and lateral flow) and groundwater, each given the mean air temperature over its lag period (`sno_lag`, `surf_lag`, `lat_lag`, `gw_lag` days) times a coefficient;
- heat exchange with the air, using dew point, wind speed and optional shading factors, over the travel time.

Parameters are in [`temperature.cha`](../input-reference/cha.md#temperaturecha). Without measured air temperature, water temperature is $5 + 0.75\,T_{air}$.

## Parameters

| Parameter | File | Effect |
|---|---|---|
| `rte_cha` | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = variable storage; 1 = Muskingum |
| 24th value (Editor column `i_fpwet`) | [`codes.bsn`](../input-reference/codes-bsn.md) | 1 = simplified soluble to particulate N and P exchange |
| `scoef` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Variable storage coefficient multiplier |
| `msk_co1`, `msk_co2`, `msk_x` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Muskingum weights and weighting factor |
| `evap_adj` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Channel evaporation coefficient |
| `wd`, `dp`, `slp`, `len`, `mann`, `side_slp` | [`hyd-sed-lte.cha`](../input-reference/sd-channel.md) | Geometry and roughness |
| `k` | [`hyd-sed-lte.cha`](../input-reference/sd-channel.md) | Bed hydraulic conductivity for transmission losses (mm/h) |
| `cov_fact`, `clay`, `dry_bd` | [`hyd-sed-lte.cha`](../input-reference/sd-channel.md) | Bank erosion resistance |
| `n_conc`, `p_conc`, `p_bio` | [`hyd-sed-lte.cha`](../input-reference/sd-channel.md) | N and P content of eroded bank material |
| `pk_rto`, `n_dep_enr`, `p_dep_enr`, `wash_bed_fr`, `n_sol_part`, `p_sol_part` | [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) (optional) | Peak rate, floodplain enrichment, channel deposition and simplified nutrient exchange |

## Related pages

- [Channel inputs](../input-reference/sd-channel.md) and [legacy channel inputs](../input-reference/cha.md)
- [Channel, sediment and nutrient outputs](../output-reference/channel-sediment-nutrient.md)
- [Hydrology](hydrology.md), [Aquifers](aquifers.md), [Reservoirs and wetlands](reservoirs-wetlands.md)
- [Pesticides](pesticides.md), [Salts and constituents](salts-constituents.md)

??? quote "Sources"

    Code at revision 62.0.1:

    - Daily channel driver: [`src/sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90)
    - Routing, transmission loss and evaporation: [`src/ch_rtmusk.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtmusk.f90)
    - Rating curve and Muskingum coefficients: [`src/sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90), [`src/sd_rating_curve.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_rating_curve.f90), [`src/rcurv_interp_flo.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/rcurv_interp_flo.f90)
    - Sediment and floodplain: [`src/sd_channel_sediment3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_sediment3.f90)
    - Inputs: [`src/sd_hydsed_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_read.f90) (`hyd-sed-lte.cha`, `sed_nut.cha`), [`src/sd_channel_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_read.f90) (`channel-lte.cha`), types in [`src/sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_module.f90)
    - Water quality: [`src/ch_watqual4.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_watqual4.f90), with the solution in [`src/wq_semianalyt.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wq_semianalyt.f90) and [`src/wq_k2m.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wq_k2m.f90) and the temperature correction in [`src/theta.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/theta.f90). QUAL2E reference: Brown, L. C., and Barnwell, T. O. (1987), The enhanced stream water quality models QUAL2E and QUAL2E-UNCAS, EPA/600/3-87/007.
    - Water quality symbols: $\mu_{max}$, $\rho$ = `ch_nut%mumax`, `%rhoq`; $\sigma_1$ to $\sigma_5$ = `%rs1` to `%rs5`; $\kappa_1$ to $\kappa_4$ = `%rk1` to `%rk4`; $\beta_1$ to $\beta_4$ = `%bc1` to `%bc4`; $\alpha_0$ to $\alpha_6$ = `%ai0` to `%ai6`; $K_L$, $K_N$, $K_P$ = `%k_l`, `%k_n`, `%k_p`; $\lambda$ = `%lambda0`; $f_{PAR}$ = `%tfact`; $T_L$ = `wgn_pms(iwgn)%daylth`; $\tau$ = `rcurv%ttime / 24`; $d$ = `rcurv%dep`; $d_{ch}$ = `sd_chd(jrch)%chd`.
    - Temperature: [`src/ch_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_temp.f90), [`src/ch_read_temp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_temp.f90)

    Columns and variables (`hyd-sed-lte.cha` is read list-directed into `swatdeg_hydsed_data`, so position decides the variable):

    | Position | Editor column | Variable |
    |---|---|---|
    | 3 to 8 | `wd`, `dp`, `slp`, `len`, `mann`, `k` | `chw`, `chd`, `chs`, `chl`, `chn`, `chk` |
    | 9 | `erod_fact` | `bank_exp` |
    | 10 | `cov_fact` | `cov` |
    | 11 | `wd_rto` | `sinu` (sinuosity, used for the bend radius) |
    | 12 | `eq_slp` | `vcr_coef` (critical velocity coefficient) |
    | 13 to 16 | `d50`, `clay`, `carbon`, `dry_bd` | `d50`, `ch_clay`, `carbon`, `ch_bd` |
    | 17 | `side_slp` | `chss` |
    | 18 | `bed_load` | `bankfull_flo` |
    | 19 to 23 | `fps`, `fpn`, `n_conc`, `p_conc`, `p_bio` | same names |

    Other symbols: $C_{st}$ = `bsn_prm%scoef`; $X$, $c_1$, $c_2$ = `bsn_prm%msk_x`, `%msk_co1`, `%msk_co2`; $\eta$ = `bsn_prm%evrch`; $r_{pk}$ = `sd_ch%pk_rto`; `rte_cha` = `bsn_cc%rte`. `codes.bsn` is read list-directed into `basin_control_codes`, so the 24th value (Editor column `i_fpwet`) sets `bsn_cc%qual2e`, and `wq_cha` sets `bsn_cc%wq`, which is not used.

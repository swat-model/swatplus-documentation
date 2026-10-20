---
title: Climate and Weather
description: Measured and generated weather, elevation lapse, snow, and potential evapotranspiration in SWAT+.
status: review
verified_against:
  - src/climate_control.f90
  - src/cli_precip_control.f90
  - src/cli_staread.f90
  - src/cli_pgen.f90
  - src/cli_tgen.f90
  - src/cli_slrgen.f90
  - src/cli_rhgen.f90
  - src/cli_wndgen.f90
  - src/cli_initwgn.f90
  - src/cli_lapse.f90
  - src/co2_read.f90
  - src/hru_control.f90
  - src/et_pot.f90
  - src/topohyd_init.f90
  - src/basin_module.f90
  - src/basin_prm_default.f90
  - src/basin_read_cc.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Climate supplies the moisture and energy that drive the water balance and sets the relative size of its parts. SWAT+ needs daily precipitation, maximum and minimum air temperature, solar radiation, relative humidity and wind speed. Each weather station in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) takes each variable either from a measured data file or from the weather generator, and every HRU, channel and other spatial object uses the station assigned to it in its connection file. Potential evapotranspiration (PET) is computed in the model by one of three methods. A fourth option is meant to read PET from a file, but in 62.0.1 it returns the Hargreaves estimate.

## Weather inputs

### Measured and generated data

Each row of [`weather-sta.cli`](../input-reference/cli.md) names a weather generator station from [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) and one data set for each variable: precipitation, temperature, solar radiation, relative humidity and wind speed, followed by a PET data set and an atmospheric deposition station. The value `sim` tells SWAT+ to generate that variable from the weather generator statistics.

Measured values come from the files listed in [`pcp.cli`](../input-reference/cli.md#observed-data-lists), [`tmp.cli`](../input-reference/cli.md#observed-data-lists), [`slr.cli`](../input-reference/cli.md#observed-data-lists), [`hmd.cli`](../input-reference/cli.md#observed-data-lists), [`wnd.cli`](../input-reference/cli.md#observed-data-lists) and [`pet.cli`](../input-reference/cli.md#observed-data-lists) (see [`*.cli`](../input-reference/cli.md), [`*.pcp`](../input-reference/pcp.md), [`*.tmp`](../input-reference/tmp.md) and [`*.tem`](../input-reference/tem.md)). The names in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) are matched to these lists with a search that assumes the lists are sorted by name; the `*.cli` page describes what happens when they are not. A value of -97 or less (for example -99) marks a missing record, and SWAT+ fills that day with a generated value. Days outside the period covered by a measured file are also generated.

### Weather generator

The generator produces daily weather from the monthly statistics of a station in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli). Precipitation is generated first, because temperature, radiation and humidity are adjusted for wet and dry days.

Whether a day is wet follows a first-order Markov chain. The probability of rain is `pr_wd` (a wet day following a dry day) or `pr_ww` (a wet day following a wet day) for the month. On a wet day the amount comes from a skewed distribution:

$$R_{day} = \mu_{mon} + 2\,\sigma_{mon}\left(\frac{\left[\left(SND_{day} - \frac{g_{mon}}{6}\right)\frac{g_{mon}}{6} + 1\right]^3 - 1}{g_{mon}}\right)$$

| Symbol | Meaning | Input |
|--------|---------|-------|
| $R_{day}$ | Generated precipitation, at least 0.1 mm | mm H2O |
| $\mu_{mon}$ | Mean daily precipitation on wet days in the month | from `pcpmm` and `pcpd` in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) |
| $\sigma_{mon}$ | Standard deviation of daily precipitation | `pcpstd`, mm |
| $g_{mon}$ | Skew coefficient of daily precipitation | `pcpskw` |
| $SND_{day}$ | Standard normal deviate for the day | generated |

The result is scaled by a monthly correction factor so that the long-term mean of generated wet-day amounts equals $\mu_{mon}$.

Maximum and minimum temperature are drawn around the monthly means `tmpmx` and `tmpmn` with standard deviations `tmpstdmx` and `tmpstdmn`. The maximum is lowered on wet days and raised on dry days by half the monthly temperature range, weighted by the fraction of wet days. Relative humidity is drawn from a triangular distribution around the monthly mean, which comes from the dew point (`dewpt`) and mean temperature, and is raised on wet days. Wind speed follows a modified exponential distribution around the monthly mean `windav`.

The generator in 62.0.1 returns the monthly mean solar radiation `solarav` for every generated day. The wet and dry day adjustment is computed but then replaced by the monthly mean, so generated radiation does not vary from day to day within a month.

`igen` in [`parameters.bsn`](../input-reference/parameters-bsn.md) sets the random number seeds. With `igen = 0` every run uses the same seeds and the same generated weather. Any other value offsets the seeds, so different values give different weather sequences.

### Maximum half-hour rainfall

The fraction of daily rain that falls in the wettest half hour, $\alpha_{0.5}$, is used by the peak runoff rate and erosivity calculations (see [Erosion and sediment](erosion-sediment.md)). It is generated every day from a triangular distribution between 0.02083 and $1 - \exp(-125/(R_{day} + 5))$, with its mode set from the monthly maximum half-hour rainfall `rainhmx` in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli). The mode is multiplied by `adj_pkrt` in [`parameters.bsn`](../input-reference/parameters-bsn.md) and limited to between 0.1 and 0.95.

### Day length and maximum radiation

Each day SWAT+ computes the day length and the maximum possible solar radiation for every weather generator station from its latitude. The solar declination $\delta$ and the relative distance between the earth and the sun $d_r$ on day of year $d$ are

$$\delta = \sin^{-1}\!\left[0.4\,\sin\!\left(\frac{d - 82}{58.09}\right)\right], \qquad d_r = 1 + 0.033\,\cos\!\left(\frac{d}{58.09}\right)$$

and the hour angle of sunset $h$, the day length $T_{DL}$ and the maximum solar radiation $H_{max}$ are

$$h = \cos^{-1}\!\left(-\tan\delta\,\tan\phi\right), \qquad T_{DL} = 7.6394\,h, \qquad H_{max} = 30\,d_r\left(h\,\sin\phi\,\sin\delta + \cos\phi\,\cos\delta\,\sin h\right)$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $\phi$ | Latitude of the weather generator station, `lat` in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli) | radians |
| $h$ | Hour angle of sunset; 0 during polar night and $\pi$ during polar day | radians |
| $T_{DL}$ | Day length | h |
| $H_{max}$ | Maximum possible solar radiation reaching the ground on a cloudless day | MJ/m²/day |

$H_{max}$ is used by net radiation and Hargreaves PET. The day length controls plant dormancy (see [Plant growth and land use management](plant-growth-lum.md)). SWAT+ also computes how the day's radiation is spread over the hours of the day, but no process in 62.0.1 uses that distribution.

### Sub-daily precipitation

With more than one time step per day (`step` in [`time.sim`](../input-reference/time-sim.md)), a day of generated precipitation is spread over the day's time steps with a double exponential intensity curve. The peak rate is

$$i_{pk} = 2\,R_{day}\,\alpha_{0.5}$$

where $R_{day}$ is the day's precipitation (mm) and $\alpha_{0.5}$ the fraction falling in the wettest half hour, so $i_{pk}$ is in mm/h. The time to the peak, as a fraction $v$ of the storm duration, is drawn from a triangular distribution between 0.05 and 0.95 with a mode of 0.25. The storm duration is

$$T_{dur} = \frac{R_{day}}{i_{pk}\,(k_1 + k_2)}, \qquad k_1 = \frac{v}{4.605}, \qquad k_2 = \frac{1 - v}{4.605}$$

limited to 24 hours, with $i_{pk}$ recomputed when the limit applies. The cumulative rainfall at time $t$ (h) from the start of the storm is

$$R(t) = R_{pk} - i_{pk}\,T_{dur}\,k_1\left[1 - \exp\!\left(\frac{t - t_{pk}}{T_{dur}\,k_1}\right)\right] \qquad (t \le t_{pk})$$

$$R(t) = R_{pk} + i_{pk}\,T_{dur}\,k_2\left[1 - \exp\!\left(\frac{t_{pk} - t}{T_{dur}\,k_2}\right)\right] \qquad (t > t_{pk})$$

with $R_{pk} = v\,R_{day}$ and $t_{pk} = v\,T_{dur}$. The storm starts at the beginning of the day, the rainfall of each time step is the increase of $R(t)$ over the step, and any amount left at the end is added to the last step that received rain.

The same curve fills a day of a measured sub-daily record that contains a missing value. Daily precipitation records are not split into time steps: in a sub-daily run a station with daily records gives no rainfall in its time steps. Use sub-daily records, or generated precipitation, for sub-daily runs.

### Elevation lapse

When `lapse` is 1 in [`codes.bsn`](../input-reference/codes-bsn.md), precipitation and temperature are corrected for the difference in elevation between each object and the gauge (or the weather generator station, for generated data) that supplies it:

$$R_{obj} = \max\left(0,\; R_{gage} + \frac{\mathrm{plaps}\,(z_{obj} - z_{gage})}{1000}\right)$$

$$T_{obj} = T_{gage} + \frac{\mathrm{tlaps}\,(z_{gage} - z_{obj})}{1000}$$

| Symbol | Meaning | Units |
|--------|---------|-------|
| $\mathrm{plaps}$ | Precipitation lapse rate, `plaps` in [`parameters.bsn`](../input-reference/parameters-bsn.md) | mm/km |
| $\mathrm{tlaps}$ | Temperature lapse rate, `tlaps` in [`parameters.bsn`](../input-reference/parameters-bsn.md) | °C/km |
| $z_{obj}$, $z_{gage}$ | Elevation of the object and of the gauge or generator station | m |

The temperature correction is applied to the maximum, minimum and mean temperature. A positive `tlaps` makes objects above the gauge cooler. The precipitation correction is a fixed depth per day, added on dry days as well as wet ones, and the result is never negative.

### Carbon dioxide

The CO2 concentration used by plant growth and Penman-Monteith PET is set for each year of the run. If the file `co2_yr.dat` is present, yearly values are read from it; years before the record use the first value and years after it the last. Without the file every year uses `co2` from [`parameters.bsn`](../input-reference/parameters-bsn.md). The values used are written to `co2.out`.

## Snow

On days when the mean air temperature is at or below `fall_tmp`, precipitation that passes the canopy is added to the snowpack. Snow melts on days when the maximum temperature is above `melt_tmp`, at a rate that varies through the year between `melt_min` and `melt_max` and is reduced by the fraction of the HRU covered by snow. The equations and the parameters are on the [`snow.sno`](../input-reference/sno.md) page. Snow sublimation is taken from the soil evaporation demand (see [Soil water and temperature](soil-water-temperature.md)).

## Potential evapotranspiration

Potential evapotranspiration is the rate of evapotranspiration from a large area covered completely by a short, actively growing crop with plenty of water. The method is chosen with `pet` in [`codes.bsn`](../input-reference/codes-bsn.md):

| `pet` | Method |
|-------|--------|
| 0 | Priestley-Taylor |
| 1 | Penman-Monteith |
| 2 | Hargreaves |
| 3 | Station PET (see [PET read from file](#pet-read-from-file)) |

The three computed methods share these terms:

| Symbol | Meaning | Calculation |
|--------|---------|-------------|
| $\bar{T}$ | Mean air temperature, °C | from the weather inputs |
| $P$ | Atmospheric pressure, kPa | $101.3 - z\,(0.01152 - 0.544\times10^{-6}\,z)$ with HRU elevation $z$ in m |
| $\lambda$ | Latent heat of vaporization, MJ/kg | $2.501 - 2.361\times10^{-3}\,\bar{T}$ |
| $\gamma$ | Psychrometric constant, kPa/°C | $1.013\times10^{-3}\,P/(0.622\,\lambda)$ |
| $e^0$, $e$ | Saturation and actual vapour pressure, kPa | $e = e^0 \times$ relative humidity |
| $\Delta$ | Slope of the saturation vapour pressure curve, kPa/°C | $4098\,e^0/(\bar{T} + 237.3)^2$ |

### Net radiation

Priestley-Taylor and Penman-Monteith use net radiation for a reference crop:

$$H_{net} = (1 - \alpha)\,H_{day} - \left(0.34 - 0.139\sqrt{e}\right)\left(0.9\,\frac{H_{day}}{H_{max}} + 0.1\right)\sigma\,T_K^4$$

where $H_{day}$ is the solar radiation reaching the ground (MJ/m²/day), $H_{max}$ the maximum possible solar radiation for the day, $\sigma = 4.903\times10^{-9}$ MJ m$^{-2}$ K$^{-4}$ day$^{-1}$, $T_K$ the mean air temperature in kelvin, and $\alpha$ the albedo: 0.23 for the reference crop, or 0.8 when the snowpack contains more than 0.5 mm of water.

### Priestley-Taylor

$$PET = 1.28\,\frac{\Delta}{\Delta + \gamma}\,\frac{H_{net}}{\lambda}$$

Priestley and Taylor (1972) replaced the aerodynamic term of Penman's equation with the coefficient 1.28, which suits humid areas. The method tends to underestimate PET in arid and semi-arid areas, where advection is a large part of the energy balance.

### Penman-Monteith

$$PET = \frac{\Delta\,H_{net} + \gamma\,\rho_K\,(e^0 - e)/r_a}{\lambda\left[\Delta + \gamma\,(1 + r_c/r_a)\right]}$$

For the reference crop SWAT+ uses the aerodynamic resistance $r_a = 114/u_{1.7}$ (s/m), where $u_{1.7} = u_{10}\,(0.17)^{0.2}$ is the wind speed at 1.7 m estimated from the input wind speed $u_{10}$ (taken as measured at 10 m), and a canopy resistance that responds to CO2:

$$r_c = \frac{49}{1.4 - 0.4\,CO_2/330}$$

$\rho_K$ combines air density, the latent heat of vaporization and unit conversions, and is computed as $1710 - 6.85\,\bar{T}$. The method needs measured or generated relative humidity and wind speed.

Penman-Monteith also computes a crop-specific maximum transpiration from the plant canopy height, leaf area and stomatal conductance (`stcon_max`, `vpd` and `frac_stcon` in [`plants.plt`](../input-reference/plt.md)). In 62.0.1 that value is replaced in the actual evapotranspiration step by the leaf area based estimate used with the other methods (see [Soil water and temperature](soil-water-temperature.md)), so the choice of PET method changes PET but not the way PET is split into transpiration and soil evaporation.

### Hargreaves

$$PET = 0.0023\,\frac{H_0}{\lambda}\,(\bar{T} + 17.8)\sqrt{T_{max} - T_{min}}$$

where $H_0$ is extraterrestrial radiation (MJ/m²/day), taken as $H_{max}\times 37.59/30$. PET is zero on days when $T_{max}$ is not above $T_{min}$. Hargreaves needs only temperature, which makes it a common choice where humidity, wind and radiation records are poor.

### PET read from file

With `pet = 3` the HRU takes the daily PET of its weather station. SWAT+ 62.0.1 first loads the station's measured PET (filling missing days with Hargreaves), but later in the same day it recomputes the station PET with the Hargreaves equation for every station, for use in the climatic moisture index. The HRU therefore receives the Hargreaves value, and `pet = 3` gives the same PET as `pet = 2`.

The same station PET (Hargreaves in every case) is the evaporative demand for channel and reservoir evaporation and for aquifer revap, whatever the `pet` setting.

### HRU adjustment

Whatever the method, PET is multiplied by `pet_co` from [`hydrology.hyd`](../input-reference/hyd.md):

$$PET_{HRU} = \mathrm{pet\_co} \times PET$$

A blank or zero `pet_co` is taken as 1. A value below 0.01 is read as a Hargreaves coefficient and converted to a multiplier by dividing it by 0.0023.

## Switches and parameters

| Input | File | Effect |
|-------|------|--------|
| `pet` | [`codes.bsn`](../input-reference/codes-bsn.md) | PET method |
| `lapse` | [`codes.bsn`](../input-reference/codes-bsn.md) | Elevation lapse of precipitation and temperature |
| `plaps`, `tlaps` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Lapse rates |
| `adj_pkrt` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Multiplier on the generated maximum half-hour rainfall fraction |
| `co2` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | CO2 concentration when `co2_yr.dat` is absent, ppm |
| `igen` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Random number seed selection for the generator |
| `pet_co` | [`hydrology.hyd`](../input-reference/hyd.md) | HRU multiplier on PET |
| `petco_pmpt` | [`parameters.bsn`](../input-reference/parameters-bsn.md) | Read and converted to a fraction, but not applied to PET in 62.0.1 |

## Related pages

- [`*.cli` files](../input-reference/cli.md), [`*.pcp`](../input-reference/pcp.md), [`*.tmp`](../input-reference/tmp.md) for the weather input formats.
- [`snow.sno`](../input-reference/sno.md) for snowfall and snowmelt.
- [Soil water and temperature](soil-water-temperature.md) for actual evapotranspiration.
- [Overview and water balance](overview-water-balance.md) for where climate enters the daily sequence.

??? quote "Sources"

    - Daily weather for all stations, maximum half-hour rainfall: [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90), [`cli_precip_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_precip_control.f90)
    - Station file reader: [`cli_staread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_staread.f90); generator statistics: [`cli_wgnread.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_wgnread.f90), [`cli_initwgn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_initwgn.f90)
    - Generators: [`cli_pgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pgen.f90), [`cli_pgenhr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pgenhr.f90), [`cli_tgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_tgen.f90), [`cli_slrgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_slrgen.f90), [`cli_rhgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_rhgen.f90), [`cli_wndgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_wndgen.f90)
    - Day length, declination, maximum radiation and hourly radiation fractions: [`cli_clgen.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_clgen.f90), called from `climate_control.f90`. The hourly fractions `frad` are computed and not used.
    - Sub-daily precipitation curve: [`cli_pgenhr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_pgenhr.f90), called from `cli_precip_control.f90` for generated days and for sub-daily records with missing values; daily records leave `wst%weat%ts` unfilled.
    - Lapse: [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90), applied in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - CO2: [`co2_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/co2_read.f90)
    - PET: [`et_pot.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_pot.f90); `pet_co` setup in [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90)
    - Basin codes and parameters: [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90), [`basin_prm_default.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_prm_default.f90)

    | Symbol or column | Fortran variable |
    |------------------|------------------|
    | `pet` (codes.bsn) | `bsn_cc%pet` |
    | `lapse` (codes.bsn) | `bsn_cc%lapse` |
    | `plaps`, `tlaps` | `bsn_prm%plaps`, `bsn_prm%tlaps`; per object `ob(iob)%plaps`, `ob(iob)%tlaps` |
    | `adj_pkrt` | `bsn_prm%adj_pkr` |
    | `co2`, yearly CO2 | `bsn_prm%co2`, `co2y(time%yrs)` |
    | `petco_pmpt` | `bsn_prm%petco_pmpt` |
    | `pet_co` | `hru(j)%hyd%pet_co` |
    | $\alpha_{0.5}$ | `wst(iwst)%weat%precip_half_hr` |
    | $H_{day}$, $H_{max}$ | `w%solrad`, `w%solradmx` |
    | $\delta$, $d_r$, $h$, $T_{DL}$ | `sd`, `dd`, `h`, `wst(iwst)%weat%daylength` |
    | $i_{pk}$, $v$, $T_{dur}$ | `pkrr`, `vv`, `dur` |
    | $H_{net}$ (reference crop) | `rn_pet` |
    | $\Delta$, $\gamma$, $\lambda$ | `dlt`, `gma`, `xl` |
    | $r_a$, $r_c$ | `rv`, `rc` |
    | PET | `pet_day` |

---
title: "snow.sno"
description: Snow parameter database. One row per snow parameter set, referenced by name from each HRU.
status: review
verified_against:
  - src/snowdb_read.f90
  - src/hru_module.f90
  - src/hru_read.f90
  - src/hrudb_init.f90
  - src/topohyd_init.f90
  - src/sq_snom.f90
  - src/ascrv.f90
  - src/actions.f90
  - src/cal_parm_select.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`snow.sno` is the snow parameter database. Each row is a named set of parameters for snowfall, snowpack temperature, snowmelt and snow cover. An HRU picks a row by name in the `snow` column of [`hru-data.hru`](hru.md). The file is named on the `hru_parm_db` line of [`file.cio`](file-cio.md) (default `snow.sno`).

If [`hru-data.hru`](../input-reference/hru.md) gives `null` for an HRU's snow entry, or a name that is not in `snow.sno`, the HRU uses the first row of `snow.sno`. No message is written in either case. A model therefore needs a `snow.sno` file with at least one row: if the file is missing or named `null` in [`file.cio`](../input-reference/file-cio.md), every HRU refers to a first row that does not exist.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one parameter set with nine values in the order below. The reader does not match columns by header name, so all nine values must be present and in this order.

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Name of the snow parameter set, matched against the `snow` column of [`hru-data.hru`](../input-reference/hru.md). |
| 2 | `fall_tmp` | °C | -5 to 5 | Snowfall temperature. On a day when the mean air temperature is at or below `fall_tmp`, all precipitation falls as snow and is added to the snowpack. |
| 3 | `melt_tmp` | °C | -5 to 5 | Snowmelt base temperature. Melt occurs only on days when the maximum air temperature is above `melt_tmp`. |
| 4 | `melt_max` | mm H₂O/°C/day | 0 to 10 | Melt factor on 21 June (day 172). |
| 5 | `melt_min` | mm H₂O/°C/day | 0 to 10 | Melt factor on 21 December (day 355). |
| 6 | `tmp_lag` | - | 0.01 to 1 | Snowpack temperature lag factor. See [Snowpack temperature](#snowpack-temperature) for how 62.0.1 uses it. |
| 7 | `snow_h2o` | mm H₂O | 0 to 500 | Snow water content at and above which the HRU is fully covered by snow. |
| 8 | `cov50` | fraction | 0.05 to 0.95 | Fraction of `snow_h2o` at which 50% of the HRU is covered by snow. |
| 9 | `snow_init` | mm H₂O | 0 and up | Snow water content at the start of the simulation. |

## Snow processes

All snow calculations run daily for each HRU, after canopy interception.

### Snowfall

If the mean air temperature $\bar{T}$ is at or below `fall_tmp`, the day's precipitation (after canopy interception) is added to the snowpack and no rain reaches the ground. In sub-daily runs the rainfall for every time step of that day is set to zero.

### Snowpack temperature

The intended snowpack temperature keeps part of the previous day's value:

$$T_{snow,d} = T_{snow,d-1}\,(1 - \ell) + \bar{T}_d\,\ell$$

where $\ell$ is `tmp_lag`. Values near 1 give the current day's air temperature most of the weight. Values near 0 make the snowpack respond slowly.

In 62.0.1 the previous day's snowpack temperature is reset to zero at the start of each day, so the calculation reduces to

$$T_{snow,d} = \ell\,\bar{T}_d$$

and `tmp_lag` acts as a scaling factor on the day's mean air temperature. It has no lag effect.

### Melt factor

The melt factor $b_{mlt}$ varies through the year between `melt_min` and `melt_max`, which accounts for the effect of snowpack density on melt:

$$b_{mlt} = \frac{\mathrm{melt\_max} + \mathrm{melt\_min}}{2} + \frac{\mathrm{melt\_max} - \mathrm{melt\_min}}{2}\,\sin\!\left(\frac{2\pi}{365}\,(d - 81)\right)$$

where $d$ is the day of the year. The factor equals `melt_max` on day 172 and `melt_min` on day 355 for every HRU. SWAT+ 62.0.1 does not swap the two for the Southern Hemisphere, so a model there should give the winter (June) factor in `melt_max` and the summer (December) factor in `melt_min`.

In rural areas the melt factor ranges from 1.4 to 6.9 mm H₂O/°C/day (Huber and Dickinson, 1988). Urban values tend to the high end because traffic compresses the snowpack: urban studies in Sweden reported 3.0 to 8.0 mm H₂O/°C/day (Bengston, 1981; Westerstrom, 1981), and snow on asphalt gave 1.7 to 6.5 mm H₂O/°C/day (Westerstrom, 1984).

### Snow cover

Drifting, shading and topography mean that snow rarely covers an HRU evenly. SWAT+ describes the covered fraction with an areal depletion curve. With $r = SNO / \mathrm{snow\_h2o}$, the ratio of the current snow water content to `snow_h2o`,

$$sno_{cov} = \frac{r}{r + \exp(c_1 - c_2\,r)} \quad \text{for } r < 1, \qquad sno_{cov} = 1 \quad \text{for } r \ge 1$$

The shape coefficients $c_1$ and $c_2$ are set once at the start of the run so that the curve passes through 50% cover at $r = \text{cov50}$ and 95% cover at $r = 0.95$. `cov50` must therefore lie between 0 and 0.95.

The depletion curve affects melt only while the snow water content is between 0 and `snow_h2o`. A small `snow_h2o` makes its effect on melt minor; a large one makes it more important.

### Snowmelt

When the maximum air temperature $T_{max}$ is above `melt_tmp` and there is snow on the ground, melt is

$$SNO_{mlt} = b_{mlt}\; sno_{cov} \left(\frac{T_{snow} + T_{max}}{2} - \mathrm{melt\_tmp}\right)$$

limited to between zero and the snow water content. Melt water is added to the day's water input at the surface, together with any rain. In sub-daily runs it is spread evenly over the day's time steps.

## Calibration and decision tables

Five of the parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md), using these parameter names: `snofall_tmp` (`fall_tmp`), `snomelt_tmp` (`melt_tmp`), `snomelt_max` (`melt_max`), `snomelt_min` (`melt_min`) and `snomelt_lag` (`tmp_lag`). `snow_h2o`, `cov50` and `snow_init` have no calibration parameter. See [parameter change files](../calibration/parameter-change-files.md).

A decision table action `snow_change` switches an HRU to another `snow.sno` row during the run and logs the change to `lu_change_out.txt`. The snow cover curve is not recalculated after the switch, so it keeps the shape from the HRU's original `cov50`.

## Example

`refdata/Ames_sub1/snow.sno` in the SWAT+ repository:

```
snow.sno: written by SWAT+ editor v2.3.3 on 2023-10-25 08:58 for SWAT+ rev.60.5.7
name                  fall_tmp      melt_tmp      melt_max      melt_min       tmp_lag      snow_h2o         cov50     snow_init
snow001                1.00000       0.50000       4.50000       4.50000       1.00000       1.00000       0.50000       0.00000
```

One parameter set named `snow001`. `melt_max` and `melt_min` are both 4.5, so the melt factor is constant through the year. With `tmp_lag` at 1.0 the snowpack temperature equals the day's mean air temperature, and with `snow_h2o` at 1 mm the HRU is fully covered by any snowpack of 1 mm or more.

## Related files

- [`hru-data.hru`](hru.md): selects a `snow.sno` row by name in its `snow` column; `null` or an unknown name selects the first row.
- [`file.cio`](file-cio.md): names the snow file.
- [`tmp.cli`](tmp.md) and [`pcp.cli`](pcp.md): supply the air temperatures and precipitation the snow routine uses.

??? quote "Sources"

    - Reader: [`snowdb_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/snowdb_read.f90)
    - Type definition: `type snow_parameters` in [`hru_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_module.f90)
    - Name lookup from `hru-data.hru`: [`hru_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_read.f90)
    - HRU setup and depletion curve: [`topohyd_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/topohyd_init.f90), [`ascrv.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ascrv.f90)
    - Snowfall and melt: [`sq_snom.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_snom.f90), called from [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Decision table action `snow_change`: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Calibration parameters: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)
    - File name slot: `in_parmdb%snow` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `name` | `snodb%name` |
    | `fall_tmp` | `snodb%falltmp` |
    | `melt_tmp` | `snodb%melttmp` |
    | `melt_max` | `snodb%meltmx` |
    | `melt_min` | `snodb%meltmn` |
    | `tmp_lag` | `snodb%timp` |
    | `snow_h2o` | `snodb%covmx` |
    | `cov50` | `snodb%cov50` |
    | `snow_init` | `snodb%init_mm` |

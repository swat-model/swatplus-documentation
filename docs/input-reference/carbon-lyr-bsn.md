---
title: carbon_lyr.bsn
description: Decomposition rates and CO2 fractions of the dynamic soil carbon model, one row for the surface soil layer and one for the deeper layers.
status: review
verified_against:
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
  - src/cbn_zhang2.f90
  - src/soils_init.f90
  - src/cal_parm_select.f90
  - src/cal_conditions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`carbon_lyr.bsn` contains the decomposition rates of the litter, microbial and humus pools of the dynamic soil carbon model (`carbon = 2` in [`codes.bsn`](codes-bsn.md)), and the fractions of decomposed carbon released as CO2. There is one row for each of two layer groups:

- layer group 1: the first soil layer of each HRU. SWAT+ adds a 10 mm surface layer when the first layer in [`soils.sol`](sol.md) is deeper than 19.5 mm, so this is normally the 10 mm surface layer.
- layer group 2: all other soil layers.

The basin-wide parameters of the carbon model are in [`carbon.bsn`](carbon-bsn.md).

## Activation and file name

The file is read only when `carbon = 2`, right after [`carbon.bsn`](../input-reference/carbon-bsn.md), and it is then required. It is not listed in [`file.cio`](file-cio.md). Its name is built from the [`carbon.bsn`](../input-reference/carbon-bsn.md) name on the `basin` line of [`file.cio`](../input-reference/file-cio.md) by inserting `_lyr` before the extension, so the default [`carbon.bsn`](../input-reference/carbon-bsn.md) gives `carbon_lyr.bsn`, and `mybasin.bsn` gives `mybasin_lyr.bsn`.

SWAT+ writes an error to the screen and to `diagnostics.out` and stops if the file does not exist, cannot be opened, or has fewer than two valid data rows.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped and may be blank. Each later line is one layer group: an integer layer group number followed by 11 values, in the order below. The reader matches values by position only.

| # | Column | Units | Group 1 (example) | Group 2 (example) | Description |
|---|--------|-------|-------------------|-------------------|-------------|
| 1 | `layer` | - | 1 | 2 | Layer group: `1` first soil layer, `2` all deeper layers. |
| 2 | `hp_rate` | 1/day | 1.2e-05 | 1.2e-05 | Decomposition rate of passive humus under optimal conditions. |
| 3 | `hs_rate` | 1/day | 2.92e-04 | 1.81e-04 | Decomposition rate of slow humus under optimal conditions. |
| 4 | `microb_rate` | 1/day | 0.0164 | 0.02 | Decomposition rate of microbial biomass under optimal conditions. Used only in group 2. |
| 5 | `meta_rate` | 1/day | 0.0405 | 0.0507 | Decomposition rate of metabolic litter under optimal conditions. |
| 6 | `str_rate` | 1/day | 0.0107 | 0.0134 | Decomposition rate of structural litter under optimal conditions, before the lignin reduction. |
| 7 | `microb_top_rate` | 1/day | 0.0164 | 0.02 | Decomposition rate of microbial biomass in the first soil layer. Used only in group 1. |
| 8 | `hs_hp` | fraction | 0.05 | 0.05 | Fraction of decomposed slow humus that goes to passive humus, before the clay adjustment. |
| 9 | `a1co2` | fraction | 0.60 | 0.55 | Fraction of decomposed metabolic litter and non-lignin structural litter released as CO2. |
| 10 | `asco2` | fraction | 0.55 | 0.55 | Fraction of decomposed slow humus released as CO2. |
| 11 | `apco2` | fraction | 0.55 | 0.55 | Fraction of decomposed passive humus released as CO2. |
| 12 | `abco2` | fraction | 0.55 | 0.0 | Fraction of decomposed microbial biomass released as CO2. Used only in group 1. |

The example values are those of `refdata/Ames_sub1/carbon_lyr.bsn` (see [Example](#example)).

Rows are read until the end of the file. A row whose layer group number is below 1 or above 2 is skipped with a message in `diagnostics.out`. A row that cannot be read (a missing value, or text in a number column) ends the reading at that row without a message, and the rows after it are ignored. The rows may be in any order. The reader counts accepted rows without checking that both groups are present, so a file with two rows for group 1 and none for group 2 passes the check and leaves the group 2 values at 0, which stops decomposition in all layers below the first.

## Use in the carbon model

Each day, for each soil layer, the potential transformation of each pool is its carbon times its rate from the layer's group times the combined temperature, water, oxygen and tillage factor (see [`carbon.bsn`](carbon-bsn.md#water-factor)):

$$\Delta C_{pool} = k_{pool}\; f_{env}\; C_{pool}$$

with these additions:

- metabolic litter: `a1co2` is released as CO2 and the rest goes to microbial biomass.
- structural litter: the rate is reduced by the lignin fraction $L$ of the litter (at most 0.8), $k = \mathrm{str\_rate}\cdot\exp(-3L)$. Of the decomposed lignin, 30% is released as CO2 and 70% goes to slow humus. Of the non-lignin part, `a1co2` is released as CO2 and the rest goes to microbial biomass.
- microbial biomass: the first soil layer uses `microb_top_rate`. Deeper layers use `microb_rate` times a texture factor $0.25 + 0.0075\,\mathrm{sand}$ (sand in %).
- slow humus: the fraction going to passive humus is $\max(0.001,\; \mathrm{hs\_hp} - 0.00009\,\mathrm{clay})$, with clay in %. `asco2` is released as CO2 and the rest goes to microbial biomass.
- passive humus: `apco2` is released as CO2 and the rest goes to microbial biomass.
- microbial biomass: in the first soil layer `abco2` is released as CO2. In deeper layers the CO2 fraction is calculated from sand content, $0.17 + 0.0068\,\mathrm{sand}$, and the `abco2` of group 2 is not used. The fraction going to passive humus is $0.003 + 0.00032\,\mathrm{clay}$ in all layers.

The actual transformations are reduced when there is not enough mineral N to meet the N demand of the receiving pools. See [soil carbon](../model-theory/carbon.md) for the full pool structure.

## Calibration

The parameter names `hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp`, `a1co2`, `asco2`, `apco2` and `abco2` are recognised in [`calibration.cal`](../calibration/parameter-change-files.md) with object type `bsn`, and the layer group is meant to be given as the layer of the change. In 62.0.1, basin parameters are passed to the change routine without a layer number, so these changes are skipped and have no effect (see [parameter change files](../calibration/parameter-change-files.md)). Calibrating these rates means editing `carbon_lyr.bsn`.

## Example

`refdata/Ames_sub1/carbon_lyr.bsn` in the SWAT+ repository:

```
carbon_lyr.bsn: derived from carb_coefs.cbn (per-layer carbon coefficients)
           layer         hp_rate         hs_rate     microb_rate       meta_rate        str_rate microb_top_rate           hs_hp           a1co2           asco2           apco2           abco2
               1         1.2e-05        2.92e-04          0.0164          0.0405          0.0107          0.0164            0.05            0.60            0.55            0.55            0.55
               2         1.2e-05        1.81e-04            0.02          0.0507          0.0134            0.02            0.05            0.55            0.55            0.55             0.0
```

The first soil layer decomposes metabolic and structural litter more slowly than the deeper layers (0.0405 and 0.0107 per day, against 0.0507 and 0.0134) and slow humus faster (2.92e-04 against 1.81e-04 per day). The 0.0 for `abco2` in group 2 has no effect, because deeper layers calculate that fraction from their sand content. `microb_rate` in group 1 and `microb_top_rate` in group 2 are not used.

## Related files

- [`carbon.bsn`](carbon-bsn.md): basin-wide carbon parameters; its name sets the name of this file.
- [`codes.bsn`](codes-bsn.md): `carbon = 2` turns the carbon model on.
- [`soils.sol`](sol.md): layer depths, clay and sand contents.
- [Carbon outputs](../output-reference/carbon.md): per-layer pools, fluxes and CO2.
- [Soil carbon](../model-theory/carbon.md): description of the carbon model.

??? quote "Sources"

    - Reader: second part of [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90)
    - Type definitions: `type carbon_inputs` (array `carbdb(2)`) and `type organic_allocations` (array `org_allo(2)`) in [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90)
    - Use: [`cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90)
    - Surface layer: [`soils_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soils_init.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90), [`cal_conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_conditions.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `layer` | `layer_id`, index into `carbdb` and `org_allo` |
    | `hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp` | `carbdb(layer)%...` of the same names |
    | `a1co2`, `asco2`, `apco2`, `abco2` | `org_allo(layer)%...` of the same names |

---
title: carbon.bsn
description: Basin-wide parameters of the dynamic soil carbon model. One row of 28 values for initial carbon pools, soluble carbon losses, organic amendments, tillage and biological mixing, temperature and water factors, residue decomposition and the slow humus initialisation method.
status: review
verified_against:
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
  - src/tillage_data_module.f90
  - src/plant_data_module.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_bsn.f90
  - src/main.f90.in
  - src/soil_nutcarb_init.f90
  - src/nut_orgnc2.f90
  - src/pl_fert.f90
  - src/pl_manure.f90
  - src/hru_control.f90
  - src/mgt_tillfactor.f90
  - src/mgt_biomix.f90
  - src/mgt_newtillmix_cswat1.f90
  - src/cbn_zhang2.f90
  - src/fcgd.f90
  - src/cbn_surfrsd_decomp.f90
  - src/cbn_rsd_decomp.f90
  - src/nut_nminrl.f90
  - src/cal_parm_select.f90
  - src/cal_conditions.f90
  - src/carbon_layers_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`carbon.bsn` contains the basin-wide parameters of the dynamic soil carbon model (`carbon = 2` in [`codes.bsn`](codes-bsn.md)): how soil organic carbon is split into pools at the start of the run, losses of soluble carbon in water, the split of organic N and P in fertilizer and manure, the duration and decay of tillage effects, the curves for tillage and biological mixing, the temperature and water factors on decomposition, surface residue photodegradation, and the C:N and C:P controls on residue decomposition.

It works together with [`carbon_lyr.bsn`](carbon-lyr-bsn.md), which contains the decomposition rates and CO2 fractions for the surface layer and for the deeper layers. In revision 62 these two files replaced [`carb_coefs.cbn`](../input-reference/cbn.md) (see [carb_coefs.cbn](cbn.md)).

## Activation and file names

The file is read only when `carbon = 2` in [`codes.bsn`](../input-reference/codes-bsn.md). With any other `carbon` code it is ignored and need not exist.

With `carbon = 2` the file is required. SWAT+ writes an error to the screen and to `diagnostics.out` and stops if:

- the file does not exist or cannot be opened;
- its data line is missing or one of the 28 values cannot be read;
- the companion file [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) is missing or has too few valid rows (see [`carbon_lyr.bsn`](carbon-lyr-bsn.md)).

There are no built-in values to fall back on.

The file is named in the third position of the `basin` line of [`file.cio`](file-cio.md), after [`codes.bsn`](../input-reference/codes-bsn.md) and [`parameters.bsn`](../input-reference/parameters-bsn.md). The default name is `carbon.bsn`. The name of the layer file is built from it by inserting `_lyr` before the extension: `carbon.bsn` gives [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md), `mybasin.bsn` gives `mybasin_lyr.bsn`, and a name without an extension gets `_lyr.bsn` added. The layer file is not listed in [`file.cio`](../input-reference/file-cio.md).

The `basin` line of [`file.cio`](../input-reference/file-cio.md) must have three names. The line is read as three names in one free-format read, so a `basin` line from an older dataset with only two names takes the first word of the next line (normally `climate`) as the carbon file name, and the rest of [`file.cio`](../input-reference/file-cio.md) is then read one line out of step. Datasets that do not use the carbon model can put `null` in the third position.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped and may be blank. Line 3 contains the 28 values in the order below. The reader matches values by position only. Columns 7, 11, 12 and 28 are integers and must be written without a decimal point, for example `2`; a value such as `2.0` in these columns stops the run with a read error.

| # | Column | Units | Example value | Description |
|---|--------|-------|---------------|-------------|
| 1 | `init_seq` | fraction | 0.95 | Fraction of each layer's soil organic carbon put into the humus and microbial pools at the start. The rest, $1 -$ `init_seq`, goes to metabolic (85%) and structural (15%) litter. |
| 2 | `init_microb` | fraction | 0.02 | Fraction of the `init_seq` share that goes to the microbial biomass pool. |
| 3 | `init_slow` | fraction | 0.44 | Fraction of the `init_seq` share that goes to the slow humus pool (when `mathers_method` is 0). |
| 4 | `init_passive` | fraction | 0.54 | Fraction of the `init_seq` share that goes to the passive humus pool. |
| 5 | `koc_c` | - | 1000 | Partition coefficient of microbial carbon between soil and water, controlling its loss in runoff, lateral flow and percolation from the top layer. Typical range 500 to 1500. |
| 6 | `solc_ratio` | - | 0.5 | Ratio of the soluble carbon concentration in surface runoff and lateral flow to the concentration in percolate. Typical range 0.1 to 1. |
| 7 | `till_eff_days` | days (integer) | 100 | Number of days a tillage operation affects decomposition. |
| 8 | `manure_c_frac` | fraction | 0.5 | Split of the organic N and P in applied fertilizer and manure between fresh residue and the slow humus pool. See [Organic fertilizer and manure](#organic-fertilizer-and-manure). |
| 9 | `bio_consol` | fraction/day | 0.15 | Daily recovery rate of biological mixing after tillage. |
| 10 | `till_consol` | fraction/day | 0.10 | Daily decline of the tillage factor as the soil settles. |
| 11 | `tmpf_eqn` | code (integer) | 2 | Temperature factor equation: `1`, `2` or `3`. See [Temperature factor](#temperature-factor). |
| 12 | `watf_eqn` | code (integer) | 1 | Water factor equation: `1` or `2`. See [Water factor](#water-factor). |
| 13 | `t_cbn_min` | °C | -0.5 | Minimum temperature of temperature equation 2. |
| 14 | `t_cbn_opt` | °C | 30.0 | Optimum temperature of temperature equation 2. |
| 15 | `t_cbn_max` | °C | 50.0 | Maximum temperature of temperature equation 2. |
| 16 | `bmix_a` | - | 3.0 | Intercept $a$ of the texture curve for biological mixing. |
| 17 | `bmix_b` | - | 5.0 | Coefficient $b$ of the texture curve for biological mixing. |
| 18 | `bmix_c` | - | -5.5 | Exponent coefficient $c$ of the texture curve for biological mixing. |
| 19 | `tillmix_a` | - | 3.0 | Intercept $a$ of the texture curve for tillage. |
| 20 | `tillmix_b` | - | 15.0 | Coefficient $b$ of the texture curve for tillage. |
| 21 | `tillmix_c` | - | -3.5 | Exponent coefficient $c$ of the texture curve for tillage. |
| 22 | `sfc_rsd_photodeg` | fraction/day | 0.001 | Fraction of surface residue lost each day to photodegradation. The lost carbon is counted as a residue emission. |
| 23 | `n_act_frac` | fraction | 0.02 | Fraction of organic N in the active humus pool. Not used with `carbon = 2`. See [Notes on individual columns](#notes-on-individual-columns). |
| 24 | `cnr_cap` | - | 500 | Upper limit on the residue C:N ratio in the C:N decomposition factor. |
| 25 | `cnr_ref` | - | 25 | Residue C:N ratio at which the C:N decomposition factor equals 1. |
| 26 | `cpr_cap` | - | 5000 | Upper limit on the residue C:P ratio in the C:P decomposition factor. |
| 27 | `cpr_ref` | - | 200 | Residue C:P ratio at which the C:P decomposition factor equals 1. |
| 28 | `mathers_method` | code (integer) | 1 | Slow humus initialisation: `1` Mathers method, any other value the `init_slow` fraction. See [Initial carbon pools](#initial-carbon-pools). |

The example values are those of `refdata/Ames_sub1/carbon.bsn` (see [Example](#example)). Since the file is required, there are no defaults in the usual sense.

## Initial carbon pools

At the start of the run, the organic carbon $C$ of each soil layer (from the organic carbon content in [`soils.sol`](sol.md)) is divided into pools:

| Pool | Carbon | C:N | C:P |
|------|--------|-----|-----|
| passive humus | $C \cdot \mathrm{init\_seq} \cdot \mathrm{init\_passive}$ | 10 | 80 |
| slow humus | $C \cdot \mathrm{init\_seq} \cdot \mathrm{init\_slow}$ | 10 | 80 |
| microbial biomass | $C \cdot \mathrm{init\_seq} \cdot \mathrm{init\_microb}$ | 8 | 80 |
| metabolic litter | $C \cdot (1 - \mathrm{init\_seq}) \cdot 0.85$ | 10 | 100 |
| structural litter | $C \cdot (1 - \mathrm{init\_seq}) \cdot 0.15$ | 150 | 1500 |

The reader does not check the fractions. `init_microb`, `init_slow` and `init_passive` should add up to 1, or the pools will not add up to the soil's organic carbon.

With `mathers_method = 1`, the slow humus pool is set from the clay and silt content instead of `init_slow`, following "Updating carbon pool initialization with DSSAT-CENTURY". In 62.0.1 the test and equation are written for clay plus silt as a fraction, while the soil values are in percent. As a result, for every layer with more than 0.35% clay plus silt the slow humus share is

$$f_{slow} = 0.0041 + 0.0053\,(\mathrm{clay} + \mathrm{silt})$$

with clay and silt in percent (0.32 for a layer with 60% clay plus silt), and the slow humus carbon is $C \cdot \mathrm{init\_seq} \cdot f_{slow}$. The passive and microbial pools keep their `init_passive` and `init_microb` shares, so with the Mathers method the pools generally do not add up to the soil's organic carbon.

## Soluble carbon losses

Each day, microbial carbon in the top layer is lost with the water leaving it:

$$C_{loss} = C_{mic}\left[1 - \exp\!\left(-\frac{Q_{surf} + Q_{perc} + Q_{lat}}{UL + 0.0001\,\mathrm{koc\_c}\cdot C_{tot}}\right)\right]$$

where $UL$ is the water content of the layer at saturation (mm) and $C_{tot}$ is the layer's total organic carbon. The loss is shared between percolation and surface runoff plus lateral flow, with the concentration in surface runoff and lateral flow equal to `solc_ratio` times the concentration in percolate. Microbial carbon attached to eroded sediment is lost in proportion to the sediment yield.

## Organic fertilizer and manure

When fertilizer with organic N or P, or manure, is applied, the organic matter goes to the slow humus pool and to metabolic and structural litter. In the code, the slow humus pool receives the fraction $1 -$ `manure_c_frac` of the organic matter in each layer, and the metabolic and structural litter together also receive $1 -$ `manure_c_frac`, split by a metabolic fraction from the C:N ratio of the material. The code comments say litter should receive the fraction `manure_c_frac`. With the value 0.5 used in the reference datasets the two readings give the same result; with other values the amounts added differ from the comments.

## Tillage and biological mixing

The tillage factor of a soil layer is calculated from a texture curve and the cumulative soil disturbance $x$ of tillage operations:

$$Z = a + b\,\exp\!\left(c\,\frac{\mathrm{clay}}{100}\right), \qquad F = Z\,\frac{x}{x + \exp(1 - 2x)}$$

with clay in percent. Tillage operations use `tillmix_a`, `tillmix_b` and `tillmix_c`; biological mixing uses `bmix_a`, `bmix_b` and `bmix_c`. The layer's tillage factor is the sum of the two parts. The original equations were $Z = 3 + 12\,\exp(-5.5\,\mathrm{clay}/100)$ for tillage and $Z = 3 + 5\,\exp(-5.5\,\mathrm{clay}/100)$ for biological mixing.

After tillage, the tillage part declines each day by the fraction `till_consol` (scaled down by $SW/FC$ when the layer is drier than field capacity), and biological mixing efficiency recovers each day by `bio_consol` times its initial value until it is back to that value. `till_eff_days` days after a tillage operation the tillage effect ends and the tillage part is reset to 0.

How the tillage factor changes decomposition depends on `idc_till` in [`codes.bsn`](codes-bsn.md#tillage-effect-on-decomposition). With `idc_till = 3` the decomposition rates are multiplied by $1 + F$. With `idc_till = 1` they are multiplied by 1.6 in tilled layers for `till_eff_days` days.

## Temperature factor

`tmpf_eqn` selects the temperature factor $\gamma_{tmp}$ on decomposition, using the layer temperature $T$ (°C). Decomposition only occurs when $T > 0$.

| `tmpf_eqn` | Equation |
|------------|----------|
| 1 | $\gamma_{tmp} = T / [T + \exp(5.058 - 0.2504\,T)]$ for $T \le 35$; $1 - 0.04\,(T - 35)$ for $35 < T \le 60$; 0 above 60. |
| 2 | $\gamma_{tmp} = \dfrac{(T - T_n)^q\,(T_x - T)}{(T_o - T_n)^q\,(T_x - T_o)}$ with $q = \dfrac{T_n - T_o}{T_o - T_x}$, and 0 outside $T_n < T < T_x$. $T_n$, $T_o$ and $T_x$ are `t_cbn_min`, `t_cbn_opt` and `t_cbn_max`. |
| 3 | $\gamma_{tmp} = 0.9\,T / [T + \exp(9.93 - 0.312\,T)] + 0.1$ |

Biological mixing is also reduced with temperature: by equation 3 when `tmpf_eqn = 3`, and by equation 2 otherwise. So `t_cbn_min`, `t_cbn_opt` and `t_cbn_max` affect biological mixing even when `tmpf_eqn = 1`.

## Water factor

`watf_eqn` selects the water factor $\gamma_{sw}$:

- `1`: $\gamma_{sw} = 0.1 + 0.9\sqrt{SW/FC}$, limited to 0.05 to 1, where $SW$ and $FC$ are the layer's water content and field capacity above wilting point.
- `2`: the product of a water term, rising from 0 at zero water content to 0.4 at wilting point and 1 at field capacity, and an aeration term that falls as the air-filled porosity drops below 0.1. Both terms are at most 1.

Decomposition rates are multiplied by the combined factor $\min\!\left(15,\; 0.9\,\sqrt{\gamma_{tmp}\,\gamma_{sw}}\;\gamma_{ox}\;f_{till}\right)$, where $\gamma_{ox}$ is an oxygen factor that decreases with depth and $f_{till}$ is the tillage factor.

With either equation $\gamma_{sw}$ never exceeds 1. Denitrification in the dynamic carbon model occurs only when $\gamma_{sw}$ reaches `denit_frac` in [`parameters.bsn`](parameters-bsn.md#denitrification), so a `denit_frac` above 1 (the default is 1.3) switches denitrification off.

## Residue decomposition

The daily decay rate of surface residue for each plant is

$$k = \max\!\left(\mathrm{rsd\_decay},\; k_{pl}\;\min(f_{CN}, f_{CP}, 1)\;\sqrt{\gamma_{tmp}\,\gamma_{sw}}\right), \qquad f_{CN} = \exp\!\left(-0.693\,\frac{CN - \mathrm{cnr\_ref}}{\mathrm{cnr\_ref}}\right)$$

limited to 1, where $k_{pl}$ is the plant's residue decomposition coefficient (`plnt_decomp` in [`plants.plt`](plt.md), or `rsd_decomp` in [`parameters.bsn`](../input-reference/parameters-bsn.md)), $CN$ is the residue C:N ratio limited to `cnr_cap`, and $f_{CP}$ is the same expression with the C:P ratio, `cpr_ref` and `cpr_cap`. A residue C:N ratio equal to `cnr_ref` gives $f_{CN} = 1$; each further `cnr_ref` halves it. Before decomposition, the fraction `sfc_rsd_photodeg` of the surface residue is removed by photodegradation.

## Notes on individual columns

- `n_act_frac` is used only by the static carbon routines (`carbon = 0`), which do not read `carbon.bsn`. With `carbon = 2` the value read has no effect, and with `carbon = 0` the model uses 0.02.
- `till_eff_days` is the only tillage duration in the model. Under `idc_till = 3` it also limits how long the tillage part of the tillage factor lasts.
- `tmpf_eqn` and `watf_eqn` values other than those listed leave the factor at 0, which stops decomposition of the soil carbon pools and denitrification in every layer.

## Calibration

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md) with object type `bsn`: `init_seq`, `init_microb`, `init_slow`, `init_passive`, `koc_c`, `solc_ratio`, `manure_c_frac`, `bio_consol`, `till_consol`, `sfc_rsd_photodeg`, `n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref`, `t_cbn_min`, `t_cbn_opt`, `t_cbn_max`, `bmix_a`, `bmix_b`, `bmix_c`, `tillmix_a`, `tillmix_b` and `tillmix_c`. `till_eff_days`, `tmpf_eqn`, `watf_eqn` and `mathers_method` cannot be calibrated. A change to `n_act_frac` has no effect with `carbon = 2`. See [parameter change files](../calibration/parameter-change-files.md).

## Example

`refdata/Ames_sub1/carbon.bsn` in the SWAT+ repository:

```
carbon.bsn: derived from carb_coefs.cbn (basin carbon scalars)
          init_seq       init_microb         init_slow      init_passive             koc_c        solc_ratio     till_eff_days     manure_c_frac        bio_consol       till_consol          tmpf_eqn          watf_eqn         t_cbn_min         t_cbn_opt         t_cbn_max            bmix_a            bmix_b            bmix_c         tillmix_a         tillmix_b         tillmix_c  sfc_rsd_photodeg        n_act_frac           cnr_cap           cnr_ref           cpr_cap           cpr_ref    mathers_method
              0.95              0.02              0.44              0.54            1000.0               0.5               100               0.5              0.15              0.10                 2                 1              -0.5              30.0              50.0               3.0               5.0              -5.5               3.0              15.0              -3.5             0.001              0.02             500.0              25.0            5000.0             200.0                 1
```

95% of soil organic carbon starts in the humus and microbial pools. Because `mathers_method = 1`, the slow humus pool is set from clay and silt, and `init_slow` is not used. Temperature equation 2 runs from -0.5 °C through an optimum of 30 °C to 50 °C, and the water factor is equation 1. Tillage affects decomposition for 100 days.

## Related files

- [`carbon_lyr.bsn`](carbon-lyr-bsn.md): decomposition rates and CO2 fractions for the surface and deeper layers.
- [`codes.bsn`](codes-bsn.md): `carbon = 2` turns the carbon model on; `idc_till` selects the tillage method.
- [`file.cio`](file-cio.md): names `carbon.bsn` on its `basin` line.
- [`parameters.bsn`](parameters-bsn.md): `rsd_decomp`, `rsd_decay`, `denit_exp` and `denit_frac` are also used by the carbon model.
- [`soils.sol`](sol.md): organic carbon, clay and silt of each layer.
- [`print.prt`](print-prt.md) and [carbon outputs](../output-reference/carbon.md): carbon output files, and the optional `carbon_layers.prt` that sets how many soil layers the per-layer carbon outputs contain.
- [Soil carbon](../model-theory/carbon.md): description of the carbon model.

??? quote "Sources"

    - Reader: [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90), called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Type definitions and module variables: `organic_fractions`, `carbon_water_coef`, `manure_coef`, `organic_controls` and the residue tunables in [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90); tillage variables in [`tillage_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/tillage_data_module.f90); `photo_degrade_factor` in [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90)
    - File name slot: `in_basin%carbon_bsn` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Pool initialisation: [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90), called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - Soluble carbon losses: [`nut_orgnc2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_orgnc2.f90)
    - Organic amendments: [`pl_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_fert.f90), [`pl_manure.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_manure.f90)
    - Tillage and mixing: [`mgt_tillfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_tillfactor.f90), [`mgt_biomix.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_biomix.f90), [`mgt_newtillmix_cswat1.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_cswat1.f90), tillage day counter in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Decomposition factors: [`cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90), [`fcgd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/fcgd.f90)
    - Residue decomposition: [`cbn_surfrsd_decomp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_surfrsd_decomp.f90)
    - `n_act_frac`: [`nut_nminrl.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/nut_nminrl.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `init_seq` | `org_frac%frac_seq` |
    | `init_microb` | `org_frac%frac_hum_microb` |
    | `init_slow` | `org_frac%frac_hum_slow` |
    | `init_passive` | `org_frac%frac_hum_passive` |
    | `koc_c` | `cb_wtr_coef%prmt_21` |
    | `solc_ratio` | `cb_wtr_coef%prmt_44` |
    | `till_eff_days` | `till_eff_days` (integer) |
    | `manure_c_frac` | `man_coef%rtof` |
    | `bio_consol` | `bio_consf` |
    | `till_consol` | `till_consf` |
    | `tmpf_eqn` | `org_con%tmpf` (integer) |
    | `watf_eqn` | `org_con%watf` (integer) |
    | `t_cbn_min`, `t_cbn_opt`, `t_cbn_max` | `org_con%tn`, `org_con%top`, `org_con%tx` |
    | `bmix_a`, `bmix_b`, `bmix_c` | `bmix_a`, `bmix_b`, `bmix_c` |
    | `tillmix_a`, `tillmix_b`, `tillmix_c` | `tillmix_a`, `tillmix_b`, `tillmix_c` |
    | `sfc_rsd_photodeg` | `photo_degrade_factor` |
    | `n_act_frac`, `cnr_cap`, `cnr_ref`, `cpr_cap`, `cpr_ref` | module variables of the same names |
    | `mathers_method` | `mathers_int`, stored as `org_frac%mathers_method = (mathers_int == 1)` |

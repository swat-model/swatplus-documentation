---
title: "Aquifer files (aquifer.aqu, initial.aqu)"
description: Properties of the one-dimensional aquifers listed in aquifer.aqu, and the initial-condition pointers of initial.aqu and initial.aqu_cs.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_aqu.f90
  - src/aqu_read.f90
  - src/aqu_initial.f90
  - src/aqu_read_init.f90
  - src/aqu_read_init_cs.f90
  - src/aquifer_module.f90
  - src/aqu_1d_control.f90
  - src/command.f90
  - src/hyd_read_connect.f90
  - src/hyd_connect.f90
  - src/cal_parm_select.f90
  - src/conditions.f90
  - src/actions.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`aquifer.aqu` contains the properties of the one-dimensional aquifers: initial water table, specific yield, baseflow recession, deep seepage, revap and groundwater nitrate and phosphorus. Each aquifer object in [`aquifer.con`](con.md) selects a row by number in its `aqu` column. The aquifer line of [`file.cio`](file-cio.md) names two files, `initial.aqu` and `aquifer.aqu` (in that order); either can be `null`.

A model has one aquifer object per row of [`aquifer.con`](../input-reference/con.md). Usually there is a shallow aquifer for each land area and one or more deep aquifers that receive the seepage of the shallow ones. Models that simulate groundwater with the [gwflow](gwflow.md) grid model use [`gwflow.con`](../input-reference/gwflow.md#gwflowcon) instead of these aquifers.

`initial.aqu` lists named sets of initial-condition files. In 62.0.1 its rows are read but not used; initial pesticides, pathogens, salts and constituents of aquifers come from `initial.aqu_cs`, described [below](#initialaqu_cs).

## aquifer.aqu

Free format, whitespace-separated. Line 1 is a title and line 2 the column header; both are skipped. Each later line is one aquifer property set with 18 values in this order. The reader does not match columns by header name.

| # | Column | Units | Built-in value | Typical range | Description |
|---|--------|-------|----------------|---------------|-------------|
| 1 | `id` | - | - | - | Number of the property set. The `aqu` column of [`aquifer.con`](../input-reference/con.md) refers to the row by this number. |
| 2 | `name` | - | - | - | Name of the aquifer. Not used by the model. |
| 3 | `init` | - | - | - | Name of an initial-condition set, matched against `initial.aqu_cs`. See [initial.aqu_cs](#initialaqu_cs). |
| 4 | `gw_flo` | mm | 0.05 | 0 to 2 | Return flow on the day before the simulation starts. It starts the recession, and sets the water volume for the initial nitrate mass. |
| 5 | `dep_bot` | m | 0 | 0 to 10 | Depth from the mid-slope surface to the bottom of the aquifer. Must be larger than `dep_wt`. |
| 6 | `dep_wt` | m | 0 | 0 to 10 | Initial depth from the mid-slope surface to the water table. |
| 7 | `no3_n` | mg N/L | 0 | 0 to 1000 | Initial nitrate-N concentration. |
| 8 | `sol_p` | mg P/L | 0 | 0 to 1000 | Mineral P concentration of the water entering the stream, constant through the run. |
| 9 | `carbon` | % | 0.5 | 0 to 15 | Organic carbon content. Reported in the aquifer output; not used in any calculation in 62.0.1. |
| 10 | `flo_dist` | m | 50 | 0 to 1000 | Average flow distance to the stream. Not used. |
| 11 | `bf_max` | mm | 0 | 0 to 2 | Return flow at which all channels linked to the aquifer receive groundwater. Used only when aquifer flow is distributed to channels with [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin). |
| 12 | `alpha_bf` | 1/day | 0 | 0 to 1 | Baseflow recession constant. |
| 13 | `revap` | - | 0 | 0 to 1 | Revap coefficient: revap as a fraction of potential evapotranspiration. |
| 14 | `rchg_dp` | fraction | 0 | 0 to 1 | Fraction of the day's recharge that leaves the aquifer as deep seepage. |
| 15 | `spec_yld` | m³/m³ | 0 | 0 to 0.4 | Specific yield: the volume of water drained by gravity per volume of aquifer. Must be above 0. |
| 16 | `hl_no3n` | days | 30 | 0 to 200 | Half-life of nitrate in the aquifer. |
| 17 | `flo_min` | m | 0 | 0 to 10 | Water table depth for return flow: the aquifer sends return flow only while the water table is at this depth below the surface or shallower. |
| 18 | `revap_min` | m | 0 | 0 to 10 | Water table depth for revap: revap occurs only while the water table is shallower than this depth. |

The built-in values apply when [`aquifer.con`](../input-reference/con.md) points to a number between 1 and the largest `id` that has no row in the file. They are not filled in for missing columns.

Give every row an `id`, and keep the ids unique. The ids do not have to be consecutive.

## Aquifer water balance

Each day, for each aquifer, in this order. Depths of water are in mm over the aquifer area (the `area` column of [`aquifer.con`](../input-reference/con.md)).

### Storage and water table

At the start of the run the stored water is

$$S_0 = 1000\,(\mathrm{dep\_bot} - \mathrm{dep\_wt})\;\mathrm{spec\_yld}$$

Each day the recharge $R$, all water routed into the aquifer from HRUs, routing units and other aquifers, is added to storage, and withdrawals for water allocation are then taken. Irrigation drawn from the aquifer by decision tables is removed from storage when it is applied. The water table depth follows from the storage:

$$h = \max\!\left(0,\ \mathrm{dep\_bot} - \frac{S}{1000\;\mathrm{spec\_yld}}\right)$$

The aquifer calculation in 62.0.1 has no recharge delay: recharge is added on the day it arrives.

### Return flow

When $h \le$ `flo_min`, return flow follows the baseflow recession

$$Q_d = Q_{d-1}\,e^{-\alpha} + R_d\,\left(1 - e^{-\alpha}\right)$$

limited to between zero and the storage, where $\alpha$ is `alpha_bf`. When $h >$ `flo_min`, $Q_d = 0$, and the next day's recession starts from zero.

The recession constant is a direct index of how fast groundwater flow responds to recharge (Smedema and Rycroft, 1983). Values are about 0.1 to 0.3 for land with a slow response and 0.9 to 1.0 for land with a rapid response. It is best estimated from measured streamflow during periods without recharge. When the number of baseflow days $BFD$ (the days for baseflow to decline through one log cycle) is known,

$$\alpha = \frac{1}{BFD}\,\ln 10 = \frac{2.3}{BFD}$$

Return flow leaves through the outflows of type `tot` in [`aquifer.con`](../input-reference/con.md).

### Deep seepage

$$\mathrm{seep}_d = \mathrm{rchg\_dp}\;R_d$$

limited to the storage. Seepage leaves through the outflows of type `rhg` in [`aquifer.con`](../input-reference/con.md), usually to a deep aquifer. Without such an outflow it leaves the model.

### Revap

When $h <$ `revap_min`,

$$\mathrm{revap}_d = \mathrm{revap}\;PET_d$$

limited to the storage, where $PET_d$ is the potential evapotranspiration at the aquifer's weather station (mm). Revap represents water that moves from the aquifer into the unsaturated zone above it when that zone is dry, and uptake by deep-rooted plants. It is removed from the aquifer and not added to the soil. As `revap` approaches 0, the transfer is restricted; as it approaches 1, revap approaches the potential evapotranspiration.

## Nitrate and phosphorus

Nitrate recharge is added to the stored nitrate $N$ (kg/ha). The concentration is $c = N/S$, and the nitrate leaving with return flow and seepage is $c\,Q$ and $c\,\mathrm{seep}$. Each day the remaining nitrate decays by

$$N \leftarrow N\,\exp\!\left(\frac{-0.693}{\mathrm{hl\_no3n} + 0.1}\right)$$

The decay represents uptake by bacteria and chemical conversion where the aquifer is depleted of oxygen; it is the net loss from all processes.

The initial nitrate mass is $10\,\mathrm{gw\_flo}\,A\,\mathrm{no3\_n}/1000$, the concentration times the volume of one day's initial return flow ($A$ in ha). This is a mass in kg for the whole aquifer, but the daily calculation treats the store as kg/ha, so the initial store scales with the aquifer area. It does not use the stored water $S_0$.

Soluble P in the return flow is $\mathrm{sol\_p}$ times the day's recharge volume (m³), divided by 1000, in kg. The load therefore follows the recharge. It appears on days with recharge even when there is no return flow, and is zero on days without recharge. The aquifer stores no phosphorus between days.

## Pesticides, salts and constituents

Pesticides entering with recharge are added to the aquifer store and decay with the aquifer half-life of [`pesticide.pes`](pes.md) (adjusted to temperature when the temperature decay option is on). The concentration is the stored mass divided by $f\,S + Q + \mathrm{revap} + \mathrm{seep}$, where $f$ is the pesticide groundwater mixing factor of [`parameters.bsn`](parameters-bsn.md). Return flow and seepage take pesticide out at that concentration, all of it dissolved. Revap takes none.

Salts and other constituents (see [`salt`](salt.md) and [`cs`](cs.md)) are mixed in the stored water and leave with return flow and seepage at the stored concentration.

## Aquifer flow to channels with aqu_cha.lin

When [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) links aquifers to channels (see [`file.cio`](file-cio.md)), the return flow is spread over the linked channels as each channel is routed: on the same day when the aquifer comes before the channel in the routing order, otherwise on the next day. The length of channel that receives flow is the total linked channel length times $Q/\mathrm{bf\_max}$; when $Q \ge$ `bf_max` all linked channels receive flow, and when it is lower only part of the channel length does, each channel in proportion to its length. Set `bf_max` to a value above zero whenever [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) is used.

## Calibration and decision tables

These parameters can be changed during calibration through [`calibration.cal`](../calibration/parameter-change-files.md) (see [parameter change files](../calibration/parameter-change-files.md)): `flo_init_mm` (`gw_flo`), `dep_bot`, `dep_wt_init` (`dep_wt`), `no3_init` (`no3_n`), `minp_init` (`sol_p`), `cbn_init` (`carbon`), `flo_dist`, `bf_max`, `alpha` (`alpha_bf`), `revap_co` (`revap`), `deep_seep` (`rchg_dp`), `sp_yld` (`spec_yld`), `hlife_n` (`hl_no3n`), `flo_min` and `revap_min`.

Calibration changes are applied after the aquifers are initialised. A change to `sp_yld` recalculates the storage from the current water table, and a change to `no3_init` recalculates the nitrate mass. Changes to `flo_init_mm` and `dep_wt_init` come too late to change the initial state and have no effect. A change to `dep_bot` does not change the stored water; it moves the water table that is calculated from it.

The decision table condition `aqu_dep` tests the water table depth of an aquifer (m). See [decision tables](dtl.md).

## initial.aqu

Named sets of initial-condition files, in the same layout as [`initial.cha`](cha.md#initialcha). Two header lines are skipped, then one set per line. The Editor adds a trailing `description` value, which the reader ignores.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Name of the set. |
| 2 | `org_min` | Name of an organic-mineral initial record. |
| 3 | `pest` | Name of a pesticide initial record. |
| 4 | `path` | Name of a pathogen initial record. |
| 5 | `hmet` | Name of a heavy metal initial record. |
| 6 | `salt` | Name of a salt initial record. |

In 62.0.1 the rows are read and nothing is done with them: the `init` column of `aquifer.aqu` is not matched against this file, and the aquifer's initial water and nitrate come from `aquifer.aqu`.

## initial.aqu_cs

An optional file with a fixed name, read when present. Two header lines are skipped, then one row per line with six names: `name`, `pest`, `path`, `hmet`, `salt` and `cs`.

- `pest` names a row in [`pest_water.ini`](pes.md). The initial pesticide in the aquifer (kg/ha) is the water concentration (mg/kg) times an assumed bulk density of 2.0 t/m³ times `dep_bot` times 10.
- `path` names a row in [`path_water.ini`](pth.md).
- `hmet` is read but not used.
- `salt` names a row in [`salt_aqu.ini`](salt.md): initial salt ion concentrations (g/m³) and salt mineral fractions.
- `cs` names a row in [`cs_aqu.ini`](cs.md): initial constituent concentrations (g/m³) and sorbed concentrations (mg/kg).

Pesticide and pathogen rows are selected by matching `name` with the `init` column of `aquifer.aqu`. Salt and constituent rows are selected by position instead: aquifer 3 (the third row of [`aquifer.con`](../input-reference/con.md)) uses row 3 of `initial.aqu_cs`, whatever its name. Salt and constituent masses are the concentrations times the initial stored water.

## Example

`refdata/Osu_1hru` in the SWAT+ repository:

```
aquifer.aqu: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
      id  name                          init        gw_flo       dep_bot        dep_wt         no3_n         sol_p        carbon      flo_dist        bf_max      alpha_bf         revap       rchg_dp      spec_yld       hl_no3n       flo_min     revap_min
       1  aqu011                    initaqu1       0.05000      10.00000       6.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.95000       0.02000       0.01000       0.05000       0.00000       5.00000       5.00000
       2  aqu012                    initaqu1       0.05000      10.00000       6.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.95000       0.02000       0.01000       0.05000       0.00000       5.00000       5.00000
      21  aqu_deep010               initaqu1       0.00000      10.00000      20.00000       0.00000       0.00000       0.50000      50.00000       1.00000       0.91000       0.00000       0.00000       0.03000       0.00000       0.00000       0.00000
```

(three of the 21 rows)

The shallow aquifers start with the water table 6 m below a 10 m deep aquifer, so they contain $1000 \times (10 - 6) \times 0.05 = 200$ mm of water. Return flow and revap both need the water table within 5 m of the surface, so neither occurs until recharge raises it by 1 m (50 mm of storage). The recession constant of 0.95 1/day gives a fast response. One percent of recharge goes to deep seepage. `hl_no3n` is 0, which gives a daily nitrate decay factor of $e^{-6.93}$, so nearly all nitrate entering the aquifer is lost on the day it arrives.

The deep aquifer `aqu_deep010` has `dep_wt` = 20 m, below its `dep_bot` of 10 m, so its initial storage is negative ($1000 \times (10 - 20) \times 0.03 = -300$ mm) and the water table starts 20 m down. It is recharged by the seepage the shallow aquifers send to it. With `flo_min` = 0 it sends return flow only when the water table reaches the surface, and with `revap_min` = 0 it has no revap.

```
initial.aqu: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description
initaqu1                   no_init              null              null              null              null  null
```

## Related files

- [`aquifer.con`](con.md): the aquifer objects, their areas, the `aqu` pointer to `aquifer.aqu` and the `tot` and `rhg` outflows.
- [`file.cio`](file-cio.md): the aquifer line, and [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) on the link line.
- [`pest_water.ini`](pes.md), [`path_water.ini`](pth.md), [`salt_aqu.ini`](salt.md), [`cs_aqu.ini`](cs.md): initial constituents referenced from `initial.aqu_cs`.
- [gwflow](gwflow.md): the grid groundwater model used instead of these aquifers.
- Outputs: [aquifer output files](../output-reference/aquifer-reservoir-plant.md) (`aquifer_day` and others).
- [Aquifers](../model-theory/aquifers.md) in the model theory.

??? quote "Sources"

    - File name slots: `type input_aqu` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90); read order in [`proc_aqu.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_aqu.f90)
    - Readers: [`aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read.f90) (`aquifer.aqu`), [`aqu_read_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init.f90) (`initial.aqu`), [`aqu_read_init_cs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read_init_cs.f90) (`initial.aqu_cs`)
    - Type definitions: `aquifer_database`, `aquifer_data_parameters`, `aquifer_dynamic`, `aquifer_init_data_char` and `aquifer_init_data_char_cs` in [`aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aquifer_module.f90)
    - Initialisation: [`aqu_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_initial.f90)
    - Daily calculation: [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)
    - `aquifer.con` pointer and outflow types: [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90), [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90); decision tables: [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `id` | index of `aqudb` |
    | `name` | `aqudb%aqunm` |
    | `init` | `aqudb%aqu_ini` |
    | `gw_flo` | `aqudb%flo` |
    | `dep_bot` | `aqudb%dep_bot` |
    | `dep_wt` | `aqudb%dep_wt` |
    | `no3_n` | `aqudb%no3` |
    | `sol_p` | `aqudb%minp` |
    | `carbon` | `aqudb%cbn` |
    | `flo_dist` | `aqudb%flo_dist` |
    | `bf_max` | `aqudb%bf_max` |
    | `alpha_bf` | `aqudb%alpha` |
    | `revap` | `aqudb%revap_co` |
    | `rchg_dp` | `aqudb%seep` |
    | `spec_yld` | `aqudb%spyld` |
    | `hl_no3n` | `aqudb%hlife_n` |
    | `flo_min` | `aqudb%flo_min` |
    | `revap_min` | `aqudb%revap_min` |

    `aqudb` is copied to `aqu_dat(iaq)` for each aquifer object in `aqu_initial`; `initial.aqu` rows go to `aqu_init_dat_c`, `initial.aqu_cs` rows to `aqu_init_dat_c_cs`.

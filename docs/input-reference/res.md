---
title: "*.res (reservoir)"
description: Reservoir object table and the initial-condition, hydrology, sediment, nutrient and weir databases it references.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/main.f90.in
  - src/proc_res.f90
  - src/res_read.f90
  - src/res_read_init.f90
  - src/res_read_hyd.f90
  - src/res_read_sed.f90
  - src/res_read_nut.f90
  - src/res_read_weir.f90
  - src/res_read_conds.f90
  - src/res_rel_conds.f90
  - src/dtbl_res_read.f90
  - src/reservoir_data_module.f90
  - src/reservoir_module.f90
  - src/res_objects.f90
  - src/res_allo.f90
  - src/res_initial.f90
  - src/res_control.f90
  - src/res_hydro.f90
  - src/res_sediment.f90
  - src/res_nutrient.f90
  - src/res_pest.f90
  - src/theta.f90
  - src/conditions.f90
  - src/actions.f90
  - src/hydrograph_module.f90
  - src/cal_parm_select.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Reservoirs are impoundments on the channel network. They receive water, sediment and nutrients from upstream objects and release to downstream objects through a release rule. Ponds that are routed as separate objects use the same files. The reservoir group has six files, named on the `reservoir` line of [`file.cio`](file-cio.md) in this order:

| Slot | Default name | Content |
|------|--------------|---------|
| 1 | `initial.res` | Named initial-condition sets for reservoirs and wetlands |
| 2 | `reservoir.res` | One row per reservoir, naming the records below |
| 3 | `hydrology.res` | Reservoir hydrology: spillway areas and volumes, seepage, evaporation, outflow smoothing |
| 4 | `sediment.res` | Sediment settling parameters, shared with wetlands |
| 5 | `nutrients.res` | Nutrient settling parameters, shared with wetlands |
| 6 | `weir.res` | Weir discharge parameters, used by `weir` release rules and by wetlands |

Slots 7 and 8 of the same line name the wetland files [`wetland.wet` and `hydrology.wet`](wet.md). A slot set to `null`, or a file that does not exist, leaves that table empty.

`reservoir.res` refers to the other files by name. The release rule named in `reservoir.res` is a decision table in [`res_rel.dtl`](../input-reference/dtl.md) (see [decision tables](dtl.md)) or, for names starting with `ctbl_`, a conditions table in `res_conds.dat`.

The five databases are read in every run. `reservoir.res` is read, and the reservoirs are set up, only when [`object.cnt`](object-cnt.md) gives one or more reservoirs. `weir.res` is read before the decision tables, so that `weir` actions in [`res_rel.dtl`](../input-reference/dtl.md) can find their weir record.

All files are free format and whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. The readers do not match columns by header name, so every row needs all of its values in the order given below. Columns after the last one listed (for example the `description` column the SWAT+ Editor writes) are ignored. Names must match, including case.

## reservoir.res

One row per reservoir.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Reservoir number. The row with `id` *n* is used for reservoir *n*, the *n*th reservoir in [`reservoir.con`](con.md). Numbers must run from 1 to the number of rows. |
| 2 | `name` | - | Reservoir name. Not used by the model. |
| 3 | `init` | - | Name of a row in `initial.res`. |
| 4 | `hyd` | - | Name of a row in `hydrology.res`. |
| 5 | `rel` | - | Release rule. A decision table name in [`res_rel.dtl`](../input-reference/dtl.md), or a name starting with `ctbl_` for a conditions table in `res_conds.dat`. |
| 6 | `sed` | - | Name of a row in `sediment.res`. |
| 7 | `nut` | - | Name of a row in `nutrients.res`. |

A name that is not found is reported in `diagnostics.out` as `<name> not found (res-hyd)`, `(res-release)`, `(res-sed)` or `(res-nut)`, and the reservoir keeps zero or built-in values for that part. An unmatched `rel` gives an empty release table, so the reservoir releases no water through its rule. An unmatched `init` is not reported; the reservoir then starts from the first row of [`om_water.ini`](../input-reference/ini.md#om_waterini).

`hyd`, `sed` and `nut` are taken from the row whose `id` equals the reservoir number. `init` and `rel` are taken from the row named by the reservoir's parameter pointer in column 8 of [`reservoir.con`](../input-reference/con.md). The SWAT+ Editor writes the same number in both places, so the two agree in Editor-built projects.

## initial.res

Named initial-condition sets, shared by reservoirs (`init` in `reservoir.res`) and wetlands (`init` in [`wetland.wet`](wet.md)).

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the initial-condition set. |
| 2 | `org_min` | - | Name of a row in [`om_water.ini`](ini.md): initial water volume and concentrations. |
| 3 | `pest` | - | Name of a row in [`pest_water.ini`](../input-reference/pes.md#pest_waterini): initial pesticides in water and benthic sediment. |
| 4 | `path` | - | Name of a pathogen initialization row. |
| 5 | `hmet` | - | Heavy-metal initialization. Read; not used. |
| 6 | `salt` | - | Salt initialization. Read; not used. Reservoir and wetland salts come from the [salt input files](salt.md). |

`org_min`, `pest` and `path` names that are not found fall back to the first row of the referenced file, without a message.

The initial water volume is the `flo` value of the [`om_water.ini`](../input-reference/ini.md#om_waterini) row, a fraction of the principal spillway volume. The concentrations in that row are converted to masses with this volume. A reservoir that is not yet operational at the start of the run (see [Operation start](#operation-start)) starts empty instead.

## hydrology.res

One row per hydrology record.

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `name` | - | - | Name of the hydrology record, matched against `hyd` in `reservoir.res`. |
| 2 | `yr_op` | year | - | Calendar year in which the reservoir becomes operational. Whole number. |
| 3 | `mon_op` | month | - | Month of `yr_op` in which the reservoir becomes operational. Whole number. |
| 4 | `area_ps` | ha | 0.08 × `vol_ps` | Surface area at the principal spillway. |
| 5 | `vol_ps` | ha-m | 0.9 × `vol_es`, or 60000 | Volume of water needed to fill the reservoir to the principal spillway. |
| 6 | `area_es` | ha | 1.5 × `area_ps` | Surface area at the emergency spillway. |
| 7 | `vol_es` | ha-m | 1.11 × `vol_ps` | Volume of water needed to fill the reservoir to the emergency spillway. |
| 8 | `k` | mm/hr | - | Hydraulic conductivity of the reservoir bottom. Use 0 for no seepage. Typical range 0 to 1. |
| 9 | `evap_co` | - | 0.6 | Evaporation coefficient, a multiplier on potential evapotranspiration. Typical range 0 to 1. |
| 10 | `shp_co1` | - | - | Smoothing factor for rising outflow. See [Outflow smoothing](#outflow-smoothing). |
| 11 | `shp_co2` | - | - | Smoothing factor for falling outflow. See [Outflow smoothing](#outflow-smoothing). |

The Default column gives the value the reader puts in when the column is zero or negative. The rules are applied in this order: if `vol_ps` is not positive, it becomes 0.9 × `vol_es` when `vol_es` is positive and 60000 ha-m otherwise; then `vol_es`, `area_ps`, `area_es` and `evap_co` are filled in as listed. The `area_ps` default corresponds to a mean depth of 12.5 m at the principal spillway.

Principal spillway values describe the normal storage of the reservoir, and emergency spillway values its maximum storage. The volumes are converted from ha-m to m³ (× 10000) when the reservoirs are set up.

A reservoir whose `hyd` name is not found has zero spillway areas and volumes.

### Operation start

A reservoir is operational from month `mon_op` of calendar year `yr_op`. Before then it passes its inflow straight through to its downstream objects and keeps no storage. `yr_op` is compared with the calendar year, so a value of 0, or any year before the start of the simulation, makes the reservoir operational from the first day. Only reservoirs that are operational on the first day get the initial storage from `initial.res`; one that starts later begins empty.

### Surface area

Each day the surface area $A$ (ha) is calculated from the storage $V$ (m³):

$$A = \beta_1\, V^{\beta_2}$$

The coefficients are set once at the start of the run from the spillway values, with volumes in m³. When `area_es` is larger than `area_ps` and `vol_es` is larger than `vol_ps`,

$$\beta_2 = \frac{\log_{10} \mathrm{area\_es} - \log_{10} \mathrm{area\_ps}}{L}, \qquad \beta_1 = \left(\frac{\mathrm{area\_es}}{\mathrm{vol\_es}}\right)^{\beta_2}$$

where $L$ is the whole-number part of $\log_{10} \mathrm{vol\_es} - \log_{10} \mathrm{vol\_ps}$. When $L$ is 0 the divisor 0.001 is used instead. $\beta_2$ is limited to 0.9, and when the limit applies $\beta_1 = (\mathrm{area\_ps}/\mathrm{vol\_ps})^{0.9}$. In all other cases $\beta_2 = 0.9$ and $\beta_1 = (\mathrm{area\_ps}/\mathrm{vol\_ps})^{0.9}$.

In 62.0.1 $L$ is 0 unless the emergency volume is at least ten times the principal volume. For almost every reservoir, then, $\beta_2 = 0.9$ and the relation reduces to

$$A = \left(\mathrm{area\_ps}\,\frac{V}{\mathrm{vol\_ps}}\right)^{0.9}$$

At the principal spillway this curve gives $\mathrm{area\_ps}^{0.9}$: 63 ha for an `area_ps` of 100 ha. The surface area sets precipitation on the reservoir, evaporation and seepage, so `area_ps` and `area_es` act on the water balance only through this relation.

### Daily water balance

On each day of operation the reservoir:

1. adds the inflow from upstream objects to storage;
2. calculates the release from its release rule, using the storage after inflow, and smooths it (decision tables only);
3. settles sediment (decision tables only);
4. adds precipitation $P = 10\,R\,A$ (m³, with $R$ the day's precipitation in mm);
5. subtracts the release, limited to the water in storage;
6. subtracts evaporation $E = 10\;\mathrm{evap\_co}\;PET\;A$ (m³, with $PET$ the day's potential evapotranspiration in mm), limited to storage;
7. subtracts seepage $S = 240\,k\,A$ (m³, $k$ in mm/hr), limited to storage;
8. updates the surface area from the new storage and calculates nutrient settling and the nutrient load in the release.

Precipitation and potential evapotranspiration come from the weather station assigned to the reservoir in [`reservoir.con`](../input-reference/con.md). When gwflow is active, seepage is exchanged with the groundwater model and `k` is not used (see [gwflow](gwflow.md)).

### Outflow smoothing

For release by decision table, the release $Q$ is smoothed against the previous day's release $Q_{d-1}$ to soften jumps when the rule switches between alternatives:

$$Q_d = \alpha\,Q + (1 - \alpha)\,Q_{d-1}, \qquad \alpha = \begin{cases} e^{-\mathrm{shp\_co1}} & Q > Q_{d-1} \\ e^{-\mathrm{shp\_co2}} & \text{otherwise} \end{cases}$$

With both factors at 0 there is no smoothing. Larger values give more weight to the previous day. The columns keep the names `shp_co1` and `shp_co2` from earlier versions, where they were surface-area shape coefficients. In 62.0.1 the shape coefficients are always calculated by the model as described above and cannot be entered.

## Release rules

The `rel` column of `reservoir.res` selects how the reservoir releases water.

### Decision tables

A decision table in [`res_rel.dtl`](../input-reference/dtl.md) evaluates its conditions each day (storage relative to the principal or emergency volume, month, inflow and others; see [decision tables](dtl.md)) and applies the `release` actions of the alternatives that are met. The `option` field of each action gives the method. Releases from several actions that apply on the same day are added.

| `option` | Release per day |
|----------|-----------------|
| `rate` | `const` m³/s. |
| `rate_pct` | `const` percent of the principal volume. |
| `inflo_rate` | The larger of inflow plus `const2` m³/s and `const` m³/s. |
| `inflo_frac` | Inflow multiplied by `const`. |
| `ab_emer` | All storage above the emergency volume. |
| `days` | (storage minus a base volume) / `const`, where `const` is the number of drawdown days. The base volume is 0 when `fp` is `null`, `const2` × principal volume when `fp` is `pvol`, and `const2` × emergency volume when `fp` is `evol`. |
| `dyrt` | (storage minus base volume) / `const` plus `const2` percent of the principal volume. The base volume is 0, the principal volume or the emergency volume for `fp` = `null`, `pvol` or `evol`. |
| `dyrt1` | As `dyrt`, with the base volume taken from condition 5, 4 or 3 of the table for `fp` = `con1`, `con2` or `con3`. |
| `inflo_targ` | Inflow plus storage above a target, where the target is the principal volume multiplied by the limit constant of the condition numbered `const`. |
| `weir` | Weir equation with the `weir.res` row named in `fp`. See [weir.res](#weirres). |
| `meas` | Measured outflow from the [recall](recall.md) record named in `fp` (daily, monthly or annual). |
| `natlake` | Natural lake outflow after Döll et al. (2003): $Q = k_r\,S_e\,\left(S_e / (V_p - S_0)\right)^{1.5}$ with dead storage $S_0$ = `const` × principal volume, $S_e$ the storage above $S_0$, $V_p$ the principal volume and $k_r$ = `const2` (1/day). |
| `nonirr-h06`, `irr-h06` | Hanazaki et al. (2006) operating rules for non-irrigation and irrigation reservoirs. |
| `hydrop` | Hydropower rule after Arheimer et al. (2019). |

For `days`, the base volume is `const2` times the spillway volume, so an action with `fp` set to `pvol` and `const2` set to 0 draws the reservoir down toward empty. Set `const2` to 1 to draw down to the principal volume.

The `nonirr-h06`, `irr-h06` and `hydrop` options base the release on a five-year record of monthly mean inflow (and, for `irr-h06`, irrigation demand) that each reservoir keeps during the run. In 62.0.1 this record is never filled and stays at zero, so `nonirr-h06` and `hydrop` release no water and `irr-h06` gives an undefined release (zero divided by zero).

In sub-daily runs the actions are applied once for each time step of the day. `days`, `dyrt` (its percentage term) and `meas` divide their daily amount by the number of steps; the other options add their full daily amount at every step. The `weir` option replaces the release with one time step's weir flow at each step.

For a reservoir, the `weir` option takes the weir crest height from the wetland data of the HRU with the same number as the reservoir. When that HRU has no wetland the crest height is zero, so the whole water depth (storage divided by surface area) acts as head. The `height` column of `weir.res` and the `weir_height` decision table action do not change the crest height that the reservoir weir release uses.

### Conditions tables

A `rel` name starting with `ctbl_` is looked up in `res_conds.dat`, a file with a fixed name that is read when it exists in the run directory. The release is the value given by the matching condition of the table. Outflow smoothing and sediment settling are not applied to these reservoirs, and their release contains no sediment.

## sediment.res

One row per sediment record. Reservoirs refer to it through `sed` in `reservoir.res`, wetlands through `sed` in [`wetland.wet`](../input-reference/wet.md#wetlandwet).

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the sediment record. |
| 2 | `sed_amt` | mg/L | Equilibrium (normal) suspended sediment concentration. Settling occurs only above this concentration. Typical range 1 to 5000. |
| 3 | `d50` | µm | Median particle size of suspended and benthic sediment. Sets the settling rate. |
| 4 | `carbon` | % | Organic carbon in suspended and benthic sediment. Used in pesticide partitioning. |
| 5 | `bd` | t/m³ | Bulk density of benthic sediment. Used in pesticide partitioning between water and benthic sediment. |
| 6 | `sed_stl` | - | Sediment settling rate. Read but not used. |
| 7 | `stl_vel` | m/day | Sediment settling velocity. Read but not used. |

### Sediment settling

Each day, when the sediment concentration $C$ (mg/L) in the reservoir is above the equilibrium concentration $C_{eq}$ (`sed_amt`), the excess settles at a rate set by the median particle size:

$$C' = (C - C_{eq})\,e^{-0.184\,d_{50}} + C_{eq}$$

With `d50` at 10 µm, 16% of the excess concentration remains after one day; at 2 µm, 69% remains. The release takes sediment at the concentration $C'$, and all silt, clay, sand and aggregate fractions in the reservoir settle.

When the concentration is at or below `sed_amt`, nothing settles and the release takes no sediment that day.

Median particle sizes of sediment classes: clay 1.95 µm, fine silt 4.9 µm, medium silt 11.7 µm, coarse silt 47 µm, fine sand 94 µm, medium sand 375 µm, coarse sand 1500 µm. A reservoir receives sediment from its whole upstream area, so a representative value for that area suits it better than the texture of one HRU.

## nutrients.res

One row per nutrient record. Reservoirs refer to it through `nut` in `reservoir.res`, wetlands through `nut` in [`wetland.wet`](../input-reference/wet.md#wetlandwet).

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the nutrient record. |
| 2 | `mid_start` | month | First month of the mid-year settling period. Whole number, 1 to 12. |
| 3 | `mid_end` | month | Last month of the mid-year settling period. Whole number, 1 to 12. |
| 4 | `mid_n_stl` | m/year | Organic nitrogen settling rate in the mid-year period. |
| 5 | `n_stl` | m/year | Organic nitrogen settling rate in the rest of the year. |
| 6 | `mid_p_stl` | m/year | Particulate phosphorus settling rate in the mid-year period. |
| 7 | `p_stl` | m/year | Particulate phosphorus settling rate in the rest of the year. |
| 8 | `chla_co` | m/year | Loss rate for soluble nitrogen (nitrate, ammonium and nitrite). |
| 9 | `secchi_co` | m/year | Loss rate for soluble phosphorus. |
| 10 | `theta_n` | - | Temperature adjustment factor for nitrogen losses. |
| 11 | `theta_p` | - | Temperature adjustment factor for phosphorus losses. |
| 12 | `n_min_stl` | mg/L | Nitrogen concentration below which no nitrogen is lost. |
| 13 | `p_min_stl` | mg/L | Phosphorus concentration below which no phosphorus is lost. |

The Editor headers `chla_co` and `secchi_co` come from older versions, where these columns were a chlorophyll-a coefficient and a water clarity coefficient. In 62.0.1 they are the soluble nitrogen and phosphorus loss rates. Chlorophyll-a and Secchi depth are not calculated from them.

The six rates are entered in m/year and divided by 365 when the file is read.

### Nutrient losses

The mid-year rates apply in the months from `mid_start` to `mid_end`, and the other rates in the remaining months. The test is `mid_start` ≤ month ≤ `mid_end`, so a period that runs across the end of the year (for example November to March) never applies and the other rates are used all year. To use one rate all year, give both columns the same value.

Each day the fraction of organic nitrogen lost is

$$k_N = \frac{\mathrm{mid\_n\_stl}}{365}\;\theta_N^{\,T-20}\,(C_N - C_{N,min})$$

limited to between 0 and 1, where $C_N$ is the organic nitrogen concentration (mg/L), $C_{N,min}$ is `n_min_stl`, $\theta_N$ is `theta_n` and $T$ is the day's mean air temperature (°C) at the weather station. Particulate phosphorus is treated the same way with `mid_p_stl` or `p_stl`, `theta_p` and `p_min_stl`. The organic nitrogen and particulate phosphorus masses are multiplied by $1 - k$.

Soluble nitrogen uses `chla_co` and the total soluble nitrogen concentration, and soluble phosphorus uses `secchi_co`. For these, the loss fraction is multiplied by a fixed 0.2 before it is applied to nitrate, ammonium, nitrite and soluble phosphorus.

The rate is multiplied by a concentration difference and the result is used as a fraction, so the units of the product do not match: a value of 1 m/year acts as a daily fraction of 1/365 per mg/L of excess concentration. The fraction cannot go below zero, so negative rates give no loss and the sediment never becomes a source of nutrients.

The release takes each nutrient in proportion to its share of the water: release / (storage + release).

Measured apparent settling velocities for phosphorus in natural lakes most often lie between 5 and 20 m/year, with reported values from below 1 to over 200 m/year (Chapra, 1997). Reservoirs show a wider range: Higgins and Kim (1981) reported −90 to 269 m/year for 18 reservoirs in Tennessee (median 42.2 m/year), and Walker and Kiihner (1978) reported −1 to 125 m/year for 27 Midwestern reservoirs (mean 12.7 m/year). Panuska and Robertson (1999) recommend these values:

| Water body nutrient dynamics | Settling velocity (m/year) |
|------------------------------|----------------------------|
| Shallow, high net internal phosphorus flux | 0 or less |
| Moderate net internal phosphorus flux | 1 to 5 |
| Minimal net internal phosphorus flux | 5 to 16 |
| High net internal phosphorus removal | more than 16 |

In 62.0.1 values of 0 or less give no phosphorus loss.

## weir.res

One row per weir record. A reservoir uses a weir record through a `weir` action in its release decision table (the record named in the action's `fp` field). Wetlands use weir records as described under [storage volumes and weir height](wet.md#storage-volumes-and-weir-height) on the wetland page.

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name of the weir record. |
| 2 | `linear_c` | - | 1.84 | Weir discharge coefficient $c$. |
| 3 | `exp_k` | - | 2.6 | Weir discharge exponent $k$. |
| 4 | `width` | m | 2.5 | Weir width $w$. |
| 5 | `height` | m | 0 | Height of the weir crest above the bottom of the impoundment. Used for wetlands only. |

The built-in values apply when a `weir` action names a record that is not in the file.

The weir discharge is

$$Q = 0.45\,A\,c\,w\,H^{k}$$

in m³/s, where $A$ is the surface area of the water body (ha) and $H$ is the water depth above the weir crest (m). In daily runs the discharge is applied hour by hour for up to 24 hours, each hour limited to the water above the crest, and the depth is updated after each hour.

## Calibration

These reservoir parameters can be changed through [`calibration.cal`](../calibration/parameter-change-files.md): `psa`, `pvol`, `esa` and `evol` (spillway areas in ha and volumes in m³), `k_res` (`k`), `evrsv` (`evap_co`), `nsed` (`sed_amt`), `res_d50` (`d50`), `sed_stlr` (`sed_stl`), `velsetlr` (`stl_vel`), `nsetlr1`, `nsetlr2`, `psetlr1`, `psetlr2` (the four settling rates), `nsolr` (`chla_co`), `psolr` (`secchi_co`), `soln_stl_fr` and `solp_stl_fr` (the fixed 0.2 factors), the storage and constituent masses `vol`, `sed`, `orgn`, `orgp`, `no3`, `nh3`, `no2` and `solp`, and the release-table constants `drawdown_days` (`const`) and `withdraw_rate` (`const2`).

Calibration acts on the values after unit conversion, so settling rates are changed in m/day. Changing `psa`, `pvol`, `esa` or `evol` does not recalculate the surface area coefficients.

## Example

`refdata/Osu_1hru` in the SWAT+ repository has no reservoirs. Its sediment, nutrient, weir and initial-condition files are used by its wetland, and show the formats.

`initial.res`:

```
initial.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                       org_min              pest              path              hmet              salt  description
initwet1                   no_init              null              null              null              null  null
```

`sediment.res`:

```
sediment.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   sed_amt           d50        carbon            bd       sed_stl       stl_vel
sedwet1                  10.00           5.00       0.04            0.8          0.15       0.0002
```

Sediment settles above 10 mg/L. With `d50` at 5 µm, 40% of the excess remains after one day.

`nutrients.res`:

```
nutrients.res: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name              mid_start   mid_end     mid_n_stl         n_stl     mid_p_stl         p_stl       chla_co     secchi_co       theta_n       theta_p     n_min_stl     p_min_stl
nutwet1                  5        10       5.50000       5.50000      10.00000      10.00000       1.00000       1.00000       1.00000       1.00000       0.10000       0.01000
```

The mid-year period is May to October, but the two rates for each nutrient are equal, so one rate applies all year. Both `theta` values are 1, so the losses do not depend on temperature.

`weir.res`:

```
weir.res: Reservoir weir inputs - asdf;lj
NAME   Linear_C    Exp_K     Width(m)	Depth(m)
weir1   1.83 	   1.50   	 5.00 		0.0
```

The header line here differs from the Editor's. It is skipped, so only the order of the values matters.

A `hydrology.res` and `reservoir.res` pair for one reservoir, written for illustration:

```
hydrology.res: example
name        yr_op  mon_op   area_ps   vol_ps   area_es   vol_es      k   evap_co  shp_co1  shp_co2
hydres1         0       0     150.0   1500.0     200.0   2200.0   0.05      0.60     0.00     0.00
```

```
reservoir.res: example
id   name      init      hyd       rel             sed      nut
1    res001    initres1  hydres1   drawdown_days   sedres1  nutres1
```

The reservoir is operational from the start. Its principal volume is 1500 ha-m (15 million m³). Because `vol_es` is less than ten times `vol_ps`, the surface area follows $A = (150\,V / 1.5\times10^{7})^{0.9}$, which gives 91 ha at the principal spillway. Outflow is not smoothed. Seepage is $240 \times 0.05 \times A$ m³ per day.

The `drawdown_days` table in `refdata/Osu_1hru/res_rel.dtl`:

```
name                     conds      alts      acts
drawdown_days                2         2         2
var                        obj   obj_num           lim_var            lim_op     lim_const      alt1      alt2
vol                        res         0              pvol                 *       1.00000         >         -
vol                        res         0              evol                 *       1.00000         <         >
act_typ                    obj   obj_num              name            option         const        const2                fp  outcome
release                    res         0         over_prin              days      15.00000       0.00000              pvol  y   n
release                    res         0    over_emergency              days       5.00000       0.00000              evol  n   y
```

Between the principal and emergency volumes the reservoir releases storage / 15 per day; above the emergency volume, storage / 5 per day. Below the principal volume no alternative applies and nothing is released. Because `const2` is 0, the base volume is zero in both actions, and each releases a share of the whole storage.

## Related files

- [`reservoir.con`](con.md): places each reservoir in the routing network and assigns its weather station.
- [`object.cnt`](object-cnt.md): number of reservoirs.
- [`file.cio`](file-cio.md): names the reservoir files.
- [`res_rel.dtl`](dtl.md): release decision tables.
- [`om_water.ini`](ini.md): initial water and concentrations referenced from `initial.res`.
- [`recall.rec`](recall.md): measured outflows for `meas` releases.
- [`wetland.wet` and `hydrology.wet`](wet.md): wetlands, which share `initial.res`, `sediment.res`, `nutrients.res`, `weir.res` and [`res_rel.dtl`](../input-reference/dtl.md).
- [Reservoir output](../output-reference/aquifer-reservoir-plant.md) and [reservoir and wetland theory](../model-theory/reservoirs-wetlands.md).

??? quote "Sources"

    - File names: `type input_res` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Call order: [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in), [`proc_res.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_res.f90)
    - Readers: [`res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read.f90), [`res_read_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_init.f90), [`res_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_hyd.f90), [`res_read_sed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_sed.f90), [`res_read_nut.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_nut.f90), [`res_read_weir.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_weir.f90), [`res_read_conds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_read_conds.f90), [`dtbl_res_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_res_read.f90)
    - Type definitions: [`reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_data_module.f90), [`reservoir_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_module.f90)
    - Setup: [`res_objects.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_objects.f90), [`res_allo.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_allo.f90), [`res_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_initial.f90), `res_convert_mass` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Daily routines: [`res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), [`res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90), [`res_rel_conds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_rel_conds.f90), [`res_sediment.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_sediment.f90), [`res_nutrient.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_nutrient.f90), [`theta.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/theta.f90), [`res_pest.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_pest.f90)
    - Decision table conditions and actions: [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | reservoir.res | `id`, `name`, `init`, `hyd`, `rel`, `sed`, `nut` | index into `res_dat_c`, then `res_dat_c%name`, `%init`, `%hyd`, `%release`, `%sed`, `%nut` |
    | initial.res | `name`, `org_min`, `pest`, `path`, `hmet`, `salt` | `res_init_dat_c%init`, `%org_min`, `%pest`, `%path`, `%hmet`, `%salt` |
    | hydrology.res | `yr_op`, `mon_op` | `res_hyddb%iyres`, `%mores` |
    | hydrology.res | `area_ps`, `vol_ps`, `area_es`, `vol_es` | `res_hyddb%psa`, `%pvol`, `%esa`, `%evol` |
    | hydrology.res | `k`, `evap_co` | `res_hyddb%k`, `%evrsv` |
    | hydrology.res | `shp_co1`, `shp_co2` | `res_hyddb%br1`, `%br2`, copied to `res_ob%lag_up`, `%lag_down` |
    | sediment.res | `sed_amt`, `d50`, `carbon`, `bd`, `sed_stl`, `stl_vel` | `res_sed%nsed`, `%d50`, `%carbon`, `%bd`, `%sed_stlr`, `%velsetlr` |
    | nutrients.res | `mid_start`, `mid_end` | `res_nut%ires1`, `%ires2` |
    | nutrients.res | `mid_n_stl`, `n_stl`, `mid_p_stl`, `p_stl` | `res_nut%nsetlr1`, `%nsetlr2`, `%psetlr1`, `%psetlr2` |
    | nutrients.res | `chla_co`, `secchi_co` | `res_nut%nsolr`, `%psolr` |
    | nutrients.res | `theta_n`, `theta_p`, `n_min_stl`, `p_min_stl` | `res_nut%theta_n`, `%theta_p`, `%conc_nmin`, `%conc_pmin` |
    | weir.res | `linear_c`, `exp_k`, `width`, `height` | `res_weir%c`, `%k`, `%w`, `%h` |

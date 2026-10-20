---
title: "hru-lte.hru"
description: Property file of the simplified HRU-lte objects. One row per HRU-lte with its curve number, soil, groundwater, plant, irrigation and USLE settings.
status: review
verified_against:
  - src/hru_lte_read.f90
  - src/hru_lte_module.f90
  - src/hru_lte_control.f90
  - src/hru_lte_output.f90
  - src/ascrv.f90
  - src/actions.f90
  - src/conditions.f90
  - src/command.f90
  - src/main.f90.in
  - src/soil_lte_db_read.f90
  - src/soil_data_module.f90
  - src/plant_data_module.f90
  - src/plant_parm_read.f90
  - src/dtbl_lum_read.f90
  - src/hyd_connect.f90
  - src/hyd_read_connect.f90
  - src/dr_ru.f90
  - src/cal_parm_select.f90
  - src/cal_parmchg_read.f90
  - src/proc_cal.f90
  - src/output_landscape_init.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`hru-lte.hru` describes the HRU-lte objects, a simplified kind of HRU. An HRU-lte has one soil layer described by a texture class, a single plant whose growing season is started and ended by decision tables, a curve number for surface runoff, separate shallow and deep groundwater stores and a fixed USLE factor for erosion. It computes no nutrients, pesticides or bacteria. HRU-lte objects can be used alone or together with ordinary HRUs, and they send water and sediment to channels, routing units and other objects like any other spatial object.

The file is named in the second position of the `hru` line of [file.cio](file-cio.md) (default `hru-lte.hru`). The objects themselves are defined in [`hru-lte.con`](../input-reference/con.md), the second file on the `connect` line, and their number is the `lhru` count in [object.cnt](object-cnt.md). The `hlt` column of [`hru-lte.con`](../input-reference/con.md) gives the `id` of the `hru-lte.hru` row each object uses. The area, latitude, elevation and weather station of the object come from [`hru-lte.con`](../input-reference/con.md); see the [connection file format](con.md).

`hru-lte.hru` is read only when the file exists and is not named `null`. When `lhru` is above zero, the file must be present: without it the HRU-lte objects have no properties and the run fails. A project with HRU-lte objects also needs [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol) (texture classes), [`plants.plt`](../input-reference/plt.md) (plant parameters) and [`lum.dtl`](../input-reference/dtl.md) (the growing-season decision tables).

## hru-lte.hru

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one HRU-lte with 35 values in the order below. The reader does not match columns by header name, so all 35 values must be present and in this order. Text values must not contain spaces.

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `id` | - | 1 and up | Row number. The `hlt` column of [`hru-lte.con`](../input-reference/con.md) refers to the row by this number. Ids must be unique; the rows may be in any order. |
| 2 | `name` | - | - | Name of the HRU-lte, up to 16 characters. Not used in calculations; the names in the output files come from [`hru-lte.con`](../input-reference/con.md). |
| 3 | `area` | km² (in the source) | - | Drainage area. Used only to estimate the time of concentration when `t_conc` is zero, which does not work in 62.0.1 (see [Time of concentration](#time-of-concentration)). The SWAT+ Editor writes the HRU area in hectares here. |
| 4 | `cn2` | - | 35 to 98 | SCS curve number for moisture condition II. See [Surface runoff](#surface-runoff). |
| 5 | `cn3_swf` | fraction | 0 to 0.95 | Soil water factor for the curve number: the soil water content at which the retention parameter reaches its condition III value, as a fraction of the way from field capacity (0) to saturation (1). A value of 1 makes the shape coefficients of the retention curve infinite; use a value below 1. The SWAT+ Editor writes 0. |
| 6 | `t_conc` | min | 10 to 1000 | Time of concentration. Sets the peak runoff rate for erosion, and the delivery ratio when the HRU-lte is an element of a routing unit with a calculated delivery ratio. Give a value above zero. The SWAT+ Editor writes 26. |
| 7 | `soil_dp` | mm | 300 to 3000 | Depth of the soil profile. Multiplies the available water capacity and porosity of the soil texture. |
| 8 | `perc_co` | fraction | 0 to 1 | Percolation threshold: percolation from the soil profile starts when soil water exceeds `perc_co` times the available water capacity. Called `perco_co` in earlier documentation, which gave a range of 0 to 6000. See [Percolation](#percolation). |
| 9 | `slp` | m/m | 0 to 0.6 | Average land surface slope. Used for lateral flow and the USLE slope factor. |
| 10 | `slp_len` | m | 10 to 150 | Slope length. Used for lateral flow and the USLE slope length factor. |
| 11 | `et_co` | - | 0.8 to 1.2 | Evapotranspiration coefficient. Multiplies potential evapotranspiration, and again actual evapotranspiration. Values below 0.4 make evapotranspiration outside the growing season negative. See [Evapotranspiration](#evapotranspiration). |
| 12 | `aqu_sp_yld` | - | 0.01 to 0.3 | Specific yield of the shallow aquifer. Read but not used. |
| 13 | `alpha_bf` | 1/day | 0 to 1 | Baseflow recession constant of the groundwater store. See [Groundwater](#groundwater). |
| 14 | `revap` | fraction | 0 to 0.2 | Revap coefficient: water removed from the shallow groundwater store each day as a fraction of the day's actual evapotranspiration. |
| 15 | `rchg_dp` | fraction | 0 to 1 | Fraction of the day's percolation that moves from the shallow store to the deep store. |
| 16 | `sw_init` | fraction | 0 to 1 | Initial soil water as a fraction of the available water capacity. |
| 17 | `aqu_init` | mm | - | Initial shallow aquifer storage. Read but not used: the store starts at zero. |
| 18 | `aqu_sh_flo` | mm | - | Initial groundwater flow. Read but not used: the flow starts at zero. |
| 19 | `aqu_dp_flo` | mm | - | Initial deep aquifer storage. Read but not used: the store starts at zero. |
| 20 | `snow_h2o` | mm H₂O | - | Initial snow water content. Read but not used: the snowpack starts at zero. |
| 21 | `lat` | degrees | -90 to 90 | Latitude. Read, and used only in a day length calculation whose result is not used, so it has no effect. |
| 22 | `soil_text` | - | - | Soil texture class, matched against the `texture` column of [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol). See [Name matching](#name-matching). |
| 23 | `trop_flag` | - | `non_trop`, `trop` | Tropical flag. Read but not used. |
| 24 | `grow_start` | - | - | Name of the [`lum.dtl`](../input-reference/dtl.md) decision table that starts the growing season, usually `pl_grow_sum` (or `pl_grow_win` for winter crops). |
| 25 | `grow_end` | - | - | Name of the [`lum.dtl`](../input-reference/dtl.md) decision table that ends the growing season and computes the yield, usually `pl_end_sum` (or `pl_end_win`). |
| 26 | `plnt_typ` | - | - | Plant name, matched against the `name` column of [`plants.plt`](../input-reference/plt.md). |
| 27 | `stress` | fraction | 0 to 1 | Plant stress factor for stresses the HRU-lte does not simulate (pests, root restriction, soil quality, nutrients). It multiplies daily biomass growth; 1 means no such stress. With 0 no biomass grows and the yield is zero. The SWAT+ Editor writes 0. |
| 28 | `pet_flag` | - | `harg`, `p_t` | Potential evapotranspiration method: `harg` for Hargreaves; any other value selects Priestley-Taylor. |
| 29 | `irr_flag` | - | - | Irrigation switch. See [Irrigation](#irrigation) for the values that switch irrigation on in 62.0.1. |
| 30 | `irr_src` | - | `outside_bsn`, `shal_aqu`, `deep_aqu` | Source of irrigation water: the HRU-lte's shallow or deep groundwater store, or an unlimited source outside the basin (any value other than `shal_aqu` and `deep_aqu`). |
| 31 | `t_drain` | hr | 0, or 24 to 72 | Time to drain the soil to field capacity through tile drains. 0 means no tile drains. |
| 32 | `usle_k` | 0.013 t m² h/(m³ t cm) | 0 to 0.65 | USLE soil erodibility factor K. |
| 33 | `usle_c` | - | 0.001 to 0.5 | USLE cover and management factor C. It is constant through the year. The SWAT+ Editor writes the `usle_c_min` of the plant. |
| 34 | `usle_p` | - | 0 to 1 | USLE support practice factor P. |
| 35 | `usle_ls` | - | - | USLE slope length and steepness factor LS. Read but not used: SWAT+ computes LS from `slp` and `slp_len`. |

## Name matching

The text columns are compared character by character with the names in the other files. The comparison is case-sensitive and trailing blanks are ignored.

- `soil_text` is looked up among the twelve texture classes of [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol) (see the [soils_lte.sol format](sol.md#soils_ltesol)). The matching class gives the available water capacity and porosity per mm of soil depth and the saturated hydraulic conductivity. If no class matches, the HRU-lte has no soil water capacity, and the run fails or produces invalid numbers when it divides by it. The SWAT+ Editor datasets contain the classes `sand`, `loamy_sand`, `sandy_loam`, `loam`, `silt_loam`, `silt`, `silty_clay_loam`, `clay_loam`, `sandy_clay_loam`, `sandy_clay`, `silty_clay` and `clay`, and the Editor picks one for each HRU-lte from the sand, silt and clay content of the first soil layer.
- `plnt_typ` is looked up in the `name` column of [`plants.plt`](../input-reference/plt.md). An unknown name writes `<name> not found (plants.plt)` to `diagnostics.out`, and the HRU-lte grows with the built-in default plant record, whose leaf area curve is not set up.
- `grow_start` and `grow_end` are looked up by table name in [`lum.dtl`](../input-reference/dtl.md). An unknown name writes `<name> entry in (hru-lte.hru) not found in (lum.dtl)` to `diagnostics.out`; the run then refers to a decision table that does not exist, so both names must be present in [`lum.dtl`](../input-reference/dtl.md).
- `pet_flag` is compared with `harg` only.
- `irr_flag` and `irr_src` are compared as described under [Irrigation](#irrigation).

## Daily water balance

Each HRU-lte runs once a day, in the order of the object list. The steps below follow that order. $SW$ is the soil water content (mm), $AWC$ and $POR$ are the available water capacity and the porosity of the profile (mm), and $K_{sat}$ is the saturated hydraulic conductivity of the texture class (mm/h):

$$AWC = awc \cdot \mathrm{soil\_dp}, \qquad POR = por \cdot \mathrm{soil\_dp}, \qquad SW_0 = \mathrm{sw\_init} \cdot AWC$$

where $awc$ and $por$ are the per-mm values of the texture class in [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol).

### Snow

When the mean air temperature $\bar{T}$ is below 0 °C, the whole day's precipitation is added to the snowpack and there is no runoff or infiltration that day. Otherwise snowmelt is

$$SNO_{mlt} = 4.57\,\bar{T}$$

limited to the snowpack, and rain and melt together form the water input $P$ for the day. The [`snow.sno`](../input-reference/sno.md) parameters are not used by HRU-lte objects.

### Surface runoff

Surface runoff uses the SCS curve number method with a retention parameter that varies with soil water (see [SCS curve number](../model-theory/hydrology.md#scs-curve-number)). At the start of the run the condition I and III curve numbers are derived from `cn2`:

$$CN_1 = CN_2 - \frac{20\,(100 - CN_2)}{100 - CN_2 + \exp\left(2.533 - 0.063\,(100 - CN_2)\right)}, \qquad CN_1 \ge 0.4\,CN_2$$

$$CN_3 = CN_2 \exp\left(0.00673\,(100 - CN_2)\right)$$

$$S_{max} = 254\left(\frac{100}{CN_1} - 1\right), \qquad S_3 = 254\left(\frac{100}{CN_3} - 1\right)$$

Each day the retention parameter is

$$S = S_{max}\left(1 - \frac{SW}{SW + \exp(w_1 - w_2\,SW)}\right), \qquad S \ge 3$$

The shape coefficients $w_1$ and $w_2$ are fixed at the start so that $S = S_3$ when $SW = AWC + \mathrm{cn3\_swf}\,(POR - AWC)$, and $S = 2.54$ when $SW = POR$. Runoff is

$$Q_{surf} = \frac{(P - 0.2\,S)^2}{P + 0.8\,S} \quad \text{for } P > 0.2\,S$$

and zero otherwise. The rest of $P$ is added to the soil water. SWAT+ also stores `cn2` limited to 35 to 98, but the runoff curve is built from the value as given in the file, so values outside that range are used as they are.

### Evapotranspiration

Potential evapotranspiration is computed with the method chosen in `pet_flag` and multiplied by `et_co`. With Hargreaves,

$$PET = \mathrm{et\_co} \cdot 0.0032\,\frac{H_0}{2.5 - 0.0022\,\bar{T}}\,(\bar{T} + 17.8)\,(T_{max} - T_{min})^{0.6}$$

where $H_0$ is the day's maximum possible solar radiation (MJ/m²). With Priestley-Taylor,

$$PET = \mathrm{et\_co} \cdot 1.28\,\frac{\Delta}{\Delta + 0.68}\cdot\frac{23.9\,H\,(1 - 0.23)}{58.3}, \qquad \Delta = \frac{5304}{T_K^2}\exp\left(21.255 - \frac{5304}{T_K}\right)$$

where $H$ is the day's solar radiation (MJ/m²) and $T_K$ the mean air temperature in kelvin. Both are simpler forms than those used for ordinary HRUs (see [Potential evapotranspiration](../model-theory/climate-weather.md#potential-evapotranspiration)).

Actual evapotranspiration is proportional to the soil water content:

$$E_a = b \cdot PET\,\frac{SW}{AWC}, \qquad b = \begin{cases}\mathrm{et\_co} & \text{during the growing season}\\ \mathrm{et\_co} - 0.4 & \text{outside it}\end{cases}$$

It is taken from the soil after lateral flow, tile flow and percolation, and is limited to the soil water left at that point. Because `et_co` enters both $PET$ and $b$, a change in `et_co` changes actual evapotranspiration roughly with its square during the growing season.

### Lateral flow

When soil water is above the available water capacity,

$$Q_{lat} = 0.024\,\frac{SW - AWC}{POR - AWC}\,K_{sat}\,\frac{\mathrm{slp}}{\mathrm{slp\_len}}$$

limited to the soil water.

### Tile flow

When `t_drain` is above zero and soil water is above the available water capacity,

$$Q_{tile} = (SW - AWC)\left(1 - \exp\left(\frac{-24}{\mathrm{t\_drain}}\right)\right), \qquad Q_{tile} \le 10\ \text{mm}$$

### Percolation

Water above `perc_co` times the available water capacity drains from the bottom of the profile:

$$w_{perc} = (SW - \mathrm{perc\_co}\cdot AWC)\left(1 - \exp\left(\frac{-24}{TT}\right)\right), \qquad TT = \max\left(2,\ \frac{POR - AWC}{K_{sat}}\right)$$

where $TT$ is the travel time in hours. With `perc_co` at 1 only water above field capacity percolates; with `perc_co` at 0 (the value the SWAT+ Editor writes) the profile can drain well below field capacity.

### Groundwater

The shallow and deep groundwater stores of an HRU-lte are separate from the aquifer objects. Percolation is added to the shallow store. Groundwater flow follows a recession with $\alpha$ = `alpha_bf`:

$$Q_{gw,d} = Q_{gw,d-1}\,e^{-\alpha} + w_{perc}\left(1 - e^{-\alpha}\right)$$

limited to the shallow storage. Then revap ($\mathrm{revap} \cdot E_a$) and deep percolation ($\mathrm{rchg\_dp} \cdot w_{perc}$) are taken from what is left in the shallow store, each limited to the storage. Deep percolation is added to the deep store, which only irrigation from `deep_aqu` draws on. Revap leaves the HRU-lte; it is not added to the soil or to the reported evapotranspiration. Both stores and the groundwater flow start at zero.

### Water yield

The water the HRU-lte sends downstream each day is

$$WYLD = Q_{surf} + Q_{lat} + Q_{tile} + Q_{gw}$$

In the `hru-lte_wb` output files, `latq` is the sum of lateral flow and groundwater flow.

## Plant growth

The plant named in `plnt_typ` grows between the two decision tables. On each day outside the growing season the `grow_start` table is checked; when its `grow_init` action runs, growth starts with zero biomass and leaf area. During the season the `grow_end` table is checked; its `grow_end` action computes the yield and ends the season. The `pl_grow_sum` and `pl_end_sum` tables of the SWAT+ reference data start growth when the fraction of the year's base-zero heat units at the weather station is between 0.15 and 0.2, and end it when the fraction is above 0.5 or on day 330. See [decision table actions](dtl.md#land-use-and-management-actions).

### Heat units to maturity

At the start of the run SWAT+ estimates the heat units to maturity, $PHU$, from the long-term monthly mean temperatures in the weather generator of the HRU-lte's station. Daily values of $\bar{T} - T_{base}$ above zero are summed over the days between a start and an end day, and

$$PHU = \max(500,\ 0.9\,\textstyle\sum(\bar{T} - T_{base}))$$

limited to 2000 for annual plant types (`warm_annual`, `cold_annual` and their tuber forms). In 62.0.1 the start and end days of the sum are the positions of the `grow_start` and `grow_end` tables in [`lum.dtl`](../input-reference/dtl.md) (first table 1, second table 2, and so on). The days of the year of the growing season are not used. For two tables next to each other in [`lum.dtl`](../input-reference/dtl.md) the sum covers no days and $PHU$ takes its minimum of 500.

### Biomass and leaf area

During the growing season the fraction of heat units $g$ increases each day by $(\bar{T} - T_{base})/PHU$. Biomass grows with intercepted radiation:

$$\Delta B = \gamma \cdot \mathrm{stress} \cdot bm_e \cdot 0.5\,H\left(1 - e^{-0.65\,(LAI + 0.05)}\right), \qquad \gamma = \min(ws,\ ts,\ as)$$

where $bm_e$ is `bm_e` of [`plants.plt`](../input-reference/plt.md), $ws = E_a/PET$ is the water stress factor (before the adjustment $b$), $ts$ the temperature stress factor and $as$ the aeration stress factor:

$$ts = \exp\left(-0.1054\left(\frac{T_{opt} - \bar{T}}{2T_{opt} - T_{base} - \bar{T}}\right)^2\right) \text{ for } \bar{T} > T_{base}, \qquad ts = 0 \text{ otherwise}$$

Aeration stress starts when $SW$ exceeds $AWC$ by more than 85% of the drainable range $POR - AWC$. Leaf area follows the leaf area curve of the plant (`frac_hu1`, `lai_max1`, `frac_hu2`, `lai_max2` and `lai_pot` in [`plants.plt`](../input-reference/plt.md)), with the daily increase scaled by $\sqrt{\gamma}$. See [plant growth](../model-theory/plant-growth-lum.md#light-interception-and-biomass) for the background of these relations.

### Yield

When the season ends, the yield is

$$Y = 0.8\,B\,HI', \qquad HI' = (HI - HI_{min})\frac{wur}{wur + \exp(6.13 - 0.0883\,wur)} + HI_{min}$$

where $HI$ is `harv_idx`, $HI_{min}$ is `harv_idx_ws` of [`plants.plt`](../input-reference/plt.md), and $wur$ is 100 times the ratio of actual to potential evapotranspiration summed over the season (100 when the potential sum is below 10 mm). Biomass and leaf area are then set to zero.

Plant growth has no effect on the water balance or on erosion: evapotranspiration does not depend on leaf area, and `usle_c` is constant. The plant affects the water balance only through the growing season itself (the factor $b$) and through irrigation.

## Irrigation

During the growing season, on days when the water stress factor $ws$ is below 0.8, the soil is filled to the available water capacity with at most 76.2 mm. With `irr_src` set to `shal_aqu` or `deep_aqu` the water is taken from the HRU-lte's shallow or deep store and limited to what it contains; any other value takes it from an unlimited source outside the basin.

In 62.0.1 irrigation is switched on when `irr_flag` sorts alphabetically after `no_irr`. The value `irr`, listed as the "irrigation" value in earlier documentation, sorts before `no_irr` and so leaves irrigation off. Values such as `yes` or `sprinkler` switch it on.

## Erosion

Sediment yield is computed with MUSLE (see [MUSLE](../model-theory/erosion-sediment.md#musle)). The slope length and steepness factor is computed at the start of the run from `slp` and `slp_len`; the `usle_ls` column is not used:

$$LS = \left(\frac{\mathrm{slp\_len}}{22.128}\right)^m\left(65.41\,\sin^2\theta + 4.56\,\sin\theta + 0.065\right), \qquad m = 0.6\left(1 - e^{-35.835\,\mathrm{slp}}\right)$$

with $\theta = \arctan(\mathrm{slp})$. Sediment from surface runoff is

$$sed = 11.8\,(Q_{surf}\; q_{peak} \cdot 1000\,A)^{0.56}\; K\,C\,P\,LS$$

with $K$, $C$ and $P$ from `usle_k`, `usle_c` and `usle_p`, and $A$ the `area` of [`hru-lte.con`](../input-reference/con.md). A concentration of 500 mg/L in lateral and groundwater flow is added to this. There is no snow cover or residue effect.

### Time of concentration

The peak runoff rate uses the time of concentration $t_c$ in seconds (`t_conc` times 60):

$$q_{peak} = \frac{2\,Q_{surf} \cdot 1000\,A}{1.5\,t_c} + \frac{(Q_{lat} + Q_{gw}) \cdot 1000\,A}{86400}$$

When `t_conc` is zero, SWAT+ tries to estimate it with the Kirpich formula, using `area` as the channel length. The slope in that formula is always zero in 62.0.1, so the estimate is infinite: depending on how the model was compiled the run either stops with a floating-point error or continues with no surface runoff in the peak rate. Give `t_conc` a value above zero.

## Area units

The HRU-lte calculations convert a depth $D$ in mm to a volume with $1000\,D\,A$ and report sediment yield per $100\,A$, which are the conversions for an area $A$ in km². $A$ is the `area` column of [`hru-lte.con`](../input-reference/con.md), which is in hectares for every other object type and which the SWAT+ Editor writes in hectares. With hectares, the flow volumes and sediment loads an HRU-lte sends downstream are 100 times the depth over its area, and the peak rate and sediment yield in the output are affected in the same way. Only the total hydrograph is filled: an HRU-lte connection in [`hru-lte.con`](../input-reference/con.md) that asks for the surface, lateral, tile or recharge hydrograph sends nothing.

## Calibration

Parameters with the suffix `_lte` in [`calibration.cal`](../calibration/parameter-change-files.md) change `hru-lte.hru` values (see [simplified HRU parameters](../calibration/parameter-change-files.md#simplified-hru-parameters-hlt)). The changes are applied after the file has been read and the HRU-lte objects have been set up, so in 62.0.1 they have an effect only for values the daily calculation reads directly from the file:

- effective: `awc_lte` (available water capacity of the object), `slope_lte` and `slopelen_lte` (lateral flow only), `revapc_lte`, `percc_lte`, `abf_lte` and `tc_lte`
- no effect: `cn2_lte`, `etco_lte`, `soildep_lte`, `sw_lte`, `sy_lte`, `gw_lte`, `gwflow_lte`, `gwdeep_lte`, `snow_lte`, `uslek_lte`, `uslec_lte`, `uslep_lte` and `uslels_lte`

`abf_lte` changes the daily recession factor $e^{-\alpha}$ in place of `alpha_bf`, and `tc_lte` changes the time of concentration in seconds. Except for `awc_lte`, a change to object number $n$ is applied to the `hru-lte.hru` row with `id` $n$; the two agree when row numbers follow the objects, as the SWAT+ Editor writes them.

## Example

No `hru-lte.hru` is included in the SWAT+ reference data. The file below is illustrative, with the column headers the SWAT+ Editor writes.

```
hru-lte.hru: illustrative example
id  name    area   cn2  cn3_swf  t_conc  soil_dp  perc_co   slp  slp_len  et_co  aqu_sp_yld  alpha_bf  revap  rchg_dp  sw_init  aqu_init  aqu_sh_flo  aqu_dp_flo  snow_h2o    lat  soil_text  trop_flag  grow_start   grow_end    plnt_typ  stress  pet_flag  irr_flag  irr_src      t_drain  usle_k  usle_c  usle_p  usle_ls
1   hlt001  52.3  77.0     0.00    26.0   1500.0     1.00  0.04     60.0   1.00        0.05      0.05   0.00     0.01     0.50      3.00        0.00      300.00      0.00  41.50  loam       non_trop   pl_grow_sum  pl_end_sum  corn        1.00  harg      no_irr    outside_bsn     0.00    0.28    0.20    1.00     0.53
```

One HRU-lte with a 1.5 m loam profile that starts half full. Percolation starts above field capacity (`perc_co` 1). Corn grows between the `pl_grow_sum` and `pl_end_sum` tables with no extra stress (`stress` 1), there is no irrigation and no tile drainage, and potential evapotranspiration follows Hargreaves. The values of `area`, `aqu_sp_yld`, `aqu_init`, `aqu_sh_flo`, `aqu_dp_flo`, `snow_h2o`, `lat`, `trop_flag` and `usle_ls` have no effect in 62.0.1.

## Related files

- [Connection files](con.md): [`hru-lte.con`](../input-reference/con.md) defines the HRU-lte objects, their area, weather station and outflow connections; its `hlt` column selects a row of this file by `id`.
- [Object counts](object-cnt.md): the `lhru` column of [`object.cnt`](../input-reference/object-cnt.md) gives the number of HRU-lte objects.
- [Master file](file-cio.md): [`file.cio`](../input-reference/file-cio.md) names this file on its `hru` line, and [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol) on its `soils` line.
- [Soil texture classes](sol.md#soils_ltesol): [`soils_lte.sol`](../input-reference/sol.md#soils_ltesol) supplies available water capacity, porosity and conductivity for `soil_text`.
- [Plant parameters](plt.md): [`plants.plt`](../input-reference/plt.md) supplies the plant parameters for `plnt_typ`.
- [Decision tables](dtl.md): the `grow_start` and `grow_end` tables in [`lum.dtl`](../input-reference/dtl.md).
- [Weather files](cli.md): the weather station named in [`hru-lte.con`](../input-reference/con.md) supplies daily weather and, through its weather generator, the temperatures for the heat units to maturity.
- [Water balance output](../output-reference/water-balance.md): `hru-lte_wb` files; plant growth and stress go to the `hru-lte_pw` files.

??? quote "Sources"

    - Reader: [`hru_lte_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_read.f90), called from [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) after `dtbl_lum_read`
    - Type definitions: `type swatdeg_hru_data` and `type swatdeg_hru_dynamic` in [`hru_lte_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_module.f90)
    - Daily water balance, plant growth, irrigation and erosion: [`hru_lte_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_control.f90), called from [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)
    - Retention curve shape: [`ascrv.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ascrv.f90)
    - Growing season actions `grow_init` and `grow_end`: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90); conditions with `obj` `hlt`: [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90)
    - Texture classes: [`soil_lte_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_lte_db_read.f90), `type soil_lte_database` in [`soil_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_data_module.f90)
    - Plant parameters: [`plant_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_data_module.f90), [`plant_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_parm_read.f90)
    - Connection and object numbering: [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90), [`hyd_read_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_read_connect.f90)
    - Delivery ratio from `t_conc`: [`dr_ru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dr_ru.f90)
    - Calibration: [`cal_parm_select.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parm_select.f90), [`cal_parmchg_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cal_parmchg_read.f90), [`proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90)
    - Output: [`hru_lte_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_lte_output.f90), [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90)
    - File name slot: `in_hru%hru_ez` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `id` | row index of `hlt_db` |
    | `name` | `hlt_db%name` |
    | `area` | `hlt_db%dakm2` |
    | `cn2` | `hlt_db%cn2` |
    | `cn3_swf` | `hlt_db%cn3_swf` |
    | `t_conc` | `hlt_db%tc` |
    | `soil_dp` | `hlt_db%soildep` |
    | `perc_co` | `hlt_db%perco` |
    | `slp` | `hlt_db%slope` |
    | `slp_len` | `hlt_db%slopelen` |
    | `et_co` | `hlt_db%etco` |
    | `aqu_sp_yld` | `hlt_db%sy` |
    | `alpha_bf` | `hlt_db%abf` |
    | `revap` | `hlt_db%revapc` |
    | `rchg_dp` | `hlt_db%percc` |
    | `sw_init` | `hlt_db%sw` |
    | `aqu_init` | `hlt_db%gw` |
    | `aqu_sh_flo` | `hlt_db%gwflow` |
    | `aqu_dp_flo` | `hlt_db%gwdeep` |
    | `snow_h2o` | `hlt_db%snow` |
    | `lat` | `hlt_db%xlat` |
    | `soil_text` | `hlt_db%text` |
    | `trop_flag` | `hlt_db%tropical` |
    | `grow_start` | `hlt_db%igrow1` |
    | `grow_end` | `hlt_db%igrow2` |
    | `plnt_typ` | `hlt_db%plant` |
    | `stress` | `hlt_db%stress` |
    | `pet_flag` | `hlt_db%ipet` |
    | `irr_flag` | `hlt_db%irr` |
    | `irr_src` | `hlt_db%irrsrc` |
    | `t_drain` | `hlt_db%tdrain` |
    | `usle_k` | `hlt_db%uslek` |
    | `usle_c` | `hlt_db%uslec` |
    | `usle_p` | `hlt_db%uslep` |
    | `usle_ls` | `hlt_db%uslels` |

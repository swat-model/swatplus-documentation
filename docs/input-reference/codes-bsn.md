---
title: codes.bsn
description: Basin-wide method codes. Selects the PET method, channel routing method, carbon model, runoff method and other options for the whole watershed.
status: review
verified_against:
  - src/basin_read_cc.f90
  - src/basin_module.f90
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/proc_bsn.f90
  - src/main.f90.in
  - src/et_pot.f90
  - src/climate_control.f90
  - src/plant_parm_read.f90
  - src/soil_plant_init.f90
  - src/surface.f90
  - src/sq_crackvol.f90
  - src/sq_crackflow.f90
  - src/swr_percmain.f90
  - src/hru_control.f90
  - src/res_control.f90
  - src/command.f90
  - src/swift_output.f90
  - src/ero_pkq.f90
  - src/ero_cfactor.f90
  - src/ero_ovrsed.f90
  - src/ch_rtmusk.f90
  - src/sd_hydsed_init.f90
  - src/sd_channel_control3.f90
  - src/pl_biomass_gro.f90
  - src/cli_lapse.f90
  - src/unit_hyd.f90
  - src/unit_hyd_ru_hru.f90
  - src/hru_hyds.f90
  - src/sq_volq.f90
  - src/soil_nutcarb_init.f90
  - src/basin_read_objs.f90
  - src/aqu_read.f90
  - src/cbn_zhang2.f90
  - src/carbon_bsn_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

`codes.bsn` contains the method codes that apply to the whole watershed: the potential evapotranspiration (PET) method, the channel routing method, the soil carbon model, the surface runoff method, the tile drainage equations, plant stress switches and a few output options. It is named in the first position of the `basin` line of [`file.cio`](file-cio.md) (default `codes.bsn`). SWAT+ reads it at the start of the run, before the inputs that depend on these codes.

If the file named in [`file.cio`](../input-reference/file-cio.md) does not exist, every code keeps the built-in value listed below.

## Format

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Line 3 contains 26 values in the order below. The reader matches values by position only, so all 26 must be present and in this order. The table gives the column headers the SWAT+ Editor writes.

| # | Column | Type | Built-in value | Description |
|---|--------|------|----------------|-------------|
| 1 | `pet_file` | text | [`pet.cli`](../input-reference/cli.md#observed-data-lists) | Not used. Measured PET is set up through [`file.cio`](../input-reference/file-cio.md) and [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) (see [PET method](#pet-method)). |
| 2 | `wq_file` | text | blank | Not used. |
| 3 | `pet` | integer | 0 | PET method: `0` Priestley-Taylor, `1` Penman-Monteith, `2` Hargreaves, `3` PET of the weather station. See [PET method](#pet-method). |
| 4 | `event` | integer | 0 | Extra column switch for two other inputs. `0`: normal format. Any other value: [`plants.plt`](../input-reference/plt.md) is read with an extra plant class column and [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) with an extra constituent column. See [Extra input columns](#extra-input-columns). |
| 5 | `crack` | integer | 0 | Crack flow: `0` off, `1` on. See [Crack flow](#crack-flow). |
| 6 | `swift_out` | integer | 0 | SWIFT input files: `0` not written, `1` written to a `SWIFT` folder at the end of the run. Older Editor versions label this column `rtu_wq`. |
| 7 | `sed_det` | integer | 0 | Peak runoff rate method for erosion: `0` NRCS method with the peak rate factor, `1` half-hour rainfall intensity method. See [Peak runoff rate](#peak-runoff-rate). |
| 8 | `rte_cha` | integer | 0 | Channel water routing: `0` variable storage, `1` Muskingum. See [Channel routing](#channel-routing). |
| 9 | `deg_cha` | integer | 0 | Not used. |
| 10 | `wq_cha` | integer | 0 | Not used. |
| 11 | `nostress` | integer | 0 | Plant stress: `0` all stresses applied, `1` all stresses turned off (water, temperature, nitrogen, phosphorus, aeration and salt), `2` nitrogen and phosphorus stress turned off. |
| 12 | `cn` | integer | 0 | Not used. |
| 13 | `c_fact` | integer | 0 | Read, then overridden: the model always uses the residue and biomass cover method for the USLE C factor. See [USLE C factor](#usle-c-factor). |
| 14 | `carbon` | integer | 0 | Soil carbon model: `0` static carbon (original SWAT humus and residue routines), `1` reserved for C-FARM (not implemented), `2` dynamic carbon model with CENTURY pools. See [Carbon model](#carbon-model). |
| 15 | `lapse` | integer | 0 | Elevation adjustment of HRU precipitation and temperature: `0` off, `1` on. See [Lapse rates](#lapse-rates). |
| 16 | `uhyd` | integer | 1 | Unit hydrograph shape for sub-daily runs: `0` triangular, `1` gamma function. See [Unit hydrograph](#unit-hydrograph). |
| 17 | `sed_cha` | integer | 0 | Not used. |
| 18 | `tiledrain` | integer | 0 | Tile flow equation: `0` drawdown-days equation, `1` DRAINMOD equations. |
| 19 | `wtable` | integer | 0 | Shallow water table depth: `0` original routine (water above field capacity fills the profile from the bottom), `1` DRAINMOD water table routine. |
| 20 | `soil_p` | integer | 0 | Soil phosphorus model: `0` original SWAT model with a fixed P availability index, `1` dynamic P availability of Vadas and White (2010). |
| 21 | `gampt` | integer | 0 | Infiltration and surface runoff: `0` curve number, `1` Green-Ampt. See [Runoff method](#runoff-method). |
| 22 | `atmo_dep` | single character | `a` | Not used. |
| 23 | `stor_max` | integer | 0 | Not used. |
| 24 | `i_fpwet` | integer | 0 | In-stream nutrient method: `0` QUAL2E, `1` QUAL2E followed by simplified first-order transformations. Called `qual2e` in earlier documentation. See [In-stream nutrients](#in-stream-nutrients). |
| 25 | `gw_flow` | integer | 0 | Gridded groundwater module: `0` off, `1` on. Called `gwflow` in earlier documentation, where it was described as flood routing. See [gwflow module](#gwflow-module). |
| 26 | `idc_till` | integer | 3 | Tillage effect on decomposition in the dynamic carbon model (`carbon = 2`): `1` DSSAT, `2` EPIC (placeholder), `3` Kemanian, `4` DNDC (placeholder). See [Tillage effect on decomposition](#tillage-effect-on-decomposition). |

The 26 values are read in one free-format read. A line with fewer values continues onto the next line of the file, and the codes that are not reached keep their built-in values. A value that cannot be read (text in an integer column, for example) ends the read without a message, so the codes after it also keep their built-in values.

## PET method

`pet` selects how daily potential evapotranspiration is calculated for each HRU:

| `pet` | Method |
|-------|--------|
| 0 | Priestley-Taylor, with $\alpha = 1.28$. |
| 1 | Penman-Monteith, with a 40 cm alfalfa reference crop and a canopy resistance that depends on the year's CO2 concentration. This method also gives the maximum transpiration of the growing plants. |
| 2 | Hargreaves. |
| 3 | The daily PET value of the HRU's weather station. |

In every case the result is multiplied by the HRU's `pet_co` from [`hydrology.hyd`](hyd.md).

With `pet = 3`, the HRU uses the daily PET stored for its weather station. A station gets measured PET from the PET gage named in [`weather-sta.cli`](../input-reference/cli.md#weather-stacli), and the gage files are listed in [`pet.cli`](../input-reference/cli.md#observed-data-lists), which is named on the `climate` line of [`file.cio`](../input-reference/file-cio.md) (see [climate files](cli.md)). In 62.0.1, however, the station PET is recalculated with the Hargreaves equation later in the same daily climate step, for every station, before the HRUs use it (the recalculated value feeds the 30-day precipitation to PET ratio). Measured PET is therefore replaced by Hargreaves PET with a minimum of 0.01 mm, and `pet = 3` gives Hargreaves PET times `pet_co`. Channel and pond evaporation and aquifer revap use the same station value under every `pet` code.

With `pet = 3` the model also opens a file called [`pet.cli`](../input-reference/cli.md#observed-data-lists) in the run folder and reads its first three lines. The file is not used after that.

## Extra input columns

`event` is not an event switch. When it is not 0:

- each row of [`plants.plt`](plt.md) is read with one more value at the end, the plant class (for example row crop, tree, grass). Calibration conditions can select plants by this class.
- each row of [`soil_plant.ini`](../input-reference/ini.md#soil_plantini) is read with one more name at the end, a constituent initial-condition record (see [initial conditions](ini.md)).

Files written by the SWAT+ Editor do not have these columns, so `event` should be 0 for them.

## Crack flow

With `crack = 1`, SWAT+ calculates a daily crack volume for each HRU from the soil's crack volume potential (`crk` in [`soils.sol`](sol.md)) and the layer water contents. Surface runoff is reduced by the crack volume (in sub-daily runs, the runoff of each time step in turn until the volume is filled), and water entering the soil flows through the cracks before the layer-by-layer percolation.

## Peak runoff rate

The peak runoff rate is used in the MUSLE sediment yield of each HRU.

With `sed_det = 0`, the peak rate comes from the NRCS method:

$$q_{peak} = \frac{\mathrm{prf}}{6578.6}\cdot\frac{A\,Q_{surf}}{t_{conc}}\cdot\frac{1}{35.3}$$

where $q_{peak}$ is in m³/s, $A$ is the HRU area (ha), $Q_{surf}$ is the surface runoff (mm), $t_{conc}$ is the time of concentration (h) and `prf` is the peak rate factor in [`parameters.bsn`](parameters-bsn.md). The factor 6578.6 converts ha·mm to mi²·in, and 35.3 converts ft³/s to m³/s. Wetlands always use this equation, whatever the value of `sed_det`.

With `sed_det = 1`, the half-hour rainfall intensity method is used:

$$\alpha_{tc} = 1 - \exp\!\left[2\,t_{conc}\,\ln(1 - \alpha_{0.5})\right], \qquad q_{peak} = \frac{\alpha_{tc}\,Q_{surf}\,A_{km}}{3.6\,t_{conc}}$$

where $\alpha_{0.5}$ is the day's fraction of rain falling in the maximum half hour (from the weather generator, scaled by `adj_pkrt` in [`parameters.bsn`](../input-reference/parameters-bsn.md)) and $A_{km}$ is the HRU area in km².

## Channel routing

`rte_cha` selects how water is routed through channels.

With `rte_cha = 0` (variable storage), the fraction of channel storage that leaves the reach in each routing step is

$$C_{sto} = \min\!\left(1,\; \mathrm{scoef}\cdot\frac{2\,\Delta t}{2\,TT + \Delta t}\right)$$

where $\Delta t$ is the routing step (h), $TT$ is the travel time at the outflow of the previous step (h) and `scoef` is the channel storage coefficient in [`parameters.bsn`](parameters-bsn.md). Daily runs use one routing step per day.

With `rte_cha = 1` (Muskingum), the outflow of a step is $O_2 = C_1 I_2 + C_2 I_1 + C_3 O_1$. The storage time constant is a weighted mean of the values at bankfull and at 0.1 bankfull depth, with the weights `msk_co1` and `msk_co2` (scaled to sum to 1), and `msk_x` is the weighting factor; all three are in [`parameters.bsn`](parameters-bsn.md). The day is divided into enough substeps to keep the scheme stable.

## USLE C factor

`c_fact` is replaced by 1 each time the C factor is calculated, so the model always uses the method based on residue and growing biomass cover (from APEX). The residue part of that method uses `rsd_cover` in [`parameters.bsn`](parameters-bsn.md). The older method based on the plants' minimum C factor is not used in 62.0.1.

## Carbon model

`carbon` selects the soil organic matter model:

- `0`: static carbon. Soil organic matter is kept in active and stable humus pools and in residue, with the original SWAT residue decomposition, mineralization and annual biological mixing.
- `2`: dynamic carbon model with CENTURY litter, microbial and humus pools. The model requires [`carbon.bsn`](carbon-bsn.md) and [`carbon_lyr.bsn`](carbon-lyr-bsn.md) and stops with an error if either is missing. Tillage, fertilizer and manure applications, grazing and the daily soil processes use the carbon pool versions of their routines, and the carbon outputs selected in [`print.prt`](print-prt.md) become available (see [carbon outputs](../output-reference/carbon.md)).
- `1`: reserved for C-FARM, which is not implemented. No organic matter routine runs under this code: the soil humus pools are not initialised, and residue decomposition and N and P mineralization are skipped for the whole run.

The numbering changed in revision 62. The dynamic carbon model used to be selected with `carbon = 1`. A `codes.bsn` from an older dataset that still has `carbon = 1` now runs with no organic matter cycling, so it must be changed to `2` (dynamic model) or `0` (static model). See [soil carbon](../model-theory/carbon.md) for the model description.

## Lapse rates

With `lapse = 1`, each HRU's daily precipitation and temperatures are adjusted for the difference between the HRU's elevation and the elevation of the gage or weather generator station that supplies the data:

$$P' = \max\!\left(0,\; P + \mathrm{plaps}\cdot\frac{z_{HRU} - z_{gage}}{1000}\right), \qquad T' = T + \mathrm{tlaps}\cdot\frac{z_{gage} - z_{HRU}}{1000}$$

with elevations in m, `plaps` in mm/km and `tlaps` in °C/km from [`parameters.bsn`](parameters-bsn.md). The precipitation adjustment is a fixed depth added on every day, wet or dry, so with a positive `plaps` an HRU above its gage also receives rain on dry days. The temperature adjustment applies to the maximum, minimum and mean temperature. Reservoirs and channels use the station weather without adjustment.

## Unit hydrograph

In sub-daily runs (more than one time step per day in [`time.sim`](time-sim.md)) with the curve number method (`gampt = 0`), daily surface runoff from HRUs and routing units is spread over the time steps with a unit hydrograph. The base time and time to peak are

$$t_b = \min\!\left(48,\; 0.5 + 0.6\,t_{conc} + \mathrm{adj\_uhyd}\right), \qquad t_p = 0.375\,t_b$$

in hours, where `adj_uhyd` is in [`parameters.bsn`](parameters-bsn.md). With `uhyd = 0` the hydrograph is triangular, rising to the peak at $t_p$ and falling to zero at $t_b$. With `uhyd = 1` it follows the gamma function

$$q(t) = \left(\frac{t}{t_p}\right)^{\alpha} \exp\!\left[\alpha\left(1 - \frac{t}{t_p}\right)\right]$$

with $\alpha$ = `uhyd_alpha` from [`parameters.bsn`](../input-reference/parameters-bsn.md). The ordinates are scaled to a total of 1 and cover at most two days. `uhyd` has no effect in daily runs or with Green-Ampt.

## Runoff method

With `gampt = 0`, daily surface runoff is calculated with the curve number method. With `gampt = 1`, infiltration and runoff are calculated with the Green-Ampt method from the rainfall of each time step, which is intended for sub-daily runs. In sub-daily runs with Green-Ampt the runoff hydrograph of a routing unit is shifted in time without attenuation, and `uhyd` is not used. The shift is a fixed 2 hours for every routing unit; the computed time of concentration is not used for it. For urban HRUs, Green-Ampt also uses `urb_init_abst` in [`parameters.bsn`](parameters-bsn.md).

Any `gampt` value above 0 also switches on the sub-daily erosion calculation from raindrop splash and overland flow, which uses `splash`, `rill`, `surq_exp` and `cov_mgt` in [`parameters.bsn`](../input-reference/parameters-bsn.md).

## In-stream nutrients

Channel water quality is always calculated with the QUAL2E routine. With `i_fpwet = 1`, simplified first-order transformations of organic N and sediment-bound P follow, using each channel's N and P transformation rates and the travel time, and their results replace the QUAL2E results for those constituents.

## gwflow module

With `gw_flow = 1`, SWAT+ looks for [`chancell.gw`](../input-reference/gwflow.md#chancellgw) in the run folder. If it is present and has data, the gridded groundwater module replaces the aquifer objects: the aquifer connection file is set to `null` and the groundwater cells connected to channels are added as objects. If [`chancell.gw`](../input-reference/gwflow.md#chancellgw) is missing or empty, `gw_flow` is set back to 0 and the aquifer objects are used. See [gwflow](gwflow.md) and [`object.cnt`](object-cnt.md).

## Tillage effect on decomposition

`idc_till` is used only with `carbon = 2`. It sets the tillage factor that multiplies the decomposition rates of the carbon pools in each soil layer:

| `idc_till` | Tillage factor |
|------------|----------------|
| 1 | DSSAT method: 1.6 in the tilled layers for `till_eff_days` days after tillage (from [`carbon.bsn`](carbon-bsn.md)), with a linear transition in a partly tilled layer; 1.0 otherwise. |
| 2 | Placeholder for the EPIC method. No tillage effect (factor 1.0). |
| 3 | Kemanian method: 1 plus the layer's tillage factor from tillage and biological mixing, calculated with the mixing curves in [`carbon.bsn`](../input-reference/carbon-bsn.md). |
| 4 | Placeholder for the DNDC method. No tillage effect (factor 1.0). |

## Example

`refdata/Ames_sub1/codes.bsn` in the SWAT+ repository:

```
codes.bsn: 
        pet_file           wq_file       pet     event     crack  swift_out   sed_det   rte_cha   deg_cha    wq_cha  nostress        cn    c_fact    carbon     lapse      uhyd   sed_cha  tiledrain    wtable    soil_p     gampt      atmo_dep  stor_max   i_fpwet   gw_flow  idc_till  
            null              null         2         0         0         0         0         0         0         0         0          2         0         2         0         1         0          0         0         0         0             0         0         0      0         3
```

This file selects Hargreaves PET (`pet = 2`), the NRCS peak rate method, variable storage channel routing, curve number runoff, the dynamic carbon model (`carbon = 2`) and the Kemanian tillage method (`idc_till = 3`). `cn = 2` and `atmo_dep = 0` are in unused columns and have no effect. `uhyd = 1` would select a gamma unit hydrograph if the run were sub-daily.

## Related files

- [`file.cio`](file-cio.md): names `codes.bsn` on its `basin` line.
- [`parameters.bsn`](parameters-bsn.md): coefficients used by the methods selected here.
- [`carbon.bsn`](carbon-bsn.md) and [`carbon_lyr.bsn`](carbon-lyr-bsn.md): required when `carbon = 2`.
- [`hydrology.hyd`](hyd.md): `pet_co` multiplies the PET of every method.
- [Climate files](cli.md): [`weather-sta.cli`](../input-reference/cli.md#weather-stacli) and [`pet.cli`](../input-reference/cli.md#observed-data-lists) for station PET.
- [gwflow](gwflow.md): inputs of the gridded groundwater module.
- [Soil carbon](../model-theory/carbon.md), [nutrient cycling](../model-theory/nutrient-cycling.md) and [channels](../model-theory/channels.md): process descriptions.

??? quote "Sources"

    - Reader: [`basin_read_cc.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_cc.f90), called from [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)
    - Type definition: `type basin_control_codes` in [`basin_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_module.f90)
    - File name slot: `in_basin%codes_bas` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - PET: [`et_pot.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_pot.f90); station PET in [`climate_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/climate_control.f90)
    - `event`: [`plant_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_parm_read.f90), [`soil_plant_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_plant_init.f90)
    - Crack flow: [`sq_crackvol.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_crackvol.f90), [`sq_crackflow.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_crackflow.f90), [`swr_percmacro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmacro.f90), [`swr_percmain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_percmain.f90)
    - SWIFT output: annual sums in [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90), files written by [`swift_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swift_output.f90), called at the end of [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - Peak rate and erosion: [`ero_pkq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_pkq.f90), [`ero_cfactor.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_cfactor.f90), [`ero_ovrsed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ero_ovrsed.f90), [`surface.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/surface.f90)
    - Channel routing: [`ch_rtmusk.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtmusk.f90), [`sd_hydsed_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_hydsed_init.f90); in-stream nutrients in [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90)
    - Plant stress: [`pl_biomass_gro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_biomass_gro.f90)
    - Carbon model branches: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`soil_nutcarb_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_init.f90), [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90), [`cbn_zhang2.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cbn_zhang2.f90)
    - Lapse rates: [`cli_lapse.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cli_lapse.f90), applied in `hru_control.f90`
    - Unit hydrograph: [`unit_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/unit_hyd.f90), [`unit_hyd_ru_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/unit_hyd_ru_hru.f90), [`hru_hyds.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_hyds.f90)
    - Runoff method: [`sq_volq.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sq_volq.f90)
    - Tile drainage and water table: `swr_percmain.f90`
    - gwflow activation: [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90)

    | Column | Fortran variable |
    |--------|------------------|
    | `pet_file` | `bsn_cc%petfile` |
    | `wq_file` | `bsn_cc%wwqfile` |
    | `pet` | `bsn_cc%pet` |
    | `event` | `bsn_cc%nam1` |
    | `crack` | `bsn_cc%crk` |
    | `swift_out` | `bsn_cc%swift_out` |
    | `sed_det` | `bsn_cc%sed_det` |
    | `rte_cha` | `bsn_cc%rte` |
    | `deg_cha` | `bsn_cc%deg` |
    | `wq_cha` | `bsn_cc%wq` |
    | `nostress` | `bsn_cc%nostress` |
    | `cn` | `bsn_cc%cn` |
    | `c_fact` | `bsn_cc%cfac` |
    | `carbon` | `bsn_cc%cswat` |
    | `lapse` | `bsn_cc%lapse` |
    | `uhyd` | `bsn_cc%uhyd` |
    | `sed_cha` | `bsn_cc%sed_ch` |
    | `tiledrain` | `bsn_cc%tdrn` |
    | `wtable` | `bsn_cc%wtdn` |
    | `soil_p` | `bsn_cc%sol_p_model` |
    | `gampt` | `bsn_cc%gampt` |
    | `atmo_dep` | `bsn_cc%atmo` |
    | `stor_max` | `bsn_cc%smax` |
    | `i_fpwet` | `bsn_cc%qual2e` |
    | `gw_flow` | `bsn_cc%gwflow` |
    | `idc_till` | `bsn_cc%idc_till` |

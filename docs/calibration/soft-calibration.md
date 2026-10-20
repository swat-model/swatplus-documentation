---
title: Soft calibration
description: The codes.sft switches, the targets in each soft calibration input file, the adjustment steps, and the output files.
status: review
verified_against:
  - src/main.f90.in
  - src/proc_cal.f90
  - src/calsoft_read_codes.f90
  - src/lcu_read_softcal.f90
  - src/ls_read_parms_cal.f90
  - src/pl_read_regions_cal.f90
  - src/pl_read_parms_cal.f90
  - src/ch_read_orders_cal.f90
  - src/ch_read_parms_cal.f90
  - src/calsoft_control.f90
  - src/calsoft_hyd.f90
  - src/calsoft_hyd_bfr.f90
  - src/calsoft_hyd_bfr_pet.f90
  - src/calsoft_hyd_bfr_et.f90
  - src/calsoft_hyd_bfr_surq.f90
  - src/calsoft_hyd_bfr_latq.f90
  - src/calsoft_hyd_bfr_perc.f90
  - src/calsoft_plant.f90
  - src/calsoft_sed.f90
  - src/calsoft_sum_output.f90
  - src/calsoft_ave_output.f90
  - src/pl_write_parms_cal.f90
  - src/header_write.f90
  - src/hydro_init.f90
  - src/topohyd_init.f90
  - src/calibration_data_module.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Soft calibration adjusts a small set of HRU and plant parameters until the simulated average annual water balance and crop yields match targets given for each land-use group. The targets are soft data: regional estimates such as the fraction of precipitation that leaves as surface runoff or evapotranspiration, the share of streamflow that is baseflow, or an average county yield. They are not time series.

Soft calibration runs inside the normal `swatplus` executable. After the base simulation ends, SWAT+ changes one parameter at a time and reruns the whole simulation period after each change. Each rerun is labelled on screen (`first esco adj`, `cn3_swf adj`, `epco adj`, and so on). A water balance calibration adds up to 17 full simulations in mode `a` and 20 in mode `b`, and plant calibration up to 13 more. The calibrated values are written to new files (see [Output files](#output-files)); the model inputs are left unchanged.

In 62.0.1 two components work: the HRU water balance (`hyd` switch) and crop yield (`plnt` switch). The other switches are read, but they do not adjust anything. The status column of the [switch table](#codessft) gives the detail for each.

## Run sequence

1. At start-up SWAT+ reads the seven soft calibration files. A missing file, or a `null` name in [`file.cio`](../input-reference/file-cio.md), gives an empty table and that part is skipped. Without `codes.sft` soft calibration is off.
2. Any changes in [`calibration.cal`](../calibration/parameter-change-files.md) are applied (see [Hard calibration](../calibration/hard-calibration.md)), so soft calibration starts from the changed values.
3. The base simulation runs as usual. At the end of each simulated year every HRU's annual water balance is added to its land-use group, and each harvest adds its yield to the plant targets.
4. If any switch in `codes.sft` is on, soft calibration runs next. It first sets the [`print.prt`](../input-reference/print-prt.md) codes back to their defaults, which are mostly off, and turns on the average annual basin water balance. The warm-up period (`nyskip`) is kept. Most output files therefore contain the base run, and `basin_wb_aa.txt` gains a record for each calibration run.
5. Each adjustment step changes one parameter for every HRU in each land-use group that is outside its tolerance, restores the starting state of the model, and reruns the full period. The steps are listed under [Adjustment steps](#adjustment-steps).
6. The calibrated parameters are written out.

## Input files

The `chg` line of [`file.cio`](../input-reference/file-cio.md) names nine files. The first two are the hard calibration files described in [Parameter change files](../calibration/parameter-change-files.md). The last seven belong to soft calibration:

| Position on `chg` line | Default name | Earlier name | Content |
|---|---|---|---|
| 3 | `codes.sft` | `codes.cal` | component switches |
| 4 | `wb_parms.sft` | `ls_parms.cal` | limits for the water balance parameters |
| 5 | `water_balance.sft` | `ls_regions.cal` | water balance targets by land-use group |
| 6 | `ch_sed_budget.sft` | `ch_orders.cal` | channel erosion targets |
| 7 | `ch_sed_parms.sft` | `ch_parms.cal` | limits for the channel parameters |
| 8 | `plant_parms.sft` | `pl_parms.cal` | plant parameter start values and limits |
| 9 | `plant_gro.sft` | `pl_regions.cal` | crop yield targets |

A file is only read when its name is on the `chg` line. A project written by SWAT+ Editor 4.0.1 can contain the `.sft` files while their names on the `chg` line are `null`. In that case edits to the files have no effect.

All files are free format. Values are separated by blanks, and names must not contain blanks or slashes. The first line of every file is a title and is skipped.

### codes.sft

- Line 1: title.
- Line 2: header.
- Line 3: eight one-letter switches in the order below.

| # | Column | Values | Status in 62.0.1 |
|---|---|---|---|
| 1 | `hyd` | `n`, `a`, `b`, `y` | Works. `a` and `b` select the mode; `y` behaves as `b`. |
| 2 | `landscape` | `n`, `y` | Not usable. It is meant for simplified (`hru-lte`) HRUs, but its target table is never set up. |
| 3 | `plnt` | `n`, `y` | Works, crop yield targets only. |
| 4 | `sed` | `n`, `y` | Not usable, see [Upland sediment](#upland-sediment). |
| 5 | `nut` | `n`, `y` | Nothing is calibrated. Setting `y` starts the soft calibration runs and changes nothing. |
| 6 | `ch_sed` | `n`, `y` | Channel results are summed, but no parameter is adjusted. |
| 7 | `ch_nut` | `n`, `y` | Nothing is calibrated. |
| 8 | `res` | `n`, `y` | Nothing is calibrated. |

Soft calibration runs when `hyd` is anything other than `n` or any other switch is `y`.

Mode `a` calibrates each water balance component against a separate ratio of precipitation. Mode `b` uses only the water yield ratio and the baseflow share (`wyr` and `bfr` in `water_balance.sft`) and derives the other targets from them. The steps for each mode are under [Adjustment steps](#adjustment-steps).

Example (SWAT+ Editor 4.0.1 layout with `hyd` set to `b`):

```
codes.sft: written by SWAT+ editor v4.0.1 on 2026-09-13 21:18 for SWAT+ rev. 62
hyd           landscape     plnt          sed           nut           ch_sed        ch_nut        res
b             n             n             n             n             n             n             n
```

### water_balance.sft

- Line 1: title.
- Line 2: number of regions.
- Line 3: header.
- For each region: a line with the region name and the number of land-use rows. If that number is above zero, a header line follows, then one target row per land-use group.

Use a single region. The HRU list of a region is filled only when the region is named `basin` or the file has one region, and in both cases the region contains every HRU. A second region gets no HRUs and is not calibrated. HRU areas are taken from [`ls_unit.ele`](../input-reference/units.md#ls_unitele) (the `bsn_frac` of element *i* is used for HRU *i*).

Target rows:

| # | Column | Units | Description |
|---|---|---|---|
| 1 | `name` | none | Land-use group. Matched to the `cal_group` column of [`landuse.lum`](../input-reference/lum.md). The name `basin` matches every HRU. |
| 2 | `surq_rto` | fraction of precipitation | Surface runoff / precipitation. Mode `a` target for `cn3_swf`. In mode `b` the value is replaced when the file is read by `wyr` × (1 − `bfr`). |
| 3 | `latq_rto` | fraction of precipitation | Lateral flow / precipitation. Mode `a` target for `latq_co`. In mode `b` it is replaced by 0.1 × `wyr` × `bfr`. |
| 4 | `perc_rto` | fraction of precipitation | Percolation below the soil profile / precipitation. Mode `a` target for `perco`. In mode `b` it is added to `wyr` to form the `esco` target. |
| 5 | `et_rto` | fraction of precipitation | Actual ET / precipitation. Mode `a` target for `esco` and `pet_co`. Not used in mode `b`. |
| 6 | `tileq_rto` | fraction | Read; not used as a target. |
| 7 | `pet` | mm | Read; not used. |
| 8 | `sed` | t/ha | Upland sediment yield target for the `sed` switch. |
| 9 | `wyr` | fraction of precipitation | Water yield / precipitation. Mode `b` target for `pet_co` and `esco`. |
| 10 | `bfr` | fraction of water yield | Share of water yield that is baseflow. Mode `b` only. Converted when the file is read to baseflow / precipitation (`wyr` × `bfr`), the target for `perco`. |
| 11 | `solp` | kg/ha | Read; not used. |

The simulated values are built from the HRU annual water balance (the columns of `hru_wb_yr`), weighted by HRU area:

- precipitation: `precip`
- surface runoff: `surq_gen`
- lateral flow: `latq`
- percolation: `perc`
- ET: `et`
- water yield: `surq_gen + latq + perc + qtile`
- baseflow: `latq + perc + qtile`

An HRU is left out of these sums once it has received more than 10 mm of irrigation in total. Its parameters are still changed with the rest of its group. The ratios in a row are not checked to add up to 1.

Example written by SWAT+ Editor 4.0.1 for revision 62. The row contains mode `a` ratios. `wyr` and `bfr` are zero, so in mode `b` every target would be zero and nothing would be calibrated.

```
water_balance.sft: written by SWAT+ editor v4.0.1 on 2026-09-13 21:18 for SWAT+ rev. 62
1
name                   num
basin                    1
    name                  surq_rto      latq_rto      perc_rto        et_rto     tileq_rto           pet           sed           wyr           bfr          solp
    basin                  0.20000       0.10000       0.10000       0.50000       0.00000       0.90000       0.00000       0.00000       0.00000       0.00000
```

### wb_parms.sft

- Line 1: title.
- Line 2: number of rows.
- Line 3: header.
- Then one row per parameter: `name chg_typ neg pos lo up`.

SWAT+ uses the rows by position and does not look at `name` or `chg_typ`. Keep the ten rows in the order below; renaming or reordering them changes which limits each step uses.

| Row | `name` | Parameter changed | Used by | How it is changed |
|---|---|---|---|---|
| 1 | `cn2` | curve number of simplified HRUs | `landscape` switch; `pos` is also used by the `sed` switch | added |
| 2 | `esco` | `esco` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | modes `a` and `b` | added |
| 3 | `latq_co` | `latq_co` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | modes `a` and `b` | added |
| 4 | `petco` | `pet_co` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | modes `a` and `b` | multiplied |
| 5 | `slope` | HRU slope | `sed` switch | subtracted |
| 6 | `tconc` | time of concentration | `sed` switch | divided |
| 7 | `etco` | ET coefficient of simplified HRUs | `landscape` switch | added |
| 8 | `perco` | `perco` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) | modes `a` and `b` | added |
| 9 | `revapc` | revap coefficient of simplified HRUs | `landscape` switch | added |
| 10 | `cn3_swf` | `cn3_swf` in [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd), with the curve numbers recomputed | modes `a` and `b` | added |

For the HRU water balance rows (2, 3, 4, 8, 10):

- `neg` and `pos` limit the adjustment made for one land-use group. For `petco` they limit the multiplier (Editor default 0.54 to 1.85). A group that reaches a limit is flagged, and some later runs skip it.
- `lo` and `up` bound the HRU parameter value after every change.

Mode `b` narrows the `petco` range for its first PET step. It halves `neg` and `pos` and moves `lo` and `up` halfway toward 1, then restores the full range for the second PET step. See [Limits in 62.0.1](#limits-in-6201) for what this does with the Editor defaults.

`cn3_swf` and `perco` are not changed on tile-drained HRUs. At start-up those HRUs are set to `cn3_swf` = 0.95 and `perco` = 0.1.

Example written by SWAT+ Editor 4.0.1 for revision 62:

```
wb_parms.sft: written by SWAT+ editor v4.0.1 on 2026-09-13 21:18 for SWAT+ rev. 62
10
name                       chg_typ           neg           pos            lo            up
cn2                         abschg      -6.00000       6.00000      35.00000      95.00000
esco                        abschg      -1.00000       1.00000       0.00000       1.00000
latq_co                     abschg      -1.00000       1.00000       0.00000       1.00000
petco                       abschg       0.54000       1.85000       0.70000       1.20000
slope                       pctchg     -25.00000      25.00000       0.00010       0.90000
tconc                       pctchg     -30.00000      30.00000       5.00000     960.00000
etco                        abschg      -0.40000       0.40000       0.80000       1.20000
perco                       abschg      -0.70000       0.70000       0.00100       1.00000
revapc                      abschg      -0.40000       0.40000       0.00000       0.40000
cn3_swf                     abschg      -1.20000       1.20000       0.00000       1.00000
```

### plant_gro.sft

- Line 1: title.
- Line 2: number of regions.
- Line 3: header.
- For each region:
    - a line with `name`, the number of plants (`lum_num`), `nspu`, and then `nspu` HRU numbers;
    - if `lum_num` is above zero, a header line and one target row per plant.

With `nspu` = 0 the region covers every HRU. Otherwise `nspu` numbers follow, and a negative number closes a range: with `nspu` = 3, the list `1 -20 35` means HRUs 1 to 20 and HRU 35. Each HRU belongs to one plant region. `plant_parms.sft` is read second, so its region assignment is the one that applies.

Target rows:

| # | Column | Units | Description |
|---|---|---|---|
| 1 | `name` | none | Plant name. Matched to the plant named in the harvest operation (`harv` or `hvkl` in a management schedule, `harvest` or `harvest_kill` in a decision table). |
| 2 | `yield` | t/ha | Target yield. Compared with the total harvested yield divided by the total harvested area over the whole run. |
| 3 | `npp` | t/ha | Read; not used. |
| 4 | `lai_mx` | none | Read; not used. |
| 5 | `wstress` | none | Read; not used. |
| 6 | `astress` | none | Read; not used. |
| 7 | `tstress` | none | Read; not used. |

### plant_parms.sft

- Line 1: title.
- Line 2: number of regions. Region *i* here is paired with region *i* of `plant_gro.sft`.
- Line 3: header.
- For each region:
    - a line with `name`, `lum_num`, `parms` and `nspu`;
    - if `lum_num` is above zero, a header line and `lum_num` × `parms` parameter rows.

Set `nspu` to 0 here, which puts every HRU in the region. With `nspu` above zero the region line is read a second time without the `parms` field, so the HRU list is misread.

Set `parms` to 4. The rows form four blocks of `lum_num` rows each, in this order: `pest_stress`, `epco`, `lai_pot`, `harv_idx`. Within every block the plants must be in the same order as in the matching `plant_gro.sft` region. SWAT+ finds a row by its position in the block and always runs all four steps.

Parameter rows:

| # | Column | Description |
|---|---|---|
| 1 | `var` | `pest_stress`, `epco`, `lai_pot` or `harv_idx` |
| 2 | `name` | plant name |
| 3 | `init_val` | start value, applied when the file is read to every plant of that name in the region's HRUs. This happens whether or not `plnt` is on. |
| 4 | `chg_typ` | read; not used |
| 5 | `neg` | lower limit of the adjustment. For `epco` it is the lowest `epco` value the calibration may set. |
| 6 | `pos` | upper limit of the adjustment. For `epco` it is the highest `epco` value the calibration may set. |
| 7 | `lo` | lower bound on the plant's value |
| 8 | `up` | upper bound on the plant's value |

### ch_sed_budget.sft and ch_sed_parms.sft

These two files are read, but no channel parameter is adjusted.

`ch_sed_budget.sft` layout:

- Line 1: title.
- Line 2: number of regions.
- Line 3: header.
- For each region: `name`, the number of target rows (`ord_num`), `nspu` and `nspu` channel numbers (0 means all channels). A header line always follows, then `ord_num` rows of `name chw chd hc fpd`.

The row fields are channel widening (mm/yr), downcutting or accretion (mm/yr), headcut advance (m/yr) and floodplain accretion (mm/yr).

`ch_sed_parms.sft` has the same layout as `wb_parms.sft`. Only `name` and `chg_typ` of its first row are used, and only when writing the channel summary.

The channel results are only summed when `ch_sed` is the only switch on, and only target rows named `basin` collect them.

## Adjustment steps

In every step:

- The tolerance is the relative difference |target − simulated| / target, taken over the average annual values of the land-use group.
- A step only reruns the simulation if at least one group is outside tolerance.
- The first run of a step moves the parameter by a fixed rate. Later runs use a secant estimate from the last two runs.

### Water balance, mode a

| Step | Parameter | Target compared | Tolerance | Runs | First-run change | `wb_parms.sft` row |
|---|---|---|---|---|---|---|
| 1 | `esco` | `et_rto` × precipitation vs simulated ET | 1 % | 1 + 2 | + (target − simulated, mm) / 500 | 2 |
| 2 | `pet_co` | same as step 1 | 1 % | 2 | multiplied by a ratio near 1 | 4 |
| 3 | `cn3_swf` | `surq_rto` × precipitation vs `surq_gen` | 2 % | 1 + 2 | − (target − simulated, mm) / 100 | 10 |
| 4 | `latq_co` | `latq_rto` × precipitation vs `latq` | 10 % first run, 5 % after | 1 + 1 | + 0.0025 × (target − simulated, mm) | 3 |
| 5 | `perco` | `perc_rto` × precipitation vs `perc` | 5 % | 1 + 3 | + 0.001 × (target − simulated, mm) | 8 |
| 6 | `cn3_swf` | as step 3 | 2 % | 1 + 2 | as step 3 | 10 |

For example, with `surq_rto` = 0.2, 800 mm of precipitation and 120 mm of simulated surface runoff, the target is 160 mm, the difference is 40 mm, and the first `cn3_swf` run lowers `cn3_swf` by 0.4.

### Water balance, mode b

| Step | Parameter | Target compared | Tolerance | Runs |
|---|---|---|---|---|
| 1 | `pet_co`, half range | `wyr` × precipitation vs simulated water yield | 1 % | 2 |
| 2 | `esco` | (`wyr` + `perc_rto`) × precipitation vs simulated water yield | 1 % | 1 + 2 |
| 3 | `pet_co`, full range | as step 1 | 1 % | 2 |
| 4 | `cn3_swf` | `wyr` × (1 − `bfr`) × precipitation vs `surq_gen` | 2 % | 1 + 2 |
| 5 | `latq_co` | 0.1 × `wyr` × `bfr` × precipitation vs `latq` | 10 % first run, 5 % after | 1 + 2 |
| 6 | `perco` | `wyr` × `bfr` × precipitation vs `latq + perc + qtile` | 5 % | 1 + 3 |
| 7 | `cn3_swf` | as step 4 | 2 % | 1 + 2 |

### Crop yield

Each plant's average harvested yield is compared with its `plant_gro.sft` target:

1. Aeration stress. If the yield is more than 20 % below target, HRUs growing that plant that have no tile drain and an accumulated aeration stress above 50 get `perco` = 0.95. One run.
2. `epco`, with a 3 % tolerance. The first run sets `epco` to 1, or to a low value when the yield is more than 10 % above target. Four more runs narrow the interval between 0 and 1. The value is kept within `neg` and `pos` of the `epco` block.
3. `pest_stress`, changed by the relative yield error. One run.
4. `lai_pot`, 1 LAI unit for every 20 % of yield difference, then secant. 1 + 2 runs.
5. `harv_idx`, half the relative yield difference, then secant. 1 + 2 runs.

### Upland sediment

The `sed` switch is meant to fit the `sed` targets by shortening the time of concentration and lowering the HRU slope, with the USLE slope-length factor recomputed. In 62.0.1 it does not work:

- Its loops run over the number of channel regions instead of the number of water balance regions.
- Simulated sediment is only summed when `hyd` is also on.
- The secant runs always compute a change of zero.

Treat the `sed` switch as unavailable.

## Output files

| File | Written when | Content |
|---|---|---|
| `hydrology-cal.hyd` | `hyd` or `plnt` on | One row per HRU with the calibrated [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) values, written at the end. |
| `plant_parms.cal` | `plnt` on | Same layout as `plant_parms.sft`, with `init_val` updated to the calibrated values and `nspu` set to 0. |
| `hru-out.cal` | any switch on | Header only, except with the `landscape` switch, which appends the simplified HRU parameters. |
| `hru-new.cal` | `hyd` on | Opened but left empty. |

To use the results in later runs, point [`file.cio`](../input-reference/file-cio.md) at the new files:

- Use `plant_parms.cal` as `plant_parms.sft`. Its `init_val` values are applied when the file is read, also with `plnt` = `n`.
- Use `hydrology-cal.hyd` as [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd), after the edits in the warning below. Rows are written per HRU under the name of its [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd) record, so every HRU needs a separate record. The extra 16th column (`perco_lim`, labelled `NOT_USED`) is ignored when the file is read.

!!! warning "Converting hydrology-cal.hyd back to an input"
    Two edits are needed before `hydrology-cal.hyd` can replace [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd):

    - `LAT_TTIME` contains the value after the start-up conversion, 1 − exp(−1 / days). Read back as an input it is taken as days and converted a second time, which makes lateral flow drain much faster. Put the original `lat_ttime` values back before using the file.
    - When `hyd` and `plnt` are both on, the file contains the title, header and HRU rows twice. Keep only the second set, which is written after plant calibration.

## Limits in 62.0.1

- Only one water balance region works (see [water_balance.sft](#water_balancesft)).
- `wb_parms.sft` and `plant_parms.sft` rows are found by position, so the row order is part of the format.
- In mode `b` the first PET step halves `neg` and `pos` for `petco`. With the Editor defaults (0.54, 1.85) the upper limit becomes 0.925. When simulated water yield is too high the step should raise PET; it caps the multiplier at 0.925 and lowers PET instead.
- `plant_parms.sft` must use `nspu` = 0 and `parms` = 4.
- The `landscape`, `sed`, `nut`, `ch_sed`, `ch_nut` and `res` switches do not calibrate anything (see [codes.sft](#codessft)).
- Annual sums include the warm-up years, but the averages divide by the printed years only. Target ratios are unaffected because precipitation is treated the same way. The fixed first-run rates, which are in mm, act on values scaled by the same factor.

## Related pages

- [Hard calibration](../calibration/hard-calibration.md). Changes from [`calibration.cal`](../calibration/parameter-change-files.md), applied before the base run.
- [Parameter change files](../calibration/parameter-change-files.md). [`cal_parms.cal`](../calibration/parameter-change-files.md) and [`calibration.cal`](../calibration/parameter-change-files.md), the first two files on the `chg` line.
- [landuse.lum](../input-reference/lum.md). The `cal_group` column that `water_balance.sft` rows are matched against.
- [hydrology.hyd](../input-reference/hyd.md). The parameters written to `hydrology-cal.hyd`.

??? quote "Sources"

    - Readers, called from [`src/proc_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cal.f90) in this order: [`pl_read_regions_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_read_regions_cal.f90) (`plant_gro.sft`), [`pl_read_parms_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_read_parms_cal.f90) (`plant_parms.sft`), [`calsoft_read_codes.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_read_codes.f90) (`codes.sft`), [`lcu_read_softcal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/lcu_read_softcal.f90) (`water_balance.sft`), [`ls_read_parms_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ls_read_parms_cal.f90) (subroutine `ls_read_lsparms_cal`, `wb_parms.sft`), [`ch_read_orders_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_orders_cal.f90) (`ch_sed_budget.sft`), [`ch_read_parms_cal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_read_parms_cal.f90) (`ch_sed_parms.sft`).
    - Control: [`src/calsoft_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_control.f90), called from [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in) after the base simulation when `cal_soft = "y"`.
    - Water balance: [`src/calsoft_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_hyd.f90) (mode `a`); [`src/calsoft_hyd_bfr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_hyd_bfr.f90) and its steps `calsoft_hyd_bfr_pet`, `_et`, `_surq`, `_latq`, `_perc` (mode `b`).
    - Crop yield: [`src/calsoft_plant.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_plant.f90), `calsoft_plant_zero.f90`, `pl_write_parms_cal.f90`. Yields are added to the targets at harvest in `mgt_sched.f90` and `actions.f90`.
    - Upland sediment: [`src/calsoft_sed.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calsoft_sed.f90). Simplified HRU water balance: `caltsoft_hyd.f90`.
    - Annual sums and averages: `calsoft_sum_output.f90` (end of every simulated year, called from `time_control.f90`) and `calsoft_ave_output.f90` (end of every run).
    - Tile-drained HRU settings: `topohyd_init.f90`. `lat_ttime` conversion: `hydro_init.f90`. Output files are opened in `header_write.f90`.
    - Types: [`src/calibration_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/calibration_data_module.f90). File names: `type input_chg` in `src/input_file_module.f90`.

    | File and column | Fortran variable |
    |---|---|
    | `codes.sft` `hyd`, `landscape`, `plnt`, `sed`, `nut`, `ch_sed`, `ch_nut`, `res` | `cal_codes%hyd_hru`, `%hyd_hrul`, `%plt`, `%sed`, `%nut`, `%chsed`, `%chnut`, `%res` |
    | `water_balance.sft` target row | `type soft_calib_ls_processes`: `name`, `srr`, `lfr`, `pcr`, `etr`, `tfr`, `pet`, `sed`, `wyr`, `bfr`, `solp` |
    | `wb_parms.sft` rows | `ls_prms(1:10)` |
    | `plant_gro.sft` target row | `type soft_calib_pl_processes` |
    | `plant_parms.sft` parameter row | `type pl_parms_cal`; row *k* of block *b* is `prm(k + (b-1)*lum_num)` |
    | HRU land-use group | `hru%lum_group_c`, from `landuse.lum` `cal_group` |
    | accumulated aeration stress | `strsa` |

    | Output file | Unit |
    |---|---|
    | `hydrology-cal.hyd` | 5001 |
    | `plant_parms.cal` | 107 |
    | `hru-out.cal` | 4999 |
    | `hru-new.cal` | 5000 |

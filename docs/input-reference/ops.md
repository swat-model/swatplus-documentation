---
title: "*.ops (operation databases)"
description: Parameter databases for harvest, grazing, irrigation, chemical application, fire and street sweeping operations.
status: review
verified_against:
  - src/mgt_read_harvops.f90
  - src/mgt_read_grazeops.f90
  - src/mgt_read_irrops.f90
  - src/mgt_read_chemapp.f90
  - src/mgt_read_fireops.f90
  - src/mgt_read_sweepops.f90
  - src/mgt_operations_module.f90
  - src/input_file_module.f90
  - src/proc_db.f90
  - src/mgt_sched.f90
  - src/actions.f90
  - src/mgt_harvgrain.f90
  - src/mgt_harvbiomass.f90
  - src/mgt_harvtuber.f90
  - src/mgt_harvresidue.f90
  - src/pl_graze.f90
  - src/hru_control.f90
  - src/pl_burnop.f90
  - src/hru_sweep.f90
  - src/hru_urbanhr.f90
  - src/pl_fert.f90
  - src/pest_apply.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The six operation databases contain named parameter sets for management operations. A scheduled operation in [`management.sch`](management.md) or an action in a [`lum.dtl`](dtl.md) decision table names an entry, and SWAT+ uses that entry's values when the operation runs.

| File | Contents | Used by |
|------|----------|---------|
| `harv.ops` | harvest operations | `harv` and `hvkl` in [`management.sch`](../input-reference/management.md#managementsch); `harvest` and `harvest_kill` in [`lum.dtl`](../input-reference/dtl.md) |
| `graze.ops` | grazing operations | `graz` in [`management.sch`](../input-reference/management.md#managementsch); `graze` in [`lum.dtl`](../input-reference/dtl.md) |
| `irr.ops` | irrigation operations | `irrm`, `irrp` and `irpm` in [`management.sch`](../input-reference/management.md#managementsch); `irrigate` and `irr_demand` in [`lum.dtl`](../input-reference/dtl.md) |
| `chem_app.ops` | application methods for fertilizer, manure and pesticide | `fert`, `manu` and `pest` in [`management.sch`](../input-reference/management.md#managementsch); `fertilize`, `fert_future`, `manure`, `pest_apply` and `manure_demand` in [`lum.dtl`](../input-reference/dtl.md) |
| `fire.ops` | burning operations | `burn` in [`management.sch`](../input-reference/management.md#managementsch) and [`lum.dtl`](../input-reference/dtl.md) |
| `sweep.ops` | street sweeping operations | `swep` in [`management.sch`](../input-reference/management.md#managementsch) |

The six file names are given on the `ops` line of [`file.cio`](file-cio.md), in the order harvest, graze, irrigation, chemical application, fire, sweep. The defaults are the names in the table. If a file is missing, or named `null` in [`file.cio`](../input-reference/file-cio.md), the database is empty, and any operation that names an entry from it uses an entry with all values zero (irrigation depth 25.4 mm).

## Format

All six files share one layout. Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one operation. The columns are read by position, so every column in the tables below must be present and in this order. A trailing `description` column, which the SWAT+ Editor writes, is ignored.

Names are matched exactly against the names used in [`management.sch`](../input-reference/management.md#managementsch) and [`lum.dtl`](../input-reference/dtl.md). A name that is not found leaves the operation pointing at an empty entry with zero values, and no message is written.

## harv.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Harvest operation name. |
| 2 | `harv_typ` | - | see below | Harvest type. |
| 3 | `harv_idx` | fraction | 0 to 1 | Harvest index override: the fraction of above-ground biomass cut. Used by biomass harvests and, as a multiplier, by `residue`. Ignored by grain and root harvests. |
| 4 | `harv_eff` | fraction | 0 to 1 | Harvest efficiency: the fraction of the harvested material removed from the HRU. |
| 5 | `harv_bm_min` | kg/ha | 0 and up | Minimum plant biomass for the harvest to take place. For `residue` harvests, the minimum surface residue left behind. |

The harvest types and what each one does:

| `harv_typ` | Harvest only (`harv`, `harvest`) | Harvest and kill (`hvkl`, `harvest_kill`) |
|------------|----------------------------------|-------------------------------------------|
| `grain` | grain harvest | grain harvest |
| `picker` | grain harvest | grain harvest |
| `stripper` | biomass harvest | grain harvest |
| `biomass` | biomass harvest | biomass harvest |
| `tree` | biomass harvest | no harvest; the plant is only killed |
| `tuber` | root harvest | root harvest |
| `peanuts` | root harvest | root harvest |
| `residue` | residue harvest | residue harvest |

A harvest of a growing plant runs only if the plant's total biomass is above `harv_bm_min`. A `residue` harvest scheduled after the plant has died runs without this check.

Grain harvest. The yield is $Y = \mathrm{harv\_eff} \cdot M_{seed}$, where $M_{seed}$ is the seed (yield) pool built up during growth from the harvest index in [`plants.plt`](plt.md). The seed mass that is not removed goes to the top soil layer as organic matter. `harv_idx` has no effect.

Biomass harvest. A fraction $h = \mathrm{harv\_idx} \cdot \mathrm{harv\_eff}$ of the seed, leaf and stem mass is cut. The cut takes place only if the above-ground biomass left afterwards is above `harv_bm_min`. The cut mass is reported as yield, and a further $(1 - \mathrm{harv\_eff})$ times the cut mass is added to the surface residue. Leaf area and accumulated heat units are multiplied by $1 - 0.5\,h$.

Root harvest (`tuber`, `peanuts`). The yield is `harv_eff` times the root mass. The remaining roots stay in the soil as residue.

Residue harvest. Each plant's surface residue is reduced by the fraction $e \cdot \mathrm{harv\_idx}$, but not below `harv_bm_min`. The efficiency $e$ is the `op_data3` value of the [`management.sch`](../input-reference/management.md#managementsch) row (or `const` of the decision table action) when it is greater than zero, and `harv_eff` otherwise.

For every type, the reported yield is reduced by the plant's pest stress.

## graze.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Grazing operation name. |
| 2 | `fert` | - | - | Name of the manure in [`fertilizer.frt`](frt.md) that the animals deposit. Called `fertname` in earlier documentation. |
| 3 | `bm_eat` | kg/ha/day | 0 to 500 | Dry biomass removed by grazing each day. |
| 4 | `bm_tramp` | kg/ha/day | 0 to 500 | Dry biomass removed by trampling each day. Read but not applied. |
| 5 | `man_amt` | kg/ha/day | 0 to 500 | Dry manure deposited each day. |
| 6 | `grz_bm_min` | kg/ha | 0 to 5000 | Minimum above-ground biomass for grazing to take place on a given day. |

A `graz` row in [`management.sch`](../input-reference/management.md#managementsch) starts a grazing period, and its `op_data3` value is the length of the period in days. On each day of the period, if the HRU's above-ground biomass is at least `grz_bm_min`, the model removes `bm_eat` from the plants (spread over the plants in proportion to their above-ground biomass, and never more than is there) and adds `man_amt` of the named manure to the top soil layer. While a plant's biomass is below 2500 kg/ha, grazing also lowers its leaf area index by `bm_eat`/1000 and multiplies its accumulated heat units by $1 - \mathrm{bm\_eat}/1000$. A `graze` action in a decision table applies one day of grazing each time it fires.

The parameter values in the SWAT+ Editor's default `graze.ops` are rough estimates. If grazing matters in a watershed, derive values from the stocking rate and type of animal. Trampling is often set equal to `bm_eat` (the animals trample as much as they eat), but in 62.0.1 `bm_tramp` has no effect.

## irr.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Irrigation operation name. |
| 2 | `amt_mm` | mm | 0 and up | Irrigation depth per application. Called `irr_amt` in earlier documentation. |
| 3 | `eff_frac` | fraction | 0 to 1 | In-field efficiency: the fraction of applied water available to the crop. Called `irr_eff` in earlier documentation. |
| 4 | `sumq_frac` | fraction | 0 to 1 | Fraction of the applied water that leaves as surface runoff. Called `surq_rto` in earlier documentation. |
| 5 | `dep_sub` | mm | 0 and up | Application depth for subsurface irrigation. Read but not used. Called `irr_dep` in earlier documentation. |
| 6 | `salt_ppm` | ppm | 0 and up | Salt concentration in the irrigation water. Used by the paddy irrigation operation `irrp`. Called `irr_salt` in earlier documentation. |
| 7 | `no3_ppm` | ppm | 0 and up | Nitrate concentration in the irrigation water. Used by `irrp`. Called `irr_no3n` in earlier documentation. |
| 8 | `po4_ppm` | ppm | 0 and up | Phosphate concentration in the irrigation water. Read but not used. Called `irr_po4` in earlier documentation. |

A scheduled irrigation (`irrm` or `irpm` in [`management.sch`](../input-reference/management.md#managementsch)) applies

$$I_{applied} = \mathrm{amt\_mm} \cdot \mathrm{eff\_frac} \cdot (1 - \mathrm{sumq\_frac}), \qquad I_{runoff} = \mathrm{amt\_mm} \cdot \mathrm{sumq\_frac}$$

The `irrigate` action in [`lum.dtl`](../input-reference/dtl.md) uses the action's `const` (mm) in place of `amt_mm` and takes `eff_frac` and `sumq_frac` from the entry named in its `option` column. The `irr_demand` action with file pointer `unlim` uses `amt_mm`, but computes runoff as $\mathrm{amt\_mm} \cdot \mathrm{eff\_frac} \cdot \mathrm{sumq\_frac}$. See [`*.dtl`](dtl.md) for both actions.

## chem_app.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Application method name, for example `broadcast`, `band`, `foliar`, `inject`, `aerial_liquid`, `aerial_solid`, `drill`, `side_dress`, `fertigate`, `basal`, `rope_wick`, `tree_inject`. |
| 2 | `chem_form` | - | `solid`, `liquid` | Form of the chemical. Read but not used. |
| 3 | `app_typ` | - | `spread`, `spray`, `inject`, `direct` | Application type. Read but not used. |
| 4 | `app_eff` | fraction | 0 to 1 | Application efficiency. Multiplies the amount of a `pest` operation or `pest_apply` action. Not applied to fertilizer or manure. |
| 5 | `foliar_eff` | fraction | 0 to 1 | Foliar efficiency. Read but not used. |
| 6 | `inject_dp` | mm | 0 and up | Injection depth. Read but not used. |
| 7 | `surf_frac` | fraction | 0 to 1 | Fraction of the applied fertilizer, manure or pesticide placed in the top 10 mm soil layer. The rest goes to the second soil layer. |
| 8 | `drift_pot` | fraction | 0 to 1 | Drift potential. Read but not used. |
| 9 | `aerial_unif` | fraction | 0 to 1 | Aerial uniformity. Read but not used. |

A decision table `fertilize` action on an HRU with standing water applies the fertilizer to the water instead of the soil when the method's `surf_frac` is 1.

## fire.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Fire operation name, for example `grass`, `tree_intense`, `tree_low`. |
| 2 | `chg_cn2` | - | 0 to 20 | Amount added to the HRU's curve number for moisture condition II. The result is capped at 98. |
| 3 | `frac_burn` | fraction | 0 to 1 | Fraction of above-ground plant biomass, surface residue and top-layer soil organic matter burned. |

A burn removes `frac_burn` of the above-ground biomass of every plant, of the surface residue, and of the slow and passive humus in the top soil layer. The phosphorus in the burned material is returned to the passive humus pool, and the burned plant carbon is reported as emitted carbon.

## sweep.ops

| # | Column | Units | Typical range | Description |
|---|--------|-------|---------------|-------------|
| 1 | `name` | - | - | Street sweeping operation name. |
| 2 | `swp_eff` | fraction | 0 to 1 | Removal efficiency: the fraction of built-up solids removed from the swept curb length. |
| 3 | `frac_curb` | fraction | 0 to 1 | Fraction of the curb length that can be swept. Parked cars and other obstacles often make part of the curb unavailable. |

Street sweeping is meant for urban HRUs that use the build-up and wash-off method. The removal efficiency depends on the type of sweeper, whether flushing is part of the cleaning, the amount of solids and the frequency of rain, and is usually higher for particulate constituents than for nitrogen and phosphorus (Pitt, 1979). SWAT+ assumes fixed nutrient concentrations in the solids, so one efficiency applies to every constituent.

In 62.0.1 a `swep` operation reads the entry and logs it, but the sweeping routine uses a curb fraction of zero and is never called during the run, so `sweep.ops` has no effect on results.

## Example

`refdata/Osu_1hru` in the SWAT+ repository, first rows of each file:

```
harv.ops: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                      harv_typ      harv_idx      harv_eff   harv_bm_min  description
forest_cut                    tree       0.95000       0.99000       0.00000
grain                        grain       0.00000       0.95000       0.00000
grass_bag                  biomass       0.50000       1.00000    2000.00000
grass_mulch                biomass       0.50000       0.00000    2000.00000
```

`grass_bag` and `grass_mulch` both use a cut fraction of 0.5. With `harv_eff` at 1, `grass_bag` removes everything it cuts; with `harv_eff` at 0, `grass_mulch` cuts nothing ($h = 0.5 \times 0$). Both run only on plants above 2000 kg/ha. `grain` removes 95% of the seed pool.

```
graze.ops: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                          fert        bm_eat      bm_tramp       man_amt    grz_bm_min  description
dairy_high                dairy_fr      25.00000      10.00000       0.95000    3000.00000  High_Prod_Dairy-Fresh_Manure
```

```
irr.ops: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    amt_mm      eff_frac     sumq_frac       dep_sub      salt_ppm       no3_ppm       po4_ppm  description
sprinkler_med         25.00000       0.85000       0.00000       0.00000     100.00000      20.00000       1.00000
drip                  25.00000       0.90000       0.00000     100.00000     100.00000      20.00000       1.00000
```

A scheduled `sprinkler_med` irrigation puts $25 \times 0.85 = 21.25$ mm of water into the soil.

```
chem_app.ops: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                     chem_form           app_typ       app_eff    foliar_eff     inject_dp     surf_frac     drift_pot   aerial_unif  description
broadcast                    solid            spread       0.90000       0.00000       0.00000       1.00000       0.00000       1.00000
inject                      liquid            inject       0.95000       0.00000     150.00000       0.20000       0.00000       1.00000
```

```
fire.ops: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                   chg_cn2     frac_burn  description
grass                  8.00000       1.00000
tree_low               6.00000       0.70000
```

## Related files

- [`management.sch`](management.md): scheduled operations that name entries in these files.
- [`*.dtl`](dtl.md): decision table actions that name entries in these files.
- [`fertilizer.frt`](frt.md): the manure named in `graze.ops`, and the fertilizers applied with a `chem_app.ops` method.
- [`plants.plt`](plt.md): the plant harvest index that builds the seed pool used by grain harvests.
- [`file.cio`](file-cio.md): names the six files on its `ops` line.

??? quote "Sources"

    - Readers: [`mgt_read_harvops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_harvops.f90), [`mgt_read_grazeops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_grazeops.f90), [`mgt_read_irrops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_irrops.f90), [`mgt_read_chemapp.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_chemapp.f90), [`mgt_read_fireops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_fireops.f90), [`mgt_read_sweepops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_sweepops.f90), called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90)
    - Type definitions: [`mgt_operations_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_operations_module.f90)
    - File name slots: `type input_ops` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90)
    - Scheduled operations: [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90); decision table actions: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Harvest: [`mgt_harvgrain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvgrain.f90), [`mgt_harvbiomass.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvbiomass.f90), [`mgt_harvtuber.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvtuber.f90), [`mgt_harvresidue.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_harvresidue.f90)
    - Grazing: [`pl_graze.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_graze.f90), daily loop in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Burning: [`pl_burnop.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_burnop.f90)
    - Street sweeping: [`hru_sweep.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_sweep.f90), [`hru_urbanhr.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_urbanhr.f90)
    - Application methods: [`pl_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_fert.f90), [`pest_apply.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pest_apply.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `harv.ops` | `harv_typ` | `harvop_db%typ` |
    | `harv.ops` | `harv_idx` | `harvop_db%hi_ovr` |
    | `harv.ops` | `harv_eff` | `harvop_db%eff` |
    | `harv.ops` | `harv_bm_min` | `harvop_db%bm_min` |
    | `graze.ops` | `fert` | `grazeop_db%fertnm` (index stored in `grazeop_db%manure_id`) |
    | `graze.ops` | `bm_eat` | `grazeop_db%eat` |
    | `graze.ops` | `bm_tramp` | `grazeop_db%tramp` |
    | `graze.ops` | `man_amt` | `grazeop_db%manure` |
    | `graze.ops` | `grz_bm_min` | `grazeop_db%biomin` |
    | `irr.ops` | `eff_frac` | `irrop_db%eff` |
    | `irr.ops` | `sumq_frac` | `irrop_db%surq` |
    | `irr.ops` | `dep_sub` | `irrop_db%dep_mm` |
    | `irr.ops` | `salt_ppm`, `no3_ppm`, `po4_ppm` | `irrop_db%salt`, `%no3`, `%po4` |
    | `chem_app.ops` | `chem_form` | `chemapp_db%form` |
    | `chem_app.ops` | `app_typ` | `chemapp_db%op_typ` |
    | `chem_app.ops` | `inject_dp` | `chemapp_db%inject_dep` |
    | `fire.ops` | `chg_cn2` | `fire_db%cn2_upd` |
    | `fire.ops` | `frac_burn` | `fire_db%fr_burn` |
    | `sweep.ops` | `swp_eff` | `sweepop_db%eff` |
    | `sweep.ops` | `frac_curb` | `sweepop_db%fr_curb` |

---
title: "*.wet (wetland)"
description: Wetland table and wetland hydrology database for HRUs with ponded water, including rice paddies.
status: review
verified_against:
  - src/input_file_module.f90
  - src/main.f90.in
  - src/wet_read.f90
  - src/wet_read_hyd.f90
  - src/reservoir_data_module.f90
  - src/reservoir_module.f90
  - src/hru_allo.f90
  - src/wet_all_initial.f90
  - src/wet_initial.f90
  - src/hru_control.f90
  - src/et_act.f90
  - src/wetland_control.f90
  - src/res_weir_release.f90
  - src/res_hydro.f90
  - src/res_sediment.f90
  - src/res_nutrient.f90
  - src/swr_satexcess.f90
  - src/conditions.f90
  - src/actions.f90
  - src/mgt_sched.f90
  - src/pl_fert_wet.f90
  - src/mgt_newtillmix_wet.f90
  - src/hru_fr_change.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

A wetland in SWAT+ is an HRU that can store ponded water on its surface. The same mechanism simulates rice paddies. Two files are specific to wetlands, named in slots 7 and 8 of the `reservoir` line of [`file.cio`](file-cio.md):

- `wetland.wet`: one row per wetland, naming its initial conditions, hydrology, release rule, sediment and nutrient records.
- `hydrology.wet`: wetland hydrology records. Depths and areas are relative to the HRU.

Wetlands also use four reservoir files, described on the [reservoir page](res.md): [`initial.res`](../input-reference/res.md#initialres), [`sediment.res`](../input-reference/res.md#sedimentres), [`nutrients.res`](../input-reference/res.md#nutrientsres) and [`weir.res`](../input-reference/res.md#weirres). Release rules are decision tables in [`res_rel.dtl`](../input-reference/dtl.md) (see [decision tables](dtl.md)).

An HRU becomes a wetland when the `surf_stor` column of [`hru-data.hru`](hru.md) names a row of `wetland.wet`. With `null` there, the HRU has no ponded storage.

Both files are free format and whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. The readers do not match columns by header name, so every row needs all of its values in the order given below. Columns after the last one listed are ignored. Names must match, including case. A slot in [`file.cio`](../input-reference/file-cio.md) set to `null`, or a file that does not exist, leaves the table empty.

## wetland.wet

One row per wetland.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Wetland number. Read; not used. Rows are used in the order they appear. |
| 2 | `name` | - | Wetland name, matched against `surf_stor` in [`hru-data.hru`](../input-reference/hru.md). |
| 3 | `init` | - | Name of a row in [`initial.res`](res.md#initialres). |
| 4 | `hyd` | - | Name of a row in `hydrology.wet`. The name `paddy` switches on rice paddy behaviour; see [Outflow](#outflow). |
| 5 | `rel` | - | Name of a release decision table in [`res_rel.dtl`](../input-reference/dtl.md). Not used for paddies. |
| 6 | `sed` | - | Name of a row in [`sediment.res`](res.md#sedimentres). |
| 7 | `nut` | - | Name of a row in [`nutrients.res`](res.md#nutrientsres). |

Several HRUs can use the same row. A name that is not found is reported in `diagnostics.out` as `<name> not found (wet-init)`, `(wet-hyd)`, `(wet-release)`, `(wet-sed)` or `(wet-nut)`, and a `surf_stor` name that is not in `wetland.wet` as `<name>not found (wetland.wet)`. A wetland whose `hyd` is not found uses the built-in hydrology values (zero depths and areas). A non-paddy wetland whose `rel` is not found releases no water through its rule.

Some files, such as the example below, have an eighth column naming a weir record. 62.0.1 does not read it; how a wetland gets its weir record is described under [Storage volumes and weir height](#storage-volumes-and-weir-height).

## hydrology.wet

One row per wetland hydrology record.

| # | Column | Units | Built-in value | Description |
|---|--------|-------|----------------|-------------|
| 1 | `name` | - | - | Name of the hydrology record, matched against `hyd` in `wetland.wet`. |
| 2 | `hru_ps` | fraction | 0 | Fraction of the HRU area covered at the principal spillway (when flow over the surface inlet riser starts). Used only in the surface area set up before the first day, which the daily calculation replaces. |
| 3 | `dp_ps` | mm | 0 | Average water depth at the principal spillway. Sets the principal volume and, without weir records, the weir height. |
| 4 | `hru_es` | fraction | 0 | Fraction of the HRU area covered at the emergency spillway (when water starts to spill into the ditch). Not used in the daily simulation. |
| 5 | `dp_es` | mm | 0 | Average water depth at the emergency spillway. Sets the emergency volume. |
| 6 | `k` | mm/hr | 0.01 | Hydraulic conductivity of the wetland bottom. Sets the seepage rate. |
| 7 | `evap` | - | 0.7 | Evaporation coefficient, a multiplier on potential evapotranspiration for ponded water. |
| 8 | `vol_area_co` | - | 1 | Coefficient $a$ of the volume–area relation. |
| 9 | `vol_dp_a` | - | 1 | Coefficient $b$ of the volume–depth relation. |
| 10 | `vol_dp_b` | - | 1 | Coefficient $c$ of the volume–depth relation. |
| 11 | `hru_frac` | fraction | 0.5 | Fraction of the HRU that drains into the wetland. Read but not used. |

The built-in values apply to wetlands whose `hyd` name is not found. In rows of the file, the reader replaces zero or negative values in four columns:

- `evap` becomes 0.6.
- `k` becomes the saturated hydraulic conductivity of the top soil layer of the HRU whose number equals the row number of the record in `hydrology.wet` (HRU 1 for the first row, and so on), which is not in general an HRU that uses the record.
- `hru_ps` and `hru_es` are set to 0.08 × and 1.5 × values that are still zero when the file is read, so they stay at 0.

## Wetland behaviour

### Storage volumes and weir height

At the start of the run, and again when a decision table switches the wetland on, the storage limits are set from the HRU area $A_{hru}$ (ha) on the assumption that the whole HRU is ponded:

$$V_p = 10\,A_{hru}\,\mathrm{dp\_ps}, \qquad V_e = 10\,A_{hru}\,\mathrm{dp\_es}$$

in m³. `hru_ps` and `hru_es` do not enter the volumes.

If [`weir.res`](../input-reference/res.md#weirres) has at least one record, every wetland starts with the first record of [`weir.res`](../input-reference/res.md#weirres) as its weir: the weir height is that record's `height` (m), the principal volume becomes $V_p = 10^4\,A_{hru}\,\mathrm{height}$, and $V_e$ is raised to at least $1.2\,V_p$. Without weir records the weir height is `dp_ps` / 1000 m. A `weir` operation in the management schedule can later change the height and select another [`weir.res`](../input-reference/res.md#weirres) record by name (see [Management and decision tables](#management-and-decision-tables)).

The initial water volume is the `flo` fraction of the [`om_water.ini`](../input-reference/ini.md#om_waterini) row named in [`initial.res`](../input-reference/res.md#initialres), multiplied by $V_p$, with concentrations from the same row.

### Daily water balance

For an HRU with a wetland, the daily HRU routines change as follows:

- Surface run-on from upstream objects (with tile flow) is added to the wetland storage.
- The HRU generates no surface runoff. The day's precipitation, over the whole HRU area ($10\,R\,A_{hru}$ m³), and any irrigation water are added to the wetland storage.
- Evaporation from the ponded water is taken before soil evaporation; while water is ponded there is no soil evaporation (see [Evaporation](#evaporation)).
- Seepage from the ponded water is the infiltration into the soil.
- Water above saturation in the soil profile is returned to the wetland storage. If the weir height is below 1 mm it becomes surface runoff instead.
- The wetland outflow is the surface runoff of the HRU.

Water depth is storage divided by the HRU area: $d = V / (10\,A_{hru})$ mm.

### Surface area

For wetlands that are not paddies, the water surface area $A_w$ follows the storage $V$ relative to the principal volume $V_p$:

$$x = b^2 + 4c\left(1 - \frac{V}{V_p}\right), \qquad h = \frac{-b - \sqrt{x}}{2c} + b, \qquad A_w = A_{hru}\,\min\!\left(1, \max(0.01,\; 1 + a\,h)\right)$$

with $a$ = `vol_area_co`, $b$ = `vol_dp_a` and $c$ = `vol_dp_b`. When $x$ is below $10^{-6}$, $h$ is 0. With the built-in values ($a = b = c = 1$) the whole HRU is covered at $V = V_p$, and 63% at $V = 0.5\,V_p$. The area set up before the first day also multiplies the fraction by `hru_ps`.

For paddies the surface area is always the HRU area.

The surface area sets seepage and the weir flow. Precipitation, evaporation and the water depth are always calculated over the whole HRU.

### Evaporation

When the HRU has ponded water and its leaf area index is 4 or less, the maximum evaporation is

$$E_{max} = \mathrm{evap}\;\left(1 - \frac{LAI}{4}\right) PET$$

With a leaf area index above 4 there is no evaporation from the ponded water. Evaporation is taken from the ponded water first, and from the soil only when no ponded water remains.

In 62.0.1 the `evap` value is looked up through the record's row number in `hydrology.wet` used as an HRU number: the coefficient applied is that of the wetland on the HRU with that number, or 0.7 if that HRU has no wetland. In a model where HRU 1 uses the first `hydrology.wet` record, HRU 2 the second and so on, this gives the intended value.

### Seepage

Daily seepage is

$$S = \min\left(V,\; 240\,k\,A_w\right)$$

in m³, with $k$ in mm/hr. When the seepage is more than 0.1 mm over the HRU, it is reduced by the amount the soil profile cannot take before it becomes saturated. Nitrate, ammonium, soluble phosphorus, organic nitrogen and organic phosphorus move with the seepage into the top soil layer in proportion to the water. A puddling operation can replace `k` during the run. When gwflow is active, the exchange with groundwater is calculated by the groundwater model (see [gwflow](gwflow.md)).

### Outflow

A wetland whose `hyd` name in `wetland.wet` is `paddy` is a rice paddy. Its outflow is weir flow from the [`weir.res`](../input-reference/res.md#weirres) record selected for it, and `rel` is not used:

- If the storage exceeds $V_e$, the water above $V_e$ is released.
- While the water depth is above the weir height, flow over the weir is $Q = 0.45\,A\,c\,w\,H^{k}$ (m³/s), with the [weir.res](res.md#weirres) coefficients, the HRU area $A$ (ha) and the depth above the weir $H$ (m). It is applied hour by hour for up to 24 hours in a daily run, each hour limited to the water above the weir.
- With the weir height at zero the whole water depth acts as head, so the ponded water drains over the weir.

Other wetlands release through the decision table named in `rel`. The conditions and release options are those of reservoirs ([release rules](res.md#release-rules)), evaluated against the wetland's storage, principal and emergency volumes, water depth and weir height. The outflow is not smoothed.

Paddy HRUs also write a daily line to `paddy_test.csv` with precipitation, irrigation, seepage, evapotranspiration terms, weir height, water depth, weir outflow, soil water, sediment and nitrate.

### Sediment and nutrients

Sediment settling and nutrient losses in the ponded water follow the reservoir equations with the wetland's [`sediment.res`](../input-reference/res.md#sedimentres) and [`nutrients.res`](../input-reference/res.md#nutrientsres) records (see [sediment settling](res.md#sediment-settling) and [nutrient losses](res.md#nutrient-losses)), using the HRU's weather. When the wetland was empty at the start of the day and releases water, the sediment yield of the outflow is calculated with a MUSLE-type equation from the HRU's cover and erosion factors, as for a flushed field.

## Management and decision tables

These operations and decision-table entries act on wetlands and paddies:

- Decision table conditions `vol_wet` (storage against the principal or emergency volume), `wet_depth` (water depth, mm) and `weirh` (weir height, mm). See [decision tables](dtl.md).
- Decision table action `weir_height` with option `wet`: sets the weir height to `const` mm, sets $V_p$ to the HRU area times that height, and raises $V_e$ to at least $1.2\,V_p$. It does not change the weir record.
- Management operation `weir`: sets the weir height to its third data value (mm), sets $V_p$ the same way with $V_e$ raised to at least $1.1\,V_p$, and selects the [`weir.res`](../input-reference/res.md#weirres) record named in its first data field.
- Decision table actions `impound_off` and `impound_on`: `impound_off` removes the wetland and its stored water from the HRU. `impound_on` sets the wetland up again from the `surf_stor` row of [`hru-data.hru`](../input-reference/hru.md); the name given in the action's file pointer is not matched in 62.0.1.
- Puddling (`puddle` action, with [`puddle.ops`](ops.md)): replaces the wetland bottom conductivity and raises the sediment concentration of the ponded water.
- Fertilizer applied to an HRU with ponded water goes into the water when `carbon` in [`codes.bsn`](codes-bsn.md) is 2. With other `carbon` values it is counted in the fertilizer output but added to neither the water nor the soil.
- Tillage when the water depth is above 1 mm mixes the soil layers with the ponded-water routine, including pesticides in the soil.

See [management schedules](management.md) and [operations](ops.md) for the operation formats.

When gwflow is active and `gwflow.wetland` exists, the wetland bed thickness (m) for each wetland HRU is read from it: two header lines, then one line per wetland with a name and a thickness, where the digits in the name give the HRU number (for example `wet019` for HRU 19).

## Example

`refdata/Osu_1hru` in the SWAT+ repository is a single rice paddy HRU. [`hru-data.hru`](../input-reference/hru.md) names `paddy0001` in `surf_stor`.

`wetland.wet`:

```
wetland.       wet: written by SWAT+ edi############for SWAT+ rev.60.5.4
     id                name        init         hyd         rel         sed         nut        WEIR
       1          paddy0001    initwet1       paddy        weir     sedwet1     nutwet1       weir1
```

The title line is damaged but is skipped. The hydrology record is `paddy`, so the HRU is a paddy and the `weir` decision table named in `rel` is not used. The `WEIR` column is not read.

`hydrology.wet`:

```
hydrology.wet: written by SWAT+ editor v2.2.0 on 2023-03-22 04:25 for SWAT+ rev.60.5.4
name                    hru_ps         dp_ps        hru_es         dp_es             k          evap   vol_area_co      vol_dp_a      vol_dp_b      hru_frac
paddy			          1.00        150.00         1.00        150.00           0.5           0.75          1.00         1.00         1.00          1.0
```

The emergency volume is 150 mm of water over the HRU. Seepage is at most 0.5 × 24 = 12 mm per day. Ponded water evaporates at 0.75 × PET while the rice canopy is sparse, falling to zero as the leaf area index reaches 4.

[`weir.res`](../input-reference/res.md#weirres) has one record, `weir1`, with a height of 0 m, so the paddy starts with a weir height of zero and a principal volume of zero, and any ponded water drains over the weir. During the season `weir_height` actions in [`lum.dtl`](../input-reference/dtl.md) raise the weir to 60 mm and lower it to 0 again. While water stands above 60 mm it flows over the 5 m weir at $Q = 0.45\,A \times 1.83 \times 5 \times H^{1.5}$ m³/s.

## Related files

- [`hru-data.hru`](hru.md): assigns a `wetland.wet` row to an HRU through `surf_stor`.
- [`file.cio`](file-cio.md): names the wetland files.
- [`initial.res`, [`sediment.res`](../input-reference/res.md#sedimentres), [`nutrients.res`](../input-reference/res.md#nutrientsres) and `weir.res`](res.md): shared with reservoirs.
- [`res_rel.dtl` and `lum.dtl`](dtl.md): wetland release rules and wetland actions.
- [`management.sch`](management.md) and [operations](ops.md): weir, irrigation, puddling, fertilizer and tillage operations on paddies.
- [Salt](salt.md) and [constituent](cs.md) inputs for wetlands.
- [Water balance output](../output-reference/water-balance.md) and [reservoir and wetland theory](../model-theory/reservoirs-wetlands.md).

??? quote "Sources"

    - File names: `type input_res` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90); call order in [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - Readers: [`wet_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_read.f90), [`wet_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_read_hyd.f90)
    - Type definitions: `type reservoir_data_char_input` and `type wetland_hyd_data` in [`reservoir_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_data_module.f90); `type wetland` in [`reservoir_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/reservoir_module.f90)
    - Setup: [`hru_allo.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_allo.f90), [`wet_all_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_all_initial.f90), [`wet_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_initial.f90)
    - Daily routines: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90), [`et_act.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/et_act.f90), [`wetland_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wetland_control.f90), [`res_weir_release.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_weir_release.f90), [`res_hydro.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_hydro.f90), [`res_sediment.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_sediment.f90), [`res_nutrient.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_nutrient.f90), [`swr_satexcess.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swr_satexcess.f90)
    - Conditions, actions and operations: [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90), [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90), [`pl_fert_wet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_fert_wet.f90), [`mgt_newtillmix_wet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_newtillmix_wet.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | wetland.wet | `id` | read into a dummy `k` |
    | wetland.wet | `name`, `init`, `hyd`, `rel`, `sed`, `nut` | `wet_dat_c%name`, `%init`, `%hyd`, `%release`, `%sed`, `%nut` |
    | hydrology.wet | `hru_ps`, `dp_ps`, `hru_es`, `dp_es` | `wet_hyddb%psa`, `%pdep`, `%esa`, `%edep` |
    | hydrology.wet | `k`, `evap` | `wet_hyddb%k`, `%evrsv` |
    | hydrology.wet | `vol_area_co`, `vol_dp_a`, `vol_dp_b` | `wet_hyddb%acoef`, `%bcoef`, `%ccoef` |
    | hydrology.wet | `hru_frac` | `wet_hyddb%frac` |

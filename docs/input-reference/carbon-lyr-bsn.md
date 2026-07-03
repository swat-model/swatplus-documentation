---
title: carbon_lyr.bsn
description: Per-layer carbon coefficients. One row per layer group holding the seven Century rate constants and four CO2 allocation fractions used by cbn_zhang2.
status: new
verified_against:
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

## Purpose

`carbon_lyr.bsn` holds the carbon coefficients that differ between soil layer groups. It populates `carbdb(layer_id)` (rate constants for the litter, microbial, slow, and passive pools) and `org_allo(layer_id)` (the CO2 fractions produced by each pool transformation). The two layer groups currently in use are:

- `layer 1` (surface litter and topsoil)
- `layer 2` (all subsurface layers)

The reader indexes directly into the `carbdb(:)` and `org_allo(:)` arrays. Both are sized `dimension(2)` in `carbon_module.f90` today; a future expansion to additional layer groups requires only a larger array allocation, not a reader change.

## Source

- Reader: same routine as [`carbon.bsn`](carbon-bsn.md), [`src/carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_bsn_read.f90). The per-layer block is parsed in the second half of the subroutine.
- Target types: `carbon_inputs` (`carbdb`) and `organic_allocations` (`org_allo`) in [`src/carbon_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/carbon_module.f90).
- Filename: hardcoded in the reader as `carbon_lyr.bsn`. **Not listed in `file.cio`** — it rides at a fixed name beside `carbon.bsn`.

## Activation

Read only when `bsn_cc%cswat == 2` (the dynamic CENTURY/SWAT-C model; the activation value moved from 1 to 2). Like `carbon.bsn`, the file is **required**: an absent file, an unparseable row, or fewer data rows than the size of `carbdb` (currently 2) triggers `error stop` with a clear message.

## Format

- Line 1: title (skipped).
- Line 2: column header (skipped).
- Lines 3..: one row per layer group. Each row begins with an integer `layer` id (1 = top, 2 = subsurface) followed by 11 real coefficients. The reader loops until end-of-file. Rows with an out-of-range `layer` id (less than 1 or greater than `size(carbdb)`) are skipped with a warning to unit 9001 and do not count toward the required row count.

| # | Field | Type | Target | Units | Description |
|---|-------|------|--------|-------|-------------|
| 1 | `layer` | int | (array index) | none | layer group id; 1 = top (surface litter + topsoil), 2 = all subsurface layers |
| 2 | `hp_rate` | real | `carbdb(layer)%hp_rate` | 1/day | passive humus transformation rate under optimal conditions |
| 3 | `hs_rate` | real | `carbdb(layer)%hs_rate` | 1/day | slow humus transformation rate under optimal conditions |
| 4 | `microb_rate` | real | `carbdb(layer)%microb_rate` | 1/day | microbial biomass transformation rate under optimal conditions |
| 5 | `meta_rate` | real | `carbdb(layer)%meta_rate` | 1/day | metabolic litter transformation rate under optimal conditions |
| 6 | `str_rate` | real | `carbdb(layer)%str_rate` | 1/day | structural litter transformation rate under optimal conditions |
| 7 | `microb_top_rate` | real | `carbdb(layer)%microb_top_rate` | 1/day | top-layer microbial activity adjustment |
| 8 | `hs_hp` | real | `carbdb(layer)%hs_hp` | none | slow-to-passive humus allocation coefficient |
| 9 | `a1co2` | real | `org_allo(layer)%a1co2` | fraction | decomposed metabolic litter routed to CO2 |
| 10 | `asco2` | real | `org_allo(layer)%asco2` | fraction | decomposed slow humus routed to CO2 |
| 11 | `apco2` | real | `org_allo(layer)%apco2` | fraction | decomposed passive humus routed to CO2 |
| 12 | `abco2` | real | `org_allo(layer)%abco2` | fraction | decomposed microbial biomass routed to CO2 |

## Example

`refdata/Lafayette/carbon_lyr.bsn`:

```
carbon_lyr.bsn: layer-keyed carbon coefficients (one row per layer group; 1 = top, 2 = subsurface; extend with 3, 4, ... in future if needed)
   layer       hp_rate       hs_rate   microb_rate   meta_rate   str_rate   microb_top_rate   hs_hp   a1co2   asco2   apco2   abco2
       1      1.2e-05      2.92e-04        0.0164      0.0405     0.0107            0.0164    0.05    0.60    0.55    0.55    0.55
       2      1.2e-05      1.81e-04          0.02      0.0507     0.0134              0.02    0.05    0.55    0.55    0.55    0.55
```

## Calibration

All 11 per-layer fields are wired in `cal_parm_select.f90`. The calibration target is the `carbdb(ly)` or `org_allo(ly)` element selected by the `ly` index in the calibration record (see [Parameter change files](../calibration/parameter-change-files.md)):

- `hp_rate`, `hs_rate`, `microb_rate`, `meta_rate`, `str_rate`, `microb_top_rate`, `hs_hp` target `carbdb(ly)%*`.
- `a1co2`, `asco2`, `apco2`, `abco2` target `org_allo(ly)%*`.

Each `case` branch in `cal_parm_select.f90` guards `ly` to the range `[1, size(carbdb)]` (or `[1, size(org_allo)]`), so out-of-range layer indices in a calibration row are silently no-op rather than crashing.

## Related files

- [`carbon.bsn`](carbon-bsn.md). Basin-wide scalar carbon parameters.
- [`codes.bsn`](codes-bsn.md). The `cswat` switch.
- [Soil carbon (model theory)](../model-theory/carbon.md). Pool definitions and Century-style transformation equations.

---
title: codes.bsn
description: Basin-wide method switches. Selects which equations and modules SWAT+ uses.
status: review
verified_against:
  - src/basin_read_cc.f90
  - src/basin_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`codes.bsn` holds the method-selection switches that apply to the whole basin: the PET method, the routing method, the carbon model, the soil P model, and so on. It is read into `bsn_cc` (`type basin_control_codes`) early in the run and then consulted by every process module.

## Source

- Reader: [`src/basin_read_cc.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_read_cc.f90)
- Type definition: [`src/basin_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/basin_module.f90), `type basin_control_codes`

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Line 3: 26 fields, list-directed, read into `bsn_cc` in declaration order.

| # | Field | Type | Default | Description |
|---|-------|------|---------|-------------|
| 1 | petfile | char(16) | `pet.cli` | Potential ET filename. Used when `pet = 3` (read PET from file). |
| 2 | wwqfile | char(16) | `""` | Watershed stream water-quality filename. |
| 3 | pet | int | 0 | PET method. `0` Priestley-Taylor, `1` Penman-Monteith, `2` Hargreaves. (Method `3` triggers reading `pet.cli`.) |
| 4 | nam1 | int | 0 | Not used. |
| 5 | crk | int | 0 | Crack flow. `1` to compute flow in cracks. |
| 6 | swift_out | int | 0 | SWIFT output. `0` do not write, `1` write `swift_hru.inp`. |
| 7 | sed_det | int | 0 | Peak rate method. `0` NRCS dimensionless hydrograph with PRF, `1` half-hour rainfall intensity method. |
| 8 | rte | int | 0 | Water routing method. `0` variable storage, `1` Muskingum. |
| 9 | deg | int | 0 | Not used. |
| 10 | wq | int | 0 | Not used. |
| 11 | nostress | int | 0 | Plant stress. `0` all stresses applied, `1` turn off all plant stress, `2` turn off nutrient stress only. |
| 12 | cn | int | 0 | Not used. |
| 13 | cfac | int | 0 | Not used. |
| 14 | cswat | int | 0 | Carbon model. `0` static (legacy mineralization), `1` C-FARM (reserved, not implemented), `2` dynamic CENTURY/SWAT-C model. |
| 15 | lapse | int | 0 | Lapse-rate adjustment for precip and temperature. `0` no, `1` yes. |
| 16 | uhyd | int | 1 | Unit hydrograph. `0` triangular, `1` gamma function. |
| 17 | sed_ch | int | 0 | Not used. |
| 18 | tdrn | int | 0 | Tile drainage equation. `0` drawdown-days, `1` DRAINMOD. |
| 19 | wtdn | int | 0 | Shallow water-table depth. `0` original routine (fill to upper limit), `1` DRAINMOD water-table depth. |
| 20 | sol_p_model | int | 0 | Soil P model. `0` original SWAT P model, `1` Vadas and White (2010). |
| 21 | gampt | int | 0 | Infiltration method. `0` curve number, `1` Green-Ampt. |
| 22 | atmo | char(1) | `a` | Not used. |
| 23 | smax | int | 0 | Not used. |
| 24 | qual2e | int | 0 | Instream nutrient routing. `0` QUAL2E, `1` QUAL2E with simplified transformations. |
| 25 | gwflow | int | 0 | gwflow module. `0` inactive, `1` active. Triggers extra logic in [`object.cnt`](../input-reference/object-cnt.md). |
| 26 | idc_till | int | 3 | Tillage method when `cswat = 2`. `1` DSSAT, `2` EPIC, `3` Kemanian, `4` DNDC. |

The "Not used" fields are read from the file but the model does not consult them. Tools commonly write `0`.

## Side effects after read

If `pet = 3`, the reader opens `pet.cli` and reads a title and header line to position the file pointer. The actual PET values are read later by the climate routines.

## Example

`refdata/Ames_sub1/codes.bsn`:

```
codes.bsn:
        pet_file           wq_file       pet     event     crack  swift_out   sed_det   rte_cha   deg_cha    wq_cha  nostress        cn    c_fact    carbon     lapse      uhyd   sed_cha  tiledrain    wtable    soil_p     gampt      atmo_dep  stor_max   i_fpwet   gw_flow  idc_till
            null              null         2         0         0         0         0         0         0         0         0          2         0         1         0         1         0          0         0         0         0             0         0         0      0         3
```

The header column names written by SWAT+ Editor (`event`, `rte_cha`, `i_fpwet`, ...) differ from the field names in the source (`crk`, `rte`, `qual2e`, ...). Order is what the reader cares about. Mapping the example to the table:

- `pet = 2`: Hargreaves.
- `cswat = 2`: dynamic CENTURY/SWAT-C carbon model. (Header label `carbon`.) The example file above still carries `carbon = 1`, which is now the reserved C-FARM slot and runs no carbon model; datasets that want the dynamic model must set `carbon = 2`.
- `uhyd = 1`: gamma-function unit hydrograph.
- `idc_till = 3`: Kemanian tillage method.

The `null` strings in columns 1 and 2 disable the PET and water-quality file inputs.

## Related files

- [`parameters.bsn`](../input-reference/parameters-bsn.md). Numeric basin parameters consumed by the methods selected here.
- [`object.cnt`](../input-reference/object-cnt.md). Reads gwflow state when `gwflow = 1`.
- [`pet.cli`](../input-reference/cli.md). Used when `pet = 3`.

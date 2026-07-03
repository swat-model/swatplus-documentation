---
title: "fertilizer.frt"
description: Fertilizer product database. Mineral and organic N and P fractions, plus the NH3 share of mineral N, for each fertilizer product.
status: review
verified_against:
  - src/fert_parm_read.f90
  - src/manure_db_read.f90
  - src/manure_orgmin_read.f90
  - src/manure_parm_read.f90
  - src/fertilizer_data_module.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

## Purpose

`fertilizer.frt` lists every fertilizer product the simulation can apply, with its mass fractions of mineral nitrogen, mineral phosphorus, organic nitrogen, organic phosphorus, and the share of mineral N that is in the NH3 form. Each record fills one `fertilizer_db` entry in the `fertdb` array. Fertilizer operations (in `chem_app.ops` and the management decision tables) reference entries here by name.

## Source

- Reader: [`src/fert_parm_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/fert_parm_read.f90)
- Type definition: [`src/fertilizer_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/fertilizer_data_module.f90), `type fertilizer_db`

## Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one record per fertilizer product. List-directed read into `fertdb(it)` (`type fertilizer_db`).

| # | Field | Type | Units | Default | Description |
|---|-------|------|-------|---------|-------------|
| 1 | fertnm | char(16) | none | "" | fertilizer name (key referenced by `chem_app.ops` and management decision tables) |
| 2 | fminn | real | kg min-N / kg fertilizer | 0.0 | fraction of fertilizer that is mineral N (NO3 + NH3) |
| 3 | fminp | real | kg min-P / kg fertilizer | 0.0 | fraction of fertilizer that is mineral P |
| 4 | forgn | real | kg org-N / kg fertilizer | 0.0 | fraction of fertilizer that is organic N |
| 5 | forgp | real | kg org-P / kg fertilizer | 0.0 | fraction of fertilizer that is organic P |
| 6 | fnh3n | real | kg NH3-N / kg min-N | 0.0 | fraction of mineral N content that is NH3 |

The five real fractions must sum to less than or equal to 1 for a single product. `fminn + fminp + forgn + forgp` is the total nutrient mass per unit fertilizer; the remainder is carrier mass.

## Example

First lines of `refdata/Ames_sub1/fertilizer.frt`:

```
fertilizer.frt: written by SWAT+ editor v2.2.2 on 2023-10-17 14:43 for SWAT+ rev.60.5.4
name                     min_n         min_p         org_n         org_p         nh3_n         pathogens  description
elem_n                 1.00000       0.00000       0.00000       0.00000       0.00000              null  ElementalNitrogen
elem_p                 0.00000       1.00000       0.00000       0.00000       0.00000              null  ElementalPhosphorous
anh_nh3                0.82000       0.00000       0.00000       0.00000       1.00000              null  AnhydrousAmmonia
urea                   0.46000       0.00000       0.00000       0.00000       1.00000              null  Urea
46_00_00               0.46000       0.00000       0.00000       0.00000       0.00000              null  46_00_00
18_46_00               0.18000       0.20200       0.00000       0.00000       0.00000              null  18_46_00
dairy_fr               0.00700       0.00500       0.03100       0.00300       0.99000              null  Dairy_FreshManure
```

Notes on the example:

- The editor writes two trailing columns (`pathogens` and `description`) that are not in `fertilizer_db`. List-directed reads stop once the type is filled, so both trailing tokens are discarded by the reader. The literal `null` in the `pathogens` column has no effect.
- For `urea`, `fminn = 0.46` and `fnh3n = 1.00`. That is, 46% of the product is mineral N, and 100% of that mineral N is in the NH3 form.
- For `18_46_00`, `fminn = 0.18` and `fminp = 0.202`. Note that the third value in the "46" position is the P (P2O5 converted to P), not P2O5 directly.

## manure_db.frt

Named manure types. Each entry points to one organic-matter record in `manure_om.frt` and (optionally) to records for pesticides, pathogens, heavy metals, salts, and other constituents that may be carried with the manure. This is the lookup used by manure-application operations and by [`manure-allocation.md`](../input-reference/manure-allocation.md).

### Source

- Reader: [`src/manure_db_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/manure_db_read.f90)
- Type: [`src/fertilizer_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/fertilizer_data_module.f90), `type manure_database` (variable `manure_db`)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one record per manure type. Two passes: count rows, then read.

| # | Field | Type | Description |
|---|-------|------|-------------|
| 1 | name | char(25) | Manure-type name. Referenced by manure-application operations and by `manure_allo.mnu`. |
| 2 | org_min | char(25) | Crosswalk into `manure_om.frt`. Resolved into `iorg_min`. |
| 3 | pests | char(25) | Pesticide profile name. Pointer field `ipests` is reserved (the crosswalk loop is commented out in the reader). Use `null` when not applicable. |
| 4 | paths | char(25) | Pathogen profile name. Pointer `ipaths`. |
| 5 | hmets | char(25) | Heavy-metal profile name. Pointer `imets`. |
| 6 | salts | char(25) | Salt-ion profile name. Pointer `isalts`. |
| 7 | constit | char(25) | Other-constituent profile name. Pointer `iconstit`. |
| 8 | descrip | char(80) | Free-text description. |

After reading each row, the reader crosswalks `org_min` against `manure_om(:)%name` and stores the matching index in `manure_db(it)%iorg_min`. The other crosswalks are present in the type but not wired in this reader.

### Example

`refdata/Osu_1hru/manure_db.frt`:

```
manure_db.frt: manure database
name          org_min             pests  paths  hmets  salts  constit  description
beef_salt     mw_beef_liq         null   null   null   null   null     midwest_beef_liquid_salt
```

One manure type, pointing at `mw_beef_liq` in `manure_om.frt`. No pesticide, pathogen, heavy-metal, salt, or constituent profile.

## manure_om.frt

Organic-matter attributes for each manure type. Holds the water fraction and the C, mineral N, mineral P, organic N, organic P, and NH3 fractions used when a manure application is partitioned into the soil pools.

### Source

- Reader: [`src/manure_orgmin_read.f90`](https://github.com/swat-model/swatplus/blob/main/src/manure_orgmin_read.f90)
- Type: [`src/fertilizer_data_module.f90`](https://github.com/swat-model/swatplus/blob/main/src/fertilizer_data_module.f90), `type manure_attributes` (variable `manure_om`)

### Format

- Line 1: title (skipped).
- Line 2: header (skipped).
- Lines 3+: one record per manure organic-matter profile.

| # | Field | Type | Units | Description |
|---|-------|------|-------|-------------|
| 1 | name | char(64) | none | Profile name. Used as the crosswalk target from `manure_db.frt`. |
| 2 | frac_water | real | kg water / (kg manure + kg water) | Water fraction of the as-applied manure. |
| 3 | fcbn | real | kg C / kg manure | Carbon fraction. |
| 4 | fminn | real | kg min-N / kg manure | Mineral N fraction (NO3 + NH3). |
| 5 | fminp | real | kg min-P / kg manure | Mineral P fraction. |
| 6 | forgn | real | kg org-N / kg manure | Organic N fraction. |
| 7 | forgp | real | kg org-P / kg manure | Organic P fraction. |
| 8 | fnh3n | real | kg NH3-N / kg min-N | Share of mineral N that is NH3. |
| 9 | description | char(64) | none | Free-text description. |

### Example

`refdata/Osu_1hru/manure_om.frt`:

```
manure_om.frt: manure organic matter database
name            frac_water   fcbn          fminn         fminp         forgn         forgp         fnh3n  description
mw_beef_liq     0.988        0.000780576   0.000311751   0.00081295    0.002110312   0.000365707   0.99   midwest_beef_liquid
mw_beef_slur    0.926        0.016786571   0.002697842   0.00081295    0.002110312   0.000365707   0.99   midwest_beef_slurry
```

Two profiles. The liquid form is nearly all water (98.8%); the slurry form is 92.6% water with much higher solids and carbon.

## Related files

- `chem_app.ops`. Fertilizer applications in management schedules reference `fertnm` from `fertilizer.frt` or a manure name from `manure_db.frt`.
- [`manure-allocation.md`](../input-reference/manure-allocation.md). Allocates manure from named source objects to HRUs and other receivers.
- [`codes.bsn`](../input-reference/codes-bsn.md). The active carbon model (`cswat`) controls how N from fertilizer and manure enters the soil pools.

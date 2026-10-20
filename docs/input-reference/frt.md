---
title: "fertilizer.frt"
description: Fertilizer and manure databases. Nutrient fractions of each fertilizer product (fertilizer.frt), the manure types (manure_db.frt) and their organic matter make-up (manure_om.frt).
status: review
verified_against:
  - src/fert_parm_read.f90
  - src/manure_db_read.f90
  - src/manure_orgmin_read.f90
  - src/fertilizer_data_module.f90
  - src/proc_db.f90
  - src/read_mgtops.f90
  - src/mgt_sched.f90
  - src/actions.f90
  - src/pl_fert.f90
  - src/pl_manure.f90
  - src/cs_fert.f90
  - src/salt_fert.f90
  - src/carbon_module.f90
  - src/carbon_bsn_read.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

Fertilizer and manure applications use three databases.

- `fertilizer.frt` lists the fertilizer products: the fractions of mineral and organic nitrogen and phosphorus in each, and how much of the mineral nitrogen is ammonium. `fert` operations in [`management.sch`](management.md) and `fertilize` actions in [decision tables](dtl.md) name a row of this file.
- `manure_db.frt` lists the manure types. Each one points to a row of `manure_om.frt` and names optional pesticide, pathogen, metal, salt and constituent profiles. `manu` operations in [`management.sch`](../input-reference/management.md#managementsch), `manure` actions in decision tables and the [manure allocation](manure-allocation.md) file name a row of this file.
- `manure_om.frt` gives the water, carbon and nutrient make-up of each manure.

`fertilizer.frt` is named on the `hru_parm_db` line of [`file.cio`](file-cio.md) (default `fertilizer.frt`). The two manure files are not listed in [`file.cio`](../input-reference/file-cio.md). SWAT+ looks for them under the fixed names `manure_db.frt` and `manure_om.frt`, and leaves the manure databases empty when they are missing.

## fertilizer.frt

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one product with the values below in this order. The reader does not match columns by header name. It reads the first six values and ignores the rest of the line, so the `pathogens` and `description` columns written by the SWAT+ Editor have no effect.

| # | Column | Units | Default | Description |
|---|--------|-------|---------|-------------|
| 1 | `name` | - | - | Name of the fertilizer, up to 16 characters. Must be unique. |
| 2 | `min_n` | kg mineral N/kg fertilizer | 0.0 | Fraction of the fertilizer that is mineral nitrogen (nitrate plus ammonium). |
| 3 | `min_p` | kg mineral P/kg fertilizer | 0.0 | Fraction of the fertilizer that is mineral phosphorus. |
| 4 | `org_n` | kg organic N/kg fertilizer | 0.0 | Fraction of the fertilizer that is organic nitrogen. |
| 5 | `org_p` | kg organic P/kg fertilizer | 0.0 | Fraction of the fertilizer that is organic phosphorus. |
| 6 | `nh3_n` | kg NH3-N/kg mineral N | 0.0 | Fraction of the mineral nitrogen that is ammonium. The rest is nitrate. |

The fractions are by weight of the product. `min_n` + `min_p` + `org_n` + `org_p` is the nutrient content and should not exceed 1; the remainder is carrier.

For a commercial fertilizer the grade gives the nitrogen and phosphate content. The phosphate value in a grade is P2O5, so it has to be converted to P (multiply by 0.44) before it goes into `min_p`.

### Fertilizer application

A fertilizer operation applies an amount in kg/ha of product. The application method row in [`chem_app.ops`](ops.md) gives the fraction placed in the top 10 mm of soil (`surf_frac`); the rest goes into the second soil layer. In each of the two layers:

- `min_n` × (1 − `nh3_n`) of the amount is added as nitrate and `min_n` × `nh3_n` as ammonium.
- `min_p` of the amount is added as labile (soluble) phosphorus.
- With `carbon` = 0 in [`codes.bsn`](codes-bsn.md), half of the organic N and P goes to the fresh residue pool and half to the active humus pool.
- With `carbon` = 2, organic N and P are added to the soil organic matter pools with a carbon content of 10 times the organic N. The share that goes to the metabolic and structural litter pools depends on the C:N ratio. The split between the fresh and humus parts is `manure_c_frac` in [`carbon.bsn`](carbon-bsn.md).

### fertilizer.frt example

The first rows of `refdata/Ames_sub1/fertilizer.frt` in the SWAT+ repository:

```
fertilizer.frt: written by SWAT+ editor v2.2.2 on 2023-10-17 14:43 for SWAT+ rev.60.5.4
name                     min_n         min_p         org_n         org_p         nh3_n         pathogens  description
elem_n                 1.00000       0.00000       0.00000       0.00000       0.00000              null  ElementalNitrogen
elem_p                 0.00000       1.00000       0.00000       0.00000       0.00000              null  ElementalPhosphorous
anh_nh3                0.82000       0.00000       0.00000       0.00000       1.00000              null  AnhydrousAmmonia
urea                   0.46000       0.00000       0.00000       0.00000       1.00000              null  Urea
18_46_00               0.18000       0.20200       0.00000       0.00000       0.00000              null  18_46_00
dairy_fr               0.00700       0.00500       0.03100       0.00300       0.99000              null  Dairy_FreshManure
```

- `urea` is 46% mineral N, all of it applied as ammonium.
- `18_46_00` is an 18-46-0 grade: 18% N and 46% P2O5, which is 20.2% P.
- `dairy_fr` is fresh dairy manure, mostly organic N.
- `elem_n` has `nh3_n` = 0, so all its nitrogen is applied as nitrate.

## manure_db.frt

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one manure type with eight values.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Name of the manure type, up to 25 characters. Manure operations and the manure allocation file refer to it by this name. |
| 2 | `org_min` | Name of a row in `manure_om.frt` that gives the water, carbon and nutrient make-up. |
| 3 | `pests` | Name of a pesticide profile, or `null`. |
| 4 | `paths` | Name of a pathogen profile, or `null`. |
| 5 | `hmets` | Name of a heavy metal profile, or `null`. |
| 6 | `salts` | Name of a salt profile, or `null`. |
| 7 | `constit` | Name of a profile for other constituents, or `null`. |
| 8 | `description` | Free text, one word. |

In 62.0.1 the `pests`, `paths`, `hmets`, `salts` and `constit` names are read but not looked up. Salt and constituent loads in manure come from the fertilizer files of the [salt](salt.md) and [constituent](cs.md) modules, taken from the row in the same position as the manure type. They are added only when the manure type's `org_min` names the second or a later row of `manure_om.frt`.

A manure application takes its make-up from the row of `manure_om.frt` in the same position as the manure type in `manure_db.frt` (first with first, second with second). The `org_min` name is matched against `manure_om.frt` when the file is read, but the application does not use the match. Keep the two files in the same order, with `org_min` naming the row in the same position.

### manure_db.frt example

`refdata/Osu_1hru/manure_db.frt`:

```
manure_db.frt: manure database
name          org_min             pests  paths  hmets  salts  constit  description
beef_salt     mw_beef_liq         null   null   null   null   null     midwest_beef_liquid_salt
```

One manure type, `beef_salt`, using the `mw_beef_liq` make-up. `mw_beef_liq` is also the first row of `manure_om.frt` below, so the position used by the application and the `org_min` name agree. Because `org_min` names the first row, no salt or constituent loads are added when `beef_salt` is applied, whatever the salt and constituent fertilizer files contain.

## manure_om.frt

Free format, whitespace-separated. Line 1 is a title and line 2 is the column header; both are skipped. Each later line is one manure make-up with nine values.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Name of the make-up, up to 64 characters. |
| 2 | `frac_water` | kg water/kg manure as applied | Water fraction of the manure as applied. Must be below 1. |
| 3 | `fcbn` | kg C/kg dry manure | Carbon fraction. |
| 4 | `fminn` | kg mineral N/kg dry manure | Mineral nitrogen fraction (nitrate plus ammonium). |
| 5 | `fminp` | kg mineral P/kg dry manure | Mineral phosphorus fraction. |
| 6 | `forgn` | kg organic N/kg dry manure | Organic nitrogen fraction. |
| 7 | `forgp` | kg organic P/kg dry manure | Organic phosphorus fraction. |
| 8 | `fnh3n` | kg NH3-N/kg mineral N | Fraction of the mineral nitrogen that is ammonium. |
| 9 | `description` | - | Free text, one word. |

### Manure application

The amount in a manure operation is the dry mass of manure in kg/ha. The nutrient fractions apply to that dry mass. The water that comes with it, amount / (1 − `frac_water`) − amount, is added to the soil water of the two top layers. As for fertilizer, `surf_frac` of the application method in [`chem_app.ops`](../input-reference/ops.md#chem_appops) goes to the top 10 mm and the rest to the second layer.

Mineral N and P are added the same way as for fertilizer. With `carbon` = 0, the organic N and P are split between the fresh and humus pools with a fixed fraction of 0.5. With `carbon` = 2, carbon from `fcbn` and organic N and P go to the manure and litter pools, and the split uses `manure_c_frac` in [`carbon.bsn`](../input-reference/carbon-bsn.md).

### manure_om.frt example

`refdata/Osu_1hru/manure_om.frt`:

```
manure_om.frt: manure organic matter database
name            frac_water   fcbn          fminn         fminp         forgn         forgp         fnh3n  description
mw_beef_liq     0.988        0.000780576   0.000311751   0.00081295    0.002110312   0.000365707   0.99   midwest_beef_liquid
mw_beef_slur    0.926        0.016786571   0.002697842   0.00081295    0.002110312   0.000365707   0.99   midwest_beef_slurry
```

Two make-ups of Midwest beef manure. The liquid form is 98.8% water and the slurry 92.6%. Applying 1000 kg/ha of `mw_beef_liq` adds about 82,300 kg/ha of water, or 8.2 mm.

## Related files

- [`management.sch`](management.md): `fert` and `manu` operations.
- [Decision tables](dtl.md): `fertilize` and `manure` actions.
- [`chem_app.ops`](ops.md): application methods and the surface fraction.
- [`manure_allo.mnu`](manure-allocation.md): moves manure from sources to the land.
- [`codes.bsn`](codes-bsn.md): the `carbon` column selects how organic nutrients enter the soil.
- [`carbon.bsn`](carbon-bsn.md): `manure_c_frac` for the dynamic carbon model.

??? quote "Sources"

    - Readers: [`fert_parm_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/fert_parm_read.f90), [`manure_db_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_db_read.f90), [`manure_orgmin_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/manure_orgmin_read.f90), called from [`proc_db.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_db.f90)
    - Type definitions: `type fertilizer_db`, `type manure_database` and `type manure_attributes` in [`fertilizer_data_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/fertilizer_data_module.f90)
    - Name lookup: [`read_mgtops.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/read_mgtops.f90)
    - Operations: [`mgt_sched.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_sched.f90), [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90)
    - Application: [`pl_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_fert.f90), [`pl_manure.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/pl_manure.f90), [`cs_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/cs_fert.f90), [`salt_fert.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/salt_fert.f90)
    - Fresh and humus split: `man_coef%rtof` in [`carbon_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_module.f90), read from `carbon.bsn` in [`carbon_bsn_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_bsn_read.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | fertilizer.frt `name` | `fertdb%fertnm` |
    | fertilizer.frt `min_n`, `min_p` | `fertdb%fminn`, `fertdb%fminp` |
    | fertilizer.frt `org_n`, `org_p` | `fertdb%forgn`, `fertdb%forgp` |
    | fertilizer.frt `nh3_n` | `fertdb%fnh3n` |
    | manure_db.frt `org_min` | `manure_db%org_min`, index in `manure_db%iorg_min` |
    | manure_db.frt `description` | `manure_db%descrip` |
    | manure_om.frt columns | `manure_om%` with the same names |

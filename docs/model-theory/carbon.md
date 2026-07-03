---
title: Soil Carbon
description: Two selectable soil carbon paths in SWAT+ - static and the active Century-style module. Input files have moved to carbon.bsn and carbon_lyr.bsn.
status: updated
verified_against:
  - src/basin_read_cc.f90
  - src/carbon_bsn_read.f90
  - src/carbon_module.f90
  - src/cbn_zhang2.f90
verified_at_commit: 37458bea1c22d34b7e9d205489c995ff05862563
---

## Overview

SWAT+ exposes two soil carbon paths today. The choice is set by the integer `bsn_cc%cswat` in [`codes.bsn`](../input-reference/codes-bsn.md):

| `cswat` | Model | Pools |
|---------|-------|-------|
| 0 | Static (legacy) | Single residue + humus; C is not tracked as a state |
| 1 | C-FARM | Reserved for the C-FARM model; not implemented. Treated as off (no carbon model, no `carbon.bsn` required). |
| 2 | Active CENTURY/SWAT-C module | Three litter pools and three soil C pools (microbial, slow, passive) following Parton et al. (1993, 1994); driven by `cbn_zhang2.f90` |

The carbon model controls how plant residue, manure, tillage, and grazing inputs are routed into the soil and the subsequent CO2, N and P fluxes.

!!! note "Carbon activation value changed to 2"
    The dynamic carbon model now activates on `cswat = 2`, matching legacy SWAT numbering (1 = C-FARM, 2 = CENTURY). It was previously selected by `cswat = 1`. `carbon_bsn_read.f90` returns early for any value other than 2, so `cswat = 1` is now inert: no carbon model and no `carbon.bsn` required. This is an input-compatibility break: existing `codes.bsn` files (including refdata and the SWAT+ Editor default) left at `carbon = 1` will silently run with the carbon model off and must be changed to `carbon = 2`.

## Process equations

### Static (cswat = 0)

Mineralisation and immobilisation are computed in `nut_nminrl.f90`. There is no explicit soil C state. Plant residue carbon is implicit through the `0.42 * biomass` conversion. Residue decomposes at rate

```
decr = max(decr_min, min(1, rsdco_pl * ca * csf))
```

with 80% of mineralised N going to NO3 and 20% to active humus N. See [nutrient cycling](../model-theory/nutrient-cycling.md).

### Active carbon module (cswat = 2)

Selected when `bsn_cc%cswat = 2`. The active path runs the full Century pool transformation in `cbn_zhang2.f90`, fed by residue inputs, microbial decomposition, and tillage-driven mixing. Basin-wide and per-layer coefficients come from [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md); both files are **required** when `cswat = 2` and are read by `carbon_bsn_read.f90`. The tillage method is set by `bsn_cc%idc_till`:

| `idc_till` | Method |
|------------|--------|
| 1 | DSSAT-style |
| 2 | EPIC-style |
| 3 | Kemanian (default) |
| 4 | DNDC-style |

In `hru_control.f90`, when `cswat = 2`:

```
call cbn_surfrsd_decomp
call cbn_rsd_transfer
call cbn_zhang2
```

Surface residue decomposes in `cbn_surfrsd_decomp.f90` using the combined temperature-moisture factor `csf` from the N cycle. Below-ground residue is partitioned to soil pools through `cbn_rsd_transfer.f90`. The `cbn_zhang2.f90` routine then runs the Century-style multi-pool turnover that C-FARM and Century share.

The active path also adds the plant biomass increment as carbon (`hpc_d(j)%npp_c`) and accumulates respiratory CO2.

Tillage residue mixing uses `mgt_newtillmix_cswat1.f90` (vs `mgt_newtillmix_cswat0.f90` for the static model). Tillage activity decays over `till_eff_days` days (a column of [`carbon.bsn`](../input-reference/carbon-bsn.md)), controlled per layer by `soil(j)%ly(ly)%tillagef_tillmix`.

### Century pool structure (active path)

The Century scheme implemented in `cbn_zhang2.f90`. Pools:

- Litter: structural (`ls`), metabolic (`lm`), with the structural pool further split into lignin (`lsl`) and non-lignin
- Soil organic carbon: microbial biomass (`bm`), slow humus (`hs`), passive humus (`hp`)

For each pool, potential transformation under optimal conditions uses a first-order rate (the `*_para` rates in `carbon_module.f90`). Daily realised transformation is

```
rate(layer) = rate_optimal * cs
cs = sqrt(cdg * sut) * xbm * ox     (cs capped at 10)
```

`cdg` and `sut` are the temperature and water factors from the N cycle. `ox` is the oxygen factor

```
ox = 1 - OX_aa * depth / (depth + exp(OX_aa - OX_bb * depth))
```

with `OX_aa = 10.0`, `OX_bb = 0.035`. `xbm` is the texture and structure factor: 1 in the surface litter and `1 - 0.75 * (silt + clay)` elsewhere.

Default Parton optimal rates (per day):

| Pool | Surface | Subsurface |
|------|---------|------------|
| Microbial biomass (BMR) | 0.0164 | 0.02 |
| Slow humus (HSR) | - | 0.000548 |
| Passive humus (HPR) | - | 0.000012 |
| Metabolic litter (LMR) | 0.0405 | 0.0507 |
| Structural litter (LSR) | 0.0107 | 0.0132 |

CO2 allocations on transformation:

| From | To CO2 (surface) | To CO2 (subsurface) |
|------|------------------|----------------------|
| Biomass | 0.60 | 0.85 - 0.68 * (silt+clay) |
| Metabolic litter | 0.60 | 0.55 |
| Non-lignin structural | 0.60 | 0.55 |
| Lignin structural | 0.30 | 0.30 |
| Slow humus | 0.55 | 0.55 |
| Passive humus | 0.55 | 0.55 |

Biomass-to-passive humus allocation in subsurface layers: `0.003 + 0.032 * clay`. Slow-to-passive allocation: `max(0.001, PRMT_45 - 0.00009 * clay)` with `PRMT_45 = 0.003`.

Microbial-biomass leaching uses a water-balance form

```
abl = 1 - exp(-vflow / (0.01 * st + KOC * bd))
```

with `KOC = 4000` (organic carbon partition coefficient, `part_DOC_para`).

Lignin shape factor for structural litter: `xlslf = exp(-3 * lslf)` where `lslf` is lignin fraction of structural litter.

C:N ratios are kept within Parton bounds for each pool and the transformation can release or consume mineral N depending on the deficit (`cpn1..cpn5` and `sum1..sum5`).

The Parton defaults are overridden by the per-layer rates and CO2 fractions supplied in [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md); the residue and basin-wide tunables come from [`carbon.bsn`](../input-reference/carbon-bsn.md). The legacy `carb_coefs.cbn` and `basins_carbon.tes` files (and their readers `carbon_coef_read.f90` and `carbon_read.f90`) have been removed.

### DOC and DIC

The Century implementation accumulates dissolved organic carbon (DOC) and dissolved inorganic carbon (DIC) percolation. Defaults `peroc_DIC_para = 0.95`, `peroc_DOC_para = 0.70`, `hlife_doc_para = 50` days for DOC half-life in groundwater. Source: `carbon_module.f90`, `cbn_zhang2.f90`.

## Switches and parameters

| File | Field | Default | Effect |
|------|-------|---------|--------|
| [`codes.bsn`](../input-reference/codes-bsn.md) | `cswat` | 0 | 0 = static, 1 = C-FARM (reserved, inert), 2 = active CENTURY/SWAT-C module |
| [`codes.bsn`](../input-reference/codes-bsn.md) | `idc_till` | 3 | Tillage method when `cswat = 2` |
| [`carbon.bsn`](../input-reference/carbon-bsn.md) | 28 basin-wide scalars | see file | Required when `cswat = 2`; covers initial pool fractions, water coupling, manure partition, biomixing and tillage curves, temperature thresholds, residue C:N / C:P controls, and the slow-humus init method |
| [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) | per-layer rate constants and CO2 fractions | see file | Required when `cswat = 2`; one row per layer group |
| `carbon_layers.prt` | `cb_n_layers` | max HRU layers | Optional; fixes the number of layers in per-layer carbon output. If absent, defaults to the largest soil layer count across all HRUs |

Notable Century coefficients (from `carbon_module.f90`):

| Name | Default | Meaning |
|------|---------|---------|
| `CFB_para` | 0.42 | Carbon fraction of residue |
| `er_POC_para` | 1.5 | POC enrichment ratio |
| `peroc_DOC_para` | 0.70 | DOC percolation coefficient |
| `peroc_DIC_para` | 0.95 | DIC percolation coefficient |
| `part_DOC_para` | 4000 | DOC partition coefficient |
| `hlife_doc_para` | 50 days | DOC half-life in groundwater |
| `ALSLCO2_para` | 0.30 | Lignin-to-CO2 allocation |
| `APCO2_para` | 0.55 | Passive humus to CO2 |
| `ASCO2_para` | 0.55 | Slow humus to CO2 |
| `BMR_para_sur` / `BMR_para_sub` | 0.0164 / 0.02 | Microbial biomass turnover (d^-1) |
| `HPR_para` | 0.000012 | Passive humus turnover (d^-1) |
| `HSR_para` | 0.000548 | Slow humus turnover (d^-1) |
| `PRMT_45_para` | 0.003 | Slow-to-passive allocation coefficient |
| `PRMT_51_para` | 1.0 | Microbial activity coefficient for top layer |
| `OX_aa_para` | 10.0 | Oxygen factor coefficient |
| `OX_bb_para` | 0.035 | Oxygen factor coefficient |

## Implementation

Core: `cbn_zhang2.f90` (Century pool transformations), `cbn_surfrsd_decomp.f90` (surface residue), `cbn_rsd_decomp.f90` (sub-surface residue, used in legacy paths), `cbn_rsd_transfer.f90` (residue routing into Century pools).

Inputs: `carbon_module.f90` (data types and module-scope tunables), `carbon_bsn_read.f90` (reads both `carbon.bsn` and `carbon_lyr.bsn`), `carbon_layers_read.f90` (optional `carbon_layers.prt`).

Tillage: `mgt_newtillmix_cswat0.f90`, `mgt_newtillmix_cswat1.f90`, `mgt_newtillmix_wet.f90`, `mgt_tillfactor.f90`, `mgt_biomix.f90`.

Driver in `hru_control.f90` switches by `bsn_cc%cswat`. Outputs are written by `output_landscape_init.f90`, `hru_carbon_output.f90`, `lsu_carbon_output.f90`, and `soil_nutcarb_write.f90`. Output gating is per-family through the `hru_cb_*` and `lsu_cb_*` rows of [`print.prt`](../input-reference/print-prt.md); the old `cbn_diagnostics` flag has been retired.

## Related pages

- [`codes.bsn`](../input-reference/codes-bsn.md). The `cswat` switch.
- [`carbon.bsn`](../input-reference/carbon-bsn.md). Basin-wide carbon scalars.
- [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md). Per-layer carbon coefficients.
- [Carbon outputs](../output-reference/carbon.md). HRU and LSU file families.
- [Parameter change files](../calibration/parameter-change-files.md). 40 wired carbon calibration parameters.
- [Nutrient cycling](../model-theory/nutrient-cycling.md).
- [Plant growth](../model-theory/plant-growth-lum.md).

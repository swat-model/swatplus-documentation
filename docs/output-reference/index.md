---
title: Output reference
description: SWAT+ writes time-stepped outputs for every object class. Files follow a consistent naming scheme and are toggled in print.prt.
status: review
verified_against:
  - src/output_landscape_init.f90
  - src/header_aquifer.f90
  - src/header_channel.f90
  - src/header_sd_channel.f90
  - src/header_reservoir.f90
  - src/header_write.f90
  - src/proc_bsn.f90
  - src/proc_hru.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

SWAT+ writes one text file per (scope, group, interval) combination. Every output is toggled in `print.prt`. This section documents the file groups, their columns, and where they are written in the source.

## Naming convention

All time-step output files follow the pattern:

```
<scope>_<group>_<interval>.txt
```

When `csvout = y` in `print.prt`, a matching `.csv` variant is also written.

**Scopes** (the spatial aggregation level):

| Scope | Meaning |
|-------|---------|
| `hru_` | one row per Hydrologic Response Unit |
| `hru-lte_` | one row per low-resolution HRU (lite model) |
| `lsunit_` | one row per landscape unit (`ls_unit.def`) |
| `ru_` | one row per routing unit |
| `region_` | one row per region defined for regional output |
| `basin_` | one row, the basin-wide sum or average |
| `channel_` | one row per channel object (legacy `cha`) |
| `channel_sd` / `sd_chan` | one row per channel object (sd_channel routing) |
| `aquifer_` | one row per aquifer object |
| `reservoir_` | one row per reservoir object |
| `wetland_` | one row per wetland object |
| `recall_` | one row per recall object (point source or inlet) |
| `crop_yld_` | one row per HRU per harvested plant |

**Groups** (the variable family):

| Group | Meaning |
|-------|---------|
| `_wb` | water balance (precipitation, ET, runoff, percolation, storage) |
| `_nb` | nutrient balance (mineral and organic N and P pools) |
| `_ls` | losses from the landscape (sediment, nutrient yields) |
| `_pw` | plant and weather (LAI, biomass, yield, temperature, stress) |
| `_cha` | channel routing (legacy: flow, sediment, nutrients) |
| `_sd_cha` | sd_channel routing (water body storage, in, out) |
| `_aqu` | aquifer storage and fluxes |
| `_res` | reservoir storage and fluxes |
| `_pest` | pesticide |
| `_salt` | salt ions |
| `_cs` | constituents |
| `_carbon` | soil carbon pools |
| `_chanbud` | channel sediment budget |
| `_chamorph` | channel morphology |

**Intervals** (the time aggregation):

| Suffix | Meaning |
|--------|---------|
| `_day` | one row per simulated day |
| `_mon` | one row per month |
| `_yr` | one row per year |
| `_aa` | one row, average annual over the print window |

Each interval is enabled independently in `print.prt`. A row in `print.prt` named `hru_wb` with `y` in the `avann` column produces `hru_wb_aa.txt`; with `y` in the `daily` column it also produces `hru_wb_day.txt`. The file is opened in `output_landscape_init.f90` only if the matching switch is `y`.

## Per-group pages

- [Naming convention](../output-reference/naming-convention.md). The full grammar and the `print.prt` mapping.
- [Water balance](../output-reference/water-balance.md). The `*_wb_*.txt` columns: precipitation, ET, runoff, percolation, soil and snow storage.
- [Channel and sediment](../output-reference/channel-sediment-nutrient.md). The legacy `channel_*.txt` and the sd_channel `channel_sd_*.txt` columns, including sediment and nutrient routing.
- [Aquifer, reservoir, plant](../output-reference/aquifer-reservoir-plant.md). The `aquifer_*.txt`, `reservoir_*.txt`, `crop_yld_*.txt`, and plant/water-stress (`*_pw_*.txt`) columns.
- [Checker and diagnostics](../output-reference/checker-diagnostics.md). The always-on diagnostic files: `checker.out`, `diagnostics.out`, `simulation.out`, `files_out.out`.
- [gwflow](../output-reference/gwflow.md). 2D groundwater outputs: basin and per-cell water balance, heat, six solute species, observation wells, and pumping.
- [Post-processing helpers](../output-reference/post-processing.md). The two Python scripts shipped in `test/` for regression checks and CSV conversion.

## Output index file

When SWAT+ runs, it writes a master index `files_out.out` listing every output file actually opened during that run. The first column is a short tag (`HRU`, `BASIN`, `CHK`, `CHN`, `AQU`, `RES`, ...) and the second column is the filename. Open `files_out.out` first to see exactly which outputs your `print.prt` produced.

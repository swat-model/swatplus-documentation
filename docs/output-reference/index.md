---
title: Output reference
description: SWAT+ output files for revision 62.0.1. Which files exist, how print.prt switches them on, and where each group is described.
status: review
verified_against:
  - src/basin_print_codes_read.f90
  - src/output_path_module.f90
  - src/proc_open.f90
  - src/proc_bsn.f90
  - src/output_landscape_init.f90
  - src/header_write.f90
  - src/header_sd_channel.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ writes text files with results for each object type (HRU, landscape unit, channel, aquifer, reservoir and so on) and for the basin as a whole, by day, month, year and as an average over the simulation. Which files are written is set in [`print.prt`](../input-reference/print-prt.md): each row names a group of outputs and has a `y` or `n` for the daily, monthly, yearly and average annual files. A few files are written in every run.

The files go to the output folder named in [`file.cio`](../input-reference/file-cio.md), or to the run folder when none is named. Every run also writes `files_out.out`, a list of the output files it opened, which is the quickest way to see what a given [`print.prt`](../input-reference/print-prt.md) produced.

## Pages

| Page | Content |
|------|---------|
| [Naming convention](naming-convention.md) | How files are named and laid out, print timing, and the [`print.prt`](../input-reference/print-prt.md) row behind every file. |
| [Water balance](water-balance.md) | `hru_wb`, `hru-lte_wb`, `lsunit_wb` and `basin_wb`: precipitation, evapotranspiration, runoff, percolation, soil water and snow. |
| [Channel, sediment, nutrient](channel-sediment-nutrient.md) | `channel_sd`, `channel_sdmorph`, `sd_chanbud`, the sediment budget files `ch_sedbud`, `chanbud_order` and `sedbud`, their basin sums, and the legacy `channel` files. |
| [Hydrographs](hydrographs.md) | `hydout`, `hydin`, `deposition` and `ru`: water and loads passed between objects, and the `hydcon.out` connection list. |
| [Recall](recall.md) | `recall` and `basin_psc`: loads released by point sources, inlets and diversions. |
| [Nutrient balance and losses](nutrient-balance.md) | `hru_nb`, `hru_ls`, `lsunit_nb`, `lsunit_ls`, `basin_nb`, `basin_ls` and `hru-lte_ls`: nitrogen and phosphorus balances and the sediment and nutrient losses from the landscape. |
| [Aquifer, reservoir, plant](aquifer-reservoir-plant.md) | `aquifer`, `reservoir`, `wetland`, crop yields and the plant and weather (`_pw`) files. |
| [Carbon](carbon.md) | Soil, residue and plant carbon files. |
| [gwflow](gwflow.md) | Outputs of the gridded groundwater module. |
| [Checker and diagnostics](checker-diagnostics.md) | Files written in every run: `checker.out`, `diagnostics.out`, `files_out.out` and others. |
| [Post-processing](post-processing.md) | The Python scripts in the `test` folder of the SWAT+ source. |

## Recent changes

- 62.0.1 adds the channel sediment budget files `ch_sedbud_*` (each channel), `chanbud_order_*` (each stream order) and `sedbud_*` (basin), all switched on by the `channel_sd` row.
- 62.0.0 added the carbon rows of [`print.prt`](../input-reference/print-prt.md) (`hru_cb_gl`, `hru_cb_trf`, `lsu_cb_gl` and others) for the carbon output families; see [Carbon](carbon.md).

??? quote "Sources"

    - `print.prt` reader: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90)
    - Output folder: [`output_path_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_path_module.f90)
    - File opening: [`proc_open.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_open.f90), [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90), [`header_write.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_write.f90), [`header_sd_channel.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_sd_channel.f90)
    - `files_out.out`: [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90)

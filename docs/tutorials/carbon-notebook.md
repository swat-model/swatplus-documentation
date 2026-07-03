---
title: Carbon notebook
description: The Jupyter notebook that plots SWAT+ soil-carbon outputs. What it reads, what it draws, how to run it.
status: review
---

The SWAT+ source tree ships one analysis notebook: [`jupyter_notebooks/carbon.ipynb`](https://github.com/swat-model/swatplus/blob/main/jupyter_notebooks/carbon.ipynb). It reads the carbon-output files for a single HRU and draws time-series plots of every carbon pool the C-FARM / Century model tracks. Use it after running a project with the carbon model enabled.

## What it reads

The notebook reads the following files from a SWAT+ output folder:

- `hru-data.hru` and `landuse.lum`. Used to look up the soil name, the `lu_mgt` name, and the management identifier for a chosen HRU.
- `mgt_out.txt`. Operation log: planting, harvest, tillage, fertilization. The notebook overlays these as event markers on every plot.
- `hru_cbn_lyr.txt`. Total soil carbon per soil layer.
- `hru_seq_lyr.txt`. Sequestered carbon per soil layer.
- `hru_rsdc_stat.txt`. Surface residue and soil carbon pools.
- `hru_plc_stat.txt`. Plant carbon pools.
- `hru_cpool_stat.txt`. Residue and soil carbon pools by layer (metabolic, structural, lignin, microbial, slow humus, passive humus).
- `hru_org_trans_vars.txt`. Organic-matter transformation variables.
- `hru_cflux_stat.txt`. Carbon flux statistics including CO2.

The notebook expects these to be produced by a run where `print.prt` lists each of those output rows with at least one frequency turned on. Daily output is what the notebook is designed for.

## What it draws

The notebook is organised by output file. Each section opens with an "Initialize" cell that loads the file into a DataFrame, then one or more graph cells produce a Plotly figure. Sections, in order:

1. Total carbon by layer depth (`hru_cbn_lyr`).
2. Total sequestered carbon and 300 mm sequestered (`hru_seq_lyr`).
3. Surface residue and soil carbon pools at 10 mm depth (`hru_rsdc_stat`).
4. Soil carbon pools at a user-specified depth.
5. Live root mass by soil layer.
6. Plant stats from `hru_plc_stat`.
7. Residue and soil carbon pools (`hru_cpool_stat`) at 10 mm.
8. Same pools at a user-specified depth.
9. Soil residue, metabolic, structural, lignin, microbial, slow humus, and passive humus pools by soil layer.
10. Soil water content by soil layer.
11. Organic-matter transformation variables (`hru_org_trans_vars`).
12. Carbon fluxes (`hru_cflux_stat`), non-CO2 and CO2.

Every plot shows the chosen variable as a time series. PLANT, HARVEST, and TILLAGE events from `mgt_out.txt` are overlaid as vertical markers so you can read the management context off the figure.

## How to run it

1. Run SWAT+ on a project with the carbon model on. In `codes.bsn`, set `carbon = 2` to activate the dynamic CENTURY/SWAT-C model (`carbon = 1` is the reserved C-FARM slot and runs no carbon model). The `Ames_sub1` reference dataset ships `carbon = 1`, so change it to `carbon = 2`.
2. Turn on the relevant outputs in `print.prt`. At minimum, `hru_cb` and the carbon-pool outputs need `daily` set to `y`.
3. Open `carbon.ipynb` in JupyterLab or VS Code.
4. Edit the first code cell. Set:
   - `hru_id` to the HRU you want to plot.
   - `wdir` and `sdir` so that `f"{wdir}/{sdir}"` is the folder that holds the SWAT+ outputs.
5. Run all cells (Run All).

The notebook uses `pandas`, `plotly`, and the standard library. Install with:

```bash
pip install pandas plotly
```

## What you should see

Each graph cell renders a Plotly figure inline. Event markers from `mgt_out.txt` line up the plots with the management schedule. The "Initialize" cells print "File not found" and stop rendering that section if the corresponding output file is missing; this is expected when an output is not enabled in `print.prt`.

## Related

- [Theory: Carbon](../model-theory/carbon.md) covers what the pools and fluxes represent.
- [print.prt](../input-reference/print-prt.md) for the output switches.
- [Cookbook: enabling the carbon model](../tutorials/cookbook.md) for the input edits.

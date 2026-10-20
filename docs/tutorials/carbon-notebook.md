---
title: Carbon notebook
description: The Jupyter notebook in the SWAT+ source repository that plots the legacy soil carbon output of one HRU. The files it reads, the switches it needs, and how to run it with Ames_sub1.
status: review
verified_against:
  - swatplus/jupyter_notebooks/carbon.ipynb
  - swatplus/refdata/Ames_sub1
  - src/command.f90
  - src/soil_nutcarb_write_legacy.f90
  - src/soil_carbvar_write_legacy.f90
  - src/carbon_legacy_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

The SWAT+ source repository has one analysis notebook, [`jupyter_notebooks/carbon.ipynb`](https://github.com/swat-model/swatplus/blob/62.0.1/jupyter_notebooks/carbon.ipynb). It reads the carbon output of one HRU and draws time series of soil carbon, the carbon pools by soil layer, plant carbon and the carbon fluxes, with the HRU's management operations marked on each graph. It uses the legacy CSU carbon files, which have no interval suffix in their names (see [legacy CSU carbon outputs](../output-reference/carbon.md#legacy-csu-carbon-outputs)). The newer carbon files, such as `hru_cbn_lyr_day.txt`, are not read by the notebook.

## Files read

The notebook reads these files from one folder:

| File | Use |
|------|-----|
| [`hru-data.hru`](../input-reference/hru.md), [`landuse.lum`](../input-reference/lum.md) | Soil, land use and schedule names of the chosen HRU. |
| `mgt_out.txt` | Management operations of the HRU, drawn as markers. |
| `hru_cbn_lyr.txt` | Total soil carbon by layer. |
| `hru_seq_lyr.txt` | Sequestered soil carbon, total and in the top 300 mm. |
| `hru_plc_stat.txt` | Plant carbon: above ground, leaf, stem, seed, root and surface residue. |
| `hru_cpool_stat.txt` | Residue, metabolic, structural, lignin, microbial, slow humus and passive humus carbon, root mass and soil water, by layer. |
| `hru_org_trans_vars.txt` | Potential transformation rates (`bmctp`, `hsctp`, `hsntp`, `hpctp`, `lslctp`, `lslnctp`) by layer. |
| `hru_cflux_stat.txt` | Carbon flows between pools and CO2 losses by layer. |

The input files and the output files must be in the same folder, which is the case unless [`file.cio`](../input-reference/file-cio.md) sets an [output folder](../input-reference/file-cio.md#output-folder).

## Switches

The legacy files are written only with these settings:

- `carbon` = 2 in [`codes.bsn`](../input-reference/codes-bsn.md), with [`carbon.bsn`](../input-reference/carbon-bsn.md) and [`carbon_lyr.bsn`](../input-reference/carbon-lyr-bsn.md) present (see [carbon model](../input-reference/codes-bsn.md#carbon-model)). `hru_plc_stat.txt`, `hru_cpool_stat.txt`, `hru_cflux_stat.txt` and `hru_org_trans_vars.txt` are written only with `carbon` = 2.
- `use_obj_lbls` = `y` in [`print.prt`](../input-reference/print-prt.md), because the carbon rows are recognised only by name.
- A `hru_cb` row with `y` or `l` in the daily column, for the first five files in the table. `l` adds layer properties at the start and end of the run.
- A `hru_cb_vars` row with `y` or `l` in the daily column, for `hru_org_trans_vars.txt`.
- `mgtout` = `y` in [`print.prt`](../input-reference/print-prt.md), for `mgt_out.txt`.

The notebook uses the shortest interval in each file, and it is designed for daily output.

## Ames_sub1 setup

The [Ames_sub1](ames-sub1.md) reference dataset at 62.0.1 already has all of these settings:

```text
csvout        use_obj_lbls  cdfout
n             y             n
crop_yld      mgtout        hydcon        fdcout
b             y             n             n
objects                  daily       monthly        yearly         avann
...
hru_cb                       l             y             y             y
hru_cb_vars                  l             y             y             y
```

The full run of 46 years writes about 9 GB, most of it daily carbon output. For the notebook, shorten the run first: with [`time.sim`](../input-reference/time-sim.md) set to 1975 to 1976, the run takes a few seconds and the output folder is about 380 MB.

## Running the notebook

1. Copy `refdata/Ames_sub1` to a new folder, shorten [`time.sim`](../input-reference/time-sim.md), and run SWAT+ in the copy (see [Running the model](ames-sub1.md#running-the-model)).
2. Install the Python packages. The notebook uses `pandas` and `plotly`, and plotly needs `nbformat` to show figures in Jupyter:

    ```bash
    pip install jupyterlab pandas plotly nbformat
    ```

3. Open `carbon.ipynb` in JupyterLab or VS Code.
4. In the first code cell, under `# hru to run against.`, set:
    - `hru_id`: the HRU number to plot (1 by default).
    - `wdir` and `sdir`: the notebook reads from the folder `f"{wdir}/{sdir}"`. The values in the shipped notebook are the author's folders and must be changed, for example `wdir = "/home/me/runs"` and `sdir = "Ames_sub1"`.
    - `output_html_file`: `True` also saves every figure as an HTML file.
5. Run all cells.

The cell that reads a file does nothing when the file is missing, and the graph cells after it then work with the table of the previous file, or stop with an error if there is none. Turn on every switch listed above before running the notebook.

## Graphs

Each section of the notebook has a cell that reads one file and one or more cells that draw Plotly figures from it. With daily output for HRU 1 of Ames_sub1, the notebook draws, in order:

1. Total soil carbon by layer (`hru_cbn_lyr.txt`), in Mg/ha per mm of layer thickness.
2. Sequestered carbon in the top 300 mm (`hru_seq_lyr.txt`), in Mg/ha.
3. Plant carbon components (`hru_plc_stat.txt`), in kg/ha.
4. Residue and soil carbon pools in the 10 mm top layer, and in the layer at a depth set in the cell (100 mm by default) (`hru_cpool_stat.txt`).
5. One graph by layer for each pool in `hru_cpool_stat.txt`: residue, metabolic, structural, lignin, microbial, slow humus, passive humus, live root mass and soil water content.
6. One graph by layer for each potential transformation rate in `hru_org_trans_vars.txt`.
7. One graph by layer for each carbon flow between pools (`cfmets1` to `cfs3s1`) and each CO2 loss (`co2fmet` to `co2fs3`) in `hru_cflux_stat.txt`.

Several graph cells have a `normalize` setting that divides each layer's value by the layer thickness, and a `show_mgt` setting that turns the management markers on or off. The markers are coloured by operation type: planting, harvest, tillage, fertilizer, manure, irrigation, pesticide and grazing.

## Related pages

- [Carbon outputs](../output-reference/carbon.md): the newer carbon files and the legacy files with their columns.
- [carbon.bsn](../input-reference/carbon-bsn.md): carbon model parameters and initial pools.
- [Soil carbon theory](../model-theory/carbon.md): what the pools and flows represent.
- [Cookbook: carbon model](cookbook.md#carbon-model): switching the carbon model on in another project.

??? quote "Sources"

    - Notebook: [`jupyter_notebooks/carbon.ipynb`](https://github.com/swat-model/swatplus/blob/62.0.1/jupyter_notebooks/carbon.ipynb) at 62.0.1. The file names, the folder variables `wdir` and `sdir`, the `read_data` and `read_mgt_out` functions and the graph cells are in its code cells.
    - Test: a copy of `refdata/Ames_sub1` with `time.sim` set to 1975 to 1976, run with a 62.0.1 Linux build (Intel compiler) made from commit 97ca231, which differs from the tag only in gwflow, calibration and export coefficient code. The run took about 10 seconds and wrote 379 MB. All code cells of the notebook were then run outside Jupyter with pandas 3.0.1 and plotly 6.6.0, with `wdir` pointed at the copy; every cell completed and 33 figures were drawn, with 731 daily values (1975 and 1976) in each data trace.
    - Legacy file switches: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90) calls [`soil_nutcarb_write_legacy.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_nutcarb_write_legacy.f90) for `pco%cb_hru` and [`soil_carbvar_write_legacy.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/soil_carbvar_write_legacy.f90) for `pco%cb_vars_hru` (only with `bsn_cc%cswat` = 2). The files are opened in [`carbon_legacy_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/carbon_legacy_module.f90). The `freq` column takes the values `day`, `mon` and `year`, which the notebook's reading cells filter on.
    - Missing files: each reading cell tests `file_path.is_file()` and otherwise only sets `df_plot` to an empty table; the graph cells test `df.empty`, where `df` is the table from the last reading cell that found its file.

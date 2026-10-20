---
title: Tutorials and Examples
description: Walkthroughs of the two reference datasets in the SWAT+ source repository, the carbon notebook, and a set of common edits.
status: review
verified_against:
  - swatplus/refdata/Ames_sub1
  - swatplus/refdata/Osu_1hru
  - swatplus/jupyter_notebooks/carbon.ipynb
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

These pages use the two small datasets in the `refdata` folder of the SWAT+ source repository and go through them file by file. They assume SWAT+ is installed and the [Getting started](../getting-started/index.md) pages have been read.

## Pages

- [Ames_sub1 walkthrough](ames-sub1.md). Twelve HRUs near Ames, Iowa, simulated from 1975 to 2020, with no routing between objects. Each input group in turn, the run, and the outputs.
- [Osu_1hru walkthrough](osu-1hru.md). One rice paddy HRU in South Korea, simulated from 2010 to 2023, with a routing unit, an aquifer and a channel. Paddy management by decision tables, and the shipped files that 62.0.1 reads differently from their headers.
- [Carbon notebook](carbon-notebook.md). The Jupyter notebook `jupyter_notebooks/carbon.ipynb`, which plots the soil carbon output of one HRU, and how to run it with Ames_sub1.
- [Cookbook recipes](cookbook.md). Short edits: change the simulation period, turn on an output, change the PET method, switch to Green-Ampt, add an HRU, switch on the carbon model.

??? quote "Sources"

    - Datasets: [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Ames_sub1) and [`refdata/Osu_1hru`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Osu_1hru) at 62.0.1.
    - Notebook: [`jupyter_notebooks/carbon.ipynb`](https://github.com/swat-model/swatplus/blob/62.0.1/jupyter_notebooks/carbon.ipynb) at 62.0.1.

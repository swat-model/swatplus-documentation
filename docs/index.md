---
title: Home
description: Documentation for the Soil and Water Assessment Tool Plus (SWAT+), an open-source watershed model.
status: review
hide:
  - navigation
  - toc
---

# SWAT+ Documentation

An open-source watershed model with plain-text inputs and outputs.

[Get started :material-arrow-right:](getting-started/index.md){ .md-button .md-button--primary }
[What is SWAT+](introduction/what-is-swatplus.md){ .md-button }

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } &nbsp; **[Getting started](getting-started/index.md)**

    ---

    Install SWAT+, run the reference dataset, and learn the shape of a project folder.

-   :material-function:{ .lg .middle } &nbsp; **[Model theory](model-theory/index.md)**

    ---

    Hydrology, soil, plants, channels, aquifers, reservoirs, nutrients, carbon, pesticides, salts.

-   :material-file-document-edit:{ .lg .middle } &nbsp; **[Input reference](input-reference/index.md)**

    ---

    Every input file, with its columns, units and defaults.

-   :material-file-chart:{ .lg .middle } &nbsp; **[Output reference](output-reference/index.md)**

    ---

    Every output file group, with column lists and aggregation rules.

-   :material-hammer-wrench:{ .lg .middle } &nbsp; **[Developer guide](developer-guide/index.md)**

    ---

    Build from source, test, tag releases, contribute.

-   :material-tune:{ .lg .middle } &nbsp; **[Calibration](calibration/index.md)**

    ---

    Soft and hard calibration workflows.

-   :material-school:{ .lg .middle } &nbsp; **[Tutorials](tutorials/index.md)**

    ---

    Walkthroughs of the Ames_sub1 and Osu_1hru reference datasets.

-   :material-help-circle:{ .lg .middle } &nbsp; **[FAQ](faq-troubleshooting/index.md)**

    ---

    Common runtime errors, water-balance issues, performance tips.

</div>

## About this site

This documentation describes SWAT+ revision 62.0.1. Each SWAT+ release has a separate version of the site, chosen with the version selector at the top of the page; `latest` is the newest.

The pages are written for model users. Every statement about model behaviour has been checked against the Fortran source of the release, and the commit is recorded in each page's front matter. Where the source does something unexpected, the page says what the model does. Source files and variable names are listed in a collapsed Sources block at the end of each page.

The model source is at [github.com/swat-model/swatplus](https://github.com/swat-model/swatplus). Every page can be downloaded as a PDF, alone or with its section ([Download as PDF](downloads.md)).

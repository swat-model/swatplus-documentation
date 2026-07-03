---
title: What is SWAT+
status: review
verified_against:
  - swatplus/README.md
  - swatplus/CITATION.cff
  - swatplus/src/input_file_module.f90
  - swatplus/refdata/Ames_sub1
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

The Soil and Water Assessment Tool Plus (SWAT+) is a public-domain watershed model. It is jointly developed by the USDA Agricultural Research Service ([USDA-ARS](https://ars.usda.gov)) and Texas A&M AgriLife Research, with contributions from Colorado State University, the USDA-ARS Hydrology and Remote Sensing Laboratory, and other institutions.

SWAT+ simulates the quantity and quality of surface water and groundwater at scales from small watersheds to large river basins. It is used to evaluate the effects of land use, land management practices, soil, climate, and climate change on water resources.

## What it computes

For each hydrologic response unit (HRU), routing reach, aquifer, reservoir, and wetland in a watershed, SWAT+ computes a daily mass balance for:

- water (precipitation, evapotranspiration, surface runoff, lateral flow, percolation, return flow, channel routing)
- sediment (detachment, transport, deposition)
- nutrients (nitrogen and phosphorus cycling in soil, plant uptake, transport in surface and subsurface flow, in-stream transformations)
- carbon (soil organic carbon pools)
- pesticides (application, decay, transport)
- salts and other constituents
- plant growth (biomass, yield, water and nutrient stress)

Output is reported daily, monthly, yearly, or as an annual average.

## What it is used for

Typical applications:

- assessing the effect of management practices on water yield and water quality
- evaluating soil erosion and non-point source pollution
- estimating crop yield response to climate and management
- supporting watershed planning and total maximum daily load (TMDL) studies
- climate change impact studies on water resources

## How it is run

SWAT+ is a Fortran command-line executable. It reads a folder of plain-text input files that describe the watershed, climate, soil, land use, management, and simulation period. It writes output as plain-text files in the same folder.

Most users do not write the input files by hand. They build a project with one of the supporting tools:

- **QSWAT+** is a QGIS plugin that delineates the watershed from a DEM, creates HRUs, and writes the input files.
- **SWAT+ Editor** is a desktop application for inspecting and editing input parameters in an existing project.

After the tools write the project folder, the SWAT+ executable is run from that folder.

## Source and license

The source code is hosted at https://github.com/swat-model/swatplus and released under LGPL-2.1.

---
title: Model Theory
description: Overview of SWAT+ process clusters and where each is documented.
status: review
---

## Overview

This section describes how SWAT+ represents the physical and management processes that move water, sediment, nutrients, and other constituents through a watershed. Each page focuses on one process cluster, lists the governing relationships, the basin codes and parameters that switch behaviour, and the source modules in `swatplus/src/` that implement it.

The clusters group together because they share state, run in the same daily order, or are configured through the same input files. The water balance cluster (HRU hydrology, soils, climate, erosion) feeds the routing cluster (channels, aquifers, reservoirs and wetlands, recall objects). The biogeochemistry cluster (plant growth, nutrient cycling, carbon, pesticides, salts and constituents) sits inside the HRU. Decision tables drive management and release rules across all clusters.

## Pages in this section

| Cluster | Page | What it covers |
|---------|------|----------------|
| Water balance | [Overview and water balance](overview-water-balance.md) | Daily HRU water balance, object flow chart, sequencing |
| Water balance | [Climate and weather](climate-weather.md) | Measured, simulated, and lapsed weather; PET methods |
| Water balance | [Hydrology](hydrology.md) | Runoff (CN, Green-Ampt), lateral flow, percolation, channel routing |
| Water balance | [Soil water and temperature](soil-water-temperature.md) | Soil profile water, soil temperature, frozen soil |
| Water balance | [Erosion and sediment](erosion-sediment.md) | MUSLE on land, channel erosion and deposition |
| Routing | [Channels](channels.md) | Channel routing methods, sediment transport, in-stream water quality |
| Routing | [Aquifers](aquifers.md) | 1D recession aquifer and 2D `gwflow` cell-based groundwater |
| Routing | [Reservoirs and wetlands](reservoirs-wetlands.md) | Reservoir water balance, release rules, sediment and nutrient processes; HRU wetlands |
| Routing | [Recall and point sources](recall-point-sources.md) | Recall time series, export coefficients, delivery ratios |
| Routing | [Decision tables](decision-tables.md) | Runtime condition evaluation and action firing |
| Biogeochemistry | [Plant growth and land use management](plant-growth-lum.md) | Heat units, biomass, yield, scheduled management |
| Biogeochemistry | [Nutrient cycling](nutrient-cycling.md) | Soil N and P pools, transformations, transport |
| Biogeochemistry | [Carbon](carbon.md) | Static, CFARM, and Century carbon models |
| Biogeochemistry | [Pesticides](pesticides.md) | Application, partitioning, decay, transport |
| Biogeochemistry | [Salts and constituents](salts-constituents.md) | Salt ion chemistry and generic constituents |

## How to read these pages

Each page follows the same shape. The Overview names the process and the role it plays in the simulation. Process equations give the governing relationships in plain math. Switches and parameters lists the `codes.bsn` and `parameters.bsn` entries that change the result, with defaults from the source. Implementation lists the source files in `swatplus/src/` that perform the calculation. Related pages cross-link to the input and output references.

The Fortran source at `swatplus/src/` is the source of truth. Where this section conflicts with the source, the source wins. Anything still uncertain is marked `TODO: verify`.

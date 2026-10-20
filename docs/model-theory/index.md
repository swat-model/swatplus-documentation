---
title: Model Theory
description: How SWAT+ represents the physical and management processes in a watershed, grouped by process.
status: review
verified_against:
  - src/hru_control.f90
  - src/command.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

These pages describe how SWAT+ represents the processes that move water, sediment, nutrients and other constituents through a watershed. Each page covers one group of processes: the equations the model solves, the input files and columns that control them, and where SWAT+ 62.0.1 differs from the SWAT 2009 theoretical documentation.

The landscape processes run once per day for every hydrologic response unit (HRU): weather, snow, evapotranspiration, surface runoff, soil water, erosion, plant growth and the soil nutrient cycles. Their results leave the HRU as surface runoff, lateral flow, tile flow and percolation, and pass to the routing objects: channels, aquifers, reservoirs and wetlands, and recall points. Decision tables apply management and reservoir release rules across both groups.

## Pages

| Group | Page | Contents |
|-------|------|----------|
| Landscape water | [Overview and water balance](overview-water-balance.md) | HRU water balance, the order of daily calculations, where each term is reported |
| Landscape water | [Climate and weather](climate-weather.md) | Measured and generated weather, day length, sub-daily precipitation, elevation lapse, potential evapotranspiration |
| Landscape water | [Hydrology](hydrology.md) | Canopy interception, surface runoff, lateral flow, percolation, tile flow, lag to the channel |
| Landscape water | [Soil water and temperature](soil-water-temperature.md) | Soil layers, water retention, initial soil water, soil evaporation, soil temperature |
| Landscape water | [Erosion and sediment](erosion-sediment.md) | Peak runoff rate, MUSLE, sub-daily erosion, sediment in lateral flow, urban loads, filter strips, grassed waterways and user BMPs |
| Routing | [Channels](channels.md) | Channel routing, sediment transport and in-stream water quality |
| Routing | [Aquifers](aquifers.md) | Aquifer objects and the gwflow groundwater module |
| Routing | [Reservoirs and wetlands](reservoirs-wetlands.md) | Reservoir water balance and release rules, wetlands |
| Routing | [Recall and point sources](recall-point-sources.md) | Recall time series and point source loads |
| Routing | [Decision tables](decision-tables.md) | Condition evaluation and actions |
| Plants and chemistry | [Plant growth and land use management](plant-growth-lum.md) | Heat units, biomass, leaf area, stresses, harvest, scheduled management |
| Plants and chemistry | [Nutrient cycling](nutrient-cycling.md) | Soil nitrogen and phosphorus pools, transformations, losses; algae, CBOD and oxygen in runoff; septic systems |
| Plants and chemistry | [Carbon](carbon.md) | Static and CENTURY-based soil carbon |
| Plants and chemistry | [Pesticides](pesticides.md) | Application, partitioning, decay and transport |
| Plants and chemistry | [Salts and constituents](salts-constituents.md) | Salt ion chemistry, other constituents, pathogens and heavy metals |

## SWAT 2009 processes not in SWAT+ 62.0.1

The SWAT 2009 theoretical documentation describes some processes that SWAT+ 62.0.1 does not simulate, or simulates in a different way:

- Elevation bands within a subbasin. SWAT+ corrects precipitation and temperature for the elevation of each object instead (see [Climate and weather](climate-weather.md#elevation-lapse)).
- Monthly climate change adjustments of precipitation, temperature, solar radiation and humidity. SWAT+ 62.0.1 has no input for them; adjust the weather files instead.
- Hourly air temperature and the distribution of solar radiation over the hours of the day.
- The adjustment of the curve number for slope.
- Transmission losses from tributary channels within a subbasin. SWAT+ has no tributary channels; losses are computed for each channel object.
- Bank storage in the main channel.
- The SWAT 2009 channel sediment routing (simplified Bagnold stream power equation, channel erodibility and cover factors, downcutting and widening). SWAT+ uses the channel sediment model described in [Channels](channels.md#sediment).
- Potholes and other depressional areas, replaced by wetlands and paddies in HRUs (see [Reservoirs and wetlands](reservoirs-wetlands.md#wetlands-and-paddies)).
- Reservoir release from measured monthly outflow or a target storage. SWAT+ uses release decision tables and measured releases from recall files.
- Chlorophyll-a and Secchi depth relations for lakes and reservoirs.
- The stream and dam reaeration formulas of QUAL2E; SWAT+ uses the reaeration rate given in [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha).
- The two-population bacteria model (persistent and less persistent bacteria), replaced by the pathogen routines described in [Salts and constituents](salts-constituents.md#pathogens-and-heavy-metals).
- Continuous fertilization and automatic fertilization by nitrogen stress. Decision tables can fertilize in response to conditions instead (see [Decision tables](decision-tables.md)).
- Consumptive water use and water transfer between objects, replaced by water allocation (see [Water allocation](../input-reference/water-allocation.md)).

## Page layout

Every symbol is defined under its equation. Where a symbol is a user input, the input file and the column header the SWAT+ Editor writes are named with it, and the basin switches and parameters that change the result are listed together on each page.

The last section of every page, Sources, is for developers. It links to the Fortran routines at the 62.0.1 tag, maps symbols and columns to Fortran variable names, and records implementation details.

??? quote "Sources"

    - Daily HRU sequence: [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Object loop that calls HRUs, channels, aquifers and reservoirs: [`command.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/command.f90)

    The pages in this section were checked against SWAT+ 62.0.1 (commit `6f51536`). Where a page and the Fortran source disagree, the source describes what the model does.

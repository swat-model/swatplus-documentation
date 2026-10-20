---
title: Input reference
description: The SWAT+ input files, their columns, units and defaults, and how the model uses them, for revision 62.0.1.
status: review
verified_against:
  - src/readcio_read.f90
  - src/input_file_module.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

This section describes the SWAT+ input files for revision 62.0.1. Each page gives the purpose of a file, its columns with units and defaults, how the model uses the values, an example from the reference datasets, and the files it is linked to. Where the code behaves in a way a user would not expect (a column that is read but has no effect, a default that differs from the one SWAT+ Editor writes), the page says so.

Every page was checked against the SWAT+ source at the commit recorded as `verified_at_commit` in its front matter. Where the source and older documentation disagree, the pages follow the source. The last section of each page, Sources, links to the Fortran routines and lists the variable names for developers.

[`file.cio`](file-cio.md) names every other input file, so it is the place to start.

## Older projects

A project set up for an earlier revision needs these changes before it runs correctly with 62.0.1:

- The `basin` line of [`file.cio`](../input-reference/file-cio.md) now has three file names, and the `water_rights` line has two. An old `basin` line shifts every later line of [`file.cio`](../input-reference/file-cio.md) by one without a message. See [older file.cio files](file-cio.md#older-filecio-files).
- The dynamic carbon model is now `carbon = 2` in [`codes.bsn`](../input-reference/codes-bsn.md). With `carbon = 1` no organic matter routine runs. See [carbon model](codes-bsn.md#carbon-model).
- [`carb_coefs.cbn`](../input-reference/cbn.md) is no longer read. Its settings moved to [`carbon.bsn`](carbon-bsn.md) and [`carbon_lyr.bsn`](carbon-lyr-bsn.md), and its output switch to [`print.prt`](print-prt.md).

## Simulation control

- [`file.cio`](file-cio.md): master index. Names the input file for every category, the weather data folders and the output folder.
- [`time.sim`](time-sim.md): simulation period and number of time steps per day.
- [`print.prt`](print-prt.md): warm-up years, daily print window and the output files written at each interval.
- [`object.cnt`](object-cnt.md): basin name, areas and the number of spatial objects of each type.

## Basin parameters

- [`codes.bsn`](codes-bsn.md): basin-wide method codes (PET method, channel routing, carbon model, runoff method and others).
- [`parameters.bsn`](parameters-bsn.md): basin-wide coefficients for runoff, peak rate, nutrients, pesticides, routing, lapse rates, erosion and CO₂.
- [`carbon.bsn`](carbon-bsn.md): parameters of the dynamic soil carbon model.
- [`carbon_lyr.bsn`](carbon-lyr-bsn.md): decomposition rates and CO₂ fractions of the dynamic soil carbon model, for the surface layer and the deeper layers.

## Spatial objects and connectivity

- [Connect files](con.md): [`hru.con`](../input-reference/con.md), [`rout_unit.con`](../input-reference/con.md), [`chandeg.con`](../input-reference/con.md), [`aquifer.con`](../input-reference/con.md), [`reservoir.con`](../input-reference/con.md), [`recall.con`](../input-reference/con.md) and the other connect files, which place each object, assign its weather station and route its outflow.
- [`hru-data.hru`](hru.md): the records each HRU uses for topography, hydrology, soil, land use, initial conditions, surface storage, snow and field geometry.
- [Hydrology and topography](hyd.md): [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd), [`topography.hyd`](../input-reference/hyd.md#topographyhyd), [`field.fld`](../input-reference/hyd.md#fieldfld) and `shade_factor.shf`.
- [Recall](recall.md): point sources and inlets given as time series.
- [`hru-lte.hru`](hru-lte.md): the simplified HRU-lte objects.
- [Routing and landscape units](units.md): [`rout_unit.def`](../input-reference/units.md#rout_unitdef), [`rout_unit.ele`](../input-reference/units.md#rout_unitele), [`rout_unit.rtu`](../input-reference/units.md#rout_unitrtu), [`ls_unit.def`](../input-reference/units.md#ls_unitdef), [`ls_unit.ele`](../input-reference/units.md#ls_unitele) and [`aqu_catunit.ele`](../input-reference/units.md#aqu_catunitele).
- [Link files](link.md): [`chan-surf.lin`](../input-reference/link.md#chan-surflin) for overbank flow to floodplain HRUs and [`aqu_cha.lin`](../input-reference/link.md#aqu_chalin) for aquifer return flow to several channels.

## Climate

- [Climate files](cli.md): weather stations ([`weather-sta.cli`](../input-reference/cli.md#weather-stacli)), weather generator statistics ([`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli)), the lists of observed data files and atmospheric deposition.
- [`*.pcp`](pcp.md): measured daily or sub-daily precipitation for one gauge.
- [`*.tmp`](tmp.md): measured daily maximum and minimum air temperature for one gauge.
- [`*.tem`](tem.md): temperature files with the `.tem` extension, read like `.tmp` files.
- [`snow.sno`](sno.md): snowfall, snowmelt and snow cover parameters.

## Soils and land use

- [`soils.sol`](sol.md): soil profiles and layer properties.
- [`landuse.lum`](lum.md): land use and management records used by HRUs.
- [Land use tables](lum-tables.md): curve number, conservation practice and overland flow Manning's n tables named in [`landuse.lum`](../input-reference/lum.md).

## Channels

- [Channel group](cha.md): the `channel` line of [`file.cio`](../input-reference/file-cio.md) and which of its files are used, initial channel contents, stream temperature and the legacy channel files.
- [Chandeg channel files](sd-channel.md): [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha), [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), [`sed_nut.cha`](../input-reference/sd-channel.md#sed_nutcha) and [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha), with the geometry, hydraulic, sediment and water quality parameters of the channels SWAT+ routes.

## Aquifers, reservoirs and wetlands

- [Aquifer files](aqu.md): [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) and its initial conditions.
- [Reservoir files](res.md): [`reservoir.res`](../input-reference/res.md#reservoirres) and its initial condition, hydrology, sediment, nutrient and weir databases.
- [Wetland files](wet.md): [`wetland.wet`](../input-reference/wet.md#wetlandwet) and [`hydrology.wet`](../input-reference/wet.md#hydrologywet), for HRUs with ponded water including rice paddies.

## Management

- [Operation databases](ops.md): harvest, grazing, irrigation, chemical application, fire and street sweeping.
- [Decision tables](dtl.md): [`lum.dtl`](../input-reference/dtl.md), [`res_rel.dtl`](../input-reference/dtl.md), [`scen_lu.dtl`](../input-reference/dtl.md) and [`flo_con.dtl`](../input-reference/dtl.md).
- [`plants.plt`](plt.md): plant parameter database.
- [`fertilizer.frt`](frt.md): fertilizer and manure databases.
- [`tillage.til`](til.md): tillage implements and biological mixing.
- [`carb_coefs.cbn`](cbn.md): no longer read in 62.0.1.
- [`treatment.trt`](trt.md): placeholder file, not read.
- [Manure allocation](manure-allocation.md): manure sources and the HRUs that draw from them.
- [Management schedules and other inputs](management.md): [`management.sch`](../input-reference/management.md#managementsch), [`puddle.ops`](../input-reference/management.md#puddleops), [`transplant.ops`](../input-reference/management.md#transplantops), `co2_yr.dat` and [`object.prt`](../input-reference/management.md#objectprt).

## Initial conditions

- [Initialization files](ini.md): [`plant.ini`](../input-reference/ini.md#plantini), [`soil_plant.ini`](../input-reference/ini.md#soil_plantini), [`nutrients.sol`](../input-reference/ini.md#nutrientssol) and [`om_water.ini`](../input-reference/ini.md#om_waterini). Pesticide, pathogen, salt and constituent initial conditions are on the pages for those modules.

## Structural practices

- [Structural practice files](str.md): tile drains, septic systems, filter strips, grassed waterways, user-defined practices, the septic and urban databases, and saturated buffers.

## Pollutants

- [Pesticides](pes.md): [`pesticide.pes`](../input-reference/pes.md#pesticidepes), initial pesticide amounts and the metabolite chain.
- [Pathogens](pth.md): [`pathogens.pth`](../input-reference/pth.md#pathogenspth) and initial pathogen amounts.
- [Heavy metals](mtl.md): heavy metal inputs.

## Groundwater

- [gwflow](gwflow.md): the cell-based groundwater module, used in place of the lumped aquifers when `gwflow = 1` in [`codes.bsn`](../input-reference/codes-bsn.md).

## Salts and constituents

- [Salt module](salt.md): inputs for the eight major salt ions.
- [Constituent module](cs.md): [`constituents.cs`](../input-reference/cs.md#constituentscs) and the inputs for selenate, selenite and boron.

## Water allocation

- [Water allocation](water-allocation.md): places of use, points of diversion and return, and the treatment, use, tower, canal, pipe and outside-basin files.

??? quote "Sources"

    - File names and their order in `file.cio`: [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90) and [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90).
    - Each page lists the readers and the routines that use its inputs in its Sources section.

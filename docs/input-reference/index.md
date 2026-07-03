---
title: Input reference
description: Every SWAT+ input file, verified against the Fortran source.
status: review
---

This section documents every SWAT+ input file. Each page lists:

- the file's purpose
- the Fortran reader and the derived type it populates
- the column layout, units, defaults
- a real example from the reference datasets
- known bugs or quirks in an `Important` section at the bottom

Every page is verified against the SWAT+ source at a specific commit, recorded in the page frontmatter as `verified_at_commit`. The source code is the only authoritative reference; example datasets are downstream and can drift.

## Simulation control

- [`file.cio`](../input-reference/file-cio.md). Master index. Names every other input file.
- [`time.sim`](../input-reference/time-sim.md). Simulation period and time step.
- [`print.prt`](../input-reference/print-prt.md). Output selection and aggregation.
- [`object.cnt`](../input-reference/object-cnt.md). Basin name, areas, spatial object counts.

## Basin parameters

- [`codes.bsn`](../input-reference/codes-bsn.md). Method switches.
- [`parameters.bsn`](../input-reference/parameters-bsn.md). Numeric coefficients.

## Spatial objects and connectivity

- [`*.con`](../input-reference/con.md). Connectivity files (hru.con, chandeg.con, aquifer.con, reservoir.con, ...).
- [`hru-data.hru`](../input-reference/hru.md). Per-HRU pointer table.
- [`*.hyd`, `field.fld`, `shade_factor.shf`](../input-reference/hyd.md). Per-HRU hydrology, topography, field geometry, and shade factor. Referenced by `hru-data.hru`.
- [`recall`](../input-reference/recall.md). Point sources and inlets. Master `recall.rec` plus salt and constituent side databases and the region/element files.

## Structural BMPs

- [`*.str`, `septic.sep`, `urban.urb`](../input-reference/str.md). Tile drains, septic systems and effluent, filter strips, grassed waterways, user-defined BMPs, saturated buffers, urban land cover.

## Climate

- [`*.cli`](../input-reference/cli.md). Index files: weather-sta.cli, weather-wgn.cli, pcp.cli, tmp.cli, slr.cli, hmd.cli, wnd.cli, pet.cli, atmodep.cli.
- [`*.pcp`](../input-reference/pcp.md). Precipitation data files.
- [`*.tmp`](../input-reference/tmp.md). Temperature data files.
- [`*.tem`](../input-reference/tem.md). Legacy temperature file extension.
- [`snow.sno`](../input-reference/sno.md). Snow parameter database.

## Soils and land use

- [`soils.sol`](../input-reference/sol.md). Soil profile and layer properties.
- [`landuse.lum`](../input-reference/lum.md). Land-use management.
- [`*.lum` lookup tables](../input-reference/lum-tables.md). Curve number, conservation practice, and overland-flow Manning's n tables referenced by `landuse.lum`.

## Initial conditions

- [`*.ini`](../input-reference/ini.md). General initial conditions: `plant.ini` (plant communities), `soil_plant.ini` (soil water, residue, plant biomass), `om_water.ini` (organic matter in water bodies). Solute-side init files are covered in their module pages under Solute transport and Pollutants.

## Channels, aquifers, reservoirs, wetlands

- [`*.cha`](../input-reference/cha.md). Legacy channel files.
- [`sd_channel`](../input-reference/sd-channel.md). SWAT+ routing channel inputs (`hydrology.cha`, `sediment.cha`, `nutrients.cha`).
- [`*.aqu`](../input-reference/aqu.md). Aquifer files (`aquifer.aqu`, `initial.aqu`).
- [`*.res`](../input-reference/res.md). Reservoir files.
- [`*.wet`](../input-reference/wet.md). Wetland files.

## Groundwater

- [`gwflow.*`](../input-reference/gwflow.md). 2D cell-based groundwater module inputs (mesh, channel coupling, tiles, ponds, canals, solutes, heat).

## Operation and management databases

- [`management.sch` and minor inputs](../input-reference/management.md). Fixed-schedule management, puddle.ops, transplant.plt, co2.out, object.prt.
- [`*.ops`](../input-reference/ops.md). harv, graze, irr, chem_app, fire, sweep.
- [`*.dtl`](../input-reference/dtl.md). Decision tables (lum.dtl, res_rel.dtl, scen_lu.dtl, flo_con.dtl).
- [`plants.plt`](../input-reference/plt.md). Plant parameter database.
- [`fertilizer.frt`](../input-reference/frt.md). Fertilizer composition and the manure type and organic-matter databases (`manure_db.frt`, `manure_om.frt`).
- [`manure_allo.mnu`](../input-reference/manure-allocation.md). Manure allocation. Sources, demands, and the rule that distributes manure between them.
- [`tillage.til`](../input-reference/til.md). Tillage operations.
- [`carb_coefs.cbn`](../input-reference/cbn.md). Century carbon coefficients.
- [`treatment.trt`](../input-reference/trt.md). Legacy treatment placeholder.

## Water allocation

- [`water_allocation.wro` and the `*.wal` transport files](../input-reference/water-allocation.md). Water-rights and inter-object water transfer module: master allocation file plus canal, pipe, tower, treatment, use, out-of-basin source and receiver inputs.

## Solute transport

- [`salt module`](../input-reference/salt.md). rtb-salt inputs: per-object initial conditions and applied loads for the eight salt ions.
- [`cs module`](../input-reference/cs.md). rtb-cs inputs: master `constituents.cs` plus per-object initial conditions and applied loads for selenium, boron, and other constituents.

## Pollutants

- [`pesticide module`](../input-reference/pes.md). `pesticide.pes` parameter database, per-HRU and per-channel initial conditions, and the parent-daughter metabolite chain.
- [`pathogen module`](../input-reference/pth.md). `pathogens.pth` parameter database and per-HRU and per-channel initial conditions.
- [`metals module`](../input-reference/mtl.md). Per-HRU initial heavy metal concentrations.

## Verification procedure

The procedure for verifying a new or updated page is in [`SOURCE-OF-TRUTH.md`](https://github.com/swat-model/swatplus-documentation/blob/main/wd/SOURCE-OF-TRUTH.md) in the docs working folder.

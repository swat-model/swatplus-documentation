---
title: Water balance and mass balance issues
description: Common causes of a bad SWAT+ water balance. Climate mapping, curve numbers, missing management, soil parameters.
status: review
---

When `basin_wb_aa.txt` does not match expectation, the cause is almost always in one of four places: climate input mapping, curve numbers, the management schedule, or soil parameters. Inspect them in that order. Compare the offending values in `checker.out` and `diagnostics.out` against the source of truth in your input files.

## What to compare

The basin-average annual water balance from `basin_wb_aa.txt` should approximately satisfy:

```text
precip = et + surq_gen + latq + perc + snopack_storage + soil_water_change
```

Where `wateryld = surq_gen + latq + qtile`. Big discrepancies in any one term point at a specific input group.

## Symptom: precip is wrong

The reported `precip` does not match the rainfall in the source `.pcp` file.

- Open `weather-sta.cli`. Confirm the station name and that `pgage` points at the right `.cli` index.
- Open the `.cli` index. Confirm it lists the `.pcp` filename that contains the right data.
- Open the `.pcp` file and check the first record. The header carries the `nbyr`, `tstep`, `lat`, `lon`, and `elev` for the station. Lat and lon mismatched with `hru.con` can mean the wrong station was assigned to the HRU.

If `diagnostics.out` contains `<name> file not found (pgage)`, the climate mapping failed entirely and SWAT+ generated rainfall from the weather generator. The reported `precip` will not match any observed dataset.

References: [*.cli](../input-reference/cli.md), [*.pcp](../input-reference/pcp.md).

## Symptom: surq_gen is too high or too low

Surface runoff is controlled by:

1. The curve number for the (soil hydrologic group, land cover) pair, taken from `cntable.lum` and modified by `cn3_swf` in `hydrology.hyd`.
2. The soil-water content, computed from `soils.sol` field capacity and saturation.
3. The infiltration method: `gampt = 0` (curve number) or `gampt = 1` (Green-Ampt) in `codes.bsn`.

Checks:

- Open `checker.out`. Confirm `hydgrp` (A, B, C, D) per soil matches what your `soils.sol` declares. A misclassification flips runoff by tens of mm.
- Open `cntable.lum`. The CN values are looked up by the `cn2` column of the offending `landuse.lum` row. Cross-check the value against a CN table for that land cover / hydrologic group pair.
- Check `cn3_swf` in `hydrology.hyd`. Defaults to zero; a value near 1 will damp runoff response to wet conditions.
- Confirm `gampt` in `codes.bsn` is what you intended.

References: [Checker and diagnostics](../output-reference/checker-diagnostics.md), [codes.bsn](../input-reference/codes-bsn.md), [landuse.lum](../input-reference/lum.md).

## Symptom: ET is too high or too low

ET depends on the PET method and on plant cover.

- `codes.bsn` field 3 (`pet`): 0 Priestley-Taylor, 1 Penman-Monteith, 2 Hargreaves, 3 file. Penman-Monteith needs solar radiation, humidity, and wind; if those are missing, the model uses generated values.
- `esco` and `epco` in `hydrology.hyd` (per HRU) control soil evaporation and plant uptake compensation. Defaults in `checker.out` are 0.95 and 1.0; deviations from those change the ET partition.
- Plant cover: if the management schedule is wrong, plants never grow, `eplant` stays low, and the run produces more bare-soil evaporation and runoff.

Open `checker.out` and confirm `esco` and `epco` match what you expect. Open `hru_pw_aa.txt` and inspect biomass and LAI; near-zero biomass on a cropped HRU means management did not fire.

References: [codes.bsn](../input-reference/codes-bsn.md), [hru.md](../input-reference/hru.md).

## Symptom: management never fires

When `landuse.lum` points at a schedule that does not exist, `diagnostics.out` writes:

```text
<lum_name>  <mgt_name>  not found in management.sch
```

The HRU runs with no operations: no plant, no fertilize, no harvest. `hru_pw_aa.txt` will show zero biomass and zero yield. `crop_yld_aa.txt` will be empty or report a residual.

Fix by either matching `landuse.lum%mgt` to a schedule name in `management.sch`, or adding the schedule.

Reference: [*.dtl](../input-reference/dtl.md) covers decision-table-driven operations.

## Symptom: percolation is zero or saturated

Percolation depends on the soil profile in `soils.sol`:

- `sumfc` (column in `checker.out`): the total field capacity over the profile. A near-zero value means the soil-layer field capacities did not load.
- `sumul`: the saturation upper limit. Should be larger than `sumfc`.
- The `perco` coefficient in `hydrology.hyd` scales the percolation rate. Default 0.5; setting to 0 stops percolation.

A `zmx = 2000` row in `checker.out` for every HRU usually means the per-soil `soils.sol` block was not parsed. Look for warnings in `diagnostics.out` referencing the soil name.

References: [soils.sol](../input-reference/sol.md), [checker.out](../output-reference/checker-diagnostics.md).

## Symptom: bad latq, qtile, or surq_runon

These depend on:

- `latq_co` in `hydrology.hyd`. The lateral-flow coefficient. Zero turns lateral flow off. Default in the shipped Ames data is 0.01.
- `tiledrain` flag in `hydrology.hyd`. Confirm `checker.out` shows `0` (no tile) or `1` (tile) as intended.
- Tile drainage parameters: see the `tile` block in `hydrology.hyd` and the `tiledrain.str` structural file.

## Symptom: ru_aa.txt and basin_wb_aa.txt disagree

The routing-unit output sums HRU contributions through routing. The basin output sums them directly. A large disagreement means routing is doing something unexpected. Check:

- `rout_unit.def`, `rout_unit.ele`, `rout_unit.rtu`. The routing definition and area weights.
- `chandeg.con` and the channel-routing inputs. A misconfigured channel that has no length or no slope produces bizarre routed values.

## Workflow

1. Run the model. Confirm `success.fin` exists.
2. Read `diagnostics.out` end to end. Resolve every line.
3. Open `checker.out`. Per HRU, sanity-check `hydgrp`, `zmx`, `sumfc`, `sumul`, `usle_k`, `esco`, `epco`, `perco`, `latq_co`, `tiledrain`.
4. Open `basin_wb_aa.txt`. Compare each term against your expectation. If precip is wrong, fix climate mapping. If ET is wrong, check PET and esco/epco. If surface runoff is wrong, check CN. If percolation is wrong, check soils.

## Related

- [Checker and diagnostics](../output-reference/checker-diagnostics.md) for the structure of the diagnostic files.
- [Common runtime errors](../faq-troubleshooting/common-runtime-errors.md) for the exact warning strings.
- [Water balance outputs](../output-reference/water-balance.md) for the column definitions.

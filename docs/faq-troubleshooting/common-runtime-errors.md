---
title: Common runtime errors
description: The runtime warnings and errors SWAT+ writes to diagnostics.out, simulation.out, and checker.out, what each one means, and how to fix it.
status: review
---

SWAT+ writes runtime messages to three files. The location of the message tells you the type of problem:

- `simulation.out`: console-style status. Successful runs end with `Execution successfully completed`. Failed runs stop mid-stream.
- `diagnostics.out`: missing references and ignored options. Each line is a name that one input file pointed at but that does not exist in the file it was supposed to be in. The run continues, but with a default substituted.
- `checker.out`: resolved per-HRU parameters. Bad values here often mean a soil or option silently failed to load.
- console output to stdout: a small number of `Error:` lines written directly by some readers. These often precede an abort.

Source: error and warning text strings traced to the SWAT+ source at `/drive/c/repositories/swatplus/src/`. Search the source with `grep -rn "write (9001" src/` to see every diagnostics line, and `grep -rn '"Error' src/` to see the stderr lines.

## Missing input references (diagnostics.out)

These all share the form `<name>  not found in <file>` or `<name>  not found (<file>)`. The reader detected that an input pointed at a name that the corresponding database does not contain.

### `<name> not found in management.sch`

Source: `landuse_read.f90` line 147.

A row in `landuse.lum` named a management schedule that does not exist in `management.sch`. Fix: open `landuse.lum`, find the row whose `mgt` column holds `<name>`, and either add a matching schedule to `management.sch` or point the row at one that exists.

This is a warning, not a stop. The land use will run without scheduled operations, which means no plant, no fertilize, no harvest. The HRU will not behave as intended.

### `<name> not found in plant.ini`

Source: `landuse_read.f90` line 144.

Same pattern, different column. Fix the `plnt_com` column of the offending `landuse.lum` row, or add a row to `plant.ini`.

### `<name> not found (landuse.lum)`

Source: `hru_read.f90` line 77.

An HRU in `hru-data.hru` named a `lu_mgt` that does not exist in `landuse.lum`. The HRU runs with no land use, which is rarely what you want.

### `<name> not found (soils.sol)`

Source: `hru_read.f90` line 157.

An HRU named a soil that is not in `soils.sol`. The HRU will fall back to a default soil. `checker.out` is the fastest place to confirm: look for `zmx = 2000`, `usle_k = 0`, or any of your soils missing entirely.

### `<name> not found (topography.hyd)`, `(hydrograph.hyd)`, `(snow.sno)`

Same family. The pointer in `hru-data.hru` does not match any record in the named file. Verify the name in both files matches exactly. Names are case-sensitive.

### `<name> not found (initial.cha)`, `(hydrology.cha)`, `(sediment.cha)`, `(nutrients.cha)`

Source: `ch_read.f90` lines 97 to 100.

A channel definition references a property record that is missing. The channel will use defaults. If your project has no channels, ignore.

### `<name> not found (res-init)`, `(res-hyd)`, `(res-release)`, `(res-sed)`, `(res-nut)`

Source: `res_read.f90` and `wet_initial.f90`. Same pattern for reservoirs and wetlands. Fix the corresponding pointer.

### `file not found (wgn)`, `(pgage)`, `(tgage)`, `(sgage)`, `(hgage)`, `(wgage)`, `(petgage)`, `(atmodep)`

Source: `cli_staread.f90` lines 72 to 95.

A weather station in `weather-sta.cli` named a gage that does not match any row in the corresponding `.cli` index file. Verify the index file lists the station file under the same name. The Ames_sub1 shipped dataset prints `ames.tem  file not found (tgage)` because the editor wrote the station with a `.tem` extension that the `.tmp` index does not contain.

### `file not found (basins_carbon.tes)`

Source: `carbon_read.f90` line 19.

Optional carbon-test file. Safe to ignore unless you are running the carbon test harness.

### `WARNING: The variable <name> in the input file carb_coefs.cbn is not a recognized variable.`

Source: `carbon_coef_read.f90` line 141.

The reader did not recognize a variable name in `carb_coefs.cbn`. Check spelling against the names in `carbon_coef_read.f90`. The variable is ignored.

### `Warning: Input file named <name> is missing or null.`

Source: `utils.f90` line 69. Emitted by the generic CSV/table reader when a referenced file is `null` or missing. Usually benign because most slots in `file.cio` accept `null`.

### `Warning: unknown column header named <name>`

Source: `utils.f90` line 874. The reader's column-name table did not include the header it found. The column is skipped. Often caused by a file written by a newer or older editor than the executable expects.

## Errors written to stdout

### `Error: The output object <name> in the input file print.prt is not a valid object.`

Source: `basin_print_codes_read.f90` line 665.

A row in `print.prt` names an object that is not in the recognized list. Fix the row name. The list of valid objects is in `basin_module.f90`.

### `Error: <name> print object is duplicated in the input file print.prt. Aborting`

Source: `basin_module.f90` line 429.

A `print.prt` row appears twice. Delete the duplicate.

### `Error: The number of nmbr_soil_test_layers has not been specified`

Source: `carbon_coef_read.f90` line 120. The `carb_coefs.cbn` file is missing the `nmbr_soil_test_layers` declaration. Add it before the soil-test block.

### `Error: The number input soil test layers exceeds nmbr_soil_test_layers of <n>`

Source: `carbon_coef_read.f90` line 127. You declared `nmbr_soil_test_layers = n` and then provided more than `n` soil-test rows. Match them.

## Failure modes that are not text errors

### Run stops mid-day with no `Execution successfully completed`

Look at the last `Original Simulation  mm  dd  yyyy` line in `simulation.out`. The crash is on or near that date. Common causes:

- Climate file is shorter than the simulation period.
- A divide-by-zero in a hydrology routine (most often caused by zero soil-layer depths or zero plant biomass).
- The compiler-generated `STOP` from a numerical routine (look for an integer code in console output).

### `success.fin` is missing

The run did not complete. The model writes `success.fin` only on a clean exit.

### Output files are not written

The corresponding row in `print.prt` is set to `n` for that interval. Cross-check against `files_out.out`, which lists every output file the run actually opened.

### `Permission denied` (Linux, macOS)

The executable file is not marked executable. Run `chmod +x swatplus-<version>-linux-x86_64`.

### `Error opening file ...`

The model is not running from inside the project folder. `cd` into the folder, or pass a full path to a launcher that does so.

## Related

- [Checker and diagnostics](../output-reference/checker-diagnostics.md) for the file structures.
- [Water balance issues](../faq-troubleshooting/water-balance-issues.md) for output sanity checks.

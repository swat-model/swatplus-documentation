---
title: Testing
description: The scenario regression test that compares SWAT+ output with reference output, and how to run it at 62.0.1.
status: review
verified_against:
  - swatplus/CMakeLists.txt
  - swatplus/test/spcheck.py
  - swatplus/refdata/Ames_sub1/.testfiles.txt
  - swatplus/.github/workflows/test.yml
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ has a scenario regression test: it runs the model on a reference dataset and compares chosen output files with copies kept in the repository. Differences outside a tolerance point to a change in results, which is then either a bug or an intended change that needs new reference outputs.

## Test script

`test/spcheck.py` (Python 3, standard library only) has three commands:

| Command | Use |
|---------|-----|
| `ctest <executable> <reference folder> <work folder>` | copy the reference folder into the work folder, run the executable there, and compare the files listed in the folder's `.testfiles.txt` with the reference copies; exit with code 1 if any value differs |
| `run <executable> <scenario>` | run `build/<executable>` on `data/<scenario>` in a new numbered folder under `runs/<scenario>/` |
| `compare <scenario> <a> <b>` | compare two numbered runs of a scenario |

Options `--abserr` and `--relerr` set the tolerances (defaults `1e-8` and `0.05`), and `--nlines` and `--nerrorlines` limit how much of each file is checked and reported.

Two numbers are equal when

$$|v_1 - v_2| \le e_{abs} + e_{rel}\,|v_2|$$

Only real numbers are compared, value by value on matching lines; integers and text are skipped, as are the title lines with the build date (lines containing `MODULAR`).

## Running the test at 62.0.1

`CMakeLists.txt` registers one test, `Ames_sub1`, with tolerances of `1e-8` absolute and 1 % relative, and reference data in `data/Ames_sub1`. At 62.0.1 the repository has no `data/` folder; the reference datasets are in `refdata/`. `ctest` therefore fails at once with `data dir not found`.

To run the comparison, call the script directly with the `refdata` folder:

```bash
cmake -B build -D CMAKE_BUILD_TYPE=Release
cmake --build build -j 8
python3 test/spcheck.py ctest build/swatplus-*-Rel refdata/Ames_sub1 build/test-runs --abserr 1e-8 --relerr 0.01
```

Notes on the reference dataset:

- A full `Ames_sub1` run writes about 9 GB, mostly daily carbon output, and takes a few minutes. Make sure the work folder has the space.
- `.testfiles.txt` lists 42 files. With the shipped `print.prt` the model rewrites fewer than half of them; the rest (all `basin_*` files, `hydin_aa.txt`, `ru_aa.txt` and others) are copied from the reference folder and compared with themselves. The test therefore checks the HRU water and nutrient balances, plant and yield output and management output, and not channel, aquifer or basin output.

## Adding a scenario

1. Put a complete input set in a new folder under `refdata/` (or `data/`).
2. Run the model and check the outputs you want to fix as the reference.
3. Commit the inputs and those outputs.
4. Add a `.testfiles.txt` naming the output files to compare, one per line (`#` starts a comment).
5. Add an `add_test` line to `CMakeLists.txt` pointing at the folder.

## Continuous integration

`.github/workflows/test.yml` builds SWAT+ with Intel `ifx` on Ubuntu and runs `ctest` on pushes to branches whose name ends in `main`. With the `data/` path above, the test step fails. The release workflow (`build.yml`) builds the release executables for each tag and does not run the tests.

??? quote "Sources"

    - [`test/spcheck.py`](https://github.com/swat-model/swatplus/blob/62.0.1/test/spcheck.py): `ctest_all`, `cmp_file` and the `run`/`compare` commands.
    - [`CMakeLists.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/CMakeLists.txt): `set(ref_dir "${PROJECT_SOURCE_DIR}/data")`, tolerances `aerr = 1e-8`, `rerr = 0.01`, and `add_test(Ames_sub1 ...)`. The `Ithaca_sub6` test is commented out.
    - [`refdata/Ames_sub1/.testfiles.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/refdata/Ames_sub1/.testfiles.txt).
    - [`.github/workflows/test.yml`](https://github.com/swat-model/swatplus/blob/62.0.1/.github/workflows/test.yml) and [`.github/workflows/build.yml`](https://github.com/swat-model/swatplus/blob/62.0.1/.github/workflows/build.yml).
    - The 9 GB output size and the list of files rewritten are from a run of the 62.0.1 `gnu-lin_x86_64` release executable on 20 October 2026.

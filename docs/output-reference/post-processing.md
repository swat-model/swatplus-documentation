---
title: Post-processing helpers
description: The two Python scripts in the test folder of the SWAT+ source. spcheck.py runs scenarios and compares their outputs; swat_output_to_csv_files.py reads output files into pandas.
status: review
verified_against:
  - test/spcheck.py
  - test/swat_output_to_csv_files.py
  - CMakeLists.txt
  - refdata/Ames_sub1/.testfiles.txt
  - src/proc_bsn.f90
  - src/output_landscape_init.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The `test` folder of the SWAT+ source has two Python scripts. They are not installed with the model; run them from a copy of the source or copy them next to your project.

- `spcheck.py` runs SWAT+ on a scenario and compares the numbers in two sets of output files. The build uses it for its regression test.
- `swat_output_to_csv_files.py` reads SWAT+ output files into pandas tables and can save them as tab-separated files.

## spcheck.py

`spcheck.py` needs Python 3.10 or later and no extra packages. It has three commands.

### run

```
python spcheck.py run <executable> <scenario>
```

Run from a folder that contains `build/`, `data/` and `runs/`. The command copies `data/<scenario>` to a new folder `runs/<scenario>/<NN>#<date and time>#<executable>`, where `NN` is the next two-digit run number (`01`, `02`, ...), and runs `build/<executable>` there. If SWAT+ ends with an error, the run folder gets the suffix `-FAILED`.

### compare

```
python spcheck.py compare <scenario> <a> <b> [--abserr 1e-8] [--relerr 0.05] [--nlines N] [--nerrorlines N]
```

Compares two earlier runs of a scenario, given by their run numbers `a` and `b`. The files to compare are listed in `data/<scenario>/.testfiles.txt`, one name per line; lines starting with `#` are skipped. A failed run cannot be compared.

### ctest

```
python spcheck.py ctest <model_path> <data_dir> <tmp_dir> [--abserr 1e-8] [--relerr 0.05] [--nlines N] [--nerrorlines N]
```

Copies the whole folder `<data_dir>`, including its output files, to `<tmp_dir>`, runs `<model_path>` there, and compares the files listed in `<data_dir>/.testfiles.txt` between the original and the new run. It exits with code 1 when it finds differences. Because the original outputs are copied too, a listed file that the new run does not write is compared with the copied original and passes.

### Comparison rule

Both files are read line by line. On each line, only tokens that are decimal numbers are compared, by position; whole numbers (dates, object numbers) and text are skipped, and lines containing the version banner `MODULAR` are skipped. Two values $f_1$ (first run) and $f_2$ (second run) differ when

$$|f_1 - f_2| \ge e_{abs} + e_{rel}\,|f_2|$$

with $e_{abs}$ = `--abserr` (default $10^{-8}$) and $e_{rel}$ = `--relerr` (default 0.05). For each differing line the script prints both lines, the field numbers, the two values and their absolute and relative error, and at the end the total number of differences.

The script assumes both files have the same layout. It stops at the end of the shorter file without reporting a difference in length. A line whose two versions have different numbers of decimal values is not reported, and it lowers the difference count by one. `--nlines` limits the number of lines checked per file, and `--nerrorlines` the number of differing lines reported per file.

### Regression test in the build

`CMakeLists.txt` registers one test, `Ames_sub1`, which calls `spcheck.py ctest` with `--relerr 0.01` and `--abserr 1e-8`. The test reads its scenario from `<source>/data/Ames_sub1`; the reference data in the 62.0.1 source is in `refdata/Ames_sub1`. The `.testfiles.txt` of `Ames_sub1` lists 42 files; six of them (`hru_nut_carb_gl_aa.txt`, `hru_soilcarb_aa.txt`, `hru_rescarb_aa.txt`, `hru_plcarb_aa.txt`, `hru_soilc_stat.txt`, `hru_resc_stat.txt`) are no longer written by 62.0.1 and pass only because of the copy described above.

## swat_output_to_csv_files.py

The script maps output file names to reading instructions for `pandas.read_csv` and loads each file into a table.

### Use

```
cd <folder with SWAT+ outputs>
python /path/to/swat_output_to_csv_files.py
```

The script reads `files_out.out` from the current folder, then reads every file listed there, except `mgt_out.txt` and `yield.out`, and writes each one to `<name>.csv` in the same folder (for example `hru_wb_aa.txt.csv`). The `.csv` files are tab-separated.

From Python, one file can be read without writing anything:

```python
import swat_output_to_csv_files as s
df = s.read_output("basin_wb_aa.txt", s.spec_dict, write_csv=False)
```

### Supported files

Most files are read by skipping line 1 (title) and line 3 (units) and taking line 2 as the column names. `crop_yld_aa.txt` and `crop_yld_yr.txt` skip two lines. `lu_change_out.txt`, `basin_crop_yld_aa.txt` and `basin_crop_yld_yr.txt` keep line 3 as data. `checker.out` and `files_out.out` are read with fixed column names.

```
files_out.out  checker.out  hru_orgc.txt
hru_wb_aa.txt  hru_ncycle_aa.txt  hru_nb_aa.txt  hru_carbon_aa.txt  hru_nut_carb_gl_aa.txt  hru_ls_aa.txt  hru_pw_aa.txt
basin_wb_aa.txt  basin_nb_aa.txt  basin_carbon_aa.txt  basin_ls_aa.txt  basin_pw_aa.txt
crop_yld_yr.txt  crop_yld_aa.txt  lu_change_out.txt  basin_crop_yld_yr.txt  basin_crop_yld_aa.txt
hydout_aa.txt  hydin_aa.txt  deposition_aa.txt  wetland_aa.txt  basin_aqu_aa.txt  basin_res_aa.txt
recall_aa.txt  basin_cha_aa.txt  basin_sd_cha_aa.txt  basin_sd_chamorph_aa.txt  basin_psc_aa.txt  ru_aa.txt
```

Only average annual files are covered. `hru_orgc.txt` and `hru_nut_carb_gl_aa.txt` are not written by 62.0.1.

### Limits with 62.0.1

- The script stops (exit code 1) at the first file listed in `files_out.out` that it has no instructions for, with the message `Swat+ output filename not found in read specification dictionary.` A 62.0.1 run usually lists such files (for example the carbon files, `sd_chanbud_aa.txt` or any daily file), so a full run stops part way. Reading single files with `read_output` works.
- It passes `delim_whitespace=True` to `pandas.read_csv`. pandas 2.2 warns about this option and pandas 3.0 no longer accepts it; with pandas 3.0 every file fails with the message `could not be parsed for some reason`.
- `basin_wb_aa.txt` ends with the two-word label `Original Simulation` and a number, which gives its data row more values than the header has names, so pandas moves the leading columns into the row index.
- `files_out.out` is read as two columns, tag and file name. With `csvout` on, some tags contain a space (`CHANBUD ORDER`), which breaks those lines.

## Related files

- [Output naming convention](naming-convention.md): output file names and layout.
- [Checker and diagnostics](checker-diagnostics.md): `files_out.out` and `checker.out`.
- [Water balance outputs](water-balance.md): the trailing label in `basin_wb_aa.txt`.

??? quote "Sources"

    - [`test/spcheck.py`](https://github.com/swat-model/swatplus/blob/62.0.1/test/spcheck.py)
    - [`test/swat_output_to_csv_files.py`](https://github.com/swat-model/swatplus/blob/62.0.1/test/swat_output_to_csv_files.py)
    - Regression test: [`CMakeLists.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/CMakeLists.txt) and [`refdata/Ames_sub1/.testfiles.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/refdata/Ames_sub1/.testfiles.txt)
    - `files_out.out`: [`proc_bsn.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_bsn.f90); removed carbon files noted in [`output_landscape_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/output_landscape_init.f90)

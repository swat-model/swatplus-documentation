---
title: "Quick start: Ames_sub1"
status: review
verified_against:
  - swatplus/refdata/Ames_sub1/file.cio
  - swatplus/refdata/Ames_sub1/print.prt
  - swatplus/refdata/Ames_sub1/time.sim
  - swatplus/refdata/Ames_sub1/object.cnt
  - swatplus/refdata/Ames_sub1/simulation.out
  - swatplus/src/main.f90
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

Run a complete SWAT+ simulation in a few minutes using the small reference dataset shipped with the source repository.

## What it is

`Ames_sub1` is a twelve-HRU dataset near Ames, Iowa. It simulates 1975 through 2020 on a daily time step (see `time.sim`). The dataset is in the SWAT+ source tree at [`refdata/Ames_sub1`](https://github.com/swat-model/swatplus/tree/main/refdata/Ames_sub1).

## Prerequisites

- A SWAT+ executable. See [Install](install.md).
- A copy of the `Ames_sub1` folder. If you cloned the source repository, it is at `swatplus/refdata/Ames_sub1`. Otherwise, download it from the link above.

## Run it

1. Copy the executable into the `Ames_sub1` folder, or note its full path.
2. From a terminal, change into the `Ames_sub1` folder:

   ```bash
   cd path/to/Ames_sub1
   ```

3. Run the model:

   ```bash
   # Linux / macOS
   ./swatplus-3.0.4-gnu-lin_x86_64

   # Windows
   swatplus-3.0.4-gnu-win_amd64.exe
   ```

A simulation of this size takes a few seconds to a minute depending on your machine.

## What you should see

While running, SWAT+ writes progress to the console and to `simulation.out`. When it finishes successfully, the last lines of `simulation.out` contain:

```
 Execution successfully completed
```

The same line is written to `success.fin`.

The folder now contains a set of output files. With the default `print.prt` for this dataset, every `objects` row is set to `avann = y`, so each enabled object group writes an annual-average file. The annual-average files that appear in `refdata/Ames_sub1` after a successful run include:

```
basin_wb_aa.txt           basin water balance
basin_nb_aa.txt           basin nutrient balance
basin_ls_aa.txt           basin landscape (sediment)
basin_pw_aa.txt           basin plant and water stress
basin_aqu_aa.txt          basin aquifer
basin_cha_aa.txt          basin channel (legacy routing)
basin_sd_cha_aa.txt       basin channel (SWAT-DEG routing)
basin_res_aa.txt          basin reservoir
basin_psc_aa.txt          basin point-source / recall
basin_crop_yld_aa.txt     basin crop yields
crop_yld_aa.txt           crop yields (HRU detail)
hru_wb_aa.txt             HRU water balance
hru_nb_aa.txt             HRU nutrient balance
hru_ls_aa.txt             HRU landscape balance
hru_pw_aa.txt             HRU plant and water stress
```

Open `basin_wb_aa.txt` to see the simulated water balance. The columns are documented in [Water balance outputs](../output-reference/water-balance.md).

## If it fails

- **`Error opening file...`** Check that you are running the executable from inside the `Ames_sub1` folder, not from its parent.
- **`Permission denied`** on Linux or macOS. Run `chmod +x` on the executable.
- The model exits before writing output. Check `diagnostics.out` and `checker.out` for the first error.

For other errors, see [FAQ and troubleshooting](../faq-troubleshooting/index.md).

## Next

- Read [Project folder anatomy](project-folder-anatomy.md) to learn what each file in `Ames_sub1` does.
- Walk through the dataset slowly in the [Ames_sub1 walkthrough](../tutorials/ames-sub1.md).
- Build your own watershed in [Your first watershed](first-watershed.md).

---
title: Install
status: review
verified_against:
  - swatplus/CMakeLists.txt
  - swatplus/doc/Building.md
  - https://github.com/swat-model/swatplus/releases/tag/62.0.1
  - https://install.swat.tamu.edu
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

SWAT+ has two parts: the model itself, a command-line program, and the tools used to build and edit projects (QSWAT+, SWAT+ Editor and SWAT+ Toolbox). Most users install the tools and let SWAT+ Editor run the model. The model can also be downloaded or built without the tools.

## SWAT+ tools

[install.swat.tamu.edu](https://install.swat.tamu.edu) has one-line installers for Windows, Linux and macOS. Each installer can be run again at any time to update.

Install all three tools at once:

```bash
# Linux and macOS
curl -fsSL https://install.swat.tamu.edu/all.sh | bash
```

```powershell
# Windows (PowerShell)
irm https://install.swat.tamu.edu/all.ps1 | iex
```

Or one at a time:

| Tool | Purpose | Linux and macOS | Windows (PowerShell) |
|------|---------|-----------------|----------------------|
| QSWAT+ | QGIS plugin that delineates the watershed, creates HRUs and writes the project database. Also installs the SWAT+ support data and TauDEM. Needs QGIS. | `curl -fsSL https://install.swat.tamu.edu/qsp.sh \| bash` | `irm https://install.swat.tamu.edu/qsp.ps1 \| iex` |
| SWAT+ Editor | Edits project inputs, writes the input files and runs the model. | `curl -fsSL https://install.swat.tamu.edu/spe.sh \| bash` | `irm https://install.swat.tamu.edu/spe.ps1 \| iex` |
| SWAT+ Toolbox | Sensitivity analysis, calibration and other tasks on a finished project. | `curl -fsSL https://install.swat.tamu.edu/spt.sh \| bash` | `irm https://install.swat.tamu.edu/spt.ps1 \| iex` |

On Linux and macOS the tools go to `~/.local/share/SWATPlus/`, and on Windows to `%USERPROFILE%\SWATPlus\`.

## Model executable

Every release on the [GitHub releases page](https://github.com/swat-model/swatplus/releases) has prebuilt executables. For 62.0.1:

| File | System |
|------|--------|
| `swatplus-62.0.1-gnu-win_amd64-Rel.zip` | Windows, 64-bit (gfortran build) |
| `swatplus-62.0.1-ifo-win_amd64-Rel.zip` | Windows, 64-bit (Intel Fortran build) |
| `swatplus-62.0.1-gnu-lin_x86_64-Rel.zip` | Linux, x86-64 (gfortran build) |
| `swatplus-62.0.1-ifx-lin_x86_64-Rel.zip` | Linux, x86-64 (Intel Fortran build) |
| `swatplus-62.0.1-gnu-lin_aarch64-Rel.zip` | Linux, ARM64 |
| `swatplus-62.0.1-gnu-mac_arm64-Rel.zip` | macOS, Apple silicon |
| `swatplus-62.0.1-ifo-mac_x86_64-Rel.zip` | macOS, Intel |

Each zip contains a single executable with the same name (plus `.exe` on Windows). The name tells you the version, the compiler (`gnu` for gfortran, `ifo` for Intel Fortran Classic, `ifx` for Intel Fortran), the system and architecture, and `Rel` for an optimized release build. The gfortran and Intel builds give results that can differ slightly in the last digits.

Unzip the file and put the executable next to your project folder or in a folder on your `PATH`. On Linux and macOS, make it executable:

```bash
chmod +x swatplus-62.0.1-gnu-lin_x86_64-Rel
```

On macOS the first start of a downloaded program may be blocked; allow it under System Settings, Privacy and Security, or remove the quarantine flag with `xattr -d com.apple.quarantine <file>`.

To check the download, run it in an empty folder:

```bash
mkdir empty && cd empty
../swatplus-62.0.1-gnu-lin_x86_64-Rel
```

It prints a banner with the revision number and stops because there is no project:

```
                   SWAT+
             Revision 62.0.1
      Soil & Water Assessment Tool
GNU (13.3.0), 2026-10-19 22:51:37, Linux
    Program reading . . . executing

 Cannot find object.cnt input file
```

It also writes a few files (`diagnostics.out`, `simulation.out`, [`codes.bsn`](../input-reference/codes-bsn.md) and others) into the folder. Run the model from inside a project folder; it reads its inputs from the current folder and writes the outputs there.

## Building from source

Build from source to change the model or to use a development version. You need `git`, CMake 3.22 or newer, a Fortran compiler (gfortran, Intel `ifx` or `ifort`) and `make` or `ninja`.

```bash
git clone https://github.com/swat-model/swatplus.git
cd swatplus
git checkout 62.0.1
cmake -B build -D CMAKE_BUILD_TYPE=Release
cmake --build build -j 8
```

The executable is written to `build/` with a name of the form `swatplus-<version>-<compiler>-<system>_<arch>-Rel` (`-Dbg` for a `Debug` build, no suffix when no build type is given). Builds from a commit between tags have a version such as `62.0.1-3-g1a2b3c4`. The [Developer Guide](../developer-guide/index.md) has instructions for Visual Studio, VS Code and Codespaces.

## Next

Run the reference dataset to check the executable from start to finish: [Quick start: Ames_sub1](quick-start-ames.md).

??? quote "Sources"

    - Release files: [SWAT+ 62.0.1 on GitHub](https://github.com/swat-model/swatplus/releases/tag/62.0.1), checked 20 October 2026; the banner above is from the `gnu-lin_x86_64` executable.
    - Installers: [install.swat.tamu.edu](https://install.swat.tamu.edu), checked 20 October 2026.
    - Executable naming: `set(SWATPLUS_EXE "swatplus-${SWAT_VERSION}-${FFC}-${AR}${TY}")` in [`CMakeLists.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/CMakeLists.txt), with `SWAT_VERSION` from `git describe --tags`.
    - Build instructions: [`doc/Building.md`](https://github.com/swat-model/swatplus/blob/62.0.1/doc/Building.md).

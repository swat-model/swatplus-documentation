---
title: Install
status: review
verified_against:
  - swatplus/CMakeLists.txt
  - swatplus/doc/Building.md
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

You have two options.

1. **Download a prebuilt executable** if you only want to run SWAT+.
2. **Build from source** if you want to modify the model or use a development version.

## Option 1: Prebuilt executable

Prebuilt binaries for Windows, Linux, and macOS are attached to each GitHub release.

1. Go to https://github.com/swat-model/swatplus/releases.
2. Pick the latest release (or a specific tagged version).
3. Under **Assets**, download the file that matches your operating system and architecture.

Binaries are named `swatplus-<version>-<compiler>-<os>_<arch>` with an optional `-Rel` or `-Dbg` suffix and a `.exe` extension on Windows. The compiler tag is `gnu` (gfortran), `ifo` (Intel `ifort`), or `ifx` (Intel `ifx`). Examples:

- Linux x86_64, gfortran: `swatplus-3.0.4-gnu-lin_x86_64`
- Windows AMD64, gfortran: `swatplus-3.0.4-gnu-win_amd64.exe`
- macOS arm64, gfortran: `swatplus-3.0.4-gnu-mac_arm64`

Put the file somewhere on your `PATH`, or keep it next to your project folder. On Linux and macOS, make it executable:

```bash
chmod +x swatplus-3.0.4-gnu-lin_x86_64
```

Run it once with no arguments to confirm it starts:

```bash
./swatplus-3.0.4-gnu-lin_x86_64
```

It will look for input files in the current directory and exit if it does not find them. That is the expected behavior outside of a project folder.

## Option 2: Build from source

You need:

- `git`
- `cmake` (3.22 or newer)
- a Fortran compiler: `gfortran`, Intel `ifort`, or Intel `ifx`
- `make` or `ninja`

Clone the source:

```bash
git clone https://github.com/swat-model/swatplus.git
cd swatplus
```

Configure and build:

```bash
cmake -B build
cmake --build build -j 8
```

The executable is written to `build/` using the `swatplus-<version>-<compiler>-<os>_<arch>` pattern (with `.exe` on Windows). To pick a specific compiler at configure time, pass `-D CMAKE_Fortran_COMPILER=gfortran` (or `ifort`, `ifx`).

To install it system-wide:

```bash
cmake --install build --prefix ~/bin
```

For platform-specific build instructions (Visual Studio on Windows, VS Code Codespaces, Intel compilers), see the [Developer guide](../developer-guide/index.md).

## Supporting tools

To build SWAT+ inputs from a DEM, soil map, and land use map, install:

- **QSWAT+** (QGIS plugin): https://swat.tamu.edu/software/plus/. Delineates the watershed, defines HRUs, and writes the input files.
- **SWAT+ Editor** (desktop app): edits parameters in an existing project. Distributed from the same page.

The SWAT+ executable itself does not need either of these to run. They produce the input files that the executable reads.

## Verifying the install

Use the reference dataset in `swatplus/refdata/Ames_sub1` to confirm the executable runs end-to-end. See [Quick start: Ames_sub1](quick-start-ames.md).

---
title: Tagging and releases
description: How SWAT+ version numbers come from Git tags, how they reach the executable, and how releases are built.
status: review
verified_against:
  - swatplus/CMakeLists.txt
  - swatplus/src/main.f90.in
  - swatplus/doc/Tagging.md
  - swatplus/.github/workflows/build.yml
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

A SWAT+ version is a Git tag. No source file is edited to make a release: the build reads the tag and writes it into the executable's name and its start-up banner.

## Version numbers

Current tags have three parts, revision, minor and patch, for example `62.0.0` and `62.0.1`. Older tags include `61.0`, `61.0.2.61` and `60.5.7`. List them with:

```bash
git tag --sort=-creatordate | head
```

At configure time CMake runs `git describe --tags`:

- on a tagged commit the version is the tag, for example `62.0.1`;
- on a later commit it is the tag, the number of commits since, and the abbreviated commit name, for example `62.0.1-3-g1a2b3c4`;
- outside a Git clone it is `unknown`.

A version can also be given by hand with `-D TAG=<version>` when configuring.

## Version in the executable and outputs

The executable name, `swatplus-<version>-<compiler>-<system>_<arch>[-Rel|-Dbg]`, for example `swatplus-62.0.1-gnu-lin_x86_64-Rel`.

The start-up banner, printed to the screen and to `simulation.out`:

```
                   SWAT+
             Revision 62.0.1
      Soil & Water Assessment Tool
GNU (13.3.0), 2026-10-19 22:51:37, Linux
    Program reading . . . executing
```

The title line of every output file, which contains the build date and `Rev <year>.<version>`:

```
 demo                      SWAT+ 2026-10-19        MODULAR Rev 2026.62.0.1
```

## Building a tagged version

```bash
git checkout 62.0.1
cmake -B build -D CMAKE_BUILD_TYPE=Release
cmake --build build -j 8
```

A tag on GitHub can be moved after it is first published (the 62.0.1 tag was replaced on 19 October 2026). Run `git fetch --tags --force` before checking out a tag in an existing clone, so that the local tag matches the one on GitHub.

## Making a release

1. Merge the changes for the release into `main`.
2. Tag the merge commit and push the tag:

    ```bash
    git tag 62.0.2
    git push origin 62.0.2
    ```

3. Pushing a tag of the form `x.y` or `x.y.z` starts the release workflow, which builds the executables for Windows, Linux and macOS with gfortran and the Intel compilers and attaches the zipped executables to a GitHub release.
4. Write the release notes on the GitHub release page, and archive the release on Zenodo (see [Citing and license](../introduction/citing-and-license.md)).
5. Tag the documentation repository with the same version, which publishes a matching version of this site.

??? quote "Sources"

    - [`CMakeLists.txt`](https://github.com/swat-model/swatplus/blob/62.0.1/CMakeLists.txt): `if(NOT TAG)` block with `git describe --tags`, `SWATPLUS_EXE`, and `configure_file` of `src/main.f90.in` with `ISO`, `TODAY` and `YEAR` time stamps.
    - [`src/main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in): `prog = " SWAT+ @TODAY@        MODULAR Rev @YEAR@.@SWAT_VERSION@"` and the banner format. The generated `src/main.f90` is overwritten on every configure; edit `main.f90.in`.
    - [`doc/Tagging.md`](https://github.com/swat-model/swatplus/blob/62.0.1/doc/Tagging.md).
    - [`.github/workflows/build.yml`](https://github.com/swat-model/swatplus/blob/62.0.1/.github/workflows/build.yml): runs on tags matching `*.*` and `*.*.*`.
    - Banner and title line: output of the 62.0.1 `gnu-lin_x86_64` release executable.

---
title: Developer Guide
description: Building, testing, and contributing to the SWAT+ source code.
status: review
---

This section is for people working on the SWAT+ Fortran source: building from a clone, running the test suite, and submitting changes back to `swat-model/swatplus`.

If you only need to run a prebuilt SWAT+ executable, see [Install](../getting-started/install.md) instead.

## Pages

- [Build with CMake](build-cmake.md). The base out-of-source build flow that every platform uses. Covers configuration, compiler selection (gfortran, ifort, ifx), debug vs release, and installation.
- [Visual Studio on Windows](visual-studio-windows.md). End-to-end workflow for Visual Studio 2022 with the Intel oneAPI Fortran compiler. Cloning, configuring, debugging against an input dataset.
- [VS Code Codespaces](vscode-codespaces.md). Running a SWAT+ build and debug session inside a GitHub Codespaces virtual instance. Useful when you do not want to install a Fortran toolchain locally.
- [Testing](testing.md). The scenario regression test suite that compares model output against golden datasets in `data/`. Driven by `ctest`.
- [Tagging and releases](tagging-releases.md). How the build system pulls the version from `git describe` and projects it into `main.f90` and the executable name. Covers the release tag flow.
- [Coding conventions](coding-conventions.md). Fortran 90/95 style rules for SWAT+ source contributions: portability, readability, robustness, arrays, I/O, and obsolescent features to avoid.
- [Contributing](contributing.md). Fork, branch, pull request, and the CI checks that run on every PR.
- [Code of conduct](code-of-conduct.md). The Contributor Covenant, applied to the SWAT+ project community.

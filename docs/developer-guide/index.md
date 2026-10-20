---
title: Developer Guide
description: Building, testing, and contributing to the SWAT+ source code.
status: review
---

This section is for people working on the SWAT+ Fortran source: building from a clone, running the test suite, and submitting changes back to `swat-model/swatplus`.

If you only need to run a prebuilt SWAT+ executable, see [Install](../getting-started/install.md) instead.

## Pages

- [Build with CMake](build-cmake.md). The build used on every platform: configuration, compilers (gfortran, `ifx`, `ifort`), compiler options, debug and release builds.
- [Visual Studio on Windows](visual-studio-windows.md). Visual Studio 2022 with the Intel oneAPI Fortran compiler: cloning, configuring, and debugging against an input dataset.
- [VS Code Codespaces](vscode-codespaces.md). Running a SWAT+ build and debug session inside a GitHub Codespaces virtual instance. Useful when you do not want to install a Fortran toolchain locally.
- [Testing](testing.md). The scenario regression test that compares model output with reference outputs, and how to run it at 62.0.1.
- [Tagging and releases](tagging-releases.md). How the version number comes from the Git tag and reaches the executable, and how a release is made.
- [Coding conventions](coding-conventions.md). Fortran 90/95 style rules for SWAT+ source contributions: portability, readability, reliability, arrays, I/O, and obsolescent features to avoid.
- [Contributing](contributing.md). Reporting problems, pull requests, and contributing to this documentation.
- [Code of conduct](code-of-conduct.md). The Contributor Covenant, applied to the SWAT+ project community.

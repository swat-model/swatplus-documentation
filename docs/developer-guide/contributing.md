---
title: Contributing
description: How to report problems and contribute code or documentation to SWAT+.
status: review
verified_against:
  - swatplus/.github/workflows/test.yml
  - swatplus/.github/workflows/build.yml
  - swatplus/CODE_OF_CONDUCT.md
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Repositories

- Model source: [github.com/swat-model/swatplus](https://github.com/swat-model/swatplus), with [issues](https://github.com/swat-model/swatplus/issues), [pull requests](https://github.com/swat-model/swatplus/pulls) and [releases](https://github.com/swat-model/swatplus/releases).
- This documentation: [github.com/swat-model/swatplus-documentation](https://github.com/swat-model/swatplus-documentation).

Questions about using the model are best asked through the [SWAT support page](https://swat.tamu.edu/support/).

## Reporting a problem

Open an issue with:

- the SWAT+ version (shown in the banner at start-up and in the executable name);
- the operating system and, for your own builds, the compiler;
- a project that shows the problem, as small as possible (one of the `refdata` datasets with the changes that cause it is ideal);
- `simulation.out` and `diagnostics.out` from the run.

## Contributing code

1. Fork `swat-model/swatplus` and create a branch from `main` with a descriptive name (`fix-aquifer-init`, `add-soil-temp-output`).
2. Build and run your change on the reference datasets before opening a pull request. See [Build with CMake](build-cmake.md) and [Testing](testing.md).
3. Open a pull request against `main`. Describe what the change does and why, which datasets you ran and how their outputs changed, and any change to input or output files.
4. Answer review comments on the same branch.

Reviewers look for:

- a clean build with gfortran and the Intel compilers;
- unchanged outputs for parts of the model the change does not touch;
- defaults for new parameters that keep existing results when the parameter is not set;
- input file changes matched by a SWAT+ Editor change or a note on how to update existing projects;
- code that follows the [coding conventions](coding-conventions.md).

## Contributing to the documentation

The documentation is a MkDocs site in the `swatplus-documentation` repository. Each page states the SWAT+ commit it was checked against in its front matter (`verified_at_commit`), and every statement about model behaviour should come from the source at that commit. Page bodies are written for model users; source file names and variable names go in the collapsed Sources block at the end of each page (`??? quote "Sources"`).

To check a change locally:

```bash
pip install -r requirements.txt
mkdocs serve
```

The site is versioned with [mike](https://github.com/jimporter/mike). Pushing a tag to the documentation repository, named after the SWAT+ version the pages describe (for example `62.0.1`), publishes that version and moves the `latest` alias to it. Earlier versions stay available from the version selector.

??? quote "Sources"

    - CI: [`.github/workflows/test.yml`](https://github.com/swat-model/swatplus/blob/62.0.1/.github/workflows/test.yml) and [`.github/workflows/build.yml`](https://github.com/swat-model/swatplus/blob/62.0.1/.github/workflows/build.yml) in the source repository.
    - Documentation build and deployment: `mkdocs.yml`, `requirements.txt` and `.github/workflows/deploy.yml` in the documentation repository.

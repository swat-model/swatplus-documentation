---
title: Contributing
description: How to contribute code, bug reports, and documentation to SWAT+.
status: review
---

## Where work happens

- **Code**: https://github.com/swat-model/swatplus
- **Issues**: https://github.com/swat-model/swatplus/issues
- **Pull requests**: https://github.com/swat-model/swatplus/pulls
- **Release notes**: https://github.com/swat-model/swatplus/releases

## Reporting a bug

Open an issue with:

- the SWAT+ version (`swatplus -v` or the executable filename)
- the operating system and compiler
- a minimal project that reproduces the problem (or, if possible, a pointer to one of the reference datasets in `refdata/` plus the changes that trigger the bug)
- the contents of `simulation.out`, `diagnostics.out`, and `checker.out` from the failed run.

Bugs that affect water or mass balance, output formats, or input parsing are highest priority.

## Submitting a change

1. **Fork** `swat-model/swatplus` on GitHub.
2. **Branch** from `main`. Use a descriptive name (`fix-aquifer-init`, `add-soil-temp-output`).
3. **Build and test locally** before pushing. See [Build from source (CMake)](../developer-guide/build-cmake.md) and [Testing](../developer-guide/testing.md).
4. **Open a pull request** against `swat-model/swatplus:main`. The PR description should state:
   - what the change does
   - why it is needed (link an issue if there is one)
   - which reference datasets you ran and what changed in their outputs
   - any new input or output fields and how existing input files should be updated
5. **Address review comments**. Force-push is acceptable on your branch during review.

## What reviewers look for

- Code compiles with both gfortran and ifx (the CI matrix).
- Reference-dataset outputs are unchanged for unrelated runs (no regression).
- New parameters have defaults that preserve existing behaviour when not set.
- Input-file changes are accompanied by SWAT+ Editor changes or a migration note.
- Style follows [Coding conventions](../developer-guide/coding-conventions.md).

## CI

The repository runs GitHub Actions on every pull request. The matrix builds with multiple compilers and runs the scenario tests in `test/`. See `.github/workflows/` for the exact configuration. A red check blocks merging.

## Documentation changes

This documentation site lives at https://github.com/swat-model/swatplus-documentation. Documentation pull requests follow the same workflow as code. Every input-reference and output-reference page is verified against the SWAT+ Fortran source; see [`SOURCE-OF-TRUTH.md`](https://github.com/swat-model/swatplus-documentation/blob/main/wd/SOURCE-OF-TRUTH.md) for the procedure if you are touching one of those pages.

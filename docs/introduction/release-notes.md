---
title: Release notes
status: review
verified_against:
  - swatplus/CITATION.cff
  - swatplus/CMakeLists.txt
  - swatplus/doc/Tagging.md
  - swatplus/doc/Building.md
verified_at_commit: 8a1edd4a23915a2cac1cd90c788f0d521404700e
---

SWAT+ releases are tagged on the [GitHub releases page](https://github.com/swat-model/swatplus/releases). Each tag corresponds to a Zenodo DOI under the concept DOI `10.5281/zenodo.14983534`.

## Versioning

Releases are identified by a git tag. Tag names look like `61.0` or `61.1` for the current series, and earlier revisions in the reference data appear as `60.5.7`. The tag is read at configure time by `git describe --tags` (see `CMakeLists.txt`) and projected into the executable name and into the banner string in `main.f90`.

The executable name produced by CMake follows the pattern:

```
swatplus-<tag>-<compiler>-<arch>[-Rel|-Dbg]
```

where `<compiler>` is `gnu`, `ifo` (Intel `ifort`), or `ifx` (Intel LLVM), and `<arch>` is the host architecture. On Windows the executable has a `.exe` extension. This is defined in `CMakeLists.txt` as:

```cmake
set(SWATPLUS_EXE "swatplus-${SWAT_VERSION}-${FFC}-${AR}${TY}")
```

A build between tags resolves to a `git describe` string of the form `<tag>-<n>-g<sha>`, for example `61.1-1-g92b4413`. See [`doc/Tagging.md`](https://github.com/swat-model/swatplus/blob/main/doc/Tagging.md) in the source repository.

## Tagging policy

See [Tagging and releases](../developer-guide/tagging-releases.md) in the developer guide for the rules a contributor follows when cutting a new tag.

## Where to find what changed

For each release, the GitHub release page lists merged pull requests since the previous tag. The full commit history is available via:

```bash
git log <previous-tag>..<current-tag> --oneline
```

A change log curated for users (input file changes, output format changes, behaviour changes) is maintained in this section as releases are cut.

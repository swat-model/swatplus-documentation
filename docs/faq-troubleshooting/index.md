---
title: FAQ and Troubleshooting
description: Answers to common SWAT+ problems. Runtime errors, water balance issues, performance tips.
status: review
---

When a SWAT+ run does not produce what you expect, the first three files to read are `simulation.out`, `diagnostics.out`, and `checker.out`. Their format is described in [Checker and diagnostics](../output-reference/checker-diagnostics.md).

## Pages

- [Common runtime errors](../faq-troubleshooting/common-runtime-errors.md). The error strings the model writes to its diagnostic files, what they mean, and what to change.
- [Water balance and mass balance issues](../faq-troubleshooting/water-balance-issues.md). When `basin_wb_aa.txt` looks wrong: climate mapping, curve numbers, missing management, bad soils.
- [Performance tips](../faq-troubleshooting/performance-tips.md). Build flags, daily versus sub-daily routing, the cost of enabling many outputs.

## When in doubt

1. Confirm the executable matches the input format. Use the SWAT+ revision printed on the first line of `simulation.out`.
2. Read `diagnostics.out` end to end. Every line is a missing reference that SWAT+ replaced with a default or skipped.
3. Read `checker.out`. The per-HRU `zmx`, `sumfc`, `sumul`, `tiledrain` columns are the fastest way to spot a soil or option that did not load.
4. Confirm `success.fin` exists. If it does not, the run aborted.

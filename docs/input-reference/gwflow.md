---
title: gwflow (2D groundwater)
description: Input files of the cell-based groundwater module, which replaces the lumped aquifers when gwflow is set to 1 in codes.bsn.
status: review
verified_against:
  - src/basin_read_objs.f90
  - src/hyd_connect.f90
  - src/gwflow_chan_read.f90
  - src/gwflow_read.f90
  - src/gwflow_output.f90
  - src/gwflow_module.f90
  - src/gwflow_simulate.f90
  - src/gwflow_lateral.f90
  - src/gwflow_gwet.f90
  - src/gwflow_channel_exch.f90
  - src/gwflow_rech.f90
  - src/gwflow_tile.f90
  - src/gwflow_reservoir.f90
  - src/gwflow_wetland.f90
  - src/gwflow_phreatophyte.f90
  - src/gwflow_pond.f90
  - src/gwflow_solute.f90
  - src/gwflow_chem.f90
  - src/gwflow_heat.f90
  - src/wet_read_hyd.f90
  - src/basin_print_codes_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

gwflow is a cell-based groundwater model. When it is active it replaces the lumped aquifers, and [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu), [`initial.aqu`](../input-reference/aqu.md#initialaqu) and the aquifer connect file are not used. The aquifer is divided into cells, and each day SWAT+ solves a water balance for every cell with Darcy flow between neighbouring cells. Cells exchange water with channels and receive recharge from HRUs or landscape units. Optional processes add groundwater ET, groundwater flow into the soil profile, saturation excess flow, tile drainage, pumping, exchange with reservoirs, wetlands, floodplains and canals, recharge ponds, phreatophyte uptake, solute transport and heat transport.

The inputs are spread over a set of small files, most of them with the `.gw` extension, one file for each part of the model. The files are not listed in [`file.cio`](file-cio.md); SWAT+ looks for them by name in the run directory. Units are metres, days and square metres unless a column says otherwise.

## Activation

Set `gwflow` to 1 in [`codes.bsn`](codes-bsn.md). At start-up SWAT+ then looks for `chancell.gw`:

- If `chancell.gw` exists, gwflow is active. Unless [`object.cnt`](object-cnt.md) already gives a gwflow object count, SWAT+ counts the channel-cell rows in `chancell.gw`, uses that count as the number of gwflow objects, removes the aquifer objects from the object total, and reads the channel-cell connections from `gwflow.con`.
- If `chancell.gw` is missing or empty, `gwflow` is reset to 0 and the run uses the lumped aquifers.

When gwflow is active SWAT+ writes a log of what it read and which options it switched on or off to `gwflow_record`. Check this file first when a gwflow run does not behave as expected.

When the count comes from `chancell.gw`, SWAT+ skips three lines before it starts counting, while the file has two lines before the first data row. The first channel-cell row is therefore not counted and the count is one less than the number of rows. `chancell.gw` is then read for that many rows, so the last row of the file is not used. Giving the gwflow count in [`object.cnt`](../input-reference/object-cnt.md) avoids this.

## File overview

| File | Required | Read when | Purpose |
|------|----------|-----------|---------|
| `chancell.gw` | yes | always | Channel-cell links, streambed zone, depth zone and observation flag |
| `gwflow.con` | yes | always | Connect file for the channel-cell objects |
| `codes.gw` | yes | always | Grid size, process switches, time step and output switches |
| `zones.gw` | yes | always | Aquifer and streambed parameters by zone |
| `cells.gw` | yes | always | Properties and initial state of every cell |
| `cellcon.gw` | yes | always | Neighbours of every cell |
| `outputs.gw` | yes | always | Observation wells and output times |
| `hrucell.gw` | one of the two | `conn_type` 1, or 2 without `lsucell.gw` | HRU-cell overlaps for recharge |
| `lsucell.gw` | one of the two | `conn_type` 2, or 1 without `hrucell.gw` | Landscape unit-cell overlaps for recharge |
| `chan_depth.gw` | no | file exists | Daily channel water depth per depth zone |
| `pumpex.gw` | no | `pumpex` is 1 and file exists | Specified pumping from cells |
| `hru_pump.gw` | no | file exists | HRUs to report irrigation pumping for |
| `tile.gw` | no | `tile` is 1 and file exists | Tile drain parameters and tile cells |
| `rescell.gw` | no | `res` is 1 and file exists | Reservoir-cell links |
| `gwflow.wetland` | no | `wet` is 1 and file exists | Wetland bed thickness |
| `floodplain.gw` | no | `fp` is 1 and file exists | Floodplain-cell links |
| `gwflow_canal.con` | no | `canal` is 1 and file exists | Canal-cell links |
| `phreato.gw`, `phreato_cell.gw` | no | `phreato.gw` exists | Phreatophyte ET curve and cells |
| `tvheads.gw` | no | file exists | Time-varying heads for boundary cells |
| `solute.gw` | no | `solute` is 1 and file exists | Solute transport settings and solute parameters |
| `cell_sol.gw` | no | solute transport on and file exists | Initial solute concentration per cell |
| `minerals.gw` | no | solute transport on, salts simulated, file exists | Salt mineral fractions per cell |
| `ponds.gw`, `pond_cell.gw` | no | `ponds.gw` exists | Recharge ponds and their cells |
| `pond_div.gw` | no | ponds active and file exists | Daily diversion into each pond |
| `sw_group.gw` | no | file exists | Groups of channel cells for exchange output |
| `transit.gw` | no | structured grid and file exists | Cells for transit-time output |

When a switch in `codes.gw` is on and its file is missing, SWAT+ notes it in `gwflow_record` and the process is not simulated. For tile drainage, floodplain exchange and solute transport the switch is also turned off for the rest of the run.

## Format conventions

- Values are separated by spaces. Column widths do not matter.
- Line 1 of every file is a title line and is skipped. Most tables have a column header on line 2, also skipped, and data from line 3. Files with a different layout are described in the section for that file.
- Cell numbers run from 1 to `ncell`, in the order of `cells.gw`, and every file that names a cell uses these numbers.
- Channel numbers are the numbers of the channels in the channel connect file ([`chandeg.con`](../input-reference/con.md)). Reservoir numbers follow the reservoir connect file.
- In `cells.gw` and `zones.gw`, an optional value may be given as `null`, which means it is not set.

## codes.gw

Grid size, process switches and output switches. Line 1 is a title. Line 2 is a row of key names and line 3 is a row of values, one value under each key. SWAT+ pairs keys and values by position and recognises the keys by name, so the order of the columns does not matter and a missing key keeps its default (0, or empty for `grid_type`).

| Key | Units | Description |
|-----|-------|-------------|
| `grid_type` | - | `structured` (regular grid) or `unstructured`. Both use the same cell numbering. |
| `ncell` | - | Number of cells. `cells.gw` and `cellcon.gw` must have this many rows. |
| `cell_size` | m | Cell size of a structured grid. Read but not used; cell areas come from `cells.gw`. |
| `n_rows`, `n_cols` | - | Rows and columns of a structured grid. Used only by the structured-grid sections of `tile.gw` and `minerals.gw`. |
| `bc_type` | - | Default boundary condition for boundary cells: 1 = specified head, 2 = no flow. A cell can override it in `cells.gw`. |
| `conn_type` | - | How recharge reaches the cells: 1 = from HRUs (`hrucell.gw`), 2 = from landscape units (`lsucell.gw`). Any other value stops the run. |
| `gw_soil` | 0/1 | Groundwater transfer into the soil profile when the water table rises into it. Only with HRU connection. |
| `satx` | 0/1 | Saturation excess flow: groundwater above the ground surface goes to the channel nearest to the cell. |
| `pumpex` | 0/1 | Specified pumping from `pumpex.gw`. |
| `tile` | 0/1 | Tile drainage from `tile.gw`. |
| `res` | 0/1 | Exchange with reservoirs from `rescell.gw`. |
| `wet` | 0/1 | Exchange with wetlands. Only with HRU connection. |
| `fp` | 0/1 | Exchange with floodplains from `floodplain.gw`. |
| `canal` | 0/1 | Seepage from canals in `gwflow_canal.con`. |
| `solute` | 0/1 | Solute transport from `solute.gw`. |
| `heat` | 0/1 | Heat transport. |
| `time_step` | day | Flow time step. The day is split into `int(1/time_step)` steps, so use 1 or a fraction of a day such as 0.5. |
| `write_day`, `write_mon`, `write_yr`, `write_aa` | 0/1 | Write the gwflow water balance files for each interval. |
| `river_thresh` | m | Distance subtracted from every channel-bed elevation in `chancell.gw` before the channel exchange is calculated. 0 uses the elevations as given. |

With LSU connection, SWAT+ turns `gw_soil` and `wet` off and says so in `gwflow_record`.

### Output switches in print.prt

The `write_*` keys are defaults. [`print.prt`](print-prt.md) can list gwflow rows, and a row that is present replaces the corresponding setting before any gwflow output file is opened:

| print.prt row | Controls | Without the row |
|---------------|----------|-----------------|
| `gwflow_wb` | Water balance files, by interval (replaces `write_day` to `write_aa`) | `write_*` keys of `codes.gw` |
| `gwflow_obs` | Observation well files, by interval | all four intervals written |
| `gwflow_pump` | HRU irrigation pumping output (on if any interval is `y`) | on |
| `gwflow_flux` | Canal, pond, tile, channel-group and channel-observation output (on if the daily or yearly column is `y`) | on |
| `gwflow_heat` | Heat balance files: daily, yearly and average annual columns | same intervals as the water balance |
| `gwflow_solute` | Solute balance files, by interval | same intervals as the water balance |

The daily channel hydrograph separation file `gwflow_chan_hydsep_day.txt` is written when daily water balance output is on. The files are described in the [gwflow output reference](../output-reference/gwflow.md).

## zones.gw

Aquifer and streambed parameters, one row per zone. Line 1 is a title and line 2 a column header. The zone number of a row is its position in the file (the first data row is zone 1); the `zone_id` column is not read.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `zone_id` | - | Zone number. Not read; the row position decides. |
| 2 | `aquifer_K` | m/day | Horizontal hydraulic conductivity of the aquifer. |
| 3 | `aquifer_Sy` | fraction | Specific yield of the aquifer. |
| 4 | `streambed_K` | m/day | Hydraulic conductivity of the streambed, for channel cells that use this zone. |
| 5 | `streambed_thick` | m | Streambed thickness, for channel cells that use this zone. |
| 6 | `thermal_K` | J/day/m/°C | Thermal conductivity of the aquifer, used by heat transport. Optional; `null` or missing means 0. |

Cells name a zone for conductivity and a zone for specific yield in `cells.gw`. Channel cells name a zone for streambed properties in `chancell.gw`.

## cells.gw

One row per cell, in cell order. Line 1 is a title and line 2 a column header. Row $i$ must have `id` equal to $i$, or the run stops with a message in `gwflow_record`. The first 14 columns are required. Columns 15 to 23 are optional: a row can end after column 14, and `null` in any of them means the value is not set.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Cell number, 1 to `ncell`, equal to the row number. |
| 2 | `name` | - | Cell name, used in output files. |
| 3 | `gis_id` | - | GIS identifier of the cell, written to output files. |
| 4 | `status` | - | 0 = inactive, 1 = active, 2 = boundary. Boundary cells keep their head and are treated by `bc_type`. |
| 5 | `elev` | m | Ground surface elevation. |
| 6 | `thck` | m | Aquifer thickness. The aquifer bottom is `elev - thck`. |
| 7 | `K_zone` | - | Zone (row of `zones.gw`) for hydraulic conductivity. Also used for `thermal_K`. |
| 8 | `Sy_zone` | - | Zone (row of `zones.gw`) for specific yield. |
| 9 | `delay` | day | Recharge delay through the unsaturated zone. |
| 10 | `exdp` | m | Extinction depth for groundwater ET, measured down from the ground surface. 0 turns groundwater ET off for the cell. |
| 11 | `init` | m | Initial groundwater head (elevation). A value below the aquifer bottom is raised to the bottom. |
| 12 | `x` | m | x coordinate of the cell centre. |
| 13 | `y` | m | y coordinate of the cell centre. |
| 14 | `area` | m² | Cell area. |
| 15 | `strK` | m/day | Streambed conductivity for this cell, in place of the zone value. |
| 16 | `strthick` | m | Streambed thickness for this cell, in place of the zone value. |
| 17 | `bc_type` | - | Boundary condition for this cell, in place of the default in `codes.gw`. |
| 18 | `tile_depth` | m | Tile depth for this cell, in place of the value in `tile.gw`. |
| 19 | `tile_area` | m² | Tile drainage area for this cell, in place of the value in `tile.gw`. |
| 20 | `tile_K` | 1/day | Tile conductance for this cell, in place of the value in `tile.gw`. |
| 21 | `row` | - | Grid row of a structured cell (0 for unstructured). Written to output only. |
| 22 | `col` | - | Grid column of a structured cell (0 for unstructured). Written to output only. |
| 23 | `init_temp` | °C | Initial groundwater temperature, used by heat transport. |

The x and y coordinates are used to find, for each cell, the nearest channel cell (for saturation excess flow and tile drainage) and, for each boundary cell, the nearest active cell, which receives the recharge that falls on the boundary cell.

## cellcon.gw

The neighbours of every cell, which define where lateral flow can happen. Line 1 is a title and line 2 a column header. One row per cell, in cell order; the first value must equal the row number.

| # | Column | Description |
|---|--------|-------------|
| 1 | `cell_id` | Cell number, equal to the row number. |
| 2 | `neighbor_tot` | Number of neighbours. |
| 3+ | `neighbor_ids` | `neighbor_tot` cell numbers. |

Flow between a cell and a neighbour uses Darcy's law with the harmonic mean of the two conductivities. The face width is the square root of the smaller of the two cell areas. No flow passes to an inactive neighbour or to a boundary neighbour with `bc_type` 2.

## outputs.gw

Output settings, one per row. Line 1 is a title and line 2 a column header. Each row starts with a category and a value; anything after the value (SWAT+ Editor writes a note) is ignored. Rows can be in any order.

| `category` | `value` | Effect |
|------------|---------|--------|
| `observation_cell` | cell number | Adds an observation well. Head, water table depth, temperature, nitrate and phosphorus at each well are written to `gwflow_obs_*.txt`. One row per well. |
| `head_output_time` | date as `YYYYDDD` | A date for a full head output. In 62.0.1 these dates are read but produce no output. |
| `detail_debug_cell` | cell number or 0 | Read but not used. |

## chancell.gw

The cells crossed by channels, one row per channel-cell pair. Line 1 is a title and line 2 a column header. A cell crossed by two channels appears on two rows.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `cell_id` | - | Cell crossed by the channel. |
| 2 | `elev_m` | m | Channel bed elevation in the cell. |
| 3 | `channel` | - | Channel number in [`chandeg.con`](../input-reference/con.md). |
| 4 | `riv_length_m` | m | Length of the channel within the cell. |
| 5 | `zone` | - | Zone (row of `zones.gw`) for streambed conductivity and thickness. |
| 6 | `dep_zone` | - | Depth zone: column of `chan_depth.gw` that gives the daily water depth. Optional, default 0. |
| 7 | `obs` | 0/1 | 1 writes daily channel exchange for this cell to `gwflow_chan_obs_flow_day.txt`. Optional, default 0. |

### Channel exchange

Exchange is calculated each day for every active channel cell with Darcy's law across the streambed. With bed elevation $z_b$ (`elev_m` minus `river_thresh`), water depth $d$, stage $z_s = z_b + d$, groundwater head $h$, streambed conductivity $K_b$ and thickness $m_b$, and flow area $A = w\,L$ (channel width times `riv_length_m`):

$$Q = \frac{K_b}{m_b}\,A \times \begin{cases} d & h < z_b \\ z_s - h & z_b < h < z_s \\ -(h - z_s) & h > z_s \end{cases}$$

A positive $Q$ (m³/day) is seepage from the channel into the aquifer and is limited to the water in the channel. A negative $Q$ is groundwater discharge to the channel and is limited to the water stored in the cell. The width $w$ is the channel width from the channel data. The depth $d$ is the channel depth from the channel data, unless `chan_depth.gw` is present, in which case it is the day's depth for the cell's depth zone.

## gwflow.con

The connect file for the channel-cell objects. It has the usual connect-file layout (title line, header line, then one row per object); see [connect files](con.md). Each row is one channel cell, with the cell number in the `CELL` column and one outflow to the channel (`sdc`, the channel number, `tot`, 1.0).

## hrucell.gw

Overlaps between HRUs and cells, used to pass recharge from HRUs to cells and, with `gw_soil`, groundwater back into the soil. Line 1 is a title and line 2 a column header.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `hru` | - | HRU number. |
| 2 | `area_m2` | m² | Total area of the HRU. |
| 3 | `cell_id` | - | Cell that overlaps the HRU. |
| 4 | `overlap_m2` | m² | Area of the overlap. |

Rows must be grouped by HRU and the HRUs must be in increasing order, since SWAT+ reads the rows for HRU 1, then HRU 2, and so on. A row with an HRU number outside 1 to the number of HRUs is skipped. Each HRU's recharge is split between its cells by `overlap_m2 / area_m2`.

The HRU's recharge delay is taken from the `delay` of its cells in `cells.gw`. When an HRU overlaps several cells, the delay of the last cell listed for that HRU is used.

## lsucell.gw

Overlaps between landscape units and cells, used in place of `hrucell.gw` with LSU connection. The layout differs from the other tables:

| Line | Content |
|------|---------|
| 1 | Title |
| 2 | Number of landscape units in the model |
| 3 | Number $n$ of landscape units connected to cells |
| next $n$ lines | One landscape unit number per line |
| next 2 lines | Headers, skipped |
| rest | One row per overlap: landscape unit number, landscape unit area (m²), cell number, overlap area (m²) |

The overlap rows must be grouped by landscape unit in increasing order. With LSU connection every HRU uses a recharge delay based on the mean `delay` of all cells.

SWAT+ Editor writes `lsucell.gw` as a title followed by rows of cell, landscape unit and area, which is a different layout from the one the model reads.

## chan_depth.gw

Daily channel water depth for each depth zone. Line 1 is a title and line 2 a column header. Then one row per simulated day, in order: day of year, year, and one depth (m) for each depth zone 1 to $N$, where $N$ is the largest `dep_zone` in `chancell.gw`. One row is read per day in sequence; the day and year values are not checked.

## pumpex.gw

Specified pumping from cells, read when `pumpex` is 1. Line 1 is a title and line 2 a column header. One row per pumping period.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Label, not used. |
| 2 | `cell_id` | - | Pumped cell. |
| 3 | `rate` | m³/day | Pumping rate during the period. |
| 4 | `yr_start` | year | First year of the period. |
| 5 | `dy_start` | day of year | First day of the period. |
| 6 | `yr_end` | year | Last year of the period. |
| 7 | `dy_end` | day of year | Last day of the period. |

Consecutive rows with the same `cell_id` form one pump with several periods (up to 1000). Rows for one cell that are not next to each other create separate pumps. Each date is converted to a day count from the start of the simulation as $(\mathrm{year} - \mathrm{first\ year}) \times 365 + \mathrm{day}$, without leap days. A year before the first simulated year is counted as day 1.

## hru_pump.gw

HRUs whose groundwater irrigation pumping is written each day to `gwflow_cell_wb_ppag_obs_day.txt`. Line 1 is a title, line 2 is the number of HRUs, and then one HRU number per line.

## tile.gw

Tile drainage, read when `tile` is 1. Each value is on a separate line:

| Line | Content |
|------|---------|
| 1 | Title |
| 2 | Tile depth below the ground surface (m), for all cells |
| 3 | Tile drainage area (m²), for all cells |
| 4 | Tile conductance (1/day), for all cells |
| 5 | Group flag: 1 if tile cell groups follow, 0 if not |
| groups | If the flag is 1: the number of groups, then for each group a name line, the number of cells, and one cell number per line |
| next | Header line, skipped |
| rest | Tile flag per cell (1 = tile drained, 0 = not). Unstructured grid: one value per line for all `ncell` cells. Structured grid: `n_rows` lines of `n_cols` values. |

Columns 18 to 20 of `cells.gw` replace the depth, area and conductance for single cells. Each day, an active tile cell whose head $h$ is above the tile elevation $z_t$ (`elev - tile_depth`) drains

$$Q_{tile} = A_{tile}\,K_{tile}\,(h - z_t)$$

in m³/day to the channel nearest to the cell. With groups, the daily tile flow of each group is written to `gwflow_tile_group_day.txt`.

The structured-grid form of the tile flags depends on grid arrays that 62.0.1 does not set up, so give the tile flags in the unstructured form. SWAT+ Editor writes the three tile values on one line followed by a list of tile cells, which is a different layout from the one the model reads.

## rescell.gw

Reservoir-cell links, read when `res` is 1.

| Line | Content |
|------|---------|
| 1, 2 | Title and a second line, skipped |
| 3 | Reservoir bed thickness (m), for all reservoirs |
| 4 | Reservoir bed conductivity (m/day), for all reservoirs |
| 5 | Number of rows that follow |
| 6 | Header, skipped |
| rest | `cell_id`, `res_id`, `res_stage` |

`res_id` is the reservoir number; a row with 0 is skipped. Exchange uses the ground elevation of the cell from `cells.gw` as the reservoir bed elevation. `res_stage` is read but not used.

## gwflow.wetland

Wetland bed thickness, read when `wet` is 1 and HRUs are connected to cells. Lines 1 and 2 are skipped. Each later row has a wetland name and a bed thickness (m). The digits in the name give the HRU number, so `wet019` sets the bed thickness of the wetland in HRU 19. Wetlands not listed use 0.25 m.

SWAT+ Editor writes this information to a file named `wetland.gw`, which the model does not read, so wetlands then use 0.25 m.

## floodplain.gw

Floodplain-cell links, read when `fp` is 1. Line 1 is a title, line 2 the number of rows, line 3 a header, then one row per cell: cell number, channel number, floodplain bed conductivity (m/day) and area of the cell inside the floodplain (m²). The area is limited to the cell area.

## gwflow_canal.con

Canal-cell links, read when `canal` is 1. The canal dimensions, bed properties and active days come from the canal records in [`water_canal.wal`](water-allocation.md). Line 1 is a title. Each later row describes one canal:

```
canal_id  n  cell_1 length_1 elev_1  cell_2 length_2 elev_2  ...
```

with `n` triplets of cell number, canal length in the cell (m) and canal bed elevation in the cell (m). A canal with a diversion source is treated as a diversion canal. A canal with no diversion and a start day above 0 is treated as a canal fed from outside the model. Any other canal is linked to a channel through water allocation.

## phreato.gw and phreato_cell.gw

Groundwater uptake by phreatophytes. Both files are needed when `phreato.gw` exists; there is no switch in `codes.gw`.

`phreato.gw` is the curve of uptake rate against water table depth. Line 1 is a title and line 2 a header, then one point per row: depth to the water table (m) and ET rate (m/day), in order of increasing depth.

`phreato_cell.gw` lists the cells with phreatophytes. Line 1 is a title and line 2 a header, then one row per cell: cell number and area covered by phreatophytes (m²).

## tvheads.gw

Line 1 is a title and line 2 a header. Each later row gives a cell number and one head per simulated year. In 62.0.1 the file is read but the heads are not applied, so boundary cells keep their initial heads.

## solute.gw

Solute transport settings, read when `solute` is 1.

| Line | Content |
|------|---------|
| 1, 2 | Title and a second line, skipped |
| 3 | Number of transport time steps per flow time step |
| 4 | Longitudinal dispersivity (m) |
| 5 | Skipped (SWAT+ Editor writes the number of solutes here) |
| rest | One row per solute: name, retardation factor, reaction rate constant (1/day), concentration in canal water from outside the model (g/m³) |

The solutes and their order are set by the model: nitrate and phosphorus first, then the salt ions and then the other constituents listed in [`constituents.cs`](cs.md). The file must have one row per solute in that order; the name column is not checked. Further values on a row are ignored. SWAT+ Editor writes an initial concentration as a fifth value, which the model does not read; initial values come from `cell_sol.gw`.

The retardation factor divides the transport time step, so 1 means no sorption. The reaction term adds concentration × groundwater volume × rate constant (g/day) to the cell, so a negative rate constant gives first-order decay.

When constituents are simulated, SWAT+ also tries to read per-cell reaction groups and shale maps after `cell_sol.gw`. In 62.0.1 no file is open at that point, so gwflow solute transport cannot run together with the constituent module.

## cell_sol.gw

Initial solute concentration in every cell. Line 1 is a title and line 2 a header, then one row per cell in cell order: cell number and one concentration (g/m³) per solute, in the order of `solute.gw`. Without this file all concentrations start at 0.

## minerals.gw

Salt mineral fractions per cell, read when solute transport is on, salt ions are simulated and the file exists. Line 1 is a title, line 2 the number of minerals, line 3 a header, then for an unstructured grid one row per cell with one fraction per mineral. The structured-grid form is read but the values are not stored. SWAT+ Editor does not write this file.

## ponds.gw, pond_cell.gw and pond_div.gw

Recharge ponds. They are active when `ponds.gw` exists, and `pond_cell.gw` must then exist too.

`ponds.gw` has a title line, a header line and one row per pond:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `pond_id` | - | Pond number, matched in `pond_cell.gw`. |
| 2 | `area` | m² | Pond area. |
| 3 | `chan` | - | Channel that supplies the diverted water. 0 if none. |
| 4 | `canal` | - | Canal that supplies the diverted water, used when `chan` is 0. 0 if none. |
| 5 | `unl` | 0/1 | 1 = the diverted water comes from outside the model, used when `chan` and `canal` are 0. |
| 6 | `bed_k` | m/day | Conductivity of the pond bed. |
| 7 | `wsta` | - | Weather station for rainfall and evaporation. |
| 8 | `evap_co` | - | Evaporation coefficient. Daily evaporation is `evap_co` × potential ET of the station × pond area. |
| 9 | `start_yr` | year | Year the pond starts operating. |
| 10 | `start_mo` | month | Month the pond starts operating. |
| 11 | `start_day` | day | Day of the month the pond starts operating. |
| 12+ | `unl_conc_1` ... | g/m³ | Concentration of each solute in water from outside the model (none when solute transport is off). |

The start date is converted to a day count with 365-day years and fixed month lengths; a start year before the first simulated year means day 1.

`pond_cell.gw` has a title line, a header line and one row per pond-cell connection: pond number, cell number and connection area (m²). The rows for a pond give its cells.

`pond_div.gw` has a title line, a header line and one row per simulated day: year, month, day and the volume diverted into each pond that day (m³), in the order of `ponds.gw`. One row is read per day in sequence, so the file needs a row for every simulated day; the dates are not checked. Without the file, no water is diverted into the ponds.

## sw_group.gw

Groups of channel cells whose daily channel exchange is summed and written to `gwflow_gwsw_group_day.txt`. Line 1 is a title and line 2 a header. Each later row gives a group number, the number of cells $n$ in the group and $n$ cell numbers.

## transit.gw

Cells for groundwater transit-time output. Read only for a structured grid. Line 1 is a title, line 2 a header, line 3 the number of cells, then one cell number per line. SWAT+ Editor does not write this file.

## Example

Start of a set of inputs for a structured grid of 1454 cells, with illustrative values.

`codes.gw` (abbreviated):

```
codes.gw: written by SWAT+ editor
     grid_type         ncell     cell_size        n_rows        n_cols   ...      time_step     write_aa  river_thresh
    structured          1454       5000.00            52            53   ...           1.00            1          5.00
```

`zones.gw`:

```
zones.gw: written by SWAT+ editor
   zone_id     aquifer_K    aquifer_Sy   streambed_K streambed_thick     thermal_K
         1       0.50000       0.20000       0.00500         0.50000       0.00000
         2       2.00000       0.20000       0.00500         0.50000       0.00000
```

`cells.gw` (first row, abbreviated):

```
 id  name      gis_id  status   elev   thck K_zone Sy_zone  delay  exdp   init ...  row  col init_temp
  1  cell0001       1       2 395.00  34.99      1       1   0.00  1.00 390.00 ...   52    1      null
```

Cell 1 is a boundary cell. Its aquifer bottom is at 395.00 - 34.99 = 360.01 m and it starts with a head of 390.00 m.

`chancell.gw`:

```
chancell.gw: written by SWAT+ editor
 cell_id   elev_m  channel  riv_length_m  zone  dep_zone  obs
      42   326.00       66       1853.55     1         0    1
      43   324.50       66        912.10     1         0    0
```

Channel 66 crosses cells 42 and 43, both with streambed properties from zone 1. With `river_thresh` at 5.00, the exchange at cell 42 uses a bed elevation of 321.00 m. Daily exchange at cell 42 is written to the channel observation output.

## Related files

- [`codes.bsn`](codes-bsn.md): `gwflow` switches the module on.
- [`object.cnt`](object-cnt.md): can give the number of gwflow objects directly.
- [`print.prt`](print-prt.md): gwflow output rows.
- [`hru-data.hru`](hru.md) and [connect files](con.md): the HRUs, landscape units, channels and reservoirs that cells connect to.
- [`water_canal.wal`](water-allocation.md): canal data used by canal seepage.
- [`constituents.cs`](cs.md) and [salt inputs](salt.md): the salts and constituents added to the gwflow solutes.
- [gwflow outputs](../output-reference/gwflow.md).

??? quote "Sources"

    - Activation and object count: [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90)
    - Readers: [`gwflow_chan_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_chan_read.f90) (`chancell.gw`, `chan_depth.gw` header) and [`gwflow_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_read.f90) (all other `.gw` files and `gwflow_canal.con`), both called from [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - Wetland bed thickness: [`wet_read_hyd.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wet_read_hyd.f90)
    - print.prt rows: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90); override logic in `gwflow_read`; output files opened in `gwflow_output_init` in [`gwflow_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_output.f90)
    - Variables: [`gwflow_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_module.f90)
    - Daily solution: [`gwflow_simulate.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_simulate.f90), [`gwflow_lateral.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_lateral.f90), [`gwflow_rech.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_rech.f90), [`gwflow_gwet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_gwet.f90), [`gwflow_channel_exch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_channel_exch.f90), [`gwflow_tile.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_tile.f90), [`gwflow_reservoir.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_reservoir.f90), [`gwflow_wetland.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_wetland.f90), [`gwflow_floodplain.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_floodplain.f90), [`gwflow_canal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_canal.f90), [`gwflow_phreatophyte.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_phreatophyte.f90), [`gwflow_pond.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_pond.f90), [`gwflow_solute.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_solute.f90), [`gwflow_chem.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_chem.f90), [`gwflow_heat.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_heat.f90)

    | File and column | Fortran variable |
    |-----------------|------------------|
    | `codes.gw` `n_rows`, `n_cols` | `grid_nrow`, `grid_ncol` |
    | `codes.gw` `bc_type` | `bc_type_int`, copied to `bc_type_array` |
    | `codes.gw` `gw_soil`, `satx`, `pumpex`, `tile`, `res`, `wet`, `fp`, `canal`, `solute`, `heat` | `gw_soil_flag`, `gw_satx_flag`, `gw_pumpex_flag`, `gw_tile_flag`, `gw_res_flag`, `gw_wet_flag`, `gw_fp_flag`, `gw_canal_flag`, `gw_solute_flag`, `gw_heat_flag` |
    | `codes.gw` `time_step` | `gw_time_step` |
    | `codes.gw` `write_day` to `write_aa` | `gwflag_day`, `gwflag_mon`, `gwflag_yr`, `gwflag_aa` |
    | `codes.gw` `river_thresh` | `gw_bed_change` |
    | `zones.gw` columns 2 to 6 | `zones_aquK`, `zones_aquSy`, `zones_strK`, `zones_strbed`, `zones_Kt` |
    | `cells.gw` `status`, `elev`, `thck`, `exdp`, `init`, `x`, `y`, `area` | `gw_state%stat`, `%elev`, `%thck`, `%exdp`, `%init`, `%xcrd`, `%ycrd`, `%area` |
    | `cells.gw` `delay` | `delay`, converted to `gw_delay = exp(-1/delay)` per HRU |
    | `cells.gw` columns 15 to 20 | `cell_strK_over`, `cell_strthick_over`, `bc_type_array`, `cell_tile_depth_over`, `cell_tile_area_over`, `cell_tile_K_over` |
    | `cellcon.gw` | `gw_state%ncon`, `cell_con%cell_id` |
    | `outputs.gw` | `gw_obs_cells`, `gw_output_yr` and `gw_output_day`, `gw_cell_obs_ss` |
    | `chancell.gw` | `gw_chan_id`, `gw_chan_elev`, `gw_chan_chan`, `gw_chan_len`, `gw_chan_zone`, `gw_chan_dpzn`, `gw_chan_obs` |
    | `tile.gw` lines 2 to 5 | `gw_tile_depth`, `gw_tile_drain_area`, `gw_tile_K`, `gw_tile_group_flag` |
    | `rescell.gw` lines 3 and 4 | `res_thick`, `res_K` |
    | `solute.gw` | `num_ts_transport`, `gw_long_disp`, `gwsol_sorb`, `gwsol_rctn`, `canal_out_conc` |
    | `ponds.gw` | `gw_pond_info` |

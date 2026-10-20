---
title: water allocation
description: Places of use, points of diversion and points of return, and the treatment, use, tower, canal, pipe and outside-basin files that make up the water allocation network.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/main.f90.in
  - src/water_allocation_module.f90
  - src/water_allocation_read.f90
  - src/water_hru_irr_read.f90
  - src/wallo_wtps_wuses.f90
  - src/water_treatment_read.f90
  - src/water_use_read.f90
  - src/water_osrc_read.f90
  - src/water_orcv_read.f90
  - src/water_tower_read.f90
  - src/water_pipe_read.f90
  - src/water_canal_read.f90
  - src/om_treat_read.f90
  - src/om_use_read.f90
  - src/om_osrc_read.f90
  - src/time_control.f90
  - src/wallo_start_day.f90
  - src/wallo_control.f90
  - src/wallo_withdraw.f90
  - src/wallo_pou_deliv.f90
  - src/wallo_return.f90
  - src/wallo_treatment.f90
  - src/wallo_use.f90
  - src/wallo_canal.f90
  - src/wallo_transfer.f90
  - src/sd_channel_control3.f90
  - src/res_control.f90
  - src/aqu_1d_control.f90
  - src/hru_control.f90
  - src/actions.f90
  - src/conditions.f90
  - src/hydrograph_module.f90
  - src/header_water_allocation.f90
  - src/gwflow_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

!!! warning
    In revision 62.0.1 the water allocation calculation follows these inputs only for a network with a single place of use, other than an irrigation district, whose POD lines are listed in POD-number order. Other layouts can take the wrong amounts or stop the run, and several columns are read but have no effect. See [Limitations in 62.0.1](#limitations-in-6201) before setting up a network.

## Purpose

Water allocation moves water from where it is taken to where it is used: irrigation districts, towns, industry, treatment plants, reservoirs, canals and places outside the basin. Revision 62.0.1 describes the network with three kinds of object:

- A **place of use** (POU) is where water goes: an irrigation district, a water treatment plant, a water use, a water tower, a canal, a channel, a reservoir, an aquifer or a receiver outside the basin. Each POU has a daily demand (its duty).
- A **point of diversion** (POD) is where water is taken: a channel, reservoir, aquifer, canal, water tower, outside-basin source or an unlimited source. A POD can supply several POUs, and a POU can draw on several PODs.
- A **point of return** (POR) is where a POU sends water after it has been used or treated: back to a channel, reservoir or aquifer, on to another treatment plant or use, or out of the basin.

Two files define the network: `place_of_use.wro` lists every POU with its PODs and PORs, and `point_of_diver.wro` lists every POD with the POUs it serves. The `.wal` files describe the objects between them: treatment plants, water uses, water towers, canals, pipes, irrigation districts and outside-basin sources.

This structure replaces the `water_allocation.wro` transfer file of earlier revisions, whose columns in earlier documentation (`rule_typ`, `srcs`, `ob_typ`, `withdr`, `limit_mon`, `cha_ob`, `rcv_ob`, `rcv_num`) have no counterpart in 62.0.1. `water_allocation.wro`, `element.wro` and `water_rights.wro` are no longer read.

## Files and activation

| File | Name set by | Contents |
|------|-------------|----------|
| `place_of_use.wro` | `water_rights` line of [`file.cio`](../input-reference/file-cio.md), first name | Places of use, with their PODs and PORs |
| `point_of_diver.wro` | `water_rights` line of [`file.cio`](../input-reference/file-cio.md), second name | Points of diversion and the POUs each serves |
| `water_hru_irr.wal` | fixed name | HRUs in each irrigation district |
| `wtps_wuses.wal` | fixed name | Numbers of treatment plants and water uses |
| `water_treat.wal` | fixed name | Water treatment plants |
| `water_use.wal` | fixed name | Water uses (domestic, industrial, commercial) |
| `outside_src.wal` | fixed name | Sources outside the basin |
| `om_treat.wal`, `om_use.wal`, `om_osrc.wal` | fixed names | Water quality sets for treated water, used water and outside sources |
| `water_tower.wal` | fixed name | Water towers (storage) |
| `water_canal.wal` | fixed name | Canals |
| `water_pipe.wal` | fixed name | Pipes |
| `outside_rcv.wal` | fixed name | Receivers outside the basin (not read) |

The `water_rights` line of [`file.cio`](file-cio.md) now takes two file names, the POU file and the POD file, with defaults `place_of_use.wro` and `point_of_diver.wro`. A [`file.cio`](../input-reference/file-cio.md) written for an earlier revision has `water_allocation.wro element.wro water_rights.wro` on that line, and SWAT+ 62.0.1 then reads `water_allocation.wro` as the POU file and `element.wro` as the POD file. Update the line before running an older project; [older file.cio files](file-cio.md#older-filecio-files) explains how the old line is read.

Water allocation runs when the POU file has at least one place of use. If a `.wro` file or `wtps_wuses.wal` is missing, or the line in [`file.cio`](../input-reference/file-cio.md) says `null`, SWAT+ creates an empty file of that name in the run folder (a file called `null` in the second case) and reads nothing from it. The empty file does no harm.

All files have a title on line 1. The `.wro` files and most `.wal` files then give the number of records on line 2 and a column header on line 3. Records are read as free-format values separated by spaces, by position, so the header text is not checked.

## Daily sequence

Each day, before any object is simulated:

1. The day's POD and POR totals are set to zero.
2. Outside-basin source PODs, water tower PODs and unlimited PODs give water to their POUs.
3. POUs with no PODs (a treatment plant or use fed only by returns from other POUs) treat or use the water they have stored and pass it to their PORs.
4. The demand of every POU is set, from `rate_max` or from its decision table, and split among its PODs by `frac` (or by a decision table).

During the day, natural PODs give water when their object is simulated: a channel POD after the channel is routed (the water comes out of the channel's outflow for the day), a reservoir POD after the day's inflow is added, an aquifer POD after recharge is added. A canal POD gives water when the canal receives water.

Each time a POD gives water, every POU whose PODs have all given water for the day receives it. Water delivered to a POU that is a treatment plant, use or canal is processed at once (treated, used, or routed through the canal), and the POU's outflow is passed to its PORs.

Because step 2 runs before step 4, outside-source, water tower and unlimited PODs work with the previous day's demand, and with zero demand on the first day.

## place_of_use.wro

Line 1 is a title, line 2 the number of POUs, line 3 a header. Each POU then takes one line, followed by one line for each of its PODs and one line for each of its PORs.

### POU line

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `num` | - | POU number, 1 to the number on line 2. The record is stored under this number. |
| 2 | `name` | - | POU name. |
| 3 | `typ` | - | POU type, from the table below. |
| 4 | `typ_num` | - | Number of the object of that type that receives the water (for example the channel number, or the record number in `water_treat.wal`). For `irr`, the record number in `water_hru_irr.wal`. |
| 5 | `pods` | - | Number of POD lines that follow. 0 for a POU fed only by returns from other POUs. |
| 6 | `pors` | - | Number of POR lines that follow. |
| 7 | `dtbl_mx` | - | Name of a flow control decision table ([`flo_con.dtl`](../input-reference/dtl.md)) that sets the daily demand, or `null`. |
| 8 | `rate_max` | m³/s | Maximum demand rate. Without a decision table the POU demands $\mathrm{rate\_max} \times 86400$ m³ every day. With a decision table, its demand is capped at that amount. |
| 9 | `dtbl_pod_fr` | - | Name of a flow control decision table that sets the fraction taken from each POD, or `null` to use the `frac` column of the POD lines. |
| 10 | `dtbl_por_fr` | - | Name of a flow control decision table that sets the fraction sent to each POR, or `null` to use the `frac` column of the POR lines. |

| POU type | Water goes to |
|----------|---------------|
| `irr` | The HRUs of an irrigation district in `water_hru_irr.wal` |
| `cha` | A channel (added to the channel's inflow) |
| `res` | A reservoir |
| `aqu` | An aquifer |
| `wtp` | A water treatment plant in `water_treat.wal` |
| `use` | A water use in `water_use.wal` |
| `wtow` | A water tower in `water_tower.wal` |
| `can` | A canal in `water_canal.wal` |
| `orcv` | A receiver outside the basin in `outside_rcv.wal` |

### POD lines

One line per POD, starting with the word `POD`.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `kind` | - | The word `POD`. |
| 2 | `num` | - | Not used (overwritten by column 5). |
| 3 | `name` | - | POD name, for reference. |
| 4 | `typ` | - | POD type, for reference. The type used is the one in `point_of_diver.wro`. |
| 5 | `typ_num` | - | Object number, for reference. |
| 6 | `conv_typ` | - | Conveyance type, `pipe` or `pump`. Read but not used. |
| 7 | `conv_num` | - | Conveyance number. Read but not used. |
| 8 | `dtbl_min` | - | Decision table for the minimum level. Read but not used. |
| 9 | `const_min` | depends on POD type | Minimum level below which the POD gives no water. See the POD type table under [point_of_diver.wro](#point_of_diverwro). |
| 10 | `dtbl_wdraw` | - | Name of a flow control decision table that manages the annual withdrawal limit, or `null`. When a name is given, the limit is not reset at the start of each year; the `duty_reset` decision table action resets it instead. |
| 11 | `ann_max` | m³/s | Annual withdrawal limit for this POD and POU. Once the volume taken during the year reaches $\mathrm{ann\_max} \times 86400$ m³, the POD gives this POU no more water until the limit is reset. |
| 12 | `frac` | fraction | Fraction of the POU's daily demand taken from this POD. The fractions of a POU's PODs normally add up to 1. |
| 13 | `comp` | - | `y` to let this POD make up a shortfall when the POU's PODs together delivered less than its demand, `n` otherwise. Channel PODs cannot make up a shortfall. |

### POR lines

One line per POR, starting with the word `POR`.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `kind` | - | The word `POR`. |
| 2 | `num` | - | Not used (overwritten by column 5). |
| 3 | `name` | - | POR name, for reference. |
| 4 | `typ` | - | Receiving object type: `cha`, `res`, `aqu`, `wtp`, `use`, `wtow`, `can` or `orcv`. `hru` is accepted but receives nothing. |
| 5 | `typ_num` | - | Number of the receiving object of that type. |
| 6 | `conv_typ` | - | Conveyance type. Read but not used. |
| 7 | `conv_num` | - | Conveyance number. Read but not used. |
| 8 | `dtbl_max` | - | Read but not used. |
| 9 | `const_max` | - | Read but not used. |
| 10 | `ann_max` | - | Read but not used. |
| 11 | `frac` | fraction | Fraction of the POU's outflow sent to this POR. |

A water treatment plant POU sends each POR its `frac` of the treated water, and a water use POU sends each POR its `frac` of its effluent. For the other POU types, canals included, each POR receives its `frac` of the water withdrawn for the POU, in addition to the delivery to the POU itself.

## point_of_diver.wro

Line 1 is a title, line 2 the number of PODs, line 3 a header. Each POD takes one line: five fixed columns, then six columns for each POU it serves.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `num` | - | POD number. |
| 2 | `name` | - | POD name. |
| 3 | `typ` | - | POD type, from the table below. |
| 4 | `typ_num` | - | Number of the object of that type (channel number, reservoir number, record number in `outside_src.wal`, and so on). |
| 5 | `pous` | - | Number of POUs served. |
| 6 to 11 | `pou_num`, `pou_name`, `pod_num`, `pou_typ`, `pou_typ_num`, `right` | - | Repeated for each POU: the POU number in `place_of_use.wro`, its name, the position of this POD among that POU's POD lines, the POU type and object number, and the water right (`sr` senior, `jr` junior). |

The `right` column is read but does not change the order of withdrawals in 62.0.1.

| POD type | Water taken from | Meaning of `const_min` |
|----------|------------------|------------------------|
| `cha` | Channel outflow for the day | Minimum daily flow volume (m³). No water is taken on days when the channel outflow is at or below it. |
| `res` | Reservoir storage | Fraction of the principal spillway volume. No water is taken when storage is at or below it. |
| `aqu` | Aquifer storage | Water table depth (m). Water is taken only while the water table is shallower than this depth. |
| `can` | Canal storage | Fraction of the current canal storage, so values up to 1 set no limit. |
| `wtow` | Water tower storage | Fraction of the current tower storage, so values below 1 set no limit. |
| `osrc` | Outside-basin source | Not used. |
| `unl` | Unlimited source with no water quality | Not used. |
| `hru` | Accepted, gives no water | - |
| `gwf` | Accepted, gives no water | - |

The amount taken is the POD's duty (its `frac` of the POU demand), limited by the water the object has above the minimum. Withdrawals from channels, reservoirs, canals and towers take sediment and nutrients with the water in proportion. Aquifer withdrawals take water, nitrate and mineral P.

Two types do not follow this rule:

- An `osrc` POD gives its `frac` of the daily volume available from the outside source, whatever the POU demand. The available volume is the `flo` value of the `om_osrc.wal` record with the same number as the source. The water has no sediment or nutrients.
- A `unl` POD gives $\mathrm{frac}$ times its duty, which is $\mathrm{frac}^2$ times the POU demand.

## water_hru_irr.wal

Irrigation districts for `irr` POUs. Line 1 is a title, line 2 the number of districts, line 3 a header. Each district takes one line with its name and number of HRUs, followed by one line per HRU.

| Line | Columns | Description |
|------|---------|-------------|
| District | `name`, `num_hrus` | District name and the number of HRU lines that follow. |
| HRU | `hru`, `dtbl_lum` | HRU number and the name of the decision table in [`lum.dtl`](../input-reference/dtl.md) that sets its irrigation demand. |

The demand of an irrigation POU is meant to be the sum of the demands of its HRUs, set by their decision tables. See [Limitations in 62.0.1](#limitations-in-6201) for how 62.0.1 handles it.

## wtps_wuses.wal

Sets up storage for treatment plants and water uses. It is needed whenever `water_treat.wal` or `water_use.wal` is used.

| Line | Contents |
|------|----------|
| 1 | Title |
| 2 | Number of treatment plants, number of water uses |
| 3 | Header (skipped) |
| 4 | Names of the treatment plants |
| 5 | Names of the water uses |

The two numbers must match the number of records in `water_treat.wal` and `water_use.wal`. Lines 4 and 5 must both be present, even when one of the numbers is 0. The names are read but not used.

## water_treat.wal

Water treatment plants. Line 1 is a title, line 2 the number of plants, line 3 a header. Each plant takes one line, followed by one line per treatment level.

Plant line:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Plant name. |
| 2 | `stor_mx` | m³ | Maximum storage. Read but not used. |
| 3 | `lag_days` | days | Treatment time. Read but not used: treated water leaves the same day. |
| 4 | `loss_fr` | fraction | Water loss during treatment. Read but not used; the loss comes from the `flo` value of the quality set. |
| 5 | `num_treats` | - | Number of treatment level lines that follow. |

Treatment level line:

| # | Column | Description |
|---|--------|-------------|
| 1 | `org_min_typ` | How the quality of the treated water is set: `const` (a record in `om_treat.wal`), `dtbl` (a decision table) or `recall` (a recall record). |
| 2 | `org_min_name` | Name of the `om_treat.wal` record, decision table or recall record. |
| 3, 4 | `pests_typ`, `pests_name` | Same pair for pesticides. Read but not used. |
| 5, 6 | `paths_typ`, `paths_name` | Same pair for pathogens. Read but not used. |
| 7, 8 | `salts_typ`, `salts_name` | Same pair for salt ions. Read but not used. |
| 9, 10 | `constit_typ`, `constit_name` | Same pair for other constituents. Read but not used. |
| 11 | `description` | Text. |

If the project has pesticides, each treatment level line is followed by a header line and a line of pesticide concentrations in the treated water, one value per pesticide. If it has pathogens, a header line and a line of pathogen concentrations follow in the same way.

When a plant has more than one treatment level, the last level sets the quality of the outflow.

Treated outflow to each POR is

$$Q_{out} = V_{stor}\; f_{\mathrm{om}}\; \mathrm{frac}_{POR}$$

where $V_{stor}$ is the water delivered to the plant that day (m³), $f_{\mathrm{om}}$ is the `flo` value of the quality set (the fraction of water that leaves the plant after treatment losses) and $\mathrm{frac}_{POR}$ is the POR's fraction. Sediment and nutrient loads are the quality set's concentrations times $Q_{out}$, limited to the loads that came into the plant. The difference between incoming and outgoing loads is reported as the amount removed by treatment.

## water_use.wal

Water uses (domestic, industrial, commercial). Line 1 is a title, line 2 the number of uses, line 3 a header. Each use takes one line, followed by the optional pesticide and pathogen lines described for `water_treat.wal`.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Use name. |
| 2 | `stor_mx` | m³ | Maximum storage. Read but not used. |
| 3 | `lag_days` | days | Read but not used. |
| 4 | `loss_fr` | fraction | Read but not used. |
| 5 to 14 | `org_min_typ`, `org_min_name`, ... `constit_typ`, `constit_name` | - | Quality pairs as in a `water_treat.wal` treatment level. `org_min_name` names a record in `om_use.wal` when the type is `const`. |
| 15 | `description` | - | Text. |

The outflow of a use is the water delivered that day times the `flo` value of its `om_use.wal` record (the fraction returned as effluent), with the record's concentrations. Each POR receives its `frac` of the outflow.

## outside_src.wal

Sources outside the basin, used by `osrc` PODs. Line 1 is a title, line 2 the number of sources, line 3 a header. Each source takes one line, followed by the optional pesticide and pathogen lines described for `water_treat.wal`.

| # | Column | Description |
|---|--------|-------------|
| 1 | `name` | Source name. |
| 2 to 11 | `org_min_typ`, `org_min_name`, ... `constit_typ`, `constit_name` | Quality pairs as in a `water_treat.wal` treatment level. `org_min_name` names a record in `om_osrc.wal` when the type is `const`. |
| 12 | `description` | Text. |

## om_treat.wal, om_use.wal and om_osrc.wal

Water quality sets for treated water, used water (effluent) and outside sources. Line 1 is a title, line 2 the number of records, line 3 a header. Each record is a name followed by 18 values.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `name` | - | Record name. |
| 2 | `flo` | see text | In `om_treat.wal` and `om_use.wal`, the fraction of the incoming water that leaves the plant or use. In `om_osrc.wal`, the volume available from the source each day (m³). |
| 3 | `sed` | mg/L | Sediment. |
| 4 | `orgn` | mg N/L | Organic nitrogen. |
| 5 | `sedp` | mg P/L | Organic phosphorus. |
| 6 | `no3` | mg N/L | Nitrate nitrogen. |
| 7 | `solp` | mg P/L | Soluble (mineral) phosphorus. |
| 8 | `chla` | mg/L | Chlorophyll a. |
| 9 | `nh3` | mg N/L | Ammonia nitrogen. |
| 10 | `no2` | mg N/L | Nitrite nitrogen. |
| 11 | `cbod` | mg/L | Carbonaceous biological oxygen demand. |
| 12 | `dox` | mg/L | Dissolved oxygen. |
| 13 to 18 | `san`, `sil`, `cla`, `sag`, `lag`, `grv` | mg/L | Sand, silt, clay, small aggregates, large aggregates and gravel. |
| 19 | `temp` | °C | Water temperature. |

## water_tower.wal

Water towers: storage between a source and its users. Line 1 is a title, line 2 the number of towers, line 3 a header, then one line per tower.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Tower number. |
| 2 | `name` | - | Tower name. |
| 3 | `stor_mx` | m³ | Storage capacity. Used by the `wtow_vol` decision table condition and the `fill_wtow` action. |
| 4 | `ddown_days` | days | Read but not used. |
| 5 | `loss_fr` | fraction | Read but not used. |

A tower is filled by a `wtow` POU and emptied by a `wtow` POD. Its water quality does not change in storage.

## water_canal.wal

Canals. Line 1 is a title, line 2 the number of canals, line 3 a header, then one line per canal.

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Canal number. |
| 2 | `name` | - | Canal name. |
| 3 | `w_sta` | - | Nearby weather station. Read but not used. |
| 4 | `init` | - | Initial concentrations. Read but not used. |
| 5 | `dtbl` | - | Decision table for canal outflow. Must be `null` in 62.0.1: with any other name the canal releases no water. |
| 6 | `ddown_days` | days | Days to draw the storage down. Each day the canal releases its storage divided by `ddown_days`. |
| 7 | `w` | m | Bottom width. |
| 8 | `d` | m | Depth. |
| 9 | `l` | km | Length. |
| 10 | `s` | m/m | Slope. Read but not used. |
| 11 | `ss` | m/m | Side slope (horizontal to vertical) of the trapezoidal section. |
| 12 | `sat_con` | mm/day | Seepage rate from the canal bed to groundwater. |
| 13 | `evap_co` | fraction | Fraction of the canal storage kept after evaporation each day. 1 means no evaporation loss; 0 empties the canal. |
| 14 | `num_aqu` | - | Number of aquifers that receive seepage. |
| 15 onward | `aqu_fr` | fraction | One value per aquifer: the fraction of the seepage that goes to aquifer 1, aquifer 2, and so on. The aquifers are always the first `num_aqu` aquifers of the model, in order. |

The canal capacity is computed from its shape as $V_{max} = (w + ss\,d)\,d\,l \times 1000$ m³ (with $l$ in km), and is used by the `fill_can` decision table action.

When a canal receives water, it first supplies any POUs for which it is a POD. Evaporation is then applied, and seepage of $\mathrm{sat\_con} \times d \times l$ m³ is divided among the aquifers by their fractions, with nitrate and soluble P in proportion. Finally the canal releases its storage divided by `ddown_days`. In 62.0.1 this release is removed from the canal but is not passed on; the PORs of a canal POU receive their share of the water withdrawn for the canal instead.

When [gwflow](gwflow.md) canal seepage is switched on, gwflow takes canal width, depth and `sat_con` from this file. It also expects a bed thickness, a diversion ID and start and end days for each canal, which `water_canal.wal` does not supply in 62.0.1, so gwflow treats every canal as connected to a channel.

## water_pipe.wal

Pipes. In 62.0.1 pipes are read but have no effect: water moves from PODs to POUs and from POUs to PORs without conveyance losses.

Line 1 is a title, line 2 the number of pipes, line 3 a header. For each pipe the reader then takes a header line and two record lines: the first gives the number of aquifers, and the second is read as the full record. Both record lines have the same layout:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Pipe number. |
| 2 | `name` | - | Pipe name. |
| 3 | `stor_mx` | m³ | Maximum storage. |
| 4 | `ddown_days` | days | Drawdown time. |
| 5 | `loss_fr` | fraction | Water lost along the pipe. |
| 6 | `num_aqu` | - | Number of aquifers that receive the loss. |
| 7 onward | `aqu_fr` | fraction | One value per aquifer: fraction of the loss to that aquifer. |

## outside_rcv.wal

Receivers outside the basin, with columns `id`, `name` and `filename` (an output file for the receiver). SWAT+ 62.0.1 does not read this file, so `orcv` POUs and PORs have no receiving object.

## Decision tables

Water allocation uses flow control decision tables ([`flo_con.dtl`](../input-reference/dtl.md)) and land use decision tables ([`lum.dtl`](../input-reference/dtl.md)). See [decision tables](dtl.md) for the file format.

| Item | Kind | Effect |
|------|------|--------|
| `wallo_dmd` with option `set_dmd` | action | Sets the POU demand to the action's constant (m³). |
| `wallo_dmd` with option `irr_dmd` | action | Adds the current demand of the POU named by the action's object number. |
| `wallo_dmd` with option `fill_res`, `fill_wtow` or `fill_can` | action | Sets the demand to the volume needed to fill a reservoir (to a fraction of its principal or emergency volume), a water tower or a canal (to a fraction of capacity), times a second constant. |
| `duty_reset` | action | Sets a new annual withdrawal limit for one POD of one POU and resets the volume taken so far. |
| `irr_pou_dmd` | condition | Tests the current demand of a POU. |
| `wtow_vol` | condition | Tests water tower storage as a fraction of `stor_mx`. |

## Limitations in 62.0.1

Several parts of the daily calculation do not follow the input structure above:

- The duty used for a withdrawal is looked up with the POD's number and the position of the POU in that POD's list, in place of the POU's number and the POD's position in that POU. Results follow the input only when these coincide: POD number $n$ is the $n$-th POD line of every POU it serves, and the $k$-th POU listed for a POD in `point_of_diver.wro` is POU number $k$. A network with one POU whose POD lines are listed in POD-number order meets this. Other layouts take the wrong duty or fail.
- For an irrigation district (`irr` POU), the HRU demands from the district's decision tables are summed and then replaced by $\mathrm{rate\_max} \times 86400$, so the POU always demands its maximum rate. Delivery to the district does not step through the listed HRUs.
- No decision table action sets the POD and POR fractions, so naming a table in `dtbl_pod_fr` or `dtbl_por_fr` sets all fractions to zero.
- For an aquifer POD, the water delivered is computed after the aquifer storage has been reduced, so it is smaller than the water removed from the aquifer by the factor $(1 - r)$, where $r$ is the fraction of storage withdrawn.
- Projects with pesticides or pathogens fail when `water_treat.wal`, `water_use.wal` or `outside_src.wal` is read, because the storage for the treated-water concentrations is not set up.
- Water taken by start-of-day PODs (outside sources, towers, unlimited sources) is not counted in the day's delivered totals, which are reset when the day's demand is set.

## Example

A town water use that draws on a channel and an aquifer and returns its effluent to another channel. The single POU lists its PODs in POD-number order, which keeps POD numbers and POU positions aligned as 62.0.1 requires.

`place_of_use.wro`:

```
place_of_use.wro: town supply
1
num  name   typ  typ_num  pods  pors  dtbl_mx  rate_max  dtbl_pod_fr  dtbl_por_fr
1    town   use  1        2     1     null     0.05      null         null
POD  1  river   cha  12  pipe  0  null  20000.0  null  20.0  0.7  n
POD  2  wells   aqu  3   pump  0  null  15.0     null  20.0  0.3  y
POR  1  outfall cha  14  pipe  0  null  0.0      0.0   1.0
```

`point_of_diver.wro`:

```
point_of_diver.wro: town supply
2
num  name   typ  typ_num  pous  pou_num  pou_name  pod_num  pou_typ  pou_typ_num  right
1    river  cha  12       1     1        town      1        use      1            sr
2    wells  aqu  3        1     1        town      2        use      1            sr
```

`wtps_wuses.wal`, `water_use.wal` and `om_use.wal`:

```
wtps_wuses.wal: town supply
0  1
treatment plant names on line 4, water use names on line 5
none
town
```

```
water_use.wal: town supply
1
name  stor_mx  lag_days  loss_fr  org_min_typ  org_min_name  pests_typ  pests_name  paths_typ  paths_name  salts_typ  salts_name  constit_typ  constit_name  description
town  0.0      0.0       0.0      const        town_eff      null       null        null       null        null       null        null         null          municipal
```

```
om_use.wal: town supply
1
name      flo  sed  orgn  sedp  no3  solp  chla  nh3  no2  cbod  dox  san  sil  cla  sag  lag  grv  temp
town_eff  0.8  20   2     0.5   10   1     0     5    0.1  20    4    0    0    0    0    0    0    18
```

The town demands $0.05 \times 86400 = 4320$ m³ a day: 70% (3024 m³) from channel 12 and 30% (1296 m³) from aquifer 3. The channel gives water only on days its outflow exceeds 20 000 m³, and the aquifer only while its water table is shallower than 15 m. The aquifer may make up a shortfall from the channel. Each POD may supply at most $20 \times 86400 = 1\,728\,000$ m³ a year to the town. 80% of the water delivered returns to channel 14 as effluent with the concentrations in `town_eff`.

## Outputs

Set the `water_allo` row of [`print.prt`](print-prt.md) to write `water_allo_day.txt` (and the monthly, yearly and average annual files) with each POU's demand and delivery, the withdrawal from each POD and the water sent to each POR. Treatment plants and water uses are reported in `wallo_treat_*.txt` and `wallo_use_*.txt`.

## Related files

- [`file.cio`](file-cio.md): the `water_rights` line names the POU and POD files.
- [Decision tables](dtl.md): flow control and land use tables used for demand, limits and irrigation.
- [Channels](sd-channel.md), [reservoirs](res.md) and [aquifers](aqu.md): PODs and receiving objects.
- [`print.prt`](print-prt.md): output switches.
- [gwflow](gwflow.md): canal seepage to the groundwater grid.

??? quote "Sources"

    - File names and `file.cio` line: `type input_water_allocation` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Read order: [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in)
    - Readers: [`water_allocation_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_allocation_read.f90) (POU and POD files), [`water_hru_irr_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_hru_irr_read.f90), [`wallo_wtps_wuses.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_wtps_wuses.f90), [`water_treatment_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_treatment_read.f90), [`water_use_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_use_read.f90), [`water_osrc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_osrc_read.f90), [`om_treat_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_treat_read.f90), [`om_use_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_use_read.f90), [`om_osrc_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/om_osrc_read.f90), [`water_tower_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_tower_read.f90), [`water_canal_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_canal_read.f90), [`water_pipe_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_pipe_read.f90), [`water_orcv_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_orcv_read.f90) (not called)
    - Types: [`water_allocation_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/water_allocation_module.f90); `hyd_output` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Daily calculation: [`wallo_start_day.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_start_day.f90) (called from [`time_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/time_control.f90)), [`wallo_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_control.f90), [`wallo_withdraw.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_withdraw.f90), [`wallo_pou_deliv.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_pou_deliv.f90), [`wallo_return.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_return.f90), [`wallo_treatment.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_treatment.f90), [`wallo_use.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_use.f90), [`wallo_canal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_canal.f90), [`wallo_transfer.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_transfer.f90) (not called)
    - POD hooks: [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90), [`res_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/res_control.f90), [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90), [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Decision tables: [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90), [`conditions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/conditions.f90)
    - Outputs: [`header_water_allocation.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/header_water_allocation.f90), [`wallo_pou_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/wallo_pou_output.f90)
    - gwflow canals: [`gwflow_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_read.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `place_of_use.wro` POU line | `num`, `name`, `typ`, `typ_num`, `pods`, `pors`, `dtbl_mx`, `rate_max`, `dtbl_pod_fr`, `dtbl_por_fr` | `ipou`, `pou%name`, `%typ`, `%typ_num`, `%pods`, `%pors`, `%dtbl_mx`, `%rate_max`, `%dtbl_pod_fr`, `%dtbl_por_fr` |
    | POD line | columns 2 to 13 | `pou%pod%num`, `%name`, `%typ`, `%num`, `%conv_typ`, `%conv_num`, `%dtbl_min`, `%const_min`, `%dtbl_wdraw`, `%ann_max`, `%frac`, `%comp` |
    | POR line | columns 2 to 11 | `pou%por%num`, `%name`, `%typ`, `%num`, `%conv_typ`, `%conv_num`, `%dtbl_max`, `%const_max`, `%ann_max`, `%frac` |
    | `point_of_diver.wro` | `num`, `name`, `typ`, `typ_num`, `pous` | `pod%num`, `%name`, `%typ`, `%typ_num`, `%pous` |
    | `point_of_diver.wro` per POU | `pou_num`, `pou_name`, `pod_num`, `pou_typ`, `pou_typ_num`, `right` | `pod%pou%num`, `%name`, `%pod_num`, `%typ`, `%typ_num`, `%right` |
    | `water_hru_irr.wal` | `name`, `num_hrus`, `hru`, `dtbl_lum` | `hruirr_db%name`, `%hrus`, `%hru_num`, `%dtbl_lum` |
    | `water_treat.wal` | `name`, `stor_mx`, `lag_days`, `loss_fr`, `num_treats` | `wtp%name`, `%stor_mx`, `%lag_days`, `%loss_fr`, `%num_treats` |
    | treatment level, `water_use.wal`, `outside_src.wal` | quality pairs | `%conc%org_min_typ`, `%org_min_name`, `%pests_typ`, `%pests_name`, `%paths_typ`, `%paths_name`, `%salts_typ`, `%salts_name`, `%constit_typ`, `%constit_name` |
    | `om_*.wal` | 18 values | `wtp_om_treat`, `wuse_om_efflu`, `osrc_om` (`type hyd_output`) |
    | `water_tower.wal` | `stor_mx`, `ddown_days`, `loss_fr` | `wtow%stor_mx`, `%ddown_days`, `%loss_fr` |
    | `water_canal.wal` | `w_sta` ... `num_aqu`, `aqu_fr` | `canal%w_sta`, `%init`, `%dtbl`, `%ddown_days`, `%w`, `%d`, `%l`, `%s`, `%ss`, `%sat_con`, `%evap_co`, `%num_aqu`, `%aqu_loss_fr` |
    | `water_pipe.wal` | `stor_mx` ... `aqu_fr` | `pipe%stor_mx`, `%ddown_days`, `%loss_fr`, `%num_aqu`, `%aqu_loss_fr` |

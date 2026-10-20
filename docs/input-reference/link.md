---
title: "Link files (chan-surf.lin, aqu_cha.lin)"
description: Optional files on the link line of file.cio. chan-surf.lin links SWAT+ channels to the floodplain HRUs that receive overbank water; aqu_cha.lin spreads the return flow of an aquifer over several channels.
status: review
verified_against:
  - src/input_file_module.f90
  - src/readcio_read.f90
  - src/main.f90.in
  - src/hyd_connect.f90
  - src/basin_read_objs.f90
  - src/proc_cha.f90
  - src/overbank_read.f90
  - src/sd_channel_surf_link.f90
  - src/sd_channel_module.f90
  - src/sd_channel_control3.f90
  - src/sd_channel_sediment3.f90
  - src/ch_rtmusk.f90
  - src/ru_read_elements.f90
  - src/aqu2d_read.f90
  - src/aqu2d_init.f90
  - src/aqu_1d_control.f90
  - src/define_unit_elements.f90
  - src/hydrograph_module.f90
  - src/hru_control.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Purpose

The `link` line of [`file.cio`](../input-reference/file-cio.md) names two optional files that connect objects outside the routing set up by the [connectivity files](con.md):

- `chan-surf.lin` lists, for a SWAT+ channel, the HRUs or routing units on its floodplain. On days with overbank flow, the wetlands of those HRUs are filled from the channel.
- `aqu_cha.lin` lists, for an aquifer, the channels that receive its return flow. The flow is shared among the channels by channel length and drainage area.

The line gives the two names in this order. The defaults, `chan-surf.lin` and `aqu_cha.lin`, apply only when [`file.cio`](../input-reference/file-cio.md) ends before the line (see the [master file](file-cio.md#categories-and-default-file-names)). Projects that do not use the files give `null` for both, as the reference datasets in the SWAT+ repository do. Earlier documentation called the first file `chan_surf.lin`.

Neither file has column names that SWAT+ checks. Both readers skip the header line and take the values by position, so the column names on this page are descriptive.

## chan-surf.lin

Free format, whitespace-separated. Line 1 is a title and is skipped. Line 2 is a single whole number, the number of channel rows; SWAT+ also counts the rows itself, and the count only sets a minimum size for the table. Line 3 is a column header and is skipped. Each later line links one channel to its floodplain objects:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Number of the SWAT+ channel, as numbered in [`chandeg.con`](../input-reference/con.md). |
| 2 | `name` | - | Name of the floodplain. Not used in calculations. |
| 3 | `num_obj` | count | Number of floodplain objects that follow. A row with 0 gives the channel no floodplain links. |
| 4 | `obj_typ` | - | Type of the first floodplain object: `hru` or `ru` (routing unit). |
| 5 | `obj_id` | - | Number of the first floodplain object, as numbered in [`hru.con`](../input-reference/con.md) or [`rout_unit.con`](../input-reference/con.md). |
| 6, 7, ... | `obj_typ`, `obj_id` | - | One further pair for each remaining object, `num_obj` pairs in all. |

Object types other than `hru` and `ru` are read and then ignored. For an `ru` object, SWAT+ takes the element numbers that [`rout_unit.def`](../input-reference/units.md#rout_unitdef) lists for that routing unit and uses each one as an HRU number. This selects the routing unit's HRUs only when each element number in [`rout_unit.ele`](../input-reference/units.md#rout_unitele) equals the number of the HRU it refers to.

The links apply to channels routed with the SWAT+ channel method ([`chandeg.con`](../input-reference/con.md)). Legacy channels ([`channel.con`](../input-reference/con.md)) make no use of them.

### Overbank flow to floodplain wetlands

Overbank flow happens on days when the channel's peak flow rate is above the bankfull threshold described under [floodplain deposition](sd-channel.md#floodplain-deposition). The overbank volume $V_{ob}$ is the floodplain volume of the channel's rating curve at the peak flow rate. After floodplain deposition, SWAT+ goes through the floodplain HRUs in the order listed (a routing unit contributes its HRUs in the order of its elements). For each HRU it takes the room left in the HRU's wetland,

$$V_{fill} = V_{emr} - V_{wet}$$

where $V_{emr}$ is the wetland's emergency volume and $V_{wet}$ its current storage (m³), and subtracts it from the overbank volume still available. When the overbank volume runs out, $V_{fill}$ is cut to what was left. The wetland then receives the fraction

$$r = \min\!\left(1,\; \frac{V_{fill}}{Q_{in}}\right)$$

of the channel's inflow $Q_{in}$ for the day (m³), with the same fraction of its sediment, nutrients and other constituents, and the channel inflow is reduced by that fraction.

Only HRUs with surface storage, a `surf_stor` entry in [`hru-data.hru`](../input-reference/hru.md) that names a record in [`wetland.wet`](../input-reference/wet.md#wetlandwet), receive water. Other HRUs in the list take nothing from the channel. The water each wetland receives is reported in the `overbank` column (mm) of the HRU [water balance output](../output-reference/water-balance.md). See also [overbank flow and floodplain deposition](../model-theory/channels.md#overbank-flow-and-floodplain-deposition) in the model theory, and the [wetland inputs](wet.md) for the emergency volume.

### Missing file and repeated read

SWAT+ reads `chan-surf.lin` while it sets up the SWAT+ channels, whether or not the model has any.

- If the slot is `null`, the file is skipped and no channel has floodplain links.
- If the slot gives a name and no file of that name exists, SWAT+ opens it anyway. This creates an empty file of that name in the run folder, nothing is read from it, and no channel has floodplain links.
- When [`object.cnt`](../input-reference/object-cnt.md) counts legacy channels (`cha` above 0), SWAT+ reads the file a second time, earlier in the setup, before the SWAT+ channels exist. If the file exists, the second read tries to set up the same table again and the run stops with an error.

## aqu_cha.lin

Free format, whitespace-separated. Line 1 is a title and line 2 a column header; both are skipped. Each later line links one aquifer to a set of channels:

| # | Column | Units | Description |
|---|--------|-------|-------------|
| 1 | `id` | - | Number of the aquifer, as numbered in [`aquifer.con`](../input-reference/con.md). |
| 2 | `name` | - | Name of the link. Not used in calculations. |
| 3 | `num_elem` | count | Number of values in the channel list that follows. A row with 0 links no channels. |
| 4, 5, ... | `elements` | - | Channel numbers, as numbered in [`chandeg.con`](../input-reference/con.md). A negative value marks a range: `1 -4` means channels 1 to 4. |

The aquifer numbers must lie between 1 and the number of aquifers. SWAT+ reads as many rows as the largest aquifer number in the first column, so each aquifer should appear on one row only. Earlier documentation described the file as a replacement for [`aquifer.con`](../input-reference/con.md). In 62.0.1 [`aquifer.con`](../input-reference/con.md) is still required, see [overlap with aquifer outflows](#overlap-with-aquifer-outflows).

### Return flow shares

For each linked aquifer, SWAT+ sorts the linked channels by drainage area, smallest first. The drainage area is the `area` column of [`chandeg.con`](../input-reference/con.md) and the channel length $L_i$ is the `len` column of [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha) (km). With $L_{tot}$ the total length of the linked channels, the length left when channel $i$ and all smaller channels have stopped receiving flow is

$$L_{left,i} = L_{tot} - \sum_{j \le i} L_j$$

Each day the contributing channel length grows with the aquifer's return flow $Q$ (mm):

$$L_c = L_{tot}\,\frac{Q}{\mathrm{bf\_max}}$$

where `bf_max` is given in [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) (mm; see [aquifer files](aqu.md)). The first contributing channel $k$ is the smallest channel with $L_c \ge L_{left,k}$, and each channel from $k$ upward receives the share

$$f_i = \frac{L_i}{L_{left,k} + L_k}, \qquad i \ge k$$

while the smaller channels receive nothing. The shares of the contributing channels add up to 1, so the whole return flow of the aquifer is passed on. When $Q$ is at or above `bf_max`, every linked channel receives flow in proportion to its length. As $Q$ falls, the channels with the smallest drainage areas stop receiving flow first. See [baseflow](../model-theory/aquifers.md#baseflow) in the model theory.

Each linked channel adds its share of the aquifer's return flow hydrograph, with its nitrate, phosphorus, salts and constituents, to its inflow. This happens when the channel is routed: on the same day if the aquifer comes before the channel in the routing order, otherwise on the next day. The water appears in the `geo_bf` column (m³/s) of the [channel output](../output-reference/channel-sediment-nutrient.md#channel_sd-files).

### Channel order, lengths and bf_max

- The shares are computed in drainage-area order. Each channel looks up its share by its position in the `aqu_cha.lin` list. A channel receives its intended share only when the list for each aquifer is already in order of increasing drainage area. In any other order, channels receive each other's shares; the total for the aquifer does not change.
- The channel length is taken from the row of [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha) whose position equals the channel's record number in [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha). This gives the right length when both files list the channels in the same order.
- Once the file is read, the calculation divides by `bf_max` for every aquifer, including aquifers the file does not list. With `bf_max` = 0 the division fails, and builds that stop on floating-point errors (the Intel builds, for example) stop the run. Give every aquifer a `bf_max` above zero when `aqu_cha.lin` is used.

### Overlap with aquifer outflows

`aqu_cha.lin` is read only when [`object.cnt`](../input-reference/object-cnt.md) counts aquifers, right after [`aquifer.con`](../input-reference/con.md). The aquifer still routes its return flow through the outflows listed in [`aquifer.con`](../input-reference/con.md), and SWAT+ also passes the shares above to the linked channels. A model that lists the same channels as outflows in [`aquifer.con`](../input-reference/con.md) and in `aqu_cha.lin` sends the return flow to them twice.

When [gwflow](gwflow.md) is active, SWAT+ sets the aquifer count to 0 and `aqu_cha.lin` is not read.

### Missing or short file

- If the slot is `null` or the file does not exist, the file is skipped and no aquifer is linked to channels.
- If the file exists but has fewer than two lines, the run stops with an end-of-file error.

## Example

No dataset in the SWAT+ repository uses either file. The two files below are illustrative.

```
chan-surf.lin: illustrative example
2
id  name    num_obj  obj_typ  obj_id  obj_typ  obj_id
1   fp001   2        hru      4       hru      5
3   fp003   1        ru       2
```

Channel 1 is linked to HRUs 4 and 5, and channel 3 to the HRUs of routing unit 2. On a day with overbank flow in channel 1, the wetland of HRU 4 is filled first, then that of HRU 5, as long as overbank volume remains. An HRU without surface storage receives nothing.

```
aqu_cha.lin: illustrative example
id  name    num_elem  elements
1   aqu01   2         1  -4
2   aqu02   3         5  7  9
```

Aquifer 1 shares its return flow among channels 1 to 4, and aquifer 2 among channels 5, 7 and 9. For the shares to reach the intended channels, channels 1 to 4 must have increasing drainage areas in that order, and so must channels 5, 7 and 9. Neither aquifer should also route its return flow to these channels in [`aquifer.con`](../input-reference/con.md).

## Related files

- [`file.cio`](../input-reference/file-cio.md): names both files on the `link` line ([master file](file-cio.md)).
- [`chandeg.con`](../input-reference/con.md), [`aquifer.con`](../input-reference/con.md), [`hru.con`](../input-reference/con.md), [`rout_unit.con`](../input-reference/con.md), [`rout_unit.def`](../input-reference/units.md#rout_unitdef) and [`rout_unit.ele`](../input-reference/units.md#rout_unitele): number the objects the files refer to ([connectivity files](con.md)).
- [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha) and [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha): channel length and bankfull flow ([channel tables](sd-channel.md)).
- [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu): `bf_max` and the return flow ([aquifer files](aqu.md)).
- [`hru-data.hru`](../input-reference/hru.md), [`wetland.wet`](../input-reference/wet.md#wetlandwet) and [`hydrology.wet`](../input-reference/wet.md#hydrologywet): the surface storage that receives overbank water ([HRU data](hru.md), [wetland inputs](wet.md)).
- [`object.cnt`](../input-reference/object-cnt.md): the aquifer and legacy channel counts ([object counts](object-cnt.md)).

??? quote "Sources"

    - File name slots: `type input_link` in [`input_file_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/input_file_module.f90), read in [`readcio_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/readcio_read.f90)
    - Readers: [`overbank_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/overbank_read.f90) (`chan-surf.lin`), [`aqu2d_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu2d_read.f90) (`aqu_cha.lin`), with element ranges expanded in [`define_unit_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/define_unit_elements.f90)
    - Call sites: [`hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90) (both readers), [`proc_cha.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_cha.f90) (`overbank_read` again, `sd_channel_surf_link`, `aqu2d_init`); aquifer count reset for gwflow in [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90)
    - Type definitions: `floodplain_parameters` in [`sd_channel_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_module.f90); `channel_aquifer_elements` and `geomorphic_baseflow_channel_data` in [`hydrograph_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hydrograph_module.f90)
    - Floodplain HRU lists: [`sd_channel_surf_link.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_surf_link.f90); routing unit elements from [`ru_read_elements.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ru_read_elements.f90)
    - Overbank filling of wetlands: [`sd_channel_sediment3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_sediment3.f90); floodplain wetland storage in [`ch_rtmusk.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/ch_rtmusk.f90); `overbank` output in [`hru_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hru_control.f90)
    - Channel sorting and lengths: [`aqu2d_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu2d_init.f90)
    - Daily shares: [`aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90); added to channel inflow in [`sd_channel_control3.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/sd_channel_control3.f90)

    | File | Column | Fortran variable |
    |------|--------|------------------|
    | `chan-surf.lin` | line 2 count | `mcha_sp` |
    | `chan-surf.lin` | `id` | index `i` of `sd_ch` |
    | `chan-surf.lin` | `name` | `sd_ch%fp%name` |
    | `chan-surf.lin` | `num_obj` | `nspu`, `sd_ch%fp%obj_tot` |
    | `chan-surf.lin` | `obj_typ` | `sd_ch%fp%obtyp` |
    | `chan-surf.lin` | `obj_id` | `sd_ch%fp%obtypno` |
    | `aqu_cha.lin` | `id` | index `iaq` of `aq_ch` |
    | `aqu_cha.lin` | `name` | `aq_ch%name` |
    | `aqu_cha.lin` | `num_elem` | `nspu` |
    | `aqu_cha.lin` | `elements` | `elem_cnt`, expanded to `aq_ch%num` |
    | `aquifer.aqu` | `bf_max` | `aqudb%bf_max` |
    | `hyd-sed-lte.cha` | `len` | `sd_chd%chl` |
    | `chandeg.con` | `area` | `ob%area_ha` |

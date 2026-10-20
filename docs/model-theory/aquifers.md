---
title: Aquifers
description: The 1D aquifer object and the gwflow grid model, which store recharge from the soil profile and return it to streams as baseflow.
status: review
verified_against:
  - src/aqu_1d_control.f90
  - src/aqu_initial.f90
  - src/aqu_read.f90
  - src/aquifer_module.f90
  - src/hyd_connect.f90
  - src/basin_read_objs.f90
  - src/gwflow_simulate.f90
  - src/gwflow_lateral.f90
  - src/gwflow_rech.f90
  - src/gwflow_gwet.f90
  - src/gwflow_channel_exch.f90
  - src/gwflow_read.f90
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

## Overview

Water that percolates below the soil profile recharges groundwater. Groundwater returns to the stream network as baseflow, moves up toward the root zone in dry periods ("revap"), and leaks downward out of the shallow system as deep seepage. SWAT+ offers two ways to simulate this:

- 1D aquifer objects (the default): each aquifer is a lumped storage defined in [`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) and connected to channels, reservoirs or other aquifers through [`aquifer.con`](../input-reference/con.md). Recharge, baseflow, revap and seepage are computed once a day from a few parameters.
- gwflow (`gwflow = 1` in [`codes.bsn`](../input-reference/codes-bsn.md)): the aquifer is replaced by a grid of cells. Each cell has a groundwater head, and water moves between cells by Darcy's law and exchanges with channels, reservoirs, wetlands, tile drains, canals and pumping wells.

In SWAT, every subbasin had a shallow and a deep aquifer. In SWAT+ an aquifer is an independent spatial object. A watershed can have one aquifer or many, and deep seepage from a shallow aquifer can be routed to a second (deep) aquifer object or allowed to leave the system.

## 1D aquifer

### Recharge

Recharge is the water an aquifer receives from the objects routed to it: percolation from HRUs, routing units or other aquifers, and any channel or reservoir seepage directed to it in the connection files. The daily recharge depth is

$$
w_{rchg} = \frac{V_{in}}{10\,A}
$$

| Symbol | Meaning | Units |
|---|---|---|
| $w_{rchg}$ | recharge to the aquifer | mm |
| $V_{in}$ | volume of water entering the aquifer on the day | m³ |
| $A$ | aquifer area | ha |

SWAT delayed recharge with an exponential lag (`GW_DELAY`). The SWAT+ 1D aquifer has no recharge delay: water leaving the soil profile is added to aquifer storage on the day it arrives. Recharge is added to storage first, and all outflows on the day are then computed from the new storage.

### Water table depth

Storage is converted to a water table depth using the specific yield:

$$
d_{wt} = d_{bot} - \frac{S}{1000\,S_y}, \qquad d_{wt} \ge 0
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $d_{wt}$ | depth from the land surface to the water table | m | initial value `dep_wt` |
| $d_{bot}$ | depth from the land surface to the bottom of the aquifer | m | `dep_bot` |
| $S$ | water stored in the aquifer | mm | |
| $S_y$ | specific yield | m³/m³ | `spec_yld` |

At the start of the simulation storage is set from the initial water table depth, $S = 1000\,(d_{bot} - d_{wt})\,S_y$.

### Baseflow

Baseflow (return flow) occurs only while the water table is at or above the threshold depth `flo_min`. It follows the recession equation used in SWAT:

$$
Q_{gw,i} =
\begin{cases}
Q_{gw,i-1}\,e^{-\alpha} + w_{rchg}\left(1 - e^{-\alpha}\right) & d_{wt} \le d_{flo} \\
0 & d_{wt} > d_{flo}
\end{cases}
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $Q_{gw,i}$ | baseflow on day $i$ | mm | initial value `gw_flo` |
| $\alpha$ | baseflow recession constant | 1/day | `alpha_bf` |
| $d_{flo}$ | water table depth at or above which baseflow occurs | m | `flo_min` |

Baseflow is limited to the water in storage. Because the threshold is a depth, a larger `flo_min` allows baseflow from a deeper water table. In SWAT the equivalent threshold `GWQMN` was a storage in mm.

The baseflow hydrograph goes to every object listed in [`aquifer.con`](../input-reference/con.md) with hydrograph type `tot`, split by the fractions given there. When channels are linked to the aquifer through the aquifer-channel link file, baseflow is spread over the linked channels from the outlet upward. The contributing channel length grows with the ratio of baseflow to `bf_max`, so `bf_max` is the baseflow at which every linked channel receives water.

### Deep seepage

A fixed fraction of the day's recharge leaves the aquifer through its bottom:

$$
w_{seep} = \beta_{deep}\, w_{rchg}
$$

where $\beta_{deep}$ is `rchg_dp` (fraction). Seepage is limited to the water left in storage after baseflow. It leaves the aquifer as its second hydrograph; routing it in [`aquifer.con`](../input-reference/con.md) with hydrograph type `rhg` sends it to another object, usually a deep aquifer.

### Revap

When the water table is shallower than `revap_min`, water is removed from the aquifer in response to evaporative demand:

$$
w_{revap} =
\begin{cases}
\beta_{rev}\,E_o & d_{wt} < d_{rev} \\
0 & d_{wt} \ge d_{rev}
\end{cases}
$$

| Symbol | Meaning | Units | Input |
|---|---|---|---|
| $w_{revap}$ | revap | mm | |
| $\beta_{rev}$ | revap coefficient | - | `revap` |
| $E_o$ | potential evapotranspiration at the aquifer's weather station | mm | |
| $d_{rev}$ | water table depth above which revap occurs | m | `revap_min` |

Revap is limited to the water left in storage. In SWAT the revap threshold `REVAPMN` was a storage in mm and revap tapered off as storage approached it. In SWAT+ the threshold is a depth and revap is either on or off. Revap is removed from the aquifer and is not added back to the soil profile.

The daily order is recharge, water table depth, baseflow, seepage, then revap. When the aquifer is a point of diversion in the water allocation inputs, withdrawals are taken after recharge and before baseflow.

### Nitrate and phosphorus

Nitrate in recharge water is added to the aquifer nitrate pool. Baseflow and seepage remove nitrate at the concentration of the aquifer water, $C_{NO3} = N_{aq}/S$. The pool also decays with half-life `hl_no3n`:

$$
N_{aq,i} = N_{aq,i-1}\,\exp\!\left(\frac{-0.693}{t_{1/2} + 0.1}\right)
$$

where $t_{1/2}$ is `hl_no3n` (days). A half-life of 0 removes almost all aquifer nitrate each day.

Soluble phosphorus in baseflow is the volume of water entering the aquifer on the day multiplied by the concentration `sol_p` (mg/L). It is a fixed concentration and does not draw on a phosphorus pool.

### Pesticides, salts and constituents

Pesticides entering with recharge decay with the aquatic half-life of the pesticide. The concentration available for transport is the pesticide mass divided by a mixing volume made of baseflow, seepage, revap and a fraction of storage set by the pesticide groundwater mixing factor in [`parameters.bsn`](../input-reference/parameters-bsn.md). Baseflow and seepage remove pesticide at that concentration. All aquifer pesticide is soluble.

Salt ions and other constituents are mixed through the aquifer water. Their concentration is mass divided by the groundwater volume, and baseflow and seepage remove mass at that concentration. See [Salts and constituents](salts-constituents.md).

## gwflow grid model

### Activation

Setting `gwflow = 1` in [`codes.bsn`](../input-reference/codes-bsn.md) turns on gwflow. SWAT+ then reads the gwflow input files ([`codes.gw`](../input-reference/gwflow.md#codesgw), [`zones.gw`](../input-reference/gwflow.md#zonesgw), [`cells.gw`](../input-reference/gwflow.md#cellsgw), [`cellcon.gw`](../input-reference/gwflow.md#cellcongw), [`chancell.gw`](../input-reference/gwflow.md#chancellgw) and the optional files for tiles, reservoirs, floodplains, canals, pumping and phreatophytes), and the 1D aquifer objects are switched off. If [`chancell.gw`](../input-reference/gwflow.md#chancellgw) is missing, gwflow is switched off and the 1D aquifers are used.

### Cell water balance

Each active cell has a head $h$, a bottom elevation, a land surface elevation, a hydraulic conductivity $K$, a specific yield $S_y$, an ET extinction depth and an area $A_{c}$. The day is divided into flow time steps of length $\Delta t$ (`time_step` in [`codes.gw`](../input-reference/gwflow.md#codesgw)). On each step the change in cell storage is the sum of lateral flows from neighbouring cells and the sources and sinks of the day:

$$
\Delta V = \left(\sum_k Q_k + Q_{ss}\right)\Delta t, \qquad h^{new} = h + \frac{\Delta V}{S_y\,A_{c}}
$$

The solution is explicit: all heads are updated from the heads at the start of the step.

### Lateral flow between cells

Flow between a cell and each connected neighbour follows Darcy's law:

$$
Q_k = K_f\,\frac{h_k - h}{L}\,b_f\,w
$$

| Symbol | Meaning | Units |
|---|---|---|
| $Q_k$ | flow from neighbour $k$ into the cell | m³/day |
| $K_f$ | face conductivity, the harmonic mean of the two cells' $K$ | m/day |
| $L$ | distance between the cell centroids | m |
| $b_f$ | mean saturated thickness of the two cells | m |
| $w$ | face width, the square root of the smaller cell's area | m |

Inactive cells and no-flow boundary cells pass no water. Constant-head boundary cells exchange water with their neighbours but keep their initial head.

### Sources and sinks

- Recharge: percolation from each HRU or landscape unit is delayed and passed to the cells it overlaps: $R_i = (1 - \delta)\,w_{perc,i} + \delta\,R_{i-1}$, with $\delta = e^{-1/\tau}$ and $\tau$ the recharge delay (days) of the cell's zone.
- Groundwater ET: ET demand not met by the soil profile is taken from the cell: all of it when the head is at or above the land surface, none when the head is below the extinction depth, and a linearly varying share in between.
- Channel exchange: each channel cell exchanges water with the stream through the streambed, $Q = K_{bed}\,(\Delta h / b_{bed})\,W\,L_{ch}$, where $W$ is channel width, $L_{ch}$ the channel length in the cell and $b_{bed}$ the bed thickness. When the head is above the channel stage, groundwater discharges to the channel and $\Delta h$ is head minus stage. When the head is between the bed and the stage, the channel leaks to the aquifer and $\Delta h$ is stage minus head. When the head is below the bed, leakage uses the flow depth as $\Delta h$.
- Other exchanges: reservoirs, ponds, wetlands, floodplains, tile drains, canals, pumping (from water allocation or an external schedule) and phreatophyte transpiration are added when their input files are present.
- Saturation excess: when the head rises above the land surface, the excess water goes to the nearest channel.

gwflow can also transport heat and solutes (nitrate, phosphorus, salt ions and constituents) between cells and can track groundwater travel time. Inputs are described in [gwflow inputs](../input-reference/gwflow.md) and outputs in [gwflow outputs](../output-reference/gwflow.md).

## Parameters

| Parameter | File | Effect |
|---|---|---|
| `gwflow` | [`codes.bsn`](../input-reference/codes-bsn.md) | 0 = 1D aquifer objects; 1 = gwflow grid model |
| `gw_flo` | [`aquifer.aqu`](../input-reference/aqu.md) | Initial baseflow (mm) |
| `dep_bot` | [`aquifer.aqu`](../input-reference/aqu.md) | Depth to the aquifer bottom (m) |
| `dep_wt` | [`aquifer.aqu`](../input-reference/aqu.md) | Initial water table depth (m) |
| `no3_n` | [`aquifer.aqu`](../input-reference/aqu.md) | Initial nitrate-N concentration (mg/L) |
| `sol_p` | [`aquifer.aqu`](../input-reference/aqu.md) | Soluble P concentration of baseflow (mg/L) |
| `bf_max` | [`aquifer.aqu`](../input-reference/aqu.md) | Baseflow at which all linked channels receive flow (mm) |
| `alpha_bf` | [`aquifer.aqu`](../input-reference/aqu.md) | Baseflow recession constant (1/day) |
| `revap` | [`aquifer.aqu`](../input-reference/aqu.md) | Revap coefficient |
| `rchg_dp` | [`aquifer.aqu`](../input-reference/aqu.md) | Fraction of recharge lost to deep seepage |
| `spec_yld` | [`aquifer.aqu`](../input-reference/aqu.md) | Specific yield (m³/m³) |
| `hl_no3n` | [`aquifer.aqu`](../input-reference/aqu.md) | Half-life of nitrate in the aquifer (days) |
| `flo_min` | [`aquifer.aqu`](../input-reference/aqu.md) | Water table depth at or above which baseflow occurs (m) |
| `revap_min` | [`aquifer.aqu`](../input-reference/aqu.md) | Water table depth above which revap occurs (m) |

## Related pages

- [`aquifer.aqu`](../input-reference/aqu.md) and [connection files](../input-reference/con.md)
- [gwflow inputs](../input-reference/gwflow.md) and [gwflow outputs](../output-reference/gwflow.md)
- [Hydrology](hydrology.md) for percolation out of the soil profile
- [Channels](channels.md) for baseflow in the stream network
- [Aquifer, reservoir and plant output](../output-reference/aquifer-reservoir-plant.md)
- [Water allocation](../input-reference/water-allocation.md) for aquifer withdrawals

??? quote "Sources"

    Code at revision 62.0.1:

    - 1D aquifer daily routine: [`src/aqu_1d_control.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_1d_control.f90)
    - Initialisation of storage, recession and nitrate decay factors: [`src/aqu_initial.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_initial.f90)
    - Reader for `aquifer.aqu`: [`src/aqu_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu_read.f90)
    - Types `aquifer_database`, `aquifer_data_parameters`, `aquifer_dynamic`: [`src/aquifer_module.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aquifer_module.f90)
    - Aquifer-channel links: [`src/aqu2d_init.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu2d_init.f90), [`src/aqu2d_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/aqu2d_read.f90)
    - Hydrograph types `tot` and `rhg`: [`src/hyd_connect.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/hyd_connect.f90)
    - gwflow activation: [`src/basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90); inputs: [`src/gwflow_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_read.f90)
    - gwflow daily driver and solution: [`src/gwflow_simulate.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_simulate.f90), [`src/gwflow_lateral.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_lateral.f90)
    - gwflow sources and sinks: [`src/gwflow_rech.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_rech.f90), [`src/gwflow_gwet.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_gwet.f90), [`src/gwflow_channel_exch.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_channel_exch.f90), [`src/gwflow_satexcess.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_satexcess.f90), [`src/gwflow_tile.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_tile.f90), [`src/gwflow_reservoir.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_reservoir.f90), [`src/gwflow_canal.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/gwflow_canal.f90)

    Symbols and variables:

    | Symbol or column | Variable |
    |---|---|
    | $w_{rchg}$ | `aqu_d%rchrg` |
    | $S$ | `aqu_d%stor` |
    | $d_{wt}$ | `aqu_d%dep_wt` |
    | $Q_{gw}$ | `aqu_d%flo` |
    | $w_{seep}$ | `aqu_d%seep` |
    | $w_{revap}$ | `aqu_d%revap` |
    | $N_{aq}$ | `aqu_d%no3_st` |
    | `gw_flo`, `no3_n`, `sol_p`, `carbon` | `aqudb%flo`, `%no3`, `%minp`, `%cbn` |
    | `alpha_bf`, `revap`, `rchg_dp`, `spec_yld`, `hl_no3n` | `aqudb%alpha`, `%revap_co`, `%seep`, `%spyld`, `%hlife_n` |
    | $e^{-\alpha}$ and the nitrate decay factor | `aqu_prm%alpha_e`, `aqu_prm%nloss` |
    | pesticide groundwater mixing factor | `bsn_prm%pestgwfact` |
    | gwflow $h$, $K$, $S_y$, extinction depth | `gw_state%head`, `%hydc`, `%spyd`, `%exdp` |
    | gwflow $\Delta t$, $\delta$ | `gw_time_step`, `gw_delay` |

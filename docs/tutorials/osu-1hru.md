---
title: Osu_1hru walkthrough
description: A walk through the Osu_1hru reference dataset at revision 62.0.1. A single rice paddy HRU in South Korea with a routing unit, an aquifer and a channel, run end to end.
status: review
verified_against:
  - swatplus/refdata/Osu_1hru
  - src/basin_print_codes_read.f90
  - src/basin_read_objs.f90
  - src/basin_read_cc.f90
  - src/actions.f90
  - src/dtbl_lum_read.f90
  - src/plant_transplant_read.f90
  - src/mgt_read_puddle.f90
  - src/recall_read.f90
  - src/swift_output.f90
  - src/proc_hru.f90
  - src/main.f90.in
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

`Osu_1hru` is the second reference dataset in the SWAT+ source repository. It has one HRU of 10 ha, a rice paddy in South Korea with weather from the Imsil station, simulated from 2010 to 2023. Unlike [Ames_sub1](ames-sub1.md), the HRU belongs to a routing unit that sends its water to an aquifer and a channel, so the routing, aquifer and channel outputs have values. The folder is [`refdata/Osu_1hru`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Osu_1hru) in the source repository.

The rice is managed almost entirely by decision tables: weir height, paddy irrigation, puddling, planting, fertilizer and harvest are actions in [`lum.dtl`](../input-reference/dtl.md). This makes the dataset a small example of paddy management. Several shipped files are in older formats or are not read by 62.0.1, and the sections below say what the model does with each one.

## file.cio

```text
simulation        time.sim          print.prt         null              object.cnt        null
basin             codes.bsn         parameters.bsn    null
climate           weather-sta.cli   weather-wgn.cli   null              pcp.cli           tmp.cli           slr.cli           null              wnd.cli           null
connect           hru.con           null              rout_unit.con     null              aquifer.con       null              null              null        recall.con              null              null              null              chandeg.con
channel           initial.cha       null              null              null              nutrients.cha     channel-lte.cha   hyd-sed-lte.cha   null
reservoir         initial.res       null              null              sediment.res      nutrients.res     weir.res              wetland.wet       hydrology.wet
routing_unit      rout_unit.def     rout_unit.ele     rout_unit.rtu     null
hru               hru-data.hru      null
...
recall            recall.rec
...
aquifer           initial.aqu       aquifer.aqu
...
water_rights      null              null              null
...
hydrology         hydrology.hyd     topography.hyd    field.fld
structural        tiledrain.str     septic.str        filterstrip.str   grassedww.str     bmpuser.str
hru_parm_db       plants.plt        fertilizer.frt    tillage.til       pesticide.pes     null              null              null              urban.urb         septic.sep        snow.sno
ops               harv.ops          graze.ops         irr.ops           chem_app.ops      fire.ops          sweep.ops
lum               landuse.lum       management.sch    cntable.lum       cons_practice.lum  ovn_table.lum
chg               cal_parms.cal     calibration.cal   null ...
init              plant.ini         soil_plant.ini    om_water.ini      null ...
soils             soils.sol         nutrients.sol     null
decision_table    lum.dtl           res_rel.dtl       null              null
regions           ls_unit.ele       ls_unit.def       null ...          aqu_catunit.ele   null ...
```

The `basin` line already has three slots, with `null` for the carbon file. The `water_rights` line has three `null` names where 62.0.1 reads two, and the extra `null` is ignored. Both lines are read correctly (see [older file.cio files](../input-reference/file-cio.md#older-filecio-files)).

The `chg` line names [`calibration.cal`](../calibration/parameter-change-files.md). Its 13 rows change `cn2`, `petco`, `latq_co`, `alpha`, `epco`, `awc`, `esco`, `perco`, `cn3_swf`, `canmx`, `lat_len`, `revap_co` and `surlag` by a percentage for every object, and the model applies these changes at start-up (see [hard calibration](../calibration/hard-calibration.md)). The run below includes them.

Reference: [file.cio](../input-reference/file-cio.md).

## Simulation settings

### time.sim

```text
day_start  yrc_start   day_end   yrc_end      step
       1      2010      365       2023         0
```

1 January 2010 to 31 December 2023, 14 years, with a daily time step.

### print.prt

```text
nyskip      day_start  yrc_start  day_end   yrc_end   interval
3           0         0         0         0         1
aa_int_cnt
0
csvout        dbout         cdfout
n             n             n
soilout       mgtout        hydcon        fdcout
n             y             n             n
objects                  daily       monthly        yearly         avann
basin_wb                     n             n             y             y
basin_nb                     n             n             n             y
...
hru_pw                       n             n             n             y
hru_cb                       n             n             n             y
hru-lte_wb                   n             n             n             y
...
pest                         n             n             n             y
```

`nyskip` 3 leaves the first three years (2010 to 2012) out of the outputs, so the average annual files cover 2013 to 2023. `basin_wb` writes yearly and average annual files, and every other row writes average annual files only.

An older SWAT+ Editor wrote this file, and 62.0.1 reads some of it differently from its headers:

- On the `csvout dbout cdfout` line, the second value is read as `use_obj_lbls`. It is `n`, so the object rows are read by position, in the fixed order listed on the [print.prt page](../input-reference/print-prt.md#output-group-rows), and their names are not checked.
- On the `soilout mgtout hydcon fdcout` line, the first value is read as `crop_yld`. It is `n`, so no `crop_yld_*` files are written. `mgtout` is `y`, so `mgt_out.txt` is written.
- The fixed order has no `hru_cb` row. The `hru_cb` line is read as the `hru-lte_wb` row, and every later line is read one row early. All these lines have the same switches (`n n n y`), so in this file the shift changes nothing. The carbon rows can only be set by name, with `use_obj_lbls` = `y`.

### object.cnt

```text
name    ls_area  tot_area  obj  hru  lhru  rtu  mfl  aqu  cha  res  rec  exco  dlr  can  pmp  out  lcha  aqu2d  hrd  wro
Osu          10        10    4    1     0    1    0    1    0    0    0     0    0    0    0    0     1      0
```

Four objects: one HRU, one routing unit, one aquifer and one SWAT+ channel (`lcha`). The line ends before `hrd` and `wro`, which stay 0. `rec` is 0, so the recall object in [`recall.con`](../input-reference/con.md) is not built (see [Other files](#other-files)).

References: [time.sim](../input-reference/time-sim.md), [print.prt](../input-reference/print-prt.md), [object.cnt](../input-reference/object-cnt.md).

## Basin settings

```text
pet_file  wq_file  pet  event  crack  rtu_wq  sed_det  rte_cha  deg_cha  wq_cha  nostress  cn  c_fact  carbon  lapse  uhyd  sed_cha  tiledrain  wtable  soil_p  gampt  atmo_dep  stor_max  i_fpwet  gw_flow  idc_till
null      null     1    0      0      1       0        0        0        1       0         0   0       0       0      1     0        0          0       0       0      a         0         0        0        3
```

- `pet` 1: Penman-Monteith potential evapotranspiration, which uses solar radiation, humidity and wind.
- The sixth column has the old header `rtu_wq`, and 62.0.1 reads it as `swift_out`. Its value 1 makes every run write the SWIFT input files into a `SWIFT` folder at the end.
- `wq_cha` 1 is not used by 62.0.1.
- `carbon` 0: static soil carbon, so no carbon file is needed.
- `gampt` 0: curve number runoff.

References: [codes.bsn](../input-reference/codes-bsn.md), [parameters.bsn](../input-reference/parameters-bsn.md).

## Climate

[`weather-sta.cli`](../input-reference/cli.md#weather-stacli) defines one station:

```text
name              wgn     pcp            tmp            slr            hmd   wnd             wnd_dir  atmo_dep
s35610n127290e    Imsil   Imsilpcp.pcp   Imsiltmp.tmp   Imsilsol.slr   sim   Imsilwind.wnd   null     null
```

Precipitation, temperature, solar radiation and wind come from the four Imsil files, each listed in its index file ([`pcp.cli`](../input-reference/cli.md#observed-data-lists), [`tmp.cli`](../input-reference/cli.md#observed-data-lists), [`slr.cli`](../input-reference/cli.md#observed-data-lists), [`wnd.cli`](../input-reference/cli.md#observed-data-lists)). Relative humidity is generated (`sim`) from the monthly statistics of the `Imsil` record in [`weather-wgn.cli`](../input-reference/cli.md#weather-wgncli). The precipitation and temperature records run from 1981 to the end of 2023. The solar radiation and wind records end on day 304 of 2022, and the model generates those two variables for the rest of the run (see [weather outside the observed record](../input-reference/time-sim.md#weather-outside-the-observed-record)).

References: [weather-sta.cli](../input-reference/cli.md), [*.pcp](../input-reference/pcp.md), [*.tmp](../input-reference/tmp.md).

## HRU, routing unit, aquifer and channel

[`hru.con`](../input-reference/con.md) has one HRU of 10 ha with no outflow connections (`out_tot` = 0):

```text
id  name     gis_id  area  lat       lon        elev       hru  wst              cst  ovfl  rule  out_tot
 1  hru0001       1    10  35.65311  127.36763  350.96629    1  s35610n127290e     0     0     0        0
```

The HRU is the only element of routing unit `rtu001` ([`rout_unit.def`](../input-reference/units.md#rout_unitdef) and [`rout_unit.ele`](../input-reference/units.md#rout_unitele)). The routing unit collects its outflow and passes it on through [`rout_unit.con`](../input-reference/con.md): surface, lateral and tile flow (`tot`) to channel 1, and percolation (`rhg`) to aquifer 1. The aquifer returns its flow to the same channel through [`aquifer.con`](../input-reference/con.md). Channel 1 in [`chandeg.con`](../input-reference/con.md) has no outflow connection and is the basin outlet. The [connection files page](../input-reference/con.md#example) shows these three files.

[`aquifer.aqu`](../input-reference/aqu.md#aquiferaqu) has 21 records, `aqu011` to `aqu102` and `aqu_deep010`, all with the same parameters except the deep one. Only the first record is used: [`aquifer.con`](../input-reference/con.md) has one aquifer, and its `aqu` column points to row 1.

[`hru-data.hru`](../input-reference/hru.md) names the records the HRU uses:

```text
id  name      topo          hydro     soil        lu_mgt        soil_plant_init  surf_stor  snow     field
 1  hru0001   topohru0001   hyd0001   PadHOEGOG   rice140_lum   soilplant1       paddy0001  snow001  null
```

`surf_stor` = `paddy0001` points to a record in [`wetland.wet`](../input-reference/wet.md#wetlandwet) whose hydrology record is `paddy`, which makes the HRU a paddy with ponded water and a weir. The [wetland page](../input-reference/wet.md#example) explains the paddy records in this dataset. A misspelled name in any of the other columns would not be reported: the HRU would use the first record of that file (see [name lookup](../input-reference/hru.md#name-lookup)).

References: [*.con](../input-reference/con.md), [hru-data.hru](../input-reference/hru.md), [aquifer.aqu](../input-reference/aqu.md), [wetland.wet](../input-reference/wet.md).

## Land use and management

[`landuse.lum`](../input-reference/lum.md) links `rice140_lum` to the plant community `rice140_comm` in [`plant.ini`](../input-reference/ini.md#plantini) and to the schedule `rice140_rot` in [`management.sch`](../input-reference/management.md#managementsch), with curve number record `rc_strow_g`, conservation practice `cross_slope` and Manning's n record `convtill_res`. The plant community starts with no growing plant.

`rice140_rot` has one dated operation and seven decision tables:

```text
rice140_rot    1    7
	 plow
	 weir60r
	 weir0
	 pad_irr_r
	 puddle
	 pl_hv_rice
	 fert_paddy
manu      5          1      0     beef_salt   broadcast  12.9927
```

The dated operation applies 12.99 kg/ha of the manure `beef_salt` with `broadcast` on 1 May each year. The decision tables in [`lum.dtl`](../input-reference/dtl.md) do the rest:

| Table | Action |
|-------|--------|
| `plow` | Tillage with `fieldcultivat` early in the year, once the base-zero heat units pass 0.05. |
| `weir60r` | Raises the paddy weir to 60 mm on a day between day 120 and day 130. |
| `weir0` | Lowers the weir to 0 on a day between day 270 and day 280. |
| `pad_irr_r` | From May, while the weir is up and the ponded water is shallower than 60 mm, irrigates with the `ponding90` record of [`irr.ops`](../input-reference/ops.md#irrops). |
| `puddle` | After April, with the weir up, water ponded and less than 10 mm of rain that day, puddles the paddy with the `med_eff` record of [`puddle.ops`](../input-reference/management.md#puddleops). |
| `pl_hv_rice` | Plants `rice140` with the weir up once the base-zero heat units pass 0.15, and harvests and kills it once it has reached 1.15 times its heat units. |
| `fert_paddy` | Applies 100 kg/ha of `elem_n` and 20 kg/ha of `elem_p` early in the year, and 36 kg/ha of `elem_n` once the rice has passed half its heat units. |

Two shipped files that these tables use are not read as their authors intended:

- The `plant` action names the transplant record `tr_rice140`. That record is in `transplant.plt`, and 62.0.1 reads transplant records only from [`transplant.ops`](../input-reference/management.md#transplantops). The name is not found, no message is written, and the rice is planted from seed. `mgt_out.txt` still writes a `TRANSPLANT` line after each `PLANT` line. With the file renamed to [`transplant.ops`](../input-reference/management.md#transplantops), the model uses the record, and the planting and harvest dates change (see [transplant.ops](../input-reference/management.md#transplantops)).
- [`puddle.ops`](../input-reference/management.md#puddleops) has no title line, so the model reads its header line as the title and its first record, `high_eff`, as the header. The `puddle` table names `med_eff`, which is still read, so puddling works (see [puddle.ops](../input-reference/management.md#puddleops)).

References: [landuse.lum](../input-reference/lum.md), [management.sch](../input-reference/management.md), [decision tables](../input-reference/dtl.md), [*.ops](../input-reference/ops.md).

## Other files

- [`soils.sol`](../input-reference/sol.md), [`nutrients.sol`](../input-reference/ini.md#nutrientssol), [`soil_plant.ini`](../input-reference/ini.md#soil_plantini): soil `PadHOEGOG` and its initial nutrients. The [soils page](../input-reference/sol.md) and the [initial conditions page](../input-reference/ini.md) use Osu_1hru as their examples.
- [`channel-lte.cha`](../input-reference/sd-channel.md#channel-ltecha), [`hyd-sed-lte.cha`](../input-reference/sd-channel.md#hyd-sed-ltecha), [`initial.cha`](../input-reference/cha.md#initialcha), [`nutrients.cha`](../input-reference/sd-channel.md#nutrientscha): the channel record used by [`chandeg.con`](../input-reference/con.md). See [SWAT+ channels](../input-reference/sd-channel.md).
- [`recall.con`](../input-reference/con.md) and [`recall.rec`](../input-reference/recall.md#recallrec): `rec` is 0 in [`object.cnt`](../input-reference/object-cnt.md), so no recall object takes part in the run. The model still reads [`recall.rec`](../input-reference/recall.md#recallrec), because [`file.cio`](../input-reference/file-cio.md) names it, and opens the data file `RECYR.` named there. That file is not in the folder, so the run leaves an empty file of that name behind. See [recall](../input-reference/recall.md#example).
- [`pesticide.pes`](../input-reference/pes.md#pesticidepes): the half-life columns contain the old decay rates (0.007 and 0.05), which 62.0.1 reads as half-lives in days. No pesticides are simulated here, so they have no effect (see [pesticide.pes](../input-reference/pes.md)).
- [`salt_hru.ini`](../input-reference/salt.md#salt_hruini), [`salt_aqu.ini`](../input-reference/salt.md#salt_aquini), [`salt_channel.ini`](../input-reference/salt.md#salt_channelini): empty, and not used, because no salts are simulated (see [salts](../input-reference/salt.md)).
- [`calibration.cal`](../calibration/parameter-change-files.md) and [`cal_parms.cal`](../calibration/parameter-change-files.md): the parameter changes described under [file.cio](#filecio), in the format on the [parameter change files page](../calibration/parameter-change-files.md).

The shipped folder also contains output files left from runs with older revisions: `mgt_out.txt`, `erosion.txt`, `fort.2222`, the `*.swf` files at the top level and the `SWIFT` folder. A 62.0.1 run overwrites `mgt_out.txt`, `erosion.txt` and the files in `SWIFT`, and does not write the others.

## Running the model

From inside the folder:

```bash
path/to/swatplus-62.0.1-gnu-lin_x86_64-Rel
```

With one HRU the run takes a few seconds and writes a few megabytes. The screen shows the date being simulated, and `simulation.out` ends with:

```text
  Original Simulation           12  31  2023 Yr   14 of   14 Time  ...

 Execution successfully completed
```

Besides the output files, the run creates some empty files in the folder: `null`, `RECYR.`, [`wtps_wuses.wal`](../input-reference/water-allocation.md#wtps_wuseswal), [`cs_hru.ini`](../input-reference/cs.md#cs_hruini), [`cs_aqu.ini`](../input-reference/cs.md#cs_aquini) and [`cs_channel.ini`](../input-reference/cs.md#cs_channelini). They come from readers that create a file when the one they look for is missing, and they do not affect the results.

## Outputs

The values below are from a five-year run (2010 to 2014) of a copy of this folder, so the average annual values cover 2013 and 2014 only. A full run gives different numbers.

### diagnostics.out

```text
 DIAGNOSTICS.OUT FILE
```

No missing names or files are reported.

### checker.out

```text
sname       hydgrp      zmx   usle_k    sumfc     sumul  usle_p  usle_ls    esco    epco  cn3_swf  perco  latq_co  tiledrain
PadHOEGOG   C         750.0   0.0000   98.114   230.336  0.7500   0.1045  0.9500  0.5000   0.9500  0.9000   0.0100          0
```

`checker.out` is written before the changes in [`calibration.cal`](../calibration/parameter-change-files.md) are applied, so `esco`, `epco`, `cn3_swf` and `perco` are the values from [`hydrology.hyd`](../input-reference/hyd.md#hydrologyhyd). `usle_k` is 0, so the HRU produces no USLE erosion. The sediment in the outputs comes from puddling, which sets the sediment concentration of the ponded water.

### mgt_out.txt

The log of every operation and decision table action. The first season, shortened:

```text
 1  2010   2  21  beef_salt   FERT
 1  2010   2  21  beef_salt   FERT
 1  2010   3  24  fldcult     TILLAGE
 1  2010   5   1  beef_salt   MANURE
 1  2010   5   4  paddy       RESET WEIR HEIGHT (m)   0.06
 1  2010   5   4  ponding     PADDY IRRIGATION
 1  2010   5   5  puddle      PUDDLE
 1  2010   5   8  rice140     PLANT
 1  2010   5   8  rice140     TRANSPLANT
 1  2010   7  21  beef_salt   FERT-WET
 1  2010  10   3  paddy       RESET WEIR HEIGHT (m)   0.00
 1  2010  10   8  rice140     HARV/KILL
```

The `FERT` lines from the `fert_paddy` table show the name `beef_salt`, the schedule's dated operation, in place of `elem_n` and `elem_p`. The amounts in the `op_var` columns (100, 20 and 36 kg/ha) are the ones applied. `FERT-WET` means the fertilizer went into the ponded water. Between planting and harvest the log also has a `PLANT_ALREADY_GROWING` line on every day the `pl_hv_rice` table finds the planting conditions met.

The 2010 rice is harvested on 8 October. In the later years of this run it does not reach 1.15 times its heat units before winter and is harvested the following spring, a few days before the next planting. Read this file to check that the decision tables do what was intended.

### Water balance

`basin_wb_aa.txt` and `hru_wb_aa.txt` have the same values, because there is one HRU:

| precip | irr | surq_gen | perc | et | wet_evap | wet_oflo |
|--------|-----|----------|------|----|----------|----------|
| 1321.9 mm | 239.5 mm | 830.8 mm | 404.5 mm | 333.3 mm | 116.3 mm | 830.1 mm |

Most of the rain and irrigation leaves the paddy over the weir (`wet_oflo`), and this water is reported as surface runoff. `basin_wb_yr.txt` gives the same columns for each printed year.

Columns: [Water balance outputs](../output-reference/water-balance.md).

### Routing, aquifer and channel

- `ru_aa.txt` and `hydout_aa.txt`: the routing unit sends about 83,000 m³ a year to the channel and about 40,000 m³ of recharge to the aquifer. The units line of these files says m³/s, but the values are volumes in m³ (see [hydrographs](../output-reference/hydrographs.md)).
- `aquifer_aa.txt`: 404.5 mm of recharge and 379.5 mm of return flow to the channel (`flo_cha`).
- `channel_sd_aa.txt`: the channel inflow is the routing unit and aquifer flow together, about 0.004 m³/s on average.

Columns: [Aquifer, reservoir, plant](../output-reference/aquifer-reservoir-plant.md), [Channel, sediment, nutrient](../output-reference/channel-sediment-nutrient.md).

### Plant growth and the paddy

- `hru_pw_aa.txt`: plant biomass, yield, stresses and weather for the HRU. With `crop_yld` set to `n` in [`print.prt`](../input-reference/print-prt.md) there are no `crop_yld_*` files, so read the yield from this file.
- `wetland_aa.txt`: the ponded water of the paddy, with precipitation, evaporation, seepage and outflow in m³.
- `paddy_test.csv`: a daily table of the paddy (irrigation, seepage, weir height, water depth, sediment and nitrate). 62.0.1 writes it in every run.

## Changes to try

- Rename `transplant.plt` to [`transplant.ops`](../input-reference/management.md#transplantops) and compare the dates in `mgt_out.txt`.
- Set the first value on the `soilout` line of [`print.prt`](../input-reference/print-prt.md) to `b` to get the `crop_yld_*` files.
- Set `pet` to 2 in [`codes.bsn`](../input-reference/codes-bsn.md) for Hargreaves PET and compare `et` in `hru_wb_aa.txt`.
- Set the sixth value of [`codes.bsn`](../input-reference/codes-bsn.md) to 0 to stop writing the `SWIFT` folder.
- Shorten the run in [`time.sim`](../input-reference/time-sim.md), or switch on daily `basin_wb` output, as shown in the [cookbook](cookbook.md).

??? quote "Sources"

    - Dataset: [`refdata/Osu_1hru`](https://github.com/swat-model/swatplus/tree/62.0.1/refdata/Osu_1hru) at 62.0.1.
    - Run: a copy of the folder with `time.sim` shortened to 2010 to 2014 and the shipped output files removed, run with a 62.0.1 Linux build (Intel compiler) made from commit 97ca231 on 20 October 2026. That commit differs from the 62.0.1 tag only in gwflow, calibration and export coefficient code, which this dataset does not use. `diagnostics.out`, `checker.out`, `mgt_out.txt` and the output values are from that run. The transplant test used the same copy with `transplant.plt` copied to `transplant.ops`.
    - `print.prt` reading: [`basin_print_codes_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_print_codes_read.f90) reads line 7 into `pco%csvout`, `pco%use_obj_labels`, `pco%cdfout` and line 9 into `pco%crop_yld`, `pco%mgtout`, `pco%hydcon`, `pco%fdcout`. In fixed order, the row after `hru_pw` is `pco%wb_sd` (`hru-lte_wb`), which receives the Osu `hru_cb` line.
    - `object.cnt`: [`basin_read_objs.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_objs.f90) reads `bsn, sp_ob` in one list-directed read, and the short line ends the read at end of file.
    - `codes.bsn`: [`basin_read_cc.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/basin_read_cc.f90) reads the line into `bsn_cc`, whose sixth component is `swift_out`. The SWIFT files are written by [`swift_output.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/swift_output.f90).
    - `checker.out` and calibration: `checker.out` is written in [`proc_hru.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/proc_hru.f90), and `proc_cal` runs later in [`main.f90.in`](https://github.com/swat-model/swatplus/blob/62.0.1/src/main.f90.in).
    - Transplant lookup: [`dtbl_lum_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/dtbl_lum_read.f90) matches the `plant` action's file pointer against `transpl%name`, which [`plant_transplant_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/plant_transplant_read.f90) fills from `transplant.ops` only. In the `plant` case of [`actions.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/actions.f90), `mgt_transplant` is called only when `act_app` > 0, but the `TRANSPLANT` line is written whenever `pco%mgtout` = `y`.
    - `fertilize` action log: the `fertilize` case of `actions.f90` writes `mgt%op_char` in the name column of `mgt_out.txt`, where `mgt` is the HRU's current schedule operation (`sched%mgt_ops(hru%cur_op)`, set in `mgt_operatn`).
    - Recall: [`recall_read.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/recall_read.f90) reads `recall.rec` whenever the file exists, independent of the `rec` count, and opens each record's data file without checking that it exists, which creates `RECYR.`.
    - Puddle file: [`mgt_read_puddle.f90`](https://github.com/swat-model/swatplus/blob/62.0.1/src/mgt_read_puddle.f90) skips a title and a header line before the records.

---
title: What is SWAT+
status: review
verified_against:
  - swatplus/README.md
  - swatplus/CITATION.cff
  - swatplus/src/input_file_module.f90
  - swatplus/refdata/Ames_sub1
verified_at_commit: 6f515368525e7d84089ae0f9d33f4c9115de5679
---

The Soil and Water Assessment Tool Plus (SWAT+) is an open-source watershed model developed jointly by the USDA Agricultural Research Service ([USDA-ARS](https://www.ars.usda.gov)) and Texas A&M AgriLife Research, with contributions from Colorado State University, the USDA-ARS Hydrology and Remote Sensing Laboratory and other institutions.

SWAT+ simulates the quantity and quality of surface water and groundwater, from small watersheds to large river basins. It is used to evaluate the effects of land use, land management, soils and climate change on water resources.

## Background

Over more than two decades the original Soil and Water Assessment Tool (SWAT) became one of the most widely used watershed models in the world. Its many applications showed limits in how a watershed could be represented, and the additions made over the years left a code base that was hard to maintain and extend. SWAT+ is a restructured version of SWAT. Most of the process equations are the same, but the code is organized around objects and the input files are relational, which makes the model easier to maintain and lets new science be added as separate modules. SWAT+ also allows a more flexible spatial representation: landscape units, HRUs, aquifers, channels and reservoirs can be connected in any arrangement through connection files. The main differences are listed on [SWAT vs SWAT+](swat-vs-swatplus.md).

## Processes simulated

For each HRU, channel, aquifer, reservoir and wetland, SWAT+ keeps a daily mass balance of:

- water: precipitation, snow, evapotranspiration, surface runoff, lateral flow, percolation, groundwater flow and channel routing
- sediment: detachment, transport and deposition on the landscape and in channels
- nutrients: nitrogen and phosphorus cycling in the soil, plant uptake, transport with runoff and subsurface flow, and in-stream transformations
- carbon: soil organic carbon and residue pools
- pesticides and pathogens: application, decay and transport
- salts and other constituents
- plant growth: biomass, leaf area, yield, and water, nutrient and temperature stress

Management (planting, tillage, fertilizer and manure, irrigation, harvest, grazing) can follow fixed schedules or rules in decision tables. Water can be allocated between sources and users, and structural practices such as tile drains, filter strips and terraces can be represented.

Output can be written daily, monthly, yearly and as average annual values. The [Model Theory](../model-theory/index.md) section describes each process.

## Applications

- effects of management practices on water yield and water quality
- soil erosion and non-point source pollution
- crop yield response to climate and management
- watershed planning and total maximum daily load (TMDL) studies
- climate change impacts on water resources
- irrigation and water allocation

## Running the model

SWAT+ is a command-line program. It reads a folder of plain-text input files that describe the watershed, climate, soils, land use, management and simulation period, and writes plain-text (and optionally CSV) output files to the same folder.

Most users do not write the input files by hand. They use the supporting tools:

- **QSWAT+**, a QGIS plugin, delineates the watershed from a DEM, creates HRUs from soil, land use and slope maps, and writes the project database.
- **SWAT+ Editor** edits the inputs of a project, writes the input files and runs the model.
- **SWAT+ Toolbox** runs sensitivity analysis, calibration and other tasks on a finished project.

All three can be installed from [install.swat.tamu.edu](https://install.swat.tamu.edu). See [Install](../getting-started/install.md).

## Source and license

The source code is at [github.com/swat-model/swatplus](https://github.com/swat-model/swatplus) and is released under the GNU Lesser General Public License 2.1. See [Citing and license](citing-and-license.md).

??? quote "Sources"

    - [`README.md`](https://github.com/swat-model/swatplus/blob/62.0.1/README.md) and [`CITATION.cff`](https://github.com/swat-model/swatplus/blob/62.0.1/CITATION.cff) in the source repository at 62.0.1.
    - Input file groups: `src/input_file_module.f90`.

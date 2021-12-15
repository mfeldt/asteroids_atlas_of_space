# Mapping The Solar System - Blender Version

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Follow](https://img.shields.io/github/followers/mfeldt.svg?style=flat-square&logo=github&label=Follow)](https://github.com/mfeldt)

This repository is based on Eleanor Lutz' [Asteroids Atlas of Space](https://github.com/eleanorlutz/asteroids_atlas_of_space).  This version will slowly evolve into a Blender, 3D version of the map, which will eventually additionally include spacecraft from the HORIZON database.

For an excellent manual on what the different files are, and how they can be used, please refer to the original repository.


## Software

 - Blender 3.0.0
 - Python 3.9


## Modifications of the data download and format

### Python scripts instead of notebooks

Jupyter notebooks are a great way to document and also teach things. Simply re-running things is however sometimes more easy from the command line. Fortunately, Jupyter offers an easy way to convert a notebook to a python script - simply use `export as -> python` in jupyter, and the corresponding python script will be saved.

In this repository, you can find the converted scripts in the `python` subdirectory.

Running the script from the command line is then as simple as 

`python 1_split_query_datasets.py`

### Adding spacecraft

One of the major motivations to switch from simple 2D plotting to Blender was the possibility to render 3D animations, and by this means to also track spacraft.
Collecting available spacecraft data from JPL's HORIZONS system is handled by the script `3a_get_spacecraft.py`.  This makes use of the telnetlib, so it will only work if your computer can establish telnet connections to NASA, which is not always the case these days.  If you cannot achieve this, you can use 
[This list from John Mick](https://github.com/johnmick/nasa-jpl-horizons/blob/master/support-files/major-body-list.txt) and modify the script to skip the telnet stuff and read the file instead. Beware however, it's (at least) 6 years old.

Spacecraft data collected on 2021-12-15 are in `data/spacecraft.csv`.

### Trail lengths

## Scripting Blender


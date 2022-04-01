---
title: 'GHEtool: An open-source tool for borefield sizing in Python'
tags:
  - geothermal
  - energy
  - borefields
  - sizing
authors:
  - name: Wouter Peere^[corresponding author]
    orcid: 0000-0002-2311-5981
    affiliation: "1, 2" 
  - name: Tobias Blanke
    orcid: 0000-0003-1529-5529
    affiliation: 3 
affiliations:
 - name: Department of Mechanical Engineering, University of Leuven (KU Leuven), Leuven, Belgium
   index: 1
 - name: boydens engineering - part of Sweco, Dilbeek, Belgium
   index: 2
 - name: Solar-Institute Jülich, FH Aachen, Aachen, Germany
   index: 3
date: 28 February 2022
bibliography: Paper.bib

---

# Summary

GHEtool is a python package that contains all the functionalities needed to deal with borefield design. It is developed for both researchers and practitioners.
The core of this package is the automated sizing of borefield under different conditions.
The sizing of a borefield is typically slow due to the high complexity of the mathematical background. Because this tool has a lot of precalculated data, GHEtool can size a borefield in the order of tenths of milliseconds.
This sizing typically takes the order of minutes. Therefore, this tool is suited for being implemented in typical workflows where iterations are required.

GHEtool also comes with a graphical user interface (GUI). This GUI is prebuilt as an exe-file because this provides access to all the functionalities without coding.
A setup to install the GUI at the user-defined place is also implemented.


# Statement of need

The building sector uses 36 % of global energy and is responsible for 39 % of energy-related CO2 emissions when upstream power generation is included, with more than half of this energy used by space heating, space cooling and water heating [@IEA].
This sector should decarbonize to reach the climate goals in 2050. One of the promising ways to achieve this goal is by using shallow geothermal energy, thereby storing heat/cold in borefields, enabling seasonal thermal energy storage.
Therefore, much interest exists from academia and practitioners in this field.

One of the main challenges in this domain is to size a borefield, which is critical since borefields have a very high investment cost. So, we want them to be as small as possible to increase their feasibility.
Borefield sizing plays a central role in research. In particular, this is a topic for borefield load optimizing, studying sensitivity on borefield configurations, and integrating seasonal thermal energy storage in 5th generation district heating.

GHEtool is a python package with a graphical counterpart centred around borefield sizing and the evaluation of temperature evolution. 

The main advantage of GHEtool is that the ground response functions (gfunctions [@gfunctions]), which are needed to size a borefield, are already precalculated for more than 140 000 borefield – ground combinations. This precalculation saves much time.
This saving can take a couple of seconds to several minutes to calculate the gfunction for even one borefield. On the other hand, the tool provides the option to provide your gfunction data for your own custom borefield configuration. 

GHEtool aims to be used both by academic researchers in thermal systems integration and as a tool for educational purposes. It offers all the code and functions needed to size a borefield.
Also, it evaluates the mean fluid and borehole wall temperature evolution. Therefore, GHEtool is beneficial for research activities relating to fifth-generation district heating, seasonal thermal energy storage and sensitivity analysis on borefield parameters.

The tool comes with a graphical user interface. This interface is particularly beneficial for educational purposes, where students (and trained engineers) can play around to see how specific decisions influence the behaviour of the borefield.
It is used at the University of Leuven (Belgium) for all master thesis students that work in the geothermal study domain and in the course B-KUL-H0H00A Thermal Systems.

Furthermore, practitioners in the HVAC domain can use it to size their borefields correctly. They become more economically feasible and ready to play an essential role in the energy transition and  of the built environment.

# Comparison with existing tools

Multiple tools are available for sizing borefields:

- EED and GLHEPRO are commercial, standalone tools for borefields. They allow the user, a.o., to plot the mean fluid and borehole wall temperature evolution [@EED; @GLHEPRO]. Furthermore, the user can size a borefield [@EED; @GLHEPRO]. The automated sizing in EED sometimes leads to an undersized borefield [@Peere]. GLHEPRO does not have this problem since it calculates the temperature in every month [@GLHEPRO].
- geoSIM is a free tool for simulating and sizing borefields but only with one particular type of tubing (geoKOAX). It is also standalone [@geoSIM].
- Ground Loop Design software (GLDTM) ‘is the world’s leading commercial GHX software design tool’ [@igshpa]. It allows the user, a.o., to plot the mean fluid and borehole wall temperature evolution. Furthermore, the user can size the borefield.
- A commonly used package in the borefield domain is pygfunction. Pygfunction is an open-source python package to calculate the thermal response factors of the ground. This function forms the basis of many borefield simulation and sizing programs [@pygfunction]. With this python package, the data of the GHEtool was precalculated.

From the mentioned tools, only EED, GLHEPRO, geoSIM and GLDTM can size borefields, but none of them is open source nor easy to be integrated into your workflow since they are standalone. From all the borefield sizing tools listed above, only geoSIM is free, but it only works with one specific type of borehole tubing [@geoSIM].
(Bernier, 2019) has reviewed exhaustive literature of all existing borefield sizing methods and tools [@Bernier].

# Features
GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available both in the code environment and in the GUI. These features are:

- Sizing the borefield (i.e. calculating the required depth) for a given injection and extraction load for the borefield (two sizing methods are available). The tool can work with monthly and hourly load profiles
- Finding the optimal rectangular borefield configuration for a given heating and cooling load
- Optimising the load profile for a given heating and cooling load
- Using dynamically calculated borehole thermal resistance
- Calculating the temperature evolution of the ground for a given building load and borefield configuration
- Importing heating and cooling loads from *.csv and *.xlsx files
- Using your custom borefield configuration

# Acknowledgements

The first author would like to thank his supervisors Lieve Helsen and Wim Boydens and his coaches Damien Picard and Iago Cupeiro Figueroa for the guidance during his master thesis, which led to this package development.
The authors would like to thank Felix Arjuna and Iago Cupeiro Figueroa for the translation of the GUI.

# References

---
title: 'GHEtool: A open-source tool for borefield sizing in Python'
tags:
  - geothermal
  - energy
  - borefields
authors:
  - name: Wouter Peere^[corresponding author]
    orcid: 0000-0002-2311-5981
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Tobias Blanke
    orcid: 0000-0003-1529-5529
    affiliation: 3 (Multiple affiliations must be quoted)
affiliations:
 - name: Department of Mechanical Engineering, University of Leuven (KU Leuven), Leuven, Belgium
   index: 1
 - name: boydens engineering - part of Sweco, Dilbeek, Belgium
   index: 2
 - name: FH Aachen, Aachen, Germany
   index: 3
date: 01 February 2021
bibliography: paper.bib

---

# Summary

The building sector uses 36% of global energy and is responsible for 39% of energy-related
CO2 emissions when upstream power generation is included, with more than half of this energy
used by space heating, space cooling and water heating [IEA].

In order to reach the climate goals in 2050, this sector should be decarbonized.
A promising way to achieve this goal is by using shallow geothermal energy,
thereby storing heat/cold in borefields. They can deliver high efficiency heating when 
connected to a heat pump but, in the future even more important, they can cool buildings
passively, meaning that no compression step is needed like in the classical compression
cooling machines. The sizing of such borefields however is important due to
the high investment cost (due to drilling), but is on the other hand very complicated.
This is due to the intrinsic complexity of transient heat diffusion problems and
the requirement for the ground to stay within certain temperature limits.




# Statement of need

GHEtool is a python package that comes also with a graphical counterpart centered around
borefield sizing and the evaluation of temperature evolution.
There already are some tools available for sizing borefields like Earth Energy Designer [EED] and
GLHEPro [GLHEPro] but both of them are commercial tools and are stand alone. Therefore, it is
harder to integrate them within your own personal workflow. GHEtool solves this by providing
an open-source solution for borefield sizing and temperature evaluation.

The power of GHEtool lies in the fact that the ground response functions (gfunctions [gfunctions]),
which are needed in order to size a borefield, are already precalculated, for it can take up to a
couple of hours to evaluate them. On the other hand, the tool provides the option to provide your
own gfunction data for your own custom configuration. Both the precalculated functions and ones
custom ones, can be calculated using the pygfunction package [pygfunction].

GHEtool was designed to be used both by academic researchers in the field of thermal
system integration and as a tool for educational purposes. It offers all the code and
functions needed to size a borefield and to evaluate the temperature evolution and is therefore
useful for all research activities relating to fifth generation district heating, seasonal
thermal energy storage and sensitivity analysis on of the borefield parameters.

Since the tool comes with a graphical user interface, it is particulary useful for educational
purposes, where students (and trained engineers) can play around to see how certain decisions
influence the behaviour of the borefield. It is used at the University of Leuven for all
master thesis students that are in the geothermal study domain and in the course on
Thermal System Simulation and at the University Of Leuven (Belgium).

Futhermore, practitionars in the HVAC domain can use it to size their geothermal applications correctly.


# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

The first author would like to thank his supervisors Lieve Helsen and Wim Boydens
and his coaches Damien Picard and Iago Cupeiro Figueroa for the guidance during his
master thesis, which, eventually, led to this package.

# References
# fiber-photometry-analysis

Version 0.1.0

analyses data obtained by fiber photometry (Doric Lesnses) in 2 different channels, by timelocking them to a TTL pulse (medPC generated) that is on a 3rd channel

## Code summary

uses input file that has a time column, brain data in 2 different channels (channel 1 and 2 ) and TTL pulses in channel 3 column. 
TTL channel column has binary data: either 3 (TTL off) or 0 (TTL on--> specific behavior taking place). 
The shock script will timelock brain data (channel 1 and 2 ) around the time when TTL was on. Each time a TTL is on is a different trial.
Average as well as SEM for all trials will be calculated for each channel. 
It will plot individual trials as well as trial average+- SEM for each channel separately, allowing for visualisation of brain signal during a behavior.

*example plot:*
![exAvgPlotPic](https://github.com/lefkothea1/fiber-photometry-analysis/blob/main/docs/exAvgPlotPic.PNG)

## important info about script contents:
time is measured as samples/sec. 
this script works for aquisition rate 12kP/sec, and decimation 50 (every 50 values will be averaged in order to minimize file size)
this results in 230-240 points per sec

to define how much time before and after the onset of TTL/behavior you want to include in trials


### requirements:
This script was created in spyder v 3.3.6, using python  3.6.5 64-bit | Qt 5.9.6 | PyQt5 5.9.2 on  Windows 10 

### Dependencies:
* modules used:
  * pandas_v0.24.0
  * numpy_v1.19.2
  * matplotlib_v3.3.2
  * os
  * time

for complete list of all dependecies in the environment that script was created look at *docs/reports/environment dependencies for full environment reproducibility*

## How to install:

1) download spyder software, by following the instructions on the link below. Spyder wil be the software used to run the code in.
http://docs.spyder-ide.org/current/installation.html

2)Download code from github
from repository  
lefkothea1 /fiber-photometry-analysis , clock on green "Code" button and select "download as zip"
save the zip file, unzip in your computer using the available software.

3) open spyder
either drag and drop script "shock analysis2" into spyder or 
open it by clicking file>open on spyder GUI
click run or F5


## Project organization

```
.
├── .gitignore
├── CITATION.md
├── LICENSE.md
├── README.md
├── requirements.txt
├── bin                <- Compiled and external code, ignored by git (PG)
│   └── external       <- Any external source code, ignored by git (RO)
├── config             <- Configuration files (HW)
├── data               <- All project data, ignored by git
│   ├── processed      <- The final, canonical data sets for modeling. (PG)
│   ├── raw            <- The original, immutable data dump. (RO)
│   └── temp           <- Intermediate data that has been transformed. (PG)
├── docs               <- Documentation notebook for users (HW)
│   ├── manuscript     <- Manuscript source, e.g., LaTeX, Markdown, etc. (HW)
│   └── reports        <- Other project reports and notebooks (e.g. Jupyter, .Rmd) (HW)
├── results
│   ├── figures        <- Figures for the manuscript or reports (PG)
│   └── output         <- Other output for the manuscript or reports (PG)
└── src                <- Source code for this project (HW)

```


## License

This project is licensed under the terms of the [MIT License](/LICENSE.md)

## Citation

Please [cite this project as described here](/CITATION.md).

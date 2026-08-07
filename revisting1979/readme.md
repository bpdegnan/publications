# On the Temperature Dependence of Subthreshold Currents in MOS Electron Inversion Layers, Revisited

This directory contains the data and MATLAB analysis scripts associated with:

> Brian P. Degnan and Jennifer Hasler,
> “On the Temperature Dependence of Subthreshold Currents in MOS Electron Inversion Layers, Revisited,”
> *2016 IEEE International Symposium on Circuits and Systems (ISCAS)*, pp. 2074–2077.

[IEEE Xplore](https://ieeexplore.ieee.org/document/7538987/) · [DOI](https://doi.org/10.1109/ISCAS.2016.7538987)

## Overview

The paper revisits the temperature dependence of MOSFET subthreshold current originally discussed by Card and Ulmer in 1979.

The material in this directory includes:

* digitized data and analysis based on the Card and Ulmer paper;
* comparison data for a CD4007 device; and
* measured nFET data from a commercially available 350 nm process for several device geometries and temperatures.

## Repository Contents

### [`card1979/`](card1979/)

Data and scripts related to the 1979 Card and Ulmer paper.

| File                  | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| `card1979data.mat`    | Digitized data extracted from the plots in the Card and Ulmer paper. |
| `CD4007.mat`          | CD4007 measurement data used for comparison.                         |
| `runme.m`             | Reproduces the primary Card-data analysis and plots.                 |
| `runme_compare4007.m` | Compares the CD4007 measurements with the extracted Card data.       |

### [`nfetdata/`](nfetdata/)

Measured nFET data and analysis scripts for devices fabricated in a commercially available 350 nm process.

| File                   | Description                                                             |
| ---------------------- | ----------------------------------------------------------------------- |
| `nfetdata.mat`         | Measured gate-sweep data for multiple nFET geometries and temperatures. |
| `runme.m`              | Runs the primary analysis and generates the summary plots.              |
| `runme_short.m`        | Processes the `short` device dataset.                                   |
| `runme_min.m`          | Processes the `min` device dataset.                                     |
| `runme_square.m`       | Processes the `square` device dataset.                                  |
| `runme_long.m`         | Processes the `long` device dataset.                                    |
| `runme_originalplot.m` | Plots the original measured data.                                       |

## Requirements

* MATLAB
* A local copy of this repository

The scripts expect their corresponding `.mat` files to be in the same directory.

## Running the Analysis

Clone the repository:

```sh
git clone https://github.com/bpdegnan/publications.git
cd publications/revisting1979
```

Start MATLAB with `revisting1979` as the current directory.

To reproduce the Card-data analysis:

```matlab
cd card1979
runme
```

To compare the Card data with the CD4007 measurements:

```matlab
runme_compare4007
```

To analyze the measured 350 nm nFET data:

```matlab
cd ../nfetdata
runme
```

Each command generates one or more MATLAB figures.

## Citation

Please cite the associated ISCAS paper when using the data or scripts from this repository:

```bibtex
@inproceedings{degnan2016temperature,
  author    = {Degnan, Brian P. and Hasler, Jennifer},
  title     = {On the Temperature Dependence of Subthreshold Currents in {MOS} Electron Inversion Layers, Revisited},
  booktitle = {2016 IEEE International Symposium on Circuits and Systems ({ISCAS})},
  pages     = {2074--2077},
  publisher = {IEEE},
  year      = {2016},
  doi       = {10.1109/ISCAS.2016.7538987},
  url       = {https://doi.org/10.1109/ISCAS.2016.7538987}
}
```

## Original Card and Ulmer Reference

```bibtex
@article{card1979temperature,
  author    = {Card, H. C. and Ulmer, R. W.},
  title     = {On the Temperature Dependence of Subthreshold Currents in {MOS} Electron Inversion Layers},
  journal   = {Solid-State Electronics},
  volume    = {22},
  number    = {5},
  pages     = {463--465},
  month     = may,
  year      = {1979},
  doi       = {10.1016/0038-1101(79)90148-5},
  url       = {https://doi.org/10.1016/0038-1101(79)90148-5}
}
```

## Questions or Additional Data

For questions about these files, or to request supporting data from one of my other publications, please [open an issue](https://github.com/bpdegnan/publications/issues).

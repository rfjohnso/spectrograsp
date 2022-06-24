# SpectroGrasp 

SpectroGrasp is an extensible open-source tool for spectrum exploration aimed at easing the data labeling task.
- Innovative automated baud rate estimator for single-carrier modulations.
- Supports SigMF and HDF5 file formats.
- Integrated energy detection (both in time & frequency).
- Native ONNX inference support.

> Note: This software is still a work in progress and you might find unreported bugs errors. Feel free to contact us and help us make a better tool :)

## How to install 

You will need a python environment with `python3` (Python < 3.10 because some required packages are not available for newer versions and preferable Python > 3.6). We recommend using a virtual environment 
(`venv`, `virtualenv`, `conda`, `docker`, etc.) to avoid *dependency hell*. 

```shell
# Create a virtual environment in the target directory
python -m venv ./venv
# Activate virtual environment (bash)
source ./venv/bin/activate
```

### Dependencies

The main dependencies of this project are the following packages:

```shell
# Graphical user interface framework
PySide6
# Plotting library
pyqtgraph
# RF analisys tools
scipy
# Numerical tools
numpy
# DigitalRF format support
digital-rf
# SigMF format support
SigMF
```

You can use the requirements file to install it most of the dependencies using pip: 

```shell
pip install -r requirements.txt
```

#### SigMF

Currently, the SigMF version 1.0.0 is available in [pypi](https://pypi.org/project/sigmf/) but this version breaks our application because during the development of this software it was not available. To have support for SigMF  we need to install it from source. This is the [commit](https://github.com/gnuradio/SigMF/commit/4154335b1e22157c4ac86accdf2606d0cafc57ae) we used during development. 

You can install it in the python environment you are currently using doing the following:

```shell
# Clone the project in the default folder (SigMF)
git clone https://github.com/gnuradio/SigMF
# Checkout the desired commit
git checkout 4154335b1e22157c4ac86accdf2606d0cafc57ae
# Change directory inside the cloned repository
cd SigMF
# Execute project setup
python setup.py install
```

## Settings file

To generate a new settings file execute the following command

```shell
python settings.py
```

You can also rename the default configuration from `config.ini.default` to `config.ini`

## How to run

You can run Spectrograsp executing 
```shell
python main.py
```
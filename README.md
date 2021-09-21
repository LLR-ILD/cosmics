# cosmics

The initial idea is to use this code in two ways:

- as a package that can be imported in python scripts doing cosmic studies.
- as a command line executable, steered through a yaml file.

## Installation

For all installation methods, the standard Github ways
of specifying the code version apply.

### pip

```sh
pip install git+https://github.com/LLR-ILD/cosmics
```

### pipx

As higgstables is designed to be used from the command line,
this is the most straight forward way for obtaining the executable.
For information on (setting up) pipx, read [their repo](https://github.com/pypa/pipx).

```sh
pipx install git+https://github.com/LLR-ILD/cosmics cosmics
```

### For development

```sh
source init.sh
```

## Import as a package

TODO: Provide some features.

## Usage as a command line executable

```sh
cosmics cosmics.yaml
```

An example steering file is provided at [`example/cosmics.yaml`](example/cosmics.yaml).

## Usage example: Leaning tower of muons

The package is developed in order to facilitate a study about cosmic muons
that traverse the ECAL prototype in a straight trajectory but not orthogonal.

The study is currently developed within this repository,
in [`example/leaning-tower-of-muons`](example/leaning-tower-of-muons/README.md).

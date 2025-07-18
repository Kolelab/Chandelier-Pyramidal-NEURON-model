# Chandelier-Pyramidal-NEURON-model

## Chandelier–Pyramidal Cell NEURON Model

This repository contains a NEURON simulation model of a pyramidal cell (PyC) and a chandelier cell (ChC). It was developed to study how GABAergic inhibition at different synapse locations (AIS, soma, basal dendrite) affects PyC firing. 
---

## Project Structure

`model/`	: Cell definitions and synapse setup scripts 

`mod/` 		: NEURON `.mod` files for ion channels used by ChC and PyC

`tools/` 	: Utilities for measuring tau, Rin, spike frequency, AP dynamics to validate the model's biological accuracy

`experiments/`  : Full simulation protocols (e.g. current steps, random noise)


---

## Requirements

- Python 3.x
- NEURON with Python support
- Python libraries:
  - `numpy`
  - `matplotlib`
  - `pandas`

You can install the required libraries with:
```bash
pip install -r requirements.txt
```

## Compiling MOD Files (Required)
Before running any simulations, you must compile the mechanisms in the `mod/` folder.

### On macOS or Linux:
```bash
cd mod
nrnivmodl
```

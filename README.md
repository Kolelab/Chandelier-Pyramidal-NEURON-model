# Chandelier-Pyramidal-NEURON-model

This repository contains a NEURON simulation model of a pyramidal cell (PyC) and a chandelier cell (ChC). It was developed to study how GABAergic inhibition at different synapse locations (AIS, soma, basal dendrite) affects PyC firing. 
---

## Project Structure

`model/`	: Cell definitions and synapse setup scripts 

`morphologies/` : PyC and ChC reconstruction files, adjusted from Jiang et al. (2015), Science, 350(6264), used for model development.

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

## How to get started: 

### 1. Install Python

Download and install Python from:  
https://www.python.org/downloads/  
Make sure to check **"Add Python to PATH"** during installation.

### 2. Install NEURON

Install NEURON with Python support:  
```bash
pip install neuron
```

## Compiling MOD Files (Required)
Before running any simulations, you must compile the mechanisms in the `mod/` folder.

### On macOS or Linux:
```bash
cd mod
nrnivmodl
```
### On Windows:
- Open the "NEURON Command Prompt" (installed with NEURON)
- Navigate to the mod folder using cd
- Run:

```bash
mknrndll
```

## Running Simulations
Run any script in the experiments/ or tools/ folder, for example:

```bash
python -i experiments/trainofspikes_simulation.py
```

### Important tips:
- Make sure you run this from the root folder (where the compiled mod/ mechanisms are located), or copy the nrnmech.dll or x86_64/ folder to the same folder as your script.
- Use the -i flag if you want to keep the Python session interactive, allowing you to work with the NEURON GUI windows (e.g., Shape, Voltage Graph, RunControl), after the script runs.

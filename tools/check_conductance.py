from neuron import h, gui
from neuron.units import ms, mV
from cells_def import Cell
import numpy as np 
from synapse_general import connect_boutons, default_syn_weight

# Load NEURON's standard run library
h.load_file("stdrun.hoc")

# Create the Chandelier and Pyramidal cells
chc_cell = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")
pyr_cell = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")

# Add channels
chc_cell.add_ih_channels()
chc_cell.add_sodium_channels()
chc_cell.add_potassium_channels()

pyr_cell.add_ih_channels()
pyr_cell.add_sodium_channels()
pyr_cell.add_potassium_channels()

# # Connect boutons from the ChC to the Pyr AIS
synapses = connect_boutons(chc_cell, pyr_cell)
for syn in synapses:
    syn.syn.e = -73 # pyr rests at -68 and we want a driving force of -4 mV

# Set temperature and simulation parameters
h.celsius = 34
h.tstop = 400  # Simulation time in ms
h.dt = 0.05  # Time step

# Define current clamp stimulation
stim_chc = h.IClamp(chc_cell.soma(0.5))
stim_chc.delay = 200 # ms
stim_chc.dur = 5  # ms

stim_pyr = h.IClamp(pyr_cell.soma(0.5))
stim_pyr.delay = 50  # ms
stim_pyr.dur = 300  # ms

# Recording vectors
t = h.Vector().record(h._ref_t)
v_chc = h.Vector().record(chc_cell.soma(0.5)._ref_v)
v_pyr = h.Vector().record(pyr_cell.soma(0.5)._ref_v)
v_pyr_ais = h.Vector().record(pyr_cell.axon[0](0.5)._ref_v)
i_chc = h.Vector().record(stim_chc._ref_i)
i_pyr = h.Vector().record(stim_pyr._ref_i)

def update_current():
    """Update stimulation amplitude interactively."""
    stim_chc.amp = chc_amp[0]
    stim_pyr.amp = pyr_amp[0]
    h.v_init = -90 * mV
    h.finitialize(h.v_init)

    h.run()
    graph1.flush()
    graph2.flush()
    graph3.flush()
    graph4.flush()

# GUI Panel
h.xpanel("Interactive VI Curve")
h.xlabel("Adjust Current Injection (nA)")
chc_amp = h.ref(0.3)
pyr_amp = h.ref(0.3)
h.xvalue("ChC Current", chc_amp, 0.1, update_current)
h.xvalue("Pyr Current", pyr_amp, 0.1, update_current)
h.xpanel()

# Graphs for voltage
graph1 = h.Graph()
graph1.size(0, h.tstop, -130, 50)
graph1.addvar("ChC Soma", chc_cell.soma(0.5)._ref_v, 2, 1)
h.graphList[0].append(graph1)

graph2 = h.Graph()
graph2.size(0, h.tstop, -130, 50)
graph2.addvar("Pyr Soma", pyr_cell.soma(0.5)._ref_v, 3, 1)
graph2.addvar("Pyr AIS", pyr_cell.axon[0](0.5)._ref_v, 4, 1)
h.graphList[0].append(graph2)

#Graphs for current
graph3 = h.Graph()
graph3.size(0, h.tstop, -0.5, 1)
graph3.addvar("ChC Current", stim_chc._ref_i, 2, 1)
h.graphList[0].append(graph3)

graph4 = h.Graph()
graph4.size(0, h.tstop, -0.5, 1)
graph4.addvar("Pyr Current", stim_pyr._ref_i, 3, 1)
h.graphList[0].append(graph4)

# Initialize and run first simulation
update_current()
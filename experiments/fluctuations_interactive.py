from neuron import h, gui
from neuron.units import ms, mV
from cells_def import Cell
import os

# Load NEURON mechanisms and morphology
h.load_file("stdrun.hoc")
h.load_file("import3d.hoc")

# Create cells
pyramidal_cell = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")

# Add channels
pyramidal_cell.add_sodium_channels()
pyramidal_cell.add_potassium_channels()
pyramidal_cell.add_ih_channels()

# Add fluctuting noise at the soma

pyr_fluct = h.Gfluct2(pyramidal_cell.soma(0.5))  # Apply to soma
pyr_fluct.delay = 100           # start noise at 100 ms
pyr_fluct.inhib = 1
pyr_fluct.g_e0 = 0.006 * 2.6
pyr_fluct.std_e = 0.0019 * 2.6
pyr_fluct.g_i0 = 0.044 
pyr_fluct.std_i = 0.0069 
pyr_fluct.E_i = -80
pyr_fluct.tau_e = 7.8
pyr_fluct.tau_i = 8.8
pyr_fluct.new_seed(1000)  # Set random seed for reproducibility


# --- Recording vectors ---
t = h.Vector().record(h._ref_t)
v_pyr_soma = h.Vector().record(pyramidal_cell.soma(0.5)._ref_v)

# Add synaptic input - can be commented out if not needed
# --- Load Chandelier Cell ---

chandelier_cell = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")
chandelier_cell.add_sodium_channels()
chandelier_cell.add_potassium_channels()
chandelier_cell.add_ih_channels()

# from synapse_general import connect_boutons, default_syn_weight 

# # Connect ChC boutons to Pyr soma at specific locations
# synapses = connect_boutons(chandelier_cell, pyramidal_cell)
# for syn in synapses:
#     syn.syn.e = -70 #setting the reversal potential

# stim_chc = h.IClamp(chandelier_cell.soma(0.5))
# stim_chc.delay = 90  # ms
# stim_chc.dur = 510   # ms
# stim_chc.amp = 0.3   # nA

# v_pyr_chc = h.Vector().record(chandelier_cell.soma(0.5)._ref_v)

# --- Simulation settings ---
h.v_init = -90
h.tstop = 700
h.dt = 0.05
h.celsius = 34

# --- Plot GUI Graphs ---

graph1 = h.Graph()
graph1.size(0, h.tstop, -120, 40)
graph1.addvar("Pyr Soma", pyramidal_cell.soma(0.5)._ref_v, 3, 1)
h.graphList[0].append(graph1)

# # can also be commented out if ChC activation is not necessary
# graph2 = h.Graph()
# graph2.size(0, h.tstop, -120,40)
# graph2.addvar("ChC Soma", chandelier_cell.soma(0.5)._ref_v, 3, 1)
# h.graphList[0].append(graph2)

# --- Plot Gfluct2 conductances in NEURON GUI ---
graph_ge = h.Graph()
graph_ge.size(0, h.tstop, 0, 0.1)  # Set y-axis range appropriately
graph_ge.addvar("g_e", pyr_fluct._ref_g_e, 2, 1)
# graph_ge.addvar("g_i", pyr_fluct._ref_g_i, 4, 1)
h.graphList[0].append(graph_ge)


# Run simulation
h.finitialize(h.v_init)
h.run()
graph1.flush()
# graph2.flush()

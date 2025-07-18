from neuron import h, gui
from neuron.units import ms, mV
from cells_def import Cell
import numpy as np
from synapse_general import connect_boutons, default_syn_weight

# Load NEURON's standard run library
h.load_file("stdrun.hoc")

# Create the Chandelier (ChC) and Pyramidal (Pyr) cells
chc_cell = Cell("C:/Users/user/Documents/NIN_internship/L23ChC-j140718b_ar_boutons.asc", "chc")
pyr_cell = Cell("C:/Users/user/Documents/NIN_internship/L23pyr-j150802c_ar.asc", "pyr")

# Add channels to both cells
chc_cell.add_ih_channels()
chc_cell.add_sodium_channels()
chc_cell.add_potassium_channels()

pyr_cell.add_ih_channels()
pyr_cell.add_sodium_channels()
pyr_cell.add_potassium_channels()

# chc_cell.translate_cell(dy=100)

# Set simulation parameters
h.celsius = 34
h.tstop = 300   # Simulation time in ms
h.dt = 0.05    # Time step

stim_chc = h.IClamp(chc_cell.soma(0.5))
stim_chc.delay = 100  # ms
stim_chc.dur = 100  # ms

stim_pyr = h.IClamp(pyr_cell.soma(0.5))
stim_pyr.delay = 50  # ms
stim_pyr.dur = 150    # ms

# Recording vectors
t = h.Vector().record(h._ref_t)
v_chc = h.Vector().record(chc_cell.soma(0.5)._ref_v)
v_pyr = h.Vector().record(pyr_cell.soma(0.5)._ref_v)


# Connect boutons from the ChC to the Pyr AIS
active_synapses = connect_boutons(chc_cell, pyr_cell)

# Global state for bouton toggling
all_active = False  # Start with inhibition OFF
gaba_reversal = h.ref(-70.0)

def update_current():
    """Update stimulation amplitudes and run simulation."""
    # Update reversal potential
    for syn in active_synapses:
        syn.syn.e = gaba_reversal[0]
    stim_chc.amp = chc_amp[0]
    stim_pyr.amp = pyr_amp[0]
    h.v_init = -90 * mV
    h.finitialize(h.v_init)
    h.run()
    graph1.flush()
    graph2.flush()

# Function to toggle all boutons at once
def activate_all_boutons():
    global all_active
    all_active = not all_active
    new_weight = default_syn_weight if all_active else 0.0
    for i, syn in enumerate(active_synapses):
        syn.netcon.weight[0] = new_weight
    state = 'Activated' if all_active else 'Deactivated'
    print(f"{state} all boutons")
    update_current()

# -------------------------------
# GUI Panel for Current Injection
# -------------------------------
h.xpanel("Interactive VI Curve")
h.xlabel("Adjust Current Injection (nA)")
chc_amp = h.ref(0.3)
pyr_amp = h.ref(0.4) # 0.3 for subthreshold stimulation, 0.45 for 50Hz spiking
h.xvalue("ChC Current", chc_amp, 0.1, update_current)
h.xvalue("Pyr Current", pyr_amp, 0.1, update_current)
h.xpanel()

# -------------------------------

# GUI Panel for Bouton Adjustment
# -------------------------------
h.xpanel("Bouton Adjustment")
h.xlabel("Activate boutons on/off:")
# Button to toggle all simultaneously
h.xbutton("Enable inhibition", activate_all_boutons)
h.xvalue("GABA Reversal (mV)", gaba_reversal, 10, update_current)
h.xpanel()

# -------------------------------
# Graphs for Voltage Recording
# -------------------------------
graph1 = h.Graph()
graph1.size(0, h.tstop, -120, 40)
graph1.addvar("ChC Soma", chc_cell.soma(0.5)._ref_v, 2, 1)
h.graphList[0].append(graph1)

graph2 = h.Graph()
graph2.size(0, h.tstop, -120, 40)
graph2.addvar("Pyr Soma", pyr_cell.soma(0.5)._ref_v, 3, 1)
h.graphList[0].append(graph2)

graph3 = h.Graph()
graph3.size(0, h.tstop, -120, 40)
graph3.addvar("ChC Bouton 1", chc_cell.axon[104](0.5)._ref_v, 4, 1)
graph3.addvar("ChC Bouton 2", chc_cell.axon[106](0.5)._ref_v, 5, 1)
graph3.addvar("ChC Bouton 3", chc_cell.axon[108](0.5)._ref_v, 6, 1)
h.graphList[0].append(graph3)

graph4 = h.Graph()
graph4.size(0, h.tstop, -120, 40)
graph4.addvar("Pyr AIS", pyr_cell.axon[0](0.5)._ref_v, 10, 1)
h.graphList[0].append(graph4)

# Graphs for Current Injection
graph5 = h.Graph()
graph5.size(0, h.tstop, -0.5, 1)
graph5.addvar("ChC Current", stim_chc._ref_i, 3, 1)
h.graphList[0].append(graph5)

graph6 = h.Graph()
graph6.size(0, h.tstop, -0.5, 1)
graph6.addvar("Pyr Current", stim_pyr._ref_i, 4, 1)
h.graphList[0].append(graph6)


# -------------------------------
# Initialize and run first simulation
# -------------------------------
update_current()

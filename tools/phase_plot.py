from neuron import h, gui 
from neuron.units import ms, mV
from cells_def import Cell
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# Load NEURON's standard run library
h.load_file("stdrun.hoc")

# Create the pyramidal and chandelier cells
pyramidal_cell = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")
chandelier_cell = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")

# Ensure soma sections exist
if not pyramidal_cell.soma or not chandelier_cell.soma:
    raise ValueError("Error: Soma section not found for one or both cells.")

# Add ion channels
pyramidal_cell.add_sodium_channels()
pyramidal_cell.add_potassium_channels()
pyramidal_cell.add_ih_channels()

chandelier_cell.add_sodium_channels()
chandelier_cell.add_potassium_channels()
chandelier_cell.add_ih_channels()

# Inject current into ChC soma
stim_chc = h.IClamp(chandelier_cell.soma(0.5))
stim_chc.delay = 50 # ms
stim_chc.dur = 5     # ms
stim_chc.amp = 0.3  # nA

# Inject current into Pyr soma
stim_pyr = h.IClamp(pyramidal_cell.soma(0.5))
stim_pyr.delay = 50 # ms
stim_pyr.dur = 5     # ms
stim_pyr.amp = 0.6  # nA

# Simulation parameters
h.v_init = -70  # Initial membrane potential
h.tstop = 100   # Simulation time in ms
h.dt = 0.01     # Time step (important for dV/dt accuracy)
h.celsius = 34  # Temperature

# Record voltage and dV/dt for both cells
t = h.Vector().record(h._ref_t)

v_pyr = h.Vector().record(pyramidal_cell.soma(0.5)._ref_v)
i_cap_pyr = h.Vector().record(pyramidal_cell.soma(0.5)._ref_i_cap)

v_chc = h.Vector().record(chandelier_cell.axon[1](0.5)._ref_v)
i_cap_chc = h.Vector().record(chandelier_cell.soma(0.5)._ref_i_cap)

# Run the simulation
h.finitialize(h.v_init)
h.run()

# Compute dV/dt for both cells using i_cap / cm
dvdt_pyr = np.array(i_cap_pyr) / pyramidal_cell.soma(0.5).cm
dvdt_chc = np.array(i_cap_chc) / chandelier_cell.soma(0.5).cm

dvdt_pyr_scaled = dvdt_pyr * 1000
dvdt_chc_scaled = dvdt_chc * 1000

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Chandelier Cell Phase Plot ---
plt.figure(figsize=(5, 4))
plt.plot(v_chc, dvdt_chc_scaled, 'r')
plt.xlabel('Voltage (mV)')
plt.ylabel('dV/dt (mV/ms)')
plt.title('Phase Plot - Chandelier')
plt.tight_layout()
plt.savefig(os.path.join(script_dir, "phase_plot_chc.svg"), format="svg")
plt.show()

# # Save Chandelier Cell data to CSV
# df_chc = pd.DataFrame({
#     "Voltage_mV": v_chc,
#     "dVdt_mV_per_ms": dvdt_chc_scaled
# })
# df_chc.to_csv(os.path.join(script_dir, "phase_plot_chc.csv"), index=False)

# --- Pyramidal Cell Phase Plot ---
plt.figure(figsize=(5, 4))
plt.plot(v_pyr, dvdt_pyr_scaled, 'b')
plt.xlabel('Voltage (mV)')
plt.ylabel('dV/dt (mV/ms)')
plt.title('Phase Plot - Pyramidal')
plt.tight_layout()
plt.savefig(os.path.join(script_dir, "phase_plot_pyr.svg"), format="svg")
plt.show()

# # Save Pyramidal Cell data to CSV
# df_pyr = pd.DataFrame({
#     "Voltage_mV": v_pyr,
#     "dVdt_mV_per_ms": dvdt_pyr_scaled
# })
# df_pyr.to_csv(os.path.join(script_dir, "phase_plot_pyr.csv"), index=False)

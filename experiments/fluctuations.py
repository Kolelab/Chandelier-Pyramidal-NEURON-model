from neuron import h, gui 
from neuron.units import ms, mV
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
from cells_def import Cell

import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))


# --- Load Cell and Mechanisms ---
h.load_file("stdrun.hoc")
h.load_file("import3d.hoc")

# Create pyramidal cell and add active channels
pyr = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")
pyr.add_sodium_channels()
pyr.add_potassium_channels()
pyr.add_ih_channels()

# --- Simulation Settings ---
h.v_init = -90
h.dt = 0.05
h.tstop = 600  # simulate 600 ms total
h.celsius = 34

# --- Function to apply noise to soma ---
def add_noise_to_soma(seed):
    gfluct = h.Gfluct2(pyr.soma(0.5)) # refer to the Gfluct .mod file for publication details
    gfluct.delay = 100           # start noise at 100 ms
    gfluct.inhib = 1
    gfluct.g_e0 = 0.006 * 2.1 # adjust to achieve desired spiking rate (note: original publication suggests that e/i ratio remains constant)
    gfluct.std_e = 0.0019 * 2.1
    gfluct.g_i0 = 0.044
    gfluct.std_i = 0.0069
    gfluct.E_i = -80
    gfluct.tau_e = 7.8
    gfluct.tau_i = 8.8
    gfluct.new_seed(seed)
    return gfluct

# Add synaptic input - can be commented out if not needed
# Load Chandelier Cell

chc = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")
chc.add_sodium_channels()
chc.add_potassium_channels()
chc.add_ih_channels()

from synapse_general import connect_boutons, default_syn_weight # change synapse file as needed

# Connect ChC boutons to Pyr soma at specific locations
synapses = connect_boutons(chc, pyr)
for syn in synapses:
    syn.syn.e = -70 # Setting the reversal potential

e_rev = syn.syn.e
print(f"ChC synaptic reversal potential: {e_rev} mV")

stim_chc = h.IClamp(chc.soma(0.5))
stim_chc.delay = 90  # ms
stim_chc.dur = 510   # ms
stim_chc.amp = 0.3   # nA

v_pyr_chc = h.Vector().record(chc.soma(0.5)._ref_v)


# --- Storage ---
spike_results = []
all_spike_times = []
first_spike_times = []

# --- Run Trials ---
n_trials = 10
noise_duration_ms = 500  # from 100 to 600 ms

for trial in range(n_trials):
    gfluct = add_noise_to_soma(seed=3000 + trial)

    t_vec = h.Vector().record(h._ref_t)
    v_vec = h.Vector().record(pyr.soma(0.5)._ref_v)

    apc = h.APCount(pyr.soma(0.5))
    apc.thresh = -20

    h.finitialize(h.v_init)
    h.run()

    t = np.array(t_vec)
    v = np.array(v_vec)

    # Spike detection
    crossings = np.where((v[:-1] < -20) & (v[1:] >= -20))[0]
    spike_times = t[crossings]
    all_spike_times.append(spike_times)

    isis = np.diff(spike_times) if len(spike_times) > 1 else []

    # Vm after noise onset
    v_mask = t > 100
    vm_mean = np.mean(v[v_mask])
    vm_std = np.std(v[v_mask])

    # Frequency
    spike_count = np.sum((spike_times >= 100) & (spike_times <= 1100))
    freq = spike_count / (noise_duration_ms / 1000)

    if len(spike_times) > 0:
        first_spike_times.append(spike_times[0])

    spike_results.append({
        "trial": trial + 1,
        "spike_times": spike_times,
        "spike_count": spike_count,
        "isi": isis,
        "vm_mean": vm_mean,
        "vm_std": vm_std,
        "frequency_hz": freq
    })

# Raster Plot - uncomment if needed to visualize spikes
# plt.figure(figsize=(12, 8))
# trial_spacing = 1.5
# y_positions = [trial_spacing * i for i in range(n_trials)][::-1]

# for i, spikes in enumerate(all_spike_times):
#     y = y_positions[i]
#     plt.vlines(spikes, y, y + 1.2, color='black', linewidth=3.0)

# # Dashed horizontal lines between trials
# for y in y_positions:
#     plt.hlines(y, 0, 1100, color='gray', linestyle='--', linewidth=0., alpha=0.5)

# yticks = [y + 0.6 for y in y_positions]
# yticklabels = [f"Trial {i+1}" for i in range(n_trials)]
# plt.yticks(yticks, yticklabels)
# plt.xlabel("Time (ms)")
# plt.ylabel("Trial")
# plt.title("Raster plot of soma spikes under noise")
# plt.xlim(0, 600)
# plt.tight_layout()
# plt.show()

# Summary Table
df = pd.DataFrame([{
    "Trial": res["trial"],
    "Spike Count": res["spike_count"],
    "Frequency (Hz)": res["frequency_hz"],
    "Vm Mean (mV)": res["vm_mean"],
    "Vm Std (mV)": res["vm_std"],
    "Spike Times (ms)": ", ".join([f"{st:.2f}" for st in res["spike_times"]])
} for res in spike_results])


print("\nSummary Table:")
print(df.to_string(index=False))
# --- Save Summary Table to Excel ---
filename = os.path.join(script_dir, f"spike_summary_dend40again.xlsx")
df.to_excel(filename, index=False)
print(f"\nSaved summary table to '{filename}'")




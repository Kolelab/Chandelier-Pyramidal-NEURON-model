from neuron import h, gui
import numpy as np
import matplotlib.pyplot as plt
from cells_def import Cell

# --------------------------------------------------------------------------
# 1) Basic Setup
# --------------------------------------------------------------------------
h.load_file("stdrun.hoc")  # NEURON standard run library

# Create cells
chc = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")
pyr = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")

# Ensure both cells have a soma section
if not chc.soma or not pyr.soma:
    raise ValueError("Error: Soma section not found in one of the cells.")

# Add ion channels
chc.add_sodium_channels()
chc.add_potassium_channels()
chc.add_ih_channels()

pyr.add_sodium_channels()
pyr.add_potassium_channels()
pyr.add_ih_channels() 

# --------------------------------------------------------------------------
# 2) Define Current Injection Protocol
# --------------------------------------------------------------------------
amps = np.arange(0, 2.1, 0.1)  
delay = 100     # ms: start injecting current at 100 ms
dur = 500       # ms: inject current for 100 ms
tstop = 700     # ms: total simulation time

h.v_init = -90  # Initial membrane potential (mV)
h.tstop = tstop
h.dt = 0.05
h.celsius = 34

# --------------------------------------------------------------------------
# 3) Run f–I Curve for Both Cells using APCount
# --------------------------------------------------------------------------
firing_rates_chc = []
firing_rates_pyr = []

for amp in amps:
    for cell, rates in zip([chc, pyr], [firing_rates_chc, firing_rates_pyr]):
        # Create IClamp
        stim = h.IClamp(cell.soma(0.5))
        stim.delay = delay
        stim.dur = dur
        stim.amp = amp

        # Create AP Counter
        ap_counter = h.APCount(cell.soma(0.5))
        ap_counter.thresh = -20  # Spike detection threshold
        
        # Run the simulation
        h.finitialize(h.v_init)
        h.run()
        
        # Get spike count
        spike_count = int(ap_counter.n)
        inject_duration_s = dur / 1000.0  # Convert to seconds
        rate_hz = spike_count / inject_duration_s if inject_duration_s > 0 else 0.0
        
        rates.append(rate_hz)
        print(f"Cell {cell} - Amplitude {amp:.2f} nA: {spike_count} spikes, {rate_hz:.1f} Hz")
        
        # Remove stimulus
        stim = None

# --------------------------------------------------------------------------
# 4) Plot the f–I Curves Side by Side
# --------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Chandelier Cell
axes[0].plot(amps, firing_rates_chc, 'o-', lw=2, label="Chandelier Cell")
axes[0].set_xlabel("Current Injection (nA)", fontsize=12)
axes[0].set_ylabel("Firing Rate (Hz)", fontsize=12)
axes[0].set_title("f–I Curve - ChC", fontsize=14)
axes[0].grid(True)

# Pyramidal Cell
axes[1].plot(amps, firing_rates_pyr, 'o-', lw=2, label="Pyramidal Cell", color='r')
axes[1].set_xlabel("Current Injection (nA)", fontsize=12)
axes[1].set_ylabel("Firing Rate (Hz)", fontsize=12)
axes[1].set_title("f–I Curve - Pyr", fontsize=14)
axes[1].grid(True)

plt.tight_layout()
plt.show()
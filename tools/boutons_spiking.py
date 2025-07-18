from neuron import h
import numpy as np
import matplotlib.pyplot as plt
from cells_def import Cell
import os

# Load necessary HOC files
h.load_file("stdrun.hoc")
h.load_file("import3d.hoc")

# Load ChC morphology
chc = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")
chc.add_ih_channels()
chc.add_sodium_channels()
chc.add_potassium_channels()

# Choose bouton sections
bouton_secs = [chc.axon[137], chc.axon[139], chc.axon[141], chc.axon[143], chc.axon[145],
               chc.axon[187], chc.axon[189], chc.axon[191], chc.axon[193], chc.axon[195],
               chc.axon[226], chc.axon[228], chc.axon[230], chc.axon[232],
               chc.axon[104], chc.axon[106], chc.axon[108], chc.axon[110], chc.axon[112], chc.axon[114],
               chc.axon[81], chc.axon[83], chc.axon[85], chc.axon[87], chc.axon[89],
               chc.axon[38], chc.axon[40], chc.axon[42], chc.axon[43]]
bouton_locs = [0.5] * len(bouton_secs)

# Record voltage at boutons
v_boutons = []
for sec, loc in zip(bouton_secs, bouton_locs):
    vec = h.Vector()
    vec.record(sec(loc)._ref_v)
    v_boutons.append(vec)

# Record voltage at soma
v_soma = h.Vector()
v_soma.record(chc.soma(0.5)._ref_v)

# Record time
t = h.Vector()
t.record(h._ref_t)

# Stimulate ChC soma
stim = h.IClamp(chc.soma(0.5))
stim.delay = 100  # ms
stim.dur = 5      # ms
stim.amp = 0.251  # nA

# Run simulation
h.celsius = 34
h.dt = 0.01
h.v_init = -90
h.finitialize(h.v_init)
h.tstop = 200
h.run()

# Define cartridges
cartridges = [
    [137, 139, 141, 143, 145],        # Cartridge 1
    [187, 189, 191, 193, 195],        # Cartridge 2
    [226, 228, 230, 232],             # Cartridge 3
    [104, 106, 108, 110, 112, 114],   # Cartridge 4
    [81, 83, 85, 87, 89],             # Cartridge 5
    [38, 40, 42, 43]                  # Cartridge 6
]

colors = ['tab:blue', 'tab:orange', 'tab:green',
          'tab:red', 'tab:purple', 'tab:brown']

# --- Plot bouton voltages over time ---
plt.figure(figsize=(12, 7))

time = np.array(t) - stim.delay

bouton_idx = 0
for cart_idx, cartridge in enumerate(cartridges):
    for _ in cartridge:
        plt.plot(time, v_boutons[bouton_idx], color=colors[cart_idx], label=f'Cartridge {cart_idx+1}' if bouton_idx == 0 else "")
        bouton_idx += 1

plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Bouton voltages grouped by cartridge')
plt.grid(False)
plt.tight_layout()
plt.show()

# --- Raster plot of bouton activation times with avg. velocity labels ---
threshold = -20  # mV
activation_times = []

for v in v_boutons:
    v_np = np.array(v)
    t_np = np.array(time)
    spike_idx = np.where(v_np > threshold)[0]
    if len(spike_idx) > 0:
        activation_times.append(t_np[spike_idx[0]])
    else:
        activation_times.append(None)

# Conduction velocities per bouton
h.define_shape()
h.distance(0, chc.soma(0.5))  # Set soma as origin

soma_v = np.array(v_soma)
soma_spike_idx = np.where((soma_v[:-1] < 0) & (soma_v[1:] >= 0))[0]
soma_spike_time = time[soma_spike_idx[0]] if len(soma_spike_idx) > 0 else None

bouton_velocities = []
bouton_distances = []

for idx, sec in enumerate(bouton_secs):
    if activation_times[idx] is not None and soma_spike_time is not None:
        delay = activation_times[idx] - soma_spike_time
        dist = h.distance(sec(0.5))  # µm
        if delay > 0:
            v = (dist / 1000) / delay  # mm/ms = m/s
            bouton_velocities.append(v)
            bouton_distances.append(dist)
        else:
            bouton_velocities.append(None)
            bouton_distances.append(None)
    else:
        bouton_velocities.append(None)
        bouton_distances.append(None)

# Compute average velocity per cartridge
avg_velocity_per_cartridge = []
bouton_idx = 0
for cartridge in cartridges:
    vels = []
    for _ in cartridge:
        v = bouton_velocities[bouton_idx]
        if v is not None:
            vels.append(v)
        bouton_idx += 1
    if vels:
        avg_velocity_per_cartridge.append(np.mean(vels))
    else:
        avg_velocity_per_cartridge.append(None)

# Plot raster + text
plt.figure(figsize=(10, 6))

bouton_idx = 0
for cart_idx, cartridge in enumerate(cartridges):
    spike_times = []
    for bouton_in_cart_idx in range(len(cartridge)):
        if activation_times[bouton_idx] is not None:
            y_shift = cart_idx + (bouton_in_cart_idx - (len(cartridge)-1)/2) * 0.15
            plt.plot(activation_times[bouton_idx], y_shift, 'o', color=colors[cart_idx])
            spike_times.append(activation_times[bouton_idx])
        bouton_idx += 1

    # Annotate average velocity
    if avg_velocity_per_cartridge[cart_idx] is not None and spike_times:
        x_text = np.mean(spike_times)
        y_text = cart_idx + 0.4
        plt.text(x_text, y_text, f"{avg_velocity_per_cartridge[cart_idx]:.2f} m/s",
                 ha='center', va='bottom', fontsize=10, color=colors[cart_idx])

plt.xlabel('Time (ms)')
plt.ylabel('Cartridge index')
plt.title('Bouton activation times per cartridge\n(with avg. conduction velocity)')
plt.yticks(range(len(cartridges)), [f'Cartridge {i+1}' for i in range(len(cartridges))])
plt.grid(True, alpha=0.5)
plt.tight_layout()
plt.show()

script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Combined plot: Soma + all boutons grouped by cartridge ---
plt.figure(figsize=(12, 7))

time = np.array(t) - stim.delay
v_soma_np = np.array(v_soma)

# Plot soma voltage
plt.plot(time, v_soma_np, label='Soma', color='black', linewidth=2, zorder=5)

# Plot all boutons, grouped by cartridge
bouton_idx = 0
for cart_idx, cartridge in enumerate(cartridges):
    for bouton_in_cart in range(len(cartridge)):
        plt.plot(time, v_boutons[bouton_idx],
                 color=colors[cart_idx],
                 linewidth=1,
                 alpha=0.7,
                 label=f'Cartridge {cart_idx+1}' if bouton_in_cart == 0 else "")
        bouton_idx += 1

plt.xlabel('Time (ms)')
plt.ylabel('Voltage (mV)')
plt.title('Somatic and bouton voltages grouped by cartridge')
plt.legend(loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(script_dir, "boutons.svg"), format="svg")
plt.show()


# --- Conduction velocity estimates per cartridge (average across boutons) ---
print("\n--- Conduction Velocity Estimates (per cartridge, averaged across boutons) ---")
cartridge_avg_lengths = []
cartridge_avg_delays = []
cartridge_avg_velocities = []

bouton_idx = 0
for cart_idx, cartridge in enumerate(cartridges):
    delays = []
    distances = []
    velocities = []

    for _ in cartridge:
        delay = None
        dist = bouton_distances[bouton_idx]
        vel = bouton_velocities[bouton_idx]

        if vel is not None and soma_spike_time is not None and activation_times[bouton_idx] is not None:
            delay = activation_times[bouton_idx] - soma_spike_time
            distances.append(dist)
            delays.append(delay)
            velocities.append(vel)

        bouton_idx += 1

    if velocities:
        avg_len = np.mean(distances)
        avg_delay = np.mean(delays)
        avg_vel = np.mean(velocities)

        cartridge_avg_lengths.append(avg_len)
        cartridge_avg_delays.append(avg_delay)
        cartridge_avg_velocities.append(avg_vel)

        print(f"Cartridge {cart_idx+1}: "
              f"Avg Path = {avg_len:.1f} µm, "
              f"Avg Delay = {avg_delay:.3f} ms, "
              f"Avg Velocity = {avg_vel:.2f} m/s")
    else:
        print(f"Cartridge {cart_idx+1}: No valid spike detected.")
        cartridge_avg_lengths.append(None)
        cartridge_avg_delays.append(None)
        cartridge_avg_velocities.append(None)




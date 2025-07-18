from neuron import h
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from cells_def import Cell
# Load NEURON's standard run library    
h.load_file("stdrun.hoc")
# Create the Pyramidal cell
pyr_cell = Cell("C:/Users/user/Documents/NIN_internship/L23pyr-j150802c_ar.asc", "pyr")

# 1. Define the hyperpolarizing current clamp at the soma
stim = h.IClamp(pyr_cell.soma(0.5))
stim.delay = 100  # ms
stim.dur = 200    # ms
stim.amp = -0.05  # nA (small hyperpolarizing step)

# 2. Set up recordings
t_vec = h.Vector().record(h._ref_t)
v_vec = h.Vector().record(pyr_cell.soma(0.5)._ref_v)

# 3. Run the simulation
h.tstop = 400
h.v_init = -90  # adjust as needed
h.finitialize(h.v_init)
h.run()

# 4. Convert recordings
t = np.array(t_vec)
v = np.array(v_vec)

# 5. Plot the voltage trace
plt.figure(figsize=(8,4))
plt.plot(t, v)
plt.xlabel('Time (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.title('Voltage Response to Hyperpolarizing Step')
plt.show()

# 6. Fit the exponential decay after the current is turned off
offset_time = stim.delay + stim.dur  # 100 + 200 = 300 ms
idx_offset = np.where(t >= offset_time)[0][0]

# Fit from offset_time to offset_time + 50 ms (adjust if needed)
fit_window = (t >= offset_time) & (t <= offset_time + 50)
t_fit = t[fit_window] - offset_time  # reset time to 0
v_fit = v[fit_window]

# 7. Define single exponential decay function
def exp_decay(t, V0, tau, Vinf):
    return Vinf + (V0 - Vinf) * np.exp(-t / tau)

# 8. Estimate initial parameters
V0_guess = v_fit[0]
Vinf_guess = v_fit[-1]
tau_guess = 20  # ms (initial guess)

# 9. Fit the data
popt, _ = curve_fit(exp_decay, t_fit, v_fit, p0=[V0_guess, tau_guess, Vinf_guess])
V0_fit, tau_fit, Vinf_fit = popt

print(f"Estimated tau: {tau_fit:.2f} ms")

# 10. Plot the fit
t_fine = np.linspace(0, 50, 500)
v_fitted = exp_decay(t_fine, V0_fit, tau_fit, Vinf_fit)

plt.figure(figsize=(8,4))
plt.plot(t_fit, v_fit, 'b.', label='Data')
plt.plot(t_fine, v_fitted, 'r-', label=f'Fit: tau={tau_fit:.2f} ms')
plt.xlabel('Time since current off (ms)')
plt.ylabel('Membrane Potential (mV)')
plt.legend()
plt.show()

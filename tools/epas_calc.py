""" This function is used to calculate the average leak conductance per section so that the membrane potential can balance to the desired resting potentials
adjusted from Yiota Poirazi, July 2001, poirazi@LNC.usc.edu """

from neuron import h, gui
from cells_def import Cell

# --- SET DESIRED RESTING POTENTIALS ---
target_vrest_chc = -84
target_vrest_pyr = -94

# --- LOAD CELLS ---
pyr = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")
chc = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")

h.v_init = -90  # Initial membrane potential
h.celsius = 34  # Temperature in Celsius

# --- ADD ACTIVE CHANNELS ---
for cell in [chc, pyr]:
    cell.add_ih_channels()
    cell.add_sodium_channels()
    cell.add_potassium_channels()

# --- BALANCE CHANNELS ---
for cell, vrest in [(chc, target_vrest_chc), (pyr, target_vrest_pyr)]:
    # Initialize the cell at the target resting potential
    h.finitialize(vrest)
    h.fcurrent()

    print(f"\n Balancing {cell.cell_name} at {vrest} mV")
    epas_by_type = {}

    # Loop through sections and balance the e_pas
    for sec in cell.all:
        for seg in sec:
            try:
                g_pas = seg.g_pas
                if not hasattr(seg, 'e_pas') or g_pas <= 0:
                    continue

                ina = seg.ina if h.ismembrane("na_ion", sec=sec) else 0
                ik = seg.ik if h.ismembrane("k_ion", sec=sec) else 0
                ih = seg.i_ih if h.ismembrane("ih", sec=sec) and hasattr(seg, 'i_ih') else 0
                v = seg.v

                total = ina + ik + ih + g_pas * v
                e_pas_calc = total / g_pas

                seg.e_pas = e_pas_calc

                sec_name = sec.name().split('.')[-1].split('[')[0]
                epas_by_type.setdefault(sec_name, []).append(seg.e_pas)

            except Exception as e:
                print(f"Error in {sec.name()}: {e}")

    # --- Print summary per section type ---
    print(f"Final e_pas values for {cell.cell_name} (balanced to {vrest} mV):")
    for sec_type, values in epas_by_type.items():
        avg = sum(values) / len(values)
        print(f"  {sec_type:<8} - avg e_pas = {avg:.2f} mV (n={len(values)})")

# Reset the membrane potential before moving to the next cell
h.finitialize()

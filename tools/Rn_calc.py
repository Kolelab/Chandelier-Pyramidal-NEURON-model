from neuron import h
from neuron.units import mV
from cells_def import Cell
import tkinter as tk

h.celsius = 34
h.v_init = -90


class SimulationGUI:
    def __init__(self, master,pyr_cell):
        self.master = master
        self.pyr_cell = pyr_cell
        #self.chc_cell = chc_cell
        master.title("NEURON Impedance Rin Calculator")

        self.compute_button = tk.Button(master, text="Compute Input Resistance", command=self.compute_input_resistance)
        self.compute_button.pack()

   
    """ Specify a location on the cell (e.g., the middle of the soma) where the measurement is made.    
    The tool “freezes” the current state of the cell’s properties (such as capacitance, conductance, and axial resistance) 
    and then computes a linearized system response.
    It then returns the impedance (or input resistance, when at 0 Hz) at that location. This impedance represents how much the voltage will 
    change per unit of injected current under the assumption of linearity. """

    def compute_input_resistance(self):
        R_in_pyr = self.compute_rn(self.pyr_cell)
        #R_in_chc = self.compute_rn(self.chc_cell)
        
        print(f"Pyramidal Cell Input Resistance (Impedance method): {R_in_pyr:.2f} MΩ")
        #print(f"Chandelier Cell Input Resistance (Impedance method): {R_in_chc:.2f} MΩ")
    
    def compute_rn(self, cell):
        """
        Uses NEURON's Impedance tool to compute the input resistance (Rin) at 0 Hz.
        This mimics the hoc code:
        
          objref zz
          zz = new Impedance()
          func rn() { local rn
            init()  // make sure all changes to g, c, ri etc. have taken effect
            soma zz.loc(0.5)  // sets origin for impedance calculations to middle of soma
            zz.compute(0)  // DC input R
            soma { rn = zz.input(0.5) }  // rn is input R at middle of the soma
            return rn
          }
        
        """
        zz = h.Impedance()
        zz.loc(cell.soma(0.5))  # Set the origin to the middle of the soma
        h.init()  # Ensure model parameters are updated
        zz.compute(0)  # Compute impedance at DC (0 Hz)
        rn = zz.input(0.5)  # Get the input resistance at the middle of the soma
        return rn

if __name__ == "__main__":
    # Load your cell models from the specified files
    pyramidal_cell = Cell("C:/Users/user/Documents/NIN/L23pyr-j150802c_ar.asc", "pyr")
    #chandelier_cell = Cell("C:/Users/user/Documents/NIN/L23ChC-j140718b_ar_boutons.asc", "chc")

    # Add channels as needed
    pyramidal_cell.add_sodium_channels()
    pyramidal_cell.add_potassium_channels()
    pyramidal_cell.add_ih_channels()

    # chandelier_cell.add_sodium_channels()
    # chandelier_cell.add_potassium_channels()
    # chandelier_cell.add_ih_channels()

    # Create a simple Tkinter GUI
    root = tk.Tk()
    gui = SimulationGUI(root, pyramidal_cell)
    root.mainloop()
from neuron import h
from cells_def import Cell

default_syn_weight = 0.004  # Default synaptic weight #based on Szabadics et al. (2006)(for a measure of GABA reversal at the AIS) and Tamas & Szabadics (2004) (for postsynaptic current conductances).

class Synapse:
    def __init__(self, presynaptic_cell, postsynaptic_cell, pre_section, post_fraction):
        """Create a synapse between a presynaptic bouton and a postsynaptic AIS location."""
        self.pre_section = pre_section  # bouton section from ChC
        self.post_section = postsynaptic_cell.axon[0]  # Pyramidal AIS

        if self.pre_section is None or self.post_section is None:
            raise ValueError("Error: Could not retrieve required sections for synapse.")

        # Create synapse at the specified fraction along the AIS
        self.syn = h.Exp2Syn(self.post_section(post_fraction))
        self.syn.tau1 = 1    # Rise time (ms)
        self.syn.tau2 = 10   # Decay time (ms)
        self.syn.e = -90    # Reversal potential (mV)

        # Connect the bouton (pre_section) to the synapse;
        # note that we use the same post_fraction to sample the voltage at the bouton.
        self.netcon = h.NetCon(self.pre_section(0.5)._ref_v, self.syn, sec=self.pre_section)
        self.netcon.threshold = -20  # AP threshold (mV)
        self.netcon.weight[0] = default_syn_weight

def connect_boutons(chc, pyr):
    """Connect ChC boutons to the Pyr soma at specific locations.
    """
    bouton_data = [
        # # Catrdidge 4:
        (chc.axon[104], 0.3),
        (chc.axon[106], 0.4),
        (chc.axon[108], 0.5),
        # (chc.axon[110], 0.6),
        # (chc.axon[112], 0.7),
        # (chc.axon[114], 0.8)
        # # Catride 2:
        # (chc.axon[187], 0.3),
        # (chc.axon[189], 0.4),
        # (chc.axon[191], 0.5),
        # (chc.axon[193], 0.6),
        # (chc.axon[195], 0.7),
        # # Catride 5:
        # (chc.axon[81], 0.3),
        # (chc.axon[83], 0.4),
        # (chc.axon[85], 0.5),
        # (chc.axon[87], 0.6)
    ]

    synapses = []
    for bouton, fraction in bouton_data:
        print(f"Connecting bouton {bouton.name()} to AIS at {fraction * pyr.axon[0].L} µm")
        synapses.append(Synapse(chc, pyr, bouton, fraction))
    return synapses

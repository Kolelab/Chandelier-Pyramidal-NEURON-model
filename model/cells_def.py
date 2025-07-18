import os
from neuron import h, gui, load_mechanisms
from neuron.units import mV, ms
import matplotlib.pyplot as plt
import tkinter as tk

h.load_file("stdrun.hoc")
h.load_file("import3d.hoc")

dll_path = "C:/Users/user/Documents/NIN/nrnmech.dll"

if os.path.exists(dll_path):
    h.nrn_load_dll(dll_path)
    print("Mechanisms loaded successfully!")
else:
    print(f"Error: {dll_path} not found!")

#Sodium and potassium channel densities for the ChC:
na_soma_chc = 1200    # Sodium density for soma
na_ais_chc = 18000    # Sodium density for AIS
na_dend_chc = 80     # Sodium density for dendrites
na_axon_chc = 1000 #Sodium density for axon (excluding AIS)

kv_soma_chc = 400 # potassium for soma
kv1_soma_chc = 600 # >>

kv_dend_chc = 100 # potassium for dendrites
kv1_dend_chc = 28  # Using kv1_soma channels

#ais
kv1_ais_chc = 2000 #using axonal Kv1
kv7_ais_chc = 400

#axon
kv_axon_chc = 50
kv1_axon_chc = 100 

#Sodium and potassium channel densities for the pyr:
na_soma_pyr	= 1200			
na_dend_pyr	= 30						
na_ais_pyr  = 10000
na_axon_pyr = 500

kv_soma_pyr = 50
kv1_soma_pyr = 250
kv7_soma_pyr = 15

kv_dend_pyr = 10
kv1_dend_pyr = 20 # Using kv1_soma channels
kv7_dend_pyr= 15

kv1_ais_pyr = 2200 #using axonal Kv1
kv7_ais_pyr = 150 #specific for ais

kv1_axon_pyr = 300

h('vShift_naischc = 12')
h('vShift_inact_naischc = 16')
h('vShift_nachc = 16')
h('vShift_inact_nachc = 20')

h('vShift_naispyr = 8')
h('vShift_inact_naispyr = 20')
h('vShift_napyr = 10')
h('vShift_inact_napyr = 20')

class Cell:
    def __init__(self, morphology_path, cell_name):
        self.morphology_path = morphology_path
        self.cell_name = cell_name
        self.all = h.SectionList()
        self.soma = None
        self.section_types = {}
        self.sections = {}
        self.load_morphology()
        self.discretize()
        self.add_passive_properties()

    def __str__(self):
        return f"{self.cell_name}"

    def load_morphology(self):
        cell = h.Import3d_Neurolucida3()
        cell.input(self.morphology_path)
        i3d = h.Import3d_GUI(cell, 0)
        i3d.instantiate(self)

        print(f"Loading morphology for {self.cell_name}:")
        for sec in self.all:  # Use self.all instead of h.allsec()
            sec_name = sec.name().split('.')[-1]
            custom_name = f"{self.cell_name}.{sec_name}"
            
            # Store the section with its custom name
            self.sections[custom_name] = sec
            
            if 'soma' in sec_name.lower():
                self.soma = sec
                print(f"  Soma found: {custom_name}")
            
            sec_type = sec_name.split('[')[0]
            if sec_type not in self.section_types:
                self.section_types[sec_type] = []
            self.section_types[sec_type].append(custom_name)

            # if self.cell_name == "chc" and sec_name == "axon[21]":
            #     sec.diam = 0.2  # Adjust diameter for ChC axon[21]
            
            #print(f"  Section added: {custom_name}")

        if self.soma is None:
            print(f"  Warning: No soma found for {self.cell_name}")
        
        # print(f"Total sections loaded for {self.cell_name}: {len(self.all)}")
        # print(f"Section types: {', '.join(self.section_types.keys())}")


    def discretize(self):
        for sec in self.all:
            if self.cell_name == "chc" and sec.name().endswith("axon[1]"):
                sec.nseg = int((sec.L/1) + 0.999)  # 1 segment per ~1 µm
                if sec.nseg % 2 == 0:
                    sec.nseg += 1  # Make sure nseg is odd
            elif self.cell_name == "pyr" and (sec.name().endswith("axon[0]") or sec.name().endswith("dend[12]")):
                sec.nseg = int((sec.L/1) + 0.999)
                if sec.nseg % 2 == 0:
                    sec.nseg += 1        
            elif "axon" in sec.name():
                sec.nseg = int((sec.L/10) + 0.999)  # 1 segment per ~10 µm
                if sec.nseg % 2 == 0:
                    sec.nseg += 1  # Make sure nseg is odd
            else:
                d_lambda = 0.1
                min_seg = 3
                nseg_calc = int((sec.L / (d_lambda * h.lambda_f(3000)) + 0.999) / 2) * 2 + 1
                sec.nseg = max(nseg_calc, min_seg)



    def add_passive_properties(self):
        if self.cell_name == "chc":
            Rm = 8000  # Membrane resistance in Ω·cm² for ChC
        elif self.cell_name == "pyr":
            Rm = 30000  # Membrane resistance in Ω·cm² for Pyramidal

        for sec in self.all:
            if self.cell_name == "chc":
                sec.Ra = 180  # Axial resistance in Ω·cm for ChC
                sec.cm = 1  # Specific membrane capacitance in µF/cm² for ChC
            elif self.cell_name == "pyr":
                sec.Ra = 180  # Axial resistance in Ω·cm
                sec.cm = 1  # Specific membrane capacitance in µF/cm²

            # Passive properties
            sec.insert('pas')
            sec.g_pas = 1 / Rm  # Passive conductance in S/cm²
            if self.cell_name == "chc": 
                sec.e_pas = -84  # Leak reversal potential in mV - based on calculation so that it can settle at -84
            elif self.cell_name == "pyr":
                sec.e_pas = -120 # Leak reversal potential in mV - based on calculation so that it can settle at -94 (but sits at -90)
                
    
        print(f"Passive properties added to {self.cell_name} with Rm = {Rm} Ω·cm²")

        
    def add_ih_channels(self):
        if self.cell_name == "chc":
            ih_value = 0.00005 # Ih conductance for ChC
        elif self.cell_name == "pyr":
            ih_value = 0.00005  # Ih conductance for Pyramidal

        for sec in self.all:
            sec.insert('ih')
            sec.gbar_ih = ih_value

        #print(f"Ih channels added to {self.cell_name} with gbar_ih = {ih_value}")


    def add_sodium_channels(self):
        for custom_name, sec in self.sections.items():
            sec_type = custom_name.split('.')[-1].split('[')[0]
            suffix_sd =  f"na{self.cell_name}" # Suffixes used for sodium channels in soma and dendrites 
            suffix_ais = f"nais{self.cell_name}" # Suffixes used for sodium channels in AIS
            suffix_axon = f"nax{self.cell_name}" # Suffixes used for sodium channels in axon

            # Determine densities based on cell type
            if self.cell_name == "chc":
                na_soma, na_dend, na_ais, na_axon = na_soma_chc, na_dend_chc, na_ais_chc, na_axon_chc
            elif self.cell_name == "pyr":
                na_soma, na_dend, na_ais, na_axon = na_soma_pyr, na_dend_pyr, na_ais_pyr, na_axon_pyr

            # Sodium channel insertion
            if 'soma' in sec_type:
                sec.insert(suffix_sd)
                setattr(sec, f'gbar_{suffix_sd}', na_soma)
            elif 'dend' in sec_type or 'apic' in sec_type:  # Dendrites and apical dendrites
                sec.insert(suffix_sd)
                setattr(sec, f'gbar_{suffix_sd}', na_dend)
            elif 'axon' in sec_type:
                if self.cell_name == "pyr" and custom_name.endswith('[0]'):  # AIS of pyramidal cell
                    sec.L = 25
                    sec.insert(suffix_ais)
                    setattr(sec, f'gbar_{suffix_ais}', na_ais)
                elif self.cell_name == "chc" and custom_name.endswith('[0]'):  # same properties as soma
                    sec.L = 1
                    sec.insert(suffix_sd)
                    setattr(sec, f'gbar_{suffix_sd}', na_soma)
                elif self.cell_name == "chc" and custom_name.endswith('[1]'):  # AIS of chandelier cell
                    sec.insert(suffix_ais)
                    setattr(sec, f'gbar_{suffix_ais}', na_ais)
                else:  # Axon excluding AIS
                    sec.insert(suffix_axon)
                    setattr(sec, f'gbar_{suffix_axon}', na_axon)

        print(f"Sodium channels added to {self.cell_name}")

    def add_potassium_channels(self):
        for custom_name, sec in self.sections.items():
            sec_type = custom_name.split('.')[-1].split('[')[0]

            # Determine densities based on cell type
            if self.cell_name == "chc":
                kv_soma, kv_dend, kv1_dend, kv1_ais, kv7_ais, kv_axon, kv1_axon = (
                    kv_soma_chc, kv_dend_chc, kv1_dend_chc, kv1_ais_chc, kv7_ais_chc, kv_axon_chc, kv1_axon_chc)
                kv7_soma, kv7_dend = 0, 0  # Chandelier cells don’t use Kv7 in soma/dendrites
            elif self.cell_name == "pyr":
                kv_soma, kv_dend, kv1_dend, kv1_ais, kv7_ais, kv_axon, kv1_axon, kv7_soma, kv7_dend = (
                    kv_soma_pyr, kv_dend_pyr, kv1_dend_pyr, kv1_ais_pyr, kv7_ais_pyr, kv1_axon_pyr, kv1_axon_pyr, kv7_soma_pyr, kv7_dend_pyr)

            # Potassium channel insertion
            if 'soma' in sec_type:
                sec.insert('Kv1S')
                sec.gbar_Kv1S = kv1_soma_chc*0.6 if self.cell_name == "chc" else kv1_soma_pyr*0.6
                sec.insert('Kv')
                sec.gbar_Kv = kv_soma
                sec.insert('Kv7_AIS')
                sec.gbar_Kv7_AIS = kv7_soma  # Now properly assigned

            elif 'dend' in sec_type or 'apic' in sec_type:  # Dendrites and apical dendrites
                sec.insert('Kv1S')
                sec.gbar_Kv1S = kv1_dend*0.6
                sec.insert('Kv')
                sec.gbar_Kv = kv_dend
                sec.insert('Kv7_AIS')
                sec.gbar_Kv7_AIS = kv7_dend  # Now properly assigned

            elif 'axon' in sec_type:
                if self.cell_name == "pyr" and custom_name.endswith('[0]'):  # AIS of pyramidal cell
                    sec.insert('Kv1')
                    sec.gbar_Kv1 = kv1_ais*0.6
                    sec.insert('Kv7_AIS')
                    sec.gbar_Kv7_AIS = kv7_ais
                elif self.cell_name == "chc" and custom_name.endswith('[0]'):  # same properties as soma
                    sec.insert('Kv1S')
                    sec.gbar_Kv1S = kv1_soma_chc*0.6
                    sec.insert('Kv')
                    sec.gbar_Kv = kv_soma
                elif self.cell_name == "chc" and custom_name.endswith('[1]'):  # AIS of chandelier cell
                    sec.insert('Kv1')
                    sec.gbar_Kv1 = kv1_ais*0.6
                    sec.insert('Kv7_AIS')
                    sec.gbar_Kv7_AIS = kv7_ais
                else:  # Axon excluding AIS
                    sec.insert('Kv1')
                    sec.gbar_Kv1 = kv1_axon*0.6

        print(f"Potassium channels added to {self.cell_name}")


    def apply_stimulus(self, delay, duration, amplitude):
        if self.soma is None:
            raise ValueError("Soma not found")
        stim = h.IClamp(self.soma(0.5))
        stim.delay = delay
        stim.dur = duration
        stim.amp = amplitude
        return stim

    def get_section(self, section_type, index=0):
        if section_type in self.section_types:
            if index < len(self.section_types[section_type]):
                return self.sections[self.section_types[section_type][index]]
        print(f"Warning: {section_type} section not found for {self.cell_name}.")
        print(f"Available section types: {', '.join(self.section_types.keys())}")
        return None

    def get_custom_name(self, section):
        for custom_name, sec in self.sections.items():
            if sec == section:
                return custom_name
        return "Unknown"













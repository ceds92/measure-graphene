# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 10:12:03 2024

@author: jced0001
"""

import pickle
import matplotlib.pyplot as plt

filename = '2024-03-26 02-02-51_Gr-SiO2-Si STM 77K anneal 670 K 180 min -70 to 0 lockin plus270deg.pk'

experiment = pickle.load(open(filename,'rb'))

"""
experiment is saved in a dictionary like this
experiment = {
    "Vb"  : Vb,         # Bias across the resistor + flake (V)
    "Vgi" : Vgi,        # Initial gate voltage (V) 
    "Vgf" : Vgf,        # Final gate voltage (V)
    "dVg" : dVg,        # Gate voltage step size (V)
    "dt"  : dt,         # Time to wait before changing gate voltage by dVg (s)

    "ts"  : ts,         # Time to settle before sampling
    "ns"  : ns,         # Number of samples
    "ds"  : ds,         # Time to wait between samples

    "Rb"  : Rb,         # Resistor value (used in calculation only) (ohm)

    "vg"  : vg,         # Gate voltage (x axis)
    "Rg"  : Rg,         # Resistance (y axis)

    "dmx" : dmx,        # Lockin signal x-channel
    "dmy" : dmy,        # Lockin signal y-channel
}
"""

Vg = experiment['vg']
Ic = experiment['dmx']

plt.figure()
plt.plot(Vg,Ic)
plt.xlabel("Vg (V)")
plt.ylabel("Ic (A)")
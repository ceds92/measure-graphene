# %%
import os
import nanonispy as nap
from scipy.signal import savgol_filter as savgol
import matplotlib.pyplot as plt
import numpy as np

path = "C:/Users/jced0001/Development/Data/Device/Graphene device chris gate spectra/"
sg_pts  = 5
sg_poly = 1
Vg = [0, -10, -20, -30, -40, -50, -55, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 55, 50, 40, 30, 20, 10, 0, -10, -20, -30, -40, -50, 0, 0, -30, 0]
start = 19
stop = 29

run = np.arange(start=start, stop=stop + 1)
# run = range(len(Vg))
I    = []
Vb   = []
dIdV = []
offset = 0.4e-9
files = os.listdir(path)
plt.figure()
for n,file in enumerate(files):
    if(not n in run): continue
    if(n == 28): continue
    dat = nap.read.Spec(path + file).signals
    Vb.append(dat['Bias calc (V)'])
    I.append(dat['Current (A)'])

    dV = Vb[-1][1] - Vb[-1][0]
    dIdV.append(savgol(I[-1],sg_pts,sg_poly,deriv=1,delta=dV))

    plt.plot(Vb[-1],dIdV[-1] + n*offset)
    print(n,Vg[n],file)
# %%

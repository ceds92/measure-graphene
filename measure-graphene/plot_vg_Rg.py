# %%
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter as savgol
mplibColours = plt.rcParams['axes.prop_cycle'].by_key()['color']

# Device on SiO2 - this is the same device that the capacitive current was measured on
# files = []
# files.append(["670 K 180min", "measure-graphene/2024-03-25 22-44-07_Gr-SiO2-Si STM 77K anneal 670 K 180 min -60 to 10.pk"])

files = []
files.append(["Pre-anneal", "2024-03-27 05-23-24_Grene-hBN-Grite STM 77K straight from ambient -1 V to 1 V.pk"])
files.append(["670 K 60min 6.8e-9", "2024-03-27 23-10-29_Grene-hBN-Grite STM 77K 60min 670K 6.8e-9 -1 V to 1 V.pk"])

fig = plt.figure()
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)
ax3 = ax2.twinx()
for f, file in enumerate(files):
    pk    = pickle.load(open(file[1],'rb'))
    label = file[0]

    Vb = pk['Vb']

    Vg = pk['vg']
    Rg = pk['Rg']
    Ig = Vb/Rg
    
    dIgdVg = savgol(Ig,5,1,deriv=1,delta=abs(Vg[0] - Vg[1]))

    Rg_norm  = Rg - np.min(Rg)
    Rg_norm /= np.max(Rg_norm)
    # plt.plot(Vg,Rg_norm,label=label)
    ax1.plot(Vg,Rg,label=label)

    ax2.plot(Vg,Ig)
    ax3.plot(Vg,dIgdVg,linestyle='dashed',color=mplibColours[f])


ax1.set_xlabel(r"$Vg$")
ax2.set_xlabel(r"$Vg$")
ax1.set_ylabel(r"$R$")
ax2.set_ylabel(r"$I (A)$")
ax3.set_ylabel(r"$dIdVg (A/V)$")
plt.legend()
# file = "2024-03-26 02-02-51_Gr-SiO2-Si STM 77K anneal 670 K 180 min -70 to 0 lockin plus270deg.pk"
# pk   = pickle.load(open(file,'rb'))
# Vg = pk['vg']
# dmx = pk['dmx']
# dmx_norm = dmx - np.min(dmx)
# dmx_norm /= np.max(dmx_norm)
# plt.plot(Vg,dmx_norm,label="dmodX +270deg")
# plt.legend()
# %%
import numpy as np
import pickle
import matplotlib.pyplot as plt

files = []
# files.append(["600 K 60 min", "2024-03-12 01-52-15_Gr-SiO2-Si STM 77K anneal DCA off -60 to 10.pk"])
# files.append(["600 K 16 hr 1.4e-9", "2024-03-22 00-03-05_Gr-SiO2-Si STM 77K anneal 600 K 16 hr -60 to 10.pk"])
# files.append(["650 K 60 min", "2024-03-21 03-29-28_Gr-SiO2-Si STM 77K anneal 650 K 60 min -60 to 10.pk"])
# files.append(["650 K 50 min 9.3e-10", "2024-03-21 04-49-22_Gr-SiO2-Si STM 77K anneal 650 K 60 min -60 to 10 post 100 V scare.pk"])
# files.append(["670 K 50 min", "2024-03-12 23-15-42_Gr-SiO2-Si STM 77K anneal 670 K 50 min -60 to 10.pk"])

files.append(["Rg","2024-03-25 22-44-07_Gr-SiO2-Si STM 77K anneal 670 K 180 min -60 to 10.pk"])

plt.figure()
for file in files:
    pk    = pickle.load(open(file[1],'rb'))
    label = file[0]

    Vg = pk['vg']
    Rg = 1/pk['Rg']

    Rg_norm  = Rg - np.min(Rg)
    Rg_norm /= np.max(Rg_norm)
    plt.plot(Vg,Rg_norm,label=label)

file = "2024-03-26 02-02-51_Gr-SiO2-Si STM 77K anneal 670 K 180 min -70 to 0 lockin plus270deg.pk"
pk   = pickle.load(open(file,'rb'))
Vg = pk['vg']
dmx = pk['dmx']
dmx_norm = dmx - np.min(dmx)
dmx_norm /= np.max(dmx_norm)
plt.plot(Vg,dmx_norm,label="dmodX +270deg")
plt.legend()
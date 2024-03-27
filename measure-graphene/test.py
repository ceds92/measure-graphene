# %%
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
from datetime import datetime

from nanonisTCP import nanonisTCP
from nanonisTCP.Bias import Bias
from nanonisTCP.UserOut import UserOut
from nanonisTCP.Signals import Signals
from nanonisTCP.LockIn  import LockIn

try:
    from pymeasure.instruments.keithley import Keithley2400
except:
    from pymeasure.instruments.keithley import Keithley2400

IP   = '130.194.165.179'
NTCP = nanonisTCP(IP,6501)

kth = Keithley2400("GPIB::1")

# %%
run_name = "Grene-hBN-Grite STM 77K straight from ambient -1 V to 1 V"
Vb  = 50e-3     # Bias across the resistor + flake (V)
Vgi = -1.0      # Initial gate voltage (V) 
Vgf = 1.0       # Final gate voltage (V)
dVg = 25e-3     # Gate voltage step size (V)
dt  = 0.2       # Time to wait before changing gate voltage by dVg (s)

ts  = 0.5       # Time to settle before sampling
ns  = 5         # Number of samples
ds  = 0.02      # Time to wait between samples

Rb = 100e3      # Resistor value (used in calculation only) (ohm)

useLockin = 0

bias    = Bias(NTCP)
userOut = UserOut(NTCP)
signals = Signals(NTCP)
lockin  = LockIn(NTCP)

compliance_current = 100e-6
kth.apply_voltage(voltage_range=5,compliance_current=compliance_current)
kth.ramp_to_voltage(0,10*abs(int(kth.source_voltage/dVg)),dt/10)
# kth.enable_source()

dmodX_idx = 86
dmodY_idx = 87
if(useLockin):
    lockin.ModOnOffSet(modulator_number=1, lockin_onoff=1)
    dmodX = signals.ValGet(dmodX_idx)
    dmoxY = signals.ValGet(dmodY_idx)

# %%
# Step 1: ramp gate voltage to initial bias, Vgi
kth.ramp_to_voltage(Vgi,10*int(abs(Vgi/dVg)),dt)

# %%
# Step 2: Sweep the gate voltage while measuring the flake resistance
N  = int((Vgf - Vgi)/dVg)
vg = np.linspace(Vgi,Vgf,N)
Rg = np.zeros_like(vg)
dmx = np.zeros_like(vg)
dmy = np.zeros_like(vg)
for n,Vg in enumerate(vg):
    kth.ramp_to_voltage(Vg,10,dt)

    time.sleep(ts)

    R_ratio = 0
    for s in range(ns):
        time.sleep(ds)
        
        R_ratio += signals.ValGet(31,wait_for_newest_data=True)/ns
    
    Rg[n] = Rb*R_ratio

    if(useLockin):
        dmx[n] = signals.ValGet(dmodX_idx)
        dmy[n] = signals.ValGet(dmodY_idx)
    
kth.ramp_to_voltage(0,10*int(abs(Vgf/dVg)),dt)

# kth.disable_source()
NTCP.close_connection()

plt.figure()
if(not useLockin):
    plt.plot(vg,Rg)

if(useLockin):
    dmxy = np.sqrt(dmx**2 + dmy**2)
    dmx_norm = dmx - np.min(dmx)
    dmx_norm /= np.max(dmx_norm)
    dmy_norm = dmy - np.min(dmy)
    dmy_norm /= np.max(dmy_norm)
    
    dmxy_norm = dmxy - np.min(dmxy)
    dmxy_norm /= np.max(dmxy_norm)
    plt.plot(vg,dmx_norm,label="dmodX")
    plt.plot(vg,dmy_norm,label="dmodY")
    plt.plot(vg,dmxy_norm, label="dmxy", linestyle='dashed')

plt.show()
# %%
# Save the experiment
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

time_string = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').replace(':','-')
pickle.dump(experiment,open(time_string + '_' + run_name + ".pk",'wb'))
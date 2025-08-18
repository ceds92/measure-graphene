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
from nanonisTCP.BiasSpectr import BiasSpectr

try:
    from pymeasure.instruments.keithley import Keithley2400
except:
    from pymeasure.instruments.keithley import Keithley2400

IP   = '130.194.165.179'
# IP   = '127.0.0.1'
NTCP = nanonisTCP(IP,6501)

kth = Keithley2400("GPIB::1")

# %%
run_name = "Grene-hBN-Grite STS Vg -1V to 1V N21"
Vgi = -1        # Initial gate voltage (V) 
Vgf = 1.0       # Final gate voltage (V)
dVg = 25e-3     # Gate voltage step size (V)
N   = 21        # Number of spectra to acquire between Vgi and Vgf
dt  = 0.2       # Time to wait before changing gate voltage by dVg (s)

ts  = 0.5       # Time to settle before sampling

useLockin  = 1
lockinAmp  = 10e-3
lockinFreq = 980

bias     = Bias(NTCP)
userOut  = UserOut(NTCP)
lockin   = LockIn(NTCP)
biasSpec = BiasSpectr(NTCP)

compliance_current = 100e-6
kth.apply_voltage(voltage_range=5,compliance_current=compliance_current)
kth.ramp_to_voltage(0,10*abs(int(kth.source_voltage/dVg)),dt/10)

if(useLockin):
    lockin.ModAmpSet(1,lockinAmp)
    lockin.ModPhasFreqSet(1,lockinFreq)
    lockin.ModOnOffSet(modulator_number=1, lockin_onoff=1)
# %%
# Step 1: ramp gate voltage to initial bias, Vgi
kth.ramp_to_voltage(Vgi,10*int(abs(Vgi/dVg)),dt)

# %%
# Step 2: Sweep the gate voltage and take a spectrum at each point
# N  = int((Vgf - Vgi)/dVg)
vg = np.linspace(Vgi,Vgf,N)
spectra = []
biasProps = biasSpec.PropsGet()
for n,Vg in enumerate(vg):
    kth.ramp_to_voltage(Vg,10,dt)
    time.sleep(ts)

    spectra.append(biasSpec.Start(get_data=True))
    time.sleep(ts)
    
kth.ramp_to_voltage(0,10*int(abs(Vgf/dVg)),dt)

# kth.disable_source()
NTCP.close_connection()

# %%
# Save the experiment
experiment = {
    "Vgi" : Vgi,        # Initial gate voltage (V) 
    "Vgf" : Vgf,        # Final gate voltage (V)
    "dVg" : dVg,        # Gate voltage step size (V)
    "dt"  : dt,         # Time to wait before changing gate voltage by dVg (s)

    "ts"  : ts,         # Time to settle before sampling

    "useLockin"  : useLockin,  # Lockin was used to aquire spectra?
    "lockinAmp"  : lockinAmp,  # Lockin amplitude
    "lockinFreq" : lockinFreq, # Lockin Frequency

    "vg"       : vg,       # Gate voltage (x axis)
    "spectra"  : spectra,  # Dictionary containing channels returned from bias spectroscopy experiment
    "biasProps": biasProps # Properties of the bias spectroscopy module during run
}

time_string = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').replace(':','-')
pickle.dump(experiment,open(time_string + '_' + run_name + ".pk",'wb'))
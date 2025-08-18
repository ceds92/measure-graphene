# %%
import numpy as np
import time
import pickle
from datetime import datetime

from nanonisTCP import nanonisTCP
from nanonisTCP.Bias import Bias
from nanonisTCP.UserOut import UserOut
from nanonisTCP.Signals import Signals
from nanonisTCP.LockIn  import LockIn
from nanonisTCP.BiasSpectr import BiasSpectr

"""
To use this code:
1) First set up these parameters in Nanonis:
    1) Setpoint current and bias
    2) Start and end bias for the sweep (make sure start bias is same as setpoint)
    3) Safer to enable backward sweep
    4) All other bspec parameters as you wish... Make sure to select the Acquisition Channels
2) Set IP to 127.0.0.1 if running this script on the same computer as Nanonis (otherwise the IP of the Nanonis PC on the network)
3) Set 'parameters'
4) Run the script

This script will acquire spectra at different gate voltages.
Note that it assumes the UserOut channels have been configured correctly.
"""
IP   = '127.0.0.1'
NTCP = nanonisTCP(IP,6503)

# %%
# Parameters
run_name = "Test"
Vgi = -1.0          # Initial gate voltage (V) 
Vgf = 1.0           # Final gate voltage (V)
dVg = 500e-3        # Gate voltage step size (V)
dt  = 0.15          # Time to wait before changing gate voltage by dVg (s)

gateChannel = 8     # UserOutput channel that controls the gate voltage 

useLockin = True    # Turn the lock-in on for measurements
lockinAmp = 5e-3    # Set the amplitude of the lock-in oscillation
lockinFrq = 977     # Set the frequency of the lock-in oscillation

save = True         # Save the data independently of nanonis?
# %%
# Functions
def rampGate(NTCP,bias,dt=0.5,db=0.01,userOutput=8):
    userOut = UserOut(NTCP)
    signals = Signals(NTCP)

    signalNames = signals.NamesGet()
    outputIndex = signalNames.index('Output ' + str(userOutput) + ' (V)')
    startBias   = signals.ValGet(outputIndex,wait_for_newest_data=True)

    if(abs(startBias - bias) < db):
        userOut.ValSet(userOutput,bias)
        return
        
    bb = np.arange(startBias,bias,np.sign(bias-startBias)*db)
    bb[-1] = bias
    for b in bb:
        time.sleep(dt)
        userOut.ValSet(userOutput,b)
        
    userOut.ValSet(userOutput,bias)

# %%
# Initialisation
bias    = Bias(NTCP)
userOut = UserOut(NTCP)
signals = Signals(NTCP)
lockin  = LockIn(NTCP)
bSpec   = BiasSpectr(NTCP)

rampGate(NTCP=NTCP,bias=0,dt=dt,userOutput=gateChannel)

dmodX_idx = 86
dmodY_idx = 87
if(useLockin):
    lockin.ModPhasFreqSet(modulator_number=1,   frequency=lockinFrq)
    lockin.ModAmpSet(modulator_number=1,        amplitude=lockinAmp)
    lockin.ModOnOffSet(modulator_number=1,      lockin_onoff=1)

# %%
# Step 1: ramp gate voltage to initial bias, Vgi
rampGate(NTCP=NTCP,bias=Vgi,dt=dt,userOutput=gateChannel)

# %%
# Step 2: Sweep the gate voltage while measuring the flake resistance
N  = int((Vgf - Vgi)/dVg) + 1
vg = np.linspace(Vgi,Vgf,N)
bSpecData = []

for n,Vg in enumerate(vg):
    print(n+1,"/",N)
    rampGate(NTCP=NTCP,bias=Vg,dt=dt,userOutput=gateChannel)
    time.sleep(1)
    
    if(save):
        bSpecData.append(bSpec.Start(get_data=True))
    else:
        bSpec.Start(get_data=False)
    
    
rampGate(NTCP=NTCP,bias=0,dt=dt,userOutput=gateChannel)

NTCP.close_connection()

# %%
# Save the experiment
experiment = {
    "Vgi" : Vgi,        # Initial gate voltage (V) 
    "Vgf" : Vgf,        # Final gate voltage (V)
    "dVg" : dVg,        # Gate voltage step size (V)
    "dt"  : dt,         # Time to wait before changing gate voltage by dVg (s)

    "vg"  : vg,         # Gate voltage (x axis)
    "spec": bSpecData   # Data
}

time_string = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').replace(':','-')
pickle.dump(experiment,open(time_string + '_' + run_name + ".pk",'wb'))
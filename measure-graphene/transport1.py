# %%
"""
This script performs a gate voltage sweep on a graphene device using a Keithley 2400
source meter to apply the gate voltage.
The drain-source voltage is set using the Nanonis Bias module.
The current through the device is measured using a lock-in amplifier via the Nanonis LockIn module.
"""
import numpy as np
import time
import pickle
from datetime import datetime
import matplotlib.pyplot as plt

from nanonisTCP import nanonisTCP
from nanonisTCP.Bias import Bias
from nanonisTCP.UserOut import UserOut
from nanonisTCP.Signals import Signals
from nanonisTCP.LockIn  import LockIn

try:
    from pymeasure.instruments.keithley import Keithley2400
except:
    from pymeasure.instruments.keithley import Keithley2400

IP   = '127.0.0.1'
NTCP = nanonisTCP(IP,6501)

# Set parameters
DeviceID = "IDS001" # Device ID for run name
Temperature = 290   # Temperature in K for run name

Vgi = -2            # Initial gate voltage (V) 
Vgf = 2.0           # Final gate voltage (V)
nVg = 10            # Number of gate voltage steps
dt  = 0.15          # Time to wait for gate voltage to settle before measuring current (s)
ns  = 10            # Number of samples to average for each measurement

R1 = 1e5            # Resistance in series with the device (Ohm)

lockinAmp = 10e-3   # Set the amplitude of the lock-in oscillation (V)
lockinFrq = 977     # Set the frequency of the lock-in oscillation (Hz)

keithley_step_delay = 0.10  # Delay between voltage steps when ramping (s)
keithley_step_size  = 50e-3 # Voltage step size when ramping (V)

back_sweep = True   # Perform backward sweep?
save = True         # Save the data?

# ###############################################################
# Initialise Nanonis modules
# ###############################################################
userOut = UserOut(NTCP)
signals = Signals(NTCP)
lockin  = LockIn(NTCP)

# ###############################################################
# Helper functions
# ###############################################################

# Ramp the gate voltage applied via the Keithley
def ramp_gate_voltage(keithley, V_start, V_end, step_size, delay):
    if V_end > V_start:
        V_range = np.arange(V_start, V_end + step_size, step_size)
    else:
        V_range = np.arange(V_start, V_end - step_size, -step_size)
    
    for V in V_range:
        keithley.source_voltage = V
        time.sleep(delay)
    keithley.source_voltage = V_end  # Ensure final voltage is set

# ###############################################################
# Initialise instruments
# ###############################################################

# Set lock-in parameters
lockin.ModAmpSet(1,lockinAmp)
lockin.ModPhasFreqSet(1,lockinFrq)
lockin.ModOnOffSet(modulator_number=1, lockin_onoff=1)

# Ramp gate voltage to initial value
keithley = Keithley2400("GPIB::25")
Vg_current = keithley.source_voltage
ramp_gate_voltage(keithley, Vg_current, Vgi, keithley_step_size, keithley_step_delay)
time.sleep(1)  # Wait a second to stabilise

# ###############################################################
# Start measurement
# ###############################################################
print("Starting measurement...")

I_values = []
Rg_values = [] # Graphene resistance values
dmodX_values = []
dmodY_values = []
Vg_range = np.linspace(Vgi, Vgf, nVg) if Vgf > Vgi else np.linspace(Vgi, Vgf, nVg)
if back_sweep:
    Vg_range = np.concatenate((Vg_range, Vg_range[::-1]))
    
for Vg in Vg_range:
    # Set gate voltage
    ramp_gate_voltage(keithley, keithley.source_voltage, Vg, keithley_step_size, keithley_step_delay)
    _ = keithley.current

    # Wait for dt seconds
    time.sleep(dt)
    
    # Read voltage across R1 from lockin (sum and square components)
    dmodX_idx = 86
    dmodY_idx = 87

    # Take ns samples and average
    dmodX = 0
    dmoxY = 0
    for _ in range(ns):
        time.sleep(0.01)
        dmodX += signals.ValGet(dmodX_idx) / ns
        dmoxY += signals.ValGet(dmodY_idx) / ns

    V_R1 = np.sqrt(dmodX**2 + dmoxY**2)  # Voltage across R1
    V_graphene = lockinAmp - V_R1  # Voltage across graphene device
    Rg = V_graphene / (V_R1 / R1)  # Graphene resistance
    Rg_values.append(Rg)

    I = np.sqrt(dmodX**2 + dmoxY**2) / R1  # Calculate current through device
    I_values.append(I)
    dmodX_values.append(dmodX)
    dmodY_values.append(dmoxY)
    print(f"Vg: {Vg:.3f} V, I: {I*1e9:.3f} nA")


lockin.ModOnOffSet(modulator_number=1, lockin_onoff=0)
ramp_gate_voltage(keithley, keithley.source_voltage, 0, keithley_step_size, keithley_step_delay)

NTCP.close_connection()

# ###############################################################
# Plot and save data
# ###############################################################

I_values = np.array(I_values)
dmodX_values = np.array(dmodX_values)
dmodY_values = np.array(dmodY_values)
plt.figure()
# plot the I-Vg curve on the left axis and Rg-Vg curve on the right axis
fig, ax1 = plt.subplots()
color = 'tab:blue'
ax1.set_xlabel('Gate Voltage Vg (V)')
ax1.set_ylabel('Current I (uA)', color=color)
ax1.plot(Vg_range, I_values*1e6, marker='o', color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax2.set_ylabel('Graphene Resistance Rg (Ohm)', color=color)  # we already handled the x-label with ax1
ax2.plot(Vg_range, Rg_values, marker='s', color=color)
ax2.tick_params(axis='y', labelcolor=color)
fig.tight_layout()  # otherwise the right y-label is slightly clipped

if save:
    run_name = f"{DeviceID}_{Temperature}K"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{run_name}.pkl"
    with open(filename, 'wb') as f:
        # dump the curve along with all measurement parameters
        pickle.dump({
            'Vg_range': Vg_range,
            'I_values': I_values,
            'Rg_values': Rg_values,
            'dmodX_values': dmodX_values,
            'dmodY_values': dmodY_values,
            'parameters': {
                'DeviceID': DeviceID,
                'Temperature': Temperature,
                'Vgi': Vgi,
                'Vgf': Vgf,
                'nVg': nVg,
                'dt': dt,
                'ns': ns,
                'R1': R1,
                'lockinAmp': lockinAmp,
                'lockinFrq': lockinFrq,
                'keithley_step_delay': keithley_step_delay,
                'keithley_step_size': keithley_step_size,
                'back_sweep': back_sweep
            }
        }, f)
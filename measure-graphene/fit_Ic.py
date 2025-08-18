# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:11:47 2024

@author: jced0001
"""
import numpy as np
import matplotlib.pyplot as plt

pi = np.pi
e = 1.6e-19
hbar = 4.14e-15/(2*pi)
vF = 1e6

energy = np.linspace(-0.6, 0.6, num=1000)

D = 2*abs(energy)/(pi * hbar**2 * vF**2)

Cqm = e * D

plt.figure()
plt.plot(energy,Cqm)

# %%
Cqm_uFcm2 = Cqm * 1e6 * 1e-4

eps0 = 8.85e-12
eps_sio2 = 3.9
d = 300e-9

Cox = eps0 * eps_sio2/d
Cox_uFcm2 = Cox * 1e6 * 1e-4

Ctot_uFcm2 = 1 / ( 1/(Cox_uFcm2) + 1/(Cqm_uFcm2) )


# Function to create a Gaussian
def gaussian(x, mu, sigma):
    return np.exp(-(x - mu)**2 / (2 * sigma**2))


sigma = 1e-3
gaussian_broadening = gaussian(energy, 0, sigma)

# Normalize Gaussian to ensure total area is 1
gaussian_broadening /= np.sum(gaussian_broadening)

# Convolve total capacitance with Gaussian
Ctot_broadened = np.convolve(Ctot_uFcm2, gaussian_broadening, mode='same')


plt.plot(energy,Ctot_uFcm2)
plt.plot(energy,Ctot_broadened)
plt.xlim([-0.3,0.3])
plt.show()

V0         = 0       # Gate voltage to get E_D to 0
eps_hBN    = 3.5     # Dielectric constant for hBN is between 3 and 4 https://www.nature.com/articles/nmat2968#Sec2 ref 30
eps_SiO2   = 3.9     # https://www.nature.com/articles/nmat2968#Sec2 (better references than this)
dhBN       = 15e-9   # hBN thicknesn gs
dSiO2      = 300e-9  # SiO2 thickness
unc        = 5e-9    # Uncertainty in dhBN

# Constants
hbar = 6.5821e-16
eps0 = 1.85e-12
pi   = np.pi
e    = 1.6e-19
gv   = 2

# Calculate the capacitance based on all of the constants
C  = 1/(dhBN/(eps0*eps_hBN) + dSiO2/(eps0*eps_SiO2))
Cl = 1/((dhBN+unc)/(eps0*eps_hBN) + dSiO2/(eps0*eps_SiO2))  # Lower-bound error
Cu = 1/((dhBN-unc)/(eps0*eps_hBN) + dSiO2/(eps0*eps_SiO2))  # Lower-bound error

# Calculate the gate-coupling constant, alpha
alpha   = C/e
alpha_l = Cl/e
alpha_u = Cu/e

sqrt = energy/(hbar * vF)
V = sqrt**2 / (pi * alpha)
V[energy<0] = -V[energy<0]

sigma = 1
gaussian_broadening = gaussian(V, 0, sigma)

# Normalize Gaussian to ensure total area is 1
gaussian_broadening /= np.sum(gaussian_broadening)

# Convolve total capacitance with Gaussian
Ctot_broadened = np.convolve(Ctot_uFcm2, gaussian_broadening, mode='same')

plt.figure()
plt.plot(V,Ctot_broadened)
plt.xlim([-100,100])
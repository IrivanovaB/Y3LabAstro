import json
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

flux_file = "fourth run.json"

# mosaic = fits.open('Fits_Data/mosaic.fits')
# header = mosaic[0].header


#Sky calibration correction (mags)              
# MAGZPT  =            2.530E+01 / 
# Photometric ZP (mags) for default extinction   
# MAGZRR  =            2.000E-02 / 
# Photometric ZP error (mags)                    
# PV2_1   =             1.00E+00 / &                                             
#  PV2_3   =             3.75E+02 / & 

magzrr = 2.530E+01
gain = 3.1
exposure_time = 720

with open(flux_file, "r") as file:
    data = json.load(file)


data = np.array(data, dtype=float)
fluxes = data[~np.isnan(data)]
fluxes = np.abs(fluxes)
#fluxes = fluxes[fluxes > 0]

fluxes = fluxes*gain/exposure_time

fluxes = np.log10(fluxes)
magnitudes = -2.5 * fluxes
magnitudes = magzrr - magnitudes 

plt.plot(fluxes, magnitudes, "x")
plt.grid()
plt.xlabel("Fluxes (in base 10 and corrected)")
plt.ylabel("Magnitude")
plt.title("Magnitude v Flux")
plt.show()


counts, bin, __ = plt.hist(magnitudes,  bins=np.arange(20, 40, 1), cumulative=True)
plt.semilogy()
plt.xlabel("Magnitudes")
plt.ylabel("Cumulative Count")
plt.show()


def line(x, m, c):
    y = x*m
    return y + c

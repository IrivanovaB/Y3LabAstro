import json
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

flux_file = "first non negative fluxes.json"

# mosaic = fits.open('Fits_Data/mosaic.fits')
# header = mosaic[0].header


#Sky calibration correction (mags)              
# MAGZPT  =            2.530E+01 / 
# Photometric ZP (mags) for default extinction   
# MAGZRR  =            2.000E-02 / 
# Photometric ZP error (mags)                    
# PV2_1   =             1.00E+00 / &                                             
#  PV2_3   =             3.75E+02 / & 

magzpt = 2.530E+01
gain = 3.1
exposure_time = 720


with open(flux_file, "r") as file:
    data = json.load(file)


data = np.array(data, dtype=float)
fluxes = data[~np.isnan(data)]
fluxes = np.abs(fluxes)
#fluxes = fluxes[fluxes > 0]

fluxes = fluxes * gain / exposure_time
magnitudes = magzpt - 2.5 * np.log10(fluxes)

# plt.plot(fluxes, magnitudes, "x")
# plt.grid()
# plt.xlabel("Fluxes (in base 10 and corrected)")
# plt.ylabel("Magnitude")
# plt.title("Magnitude v Flux")
# plt.show()


counts, bins = np.histogram(magnitudes,  bins=np.arange(10, 30, 0.5))

bins = (bins[1:] + bins[:-1]) / 2
plt.plot(bins, counts.cumsum(), '.')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("Cumulative N")
plt.savefig('figures/preliminary_count_plot', dpi=300)
plt.show()


def line(x, m, c):
    y = x*m
    return y + c

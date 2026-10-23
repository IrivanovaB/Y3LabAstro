import json
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

flux_file = "fluxes.json"
flux_err_file = "fluxes_err.json"

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
magerr = 2.000E-02
gain = 3.1
exposure_time = 720


with open(flux_file, "r") as file:
    fluxes = json.load(file)

with open(flux_err_file, "r") as file:
    fluxes_err = json.load(file)

fluxes = np.array(fluxes, dtype=float)
fluxes_err = np.array(fluxes_err, dtype=float)

fluxes_err = fluxes_err[~np.isnan(fluxes)]
fluxes = fluxes[~np.isnan(fluxes)]

fluxes_err = fluxes_err[fluxes > 0]
fluxes = fluxes[fluxes > 0]

fluxes = fluxes * gain / exposure_time
fluxes_err = fluxes_err * gain / exposure_time

magnitudes_err = - 2.5 / np.log(10) * fluxes_err / fluxes
magnitudes_err = np.sqrt(magerr**2 + magnitudes_err**2)
magnitudes = magzpt - 2.5 * np.log10(fluxes)

# plt.plot(fluxes, magnitudes, "x")
# plt.grid()
# plt.xlabel("Fluxes (in base 10 and corrected)")
# plt.ylabel("Magnitude")
# plt.title("Magnitude v Flux")
# plt.show()

plt.plot(magnitudes, magnitudes_err, 'x')
plt.xlabel('Apparent magnitude')
plt.ylabel('Uncertainty')
plt.ylim((-0.1, 1.5))
# plt.savefig('figures/magnitude_uncertainty', dpi=300)
plt.show()

bins = np.arange(np.min(magnitudes)-0.5, np.max(magnitudes)+0.5, 0.5)
counts, bins = np.histogram(magnitudes, bins=bins)

bins = (bins[1:] + bins[:-1]) / 2

plt.errorbar(bins, counts, yerr=np.sqrt(counts), fmt='x')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("N")
# plt.savefig('figures/count_plot', dpi=300)
plt.show()

plt.errorbar(bins, counts.cumsum(), yerr=np.sqrt(counts.cumsum()), fmt='x')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("Cumulative N")
# plt.savefig('figures/cumulative_count_plot', dpi=300)
plt.show()


def line(x, m, c):
    y = x*m
    return y + c

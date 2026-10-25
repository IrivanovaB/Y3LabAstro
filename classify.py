'''
A module for the galaxy number count.
'''

import json
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.stats import cumfreq


flux_file = "data runs/fluxes running.json"
flux_err_file = "data runs/fluxes_err running.json"

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
normalisation = 0.0564
#normalisation = 1


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

plt.plot(magnitudes, magnitudes_err, 'ko')
plt.grid()
plt.xlabel('Apparent magnitude')
plt.ylabel('Uncertainty')
plt.ylim((-0.1, 1.5))
# plt.savefig('figures/magnitude_uncertainty', dpi=300)
plt.show()

bins = np.arange(np.min(magnitudes)-0.5, np.max(magnitudes)+0.5, 0.5)
counts, bins = np.histogram(magnitudes, bins=bins)
# #counts, bins = cumfreq(magnitudes, numbins=len(bins))
# counts = np.cumsum(counts)
counts_err = np.sqrt(counts) / normalisation
counts = counts / normalisation
bins = (bins[1:] + bins[:-1]) / 2
counts_err = np.sqrt(counts)

plt.errorbar(bins, counts, yerr=counts_err, fmt='x')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("N")

# plt.ylabel("N (per deg\u00b2 per 0.5 mag)")
# plt.savefig('figures/count_plot', dpi=300)
plt.show()

counts = counts.cumsum()
counts_err = np.sqrt(counts)

def log_line(x, m, c):
    return 10**(x*m + c)

popt, pcov = optimize.curve_fit(
    log_line, xdata=bins[2:12], ydata=counts[2:12], sigma=counts_err[2:12]
)

print(f'slope = {popt[0]:.4f} +/- {np.sqrt(pcov[0][0]):.4f}')

plt.errorbar(bins, counts, yerr=counts_err, fmt='x')
line_x = bins[2:12]
line_x = np.append(line_x, 14)
line_x = np.append(line_x, 21)
plt.plot(line_x, log_line(line_x, *popt), label="Gradient = 0.42 ± 0.03")
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("Cumulative N")
plt.grid()
plt.legend(loc='lower right')
plt.title("Cumulative Count per Apparent Magnitudes")
plt.xlim((15, 20))
plt.ylim((10, 12000))
# plt.ylabel("Cumulative N (per deg\u00b2 per 0.5 mag)")
# plt.savefig('figures/cumulative_count_plot', dpi=300)
plt.show()



'''
A module for the galaxy number count.
'''

import json
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.stats import cumfreq


flux_file = "data/fluxes.json"
flux_err_file = "data/fluxes_err.json"
flux_file = "data/fluxes.json"
flux_err_file = "data/fluxes_err.json"


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

plt.hist(magnitudes_err)
plt.show()

# plt.plot(fluxes, magnitudes, "x")
# plt.grid()
# plt.xlabel("Fluxes (in base 10 and corrected)")
# plt.ylabel("Magnitude")
# plt.title("Magnitude v Flux")
# plt.show()

bins = np.arange(14, 24.5, 0.5)
magnitudes_err_binned = []

for b in bins[:-1]:
    err = magnitudes_err[(magnitudes > b) & (magnitudes < (b+0.5))]
    if len(err) == 0:
        magnitudes_err_binned.append(0)
    else:
        err = np.sqrt(np.sum(err**2)) / len(err)
        magnitudes_err_binned.append(err)

plt.plot(magnitudes, magnitudes_err, '.', ms=4, alpha=0.5, label='Source')
plt.xlabel('Apparent magnitude')
plt.ylabel('Magnitude uncertainty')
plt.legend()
# plt.savefig('figures/magnitude_uncertainty', dpi=300)
plt.show()

counts, bins = np.histogram(magnitudes, bins=bins)
# #counts, bins = cumfreq(magnitudes, numbins=len(bins))
# counts = np.cumsum(counts)
counts_err = np.sqrt(counts) / normalisation
counts = counts / normalisation
bins = (bins[1:] + bins[:-1]) / 2

plt.errorbar(bins, counts, xerr=magnitudes_err_binned, yerr=counts_err, fmt='.', capsize=4, label='Data')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("N (per deg\u00b2 per 0.5 mag)")
plt.legend()
# plt.savefig('figures/normalised_count_plot', dpi=300)
plt.show()

counts = counts.cumsum()
counts_err = np.sqrt(counts)

def log_line(x, m, c):
    return 10**(x*m + c)

popt, pcov = optimize.curve_fit(
    log_line, xdata=bins[4:12], ydata=counts[4:12], sigma=counts_err[4:12]
)

print(f'slope = {popt[0]:.4f} +/- {np.sqrt(pcov[0][0]):.4f}')

plt.errorbar(bins, counts, yerr=counts_err, fmt='.', capsize=4, label='Data')
plt.plot(bins[4:12], log_line(bins[4:12], *popt), label='Fit')
plt.semilogy()
plt.xlabel("Apparent magnitude")
plt.ylabel("Cumulative N (per deg\u00b2)")
plt.legend()
# plt.savefig('figures/normalised_cumulative_count_plot', dpi=300)
plt.show()

uncertainty_01 = magnitudes_err[(magnitudes > 16) & (magnitudes < 20)]
uncertainty_01 = (uncertainty_01 < 0.1).sum() / len(uncertainty_01)

print('STATISTCIS')
print(f'Slope = {popt[0]:.4f} +/- {np.sqrt(pcov[0][0]):.4f}')

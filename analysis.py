'''
A module for the galaxy number count plot.
'''

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize


# File paths.
flux_file = 'data/fluxes.json'
flux_err_file = 'data/fluxes_err.json'

with open(flux_file, 'r') as file:
    fluxes = json.load(file)

with open(flux_err_file, 'r') as file:
    fluxes_err = json.load(file)

# Constants.
magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720
normalisation = 0.0564

# Histogram bins.
bins = np.arange(14, 24.5, 0.5)


# Converts from pixel flux to apparent magnitude.
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

# Calculates the error in each magnitude bin.
magnitudes_err_binned = []
for b in bins[:-1]:
    err = magnitudes_err[(magnitudes > b) & (magnitudes < (b+0.5))]
    if len(err) == 0:
        magnitudes_err_binned.append(0)
    else:
        err = np.sqrt(np.sum(err**2)) / len(err)
        magnitudes_err_binned.append(err)

# Plots the uncertainty in the magnitude.
plt.plot(magnitudes, magnitudes_err, '.', ms=4, alpha=0.5, label='Source')
plt.xlabel('Apparent magnitude')
plt.ylabel('Magnitude uncertainty')
plt.legend()
# plt.savefig('figures/magnitude_uncertainty', dpi=300)
plt.show()

# Binning and normalisation.
counts, bins = np.histogram(magnitudes, bins=bins)
counts_err = np.sqrt(counts) / normalisation
counts = counts / normalisation
bins = (bins[1:] + bins[:-1]) / 2

# Plots the non-cumulative count plot.
plt.axvspan(16, 20, color='lightblue', alpha=0.3, label='Valid mag')
plt.errorbar(bins, counts, xerr=magnitudes_err_binned, yerr=counts_err,
             fmt='.', capsize=4, color='black', label='Data')
plt.semilogy()
plt.xlabel('Apparent magnitude')
plt.ylabel('N (per deg\u00b2 per 0.5 mag)')
plt.legend()
# plt.savefig('figures/normalised_count_plot', dpi=300)
plt.show()

# Cumulative counts.
counts = counts.cumsum()
counts_err = np.sqrt(counts)

# Line fitting.
def log_line(x, m, c):
    '''
    A straight line in a logged y-axis.
    '''
    return 10**(x*m + c)

popt, pcov = optimize.curve_fit(
    log_line, xdata=bins[4:12], ydata=counts[4:12], sigma=counts_err[4:12]
)

perr = np.sqrt(np.diag(pcov))
fit_plus = log_line(np.array([14, 22]), popt[0]+perr[0], popt[1]-perr[1])
fit_minus = log_line(np.array([14, 22]), popt[0]-perr[0], popt[1]+perr[1])

# Plots the cumulative count plot.
plt.axvspan(16, 20, color='lightblue', alpha=0.3, label='Valid mag')
plt.errorbar(bins, counts, yerr=counts_err, fmt='.',
             capsize=4, color='black', label='Data')
plt.plot(np.array([16, 20]), log_line(np.array([16, 20]), *popt),
         color='red', label='Fit ± σ')
plt.plot(np.array([14, 22]), log_line(np.array([14, 22]), *popt), '--',
         color='red')
plt.fill_between(np.array([14, 22]), fit_plus, fit_minus,
                 color='orange', alpha=0.4)
plt.semilogy()
plt.xlabel('Apparent magnitude')
plt.ylabel('Cumulative N (per deg\u00b2)')
plt.xlim(14, 24)
plt.ylim(top=2e4)
plt.legend()
# plt.savefig('figures/normalised_cumulative_count_plot', dpi=300)
plt.show()

# Fit result.
print('STATISTCIS')
print(f'Slope = {popt[0]:.4f} +/- {np.sqrt(pcov[0][0]):.4f}')
print(f'y-intercept = {popt[1]:.4f} +/- {np.sqrt(pcov[1][1]):.4f}')

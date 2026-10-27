'''
A module for simulated sources.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from maths import gaussian_2d
from photometry import finding_masks


# Constants.
magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720
bg = 3420
bg_fluc = 11

# Global variables.
sample = 100


# Converts from apparent magnitude to pixel flux.
magnitudes = np.arange(14, 24.5, 0.5)
fluxes = (magnitudes - magzpt)/-2.5
fluxes = 10**fluxes
fluxes = fluxes*exposure_time/gain

# Creates the image and the mask.
image = np.zeros((400, 400))
ny, nx = np.shape(image)
xy = np.meshgrid(range(nx), range(ny))
mask = np.zeros_like(image)
mask[0, 0] = 1

# From https://medium.com/@ms_somanna/guide-to-adding-noise-to-your-data-using-python-and-numpy-c8be815df524
# Based on what we found for the global background noise.
gaussian_noise = np.random.normal(bg, bg_fluc, np.shape(image))

# Simulates the sources.
mags = []
mags_err = []

for f in fluxes:
    i = 0
    mag_i = []
    mag_err_i = []

    while i < sample:
        # Generates a random Gaussian sigma between 1 and 5.
        size_x = np.random.randint(1, 6)
        size_y = np.random.randint(1, 6)

        normalised_source = gaussian_2d(
            xy=xy, A=1, mu_x=200, mu_y=200, sigma_x=size_x, sigma_y=size_y,
            theta=0, B_x=0, B_y=0, C=0
        )

        # Normalisation and noise injection.
        norm_sum = np.sum(normalised_source)
        source = normalised_source * f / norm_sum
        source += gaussian_noise

        source = np.ma.array(source, mask=mask)

        # Source detection and photometry.
        image, obj, flux, flux_err = finding_masks(source, [200, 200])

        # Converts from pixel flux to apparent magnitude.
        mag = magzpt - 2.5 * np.log10(flux[0] * gain / exposure_time)
        flux_err = flux_err[0] * gain / exposure_time
        mag_err = - 2.5 / np.log(10) * flux_err / flux[0]
        mag_err = np.sqrt(magerr**2 + mag_err**2)

        if not np.isfinite(mag):
            continue

        mag_i.append(mag)
        mag_err_i.append(mag_err)

        i += 1

    mag_err_i = np.sqrt(np.sum(np.array(mag_err_i)**2)) / sample
    mag_err_i = np.max([np.std(mag_i), mag_err_i])

    mags.append(np.mean(mag_i))
    mags_err.append(np.std(mag_i))


# Line fitting.
def line(x, m, c):
    '''
    A straight line.
    '''
    return x*m + c

popt, pcov = optimize.curve_fit(
    line, xdata=magnitudes, ydata=mags, sigma=mags_err
)

# Plots the simulation result.
plt.errorbar(magnitudes, mags, mags_err, fmt='.', capsize=4, color='black')
plt.plot(np.array([12, 28]), line(np.array([12, 28]), *popt),
         color='red', label='Fit')
plt.xlabel('Actual magnitude')
plt.ylabel('Detected magnitude')
plt.grid()
plt.axis('square')
plt.xlim(13, 26)
plt.ylim(13, 28)
plt.legend()
plt.tight_layout()
# plt.savefig('figures/magnitude_simulation', dpi=300)
plt.show()

# Fit results.
print('STATISTICS')
print(f'm = {popt[0]:.5f} +/- {np.sqrt(pcov[0][0]):.5f}')
print(f'c = {popt[1]:.4f} +/- {np.sqrt(pcov[1][1]):.4f}')
print(f'Samples (per 0.5 mag) = {sample}')

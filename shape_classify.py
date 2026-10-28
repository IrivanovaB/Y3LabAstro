"""
A module to classify the shape of the astronomical object - the idea being more elliptical objects are more likely to be galaxies. 

Packages: json, numpy, matplotlib
"""

import json
import numpy as np
import matplotlib.pyplot as plt

shape_file = "data/shapes.json"
flux_file = "data/fluxes.json"

flux_err_file = "data/fluxes_err.json"
shape_err_file = "data/shapes_err.json"


with open(shape_file, "r") as file:
    shapes = json.load(file)
    file.close()

with open(shape_err_file, "r") as file:
    ratios_err = json.load(file)
    file.close()

with open(flux_file, "r") as file:
    fluxes = json.load(file)
    file.close()

with open(flux_err_file, "r") as file:
    fluxes_err = json.load(file)
    file.close()



areas = []
ratios = []
peaks = []

for x in shapes:
    if isinstance(x, float): #i.e nan
        ratios.append(np.nan)
        areas.append(np.nan)
        peaks.append(np.nan)
    elif len(x) == 6: #we will be discarding the edge cases 
        #ratios.append(x[2]/x[3]) #in theory this is the ratio
        ratios.append(np.nan)
        areas.append(np.nan)
        peaks.append(np.nan)
    elif len(x) == 9:
        ratios.append(x[4]/x[3])
        areas.append(np.pi*x[4]*x[3])
        peaks.append(x[0])
    else:
        ratios.append(0)
        areas.append(0)




ratios = np.array(ratios, dtype=float)
fluxes = np.array(fluxes, dtype=float)
areas = np.array(areas, dtype=float)
fluxes_err = np.array(fluxes_err, dtype=float)
ratios_err = np.array(ratios_err, dtype=float)

valid = np.isfinite(fluxes) & np.isfinite(ratios)

fluxes = fluxes[valid]
ratios = ratios[valid]
fluxes_err = fluxes_err[valid]
ratios_err = ratios_err[valid]
areas = areas[valid]


# plt.plot(ratios, pixel_peaks, "kx")
# plt.xlim((0, 2))
# plt.xlabel("Ratio of object (pix^2)")
# plt.ylabel("Pixel Peak")
# plt.grid()
# plt.show()



# plt.plot(ratios, fluxes, "x")
# plt.xlim((0, 3))
# plt.grid()
# plt.xlabel("Ratios")
# plt.ylabel("Fluxes")
# plt.show()



magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720
fluxes = fluxes * gain / exposure_time
magnitudes = magzpt - 2.5 * np.log10(fluxes)

fluxes_err = fluxes_err * gain / exposure_time
magnitudes_err = - 2.5 / np.log(10) * fluxes_err / fluxes
magnitudes_err = np.sqrt(magerr**2 + magnitudes_err**2)


plt.plot(magnitudes, ratios, "kx")
plt.errorbar(magnitudes, ratios, xerr=magnitudes_err, yerr=ratios_err, color="red", fmt="+")
plt.grid()
plt.xlim((15,20))
plt.ylim((0,3))
plt.xlabel("Magnitudes")
plt.ylabel("Ratios")
plt.title("Ratio per magnitude")
plt.show()





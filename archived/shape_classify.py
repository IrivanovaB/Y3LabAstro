import json
import numpy as np
import matplotlib.pyplot as plt

shape_file = "data runs/shapes running.json"
flux_file = "data runs/fluxes running.json"

flux_err_file = "data runs/fluxes_err running.json"
shape_err_file = "data runs/shapes_err running.json"

with open(shape_file, "r") as file:
    shapes = json.load(file)
    file.close()

with open(shape_err_file, "r") as file:
    ratios_err = json.load(file)
    file.close()

with open("peak_values.json", "r") as file:
    pixel_peaks = json.load(file)
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

with open(flux_file, "r") as file:
    fluxes = json.load(file)
    file.close()


with open(flux_err_file, "r") as file:
    fluxes_err = json.load(file)
    file.close()



ratios = np.array(ratios, dtype=float)
fluxes = np.array(fluxes, dtype=float)
fluxes_err = np.array(fluxes_err, dtype=float)
ratios_err = np.array(ratios_err, dtype=float)

flux_nan = np.isnan(fluxes)
ratios_nan = np.isnan(ratios)

indices = 1 - (flux_nan + ratios_nan)

indices = np.unique(np.cumsum(indices))

indices_r = 1 - ratios_nan
indices_r = np.unique(np.cumsum(indices_r))

areas = np.array(areas, dtype=float)
peaks = np.array(peaks, dtype=float)
pixel_peaks = np.array(pixel_peaks, dtype=float)
areas = areas[indices_r]
peaks = peaks[indices_r]
pixel_peaks = pixel_peaks[indices_r]

ratios = ratios[indices_r]

plt.plot(ratios, pixel_peaks, "kx")
plt.xlim((0, 2))
plt.xlabel("Ratio of object (pix^2)")
plt.ylabel("Pixle Peak")
plt.grid()
plt.show()

peak_per_area = pixel_peaks/areas

plt.hist(peak_per_area, bins=100)
plt.ylabel("Count")
plt.semilogy()
plt.xlabel("Pixel peak value per area (power)")
plt.show()



fluxes = fluxes[indices]
ratios = ratios[indices]
fluxes_err = fluxes_err[indices]
ratios_err = ratios_err[indices]


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
plt.show()





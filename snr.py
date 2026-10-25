import json
import numpy as np
import matplotlib.pyplot as plt

flux_file = "fluxes.json"
snr_file = "snr.json"
flux_err_file = "fluxes_err.json"
shape_file = "shapes.json"



with open(flux_file, "r") as file:
    fluxes = json.load(file)
    file.close()

with open(flux_err_file, "r") as file:
    fluxes_err = json.load(file)
    file.close()

with open(snr_file, "r") as file:
    snr = json.load(file)
    file.close()

with open(shape_file, "r") as file:
    shapes = json.load(file)
    file.close()


areas = []

for x in shapes:
    if isinstance(x, float): #i.e nan
        areas.append(np.nan)
    elif len(x) == 6: #we will be discarding the edge cases 
        areas.append(np.nan)
    elif len(x) == 9:
        areas.append(np.pi*x[4]*x[3])
    else:
        areas.append(0)




fluxes = np.array(fluxes, dtype=float)
fluxes_err = np.array(fluxes_err, dtype=float)
snr = np.array(snr, dtype=float)
areas = np.array(areas, dtype=float)

valid = np.isfinite(fluxes) & np.isfinite(snr)

fluxes = fluxes[valid]
snr = snr[valid]
areas = areas[valid]


magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720
fluxes = fluxes * gain / exposure_time
magnitudes = magzpt - 2.5 * np.log10(fluxes)


snr = 10 * np.log10(snr)

# plt.plot(magnitudes, snr, "x", label = "object")
# plt.title("SNR Per Object Magnitude")
# plt.legend(loc='upper right')
# plt.xlabel("Magnitude")
# plt.ylabel("SNR (dB)")
# #plt.hlines(7, xmin=np.min(fluxes), xmax=np.max(fluxes), color="red")
# plt.grid()
# plt.show()


plt.plot(areas, snr, "x", label="object")
plt.title("SNR Per Object Area")
plt.ylabel("SNR (dB)")
plt.xlim((0, 50))
plt.xlabel("Area (pix^2)")
plt.legend()
plt.grid()
plt.show()
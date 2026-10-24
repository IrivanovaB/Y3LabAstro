import json
import numpy as np
import matplotlib.pyplot as plt

shape_file = "shapes.json"
flux_file = "data runs/fluxes full flux.json"

with open(shape_file) as file:
    shapes = json.load(file)
    file.close()

ratios = []

for x in shapes:
    if isinstance(x, float):
        ratios.append(0)
    elif len(x) == 6:
        ratios.append(x[2]/x[3])
    elif len(x) == 9:
        ratios.append(x[3]/x[4])
    else:
        ratios.append(0)

with open(flux_file) as file:
    fluxes = json.load(file)
    file.close()

ratios = np.array(ratios, dtype=float)
fluxes = np.array(fluxes, dtype=float)

flux_nan = np.isnan(fluxes)
ratios_nan = np.isnan(ratios)

indices = 1 - (flux_nan + ratios_nan)

indices = np.unique(np.cumsum(indices))

fluxes = fluxes[indices]
ratios = ratios[indices]

# plt.plot(ratios, fluxes, "x")
# plt.xlim((0, 3))
# plt.grid()
# plt.xlabel("Ratios")
# plt.ylabel("Fluxes")
# plt.show()



magzpt = 2.530E+01
gain = 3.1
exposure_time = 720
fluxes = fluxes * gain / exposure_time
magnitudes = magzpt - 2.5 * np.log10(fluxes)

plt.plot(magnitudes, ratios, "kx")
plt.grid()
plt.ylim((0,3))
plt.xlabel("Magnitudes")
plt.ylabel("Ratios")
plt.show()
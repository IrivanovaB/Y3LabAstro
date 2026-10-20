import json
import matplotlib.pyplot as plt
import numpy as np

with open("fluxes.json", encoding="utf-8") as flux_file:
    fluxes = json.load(flux_file)


fluxes = np.abs(fluxes)
fluxes = fluxes[fluxes < 1e7]

plt.hist(fluxes, bins="auto")
plt.title("FLUXES")
plt.show()

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

ratios = []
areas = []

for x in shapes:
    if isinstance(x, float): #i.e nan
        areas.append(np.nan)
        ratios.append(np.nan)
    elif len(x) == 6: #we will be discarding the edge cases 
        areas.append(np.nan)
        ratios.append(np.nan)
    elif len(x) == 9:
        areas.append(np.pi*x[4]*x[3])
        ratios.append(x[4]/x[3])
    else:
        areas.append(0)
        ratios.append(0)




fluxes = np.array(fluxes, dtype=float)
fluxes_err = np.array(fluxes_err, dtype=float)
snr = np.array(snr, dtype=float)
areas = np.array(areas, dtype=float)
ratios = np.array(ratios, dtype=float)

valid = np.isfinite(fluxes) & np.isfinite(snr)

fluxes = fluxes[valid]
snr = snr[valid]
areas = areas[valid]
ratios = ratios[valid]
fluxes_err = fluxes_err[valid]


magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720
normalisation = 0.0564
#normalisation = 1


fluxes = fluxes * gain / exposure_time
fluxes_err = fluxes_err * gain / exposure_time

magnitudes_err = - 2.5 / np.log(10) * fluxes_err / fluxes
magnitudes_err = np.sqrt(magerr**2 + magnitudes_err**2)
magnitudes = magzpt - 2.5 * np.log10(fluxes)
#snr = 10 * np.log10(snr)


bins = np.arange(14, 24.5, 0.5)
magnitudes_err_binned = []
avg_snr = []
seom = []

for b in bins[:-1]:
    snrs = snr[(magnitudes > b) & (magnitudes < (b+0.5))]
    err = magnitudes_err[(magnitudes > b) & (magnitudes < (b+0.5))]
    if len(err) == 0:
        magnitudes_err_binned.append(0)
        avg_snr.append(np.nan)
        seom.append(np.nan)
    else:
        err = np.sqrt(np.sum(err**2)) / len(err)
        magnitudes_err_binned.append(err)
        avg_snr.append(np.mean(snrs))
        seom.append(np.std(snrs)/np.sqrt(len(snrs)))

# avg_snr = 10*np.log10(avg_snr)
# seom = np.abs(10*np.log10(seom))
plt.semilogy()
#plt.plot(bins[:-1], avg_snr, "ko")
plt.errorbar(bins[:-1], avg_snr, xerr=magnitudes_err_binned, yerr=seom, fmt="ko", capsize=4)
#plt.plot(bins[:-1], avg_snr, "ko", label="SNR")
#plt.title("Average SNR per magnitude")
plt.xlabel("Apparent magnitude")
plt.ylabel("Average SNR")
plt.axvspan(16, 20, color="lightblue", alpha=0.3, label="Valid mag")
plt.legend(loc="lower left")
#plt.grid()
plt.tight_layout()
plt.savefig('figures_presentation/fig_9', dpi=300)
plt.show()

plt.plot(magnitudes, snr, "x", label = "object")
plt.title("SNR Per Object Magnitude")
plt.legend(loc='upper right')
plt.xlabel("Magnitude")
plt.ylabel("SNR (dB)")
#plt.hlines(7, xmin=np.min(fluxes), xmax=np.max(fluxes), color="red")
plt.grid()
plt.show()


# plt.plot(areas, snr, "x", label="object")
# plt.title("SNR Per Object Area")
# plt.ylabel("SNR (dB)")
# #plt.xlim((0, 80))
# plt.xlabel("Area (pix^2)")
# # plt.xlabel("Ratio")
# plt.legend()
# plt.grid()
# plt.show()

# plt.hist(snr, bins=20)
# plt.title("Hist of SNR")
# plt.xlabel("SNR")
# plt.ylabel("Count")
# plt.show()
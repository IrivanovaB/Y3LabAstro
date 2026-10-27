'''
A module for simulated sources.
'''

from archive.photometry_functional import finding_masks
import numpy as np
from maths import gaussian_2d
import matplotlib.pyplot as plt
from scipy import optimize


magnitudes = np.arange(14, 24.5, 0.5)
sample = 100

#calculating the total flux from the apparent magnitudes 
magzpt = 2.530E+01
magerr = 2.000E-02
gain = 3.1
exposure_time = 720

fluxes = (magnitudes - magzpt)/-2.5
fluxes = 10**fluxes
fluxes = fluxes*exposure_time/gain


#now need to use the flux to generate the source 

#creating the source area 
image = np.zeros((400, 400))

#from https://medium.com/@ms_somanna/guide-to-adding-noise-to-your-data-using-python-and-numpy-c8be815df524
gaussian_noise = np.random.normal(3420, 11, np.shape(image)) #based on what we found for the global background noise

# plt.imshow(gaussian_noise)
# plt.title("Gaussian Noise")
# plt.show()


#create a normal distribution to then apply the flux

ny, nx = np.shape(image)
xy = np.meshgrid(range(nx), range(ny))

mask = np.zeros_like(image)
mask[0,0] = 1

mags = []
mags_err = []
# detection_sigma = []

for f in fluxes:
    i = 0
    mag_i = []
    mag_err_i = []
    # detection_sigma_i = []

    while i < sample:
        size_x = np.random.randint(1, 6)
        size_y = np.random.randint(1, 6)

        # box = [[0, 0], np.shape(image)[0], np.shape(image)[1]]
        # ellipse = [[200, 200], [size_x, size_y], 0]

        # bm = get_binary_mask(im=image, box=box, ellipse=ellipse)
        # bm = 1 - bm
        # area = np.sum(bm)
        # image = np.ma.array(image, mask=bm)

        # bg_no_source = np.ma.array(gaussian_noise, mask=bm)
        # sum_bg = np.ma.sum(bg_no_source)
        # fluxes = fluxes + sum_bg

        #A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C
        param = [1, 200, 200, 6, 6, 0, 0, 0, 3420]
        normalised_source = gaussian_2d(xy=xy, A=1, mu_x=200, mu_y=200, sigma_x=size_x, sigma_y=size_y, theta=0, B_x=0, B_y=0, C=0)

        # normalised_source = normalised_source/np.max(normalised_source)

        norm_sum = np.sum(normalised_source)

        source = normalised_source*f/norm_sum
        source += gaussian_noise

        # plt.imshow(source)
        # plt.title("Source")
        # plt.show()

        #normalised_source = np.ma.array(normalised_source, mask=bm)
        # plt.imshow(source_1)
        # plt.show()

        source = np.ma.array(source, mask=mask)

        image, obj, flux, flux_err = finding_masks(source, [200, 200], False)

        mag = magzpt - 2.5 * np.log10(flux[0]*gain/exposure_time)

        flux_err = flux_err[0] * gain / exposure_time
        mag_err = - 2.5 / np.log(10) * flux_err / flux[0]
        mag_err = np.sqrt(magerr**2 + mag_err**2)

        # print(f"Actual obj {ellipse} and flux {f} and mag {m}")
        # print(f"Found obj {obj} and flux {flux} and mag {mag} +/- {mag_err}")

        if not np.isfinite(mag):
            continue

        mag_i.append(mag)
        mag_err_i.append(mag_err)
        # detection_sigma_i.append(obj[0][0]/11)

        i += 1
        print(i)

    mag_err_i = np.sqrt(np.sum(np.array(mag_err_i)**2)) / sample
    mag_err_i = np.max([np.std(mag_i), mag_err_i])

    mags.append(np.mean(mag_i))
    mags_err.append(np.std(mag_i))
    # detection_sigma.append(np.mean(detection_sigma_i))

    # plt.imshow(image)
    # plt.title("returned masked image")
    # plt.show()


def line(x, m, c):
    return x*m + c

popt, pcov = optimize.curve_fit(
    line, xdata=magnitudes, ydata=mags, sigma=mags_err
)

plt.errorbar(magnitudes, mags, mags_err, fmt='x', label='Data')
plt.plot(np.array([13, 25]), line(np.array([13, 25]), *popt), label='Fit')
plt.xlabel('Actual magnitude')
plt.ylabel('Detected magnitude')
plt.grid()
plt.axis('square')
plt.legend()
plt.tight_layout()
# plt.savefig('figures/magnitude_simulation', dpi=300)
plt.show()

print('STATISTICS')
print(f'm = {popt[0]:.5f} +/- {np.sqrt(pcov[0][0]):.5f}')
print(f'c = {popt[1]:.4f} +/- {np.sqrt(pcov[1][1]):.4f}')
print(f'Samples (per 0.5 mag) = {sample}')


# plt.plot(magnitudes, detection_sigma, 'x')
# plt.xlabel('Magnitude')
# plt.ylabel('SNR')
# plt.tight_layout()
# plt.show()


# #A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C
# param = [33, 50, 50, 6, 6, 0, 0, 0, 3420]
# normalised_source = gaussian_2d(xy=xy, A=33, mu_x=50, mu_y=50, sigma_x=6, sigma_y=6, theta=0, B_x=0, B_y=0, C=0)
# source_2 = normalised_source + gaussian_noise

# plt.imshow(source_2)
# plt.title("Source")
# plt.show()

# #normalised_source = np.ma.array(normalised_source, mask=bm)
# # plt.imshow(source_2)
# # plt.show()

# mask = np.zeros_like(image)
# mask[0,0] = 1
# source_2 = np.ma.array(source_2, mask=mask)

# image, obj, flux, flux_err = finding_masks(source_2, [50, 50], False)
# mag = magzpt - 2.5 * np.log10(flux[0]*gain/exposure_time)

# flux_err = flux_err[0] * gain / exposure_time
# mag_err =  - 2.5 / np.log(10) * flux_err / flux[0]
# mag_err = np.sqrt(magerr**2 + mag_err**2)

# print(f"obj: {obj}")
# print(f"flux: {flux}")
# print(f"mag: {mag} +/- {mag_err}")
# plt.imshow(image)
# plt.title("returned masked image")
# plt.show()

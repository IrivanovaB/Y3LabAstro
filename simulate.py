from photometry import fit_n_gaussian, get_binary_mask, plot_n_gaussian
import numpy as np
from maths import gaussian_2d, gaussian_2d_fit #cba to figure out the params 
import matplotlib.pyplot as plt

from photometry import finding_masks



magnitudes = np.arange(16, 25, 0.5)

#calculating the total flux from the apparent magnitudes 
magzpt = 2.530E+01
gain = 3.1
exposure_time = 720

fluxes = (magnitudes - magzpt)/-2.5
fluxes = 10**fluxes
fluxes = fluxes*exposure_time/gain


#now need to use the flux to generate the source 

#creating the source area 
image = np.zeros((100, 100))

#from https://medium.com/@ms_somanna/guide-to-adding-noise-to-your-data-using-python-and-numpy-c8be815df524
gaussian_noise = np.random.normal(3420, 11, np.shape(image)) #based on what we found for the global background noise

# plt.imshow(gaussian_noise)
# plt.title("Gaussian Noise")
# plt.show()

box = [[0, 0], np.shape(image)[0], np.shape(image)[1]]
ellipse = [[25, 25], [10, 10], 0]


bm = get_binary_mask(im=image, box=box, ellipse=ellipse)
bm = 1 -bm
area = np.sum(bm)
image = np.ma.array(image, mask=bm)

bg_no_source = np.ma.array(gaussian_noise, mask=bm)
sum_bg = np.ma.sum(bg_no_source)
fluxes = fluxes + sum_bg


#create a normal distribution to then apply the flux

ny, nx = np.shape(image)
xy = np.meshgrid(range(nx), range(ny))


#A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C
param = [1, 25, 25, 5, 5, 0, 0, 0, 3420]
normalised_source = gaussian_2d(xy=xy, A=1, mu_x=25, mu_y=25, sigma_x=2, sigma_y=2, theta=0, B_x=0, B_y=0, C=0)

normalised_source = normalised_source/np.max(normalised_source)

norm_sum = np.sum(normalised_source)
target = fluxes[-1]

source_1 = normalised_source*target/norm_sum

source_1 += gaussian_noise

plt.imshow(source_1)
plt.title("Source")
plt.show()

#normalised_source = np.ma.array(normalised_source, mask=bm)
# plt.imshow(source_1)
# plt.show()

mask = np.zeros_like(image)
mask[0,0] = 1
source_1 = np.ma.array(source_1, mask=mask)

image, obj, flux = finding_masks(source_1, [25, 25], False)
print(f"Actual obj {ellipse} and flux {target}")
print(f"Found obj {obj} and flux {flux}")
plt.imshow(image)
plt.title("returned masked image")
plt.show()
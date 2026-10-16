import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import imageio.v3 as iio
from image_containers import ImageContainer
from detection_box import main 
import cv2

#Read in our analysis image
image = fits.open("Fits_Data/mosaic.fits")
image = image[0].data
# mask = iio.imread('Fits_Data/mask.png')
mask = cv2.imread('Fits_Data/mask.png')
mask = cv2.cvtColor(mask, 7)

mask = mask[::-1, ::]

# data = hdu[0].data

# # Plots the histogram.
# mosaic = ImageContainer(image=image[0].data)
# mosaic.import_mask(mask=mask)
# mosaic.plot_pixel_hist(p0=[2e6, 3400, 10])


image = image*mask
m, o = main(image)


# def plot_mask_image(image, mask):
#     fig = plt.figure()
#     plt.imshow(image.data, cmap="gray")
#     plt.imshow(mask.data, cmap="viridis", alpha=0.7)
#     plt.show()


# analysis_image = Original(data)
# mask = Threshold(np.zeros(analysis_image.shape()))
# flare_mask = Flare_Bleed(mask.data)
# flare_mask.flare_region((3213, 1437), analysis_image)

# print(analysis_image.shape())
# plot_mask_image(analysis_image, flare_mask)

# masked_image = MaskedOriginal(data)

# masked_image.plot_pixel_hist(p0=[5e6, 4000, 1000])

# # #example
# analysis_image.threshold().sobel().plot()
# mask = MissingMask(data)
# plot_mask_image(analysis_image, mask)

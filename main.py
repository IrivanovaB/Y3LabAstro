import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import imageio.v3 as iio
from images import load_image, plot_pixel_histogram


# Read in our analysis image.
image = load_image()

# Plots the histogram.
plot_pixel_histogram(im=image, p0=[2e6, 3400, 10])


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

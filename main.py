import numpy as np
from astropy.io import fits 
from frames import Frame, Image, Mask
from scipy import optimize, ndimage
import matplotlib.pyplot as plt

#Read in our analysis image
hdu = fits.open(r"Fits_Data/mosaic.fits")
data = hdu[0].data


def plot_mask_image(image, mask):
    fig = plt.figure()
    plt.imshow(image.data, cmap="gray")
    plt.imshow(mask.data, cmap="viridis", alpha=0.7)
    plt.show()


analysis_image = Original(data)
mask = Threshold(np.zeros(analysis_image.shape()))
flare_mask = Flare_Bleed(mask.data)
flare_mask.flare_region((3213, 1437), analysis_image)

print(analysis_image.shape())
plot_mask_image(analysis_image, flare_mask)

masked_image = MaskedOriginal(data)

masked_image.plot_pixel_hist(p0=[5e6, 4000, 1000])

# # #example
# analysis_image.threshold().sobel().plot()
# mask = MissingMask(data)
# plot_mask_image(analysis_image, mask)

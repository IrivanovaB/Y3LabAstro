from astropy.io import fits 
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import cv2

hdu = fits.open(r"Fits_Data\mosaic.fits")

#hdu = fits.open(r"FIT")
data = hdu[0].data

threshold = np.average(data.flatten()) #just the mean value
shape = np.shape(data)

flat_data = data.flatten()
#clean_data = np.where(flat_data >= threshold, flat_data, np.zeros_like(flat_data))
clean_data = np.where(flat_data <= 50000, flat_data, np.zeros_like(flat_data))
data = np.reshape(clean_data, shape)

#smooth
gaus = ndimage.gaussian_filter(data,sigma=0.1)



#def sobel(): #prewitt visually looks the same 
#following procedure of https://github.com/adamiao/sobel-filter-tutorial/blob/master/sobel_using_scipy.py
x_filter, y_filter = ndimage.sobel(gaus, axis=0), ndimage.sobel(gaus, axis=1)
filtered_image = np.hypot(x_filter, y_filter)  
filtered_image = filtered_image / np.max(filtered_image)  


filtered_image = filtered_image - 1
filtered_image = np.abs(filtered_image)


def blank_corners_edges(mask): #1 = ignore; #first index = y, second index = x
    #top left (bottom left in matplotlib)
    mask[4519:4611, 0:114] = 1 
    #top right (bottom right in matplotlib)
    mask[4514:4610, 2166:2478] = 1
    mask[4212:4610, 2478:2570] = 1

    #bottom left (top left in matplotlib)
    mask[0:422, 0:25] = 1
    mask[0:402, 25:95] = 1
    mask[0:118, 95:116] = 1
    mask[0:99, 116:406] = 1
    mask[0:23, 406:422] = 1
    #bottom right (top right in matplotlib) 
    mask[0:115, 2471:2570] = 1

    #edges
    #bottom edge (top edge in matplotlib)
    mask[:1, 0:] = 1
    #left edge 
    mask[0:, 0:4] = 1
    #top edge (bottom edge in matplotlib)
    mask[4609:, 0:] = 1
    #right edge
    mask[0:, 2569:] = 1

    #n.b. this is a very rudimentary blocking --> some pixels aren't actually apart of these corners and edges 
    #how much they contribute to the count is another matter but could look at like specific edge blocking and remove the values that aren't constant 
    #or assign an uncertainty for removing it bc we've just remove one row of pixels effectively per side which isn't enough to classify anything as that could be noise
    return mask


mask = np.zeros(np.shape(filtered_image), dtype=np.int8)
mask = blank_corners_edges(mask)


# fig = plt.figure(1)
# ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
# ax1.imshow(filtered_image, cmap="gray")
# ax2.imshow(filtered_image, cmap=plt.get_cmap('gray'))
# plt.show()

fig = plt.figure()
plt.imshow(filtered_image, cmap="gray")
plt.imshow(mask, cmap="viridis", alpha=0.5)
plt.show()
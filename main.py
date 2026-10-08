import numpy as np
from astropy.io import fits 
from classes import Frame, Image, Mask
from scipy import ndimage
import matplotlib.pyplot as plt

#Read in our analysis image
hdu = fits.open(r"Fits_Data/mosaic.fits")
data = hdu[0].data


class Original(Image):
    def __init__(self, data):
        super().__init__(data)
        self.__original__ = data

    def data(self):
        return self.__data__

    def threshold(self):
        """
        Applies the upper threshold due to reliability of bit depth

        Can establish an average threshold as well.
        """
        flat_data = self.__data__.flatten()
        threshold = np.average(flat_data)
        #clean_data = np.where(flat_data >= threshold, flat_data, np.zeros_like(flat_data))
        clean_data = np.where(flat_data <= 50000, flat_data, np.zeros_like(flat_data))
        self.__data__ = np.reshape(clean_data, self.__shape__)
        return self

    def gaussian(self):
        """
        Applies Gaussian filter for blurring (not sure if it blurs or not but here we go)
        """
        self.__data__ = ndimage.gaussian_filter(self.__data__, sigma=5)
        return self

    def sobel(self):
        """
        Applies sobel filter which is used for edge detection.

        Follows procedure of https://github.com/adamiao/sobel-filter-tutorial/blob/master/sobel_using_scipy.py
        """
        x_filter, y_filter = ndimage.sobel(self.data, axis=0), ndimage.sobel(self.data, axis=1)
        filtered_image = np.hypot(x_filter, y_filter)  
        filtered_image = filtered_image / np.max(filtered_image)  
        self.__data__ = filtered_image
        return self

    def invert(self):
        """
        Just inverts the values
        """
        self.__data__ = self.__data__ - np.max(self.__data__)
        self.__data__ = self.__data__ *-1
        return self

    def plot(self):
        fig = plt.figure(1)
        ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
        ax1.imshow(self.__original__, cmap="gray")
        ax2.imshow(self.data, cmap=plt.get_cmap('gray'))
        plt.show()


class MissingMask(Mask):
    def __init__(self, data):
        super().__init__(np.where(data <= 36000, np.ones_like(data), np.zeros_like(data)))
        self.blank_corners_edges()

    def data(self):
        return self.__data__

    def blank_corners_edges(self): #1 = ignore; #first index = y, second index = x
        """
        Just inputs the known blank sections 

        #n.b. this is a very rudimentary blocking --> some pixels aren't actually apart of these corners and edges 
        #how much they contribute to the count is another matter but could look at like specific edge blocking and remove the values that aren't constant 
        #or assign an uncertainty for removing it bc we've just remove one row of pixels effectively per side which isn't enough to classify anything as that could be noise

        """
        #top left (bottom left in matplotlib)
        self.__data__[4519:4611, 0:114] = 0
        #top right (bottom right in matplotlib)
        self.__data__[4514:4610, 2166:2478] = 0
        self.__data__[4212:4610, 2478:2570] = 0

        #bottom left (top left in matplotlib)
        self.__data__[0:422, 0:25] = 0
        self.__data__[0:402, 25:95] = 0
        self.__data__[0:118, 95:116] = 0
        self.__data__[0:99, 116:406] = 0
        self.__data__[0:23, 406:422] = 0
        #bottom right (top right in matplotlib)
        self.__data__[0:115, 2471:2570] = 0

        #edges
        #bottom edge (top edge in matplotlib)
        self.__data__[:1, 0:] = 0
        #left edge 
        self.__data__[0:, 0:4] = 0
        #top edge (bottom edge in matplotlib)
        self.__data__[4609:, 0:] = 0
        #right edge
        self.__data__[0:, 2569:] = 0
        return self

    def plot(self):
        """
        Plots the mask.
        """
        plt.imshow(self.__data__, cmap="gray")
        plt.tight_layout()
        # plt.savefig("figures/mask", dpi=300)
        plt.show()


class MaskedOriginal(Frame):
    def __init__(self, data):
        self.__image__ = Original(data)
        self.__mask__ = MissingMask(data)
        self.__image_data__ = self.__image__.data()
        self.__mask_data__ = self.__mask__.data()
        super().__init__(self.__image_data__[self.__mask_data__ == 1])

    def data(self):
        return self.__data__

    def plot(self):
        """
        Plots the masked image.
        """
        plt.imshow(self.__image_data__, cmap="gray")
        plt.imshow(self.__mask_data__, cmap="viridis", alpha=0.7)
        plt.tight_layout()
        # plt.savefig("figures/masked image", dpi=300)
        plt.show()

    def plot_pixel_histogram(self):
        """
        Plots the pixel value histogram of the masked image.
        """
        plt.hist(self.__data__, bins=100)
        plt.xlabel("Pixel Value (a.u.)")
        plt.ylabel("Count")
        plt.tight_layout()
        # plt.savefig("figures/pixel values histogram of masked image", dpi=300)
        plt.show()


masked_image = MaskedOriginal(data)
masked_image.plot_pixel_histogram()

# # #example
# analysis_image.threshold().sobel().plot()
# mask = MissingMask(data)
# plot_mask_image(analysis_image, mask)


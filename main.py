import numpy as np
from astropy.io import fits 
from classes import Image, Mask
from scipy import ndimage
import matplotlib.pyplot as plt

#Read in our analysis image
hdu = fits.open(r"Fits_Data\mosaic.fits")
data = hdu[0].data

class Original(Image):
    def __init__(self, data):
        super().__init__(data)
        self.original = data

    def threshold(self):
        """
        Applies the upper threshold due to reliability of bit depth

        Can establish an average threshold as well.
        """
        flat_data = self.data.flatten()
        threshold = np.average(flat_data)
        #clean_data = np.where(flat_data >= threshold, flat_data, np.zeros_like(flat_data))
        clean_data = np.where(flat_data <= 32000, flat_data, np.zeros_like(flat_data))
        self.data = np.reshape(clean_data, self.shape)
        return self

    def gaussian(self, sigma):
        """
        Applies Gaussian filter for blurring (not sure if it blurs or not but here we go)
        """
        self.data = ndimage.gaussian_filter(self.data, sigma=sigma)
        return self

    def sobel(self):
        """
        Applies sobel filter which is used for edge detection.

        Follows procedure of https://github.com/adamiao/sobel-filter-tutorial/blob/master/sobel_using_scipy.py
        """
        x_filter, y_filter = ndimage.sobel(self.data, axis=0), ndimage.sobel(self.data, axis=1)
        filtered_image = np.hypot(x_filter, y_filter)  
        filtered_image = filtered_image / np.max(filtered_image)  
        self.data = filtered_image
        return self

    def invert(self):
        """
        Just inverts the values
        """
        self.data = self.data - np.max(self.data)
        self.data = self.data*-1
        return self

    def plot(self):
        fig = plt.figure(1)
        ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
        ax1.imshow(self.original, cmap="gray")
        ax2.imshow(self.data, cmap=plt.get_cmap('gray'))
        plt.show()

class Missing_Mask(Mask):
    def __init__(self, data):
        super().__init__(data)
        self.data = self.blank_corners_edges()

    def blank_corners_edges(self): #1 = ignore; #first index = y, second index = x
        """
        Just inputs the known blank sections 

        #n.b. this is a very rudimentary blocking --> some pixels aren't actually apart of these corners and edges 
        #how much they contribute to the count is another matter but could look at like specific edge blocking and remove the values that aren't constant 
        #or assign an uncertainty for removing it bc we've just remove one row of pixels effectively per side which isn't enough to classify anything as that could be noise

        """
        #top left (bottom left in matplotlib)
        self.data[4519:4611, 0:114] = 1 
        #top right (bottom right in matplotlib)
        self.data[4514:4610, 2166:2478] = 1
        self.data[4212:4610, 2478:2570] = 1

        #bottom left (top left in matplotlib)
        self.data[0:422, 0:25] = 1
        self.data[0:402, 25:95] = 1
        self.data[0:118, 95:116] = 1
        self.data[0:99, 116:406] = 1
        self.data[0:23, 406:422] = 1
        #bottom right (top right in matplotlib) 
        self.data[0:115, 2471:2570] = 1

        #edges
        #bottom edge (top edge in matplotlib)
        self.data[:1, 0:] = 1
        #left edge 
        self.data[0:, 0:4] = 1
        #top edge (bottom edge in matplotlib)
        self.data[4609:, 0:] = 1
        #right edge
        self.data[0:, 2569:] = 1
        return self.data

def plot_mask_image(image, mask):
    fig = plt.figure()
    plt.imshow(image.data, cmap="gray")
    plt.imshow(mask.data, cmap="viridis", alpha=0.7)
    plt.show()
    #return fig

analysis_image = Original(data)


class Flare(Mask):
    def __init__(self, data):
        super().__init__(data)

    def central_flare(self, image):
        average_value = np.average(analysis_image.data)

        #flare bulb centre at [1437, 3213]
        central_x = 1436
        line = image.data[:, central_x]
        self.data[:, 1436] = line

        #going to the right
        x = central_x + 1
        right_line = image.data[:, x] 

        while (right_line >= average_value).any():
            shape = np.where(right_line >= average_value, right_line, np.zeros_like(right_line))
            self.data[:, x] = shape
            x += 1
            right_line = image.data[:, x]

        #going to the left
        x_left = central_x - 1
        left_line = image.data[:, x_left]
        while (left_line >= average_value).any():
            shape = np.where(left_line >= average_value, left_line, np.zeros_like(left_line))
            self.data[:, x_left] = shape
            x_left -= 1
            left_line = image.data[:, x_left]


        self.data = self.data/np.max(self.data) #normed

        plot_mask_image(image, self)


flare = Flare(np.zeros(analysis_image.shape))
flare.central_flare(analysis_image)

# # #example
# analysis_image.threshold().sobel().plot()
# mask = Missing_Mask(np.zeros(np.shape(analysis_image)))
# plot_mask_image(analysis_image, mask)

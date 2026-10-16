'''
A module for the image and mask frames.
'''

from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage


class Frame:
    """
    Parent class for anything that can constitute a layer.
    """
    def __init__(self, data):
        '''
        Args:
            data (arr): The layer data.
        '''
        self.data = data
        self.__shape = np.shape(data)

    def shape(self):
        '''
        Returns:
            arr: The layer shape.
        '''
        return self.__shape


class Image(Frame):
    """
    Child class of Frame. Functions as representing an image layer. 
    """
    def __init__(self, data):
        '''
        Args:
            data (arr): The layer data.
        '''
        super().__init__(data)
        self.__original = deepcopy(self.data)

    def original(self):
        '''
        Returns:
            arr: The original layer.
        '''
        return self.__original

    def threshold(self):
        """
        Applies the upper threshold due to reliability of bit depth

        Can establish an average threshold as well.
        """
        flat_data = self.data.flatten()
        threshold = np.average(flat_data)
        #clean_data = np.where(flat_data >= threshold, flat_data, np.zeros_like(flat_data))
        clean_data = np.where(flat_data <= 50000, flat_data, np.zeros_like(flat_data))
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

        Follows procedure of
        https://github.com/adamiao/sobel-filter-tutorial/blob/master/sobel_using_scipy.py
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
        self.data = self.data *-1
        return self

    def plot(self):
        fig = plt.figure(1)
        ax1, ax2 = fig.add_subplot(121), fig.add_subplot(122)
        ax1.imshow(self.__original, cmap="gray")
        ax2.imshow(self.data, cmap=plt.get_cmap('gray'))
        plt.show()


class Mask(Frame):
    """
    Child class of Frame. Functions as a mask overtop of an image.
    """
    def __init__(self, data):
        '''
        Args:
            data (arr): The layer data.
        '''
        super().__init__(data)


class EdgeMask(Mask):
    '''
    Masks the non-overlapping edges.
    '''
    def __init__(self, data):
        '''
        Args:
            data (arr): The layer data.
        '''
        super().__init__(data)
        self.data = np.ones_like(self.data)
        self.blank_corners_edges()

    def blank_corners_edges(self): #1 = ignore; #first index = y, second index = x
        """
        Just inputs the known blank sections 

        #n.b. this is a very rudimentary blocking --> some pixels aren't actually apart of these corners and edges 
        #how much they contribute to the count is another matter but could look at like specific edge blocking and remove the values that aren't constant 
        #or assign an uncertainty for removing it bc we've just remove one row of pixels effectively per side which isn't enough to classify anything as that could be noise

        """
        #top left (bottom left in matplotlib)
        self.data[4519:4611, 0:114] = 0
        #top right (bottom right in matplotlib)
        self.data[4514:4610, 2166:2478] = 0
        self.data[4212:4610, 2478:2570] = 0

        #bottom left (top left in matplotlib)
        self.data[0:422, 0:25] = 0
        self.data[0:402, 25:95] = 0
        self.data[0:118, 95:116] = 0
        self.data[0:99, 116:406] = 0
        self.data[0:23, 406:422] = 0
        #bottom right (top right in matplotlib)
        self.data[0:115, 2471:2570] = 0

        #edges
        #bottom edge (top edge in matplotlib)
        self.data[:1, 0:] = 0
        #left edge 
        self.data[0:, 0:4] = 0
        #top edge (bottom edge in matplotlib)
        self.data[4609:, 0:] = 0
        #right edge
        self.data[0:, 2569:] = 0
        return self

    def plot(self):
        """
        Plots the mask.
        """
        plt.imshow(self.data, cmap="gray")
        plt.tight_layout()
        # plt.savefig("figures/mask", dpi=300)
        plt.show()


class ThresholdMask(Mask):
    '''
    Masks the pixels with an intensity above the threshold.
    '''
    def __init__(self, data, threshold):
        '''
        Args:
            data (arr): The layer data.
            threshold (int): The threshold.
        '''
        super().__init__(data)
        self.threshold = threshold
        self.apply_threshold()

    def apply_threshold(self):
        self.data = np.where(self.data < self.threshold,
                             np.ones_like(self.data),
                             np.zeros_like(self.data))
        return self


class BleedingMask(Mask):
    '''
    Masks the bleeding.
    '''
    def __init__(self, data):
        '''
        Args:
            data (arr): The layer data.
        '''
        super().__init__(data)

    def flare_region(self, flare_centre, image):
        threshold = np.average(image.data)

        centre_x = flare_centre[1]
        centre_y = flare_centre[0]

        # line = image.data[:, centre_x]

        # mask_l_r = Mask(np.zeros(image.shape()))

        # self.data[:, centre_x] = line

        #going right
        # x_r = centre_x + 1
        # right_line = image.data[:, x_r]
        # while (right_line > threshold).any():
        #     right_line = np.where(right_line>threshold, right_line, np.zeros_like(right_line))
        #     mask_l_r.data[:, x_r] = right_line
        #     x_r += 1
        #     right_line = image.data[:, x_r]

        # #going left
        # x_l = centre_x - 1
        # left_line = image.data[:, x_l]
        # while (left_line > threshold).any():
        #     left_line = np.where(left_line>threshold, left_line, np.zeros_like(left_line))
        #     mask_l_r.data[:, x_l] = left_line
        #     x_l -= 1
        #     left_line = image.data[:, x_l]

        #going up
        line = image.data[centre_y, :]
        self.data[centre_y, :] = line
        x_u = centre_y + 1
        up_line = image.data[x_u, :]
        while (up_line > threshold).any():
            up_line = np.where(up_line>threshold, up_line, np.zeros_like(up_line))
            self.data[x_u, :] = up_line
            x_u += 1
            up_line = image.data[x_u, :]

        #going down
        x_d = centre_y - 1
        down_line = image.data[x_d, :]
        while (down_line > threshold).any():
            down_line = np.where(down_line>threshold, down_line, np.zeros_like(down_line))
            self.data[x_d, :] = down_line
            x_d -= 1
            down_line = image.data[x_d, :]

        self.data = self.data/36000

        return self

    def define_flares(self):
        box_size = (87, 257) #54 boxes up and 10 boxes along -> 540 total boxes 
        #fml

        for ix in range(1, 10):
            for iy in range(1, 54):
                box = self.data[box_size[1]]

        return self


class ImportMask(Mask):
    '''
    Imports a mask stored as a PNG.
    '''
    def __init__(self, data):
        '''
        Args:
            data (arr): The mask.
        '''
        super().__init__(np.sum(data[:,:,:3], axis=2))
        # White pixels have a total value across RGB of 765.
        self.data = np.where(self.data == 765, np.ones_like(self.data),
                             np.zeros_like(self.data))
        self.data = np.flip(self.data, axis=0)

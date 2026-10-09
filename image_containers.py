'''
A module for the image containers composed of layers of frames.
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from frames import Frame, Image, Mask, EdgeMask, SaturationMask, BleedingMask, CircleMask
from maths import gaussian_1d, gaussian_1d_fit


class ImageContainer():
    '''
    A container of an image and its mask frames.
    '''
    def __init__(self, image):
        '''
        Initialises the class.

        Args:
            image (arr): The image.
        '''
        self.__image = Image(image)
        self.__mask = []

    def mask_edge(self):
        '''
        Adds an EdgeMask.
        '''
        self.__mask.append(EdgeMask(self.__image.data))

    def mask_saturation(self):
        '''
        Adds a SaturationMask.
        '''
        self.__mask.append(SaturationMask(self.__image.data))

    def gaussian_fit(self, p0):
        """
        Fits a Gaussian to the pixel value histogram.
        """
        count, pixel = np.histogram(self.__image, bins=1000)
        pixel = (pixel[1:] + pixel[:-1]) / 2
        return optimize.curve_fit(gaussian, xdata=pixel, ydata=count, p0=p0)

    def plot(self):
        """
        Plots the masked image.
        """
        plt.imshow(self.__image__, cmap="viridis")
        plt.imshow(self.__mask__, cmap="gray", alpha=0.7)
        plt.tight_layout()
        # plt.savefig("figures/masked image", dpi=300)
        plt.show()

    def plot_pixel_hist(self, p0):
        """
        Plots the pixel value histogram of the masked image.
        """
        def gaussian(x, A, mu, sigma):
            return A * np.exp(- (x-mu)**2 / (2 * sigma**2))
        popt, pcov = self.gaussian_fit(p0)
        plt.hist(self.__data__, bins=1000)
        plt.plot(np.arange(0, 35000, 100), gaussian(np.arange(0, 35000, 100), *popt))
        plt.xlabel("Pixel Value (a.u.)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("figures/fitted pixel values histogram of masked image", dpi=300)
        plt.show()

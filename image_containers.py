'''
A module for the image containers composed of layers of frames.
'''

import numpy as np
import matplotlib.pyplot as plt
from frames import Image, EdgeMask, ThresholdMask, BleedingMask, CircleMask
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
        return self

    def mask_threshold(self, threshold=36000):
        '''
        Adds a ThresholdMask.

        Args:
            threshold (int): The threshold. Defaults to 36000.
        '''
        self.__mask.append(ThresholdMask(self.__image.data,
                                         threshold=threshold))
        return self

    def select_image_region(self, coord):
        '''
        Selects a square region in the image.

        Args:
            coord (list | None): The coordinates of the region. In the
                format of [x_start, x_end, y_start, y_end]. If None,
                return original image.

        Returns:
            tuple[arr, list]: The data of the image and its masks in
                selected region.
        '''
        if coord is None:
            image = self.__image.data
            masks = [mask.data for mask in self.__mask]
            return image, masks
        x_start, x_end, y_start, y_end = coord
        image = self.__image.data[x_start:x_end, y_start:y_end]
        masks = [mask.data[x_start:x_end, y_start:y_end]
                 for mask in self.__mask]
        return image, masks

    def masked_image_pixels(self, coord=None):
        '''
        Returns the pixel values of the masked image.

        Args:
            coord (list | None): The coordinates of the region. In the
                format of [x_start, x_end, y_start, y_end]. If None,
                return original image. Defaults to None.

        Returns:
            arr: The pixel values of the masked image.
        '''
        image, masks = self.select_image_region(coord=coord)
        return image[np.array(masks).all(axis=0)]

    def plot_image(self, coord=None):
        '''
        Plots the masked image.

        Args:
            coord (list): The range of the coordinates to evaluate the
                histogram at. In the format of [x_start, x_end,
                y_start, y_end]. If None, evaluate the entire image.
                Defaults to None.
        '''
        image, masks = self.select_image_region(coord=coord)
        plt.imshow(image, cmap="viridis")
        for mask in masks:
            plt.imshow(mask, cmap="gray", alpha=0.7)
        plt.tight_layout()
        # plt.savefig("figures/masked image", dpi=300)
        plt.show()

    def pixel_hist(self, bin_width=10., coord=None):
        '''
        Calculates the pixel value histogram of the masked image.

        Args:
            bin_width (float): The bin width. Defaults to 10.
            coord (list): The range of the coordinates to evaluate the
                histogram at. In the format of [x_start, x_end,
                y_start, y_end]. If None, evaluate the entire image.
                Defaults to None.

        Returns:
            tuple[arr, arr]: The histogram values and the bin edges.
        '''
        image = self.masked_image_pixels(coord=coord)
        bins = np.arange(image.max() + 10, step=bin_width)
        return np.histogram(image, bins=bins)

    def pixel_hist_gaussian_fit(self, p0, bin_width=10., coord=None):
        '''
        Fits a Gaussian distribution to the pixel value histogram.

        Args:
            p0 (list): Initial guesses.
            bin_width (float): The bin width. Defaults to 10.
            coord (list): The range of the coordinates to evaluate the
                histogram at. In the format of [x_start, x_end,
                y_start, y_end]. If None, evaluate the entire image.
                Defaults to None.

        Returns:
            tuple[arr, arr]: The optimal values and the covariance matrix.
        '''
        count, bin_edge = self.pixel_hist(coord=coord, bin_width=bin_width)
        bins = (bin_edge[1:] + bin_edge[:-1]) / 2
        return gaussian_1d_fit(x_data=bins, y_data=count, p0=p0)

    def plot_pixel_hist(self, bin_width=10., coord=None, p0=None,
                        zoomed_in=False):
        '''
        Plots the pixel value histogram of the masked image.

        Args:
            bin_width (float): The bin width. Defaults to 10.
            coord (list | None): The range of the coordinates to
                evaluate the histogram at. In the format of [x_start,
                x_end, y_start, y_end]. If None, evaluate the entire
                image. Defaults to None.
            p0 (list | None): Initial guesses. If supplied, plots the
                Gaussian fit. Defaults to None.
            zoomed_in (bool): If True, zoom in to the Gaussian region.
                Defauls to False
        '''
        count, bin_edge = self.pixel_hist(coord=coord, bin_width=bin_width)
        plt.stairs(count, bin_edge, fill=True)
        if p0 is not None:
            popt, pcov = self.pixel_hist_gaussian_fit(
                p0=p0,bin_width=bin_width, coord=coord
            )
            bins = (bin_edge[1:] + bin_edge[:-1]) / 2
            plt.plot(bins, gaussian_1d(bins, *popt))
            perr = np.sqrt(np.diag(pcov))
            print(f'A = {popt[0]:.2f} +/- {perr[0]:.2f}\n'
                  f'μ = {popt[1]:.2f} +/- {perr[1]:.2f}\n'
                  f'σ = {popt[2]:.2f} +/- {perr[2]:.2f}')
        plt.xlabel("Pixel Value (a.u.)")
        plt.ylabel("Count")
        plt.tight_layout()
        if zoomed_in:
            plt.xlim(left=(popt[1] - 10*popt[2]), right=(popt[1] + 10*popt[2]))
            plt.ylim(top=3*popt[0])
        # plt.savefig("figures/masked image histogram", dpi=300)
        plt.show()

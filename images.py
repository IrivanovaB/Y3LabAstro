'''
A module for the mosaic image.
'''

import numpy as np
import matplotlib.pyplot as plt
import imageio.v3 as iio
from astropy.io import fits
from maths import gaussian_1d, gaussian_1d_fit


# Global variables.
bin_width = 5


def load_mask():
    '''
    Loads the binary mask.

    Returns:
        arr: The binary mask with 1 for the masked regions.
    '''
    mask = iio.imread('Fits_Data/mask.png')
    mask = np.sum(mask[:,:,:3], axis=2)
    # White pixels have a total value across RGB of 765.
    mask = np.where(mask == 765, np.zeros_like(mask), np.ones_like(mask))
    mask = np.flip(mask, axis=0)
    return mask


def load_image():
    '''
    Loads the mosaic image with the mask.

    Returns:
        arr: The masked mosaic image.
    '''
    image = fits.open("Fits_Data/mosaic.fits")
    image = np.ma.array(image[0].data, mask=load_mask())
    return image


def get_pixel_histogram(im, threshold=None):
    '''
    Computes the pixel value histogram of the image.

    Args:
        im (arr): The image.
        threshold (list | None): The lower and upper thresholds of the
            pixel value. Defaults to None.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''
    im = im.compressed()
    if threshold is not None:
        im = im[im > threshold[0]]
        im = im[im < threshold[1]]
    bins = np.arange(np.max(im)+10., step=bin_width)
    return np.histogram(im, bins=bins)


def fit_pixel_histogram(im, p0, threshold=None):
    '''
    Fits a Gaussian distribution to the pixel value histogram.

    Args:
        im (arr): The image.
        p0 (list): Initial guesses.
        threshold (list | None): The lower and upper thresholds of the
            pixel value. Defaults to None.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''
    count, bin_edge = get_pixel_histogram(im=im, threshold=threshold)
    bins = (bin_edge[1:] + bin_edge[:-1]) / 2
    return gaussian_1d_fit(x_data=bins, y_data=count, p0=p0)


def plot_pixel_histogram(im, p0=None, threshold=None):
    '''
    Args:
        im (arr): The image.
        p0 (list | None): Initial guesses. If supplied, plots the
            Gaussian fit. Defaults to None.
        threshold (list | None): The lower and upper thresholds of the
            pixel value. Defaults to None.

    Returns:
        tuple[arr, arr]: If p0 is not None, the optimal values and the
            covariance matrix.
    '''
    count, bin_edge = get_pixel_histogram(im=im, threshold=threshold)
    plt.stairs(count, bin_edge, fill=True)
    plt.xlabel("Pixel value (ADU)")
    plt.ylabel("Count (per 5 ADU)")
    plt.tight_layout()
    if p0 is not None:
        popt, pcov = fit_pixel_histogram(im=im, p0=p0, threshold=threshold)
        bins = (bin_edge[1:] + bin_edge[:-1]) / 2
        plt.plot(bins, gaussian_1d(bins, *popt))
        plt.xlim(popt[1] - 10*popt[2], popt[1] + 10*popt[2])
        plt.xlim(popt[1] - 10*popt[2], popt[1] + 10*popt[2])
        perr = np.sqrt(np.diag(pcov))
        print(f'A = {popt[0]:.2f} +/- {perr[0]:.2f}\n'
              f'μ = {popt[1]:.2f} +/- {perr[1]:.2f}\n'
              f'σ = {popt[2]:.2f} +/- {perr[2]:.2f}')
    else:
        popt = None
        pcov = None
    # plt.savefig("figures/pixel_value_histogram", dpi=300)
    plt.show()
    return popt, pcov

'''
A module for the mathematical functions.
'''

import numpy as np


def gaussian_1d(x, A, mu, sigma):
    '''
    A 1D Gaussian distribution.

    Args:
        x (float): The x value.
        A (float): The normalisation factor.
        mu (float): The mean.
        sigma (float): The standard deviation.

    Returns:
        float: The Gaussian distribution evaluated at x.
    '''
    return A * np.exp(- (x-mu)**2 / (2 * sigma**2))


def gaussian_2d(x, y, A, mu_x, mu_y, sigma):
    '''
    A 2D Gaussian distribution.

    Args:
        x (float): The x value.
        y (float): The y value.
        A (float): The normalisation factor.
        mu_x (float): The mean in the x direction.
        mu_y (float): The mean in the y direction.
        sigma (float): The standard deviation.

    Returns:
        float: The Gaussian distribution evaluated at (x, y).
    '''
    return A * np.exp(- ((x-mu_x)**2 + (y-mu_y)**2)/ (2 * sigma**2))

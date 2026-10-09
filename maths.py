'''
A module for the mathematical functions.
'''

import numpy as np
from scipy import optimize


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


def gaussian_2d(x, y, A, mu_x, mu_y, sigma_x, sigma_y):
    '''
    A 2D Gaussian distribution.

    Args:
        x (float): The x value.
        y (float): The y value.
        A (float): The normalisation factor.
        mu_x (float): The mean in the x direction.
        mu_y (float): The mean in the y direction.
        sigma_x (float): The standard deviation in the x direction.
        sigma_y (float): The standard deviation in the y direction.

    Returns:
        float: The Gaussian distribution evaluated at (x, y).
    '''
    return A * np.exp(- (x-mu_x)**2 / (2 * sigma_x**2)
                      + (y-mu_y)**2 / (2 * sigma_y**2))


def gaussian_1d_fit(x_data, y_data, p0):
    '''
    Fits to a 1D Gaussian distribution.

    Args:
        x_data (arr): The x data.
        y_data (arr): The y data.
        p0 (list): The initial guesses.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''


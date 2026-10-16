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
        mu (float): The expected value.
        sigma (float): The standard deviation.

    Returns:
        float: The Gaussian distribution evaluated at x.
    '''
    return A * np.exp(- (x-mu)**2 / (2 * sigma**2))


def gaussian_2d(xy, A, mu_x, mu_y, sigma_x, sigma_y, theta):
    '''
    A 2D Gaussian distribution.

    Args:
        xy (arr): The x and y values.
        A (float): The normalisation factor.
        mu_x (float): The expected value in the x direction.
        mu_y (float): The expected value in the y direction.
        sigma_x (float): The standard deviation in the x direction.
        sigma_y (float): The standard deviation in the y direction.
        theta (float): The positive anti-clockwise rotation angle.

    Returns:
        float: The Gaussian distribution evaluated at (x, y).
    '''
    x, y = xy
    a = (np.cos(theta)**2 / (2*sigma_x**2)
         + np.sin(theta)**2 / (2*sigma_y**2))
    b = (- np.sin(theta)*np.cos(theta) / (2*sigma_x**2)
         + np.sin(theta)*np.cos(theta) / (2*sigma_y**2))
    c = (np.sin(theta)**2 / (2*sigma_x**2)
         + np.cos(theta)**2 / (2*sigma_y**2))
    return A * np.exp(- a*(x-mu_x)**2 - 2*b*(x-mu_x)*(y-mu_y) - c*(y-mu_y)**2)


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
    return optimize.curve_fit(gaussian_1d, xdata=x_data, ydata=y_data, p0=p0,
                              bounds=[[0, 0, 0], [np.inf, np.inf, np.inf]])


def gaussian_2d_fit(xy_data, z_data, p0):
    '''
    Fits to a 2D Gaussian distribution.

    Args:
        xy_data (arr): The x and y data.
        z_data (arr): The z data.
        p0 (list): The initial guesses.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''
    return optimize.curve_fit(
        gaussian_2d, xdata=xy_data, ydata=z_data, p0=p0, bounds=[
            [0, 0, 0, 6, 6, 0],
            [np.inf, np.inf, np.inf, np.inf, np.inf, np.pi]
        ]
    )

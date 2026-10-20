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


def gaussian_2d(xy, A, mu_x, mu_y, sigma_x, sigma_y, theta, B_x, B_y, C):
    '''
    A 2D Gaussian distribution with a background plane.

    Args:
        xy (arr): The x and y values.
        A (float): The normalisation factor.
        mu_x (float): The expected value in the x direction.
        mu_y (float): The expected value in the y direction.
        sigma_x (float): The standard deviation in the x direction.
        sigma_y (float): The standard deviation in the y direction.
        theta (float): The positive anti-clockwise rotation angle.
        B_x (float): The slope of the background plane in the x
            direction.
        B_y (float): The slope of the background plane in the y
            direction.
        C (float): The z-intercept of the background plane.

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
    return (
        A*np.exp(- a*(x-mu_x)**2 - 2*b*(x-mu_x)*(y-mu_y) - c*(y-mu_y)**2)
        + B_x*x + B_y*y + C
    )


def gaussian_2d_n(xy, *params):
    """
    pn of structure list or array with 
        A, mu_x, mu_y, sigma_x, sigma_y, theta, B_x, B_y, C
    """
    params = np.asarray(params).reshape(-1, 9)
    x, y = xy
    multi_fit = np.zeros_like(x, dtype=float)
    for p in params:
        A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C = p
        multi_fit += gaussian_2d(xy, A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C)

    return multi_fit




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
    return optimize.curve_fit(
        gaussian_1d, xdata=x_data, ydata=y_data, p0=p0,
        bounds=[[0, 0, 0], [np.inf, np.inf, np.inf]]
    )


def gaussian_2d_fit(xy_data, z_data, p0):
    '''
    Fits to a 2D Gaussian distribution with a background plane.

    Args:
        xy_data (arr): The x and y data.
        z_data (arr): The z data.
        p0 (list): The initial guesses.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''
    x_data, y_data = xy_data
    return optimize.curve_fit(
        gaussian_2d, xdata=(x_data.ravel(), y_data.ravel()),
        ydata=z_data.ravel(), p0=p0, bounds=[
            [0, 0, 0, 0, 0, 0, -np.inf, -np.inf, 0], np.full(9, np.inf)
        ]
    )


def gaussian_2d_n_fit(xy_data, z_data, p0):
    x_data, y_data = xy_data
    p0 = np.asarray(p0, dtype=float)
    p0 = p0.ravel()

    number = len(p0)//9

    standard_bounds = [[0, 0, 0, 0, 0, 0, -np.inf, -np.inf, 0], np.full(9, np.inf)]
    bounds = np.tile(standard_bounds, (number, 1)).ravel()

    return optimize.curve_fit(
            gaussian_2d_n, xdata=(x_data.ravel(), y_data.ravel()),
            ydata=z_data.ravel(), p0=p0
        )

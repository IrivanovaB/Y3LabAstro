'''
A module for the photometry. Produces data files in the "data" folder which are used for analysis.

Package dependencies: json, numpy, matplotlib, cv2, skimage
Imported modules from directory: images, maths

'''

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import cv2
from skimage.feature import peak_local_max
from images import load_image
from maths import (gaussian_2d, gaussian_2d_fit,
                   gaussian_2d_n, gaussian_2d_n_fit)


# Global variables.
image = load_image()
box_size = 6
bg_box_size = 50
bg_threshold = 11
global_bg = 3420
ellipse_size = 15
saturation = 36000


# Note that all of the following image coordinates are in (y, x) instead of (x, y).


def find_centre(im):
    '''
    Finds the coordinates of the brightest pixel in an image.

    NOTE: The detection threshold currently is set at 1*std of the
    global background mean.

    Args:
        im (arr)
            The image.

    Returns:
        max_index (arr)
            The coordinates of the brightest pixel as (y, x)
    '''

    max_index = np.unravel_index(np.argmax(im), np.shape(im))
    if im[max_index] < (global_bg + bg_threshold):
        print("All sources found!")
        return None
    return max_index


def edge_box(bounds, dx, dy):
    '''
    For a box which is partially outside the image or 
    on the edge of another object's mask.

    Args:
        bounds (list)
            [min y, min x, max y, max x]
        dx (list)
            [x2, x1], where x2 < x1. x2 is restricted by the
            boundary bounds[1], and x1 the boundary bounds[3].
        dy (list)
            [y2, y1], where y2 < y1. y2 is restricted by the
            boundary bounds[0], and y1 the boundary bounds[2].

    Returns:
        cs (list)
            The updated coordinates of the box
        h, w (float)
            height, width
    '''

    cs = [0, 0, 0, 0] # [y2, x2, y1, x1].

    # If y2 goes beyond the top of the image.
    if dy[0] < bounds[0]:
        cs[0] = bounds[0]
    else:
        cs[0] = dy[0]

    # If y1 goes beyond the bottom of the image.
    if dy[1] > bounds[2]:
        cs[2] = bounds[2]
    else:
        cs[2] = dy[1]

    # If x1 goes beyond the right of the image.
    if dx[1] > bounds[3]:
        cs[3] = bounds[3]
    else:
        cs[3] = dx[1]

    # If x2 goes beyond the left of the image.
    if dx[0] < bounds[1]:
        cs[1] = bounds[1]
    else:
        cs[1] = dx[0]

    if cs[0] > cs[2]: #y2 < y1
        cs[0], cs[2] = cs[2], cs[0]
        cs[1], cs[3] = cs[3], cs[1]

    h = np.abs(cs[0] - cs[2])
    w = np.abs(cs[1] - cs[3])

    return cs, h, w


def create_box(centre, prev_box, bounds, size=box_size):
    '''
    Creates a new box based on the information of the previous box.

    Args:
        centre (tuple)
            The coordinates of the centre of the box.
        prev_box (list | None)
            The information of the previous box. If None, no previous boxes exist.
        bounds (list)
            [min y, min x, max y, max x]
        size (integer)
            the increase in the box's size in all directions 

    Returns:
        (list)
            The coordinates of the top left corner of the box, its
            height, and its width.
    '''

    if prev_box is None:
        dx = [centre[1] - size, centre[1] + size]
        dy = [centre[0] - size, centre[0] + size]
        if ((dx[0] < bounds[1]) or (dx[1] > bounds[3])
            or (dy[0] < bounds[0]) or (dy[1] > bounds[2])):

            cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy)
            # cs is (y2, x2, y1, x1).

            return [[cs[0], cs[1]], h, w]

        # Starting coords of the top left corner, h, w.
        return [[centre[0] - size, centre[1] - size],
                2*size + 1, 2*size + 1]

    h, w = prev_box[1], prev_box[2]

    c = [prev_box[0][0], prev_box[0][1]]
    # Left, right. Increase by w because corner in top left.
    dx = [c[1] - size, c[1] + w + size]
    # Down, up. Decrase by h because corner in top left.
    dy = [c[0] - size, c[0] + h + size]

    if (dx[0] < bounds[1]) or (dy[0] < bounds[0]) or (dx[1] > bounds[3]) or (dy[0] > bounds[2]):
        cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy)
        return [[cs[0], cs[1]], h, w]

    return [[prev_box[0][0] - size, prev_box[0][1] - size],
            h + 2*size, w + 2*size]


def get_box_coords(box):
    '''
    Finds the coordinates of the corners of the box.

    Args:
        box (list): The box information.

    Returns:
        tuple[arr, arr, arr]: The x-coordinates, the y-coordinates, and
            the combined coordinates.
    '''

    h = box[1]
    w = box[2]

    box_x = [box[0][1], box[0][1]+w-1, box[0][1]+w-1, box[0][1], box[0][1]]
    box_y = [box[0][0], box[0][0], box[0][0]+h-1, box[0][0]+h-1, box[0][0]]
    box_coords = np.stack((box_y, box_x), axis=-1)
    return box_x, box_y, box_coords


def get_box_image(im, box):
    '''
    Finds the boxed region of the image.

    Args:
        im (arr): The image.
        box (list): The box information.

    Output:
        (arr)
            The section of the image that the box takes up
    '''

    _, _, box_coords = get_box_coords(box)
    return im[box_coords[0][0]:(box_coords[2][0]+1),
              box_coords[0][1]:(box_coords[2][1]+1)]


def box_in_sky(im, box, centre):
    '''
    Plots the bounding box region and its surrounding image.

    Args:
        im (arr): The image.
        box (list): The box information.
        centre (tuple): The coordinates of the centre of the box.
    '''

    bx, by, _ = get_box_coords(box)
    b_image = get_box_image(im, box)

    fig, (axs1, axs2) = plt.subplots(1, 2)
    fig.suptitle("Box in the Sky")

    axs1.imshow(im)
    axs1.plot(bx, by, color="red", alpha=0.5, label="box")
    axs1.plot(centre[1], centre[0], "rx", label="centre")
    axs1.legend()
    axs1.set_xlim((centre[1]-150, centre[1]+150))
    axs1.set_ylim((centre[0]+150, centre[0]-150))
    axs2.imshow(b_image)
    plt.show()


def plot_box_3d(box_im):
    '''
    Plots the boxed region in 3D.

    Args:
        box_im (list): The boxed region.
    '''

    nx, ny = np.shape(box_im)
    x, y = np.meshgrid(range(nx), range(ny))

    fig = plt.figure()
    subfig = fig.add_subplot(111, projection="3d")
    subfig.plot_surface(x, y, box_im)
    plt.show()


def box_stats(box_im, verbose=False):
    '''
    Computes the statistics of the boxed region.
    
    Args:
        box_im (arr): The boxed region.
        verbose (bool): If True, outputs the statistics. Defaults to
            False.

    Returns:
        tuple[float, float, float]: The mean, median, and standard
            deviation of the boxed region.
    '''

    if verbose:
        print(f"The mean is: {np.mean(box_im)}")
        print(f"The median is: {np.median(box_im)}")
        print(f"The stdev is: {np.std(box_im)}")
        print("\n")
    return np.mean(box_im), np.median(box_im), np.std(box_im)


def axis_stats(box_im, plot=False):
    '''
    Computes the statistics of the boxed region.

    Args:
        box_im (arr): The boxed region.
        plot (bool): If True, plots the statistics. Defaults to False.

    Returns:
        tuple[arr, arr, arr, arr]: The means and medians in the x and
            y directions.
    '''

    x_means = np.mean(box_im, axis=0)
    y_means = np.mean(box_im, axis=1)
    x_medians = np.median(box_im, axis=0)
    y_medians = np.median(box_im, axis=1)
    x_stds = np.std(box_im, axis=0)
    y_stds = np.std(box_im, axis=1)

    if plot:
        fig, (axs1, axs2, axs3) = plt.subplots(1, 3)
        fig.suptitle("Mean/medians/stdev")

        axs1.plot(x_means, color="blue", alpha=0.5)
        axs1.plot(x_means, color="blue", marker="x", label="x")
        axs1.plot(y_means, color="orange", alpha=0.5)
        axs1.plot(y_means, color="orange", marker="o", label="y")
        axs1.set_title("Means")
        axs1.legend()

        axs2.plot(x_medians, color="blue", alpha=0.5)
        axs2.plot(x_medians, color="blue", marker="x", label="x")
        axs2.plot(y_medians, color="orange", alpha=0.5)
        axs2.plot(y_medians, color="orange", marker="o", label="y")
        axs2.set_title("Medians")
        axs2.legend()

        axs3.plot(x_stds, color="blue", alpha=0.5)
        axs3.plot(x_stds, color="blue", marker="x", label="x")
        axs3.plot(y_stds, color="orange", alpha=0.5)
        axs3.plot(y_stds, color="orange", marker="o", label="y")
        axs3.set_title("Stdevs")
        axs3.legend()
        plt.show()

    return x_means, y_means, x_medians, y_medians


def fit_gaussian(box_im):
    '''
    Fits a 2D Gaussian distribution with a background plane to the
    boxed region.

    Args:
        box_im (arr): The boxed region.

    Returns:
        tuple[arr, arr]: The optimal values and the covariance matrix.
    '''

    ny, nx = np.shape(box_im)
    xy = np.meshgrid(range(nx), range(ny))
    p0 = [
        np.max(box_im),
        *np.unravel_index(np.argmax(box_im), np.shape(box_im)),
        nx/4, ny/4, 0,
        0, 0, np.median(box_im)
    ]
    return gaussian_2d_fit(xy_data=xy, z_data=box_im, p0=p0)


def plot_gaussian(box_im, popt):
    '''
    Plots the boxed region in 3D with the fitted Gaussian distribution.

    Args:
        box_im (arr): The boxed region.
        popt (arr): The fitted values.
    '''

    ny, nx = np.shape(box_im)
    x, y = np.meshgrid(range(nx), range(ny))

    fig = plt.figure()
    subfig = fig.add_subplot(111, projection="3d")
    subfig.plot_surface(x, y, box_im, label="Data")
    subfig.plot_surface(x, y, gaussian_2d((x, y), *popt), alpha=0.5, label="Fit")
    subfig.legend()
    plt.show()


def fit_n_gaussian(box_im, peaks):
    '''
    Fits n Gaussian distributions with a background plane to the boxed
    region.

    Args:
        box_im (arr)
            The image of the bounding box
        peaks (list)
            The list of the coordinates of the found peaks of the sources (where the peak
            of the Gaussian should be)

    Returns:
        (list), (list)
            The list of the optimised fit parameters of the n Gaussians, and the associated
            covariance matrix
    '''

    ny, nx = np.shape(box_im)
    xy = np.meshgrid(range(nx), range(ny))

    ps = []
    for peak in peaks:
        A = box_im[peak[0], peak[1]]

        sigma_x, sigma_y = 0, 0

        if A < global_bg*1.5:
            sigma_x, sigma_y = 0.75, 0.75
        else:
            sigma_x, sigma_y = nx/30, ny/30

        # each of form A, mu_x, mu_y, sigma_x, sigma_y, theta, B_x, B_y, C
        ps.append([A, peak[0], peak[1], sigma_x, sigma_y, np.pi/6, 0, 0, np.median(box_im)])

    ps = np.array(ps, dtype=float)
    ps = ps.flatten()

    return gaussian_2d_n_fit(xy_data=xy, z_data=box_im, p0=ps)


def plot_n_gaussian(box_im, popt):
    '''
    Plots the boxed region in 3D with the fitted n Gaussian
    distributions.

    Args:
        box_im (arr)
            The region of the image taken up by the box
        popt (list)
            The optimised paramaters for the Gaussian fit
    '''

    ny, nx = np.shape(box_im)
    x, y = np.meshgrid(range(nx), range(ny))

    fig = plt.figure()
    subfig = fig.add_subplot(111, projection="3d")
    subfig.plot_surface(x, y, box_im, label="Data")
    subfig.plot_surface(x, y, gaussian_2d_n((x, y), *popt), alpha=0.5, label="Fit")
    subfig.legend()
    plt.show()


def get_residuals(box_im, popt):
    '''
    Computes the residual of the fit.
    
    Args:
        box_im (arr)
            The section of the image taken up by the bounding box
        popt (list)
            The optimised Gaussian fit parameters 
    
    Returns
        residuals (arr)
            The calculated residuals between the Gaussian fit and the actual pixel values
        (float)
            The reduced chi square value for the Gaussian fit 
    '''

    ny, nx = np.shape(box_im)
    x, y = np.meshgrid(range(nx), range(ny))

    fit = gaussian_2d_n((x, y), *popt)

    residuals = box_im - fit
    residuals = np.abs(residuals)
    chi_squares = residuals*residuals
    chi_squares = chi_squares/fit
    return residuals, (np.sum(chi_squares))/(len(chi_squares) - 9)


def plot_residuals(res, chi_sq):
    '''
    Plots the residual of the fit.

    Args:
        res (arr)
            The residuals of the Gaussian fit
        chi_sq (float)
            The reduced chi square value for the fit 
    '''

    nx, ny = np.shape(res)
    x, y = np.meshgrid(range(nx), range(ny))

    fig = plt.figure()
    subfig = fig.add_subplot(111, projection="3d")
    subfig.plot_surface(x, y, res, alpha=0.5, label="Residuals")
    subfig.legend()
    # plt.title(chi_sq)
    # plt.imshow(res)


def get_ellipse_params(popt, size=ellipse_size):
    '''
    Converts the fitted values into the ellipse parameters.

    Args:
        popt (arr): The fitted values.
        size (int): The ellipse size.

    Returns:
        tuple[arr, arr, float]: The centre, the axes, and the clockwise
            rotation angle.
    '''

    return [[popt[2], popt[1]], [size*popt[4], size*popt[3]], [90-180/np.pi*popt[5], 0]]


def plot_ellipse(box_im, ellipse):
    '''
    Plots the boxed region with the fitted Gaussian distribution.

    Args:
        box_im (arr): The boxed region.
        ellipse (arr): The parameters of the fitted ellipse.
    '''

    center, diameters, angle = ellipse
    angle = angle[0]
    fig, ax = plt.subplots()
    ax.imshow(box_im, cmap="viridis")
    ax.add_patch(
        Ellipse(
            xy=center,
            width=diameters[0],
            height=diameters[1],
            angle=angle,
            fill=False,
            edgecolor="red",
        )
    )
    ax.set_aspect("equal")
    plt.show()


def shift_ellipse_coord(box, ellipse):
    '''
    Shifts the coordinate of the centre of the fitted ellipse from the
    boxed region to the full image.

    Args:
        ellipse (list): The parameters of the fitted ellipse.
        popt (arr): The fitted values.
    
    Returns:
        ellipse (list)
            The parameters of the fitted ellipse, now with the centres in global coordinates
            (those of the image)
    '''

    ellipse[0][0] += box[0][1]
    ellipse[0][1] += box[0][0]
    return ellipse


def shift_popt_coord(box, popt):
    '''
    Shifts the coordinate of the centre of the fitted Gaussian from the
    boxed region to the full image.

    Args:
        box (list): The box information.
        popt (arr): The fitted values.

    Returns:
        popt (list)
            The optimised parameters - now with the centre in global coordinates 
            (that being those of the image) 
    '''

    popt[1] += box[0][0]
    popt[2] += box[0][1]
    return popt


def pad_edge_box(box_im, bounds, source):
    '''
    Pads a box for an object on the edge of the image or with an edge defined by being
    clipped by another object's mask. 

    Args:
        box_im (arr): The boxed region.
        bounds (list): The shape of the image.

    Returns:
        padded_im (arr)
            An image twice the size of the original where the created area is padded 
            with an average fill value
        mask (arr)
            The binary mask to indicate what part of the padded image has been padded 
    '''

    half_shape = np.shape(box_im)
    midpoint_x = half_shape[1]
    midpoint_y = half_shape[0]

    fill = np.average(box_im)

    if midpoint_x > midpoint_y:
        # i.e. The object is on the edge top or bottom, and the box needs to expand vertically. 
        # i.e. the width is greater than the height and so had trouble expanding the height 
        padded_im = np.zeros((half_shape[0]*2, half_shape[1]))
        mask = np.ones((half_shape[0]*2, half_shape[1]))

        if np.abs(source[0] - bounds[0]) <= bounds[2] - 1 - source[0]: #more up than down
            #on the top
            padded_im[midpoint_y:, :] = box_im
            padded_im[:midpoint_y, :] = fill
            mask[midpoint_y:, :] = 0

        else:
            #on the bottom
            padded_im[:midpoint_y, :] = box_im
            padded_im[midpoint_y:, :] = fill
            mask[:midpoint_y, :] = 0

    elif midpoint_y > midpoint_x:
        # Object on the left or right, and so needs to be expanded horizontally 
        padded_im = np.zeros((half_shape[0], half_shape[1]*2))
        mask = np.ones((half_shape[0], half_shape[1]*2))

        if np.abs(source[1]-bounds[1]) <= bounds[3] - 1 - source[1]: #more left than right
            padded_im[:, midpoint_x:] = box_im
            padded_im[:, :midpoint_x] = fill
            mask[:, midpoint_x:] = 0

        else:
            padded_im[:, :midpoint_x] = box_im
            padded_im[:, midpoint_x:] = fill
            mask[:, :midpoint_x] = 0

    else:
        print("idk man")

    return padded_im, mask


def get_binary_mask_historic(box_im, ellipse):
    '''
    #An older version of finding the binary mask. Kept for reference.

    Computes the binary mask.

    Args:
        box_im (arr): The boxed region.
        ellipse (arr): The parameters of the fitted ellipse.

    Returns:
        arr: The binary mask.
    '''

    object_binary_mask = np.zeros(np.shape(box_im), dtype=np.uint8)
    center = tuple(np.round(ellipse[0]).astype(int))
    center = tuple((center[1], center[0])) #just some error

    axes = tuple(np.round(np.asarray(ellipse[1]) / 2).astype(int))

    object_binary_mask = cv2.ellipse(
        object_binary_mask, center, axes, ellipse[2], 0, 360,
        color=(255, 0, 0), thickness=-1
    )

    binary_mask = object_binary_mask/np.max(object_binary_mask)
    return binary_mask


def get_binary_mask(im, box, ellipse):
    '''
    Computes the binary mask.

    Args:
        im (arr): The image.
        box_im (arr): The box information.
        ellipse (arr): The parameters of the fitted ellipse.

    Returns:
        arr: The binary mask.
    '''

    object_binary_mask = np.zeros(np.shape(im), dtype=np.uint8)

    center = np.round(ellipse[0])
    center[0] += box[0][1]
    center[1] += box[0][0]
    center = tuple(center.astype(int))
    axes = tuple(np.round(np.asarray(ellipse[1]) / 2).astype(int))

    if axes[0] == 0 or axes[1] == 0:
        object_binary_mask[center[1], center[0]] = im[center[1], center[0]]
    else: 
        #Because we use different structures for different types of objects
        object_binary_mask = cv2.ellipse(
                object_binary_mask, center, axes, ellipse[2][0], 0, 360,
                color=(255, 0, 0), thickness=-1
            )
    
    binary_mask = object_binary_mask/np.max(object_binary_mask)
    return binary_mask


def get_new_image(mask, im, plot=False):
    '''
    Finds the masked image.

    Args:
        mask (arr): The binary mask.
        im (arr): The image.
        plot (bool): If True, plots the image. Defaults to False.

    Returns:
        new_image (arr)
            The newly masked image array
    '''

    new_image = np.ma.array(im, mask=mask)

    if plot:
        plt.imshow(new_image)
        plt.title("New Masked Image")
        plt.show()

    return new_image


def fit_ellipse(im, threshold, padded): #aided with copilot to use cv2
    """
    Fit an ellipse to the largest connected region at or above threshold.

    Args:
        im (arr)
            The image of the source
        threshold (float)
            The value for the threshold of the mask
        padded (bol)
            Whether the image has been padded or not
    
    Returns:
        (list)
            The parameters of the ellipse such that
                [[y, x], [a, b], [theta, 0]]
            where [y, x] is the centre and [a, b] are the axis
    """

    if not padded:
        im = np.asarray(im)

    mask = np.ascontiguousarray(
        (np.isfinite(im) & (im >= threshold)).astype(np.uint8)
    )
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No pixels meet the threshold")

    contour = max(contours, key=cv2.contourArea)
    if len(contour) < 5:
        raise ValueError("The largest thresholded region needs at least 5 boundary points")

    ellipse = cv2.fitEllipse(contour)

    return [[ellipse[0][0], ellipse[0][1]], [ellipse[1][0], ellipse[1][1]], [ellipse[2], 0]]


def get_local_background(im, centre):
    '''
    Computes the local background mean around a source.

    Args:
        im (arr): The image.
        centre (tuple): The coordinates of the brightest pixel.

    Returns:
        float: The local background mean.
    '''

    shape = np.shape(im)
    box = create_box(centre=centre, prev_box=None, bounds=[0, 0, shape[0], shape[1]], size=bg_box_size)
    box_im = get_box_image(im=im, box=box)

    return np.median(box_im.compressed())

def get_local_rms_background(im, centre):
    """
    Calcualtes the RMS background value for a local patch of sky.

    Args:
        im (arr)
            The image for the local patch of sky
        centre (list)
            The coordinates of the centre of the patch of sky in [y, x]

    Returns:
        rms (float)
            The RMS background value 
    """

    shape = np.shape(im)
    box = create_box(centre=centre, prev_box=None, bounds=[0, 0, shape[0], shape[1]], size=bg_box_size)
    box_im = get_box_image(im=im, box=box)

    pixels = box_im.flatten()

    rms = [pix**2 for pix in pixels]
    rms = np.array(rms)
    rms = rms/len(rms)
    rms = np.sqrt(np.sum(rms))
    return rms

def calculate_ratio(ellipse, cov, i):
    """
    Calculates the ratio of the ellipse axises.

    Args:
        ellipse (list)
            The list of ellipse parameters represented by
                [[y, x], [a, b], [theta, 0]]
            where [y, x] is the centre and [a, b] are the axis
        cov (list)
            The covariance matrix associated with the fit parameters
            used to determine the ellipse parameters
        i (int)
            An integer to represent which number fit the ellipse is

    Returns:
        r (float)
            The ratio of the axises
        unr_r (float)
            The uncertainty of the ratio of the axises
    """

    a = ellipse[1][0]
    b = ellipse[1][1]
    r = a/b

    unc_a = np.sqrt(cov[9*i+4][9*i+4])*ellipse_size
    unc_b = np.sqrt(cov[9*i+3][9*i+3])*ellipse_size
    unc_r = (unc_a**2 + (unc_b*r)**2)/b**2
    return r, np.sqrt(unc_r)

def finding_sources(im, centre, original_im):
    '''
    Detects a source, performs instance segmentation, and calculates the photometry. 


    NOTE: The detection threshold currently is set at 3*std of the local background mean.
    Also note: object here can mean more than one object being detected.
    

    Args:
        im (2D arr)
            The entire currently masked image to find the next source.
        centre (1D arr)
            The coordinates of the brightest pixel in order [y, x].
        original_im (2D arr)
            The original masked image with all sources unmasked.  

    Returns:
        masked_image (2D arr) 
            The currently masked image with another mask applied on top for the detect object.
        objs_shifted (list)
            The parameters of the fitted mask. The coordinates of the centre are absolute 
            coordinates in terms of the image.

            Either of form:
                [A, mu_x, mu_y, sig_x, sig_y, theta, B_x, B_y, C] 
                    which are the parameters for the fitted Gaussian from maths.py
            or:
                [[y, x], [a, b], [theta, 0]] 
                    where [y,x] is the centre in absolute coordinates, [a, b] are the axises, 
                    and theta is the rotation angle

        objs_err (list [float])
            The uncertainty of the ratio of the two axises of the fitted mask.
        flux_segment (list [float])
            The calculated flux for the object using photometry. 
        flux_segment_err (list [float])
            The uncertainty of the calculated flux for the object.
        snr (list [float])
            The calculated SNR using the definition from this paper:
                Deeg HJ, Doyle LR. VAPHOT - A Package for Precision Differential Aperture Photometry. In: Borucki WJ, Lasher LE. (eds.) Third Workshop on Photometry. Moffett Field, United States: NASA Ames Research Center; 2001. p. 85–93. https://ui.adsabs.harvard.edu/abs/2001phot.work...85D/abstract. 
    '''

    centre_pixel = im[centre]
    shape = np.shape(im)
    bounds = [0, 0, shape[0], shape[1]] #basically [min y, min x, max y, max x]

    # Create first bounding box.
    box = create_box(centre=centre, prev_box=None, bounds=bounds)
    box_im = get_box_image(im=im, box=box)
    box_im_edge = np.concatenate(
        (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
    )

    # Establish a local background from a signficantly larger bounding box.
    local_bg = get_local_background(im=im, centre=centre)
    #local_rms = get_local_rms_background(im=im, centre=centre)
    threshold = local_bg + 3*bg_threshold


    # For the case where the bounding box is on an edge -> need to redefine the bounds.
    # Edges of masks are treated like edges of an image.
    masked_cols_i = np.flatnonzero(box_im.mask.all(axis=0))
    if len(masked_cols_i) > 0:
        min_i = np.min(masked_cols_i)
        max_i = np.max(masked_cols_i)
        min_masked_x = box[0][1] + min_i
        max_masked_x = box[0][1] + max_i
        if centre[1] < min_masked_x: 
            #if source is to the left of the masked columns 
            bounds = (bounds[0], bounds[1], bounds[2], min_masked_x)
        else: 
            #if source is to the right of the masked columns 
            bounds = (bounds[0], max_masked_x+1, bounds[2], bounds[3])


    while (box_im_edge > threshold).sum() > (len(box_im_edge) / 2):
        # i.e. If the number of pixels on the edge that are above the threshold is larger than a half.
        # Creating new bounding box until condtion is met. 

        box = create_box(centre=centre, prev_box=box, bounds=bounds, size=box_size)
        box_im = get_box_image(im=im, box=box)

        box_im_edge = np.concatenate(
            (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
        )

        if np.mean(box_im.compressed()) < (threshold):
            # No signficant contribution from an object -> likely to be a hot pixel.
            print("Discarding hot pixel.")
            mask = np.zeros_like(im)
            mask[centre[0], centre[1]] = 1
            masked_image = np.ma.array(im, mask=mask)
            return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan], np.array([np.nan])

    # Establishing conditons which deal with objects on edges and masked and partially masked by other objects.
    edge_mask = None

    # Establishing lists for vlaues to return. 
    bms = []
    flux_segment = []
    flux_segment_err = []
    objs = []
    objs_shifted = []
    objs_err = []
    snr = []


    try:
        if box[1] != box[2]: 
            # Edge boxes are padded beyond their edge to allow fitting a mask. This is inspired by 
            # pooling on the edges used in computer vision. The source is discarded as there 
            # is incomplete information. 

            box_im, edge_mask = pad_edge_box(box_im=box_im, bounds=bounds, source=centre)

            box_im = np.ma.array(box_im, mask=edge_mask)

            obj = fit_ellipse(box_im, np.ma.median(box_im), True)

            obj_shifted = shift_ellipse_coord(box=box, ellipse=obj)


            def flatten(xss): 
            # Using method from:
            # https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
                return [x for xs in xss for x in xs]

            
            obj_shifted = np.array(flatten(obj_shifted))
            objs_shifted.append(obj_shifted)


            obj[0][0] -= box[0][1]
            obj[0][1] -= box[0][0]
            bm = get_binary_mask(im=im, box=box, ellipse=obj)
            bms.append(bm)


            image_mask = np.ma.getmask(im)
            masked_bm = np.ma.array(bm, mask=image_mask)

            # Photometry
            area = np.ma.sum(masked_bm)
            flux = np.ma.sum(im * bm)
            flux_err = np.sqrt(flux - area * bg_threshold**2)
            flux = flux - local_bg * area
            flux_segment.append(flux)
            flux_segment_err.append(flux_err)

            objs_err.append(np.nan)
            noise = np.sqrt(flux + (11*area)**2)
            snr.append((flux)/noise)
        else:
            peaks = peak_local_max(box_im, min_distance=6, threshold_abs=(threshold)) #if multiple sources

            if len(peaks) == 0:
                peaks_i = np.unravel_index(np.argmax(box_im), np.shape(box_im))
                peaks = [[peaks_i[0], peaks_i[1]]]
         
            objs, cov = fit_n_gaussian(box_im=box_im, peaks=peaks)
            # plot_gaussian(box_im=box_im, popt=obj[0])


            no_of_objs = len(objs)//9
            objs = objs.reshape(no_of_objs, 9)

            for i, obj in enumerate(objs):
                if obj[3] > box[2] or obj[4] > box[1]:
                    # If the std dev of the fitted Gaussian is larger than the dimen of box.
                    # Result is unreliable, and so we mask it as it is unphysical.
                    print("Fitted parameters outside region of interest.")

                    mask = np.zeros_like(im)
                    mask[centre[0], centre[1]] = 1
                    masked_image = get_new_image(mask=mask, im=im)
                    return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan], np.array([np.nan])
                
                elif (obj[1] < np.abs(peaks[i][0]-obj[3])) or (obj[1] > np.abs(peaks[i][0]+obj[3])) or (obj[2] < np.abs(peaks[i][1]-obj[4])) or (obj[2] > np.abs(peaks[i][1]+obj[4])):
                    # If the fitted peak location if not within a std dev of the actual peak values.
                    # We move the mask to be centred on the peak values. 
                    # These objects are kept because of the std dev being within the confines of the box.

                    obj[1] = peaks[i][0]
                    obj[2] = peaks[i][1]

                if obj[3]*ellipse_size < 3 or obj[4]*ellipse_size < 3: 
                    # If the detected object is smaller than the 6 pixel detection limit.
                    print("Detected object smaller than resolution.")

                    ellipse=get_ellipse_params(popt=obj)
                    mask = get_binary_mask(im=im, box=box, ellipse=ellipse)
                    masked_image = get_new_image(mask=mask, im=im)
                    return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan], np.array([np.nan])


                ellipse = get_ellipse_params(popt=obj)

                r, unc_r = calculate_ratio(ellipse, cov, i)

                obj_shifted = shift_popt_coord(box=box, popt=obj)
                objs_shifted.append(obj_shifted)


                bm = get_binary_mask(im=im, box=box, ellipse=ellipse)
                bms.append(bm)



                ellipse_area = np.sum(bm)

                image_mask = np.ma.getmask(im)
                masked_bm = np.ma.array(bm, mask=image_mask)

                area = np.ma.sum(masked_bm)

                flux = 0
                flux_err = 0

                if ellipse_area > area:
                    # If the fitted mask if clipped by another mask.

                    image_mask = np.ma.getmask(original_im)

                    clipped_section = np.ma.array(bm, mask=image_mask)
                    clipped_area = np.ma.sum(clipped_section)

                    if ellipse_area > clipped_area:
                        # If the mask if clipped by the preprocessing mask.
                        # Discard as missing information.

                        flux = np.nan
                        flux_err = np.nan
                    else:
                        # If not the preprocessing mask, treat image as if no masks are applied
                        # in order to calculate photometry. 

                        select_ellipse = bm*original_im

                        flux = np.ma.sum(select_ellipse)
                        area = np.sum(bm) 

                        flux_err = np.sqrt(flux - area * bg_threshold**2)
                        flux = flux - local_bg * area
                else:
                    flux = np.ma.sum(im * bm)
                    flux_err = np.sqrt(flux - area * bg_threshold**2)
                    flux = flux - local_bg * area

                objs_err.append(unc_r)
                flux_segment.append(flux)
                flux_segment_err.append(flux_err)

                noise = np.sqrt(flux + (11*area)**2) # From the equation given in the paper mentioned above.
                snr.append((flux)/noise)


    except RuntimeError as exc:
        # If a Gaussian can't be fitted -> treat as a stray or hot pixel.
        print(f"Gaussian fit failed: {exc}")
        bm = np.zeros_like(im)
        bm[centre[0], centre[1]] = 1
        masked_image = im
        masked_image = get_new_image(mask=bm, im=masked_image)
        obj = np.array([np.nan])
        flux = [np.nan]
        flux_err = [np.nan]
        objs_err = [np.nan]
        peak_value = [centre_pixel]
        snr = np.array([np.nan])
        return masked_image, obj, objs_err, flux, flux_err, snr


    masked_image = im
    for bm_mask in bms:
        masked_image = get_new_image(mask=bm_mask, im=masked_image)

    if centre_pixel > saturation:
        # Dicarding all oversaturated objects while masking them.
        print("object oversaturated")
        objs_shifted = np.array([np.nan])
        flux_segment = [np.nan]
        flux_segment_err = [np.nan]
        objs_err = [np.nan]
        snr = np.array([np.nan])

    return masked_image, objs_shifted, objs_err, flux_segment, flux_segment_err, snr

def add_incomplete_masks(im):
    """
    A function to extend certain incomplete masks for very visible and obvious stars. 

    Inputs
        im (2D arr)
            The original image with the preprocessing mask applied
    
    Outputs
        im (2D arr)
            The image with the masks completed.
    """

    stripe_mask = np.zeros_like(im)
    stripe_mask[2613:, 1447:1449] = 1
    im = get_new_image(mask=stripe_mask, im=im)

    #incomplete star masks 
    circles = [[[1772, 577], [25, 25], [0, 0]], [[1690, 36], [30, 30], [0, 0]], [[1365, 4331], [20, 20], [0, 0]], 
               [[1312, 4400], [30, 30], [0, 0]], [[1339, 4587], [20, 20], [0, 0]]]
    boxes = [[[0, 0], 20, 20], [[0,0], 30, 30], [[0,0], 20, 20], [[0,0], 30, 30], [[0,0], 20, 20]]

    for i in range(len(circles)):
        circle_mask = get_binary_mask(im=im, box=boxes[i], ellipse=circles[i])
        im = get_new_image(mask=circle_mask, im=im)

    #two hot pixels at the bottom
    bottom = np.zeros_like(im)
    bottom[4607:4608, 690:692] = 1
    im = get_new_image(mask=bottom, im=im)
    return im 

def run_photometry():
    '''
    Runs the photometry of the image with a preprocessing mask applied.

    Outputs
        fluxes.json (file)
            File containing the calculated flux per object
        fluxes_err.json (file)
            File containing the calcuated flux uncertainty per object
        shapes.json (file)
            File containing the parameters of the mask of the object
        shapes_err.json (file)
            File containing the uncertainty in the ratio of axises of the object mask
        SNR.json (file)
            File containing the calculated SNR per detected object
    '''

    im = image
    im = add_incomplete_masks(im)
    original_im = im

    # Patches of the sky used for testing
    # im = image[2560:4601, 1549:2500]

    # im = im[0:15, 540:590]  #example of an edge object for the segment
    # im = np.transpose(im) #applying different orientations to test robustness
    # im = im[::-1, ::-1]

    centre = find_centre(im=im)

    plt.imshow(im)
    plt.title("Original Image with Preprocessing Mask")
    plt.show()

    # Values to be written to JSON files.
    objects = []
    fluxes = []
    fluxes_err = []
    shape_batches = []
    shape_err_batches = []
    snr_batches = []


    detectable = True 
    obj_i = 0
    while centre is not None and detectable:
        im, objs, objs_err, f, f_err, snr = finding_sources(im=im, centre=centre, original_im=original_im)

        for i, obj in enumerate(objs):
            objects.append(obj)
            fluxes.append(f[i])
            fluxes_err.append(f_err[i])
            obj_i += 1

            if np.isnan(f[i]) == False: 
                if int(f[i]) == 0:
                    # If there is no source detected.
                    print("All detectable sources found.")
                    detectable = False


        # Data files
        with open("data/fluxes.json", "w") as flux_file:
            json.dump([float(value) for value in fluxes], flux_file)
            flux_file.close()

        with open("data/fluxes_err.json", "w") as flux_err_file:
            json.dump([float(value) for value in fluxes_err], flux_err_file)
            flux_err_file.close()

        shape_batches.append([obj.tolist() for obj in objs])
        with open("data/shapes.json", "w") as shape_file:
            json.dump([shape for batch in shape_batches for shape in batch], shape_file)

        shape_err_batches.append([float(err) for err in objs_err])
        with open("data/shapes_err.json", "w") as shape_err_file:
            json.dump([err for batch in shape_err_batches for err in batch], shape_err_file)
            shape_err_file.close()

        snr_batches.append([float(s) for s in snr])
        with open("data/SNR.json", "w") as file:
            json.dump([s for batch in snr_batches for s in batch], file)
            file.close()

        centre = find_centre(im=im)

        print(obj_i) #progress 

    

run_photometry()
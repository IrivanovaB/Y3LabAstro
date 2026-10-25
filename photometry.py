'''
A module for the photometry.
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
debug = False


# Note that all of the following are in (y, x) instead of (x, y).


def find_centre(im):
    '''
    Finds the coordinates of the brightest pixel in an image.

    NOTE: The detection threshold currently is set at 1*std of the
    global background mean.

    Args:
        im (arr): The image.

    Returns:
        tuple: The coordinates of the brightest pixel.
    '''
    max_index = np.unravel_index(np.argmax(im), np.shape(im))
    if im[max_index] < (global_bg + bg_threshold):
        print("All sources found!")
        return None
    return max_index


def edge_box(bounds, dx, dy, debug_mode=False):
    '''
    For a box which is partially outside the image.

    Args:
        bounds [min y, min x, max y, max x]
        dx (list): [x2, x1], where x2 < x1. x2 is restricted by the
            boundary bounds[1], and x1 the boundary bounds[3].
        dy (list): [y2, y1], where y2 < y1. y2 is restricted by the
            boundary bounds[0], and y1 the boundary bounds[2].

    Returns:
        list: The updated coordinates of the box, its height, and its
            width.
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


def create_box(centre, prev_box, bounds, size=box_size, debug_mode=False):
    '''
    Creates a new box based on the information of the previous box.

    Args:
        centre (tuple): The coordinates of the centre of the box.
        prev_box (list | None): The information of the previous box. If
            None, no previous boxes exist.
        bounds [min y, min x, max y, max x]

    Returns:
        list: The coordinates of the top left corner of the box, its
            height, and its width.
    '''

    if prev_box is None:
        dx = [centre[1] - size, centre[1] + size]
        dy = [centre[0] - size, centre[0] + size]
        if ((dx[0] < bounds[1]) or (dx[1] > bounds[3])
            or (dy[0] < bounds[0]) or (dy[1] > bounds[2])):
            # (dx[0]<0) means that to the bottom of the centre it goes
            # beyond the image.
            # (dx[1]>bounds[1]) this means that to the top of the
            # centre it goes beyond the image.
            # Similarly for dy.

            # cs is (y2, x2, y1, x1).
            cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy, debug_mode=debug_mode)

            # Starting in the bottom left (i.e. top left i think).
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
        cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy, debug_mode=debug_mode)
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
    '''
    _, _, box_coords = get_box_coords(box)
    return im[box_coords[0][0]:(box_coords[2][0]+1),
              box_coords[0][1]:(box_coords[2][1]+1)]


def box_in_sky(im, box, centre):
    '''
    Plots the boxed region and its surrounding image.

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
    #plt.show()


def fit_n_gaussian(box_im, peaks, debug_mode):
    '''
    Fits n Gaussian distributions with a background plane to the boxed
    region.
    '''
    ny, nx = np.shape(box_im)
    xy = np.meshgrid(range(nx), range(ny))

    ps = []
    for peak in peaks:
        #A, mu_x, mu_y, sigma_x, sigma_y, theta, B_x, B_y, C
        A = box_im[peak[0], peak[1]]

        sigma_x, sigma_y = 0, 0

        if A < global_bg*1.5:
            sigma_x, sigma_y = 0.75, 0.75
        else:
            sigma_x, sigma_y = nx/30, ny/30

        ps.append([A, peak[0], peak[1], sigma_x, sigma_y, np.pi/6, 0, 0, np.median(box_im)])

    #Trying to resolve the error of curve fit returning []. 

    if debug_mode:
        print(f"parameters: {ps}")

    ps = np.array(ps, dtype=float)
    ps = ps.flatten()

    return gaussian_2d_n_fit(xy_data=xy, z_data=box_im, p0=ps)


def plot_n_gaussian(box_im, popt):
    '''
    Plots the boxed region in 3D with the fitted n Gaussian
    distributions.
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
    net_turn = popt[5]/(2*np.pi) - popt[5]//(2*np.pi)

    return ((popt[2], popt[1]), (size*popt[4], size*popt[3]), 90-180/np.pi*popt[5])
    # return ((popt[2], popt[1]), (ellipse_size*popt[4], ellipse_size*popt[3]),
    #         90 - 180*net_turn/(np.pi))


def plot_ellipse(box_im, ellipse):
    '''
    Plots the boxed region with the fitted Gaussian distribution.

    Args:
        box_im (arr): The boxed region.
        ellipse (arr): The parameters of the fitted ellipse.
    '''
    center, diameters, angle = ellipse
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
    '''
    popt[1] += box[0][0]
    popt[2] += box[0][1]
    return popt


def pad_edge_box(box_im, bounds, source):
    '''
    Pads the edge box.

    Args:
        box_im (arr): The boxed region.
        bounds (list): The shape of the image.

    Returns:
        tuple[arr, arr, arr, arr]: The padded image, xi, yi, and the
            mask.
    '''
    half_shape = np.shape(box_im)
    midpoint_x = half_shape[1]
    midpoint_y = half_shape[0]

    # x_i = np.arange(0, midpoint_x, 1)
    # y_i = np.arange(0, midpoint_y, 1)

    fill = np.average(box_im)

    #if (x_i == 0).any() or (x_i >= bounds[1]-1).any():
    if midpoint_x > midpoint_y:
        # i.e. The object is on the edge top or bottom.
        # So expanding this vertically. 
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
    #elif (y_i == 0).any() or (y_i >= bounds[0]-1).any():
    elif midpoint_y > midpoint_x:
        # Object on the left or right.
        # So expanding horizontally
        padded_im = np.zeros((half_shape[0], half_shape[1]*2))
        mask = np.ones((half_shape[0], half_shape[1]*2))
        if np.abs(source[1]-bounds[1]) <= bounds[3] - 1 - source[1]: #more left than right
            # box_im[midpoint_y:, :] = rb
            # box_im[:midpoint_y, :] = fill
            # mask[midpoint_y:, :] = 1
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
    #just an old version in case we needed it 
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


def get_binary_mask(im, box, ellipse, debug_mode=False):
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
        object_binary_mask = cv2.ellipse(
                object_binary_mask, center, axes, ellipse[2], 0, 360,
                color=(255, 0, 0), thickness=-1
            )

    if debug_mode: 
        print("Ellipse being plotted")
        print(center, axes, ellipse[2])
        plt.imshow(object_binary_mask)
        plt.show()

    binary_mask = object_binary_mask/np.max(object_binary_mask)
    return binary_mask


def get_new_image(mask, box, im, padded_image, edge_mask, padded, plot=False):
    '''
    Finds the masked image.

    Args:
        xi (arr):
        yi (arr):
        mask (arr): The binary mask.
        box (arr): The information of the box.
        im (arr): The image.
        plot (bool): If True, plots the image. Defaults to False.
    '''
    # _, _, bc = get_box_coords(box)

    # box_im = get_box_image(im=im, box=box)
    new_image = im

    if padded:
        #combined_mask = np.ma.mask_or(mask, edge_mask)
        #masked_image = np.ma.array(padded_image, mask=combined_mask)

        yi, xi = np.where(edge_mask!=1)

        #masked_image = masked_image[yi[0]:(yi[-1]+1), xi[0]:(xi[-1]+1)]
        # new_image[bc[0][0]:(bc[2][0]+1), bc[0][1]:(bc[2][1]+1)] = np.ma.array(
        #     new_image[bc[0][0]:(bc[2][0]+1), bc[0][1]:(bc[2][1]+1)],
        #     mask=edge_mask[yi[0]:(yi[-1]+1), xi[0]:(xi[-1]+1)]
        # )
        new_image = np.ma.array(new_image, mask=mask)
    else:
        # xi = np.arange(0, np.shape(box_im)[1], 1)
        # yi = np.arange(0, np.shape(box_im)[0], 1)
        # # Refined box.
        # rb = [bc[0][1]+xi[0], bc[0][1]+xi[-1], bc[0][0]+yi[0], bc[0][0]+yi[-1]]

        # new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1] = np.ma.array(
        #     new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1], mask=mask
        # )
        new_image = np.ma.array(new_image, mask=mask)
    #new_image = np.ma.array(new_image, mask=mask)

    # plt.imshow(new_image)
    # plt.show()

    # if plot:
    #     plt.imshow(new_image)
    #     plt.xlim(rb[0], rb[1])
    #     plt.ylim(rb[2], rb[3])
    #     plt.title("Area Removed by Mask")
    #     plt.show()

    return new_image


def fit_ellipse(im, threshold): #this function was vibe coded with copilot to be improved/ammended later - just currently need to get something to work 
    """Fit an ellipse to the largest connected region at or above threshold.

    Returns ``((center_x, center_y), (diameter_1, diameter_2), angle_degrees)``,
    with coordinates relative to ``im``.
    """
    im = np.asarray(im)
    #debug with copilot as masked objects are hard to work with
    # data = np.ma.getdata(im)
    # valid = ~np.ma.getmaskarray(im) & np.isfinite(data)
    # plt.imshow(valid)
    # plt.show()
    # mask = np.ascontiguousarray((valid & (data >= threshold)).astype(np.uint8))

    # plt.imshow(mask)
    # plt.show()
    mask = np.ascontiguousarray(
        (np.isfinite(im) & (im >= threshold)).astype(np.uint8)
    )
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No pixels meet the threshold")

    contour = max(contours, key=cv2.contourArea)
    if len(contour) < 5:
        raise ValueError("The largest thresholded region needs at least 5 boundary points")

    return cv2.fitEllipse(contour)


def get_local_background(im, centre):
    '''
    Computes the local background mean around a source.

    Args:
        im (arr): The image.
        centre (tuple): The coordinates of the brightest pixel.

    Returns:
        float: The local background mean.
    '''
    # box = [[centre[0] - bg_box_size, centre[1] - bg_box_size],
    #        2*bg_box_size + 1, 2*bg_box_size + 1]
    shape = np.shape(im)
    box = create_box(centre=centre, prev_box=None, bounds=[0, 0, shape[0], shape[1]], size=bg_box_size)
    box_im = get_box_image(im=im, box=box)

    return np.median(box_im.compressed())

def get_local_rms_background(im, centre):
    shape = np.shape(im)
    box = create_box(centre=centre, prev_box=None, bounds=[0, 0, shape[0], shape[1]], size=bg_box_size)
    box_im = get_box_image(im=im, box=box)

    pixels = box_im.flatten()

    rms = [pix**2 for pix in pixels]
    rms = np.array(rms)
    rms = rms/len(rms)
    rms = np.sqrt(np.sum(rms))
    return rms


def finding_masks(im, centre, debug_mode, original_im, preprocessing_clipped, objects_clipped):
    '''
    Masks a source.

    NOTE: The detection threshold currently is set at 3*std of the
    local background mean.

    Args:
        im (arr): The image.
        centre (tuple): The coordinates of the brightest pixel.

    Returns:
        tuple[arr, arr, arr]: The masked image, the parameters of the
            fitted object, and the flux of the source.
    '''
    centre_pixel = im[centre]
    shape = np.shape(im)
    bounds = [0, 0, shape[0], shape[1]] #basically [min y, min x, max y, max x]
    box = create_box(centre=centre, prev_box=None, bounds=bounds)
    box_im = get_box_image(im=im, box=box)
    box_im_edge = np.concatenate(
        (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
    )
    local_bg = get_local_background(im=im, centre=centre)
    threshold = local_bg + 3*bg_threshold

    local_rms = get_local_rms_background(im=im, centre=centre)
    #threshold = local_bg

    # if np.array([box_im.compressed() > local_bg]).sum() < 5:
    #     # print([box_im > local_bg])
    #     plt.imshow(box_im)
    #     plt.show()
    #     mask = np.zeros(np.shape(im))
    #     # above_med = box_im[box_im > local_bg]
    #     mask[centre[1], centre[0]] = 1
    #     masked_image = np.ma.array(im, mask=mask)
    #     return masked_image, [np.nan], [np.nan]
    box_growth = 0

    masked_cols_i = np.flatnonzero(box_im.mask.all(axis=0))
    if len(masked_cols_i) > 0:
        min_i = np.min(masked_cols_i)
        max_i = np.max(masked_cols_i)
        min_masked_x = box[0][1] + min_i
        max_masked_x = box[0][1] + max_i
        if centre[1] < min_masked_x: #if source is to the left of the masked columns 
            bounds = (bounds[0], bounds[1], bounds[2], min_masked_x)
        else: #if source is to the right of the masked columns 
            bounds = (bounds[0], max_masked_x+1, bounds[2], bounds[3])

    if debug_mode:
        box = create_box(centre=centre, prev_box=box, bounds=bounds, size=box_size, debug_mode=debug_mode)
        box_in_sky(im=im, box=box, centre=centre)

    while (box_im_edge > threshold).sum() > (len(box_im_edge) / 2):
        # i.e. If the number of pixels on the edge that are above the
        # threshold is larger than a half.
        box = create_box(centre=centre, prev_box=box, bounds=bounds, size=box_size, debug_mode=debug_mode)
        box_im = get_box_image(im=im, box=box)

        box_im_edge = np.concatenate(
            (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
        )

        #box_in_sky(im=im, box=box, centre=centre)
        if np.mean(box_im.compressed()) < (threshold):
            print("just a bright pixel amongst some noise")
            mask = np.zeros_like(im)
            mask[centre[0], centre[1]] = 1
            masked_image = np.ma.array(im, mask=mask)
            return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan], preprocessing_clipped, objects_clipped, [centre_pixel], np.array([np.nan])

    if debug_mode:
        box_in_sky(im=im, box=box, centre=centre)

    # if box[1] != box[2]:
    #     box_im, xi, yi, edge_mask = pad_edge_box(box_im=box_im, bounds=bounds)
    #     plt.imshow(box_im)
    #     plt.title("padded box")
    #     plt.show()

    edge_mask = None
    padded_image = None
    padded = False

    bms = []
    flux_segment = []
    flux_segment_err = []
    objs = []
    objs_shifted = []
    objs_err = []
    peak_values = []
    snr = []

    try:
        if box[1] != box[2]:
            box_im, edge_mask = pad_edge_box(box_im=box_im, bounds=bounds, source=centre)
            padded = True

            box_im = np.ma.array(box_im, mask=edge_mask)

            obj = fit_ellipse(box_im, np.ma.median(box_im))
            obj = [[obj[0][0], obj[0][1]], [obj[1][0], obj[1][1]], obj[2]]
            if debug_mode:
                print(centre)
                print(obj)
                plot_ellipse(box_im=box_im, ellipse=obj)


            ellipse_list = [[obj[0][0], obj[0][1]], [obj[1][0], obj[1][1]], [obj[2], 0]]
            obj_shifted = shift_ellipse_coord(box=box, ellipse=ellipse_list)

            def flatten(xss): #https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
                return [x for xs in xss for x in xs]
            
            obj_shifted = np.array(flatten(obj_shifted))
            objs_shifted.append(obj_shifted)

            if debug_mode:
                print(f"obj {obj}")
                plt.imshow(box_im)
                plt.show()


            bm = get_binary_mask(im=im, box=box, ellipse=obj)
            bms.append(bm)
            # bm = get_box_image(im=bm, box=box)
            image_mask = np.ma.getmask(im)
            masked_bm = np.ma.array(bm, mask=image_mask)

            area = np.ma.sum(masked_bm)
            flux = np.ma.sum(im * bm)
            flux_err = np.sqrt(flux - area * bg_threshold**2)
            flux = flux - local_bg * area
            flux_segment.append(flux)
            flux_segment_err.append(flux_err)

            objs_err.append(np.nan)
            peak_values.append(centre_pixel)
            noise = np.sqrt(flux + (11*area)**2)
            snr.append((flux-local_bg)/noise)
        else:
            if debug_mode:
                print(f"threshold {threshold}")
            peaks = peak_local_max(box_im, min_distance=6, threshold_abs=(threshold))

            if len(peaks) == 0:
                #peaks = [[centre[1], centre[0]]]
                peaks_i = np.unravel_index(np.argmax(box_im), np.shape(box_im))
                peaks = [[peaks_i[0], peaks_i[1]]]

            objs, cov = fit_n_gaussian(box_im=box_im, peaks=peaks, debug_mode=debug_mode)

            if debug_mode:
                print(peaks)
                print(f"fitted object: {objs}")
                plot_n_gaussian(box_im=box_im, popt=objs)
                plt.show()

            # obj = fit_gaussian(box_im=box_im)
            # plot_gaussian(box_im=box_im, popt=obj[0])

            #residuals, chi_sq = get_residuals(box_im=box_im, popt=objs)
            #plot_residuals(residuals, chi_sq)
            #plt.show()

            #need to discuss methods
            no_of_objs = len(objs)//9

            objs = objs.reshape(no_of_objs, 9)

            for i, obj in enumerate(objs):
                if obj[3] > box[2] or obj[4] > box[1]:
                    print("Stdev outside the box")
                    #basically if stddev goes outside the box then the result is unreliable and we mask it as it is unphysical (possibly can denote how often this happens)
                    mask = np.zeros_like(im)
                    mask[centre[0], centre[1]] = 1
                    masked_image = get_new_image(mask=mask, box=box, im=im, padded_image=padded_image, edge_mask=edge_mask, padded=padded)
                    return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan], preprocessing_clipped, objects_clipped, [box_im[peaks[i][0], peaks[i][1]]], np.array([np.nan])
                #brute force: basically if fitted peak is not within stddev of actual peak
                elif (obj[1] < np.abs(peaks[i][0]-obj[3])) or (obj[1] > np.abs(peaks[i][0]+obj[3])) or (obj[2] < np.abs(peaks[i][1]-obj[4])) or (obj[2] > np.abs(peaks[i][1]+obj[4])):
                    print("peak outside the box")
                    obj[1] = peaks[i][0]
                    obj[2] = peaks[i][1]
                if obj[3]*ellipse_size < 3 or obj[4]*ellipse_size < 3: #6 pixel detection limit
                    print("Detected object too small")
                    ellipse=get_ellipse_params(popt=obj)
                    mask = get_binary_mask(im=im, box=box, ellipse=ellipse)
                    masked_image = get_new_image(mask=mask, box=box, im=im, padded_image=padded_image, edge_mask=edge_mask, padded=padded)
                    return masked_image, np.array([np.nan]), np.array([np.nan]), [np.nan], [np.nan],preprocessing_clipped, objects_clipped, [box_im[peaks[i][0], peaks[i][1]]], np.array([np.nan])

                    #im, objs, objs_err, f, f_err, preprocessing_clipped, objects_clipped


                ellipse = get_ellipse_params(popt=obj)

                a = ellipse[1][0]
                b = ellipse[1][1]
                r = a/b

                unc_a = np.sqrt(cov[9*i+4][9*i+4])*ellipse_size
                unc_b = np.sqrt(cov[9*i+3][9*i+3])*ellipse_size

                unc_r = (unc_a**2 + (unc_b*r)**2)/b**2

                obj_err = np.sqrt(unc_r)

                if debug_mode:
                    plot_ellipse(box_im=box_im, ellipse=ellipse)

                obj_shifted = shift_popt_coord(box=box, popt=obj)
                objs_shifted.append(obj_shifted)

                bm = get_binary_mask(im=im, box=box, ellipse=ellipse)
                bms.append(bm)

                ellipse_area = np.sum(bm)

                # bm = get_box_image(im=bm, box=box)
                image_mask = np.ma.getmask(im)
                masked_bm = np.ma.array(bm, mask=image_mask)

                area = np.ma.sum(masked_bm)

                flux = 0
                flux_err = 0
                

                #i.e. if the fit is clipped by any mask
                if ellipse_area > area:
                    # #if ignoring these alternatively
                    # flux = np.nan
                    # flux_err = np.nan

                    image_mask = np.ma.getmask(original_im)

                    clipped_section = np.ma.array(bm, mask=image_mask)

                    clipped_area = np.ma.sum(clipped_section)

                    #if the fit is clipped by the preprocessing mask 
                    if ellipse_area > clipped_area:
                        preprocessing_clipped += 1 
                        flux = np.nan
                        flux_err = np.nan
                    else:
                        #only ellipse left
                        #select_ellipse = np.ma.array(im, mask=clipped_section)
                        select_ellipse = bm*original_im

                        flux = np.ma.sum(select_ellipse)
                        area = np.sum(bm) 

                        flux_err = np.sqrt(flux - area * bg_threshold**2)
                        flux = flux - local_bg * area
                        objects_clipped += 1
                else:
                    flux = np.ma.sum(im * bm)
                    flux_err = np.sqrt(flux - area * bg_threshold**2)
                    flux = flux - local_bg * area

                objs_err.append(obj_err)
                flux_segment.append(flux)
                flux_segment_err.append(flux_err)
                peak_values.append(box_im[peaks[i][0], peaks[i][1]])
                noise = np.sqrt(flux + (11*area)**2)
                snr.append((flux-local_bg)/noise)


        # ellipse = get_ellipse_params(popt=objs)
        # plot_ellipse(box_im=box_im, ellipse=ellipse)

        # bm = get_binary_mask(box_im=box_im, ellipse=ellipse)
        # flux = np.sum(box_im * bm)
        # bm_r = 1 - bm
        # bg_flux = np.mean(box_im * bm_r)
        # flux = flux - bg_flux * bm.sum()


    except RuntimeError as exc:
        print(f"Gaussian fit failed: {exc}")
        bm = np.zeros_like(im)
        bm[centre[0], centre[1]] = 1
        masked_image = im
        masked_image = get_new_image(
            mask=bm, box=box, im=masked_image, padded_image=padded_image,
            edge_mask=edge_mask, padded=padded
        )
        obj = np.array([np.nan])
        flux = [np.nan]
        flux_err = [np.nan]
        objs_err = [np.nan]
        peak_value = [centre_pixel]
        snr = np.array([np.nan])
        return masked_image, obj, objs_err, flux, flux_err, preprocessing_clipped, objects_clipped, peak_value, snr


    masked_image = im
    for bm_mask in bms:
        #masked_image = get_new_image(xi=xi, yi=yi, mask=bm, box=box, im=im)
        masked_image = get_new_image(
            mask=bm_mask, box=box, im=masked_image, padded_image=padded_image,
            edge_mask=edge_mask, padded=padded
        )

    if centre_pixel > saturation:
            print("object oversaturated")
            objs_shifted = np.array([np.nan])
            flux_segment = [np.nan]
            flux_segment_err = [np.nan]
            objs_err = [np.nan]
            peak_values = [im[centre]]
            snr = np.array([np.nan])

    return masked_image, objs_shifted, objs_err, flux_segment, flux_segment_err, preprocessing_clipped, objects_clipped, peak_values, snr


def run_photometry():
    '''
    Runs the photometry.
    '''
    im = image
    #im[2975:3020, 1447:1449] = 0
    stripe_mask = np.zeros_like(im)
    stripe_mask[2613:, 1447:1449] = 1
    im = get_new_image(mask=stripe_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #incomplete mask
    circle = [[1772, 577], [25, 25], 0]
    circle_mask = get_binary_mask(im=im, box=[[0, 0], 20, 20], ellipse=circle)
    #plot_ellipse(im[567:588, 1762:1783], ellipse = circle)
    im = get_new_image(mask=circle_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #incomplete mask
    circle_2 = [[1690, 36], [30, 30], 0]
    circle_2_mask = get_binary_mask(im=im, box=[[0,0], 30, 30], ellipse=circle_2)
    im = get_new_image(mask=circle_2_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #incomplete mask
    circle_3 = [[1365, 4331], [20, 20], 0]
    circle_3_mask = get_binary_mask(im=im, box=[[0,0], 20, 20], ellipse=circle_3)
    im = get_new_image(mask=circle_3_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #incomplete mask
    circle_4 = [[1312, 4400], [30, 30], 0]
    circle_4_mask = get_binary_mask(im=im, box=[[0,0], 30, 30], ellipse=circle_4)
    im = get_new_image(mask=circle_4_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #this is a corrupted object on the bottom - basically it has a mask over it by the time i have detected it but there are a bunch of 0 squares around it and inside it and also a lot of bright spots surrounding it
    circle_5 = [[1339, 4587], [20, 20], 0]
    circle_5_mask = get_binary_mask(im=im, box=[[0,0], 20, 20], ellipse=circle_5)
    im = get_new_image(mask=circle_5_mask, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    #two pixels at the bottom
    bottom = np.zeros_like(im)
    bottom[4607:4608, 690:692] = 1
    im = get_new_image(mask=bottom, box=None, im=im, padded_image=None, edge_mask=None, padded=False)

    original_im = im

    #im[im>36000] = 36000
    #im = image[2560:4601, 1549:2500]

    #im = im[950:1010, 620:680]
    # im = image
    #im = im[0:15, 540:590]  #example of an edge object for the segment

    # im = np.transpose(im)
    # im = im[::-1, ::-1]

    centre = find_centre(im=im)

    plt.imshow(im)
    plt.title("Original segment")
    plt.show()

    objects = []
    objects_errors = []
    fluxes = []
    fluxes_err = []
    # with open("fluxes.json", "w") as flux_file:
    #     json.dump(fluxes, flux_file)

    debug = False

    data = {}
    shape_batches = []
    shape_err_batches = []
    peak_batches = []
    snr_batches = []

    
    preprocessing_clipped = 0
    objects_clipped = 0

    obj_i = 0
    while centre is not None:
        before_preprocessed = preprocessing_clipped
        before_objects_clipped = objects_clipped
        im, objs, objs_err, f, f_err, preprocessing_clipped, objects_clipped, peak_values, snr = finding_masks(im=im, centre=centre, original_im=original_im, debug_mode=debug, preprocessing_clipped=preprocessing_clipped, objects_clipped=objects_clipped)


        #if before_preprocessed < preprocessing_clipped: #i.e. more objects were clipped
        for i, obj in enumerate(objs):
            objects.append(obj)
            fluxes.append(f[i])
            fluxes_err.append(f_err[i])
            #data.update({"id": obj_i, "obj": obj, "flux":f[i], "flux error": f_err[i]})
            obj_i += 1



        with open("fluxes.json", "w") as flux_file:
            json.dump([float(value) for value in fluxes], flux_file)
            flux_file.close()

        with open("fluxes_err.json", "w") as flux_err_file:
            json.dump([float(value) for value in fluxes_err], flux_err_file)
            flux_err_file.close()

        #print(objs)
        shape_batches.append([obj.tolist() for obj in objs])
        with open("shapes.json", "w") as shape_file:
            json.dump([shape for batch in shape_batches for shape in batch], shape_file)

        shape_err_batches.append([float(err) for err in objs_err])
        with open("shapes_err.json", "w") as shape_err_file:
            json.dump([err for batch in shape_err_batches for err in batch], shape_err_file)
            shape_err_file.close()

        # peak_batches.append([float(peak) for peak in peak_values])
        # with open("peak_values.json", "w") as peak_file:
        #     json.dump([peak for batch in peak_batches for peak in batch], peak_file)
        #     peak_file.close()

        snr_batches.append([float(s) for s in snr])
        with open("SNR.json", "w") as file:
            json.dump([s for batch in snr_batches for s in batch], file)
            file.close()

        centre = find_centre(im=im)
        # plt.imshow(segment)
        # plt.title("Edge object removed from segment")
        # plt.show()
        print(len(fluxes))
        # print(f"no clipped by the proprocessing mask {preprocessing_clipped}")
        # print(f"no clipped by other objects {objects_clipped}")
        if len(fluxes) >= 750: #99
            debug = True
        else:
            debug = False

    


run_photometry()
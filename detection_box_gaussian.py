import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import imageio.v3 as iio
import cv2
import json
from frames import load_mask
from maths import gaussian_2d, gaussian_2d_fit


# Global variables.
mosaic = fits.open('Fits_Data/mosaic.fits')
mosaic_mask = iio.imread('Fits_Data/mask.png')
image = np.ma.array(mosaic[0].data, mask=load_mask(mosaic_mask))
box_size = 6
bg_box_size = 50


# Future considerations:
# Uncertainty quantification.
# Identification of overlapping sources.
# Statistical testing of methods (e.g. Gaussian fit residual).
# Threshold justification.

# Note that all of the following are in (y, x) instead of (x, y).


def find_centre(im):
    '''
    Finds the coordinates of the brightest pixel in an image.

    NOTE: The detection threshold currently is set at the median pixel
    value of the image + 20.

    Args:
        im (arr): The image.

    Returns:
        tuple: The coordinates of the brightest pixel.
    '''
    max_index = np.unravel_index(np.argmax(im), np.shape(im))
    if im[max_index] < (np.median(im) + 20):
        print("All sources found!")
        return None
    return max_index


def edge_box(bounds, dx, dy):
    '''
    For a box which is partially outside the image.

    Args:
        bounds (list): The shape of the image.
        dx (list): [x2, x1], where x2 < x1. x2 is restricted by the
            boundary x=0, and x1 the boundary bounds[1].
        dy (list): [y2, y1], where y2 < y1. y2 is restricted by the
            boundary y=0, and y1 the boundary bounds[0].

    Returns:
        list: The updated coordinates of the box, its height, and its
            width.
    '''
    cs = [0, 0, 0, 0] # [y2, x2, y1, x1].

    # If y2 goes beyond the top of the image.
    if dy[0] < 0:
        cs[0] = 0
    else:
        cs[0] = dy[0]

    # If y1 goes beyond the bottom of the image.
    if dy[1] > bounds[0]:
        cs[2] = bounds[0]
    else:
        cs[2] = dy[1]

    # If x1 goes beyond the right of the image.
    if dx[1] > bounds[1]:
        cs[3] = bounds[1]
    else:
        cs[3] = dx[1]

    # If x2 goes beyond the left of the image.
    if dx[0] < 0:
        cs[1] = 0
    else:
        cs[1] = dx[0]

    h = np.abs(cs[0] - cs[2])
    w = np.abs(cs[1] - cs[3])
    return cs, h, w


def create_box(centre, prev_box, bounds):
    '''
    Creates a new box based on the information of the previous box.

    Args:
        centre (tuple): The coordinates of the centre of the box.
        prev_box (list | None): The information of the previous box. If
            None, no previous boxes exist.
        bounds (list): The shape of the image.

    Returns:
        list: The coordinates of the top left corner of the box, its
            height, and its width.
    '''
    if prev_box is None:
        dx = [centre[1] - box_size, centre[1] + box_size]
        dy = [centre[0] - box_size, centre[0] + box_size]
        if ((dx[0] < 0) or (dx[1] > bounds[1])
            or (dy[0] < 0) or (dy[1] > bounds[0])):
            # (dx[0]<0) means that to the bottom of the centre it goes
            # beyond the image.
            # (dx[1]>bounds[1]) this means that to the top of the
            # centre it goes beyond the image.
            # Similarly for dy.

            # cs is (y2, x2, y1, x1).
            cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy)

            # Starting in the bottom left (i.e. top left i think).
            return [[cs[0], cs[1]], h, w]

        # Starting coords of the top left corner, h, w.
        return [[centre[0] - box_size, centre[1] - box_size],
                2*box_size + 1, 2*box_size + 1]

    h, w = prev_box[1], prev_box[2]
    if h!= w: # i.e. Working with a box on the edge.
        c = [prev_box[0][0], prev_box[0][1]] # The corner.

        # Left, right. Increase by w because corner in top left.
        dx = [c[1] - box_size, c[1] + w + box_size]
        # Down, up. Decrase by h because corner in top left.
        dy = [c[0] - h - box_size, c[0] + box_size]

        cs, h, w = edge_box(bounds=bounds, dx=dx, dy=dy)
        return [[cs[0], cs[1]], h, w]

    return [[prev_box[0][0] - box_size, prev_box[0][1] - box_size],
            h + 2*box_size, w + 2*box_size]


def get_box_coords(box):
    '''
    Finds the coordinates of the corners of the box.

    Args:
        box (list): The box information.

    Returns:
        tuple[arr, arr, arr]: The x-coordinates, the y-coordinates, and
            the combined coordinates.
    '''
    h = box[2]
    w = box[1]

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
    nx, ny = np.shape(box_im)
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
    nx, ny = np.shape(box_im)
    x, y = np.meshgrid(range(nx), range(ny))

    fig = plt.figure()
    subfig = fig.add_subplot(111, projection="3d")
    subfig.plot_surface(x, y, box_im)
    subfig.plot_surface(x, y, gaussian_2d((x, y), *popt), alpha=0.5)
    plt.show()


def get_ellipse_params(popt):
    '''
    Converts the fitted values into the ellipse parameters.

    NOTE: The axes are currently set at 10*std.

    Args:
        popt (arr): The fitted values.

    Returns:
        tuple[arr, arr, float]: The centre, the axes, and the clockwise
            rotation angle.
    '''
    return (popt[2], popt[1]), (10*popt[4], 10*popt[3]), 180/np.pi*popt[5]


def plot_ellipse(box_im, ellipse):
    '''
    Plots the boxed region with the fitted Gaussian distribution.

    Args:
        box_im (arr): The boxed region.
        ellipse (arr): The parameters of the fitted ellipse.
    '''
    center, diameters, angle = ellipse
    fig, ax = plt.subplots()
    ax.imshow(box_im, cmap="gray")
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


def pad_edge_box(box_im, bounds):
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

    x_i = np.arange(0, midpoint_x, 1)
    y_i = np.arange(0, midpoint_y, 1)

    fill = np.average(box_im)

    if (x_i == 0).any() or (x_i >= bounds[1]-1).any():
        # i.e. The object is on the edge top or bottom.
        padded_im = np.zeros((half_shape[0], half_shape[1]*2))
        # print(np.shape(padded_im))
        # print(np.shape(box_im))
        # print(midpoint_x)
        mask = np.zeros((half_shape[0], half_shape[1]*2))
        if (x_i == 0).any() or (y_i == 0).any():
            padded_im[:, midpoint_x:] = box_im
            padded_im[:, :midpoint_x] = fill
            mask[:, midpoint_x:] = 1
        else:
            padded_im[:midpoint_y, :] = box_im
            padded_im[midpoint_y:, :] = fill
            mask[:midpoint_y, :] = 1
    elif (y_i == 0).any() or (y_i >= bounds[0]-1).any():
        # Object on the top or bottom edge.
        padded_im = np.zeros((half_shape[0]*2, half_shape[1]))
        mask = np.zeros((half_shape[0]*2, half_shape[1]))
        if (y_i == 0).any():
            # box_im[midpoint_y:, :] = rb
            # box_im[:midpoint_y, :] = fill
            # mask[midpoint_y:, :] = 1
            padded_im[:, midpoint_x:] = box_im
            padded_im[:, :midpoint_x] = fill
            mask[:, midpoint_x:] = 1
        else:
            padded_im[:midpoint_y, :] = box_im
            padded_im[midpoint_y:, :] = fill
            mask[midpoint_y:, :] = 1
    else:
        print("idk man")

    return padded_im, x_i, y_i, mask


def get_binary_mask(box_im, ellipse):
    '''
    Computes the binary mask.

    Args:
        box_im (arr): The boxed region.
        ellipse (arr): The parameters of the fitted ellipse.

    Returns:
        arr: The binary mask.
    '''
    object_binary_mask = np.zeros(np.shape(box_im), dtype=np.uint8)
    center = tuple(np.round(ellipse[0]).astype(int))
    axes = tuple(np.round(np.asarray(ellipse[1]) / 2).astype(int))

    object_binary_mask = cv2.ellipse(
        object_binary_mask, center, axes, ellipse[2], 0, 360,
        color=(255, 0, 0), thickness=-1
    )

    binary_mask = object_binary_mask/np.max(object_binary_mask)
    return binary_mask


def get_new_image(xi, yi, mask, box, im, plot=False):
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
    _, _, bc = get_box_coords(box)

    # Refined box.
    rb = [bc[0][1]+xi[0], bc[0][1]+xi[-1], bc[0][0]+yi[0], bc[0][0]+yi[-1]]

    new_image = im
    new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1] = np.ma.array(
        new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1], mask=mask
    )

    if plot:
        plt.imshow(new_image)
        plt.xlim(rb[0], rb[1])
        plt.ylim(rb[2], rb[3])
        plt.title("Area Removed by Mask")
        plt.show()

    return new_image


def get_pixel_threshold(im, centre):
    '''
    Computes the threshold on the pixel value at the edge of the box.

    NOTE: The threshold is currently set at the median + 20.

    Args:
        im (arr): The image.
        centre (tuple): The coordinates of the brightest pixel.

    Returns:
        float: The pixel value threshold.
    '''
    box = [[centre[0] - bg_box_size, centre[1] - bg_box_size],
           2*bg_box_size + 1, 2*bg_box_size + 1]
    box_im = get_box_image(im=im, box=box)
    return np.median(box_im) + 20


def finding_masks(im, centre):
    '''
    Masks a source.

    Args:
        im (arr): The image.
        centre (tuple): The coordinates of the brightest pixel.

    Returns:
        tuple[arr, arr, arr]: The masked image, the parameters of the
            fitted ellipse, and the flux of the source.
    '''
    bounds = np.shape(im)
    box = create_box(centre=centre, prev_box=None, bounds=bounds)
    box_im = get_box_image(im=im, box=box)
    box_im_edge = np.concatenate(
        (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
    )
    threshold = get_pixel_threshold(im=im, centre=centre)

    while (box_im_edge > threshold).sum() > (len(box_im_edge) / 4):
        # i.e. If the number of pixels on the edge that are above the
        # threshold is larger than a quarter.
        box = create_box(centre=centre, prev_box=box, bounds=bounds)
        box_im = get_box_image(im=im, box=box)
        box_im_edge = np.concatenate(
            (box_im[:, 0], box_im[:, -1], box_im[0, 1:-1], box_im[-1, 1:-1])
        )
        box_in_sky(im=im, box=box, centre=centre)

    box_in_sky(im=im, box=box, centre=centre)

    if box[1] != box[2]:
        box_im, xi, yi, _ = pad_edge_box(box_im=box_im, bounds=bounds)

    while True:
        try:
            obj = fit_gaussian(box_im=box_im)
            plot_gaussian(box_im=box_im, popt=obj[0])

            ellipse = get_ellipse_params(popt=obj[0])
            plot_ellipse(box_im=box_im, ellipse=ellipse)

            bm = get_binary_mask(box_im=box_im, ellipse=ellipse)
            flux = np.sum(box_im * bm)
            bm_r = 1 - bm
            bg_flux = np.mean(box_im * bm_r)
            flux = flux - bg_flux * bm.sum()
            break

        except RuntimeError:
            bm = np.where(box_im > np.median(box_im),
                          np.ones_like(box_im), np.zeros_like(box_im))
            obj = np.nan
            flux = np.nan
            break

    xi = np.arange(0, np.shape(box_im)[1], 1)
    yi = np.arange(0, np.shape(box_im)[0], 1)
    masked_image = get_new_image(xi=xi, yi=yi, mask=bm, box=box, im=im)

    return masked_image, obj, flux


def main():
    '''
    Runs the photometry.
    '''
    im = image[2560:4601, 1549:2500]
    # im = image
    # segment = segment[0:15, 540:590]  #example of an edge object for the segment

    # #segment = np.transpose(segment)
    # #segment = segment[::-1, ::-1]

    centre = find_centre(im=im)

    plt.imshow(im)
    plt.title("Original segment")
    plt.show()

    objects = []
    fluxes = []
    with open("fluxes.json", "w") as flux_file:
        json.dump(fluxes, flux_file)

    while centre is not None:
        im, obj, flux = finding_masks(im=im, centre=centre)
        objects.append(obj)
        fluxes.append(flux)
        with open("fluxes.json", "w") as flux_file:
            json.dump([float(value) for value in fluxes], flux_file)
        centre = find_centre(im=im)
        # plt.imshow(segment)
        # plt.title("Edge object removed from segment")
        # plt.show()


main()

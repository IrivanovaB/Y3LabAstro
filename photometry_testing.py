'''
A module for testing the methods in photometry.
'''

import numpy as np
import matplotlib.pyplot as plt
from images import load_image, fit_pixel_histogram
from photometry import (get_box_image, find_centre, get_local_background,
                        finding_masks, get_ellipse_params)


# Global variables.
image = load_image()
image_shape = np.shape(image)
bg_threshold = 11
global_bg = 3420


def generate_random_box(box_size):
    '''
    Generates a random boxed region of a given size.

    Args:
        box_size (list): The dimensions of the box.

    Returns:
        list: The box information.
    '''
    y = np.random.randint(image_shape[0]-box_size[0])
    x = np.random.randint(image_shape[1]-box_size[1])
    return [[y, x], *box_size]


def background_box(sample=10000, box_size=[101, 101]):
    '''
    Computes mean standard deviation of the local background mean and
    the z-score of the median pixel value of a boxed region.

    Args:
        sample (int): The number of samples. Defaults to 10000.
        box_size (list): The shape of the box. Defaults to [101, 101].
    '''
    box_area = box_size[0]*box_size[1]
    std = []
    z_score = []
    i = 0
    while i < sample:
        try:
            box = generate_random_box(box_size=box_size)
            box_im = get_box_image(im=image, box=box)
            median = np.median(box_im.compressed())
            p0 = [box_area/5, median, 10, 0, 0]
            popt, _ = fit_pixel_histogram(im=box_im, p0=p0)
            std.append(popt[2])
            z_score.append((median - popt[1]) / popt[2])
            i += 1
        except Exception:
            continue

    plt.hist(z_score, bins=np.arange(-0.5, 0.51, 0.01))
    plt.xlabel('Median offset (σ)')
    plt.ylabel('Count (per 0.01σ)')
    plt.tight_layout()
    # plt.savefig('figures/local_background_median_offset', dpi=300)
    plt.show()

    std_err = np.std(std)
    std = np.mean(std)
    z_score = np.abs(np.array(z_score))
    z_score_01 = (z_score < 0.1).sum() / sample
    z_score_10 = (z_score < 1.).sum() / sample
    z_score_01_err = np.sqrt(z_score_01*(1-z_score_01) / sample)
    z_score_10_err = np.sqrt(z_score_10*(1-z_score_10) / sample)

    print('STATISTICS')
    print(f'Local background fluctuation = {std:.4f} +/- {std_err:.4f}')
    print(f'P(median offset < 0.1σ) = {z_score_01:.4f} +/- {z_score_01_err:.4f}')
    print(f'P(median offset < 1.0σ) = {z_score_10:.4f} +/- {z_score_10_err:.4f}')
    print(f'Samples = {sample}')
    print(f'Box size = {box_size}')


def get_ellipse_axes(im, ellipse):
    '''
    Locates the pixels that lie on the semi-major and semi-minor axes
    of the ellipse.

    Args:
        im (arr): The image.
        ellipse (arr): The ellipse parameters.

    Returns:
        arr: The pixels on the axes of the ellipse.
    '''
    shape = np.shape(im)
    centre = ellipse[0]
    theta = np.pi/180 * ellipse[2]
    l = np.arange(-200, 200, 0.1)
    x_axis1 = np.rint(centre[0] + l * np.cos(theta)).astype('int')
    y_axis1 = np.rint(centre[1] + l * np.sin(theta)).astype('int')
    x_axis2 = np.rint(centre[0] - l * np.sin(theta)).astype('int')
    y_axis2 = np.rint(centre[1] + l * np.cos(theta)).astype('int')
    def within_image(x, y):
        xy = np.column_stack((x, y))
        mask = (x >= 0) & (x < shape[1]) & (y >= 0) & (y < shape[0])
        return xy[mask]
    axis1 = within_image(x_axis1, y_axis1)
    axis2 = within_image(x_axis2, y_axis2)
    return im[axis1[:, 1], axis1[:, 0]], im[axis2[:, 1], axis2[:, 0]]


def detection_ellipse(sample=100, box_size=[200, 200]):
    '''
    Computes the number of standard deviations from the centre of the
    source at which the fitted distribution is within one pixel of the
    local background mean.

    Args:
        sample (int): The number of samples. Defaults to 100.
        box_size (list): The shape of the box. Defaults to [101, 101].
    '''
    i = 0
    std = []
    while i < sample:
        box = generate_random_box(box_size=box_size)
        box_im = get_box_image(im=image, box=box)
        if len(box_im.compressed()) == 0:
            continue
        max_index = find_centre(im=box_im)
        max_value = box_im[max_index]
        if np.ma.is_masked(max_value) or not np.isfinite(max_value):
            continue
        max_index_shifted = [max_index[0]+box[0][0], max_index[1]+box[0][1]]
        try:
            _, popt, _ = finding_masks(im=image, centre=max_index_shifted)
        except Exception:
            continue
        popt = popt[0]
        if popt[0] < bg_threshold:
            continue
        ellipse = get_ellipse_params(popt=popt, size=1)
        std1, std2 = ellipse[1]
        axis1, axis2 = get_ellipse_axes(im=image, ellipse=ellipse)
        if (len(axis1) != 4000) or (len(axis2) != 4000):
            continue
        local_bg = get_local_background(im=image, centre=max_index_shifted)
        l = np.arange(-200, 200, 0.1)
        axis1_mean = np.mean(axis1.reshape(-1, 10), axis=1)
        axis2_mean = np.mean(axis2.reshape(-1, 10), axis=1)
        l_mean = np.mean(l.reshape(-1, 10), axis=1)
        axis1_bg = l_mean[axis1_mean <= local_bg]
        axis2_bg = l_mean[axis2_mean <= local_bg]
        axis1_bg = [np.max(axis1_bg[axis1_bg < 0]),
                    np.min(axis1_bg[axis1_bg > 0])]
        axis2_bg = [np.max(axis2_bg[axis2_bg < 0]),
                    np.min(axis2_bg[axis2_bg > 0])]
        axis1_bg = np.abs(axis1_bg / std1)
        axis2_bg = np.abs(axis2_bg / std2)
        std.append([*axis1_bg, *axis2_bg])
        # plt.plot(l, axis1, '.', ms=1)
        # plt.plot(l, axis2, '.', ms=1)
        # plt.xlabel('Distance from source')
        # plt.ylabel('Pixel value')
        # # plt.savefig('figures/detection_ellipse_axes_pixel', dpi=300)
        # plt.show()
        i += 1
    std = np.array(std).flatten()

    plt.hist(std, bins=np.arange(0, np.max(std)+0.5, 0.5))
    plt.xlabel('Source size (σ)')
    plt.ylabel('Count (per 0.5σ)')
    plt.tight_layout()
    # plt.savefig('figures/source_size', dpi=300)
    plt.show()

    std_10 = (std < 10).sum() / len(std)
    std_15 = (std < 15).sum() / len(std)
    std_10_err = np.sqrt(std_10*(1-std_10) / sample)
    std_15_err = np.sqrt(std_15*(1-std_15) / sample)
    std_err = np.std(std)
    std = np.mean(std)

    print('STATISTICS')
    print(f'Source size = {std:.4f} +/- {std_err:.4f} σ')
    print(f'P(size < 10σ) = {std_10:.4f} +/- {std_10_err:.4f}')
    print(f'P(size < 15σ) = {std_15:.4f} +/- {std_15_err:.4f}')
    print(f'Samples = {sample}')
    print(f'Box size = {box_size}')

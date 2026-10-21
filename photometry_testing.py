'''
A module for testing the methods in photometry.
'''

import numpy as np
import matplotlib.pyplot as plt
from images import load_image, fit_pixel_histogram
from detection_box_gaussian import get_box_image, find_centre, get_local_background, fit_gaussian, plot_gaussian


# Global variables.
image = load_image()
image_shape = np.shape(image)


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
            im = get_box_image(im=image, box=box)
            median = np.median(im.compressed())
            p0 = [box_area/5, median, 10, 0, 0]
            popt, _ = fit_pixel_histogram(im=im, p0=p0)
            std.append(popt[2])
            z_score.append((median - popt[1]) / popt[2])
            i += 1
        except Exception:
            continue

    plt.hist(z_score, bins=np.arange(-0.5, 0.51, 0.01), density=True)
    plt.xlabel('z-score')
    plt.tight_layout()
    # plt.savefig('figures/background_box_median_z_score', dpi=300)
    plt.show()

    std_err = np.std(std)
    std = np.mean(std)
    z_score = np.abs(np.array(z_score))
    z_score_01 = (z_score < 0.1).sum() / sample
    z_score_10 = (z_score < 1.).sum() / sample
    z_score = np.mean(z_score)
    print('STATISTICS')
    print(f'std of local background mean = {std:.4f} +/- {std_err:.4f}')
    print(f'z-score of median = {z_score:.4f}')
    print(f'P(z-score < 0.1) = {z_score_01:.4f}')
    print(f'P(z-score < 1.0) = {z_score_10:.4f}')
    print(f'Samples = {sample}')
    print(f'Box size = {box_size}')


def get_ellipse_axes():
    '''
    Locates the pixels that lie on the semi-major and semi-minor axes
    of the ellipse.

    Args:

    Returns:

    '''

def detection_ellipse(sample=10, box_size=[101, 101]):
    '''
    Computes the number of standard deviations from the centre of the
    source at which the fitted distribution is within one pixel of the
    local background mean.

    Args:
        sample (int): The number of samples. Defaults to 10000.
        box_size (list): The shape of the box. Defaults to [101, 101].
    '''
    i = 0
    std_no = []
    while i < sample:
        box = generate_random_box(box_size=box_size)
        im = get_box_image(im=image, box=box)
        if len(im.compressed()) == 0:
            continue
        max_index = find_centre(im=im)
        max_value = im[max_index]
        if np.ma.is_masked(max_value) or not np.isfinite(max_value):
            continue
        max_index_shifted = [max_index[0]+box[0][0], max_index[1]+box[0][1]]
        local_bg = get_local_background(im=image, centre=max_index_shifted)
        std = np.sqrt(2 * np.log(max_value - local_bg))
        popt, pcov = fit_gaussian(box_im=im)

        if not np.isfinite(std):
            continue
        std_no.append(std)
        i += 1

    plt.hist(std_no, bins=np.arange(0, 5, 0.1), density=True)
    plt.xlabel('Standard deviation')
    plt.tight_layout()
    # plt.savefig('figures/detection_ellipse', dpi=300)
    plt.show()

    std_no_err = np.std(std_no)
    std_no_mean = np.mean(std_no)
    print('STATISTICS')
    print(f'Number of std = {std_no_mean:.4f} +/- {std_no_err:.4f}')
    print(f'Samples = {sample}')
    print(f'Box size = {box_size}')

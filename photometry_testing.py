'''
A module for testing the methods in photometry.
'''

import numpy as np
import matplotlib.pyplot as plt
from images import load_image, fit_pixel_histogram
from photometry import get_box_image


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


def background_box(sample, box_size):
    '''
    Computes mean standard deviation of the local background mean and
    the z-score of the median pixel value of a boxed region.

    Args:
        sample (int): The number of samples.
        box_size (list): The shape of the box.

    Returns:
        tuple[float, float, float, float, float]: The mean standard
            deviation of the local background mean, its uncertainty,
            the mean absolute z-score of the median, the probability of
            it being below 0.1, and that below 1.0.
    '''
    box_area = box_size[0]*box_size[1]
    boxes = [generate_random_box(box_size=box_size) for _ in range(sample)]
    ims = [get_box_image(im=image, box=box) for box in boxes]
    std = []
    z_score = []
    for im in ims:
        median = np.median(im.compressed())
        p0 = [box_area/5, median, 10, 0, 0]
        popt, _ = fit_pixel_histogram(im=im, p0=p0)
        std.append(popt[2])
        z_score.append((median - popt[1]) / popt[2])
    # plt.hist(z_score, bins=np.arange(-0.4, 0.41, 0.01), density=True)
    # plt.xlabel('z-score')
    # plt.tight_layout()
    # # plt.savefig('figures/background_box_median_z_score', dpi=300)
    # plt.show()
    std_err = np.std(std)
    std = np.mean(std)
    z_score = np.abs(np.array(z_score))
    z_score_01 = (z_score < 0.1).sum() / sample
    z_score_10 = (z_score < 1.).sum() / sample
    z_score = np.mean(z_score)
    # print('STATISTICS')
    # print(f'Standard deviation of local background mean = {std:.4f} +/- {std_err:.4f}')
    # print(f'z-score of median = {z_score:.4f}')
    # print(f'P(z-score < 0.1) = {z_score_01:.4f}')
    # print(f'P(z-score < 1.0) = {z_score_10:.4f}')
    return std, std_err, z_score, z_score_01, z_score_10


def backgroud_box_iterated(iteration=100, sample=100, box_size=[101, 101]):
    '''
    Computes z-score of the median pixel value of a boxed region. The
    local background mean is taken to be the peak of the fitted
    Gaussian distribution.

    Args:
        iteration (int): The number of iterations. Defaults to 100.
        sample (int): The number of samples. Defaults to 100.
        box_size (list): The shape of the box. Defaults to [101, 101].

    Returns:
        tuple[float, float, float, float, float]: The mean standard
            deviation of the local background mean, its uncertainty,
            the mean absolute z-score of the median, the probability of
            it being below 0.1, and that below 1.0.
    '''
    i = 0
    std = []
    std_err = []
    z_score = []
    z_score_01 = []
    z_score_10 = []
    while i < iteration:
        try:
            s, s_err, z, z_01, z_10 = background_box(sample=sample,
                                                     box_size=box_size)
            std.append(s)
            std_err.append(s_err)
            z_score.append(z)
            z_score_01.append(z_01)
            z_score_10.append(z_10)
            i += 1
        except Exception:
            continue
    std = np.mean(std)
    std_err = np.sqrt(np.sum(np.array(std_err)**2)) / iteration
    print('OVERALL STATISTICS')
    print(f'std of local background mean = {std:.4f} +/- {std_err:.4f}')
    print(f'z-score of median = {np.mean(z_score):.4f}')
    print(f'P(z-score < 0.1) = {np.mean(z_score_01):.4f}')
    print(f'P(z-score < 1.0) = {np.mean(z_score_10):.4f}')
    print(f'Iterations run = {iteration}')
    print(f'Samples per iteration = {sample}')
    print(f'Box size = {box_size}')


def detection_ellipse():
    '''
    Computes the number of standard deviations from the centre of the
    source at which the fitted distribution is within one standard
    deviation of the local background mean.
    '''



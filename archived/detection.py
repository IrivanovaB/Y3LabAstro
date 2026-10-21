import numpy as np
from astropy.io import fits 
from frames import Frame, Image, Mask
from scipy import optimize, ndimage
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import cv2

#Read in our analysis image
hdu = fits.open(r"Fits_Data/mosaic.fits")
image = hdu[0].data

# img_normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
# image = np.uint8(img_normalized)

image = image[2560:4601, 1549:2500]


# # #image = cv2.GaussianBlur(image, (5,5), 1.5)
# # circles = cv2.HoughCircles(
# #     image, cv2.HOUGH_GRADIENT,
# #     dp=1,
# #     minDist=7,
# #     param1=30,
# #     param2=20,
# #     minRadius=6, maxRadius=200
# # )


# features = cv2.SIFT_create()

# keypoints = features.detect(image, None)


#max = np.argwhere(image>=(np.average(image)+5*np.std(image)))
max_index = np.argwhere(image==np.max(image))

point = max_index[0]
# print(point) #[1198  586]

#start coord (y, x), h, w; first going to try circles of radius 7 #so that it is centred 
#currently going to assume that there is nothing on the edges # if (np.abs(point[1]-3) >= 0)

box_0 = [[point[0]-3, point[1]-3], 7, 7]
# print(box_0) # [[np.int64(1195), np.int64(583)], 7, 7]

def get_box_coords(box):
    h = box[1]
    w = box[2]

    box_x = [box[0][1], box[0][1]+w-1, box[0][1]+w-1, box[0][1], box[0][1]]
    box_y = [box[0][0], box[0][0], box[0][0]+h-1, box[0][0]+h-1, box[0][0]]

    box_coords = []
    for i in range(5):
        box_coords.append([box_y[i], box_x[i]])

    return box_x, box_y, box_coords


def plot_box(centre, box):
    plt.plot(centre[1], centre[0], "ro")

    box_x, box_y, __ = get_box_coords(box)

    plt.plot(box_x, box_y, label="box")
    plt.legend()
    plt.show()


def fit_ellipse(im, threshold): #this function was vibe coded with copilot to be improved/ammended later - just currently need to get something to work 
    """Fit an ellipse to the largest connected region at or above threshold.

    Returns ``((center_x, center_y), (diameter_1, diameter_2), angle_degrees)``,
    with coordinates relative to ``im``.
    """
    im = np.asarray(im)
    if im.ndim != 2:
        raise ValueError("im must be a two-dimensional image")

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


def plot_ellipse(im, ellipse):
    center, diameters, angle = ellipse
    fig, ax = plt.subplots()
    ax.imshow(im, cmap="gray")
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


box_x, box_y, box_c = get_box_coords(box_0)

box_image = image[box_c[0][0]:(box_c[2][0]+1), box_c[0][1]:(box_c[2][1]+1)]

def first_box_in_sky(bx, by, centre, b_image):
    fig, (axs1, axs2) = plt.subplots(1, 2)
    fig.suptitle("Box in the Sky")
    axs1.imshow(image)
    axs1.plot(bx, by, color="red", alpha=0.5, label="box")
    axs1.plot(centre[1], centre[0], "rx", label="centre")
    axs1.legend()
    axs1.set_xlim((700, 500))
    axs1.set_ylim((1300, 1100))
    axs2.imshow(b_image)
    plt.show()

#first_box_in_sky(box_x, box_y, point, box_image)

def get_box_image(bc):
    return image[bc[0][0]:(bc[2][0]+1), bc[0][1]:(bc[2][1]+1)]


def box_stats(b_image):
    print(f"The mean is: {np.average(b_image)}")
    print(f"The median is: {np.median(b_image)}")
    print(f"The stdev is: {np.std(b_image)}")
    print("\n")
    return np.average(b_image), np.median(b_image), np.std(b_image)


def axis_stats(im):
    x_means = np.mean(im, axis=0)
    y_means = np.mean(im, axis=1)
    x_medians = np.median(im, axis=0)
    y_medians = np.median(im, axis=1)
    x_stds = np.std(im, axis=0)
    y_stds = np.std(im, axis=1)

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


def draw_ellipse(im, ellipse):
    #needs to be same image used to find the ellipse
    plt.imshow(im)

    """
    equation for general ellipse and rotated ellipse
    https://en.wikipedia.org/wiki/Ellipse#General_ellipse

    X = (x - x_0) cos(theta) + (y - y_0) sin(theta)
    Y = - (x - x_0) sin(theta) + (y - y_0) cos(theta)

    (X/a)**2 + (Y/b)**2 = 1


    """




#a0, m0, s0 = box_stats(box_image)


#now we will make a 21x21 box
box_1 = [[box_0[0][0]-7, box_0[0][1]-7], 21, 21]

b1x, b1y, b1c = get_box_coords(box_1)
box_image_1 = get_box_image(b1c)
#first_box_in_sky(b1x, b1y, point, box_image_1)
#a1, m1, s1 = box_stats(box_image_1)




box_2 = [[box_1[0][0]-7, box_1[0][1]-7], 35, 35]
b2x, b2y, b2c = get_box_coords(box_2)
box_image_2 = get_box_image(b2c)
#first_box_in_sky(b2x, b2y, point, box_image_2)
#a2, m2, s2 = box_stats(box_image_2)

# axis_stats(box_image_2)

#condition to make a larger box?

box_3 = [[box_2[0][0]-7, box_2[0][1]-7], 49, 49]
b3x, b3y, b3c = get_box_coords(box_3)
box_image_3 = get_box_image(b3c)
#first_box_in_sky(b3x, b3y, point, box_image_3)
#a3, m3, s3 = box_stats(box_image_3)

#axis_stats(box_image_3)


#actually box 7
box_4 = [[box_3[0][0]-21, box_3[0][1]-21], 91, 91]
b4x, b4y, b4c = get_box_coords(box_4)
box_image_4 = get_box_image(b4c)
#first_box_in_sky(b4x, b4y, point, box_image_4) 
a4, m4, s4 = box_stats(box_image_4)

#axis_stats(box_image_4)

#IMPORTANT: INSERT CONDITION

x_means = np.mean(box_image_4, axis=0)
y_means = np.mean(box_image_4, axis=1)

x_indices = np.where(x_means>=(a4)) #currenty completely arbitrary
y_indices = np.where(y_means>=(a4))

refined_box = box_image_4[np.ix_(y_indices[0], x_indices[0])]

# plt.imshow(refined_box)
# plt.title("First attempt at a refined box")
# plt.show()

ellipse = fit_ellipse(refined_box, m4)

# plot_ellipse(refined_box, ellipse)


object_binary_mask = np.zeros(np.shape(refined_box), dtype=np.uint8)
center = tuple(np.round(ellipse[0]).astype(int))
axes = tuple(np.round(np.asarray(ellipse[1]) / 2).astype(int))
object_binary_mask = cv2.ellipse(
    object_binary_mask, center, axes, ellipse[2], 0, 360, color=(255, 0, 0), thickness=-1
)
# plt.imshow(refined_box, cmap="gray")
# plt.imshow(object_binary_mask, alpha=0.3, cmap="viridis")
# plt.title("Binary map of first ellipse fit")
# plt.show()


binary_mask = object_binary_mask/np.max(object_binary_mask)
binary_mask = 1 - binary_mask 

relative_mask = np.ma.array(refined_box, mask=binary_mask)
relative_mask = relative_mask/np.max(relative_mask)

# plt.imshow(relative_mask, cmap="viridis")
# plt.title("Mask Applied")
# plt.show()

#now we need to set this chunk of the original image to 0 so that we can look for the next object

rb = [b4c[0][1]+x_indices[0][0], b4c[0][1]+x_indices[0][-1], b4c[0][0]+y_indices[0][0], b4c[0][0]+y_indices[0][-1]]
new_image = image
relative_mask = 1-relative_mask
new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1] = new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1]*relative_mask
plt.imshow(new_image)
plt.xlim((700, 500))
plt.ylim((1300, 1100))
plt.title("Area Removed: Relative Mask")
plt.show()



"""
OKAY IRIS HELLO

SO in effect we will take a set of points
distinguish a way to make that list smaller --> thinking only accept points with the most extreme gradients of the indices

with a smaller list 
plot an arbitary ellipse for each of them (creating a mask for each)
create an ellipse twice the size -> binomial search if that is then too big; if it is too small (like relative values) then expand it again
create a relative mask as well based off of values
combine masks to a master masks and then exclude them from the next search  

"""
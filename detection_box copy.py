import numpy as np
from astropy.io import fits 
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import cv2

#global variables
hdu = fits.open(r"Fits_Data/mosaic.fits")
image = hdu[0].data


def find_centre(box_0):
    max_index = np.argwhere(box_0==np.max(box_0))

    if box_0[max_index[0][0], max_index[0][1]] == 0.1*np.median(box_0): #basically have found all the bright objects
        return None
    else: 
        return max_index[0]

def create_box(centre, prev_box, bounds):
    """
    Create a new bounding box based on the previous box info

    bounds: the shape of the image or segment (y, x)
    """

    if prev_box == None:
        dx = [centre[1] - 3, centre[1] + 3]
        dy = [centre[0] - 3, centre[0] + 3]
        if (dx[0] < 0) or (dx[1] > bounds[1]) or (dy[0] < 0) or (dy[1] > bounds[0]):
            #(dx[0]<0) this means that to the bottom of the centre it goes beyond the image
            #(dx[1]>bounds[1]) this means that to the top of the centre it goes beyond the image
            #similarly for dy
            cs = [0., 0., 0., 0.] #coords (y up, y down, x right, x left)
            if (dy[1] > bounds[0]):
                cs[0] = bounds[0]
            else:
                cs[0] = dy[1] + 3

            if dy[0] < 0:
                cs[1] = 0
            else:
                cs[1] = dy[0] -3

            if dx[0] > bounds[1]:
                cs[2] = bounds[1]
            else:
                cs[2] = dx[1] + 3
            
            if dx[0] < 0:
                cs[3] = 0
            else:
                cs[3] = dx[1] - 3

            h = np.abs(cs[0] - cs[1])
            w = np.abs(cs[3] - cs[2])

            return [[cs[1], cs[3]], h, w]    #starting in the bottom left (i.e. top left i think) 
              
        else:
            return [[centre[0]-3, centre[1]-3], 7, 7] #starting coords of the top left corner, h, w
        """
        this works
        """
    else:
        h,w = prev_box[1], prev_box[2]
        if h!= w: #i.e. working with a box on the edge 
            c = [prev_box[0][0], prev_box[0][1]] #the corner

            dx = [c[1] - 7, c[1] + 7] #left, right
            dy = [c[0] - 7, c[0] + 7] #down, up

            #return a new box

        else:
            return [[prev_box[0][0]-7, prev_box[0][1]-7], h+14, w+14]


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
    """
    need to include a way to plot the image
    """
    plt.plot(centre[1], centre[0], "ro")

    box_x, box_y, __ = get_box_coords(box)

    plt.plot(box_x, box_y, label="box")
    plt.legend()
    plt.show()

def get_box_image(segment, box):
    bx, by, bc = get_box_coords(box)

    if (np.array(bc) < 0).any(): #if the object is on the edge 
        xi = np.arange(bc[0][1], bc[1][1], 1)
        yi = np.arange(bc[0][0], bc[2][0], 1)
        pad_x_i = np.where(xi < 0)
        keep_x_i = np.where(xi>=0)[0]
        pad_y_i = np.where(yi < 0)
        keep_y_i = np.where(yi>=0)[0]

        im = np.zeros((len(yi), len(xi)))
        if len(pad_x_i) > 0:
            im[pad_x_i] = 0
        if len(pad_y_i) > 0:
            im[pad_y_i] = 0
        im[keep_y_i[0]:keep_y_i[-1]+1, keep_x_i[0]:keep_x_i[-1]+1] = segment[keep_y_i[0]:keep_y_i[-1]+1, keep_x_i[0]:keep_x_i[-1]+1]
        # plt.imshow(im, cmap="gray")
        # plt.show()
        return im, True
    else: 
        return segment[bc[0][0]:(bc[2][0]+1), bc[0][1]:(bc[2][1]+1)], False

def box_in_sky(segment, box, centre):
    bx, by, bc = get_box_coords(box)
    b_image, __ = get_box_image(segment, box)

    fig, (axs1, axs2) = plt.subplots(1, 2)
    fig.suptitle("Box in the Sky")

    axs1.imshow(segment)
    axs1.plot(bx, by, color="red", alpha=0.5, label="box")
    axs1.plot(centre[1], centre[0], "rx", label="centre")
    axs1.legend()

    axs1.set_xlim((centre[1]+250, centre[1]-250))
    axs1.set_ylim((centre[0]+250, centre[0]-250))
    axs2.imshow(b_image)
    plt.show()

def box_stats(b_image, verbose=False):
    if verbose: 
        print(f"The mean is: {np.average(b_image)}")
        print(f"The median is: {np.median(b_image)}")
        print(f"The stdev is: {np.std(b_image)}")
        print("\n")
    return np.average(b_image), np.median(b_image), np.std(b_image)

def axis_stats(im, plot=False):
    x_means = np.mean(im, axis=0)
    y_means = np.mean(im, axis=1)
    x_medians = np.median(im, axis=0)
    y_medians = np.median(im, axis=1)
    x_stds = np.std(im, axis=0)
    y_stds = np.std(im, axis=1)

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


def fit_ellipse(im, threshold): #this function was vibe coded with copilot to be improved/ammended later - just currently need to get something to work 
    """Fit an ellipse to the largest connected region at or above threshold.

    Returns ``((center_x, center_y), (diameter_1, diameter_2), angle_degrees)``,
    with coordinates relative to ``im``.
    """
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

def refine_box(box, a):
    """
    box needs to be the box image itself
    """
    x_means = np.mean(box, axis=0)
    y_means = np.mean(box, axis=1)

    x_i = np.array(np.where(x_means>=(a))) #currenty completely arbitrary
    y_i = np.array(np.where(y_means>=(a)))

    x_i = x_i[0]
    y_i = y_i[0]

    #return box[np.ix_(y_indices[0], x_indices[0])], x_indices, y_indices
    return box[y_i[0]:y_i[-1]+1, x_i[0]:x_i[-1]+1], x_i, y_i

def get_binary_mask(box, ellipse):
    """
    where box is the refined box
    ellipse is the fitted ellipse
    """
    object_binary_mask = np.zeros(np.shape(box), dtype=np.uint8)
    center = tuple(np.round(ellipse[0]).astype(int))
    axes = tuple(np.round(np.asarray(ellipse[1]) / 2).astype(int))

    object_binary_mask = cv2.ellipse(
        object_binary_mask, center, axes, ellipse[2], 0, 360, color=(255, 0, 0), thickness=-1)
    
    binary_mask = object_binary_mask/np.max(object_binary_mask)
    return 1 - binary_mask 

def get_relative_mask(box, binary_mask):
    """
    where box is the refined box 
    """
    relative_mask = np.ma.array(box, mask=binary_mask)
    return 1- relative_mask/np.max(relative_mask) #normalised 

def get_masks(box, ellipse):
    bm = get_binary_mask(box, ellipse)
    rm = get_relative_mask(box, bm)
    return bm, rm


def plot_mask(im, mask):
    plt.imshow(im, cmap="gray")
    plt.imshow(mask, cmap="viridis", alpha=0.5)
    plt.title("Mask?")
    plt.show()

def get_new_image(xi, yi, mask, box, segment):
    bx, by, bc = get_box_coords(box)

    
    new_image = segment
    #refined box
    rb = [bc[0][1]+xi[0], bc[0][1]+xi[-1], bc[0][0]+yi[0], bc[0][0]+yi[-1]]
    new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1] = new_image[rb[2]:rb[3]+1, rb[0]:rb[1]+1]*mask

    return new_image

def plot_new_image(xi, yi, mask, original_box, segment, plot=False):
    new_image = get_new_image(xi, yi, mask, original_box, segment)

    if plot:
        plt.imshow(new_image)
        plt.xlim((700, 500))
        plt.ylim((1300, 1100))
        plt.title("Area Removed by Mask")
        plt.show()

    return new_image

def main2(): #keeping for historic reasons
    segment = image[2560:4601, 1549:2500] 

    point = find_centre(segment)
    box_0 = create_box(point, prev_box=None)
    box_1 = create_box(point, prev_box=box_0)
    box_2 = create_box(point, prev_box=box_1)
    box_3 = create_box(point, prev_box=box_2)
    box_4 = create_box(point, prev_box=box_3)
    box_5 = create_box(point, box_4)
    box_6 = create_box(point, box_5)
    box_7 = create_box(point, box_6)
    box_8 = create_box(point, box_7)
    box_n = create_box(point, box_8)

    box_in_sky(segment, box_n, point)

    b_image = get_box_image(segment, box_n)
    a, m, s = box_stats(b_image)
    refined_box, xi, yi = refine_box(b_image, a)

    xmu, ymu, xmed, ymed = axis_stats(b_image)
    xmed_s = np.std(xmed)
    ymed_s = np.std(ymed)


    obj = fit_ellipse(refined_box, m)
    plot_ellipse(refined_box, obj)

    bm, rm = get_masks(refined_box, obj)
    bm = get_binary_mask(refined_box, obj)


    plot_new_image(xi, yi, rm, box_n, segment)

    #arbitrary beginning threshold: the median of the edges needs to fall within 10% of the median of the overall box image


def finding_masks(segment, point, counter):
    # x_distance = point[1] - 3
    # y_distance = point[0] - 3
    # if (x_distance < 0) or (y_distance < 0):
    #     #basically if the initial box of the point falls on the edge
    #     masked_image = segment
    #     masked_image[point[0], point[1]] = 0
    #     return masked_image, 0, 0

    box_0 = create_box(point, prev_box=None)

    box_1 = create_box(point, box_0)
    b1_image, padded = get_box_image(segment, box_1)
    if padded:
        plt.title("First padded box")
        plt.imshow(b1_image)
        plt.show()
        
    #a1, m1, s1 = box_stats(b1_image) #other threshold ideas 
    xmus, ymus, xmeds, ymeds = axis_stats(b1_image)

    if (len(ymus) == 0) or (len(xmus) == 0) or (len(xmeds) == 0) or (len(ymeds) == 0):
        print(xmus)
        print(ymus)
        print(xmeds)
        print(ymeds)
        print("\n")
        print(point)
        print(box_0)
        print(box_1)
        # plt.imshow(get_box_image(segment, box_0))
        # plt.show()
        # plt.imshow(b1_image)
        # plt.show()

    prev_box = box_1

    # b0_image = get_box_image(segment, box_0)
    # xmus, ymus, xmeds, ymeds = axis_stats(b0_image)

    box_n = box_1
    bn_image = b1_image

    # print(f"Means x {xmus[0]}, {xmus[-1]}; y {ymus[0]}, {ymus[-1]}")
    # print(f"Medians x {xmeds[0]}, {xmeds[-1]}; y {ymeds[0]}, {ymeds[-1]}")

    c = 1

    while (np.abs(xmus[0] - xmeds[0]) >= 0.1*xmeds[0]) or (np.abs(xmus[-1] - xmeds[-1]) >= 0.1*xmeds[0]) or (np.abs(ymus[0] - ymeds[0]) >= 0.1*ymeds[0]) or (np.abs(ymus[-1] - ymeds[-1]) >= 0.1*ymeds[0]):
        box_n = create_box(point, prev_box)
        bn_image, padded = get_box_image(segment, box_n)

        xmus, ymus, xmeds, ymeds = axis_stats(bn_image)

        if (np.shape(bn_image)[0]+7 > np.shape(segment)[0]) or (np.shape(bn_image)[1]+7 > np.shape(segment)[1]):
            #i.e. the box for the object is larger than the actual segment we are looking at 
            #this is ignoring objects that could be at the edges for the moment
            break

        # if (len(ymus) == 0) or (len(xmus) == 0) or (len(xmeds) == 0) or (len(ymeds) == 0):
        #     print(xmus)
        #     print(ymus)
        #     print(xmeds)
        #     print(ymeds)
        #     print("\n")
        #     print(point)
        #     print(prev_box)
        #     print(box_n)
        #     plt.imshow(bn_image)
        #     plt.show()
        
        prev_box=box_n
        c+=1 

    # print(box_n)
    #box_in_sky(segment, box_n, point)

    a, m, s = box_stats(bn_image) #average, median, std
    refined_box, xi, yi = refine_box(bn_image, a)
    obj = fit_ellipse(refined_box, m)
    #plot_ellipse(refined_box, obj)
    bm, rm = get_masks(refined_box, obj)

    masked_image = plot_new_image(xi, yi, bm, box_n, segment) #depends if we want to use binary or relative mask 
    return masked_image, bm, obj
    

def main():
    segment = image[2560:4601, 1549:2500] 
    # plt.imshow(segment)
    # plt.xlim((735, 723))
    # plt.ylim((1291, 1279))
    # plt.show()
    point = find_centre(segment)

    masks = []
    objects = []

    counter = 1

    print(f"segment shape {np.shape(segment)}")

    while (point != None).any():
        segment, bm, obj = finding_masks(segment, point, counter)
        masks.append(bm)
        objects.append(obj) 
        point = find_centre(segment)
        counter += 1

    return masks, objects

m, o = main()
print(len(o))
    



    



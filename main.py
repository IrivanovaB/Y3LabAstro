'''
The main module.
'''

from images import load_image, plot_pixel_histogram
from detection_box_gaussian import run_photometry


# # Read in our analysis image.
# image = load_image()

# # Plot the histogram.
# plot_pixel_histogram(im=image, p0=[2e6, 3400, 10, 0, 0])

# Run the photometry.
run_photometry()

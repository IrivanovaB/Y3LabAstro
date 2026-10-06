from astropy.io import fits 
import numpy as np
import scipy
import matplotlib.pyplot as plt
import cv2

# test_image = cv2.imread(r"test.png")

# print(type(test_image))
# plt.imshow(test_image)
# plt.show()


hdu = fits.open(r"Fits_Data\mosaic.fits")

data = hdu[0].data

# hist, __, __ = plt.hist(data.flatten())

std = np.std(data.flatten())
peak = np.average(data.flatten())
shape = np.shape(data)

#threshold of mean + 3sigma

threshold = std + peak

flat_data = data.flatten()
clean_data = np.where(flat_data >= threshold, flat_data, np.zeros_like(flat_data))
reshape_data = np.reshape(clean_data, shape)


# plt.plot(data[1000])
# plt.show()
# plt.imshow(data, cmap="gray")
# plt.colorbar()
# plt.title("Preprocessing: image after a threshold")
# plt.show()

hist = plt.hist(clean_data, bins="auto")
plt.xlabel("Pixel Value")
plt.ylabel("Count")
plt.xlim(left=1)
plt.semilogy()
plt.show()



# plt.xlabel("Pixel Value (a.u.)")
# plt.ylabel("Count")
# plt.title("Histogram of Image Values")
# plt.savefig("histogram of image values", dpi=300)
# plt.show()


# fft = np.abs(np.fft.fft2(data))
# fft_cleaned = [[pix if np.isfinite(pix) else 0 for pix in pix_row] for pix_row in fft]
# plt.imshow(fft_cleaned, norm="log")
# plt.show()

# hist = plt.hist(np.array(fft_cleaned).flatten())
# plt.semilogy()
# plt.show()

# fft_x = [0 if np.isfinite(pix) else pix for pix in fft[0]]
# x_path = [pix[0] for pix in fft]
# print(len(x_path))

# fft = scipy.fft.fft(hist)
# fft_freq = scipy.fft.fftfreq(len(hist))
# # fft = abs(fft)
# # fft_freq = fft_freq[fft_freq > 0]
# plt.plot(fft_freq, fft)
# plt.show()

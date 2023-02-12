import cv2 as cv


def moph(image, n_iter, kernel_size):
  kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
  return cv.dilate(image, kernel, iterations=n_iter)
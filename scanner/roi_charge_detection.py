import cv2 as cv
from .roi import ROI, ArtifactROI
import dataclasses
import numpy as np
from typing import List

def pyramid_down(image: np.array, n: int):
  for _ in range(n):
    image = cv.pyrDown(image)
  factor = 1/2**n
  return image, factor


class ScreenState:
  roi: List[ROI]
  transformed_roi: List[ROI]
  def __init__(self, roi_list):
    self.roi_list = roi_list
    self.scaled_roi_list = None

    self.previous = None
    self.small_screen = None

    self.diff_threshold = 0.5
    self.n_pyramid_down = 2

  def _is_same_image(self, current, previous):
    diff = np.mean((current - previous)**2)
    if diff > self.diff_threshold:
      return False
    return True

  def compare(self, screen):
    current = []
    for i, roi in enumerate(self.scaled_roi_list):
      clip = roi.clip_image(screen)
      current.append(clip)

    result = False
    if self.previous:
      def compare_all():
        for i in range(len(self.scaled_roi_list)):
          if not self._is_same_image(current[i], self.previous[i]):
            return False
        return True
      result = compare_all()
    self.previous = current
    return result

  def is_same(self, screen):
    screen = cv.cvtColor(screen, cv.COLOR_BGR2GRAY)
    screen, factor = pyramid_down(screen, self.n_pyramid_down)
    self.small_screen = screen

    if not self.scaled_roi_list:
      rois = []
      for roi in self.roi_list:
        troi = roi.scale(factor)
        rois.append(troi)
      self.scaled_roi_list = rois

    return self.compare(screen)



def test_roi_detection():
  roi = [
    ROI(1214, 150, 1500, 430),
    ROI(1230, 590, 1800, 790),
    ROI(1251, 530, 1324, 570),
    ROI(1640, 35, 1869, 82),
  ]

  state = ScreenState(roi)

  from . import frame_reader
  filename = frame_reader.get_test_video_path()
  reader = frame_reader.FrameReader(filename, time=0)

  frame = reader.next()
  is_same = state.is_same(frame)
  assert not is_same

  for i in range(23):
    frame = reader.next()
    is_same = state.is_same(frame)
    assert is_same, i

  frame = reader.next()
  is_same = state.is_same(frame)
  assert not is_same

  for i in range(9):
    frame = reader.next()
    is_same = state.is_same(frame)
    assert is_same, i

  frame = reader.next()
  is_same = state.is_same(frame)
  assert not is_same
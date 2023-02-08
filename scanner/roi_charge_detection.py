import cv2 as cv
from .roi import ArtifactROI
import dataclasses
import numpy as np

def pyramid_down(image, n):
  for _ in range(n):
    image = cv.pyrDown(image)
  return image


class ScreenState:
  roi: ArtifactROI
  transformed_roi: ArtifactROI
  def __init__(self, roi):
    self.roi = roi

    self.transformed_roi = None
    self.previous = None

    self.small_screen = None

  @staticmethod
  def compare_roi(current, previous):
    for k, v in current.items():
      im_prev = previous[k]
      im_curr = v

      diff = np.mean((im_prev - im_curr)**2)
      # print(f'{k} {diff=}')
      
      if diff > 0.5:
        return False
    return True

  def compare(self, screen):
    current = {}
    roi_props = dataclasses.asdict(self.transformed_roi)
    for k, v in roi_props.items():
      x, y, xx, yy = v
      current[k] = screen[y:yy, x:xx]

    result = False
    if self.previous:
      result = self.compare_roi(current, self.previous)
    self.previous = current
    return result

  def is_same(self, screen):
    small_screen = cv.cvtColor(screen, cv.COLOR_BGR2GRAY)
    small_screen = pyramid_down(small_screen, 2)
    self.small_screen = small_screen

    if not self.transformed_roi:
      w, h = small_screen.shape[:2]
      ww, hh = screen.shape[:2]
      ratio = w / ww
      self.transformed_roi = self.roi.scale(ratio)
      print(self.transformed_roi)

    return self.compare(small_screen)



def test_roi_detection():
  roi = ArtifactROI(
      main=[1214, 150, 1500, 430],
      sub=[1230, 590, 1800, 790],
      level=[1251, 530, 1324, 570],
      title=[1640, 35, 1869, 82],
  )

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
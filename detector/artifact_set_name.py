import cv2 as cv
import numpy as np
import pytesseract as ocr

import scanner
from scanner import ROI
from sketch import sketch

from .util import moph


def find_artifact_set_name_roi(screen: np.array, artifact_panel_roi: ROI):
  '''
  screen: colored image
  '''
  panel = artifact_panel_roi.clip_image(screen)
  hsv = cv.cvtColor(panel, cv.COLOR_BGR2HSV)

  h = cv.inRange(hsv[...,0], 50, 58)
  s = cv.inRange(hsv[...,1], 30, 255)
  mask = s & h

  mask = moph(mask, kernel_size=[3, 3], n_iter=5)

  contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  text_contour = min(contours, key=lambda i: cv.boundingRect(i)[1])
  x, y, w, h = cv.boundingRect(text_contour)

  return ROI(x, y, x+w, y+h).translate(*artifact_panel_roi.p1)


def parse_artifact_set_name(gray, set_name_roi: ROI):
  slice = set_name_roi.clip_image(gray)
  sketch('artifact_set_name/roi', set_name_roi)

  slice = 255 - slice
  _, mask = cv.threshold(slice, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
  slice = slice & mask
  slice = cv.equalizeHist(slice)
  sketch('artifact_set_name/before_ocr', slice)
  
  text = ocr.image_to_string(slice, lang="chi_sim", config="--psm 6")
  set_name = scanner.match_artifact_set_name(text)

  return set_name



import pytest

frame_timestamp = [
    (0,     '流放者'),
    (5.22,  '祭水之人'),
    (5.4,   '游医'),
]

@pytest.fixture(params=frame_timestamp)
def video_test_case(request):
    timestamp, name = request.param
    filename = scanner.frame_reader.get_test_video_path()
    reader = scanner.FrameReader(filename, time=timestamp)
    return (reader.next(), name)


def test_find_artifact_set_roi(video_test_case):
  video_frame, name = video_test_case

  frame = video_frame.copy()
  gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  lower_panel = ROI(1213, 504, 1830, 1111)

  set_name_roi = find_artifact_set_name_roi(frame, lower_panel)
  parsed_name = parse_artifact_set_name(gray, set_name_roi)
  
  assert parsed_name == name
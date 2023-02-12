import cv2 as cv
from scanner import ROI
import scanner
import pytesseract as ocr
import numpy as np


def find_all_text_roi_in_range(gray, roi: ROI, color_range, kernel_size, kernel_n_iter):
  im = roi.clip_image(gray)
  im = cv.inRange(im, color_range['lo'], color_range['hi'])

  kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
  im = cv.dilate(im, kernel, iterations=kernel_n_iter)
  # im = cv.morphologyEx(im, cv.MORPH_CLOSE, kernel, iterations=kernel_n_iter)

  cnts = cv.findContours(im, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  cnts = cnts[0] if len(cnts) == 2 else cnts[1]

  result = []
  for c in cnts:
    x, y, w, h = cv.boundingRect(c)
    text_roi = ROI(x, y, x+w, y+h).translate(*roi.p1)
    result.append(text_roi)

  return result

def parse_type(gray: np.array, roi: ROI):
  slice = roi.clip_image(gray)
  text = ocr.image_to_string(slice, lang="chi_sim")
  return scanner.match_artifact_type(text)

def parse_main_stat_name(gray: np.array, roi: ROI):
  slice = roi.clip_image(gray)
  slice = 255 - slice

  # slice = cv.equalizeHist(slice)

  text = ocr.image_to_string(slice, lang="chi_sim", config="--psm 6")
  return scanner.match_main_stat_name(text)

def parse_main_stat_value(gray: np.array, roi: ROI):
  slice = roi.clip_image(gray)
  text = ocr.image_to_string(slice, config="--psm 6")
  return scanner.match_main_stat_value(text)

def parse_type_main_stat_name_value(gray: np.array, upper_panel_roi: ROI):
  color_range = dict(lo=150, hi=255)
  kernel_size = 10,3
  kernel_n_iter = 5
  text_rois = find_all_text_roi_in_range(
    gray, upper_panel_roi, color_range, kernel_size, kernel_n_iter)

  text_rois.sort(key=lambda r: r.y1)
  assert len(text_rois) == 3
  artifact_type, main_stat_name, main_stat_value = text_rois

  type = parse_type(gray, artifact_type)
  main_name = parse_main_stat_name(gray, main_stat_name)
  main_value = parse_main_stat_value(gray, main_stat_value)

  return type, main_name, main_value




import pytest
frame_timestamp = [
    (0,     ('时之沙', '攻击力', '22.3%')),
    (5.22,  ('理之冠', '暴击率', '7.5%')),
    (5.4,   ('生之花', '生命值', '918')),
]

@pytest.fixture(params=frame_timestamp)
def video_test_case(request):
    timestamp, name = request.param
    filename = scanner.frame_reader.get_test_video_path()
    reader = scanner.FrameReader(filename, time=timestamp)
    return (reader.next(), name)


def test_find_artifact_set_roi(video_test_case):
  video_frame, ground_truth = video_test_case

  frame = video_frame.copy()
  gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  upper_panel = ROI(1214, 230, 1550, 430)

  result = parse_type_main_stat_name_value(gray, upper_panel)
  
  assert result == ground_truth
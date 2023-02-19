import cv2 as cv
import pytesseract as ocr

import scanner
from scanner import ROI
from sketch import sketch


def parse_level(gray, roi: ROI):
  slice = roi.clip_image(gray)
  sketch('level/roi', roi)

  slice = 255 - slice
  sketch('level/before_ocr', slice)

  text = ocr.image_to_string(slice)
  level = scanner.match_level(text)
  return level



import pytest

frame_timestamp = [
    (0,     '9'),
    (5.22,  '4'),
    (5.4,   '4'),
]

@pytest.fixture(params=frame_timestamp)
def video_test_case(request):
    timestamp, name = request.param
    filename = scanner.frame_reader.get_test_video_path()
    reader = scanner.FrameReader(filename, time=timestamp)
    return (reader.next(), name)


def test_find_artifact_set_roi(video_test_case):
  video_frame, reference = video_test_case

  frame = video_frame.copy()
  gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  level_roi = ROI(1251, 530, 1324, 570)

  level = parse_level(gray, level_roi)
  
  assert level == reference
import cv2 as cv
from scanner import ROI
import scanner
import pytesseract as ocr
from .util import moph



def parse_level(gray, roi: ROI):
  slice = roi.clip_image(gray)

  slice = 255 - slice

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
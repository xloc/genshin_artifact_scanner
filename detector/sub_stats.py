import cv2 as cv
import pytesseract as ocr

import scanner
from scanner import ROI
from sketch import sketch


def find_sub_stats_roi(set_name_roi: ROI, sub_stats_template_roi: ROI):
  sub_stats_roi = sub_stats_template_roi.copy()
  sub_stats_roi.y2 += set_name_roi.y1
  return sub_stats_roi


def parse_sub_stats(gray, sub_stats_roi: ROI):
  sketch('sub_stats/roi', sub_stats_roi)

  slice = sub_stats_roi.clip_image(gray)
  sketch('sub_stats/before_ocr', slice)
  
  text = ocr.image_to_string(slice, lang="chi_sim", config="--psm 6")
  set_name = scanner.match_sub_stats(text)

  return set_name



import pytest

frame_timestamp = [
    (0,     {'元素精通': '13', '攻击力': '12', '生命值': '3.3%', '防御力': '19'}),
    (5.22,  {'攻击力': '2.5%', '防御力': '8'}),
    (5.4,   {'元素充能效率': '3.1%', '暴击伤害': '3.3%'}),
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
  sub_stats = ROI(1270, 590, 1800, 504)

  from .artifact_set_name import find_artifact_set_name_roi
  artifact_set_roi = find_artifact_set_name_roi(frame, lower_panel)
  sub_stats_roi = find_sub_stats_roi(artifact_set_roi, sub_stats)
  parsed_name = parse_sub_stats(gray, sub_stats_roi)
  
  assert parsed_name == name
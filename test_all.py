from scanner import frame_reader, ScreenState, ROI
import numpy as np
import cv2 as cv
from detector import level, type_and_main_stat, artifact_set_name, sub_stats

# class allroi:
#   upper = ROI(1214, 230, 1550, 430)
#   lower = ROI(1213, 504, 1830, 1111)
#   level = ROI(1251, 530, 1324, 570)
#   sub_stats_template = ROI(1270, 590, 1800, 504)


class allroi:
  upper = ROI(1434, 265, 1828, 520)
  lower = ROI(1434, 596, 2159, 1310)
  level = ROI(1476, 632, 1561, 674)
  sub_stats_template = ROI(1500, 700, 2141, 596)

class ArtifactFields:
  def __repr__(self):
    return '\n'.join([f"{k:10}: {v}" for k, v in self.__dict__.items()])


def parse_frame(frame: np.array):
  artifact = ArtifactFields()
  gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

  set_roi = artifact_set_name.find_artifact_set_name_roi(frame, allroi.lower)
  artifact.set_name = artifact_set_name.parse_artifact_set_name(gray, set_roi)

  sub_stats_roi = sub_stats.find_sub_stats_roi(set_roi, allroi.sub_stats_template)
  artifact.sub_stats = sub_stats.parse_sub_stats(gray, sub_stats_roi)

  type_name_value = type_and_main_stat.parse_type_main_stat_name_value
  [
    artifact.type, 
    artifact.main_stat_name, 
    artifact.main_stat_value
  ] = type_name_value(gray, allroi.upper)

  artifact.level = level.parse_level(gray, allroi.level)

  return artifact



import json
def is_data_same(a, b):
  aa = json.dumps(a, sort_keys=True)
  bb = json.dumps(b, sort_keys=True)
  return aa == bb


def test_parse_all(video_path: str):
  if not video_path:
    video_path = frame_reader.get_test_video_path()
  reader = frame_reader.FrameReader(video_path, time=0)

  state = ScreenState([allroi.upper, allroi.lower])

  artifacts = []
  last_info = None
  while True:
    frame = reader.next()
    if frame is None: break
    
    if not state.is_same(frame):
      try:
        info = parse_frame(frame)
        info = info.__dict__
      except Exception as e:
        info = dict(error_message=str(e))
        

      if is_data_same(info, last_info):
        continue

      result = dict(time=reader.frame_time, info=info)
      artifacts.append(result)
      last_info = info
      print(f'{reader.frame_time:.4f}', info)

  return artifacts




import click

@click.command()
@click.option("--output_path", type=click.Path(exists=False, dir_okay=False), default="output.yaml", help='artifacts output filename')
@click.argument("video_path", type=click.Path(exists=True, dir_okay=False))
def command(output_path, video_path):
  result = test_parse_all(video_path)

  import yaml
  with open(output_path, 'w') as f:
    yaml.dump(result, f, allow_unicode=True)




if __name__ == "__main__":
  command()

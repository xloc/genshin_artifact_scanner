import cv2 as cv
from scanner import ROI
import scanner
import pytesseract as ocr

class allroi:
  artifact_pannel = ROI(1213, 148, 1830, 1111)
  sub_stats = ROI(1270, 590, 1800, artifact_pannel.y1)
  main = ROI(1214, 230, 1600, 430)
  level = ROI(1251, 530, 1324, 570)



def moph(image, n_iter, kernel_size):
  kernel = cv.getStructuringElement(cv.MORPH_RECT, kernel_size)
  return cv.dilate(image, kernel, iterations=n_iter)


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


def find_artifact_set_name_roi(image):
  image = allroi.artifact_pannel.clip_image(image)
  hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

  h = cv.inRange(hsv[...,0], 50, 58)
  s = cv.inRange(hsv[...,1], 30, 255)
  mask = s & h

  mask = moph(mask, kernel_size=[3, 3], n_iter=5)

  contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
  text_contour = max(contours, key=cv.contourArea)
  x,y,w,h = cv.boundingRect(text_contour)

  return ROI(x, y, x+w, y+h).translate(*allroi.artifact_pannel.p1)


def find_sub_stats_roi(set_name_roi: ROI):
  sub_stats_roi = allroi.sub_stats.copy()
  sub_stats_roi.y2 += set_name_roi.y1
  return sub_stats_roi


class ArtifactFields:
  def __repr__(self):
    return '\n'.join([f"{k:10}: {v}" for k, v in self.__dict__.items()])


def parse_frame(frame):
  gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
  artifact = ArtifactFields()

  # artifact set name
  set_name_roi = find_artifact_set_name_roi(frame)
  slice = set_name_roi.clip_image(gray)
  text = ocr.image_to_string(slice, lang="chi_sim")
  artifact.set_name = scanner.match_artifact_set_name(text)

  # substats
  sub_stats_roi = find_sub_stats_roi(set_name_roi)
  slice = sub_stats_roi.clip_image(gray)
  text = ocr.image_to_string(slice, lang="chi_sim")
  artifact.sub_stats = scanner.match_sub_stats(text)

  # type & main stat name/value
  color_range = dict(lo=150, hi=255)
  kernel_size = 10,3
  kernel_n_iter = 5
  text_rois = find_all_text_roi_in_range(gray, allroi.main, color_range, kernel_size, kernel_n_iter)
  text_rois.sort(key=lambda r: r.y1)
  assert len(text_rois) == 3
  artifact_type, main_stat_name, main_stat_value = text_rois
  # type
  slice = artifact_type.clip_image(gray)
  text = ocr.image_to_string(slice, lang="chi_sim")
  artifact.type = scanner.match_artifact_type(text)
  # main stat name
  slice = main_stat_name.clip_image(gray)
  slice = 255 - slice
  slice = cv.equalizeHist(slice)
  text = ocr.image_to_string(slice, lang="chi_sim")
  artifact.main_stat_name = scanner.match_main_stat_name(text)
  # main stat value
  slice = main_stat_value.clip_image(gray)
  text = ocr.image_to_string(slice)
  artifact.main_stat_value = scanner.match_main_stat_value(text)

  # level
  slice = allroi.level.clip_image(gray)
  slice = 255 - slice
  text = ocr.image_to_string(slice)
  artifact.level = scanner.match_level(text)

  return artifact



def test_parse():
  from scanner import frame_reader, ArtifactROI, ScreenState
  import dataclasses
  filename = frame_reader.get_test_video_path()
  print(filename)
  reader = frame_reader.FrameReader(filename, time=0, interval=0.02)

  roi = ArtifactROI(
      main=[1214, 150, 1500, 430],
      sub=[1230, 590, 1800, 790],
      level=[1251, 530, 1324, 570],
      title=[1640, 35, 1869, 82],
  )
  state = ScreenState(roi)

  artifacts = []
  while True:
    frame = reader.next()
    if frame is None: break

    if not state.is_same(frame):
      okay = "pass"
      try:
        info = parse_frame(frame)
        info = info.__dict__
        result = dict(time=reader.frame_time, info=info)
        artifacts.append(result)
        print(f'{reader.frame_time:.4f}', info)
      except Exception as e:
        okay = 'fail'
        print(f'{reader.frame_time:.4f}', e)
        artifacts.append(dict(time=reader.frame_time, error=True, message=str(e)))
      cv.imwrite(f"error/{reader.frame_time:.4f} {okay}.png", frame)
        # raise e
  
  
  



  
if __name__ == "__main__":
  test_parse()



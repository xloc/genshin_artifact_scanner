import cv2 as cv
import pytesseract as ocr
from scanner.matchers import (
  match_main_stat,
  match_artifact_type,
  match_artifact_name,
  match_sub_stats,
  match_level
)

def parse_frame(image, roi):
  image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
  image = cv.equalizeHist(image)

  x, y, xx, yy = roi.main
  slice = image[y:yy, x:xx]
  slice = 255 - slice
  s = ocr.image_to_string(slice, lang="chi_sim+chi_tra")
  main_stat = match_main_stat(s)
  type = match_artifact_type(s)
  name = match_artifact_name(s)


  x, y, xx, yy = roi.sub
  slice = image[y:yy, x:xx]
  s = ocr.image_to_string(slice, lang="chi_sim+chi_tra")
  sub_stats = match_sub_stats(s)

  x, y, xx, yy = roi.level
  slice = 255 - image[y:yy, x:xx]
  s = ocr.image_to_string(slice)
  level = match_level(s)

  return Artifact(
      type=type,
      name=name,
      main_stat=main_stat,
      sub_stats=sub_stats,
      level=level
  )

roi = ArtifactROI(
    main=[1214, 150, 1500, 430],
    sub=[1230, 590, 1800, 790],
    level=[1251, 530, 1324, 570],
    title=[1640, 35, 1869, 82],
)
art = parse_frame(frame, roi)
dataclasses.asdict(art)

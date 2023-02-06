import cv2 as cv

class FrameReader:
  capture: cv.VideoCapture

  def __init__(self, path, time=None, interval=None):
    self.capture = capture = cv.VideoCapture(path)
    self.n_frame = capture.get(cv.CAP_PROP_FRAME_COUNT)
    self.sample_rate = capture.get(cv.CAP_PROP_FPS)
    self.duration = self.n_frame / self.sample_rate

    self.time = 0
    self.interval = interval
    self.frame_time = None

    if time:
      self.time = time
      self.capture.set(cv.CAP_PROP_POS_MSEC, int(time * 1000))

  def next(self):
    self.frame_time = self.time
    valid, frame = self.capture.read()
    if not valid:
      return None

    if self.interval:
      self.time += self.interval
      self.capture.set(cv.CAP_PROP_POS_MSEC, int(self.time * 1000))


    return frame


def get_test_video_path():
  import glob

  filename = glob.glob("*.[mM][pP]4")
  filename = list(filename)[0]
  return filename


def test_frame_reader():
  filename = get_test_video_path()
  reader = FrameReader(filename, time=0, interval=1)

  for i in range(3):
    frame = reader.next()
    print(reader.frame_time)
    assert(frame.shape == (1260, 1920, 3))
    # cv.imshow(frame)

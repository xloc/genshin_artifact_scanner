import dataclasses
import numpy


@dataclasses.dataclass
class ArtifactROI:
  main: list
  sub: list
  level: list
  title: list

  def scale(self, factor: float):
    def scale(l):
      return [int(i * factor) for i in l]
    
    props = dataclasses.asdict(self)
    props = {k: scale(v) for k, v in props.items()}
    return ArtifactROI(**props)

def test_roi_scale():
  roi = ArtifactROI(
      main=[1214, 150, 1500, 430],
      sub=[1214, 500, 1830, 790],
      level=[1251, 530, 1324, 570],
      title=[1637, 30, 1869, 82],
  )
  roi = roi.scale(0.5)
  assert roi.main == [607, 75, 750, 215]
  assert roi.sub == [607, 250, 915, 395]


@dataclasses.dataclass
class ROI:
  x1: int
  y1: int
  x2: int
  y2: int

  p1 = property(lambda s: (s.x1, s.y1))
  p2 = property(lambda s: (s.x2, s.y2))
  w = property(lambda s: s.x2 - s.x1)
  h = property(lambda s: s.y2 - s.y1)

  def __getitem__(self, i):
    return [self.x1, self.y1, self.x2, self.y2][i]
  
  def clip_image(self, image: numpy.array):
    return image[self.y1:self.y2, self.x1:self.x2, ...]
  
  def translate(self, x, y):
    return ROI(self.x1 + x, self.y1 + y,
               self.x2 + x, self.y2 + y)
  
  def copy(self):
    return ROI(**dataclasses.asdict(self))

def test_roi_unpacking():
  a, b, c, d = ROI(1, 2, 3, 4)
  assert a==1 and b==2 and c==3 and d==4

def test_roi_clip_image():
  image = numpy.zeros([100,100,1])
  roi = ROI(20, 20, 30, 50)
  result = roi.clip_image(image)
  assert result.shape == (30, 10, 1)

def test_roi_translate():
  a, b, c, d = ROI(1, 2, 3, 4).translate(10, 20)
  assert a==11 and b==22 and c==13 and d==24

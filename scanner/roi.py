import dataclasses

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
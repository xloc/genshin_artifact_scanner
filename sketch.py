import collections
import numpy as np
import cv2 as cv
import pathlib

import yaml

def defaultdict_representer(dumper, data):
    return dumper.represent_dict(dict(data))
yaml.add_representer(collections.defaultdict, defaultdict_representer)


class SketchRecorder:
  def __init__(self, base_dir='.', save_all=False, save_error=True):
    self.save_all = save_all
    self.save_error = save_error
    self.base_dir = pathlib.Path(base_dir)
    self.record = {}
  
  def save(self):
    # save all images
    images = {k:v for k, v in self.record.items() if type(v) == np.ndarray}
    for k in images:
      file_path = self.base_dir.joinpath(f"{k}.png")
      file_path.parent.mkdir(parents=True, exist_ok=True)
      cv.imwrite(str(file_path), images[k])

    # save everything else to yaml
    others = {k:v for k, v in self.record.items() if type(v) != np.ndarray}
    json = collections.defaultdict(dict)
    for k in others:
      curr = json
      for nested in k.split("/")[:-1]:
        curr = curr[nested]
      print(json)
      curr[k.rsplit('/', 1)[-1]] = others[k]

    self.base_dir.mkdir(parents=True, exist_ok=True)
    file_path = self.base_dir / "data.yaml"
    yaml.dump(json, file_path.open('w'), allow_unicode=True)

  def __enter__(self):
    self.register()
    return self
  
  def __exit__(self, exc_type, exc_value, traceback):
    is_error = exc_type is not None
    if self.save_all or (self.save_error and is_error):
      self.save()
    if is_error:
      raise exc_value

  def register(self):
    global recorder
    recorder = self

  def sketch(self, key, value):
    self.record[key] = value

  def __str__(self):
    return '\n'.join([
      f"{key}: {value!r}"
        for key, value in self.record.items()
    ])
  
recorder = None


def can_sketch() -> SketchRecorder:
  global recorder
  if recorder is not None:
    return recorder
  
def sketch(key: str, value):
  global recorder
  if recorder is not None:
    return recorder.sketch(key, value)
  

def test_sketch():
  assert can_sketch() == None

  def make_image(h, w, a):
      x = np.linspace(0, 2*np.pi*w/a, w)
      y = np.linspace(0, 2*np.pi*h/a, h)
      xx, yy = np.meshgrid(x, y)

      img = np.sin(xx) * np.cos(yy)
      img += 1
      img *= 127

      return img
  
  with SketchRecorder('sketch/test', save_all=True) as r:
    r.sketch('a', 1)
    sketch('z/b', 2)
    sketch('z/c', 3)
    sketch('b/c', make_image(500, 500, 100))
  

  # sr = SketchRecorder()
  # sr.register()

  # assert can_sketch() is not None
  # if recorder := can_sketch():
  #   recorder.sketch('abc', 'asdf')
  #   recorder.sketch('abd', 'asdf')

  # assert str(sr) == "abc: 'asdf'\nabd: 'asdf'"

  
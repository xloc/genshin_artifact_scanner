import collections
import pathlib
import traceback as tracebacklib

import yaml
import numpy as np
import cv2 as cv

from scanner.roi import ROI


def defaultdict_representer(dumper, data):
    return dumper.represent_dict(dict(data))
yaml.add_representer(collections.defaultdict, defaultdict_representer)

def str_presenter(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, str_presenter)


def roi_constructor(loader, node):
  data = loader.construct_mapping(node)
  return ROI(**data)
yaml.add_constructor('!!python/object:scanner.roi.ROI', roi_constructor, Loader=yaml.FullLoader)



class SketchRecorder:
  def __init__(self, base_dir='.', save_all=False, save_error=True, log_error=True):
    self.save_all = save_all
    self.save_error = save_error
    self.log_error = log_error
    self.base_dir = pathlib.Path(base_dir)

    self.record = {}

  def _save_yaml(self, yaml_data: dict):
    json = collections.defaultdict(dict)
    for k in yaml_data:
      curr = json
      for nested in k.split("/")[:-1]:
        curr = curr[nested]
      curr[k.rsplit('/', 1)[-1]] = yaml_data[k]

    self.base_dir.mkdir(parents=True, exist_ok=True)
    file_path = self.base_dir / "data.yaml"

    # if file_path.exists():
    #   if file_path.is_dir():
    #     raise FileExistsError(f"the file {file_path} is exist and is a dir")
    #   with file_path.open() as f:
    #     prev_yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    #   yaml_data.update(prev_yaml_data)
    
    yaml.dump(json, file_path.open('w'), allow_unicode=True)
  
  def save(self):
    # save all images
    images = {k:v for k, v in self.record.items() if type(v) == np.ndarray}
    for k in images:
      file_path = self.base_dir.joinpath(f"{k}.png")
      file_path.parent.mkdir(parents=True, exist_ok=True)
      cv.imwrite(str(file_path), images[k])

    # save everything else to yaml
    others = {k:v for k, v in self.record.items() if type(v) != np.ndarray}
    self._save_yaml(others)

  def __enter__(self):
    self.register()
    return self
  
  def __exit__(self, exc_type, exc_value, traceback):
    is_error = exc_type is not None

    if is_error and self.log_error:
      self.sketch('catched_exception/exception', exc_value)

      trackback_object = tracebacklib.format_exception(exc_type, exc_value, traceback)
      traceback_str = '\n'.join(trackback_object)
      self.sketch('catched_exception/traceback', traceback_str)

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
  
def test_excpetion_log():
  import contextlib

  options = dict(
    log_error=True,
    save_error=True
  )

  with contextlib.suppress(ValueError):
    with SketchRecorder('sketch/exception', "options") as r:
      raise ValueError("this is a value error")
  
    

  
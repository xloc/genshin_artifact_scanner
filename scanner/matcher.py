import re
import yaml

level_re = re.compile(r'\+(\d+)')
def match_level(s):
  matched = level_re.search(s)
  if not matched:
    raise KeyError("no matched level")
  return matched[1]

def test_match_level():
  result = match_level("+12")
  assert result == "12"



VALUE_OR_PERCENTAGE_REGEX = r"\d+\.\d+%|\d[\d,]*"



sub_stat_re = re.compile(
    r'(生命值|攻击力|防御力|元素精通|暴击率|暴击伤害|元素充能效率)' +
    r'\+' +
    r'({})'.format(VALUE_OR_PERCENTAGE_REGEX))
def match_sub_stat(ln):
  groups = sub_stat_re.search(ln)
  if groups is None:
    return None
  return groups[1], groups[2]

def match_sub_stats(s):
  result = {}
  for ln in s.splitlines():
    ret = match_sub_stat(ln)
    if ret is None: continue

    stat, val = ret
    result[stat] = val

  return result

def test_match_sub_stats():
  s = " \n\n \n\n“ 防御力+19\n“元素精通+13\n“ 生命值+3.3%\n' 攻击力+12\n\x0c"
  result = match_sub_stats(s)
  assert result == {'元素精通': '13', '攻击力': '12', '生命值': '3.3%', '防御力': '19'}



main_stats = "生命值 攻击力	防御力 元素精通 元素充能效率 物理伤害加成 暴击率 暴击伤害 治疗加成".split()
main_stats += [element+"元素伤害加成" for element in "火水风草冰雷岩"]
def match_main_stat_name(s):
  matched = False
  for stat in main_stats:
    if stat in s:
      matched = True
      break
  if not matched:
    raise KeyError(f"no matched main stat in {s!r}")
  
  return stat

value_re = re.compile(VALUE_OR_PERCENTAGE_REGEX)
def match_main_stat_value(s):
  value = value_re.search(s)
  if value is None:
    raise KeyError(f"no value found in {s!r}")
  
  return value[0]

def match_main_stat(s):
  name = match_main_stat_name(s)
  value = match_main_stat_value(s)

  return name, value

def test_match_main_stat():
  s = '流放者怀表\n\n时之沙\n\n攻击力\n\n22.3%\n\x0c'
  ret = match_main_stat(s)
  assert ret == ('攻击力', '22.3%')



artifact_types = dict(
  花="生之花", 
  羽="死之羽",
  沙="时之沙",
  杯="空之杯",
  冠="理之冠",
)
def match_artifact_type(s):
  for key, val in artifact_types.items():
    if key in s:
      return val
  raise KeyError("artifact type does not exist")

def test_match_artifact_type():
  s = '流放者怀表\n\n时之沙\n\n攻击力\n\n22.3%\n\x0c'
  ret = match_artifact_type(s)
  assert ret == '时之沙'



def load_artifact_names():
  import pathlib
  yaml_path = pathlib.Path(__file__).parent.joinpath("artifacts.yaml").resolve()
  print(yaml_path)

  with yaml_path.open() as f:
    artifact_data = yaml.load(f, Loader=yaml.FullLoader)

  artifact_names = []
  for key, combo in artifact_data.items():
    if key == "glacier-and-snowfield":
      continue
    for name in combo['item-name'].values():
      artifact_names.append(name)

  assert(len(artifact_names) == len(set(artifact_names)))
  # # if not 
  # import collections
  # {k:v for k, v in collections.Counter(artifact_names).items() if v>1}

  artifact_names = set(artifact_names)
  return artifact_names

artifact_names = load_artifact_names()
def match_artifact_name(s):
  for name in artifact_names:
    if name in s:
      return name
  raise KeyError(f"artifact name does not exist in {s!r}")

def test_match_artifact_name():
  s = '流放者怀表\n\n时之沙\n\n攻击力\n\n22.3%\n\x0c'
  ret = match_artifact_name(s)
  assert ret == '流放者怀表'


def artifact_set_name_mapper(name: str):
  if name.endswith('之人') and len(name) == 4:
    return f"祭{name[1]}之人"
  return name

# [\u4e00-\u9fa5] stands for chinese characters
def match_artifact_set_name(s):
  set_re = re.compile(r"([\u4e00-\u9fa5]+)[:;]")
  ret = set_re.search(s)
  if ret is None:
    raise KeyError(f"artifact set name does not exist in {s!r}")
  else:
    name = ret[1]
    name = artifact_set_name_mapper(name)
    return name

def test_match_artifact_set_name():
  s = '流放者:\n\x0c'
  assert match_artifact_set_name(s) == '流放者'
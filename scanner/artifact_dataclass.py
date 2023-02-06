from dataclasses import dataclass

@dataclass
class Artifact:
  type: object
  name: object
  level: object

  main_stat: object
  sub_stats: object

def test_artifact_dataclass():
  data = {
    'type': '死之羽',
    'name': '追忆之风',
    'level': '0',
    'main_stat': ('攻击力', '42'),
    'sub_stats': {'防御力': '17', '攻击力': '3.7%'}
  }

  Artifact(**data)
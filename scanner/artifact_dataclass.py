from dataclasses import dataclass

@dataclass
class Artifact:
  type: str
  name: str
  level: str

  main_stat: str
  sub_stats: dict[str, str]

def test_artifact_dataclass():
  data = {
    'type': '死之羽',
    'name': '追忆之风',
    'level': '0',
    'main_stat': ('攻击力', '42'),
    'sub_stats': {'防御力': '17', '攻击力': '3.7%'}
  }

  Artifact(**data)
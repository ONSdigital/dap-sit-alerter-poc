from pathlib import Path

import yaml


def write_yaml(tmp_path: Path, content: dict) -> str:
  file_path = tmp_path / 'config.yaml'
  file_path.write_text(yaml.dump(content))
  return str(file_path)
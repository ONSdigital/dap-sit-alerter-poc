from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml

from src.models.slo_config_model import load_slo_config


def write_yaml(tmp_path: Path, content: dict) -> str:
    file_path = tmp_path / 'config.yaml'
    file_path.write_text(yaml.dump(content))
    return str(file_path)


@pytest.fixture
def config_dictionary():
    return {
        "slo_days": {
            "high": 1,
            "medium": 10,
            "low": 100,
        }
    }


def test_load_slo_config_returns_a_dictionary():
    # act
    result = load_slo_config()
    # assert
    assert type(result) == dict


def test_load_slo_config_returns_expected_dictionary(tmp_path, config_dictionary):
    # arrange
    path = write_yaml(tmp_path, config_dictionary)

    # act
    result = load_slo_config(path)

    # assert
    assert result == config_dictionary["slo_days"]


def test_load_slo_config_raises_value_error_when_slo_days_are_missing(tmp_path):
    # arrange
    config = {"battlefield_counterstrike": {}}
    path = write_yaml(tmp_path, config)

    # act & assert
    with pytest.raises(ValueError):
        load_slo_config(path)


@pytest.mark.parametrize(
    "invalid_slo_days",
    [None, [], "Beneficial Cucumber", {}],
)
def test_load_slo_config_raises_value_error_when_slo_days_is_invalid(tmp_path, invalid_slo_days):
    # arrange
    config = {"slo_days": invalid_slo_days}
    path = write_yaml(tmp_path, config)

    # act & assert
    with pytest.raises(ValueError):
        load_slo_config(path)


@pytest.mark.parametrize(
    "invalid_priority_key",
    ["", "    ", 123, None],
)
def test_load_slo_config_raises_value_error_when_priority_key_is_invalid(tmp_path, invalid_priority_key):
    # arrange
    config = {"slo_days": {invalid_priority_key: 5}}
    path = write_yaml(tmp_path, config)

    # act & assert
    with pytest.raises(ValueError):
        load_slo_config(path)


@pytest.mark.parametrize(
    "invalid_day_value",
    [0, -1, 1.5, "3", None],
)
def test_load_slo_config_raises_value_error_when_days_value_is_invalid(tmp_path, invalid_day_value):
    # arrange
    config = {"slo_days": {"high": invalid_day_value}}
    path = write_yaml(tmp_path, config)

    # act & assert
    with pytest.raises(ValueError):
        load_slo_config(path)


def test_load_slo_config_raises_file_not_found_when_config_file_does_not_exist():
    # act & assert
    with pytest.raises(FileNotFoundError):
        load_slo_config("this_file_does_not_exist")


@patch("builtins.open", new_callable=mock_open, read_data="bad: yaml:")
@patch("yaml.safe_load", side_effect=yaml.YAMLError("parse error"))
def test_load_slo_config_raises_yaml_error_with_invalid_yaml_file(_mock_safe_load, _mock_file):
    # arrange
    path = "bandicoot_cumbersnazzle.yml"

    # act & assert
    with pytest.raises(yaml.YAMLError, match="parse error"):
        load_slo_config(path)


@patch("builtins.open", new_callable=mock_open, read_data="slo_days:\n  p1: 1")
def test_load_slo_config_calls_open_once(mock_file, tmp_path):
    # arrange
    path = "dummy.yml"

    # act
    load_slo_config(str(path))

    # assert
    mock_file.assert_called_once_with(path, "r")

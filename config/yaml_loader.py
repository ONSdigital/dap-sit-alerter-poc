import logging

import yaml


def load_yaml(path: str) -> dict:
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
    except Exception as err:
        # TODO: test dis
        logging.error(f"Failed to load config from {path}: {err}")
        raise
    return config



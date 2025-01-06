import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config():
    print(CONFIG_PATH)
    with open(CONFIG_PATH, "r") as fp:
        config = json.load(fp)
    return config

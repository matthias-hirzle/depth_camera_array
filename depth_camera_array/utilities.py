import json
import os

DEFAULT_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))


def create_if_not_exists(path: str) -> str:
    print(path)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def dump_dict_as_json(data: dict, path: str):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as f:
        json.dump(data, f)


def load_json_to_dict(path) -> dict:
    with open(path, 'r') as f:
        data = json.load(f)
    return data

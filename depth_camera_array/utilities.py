import json
import os


def get_or_create_data_dir() -> str:
    path = os.path.join(os.getcwd(), '..', 'data')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def dump_dict_as_json(data: dict, path: str):
    if not os.path.exists(os.path.basename(path)):
        os.makedirs(os.path.basename(path))
    with open(path, 'w') as f:
        json.dump(data, f)


def load_json_to_dict(path) -> dict:
    with open(path, 'r') as f:
        data = json.load(f)
    return data

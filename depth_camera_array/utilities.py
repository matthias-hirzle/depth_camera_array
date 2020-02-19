import os


def get_or_create_data_path() -> str:
    path = os.path.join(os.getcwd(), '..', 'data')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

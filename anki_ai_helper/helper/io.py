import os
import tempfile

ANKI_AI_HELPER_DIR = ".anki_ai_helper"


def _create_directory(base_path: str, directory_name: str) -> str:
    target_dir = os.path.join(base_path, directory_name)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    return target_dir


def create_package_directory(directory_name: str) -> str:
    home_dir = os.path.expanduser("~")
    hidden_dir = os.path.join(home_dir, ANKI_AI_HELPER_DIR)
    return _create_directory(hidden_dir, directory_name)


def create_temp_directory(directory_name: str) -> str:
    tmp_dir = tempfile.gettempdir()
    return _create_directory(tmp_dir, directory_name)


def delete_file(file_path: str) -> int:
    if os.path.exists(file_path):
        os.remove(file_path)
        return 1

    return 0

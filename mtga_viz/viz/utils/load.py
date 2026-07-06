from pathlib import Path
from importlib.resources import files
import json


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_asset_path(fmt: str, name: str, suffix: str = ".jpg") -> str:
    """
    Resolve an asset path from mtga_viz.viz.assets.

    Args:
        fmt (str): Format folder inside assets, e.g. "timeless".
        name (str): Canonical file name without extension.
        suffix (str, optional): File extension. Defaults to ".jpg".

    Returns:
        str: Full asset path as string.

    Raises:
        FileNotFoundError: If the asset does not exist.
    """
    path = files("mtga_viz.viz.assets").joinpath(fmt, f"{name}{suffix}")

    return str(path)


def load_data_plot(data_dir):
    """This function loads all required json at a given directory (basically the ones saved during exploration)"""
    if data_dir is None:
        raise ValueError("DATA_DIR must be defined in subclass.")

    data_dir = Path(data_dir)

    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    json_files = sorted(data_dir.glob("*.json"))   # only this folder
    # json_files = sorted(data_dir.rglob("*.json"))  # this folder + subfolders

    if not json_files:
        raise ValueError(f"No JSON files found in: {data_dir}")

    data = {}
    for path in json_files:
        data[path.stem] = load_json(path)

    return data

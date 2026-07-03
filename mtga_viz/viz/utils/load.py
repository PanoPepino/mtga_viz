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

    if not Path(path).exists():
        raise FileNotFoundError(
            f"Asset not found for fmt={fmt!r}, name={name!r}, suffix={suffix!r}"
        )

    return str(path)

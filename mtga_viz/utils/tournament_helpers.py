import pandas as pd
from pandas import DataFrame
from pathlib import Path
from mtga_viz.utils.constants import RESULT_SWAP


def invert_result(result: str) -> str:
    """
    This function just take the string result and invert it. Nothing strange.

    Args:
        result (str):

    Returns:
        str: The inversed result
    """

    result = str(result).strip()
    if result in RESULT_SWAP:
        return RESULT_SWAP[result]

    left, right = result.split("-")
    return f"{right.strip()}-{left.strip()}"


def load_tournament_csv(path) -> pd.DataFrame:
    """
    Function to load information of a tournament mirroing entries, so one properly accounts for oppo decks as user decks, as mtgmelee provides non mirroed results.

    Args:
        path (Path): The path to the .csv file to load.

    Returns:
        pd.DataFrame: The dataframe with reflected entries.
    """

    df = pd.read_csv(path)

    mirrored = df.copy()
    mirrored[["user_deck", "oppo_deck"]] = mirrored[["oppo_deck", "user_deck"]]
    mirrored["result_vs_oppo"] = mirrored["result_vs_oppo"].apply(invert_result)

    return pd.concat([df, mirrored], ignore_index=True)


def build_paths(directory=None, files=None):
    """
    This function will create paths to all provided files given a root directory.
    """

    if directory is None:
        directory = Path(".")
    else:
        directory = Path(directory)

    if files is None:
        return sorted(directory.glob("*.csv"))

    return [directory / file_name for file_name in files]

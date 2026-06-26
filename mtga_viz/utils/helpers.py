import math
import pandas as pd
import re

from pandas import DataFrame
from .constants import TWO_COLOR_GUILDS, THREE_COLOR_GUILDS


def add_hour_index(df,
                   time_col,
                   interval_window: int):
    """
    This function reads the the time_col (i.e. message_timestamp) of the dataframe and creates a new column with how many hours elapsed since begining of the recording. window is in charge of controlling the period of time you want to divide your data by.

    Example:

    - If total dataframe is 100 hours, and the interval window is 1 hour, it will divide the whole time span in 100 periods. If you then have weeks of recording, you can perhaps then say that window is 24h or more.

    Return:

    - The new df with the new column
    - Total length event, rounded
    - The amount of intervals of the event
    """

    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col])

    start_time = df[time_col].iloc[0]
    elapsed_hours = (df[time_col] - start_time).dt.total_seconds() / 3600.0

    df["time_window"] = (elapsed_hours // interval_window).astype("int64")
    intervals = df['time_window'].max()+1

    length_event = round((df[time_col].iloc[-1] - start_time).total_seconds() / 3600.0)

    return df, length_event, intervals  # Ojo, important the order


def is_trophy(df, run_col):
    """
    Simply checks if a run is a trophy and counts how many trophies obtained in the whole recording.
    """

    df = df.copy()
    df["is_trophy"] = df[run_col].eq("7-0").map({True: "yes", False: "no"})
    amount_trophies = df["is_trophy"].eq("yes").sum() / 7  # A trophy consists of 7 victories
    return df, amount_trophies


def mtg_prefix_normalisation(value):
    """
    This function checks a given string, inspects the 0-th element and evaluates if it belongs to the official ordering of colors by MTG (in lower case). if not, it reorders.
    """

    if not isinstance(value, str) or not value:
        return value

    parts = value.split(" ", 1)
    first = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    allowed = set("wubrg")
    if first and all(ch in allowed for ch in first):
        ordered = "".join(ch for ch in "wubrg" if ch in first)
        return f"{ordered} {rest}".rstrip()

    return value


def mtg_guild_normalisation(value):
    """
    Take Izzet, Dimir, Sultai wording to the right ordering colors, in lower case.
    """

    if not isinstance(value, str) or not value:
        return value

    # 1) Exactly: one of wurbg, then a space, then anything
    m = re.match(r'^([wubrg])\s+(.*)$', value)
    if m:

        return f"mono {m.group(1)} {m.group(2)}".rstrip()

    # 2) / 3) Replace family name only if it is the first token
    value = value
    parts = value.split(" ", 1)
    first = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if first in TWO_COLOR_GUILDS:
        return f"{TWO_COLOR_GUILDS[first]} {rest}".rstrip()

    if first in THREE_COLOR_GUILDS:
        return f"{THREE_COLOR_GUILDS[first]} {rest}".rstrip()

    return value


def assign_archetype(df: DataFrame,
                     source_col: str,
                     keyword_dict: dict,
                     new_col: str,
                     default_tag: str):
    """
    For a given column `source_col`, check its entries against a dictionary where each key is the archetype and each item is a list with important words for each archetype (i.e. Tempo would contain a list like ['tempo', 'shadow', 'canadian'], etc). Then, it assigns the archetype to each entry.

    As the meta would shift from event to event, the dictionary is user defined.
    """
    def find_tag(x):
        if pd.isna(x):
            return default_tag
        s = str(x).lower()
        for tag, keywords in keyword_dict.items():
            if any(k.lower() in s for k in keywords):
                return tag
        return default_tag

    df[new_col] = df[source_col].apply(find_tag)
    return df


def count_runs(df, run_col):
    """
    Checks if a run is a trophy, counts how many trophies were obtained, computes normalized run counts by dividing each row count by the total matches (wins + losses) that constitute that run result.
    """

    df = df.copy()

    # Amount of trophies (7-0 runs)
    # Assuming every 7-0 row is part of a 7-match set
    amount_trophies = df[run_col].eq("7-0").sum() / 7

    run_counts = df[run_col].value_counts(dropna=False)

    run_summary = pd.DataFrame({
        "run": run_counts.index,
        "count": run_counts.values
    })

    # Split wins and losses
    wins_losses = run_summary["run"].str.split("-", expand=True).astype(int)
    run_summary["wins"] = wins_losses[0]
    run_summary["losses"] = wins_losses[1]

    # (e.g., a 6-1 run has 7 rows, a 2-1 run has 3 rows)
    run_summary["games_expected_per_run"] = run_summary["wins"] + run_summary["losses"]

    # Handle edge case: if someone entered "0-0" or data is empty to avoid division by zero
    run_summary["denom"] = run_summary["games_expected_per_run"].replace(0, 1)

    # Calculate actual number of runs
    run_summary["normalized_count"] = run_summary["count"] / run_summary["denom"]

    run_summary = run_summary.sort_values(
        by=["games_expected_per_run", "wins", "losses"],
        ascending=[True, True, True]
    ).reset_index(drop=True)

    types_of_run = run_summary["run"].tolist()
    run_counts_out = run_summary.set_index("run")["count"]
    normalized_run_counts = run_summary.set_index("run")["normalized_count"]

    return df, amount_trophies, types_of_run, run_counts_out, normalized_run_counts


def list_to_table(items, n_cols=4):
    """
    Transform any list or series to a simple table for cleaner visualisation.
    """

    items = sorted(list(items), key=str.lower)
    rows = math.ceil(len(items) / n_cols)
    padded = items + [None] * (rows * n_cols - len(items))
    table = pd.DataFrame([padded[i:i+n_cols] for i in range(0, len(padded), n_cols)])
    return print(table.to_string(index=False, header=False))

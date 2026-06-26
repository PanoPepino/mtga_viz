import math
import pandas as pd
import re

from pandas import DataFrame
from .constants import TWO_COLOR_GUILDS, THREE_COLOR_GUILDS


def add_hour_index(df,
                   time_col,
                   interval_window: int):
    """
    Read the time_col (i.e. message_timestamp) and create a new integer column
    ``time_window`` representing how many full ``interval_window``-hour buckets
    have elapsed since the first recorded timestamp.

    This is the primary function for slicing event data into hourly (or
    multi-hour) intervals before computing per-interval statistics.

    Example:
        - If the total recording spans 100 hours and ``interval_window=1``,
          the data is divided into 100 one-hour periods.
        - If ``interval_window=24``, each bucket covers one calendar day.

    Args:
        df (DataFrame): Raw or cleaned match DataFrame containing a timestamp column.
        time_col (str): Name of the column with UTC-compatible timestamp strings.
        interval_window (int): Width of each time bucket in hours.

    Returns:
        tuple:
            - df (DataFrame): Copy of the input with a new ``time_window`` int column.
            - length_event (int): Total event duration in hours, rounded to the nearest hour.
            - intervals (int): Total number of distinct time buckets present in the data.

    Note:
        Return order matters — unpack as ``df, length_event, intervals``.
    """

    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    df = df.dropna(subset=[time_col])

    start_time = df[time_col].iloc[0]
    elapsed_hours = (df[time_col] - start_time).dt.total_seconds() / 3600.0

    df["time_window"] = (elapsed_hours // interval_window).astype("int64")
    intervals = df['time_window'].max() + 1

    length_event = round((df[time_col].iloc[-1] - start_time).total_seconds() / 3600.0)

    return df, length_event, intervals  # Ojo, important the order


def is_trophy(df, run_col):
    """
    Check whether each row belongs to a trophy run (7-0) and count the total
    number of trophies in the recording.

    A trophy consists of 7 consecutive wins with no losses, so a 7-0 run
    generates exactly 7 rows in the DataFrame — the trophy count is therefore
    the raw row-count of ``'7-0'`` divided by 7.

    Args:
        df (DataFrame): Match DataFrame containing a run-result column.
        run_col (str): Name of the column with run results (e.g. ``'run_result'``).

    Returns:
        tuple:
            - df (DataFrame): Copy of the input with a new boolean-like
              ``is_trophy`` column (``'yes'`` / ``'no'``).
            - amount_trophies (float): Number of complete 7-0 trophies.
    """

    df = df.copy()
    df["is_trophy"] = df[run_col].eq("7-0").map({True: "yes", False: "no"})
    amount_trophies = df["is_trophy"].eq("yes").sum() / 7  # A trophy consists of 7 victories
    return df, amount_trophies


def mtg_prefix_normalisation(value):
    """
    Enforce the official WUBRG color-ordering on the color-prefix of a deck
    name string.

    MTG uses a canonical color order (White → Blue → Black → Red → Green,
    i.e. ``wubrg``). If the first token of ``value`` is composed entirely of
    those letters (e.g. ``'ur'``, ``'rbw'``), it is reordered to match the
    canonical sequence. Non-color prefixes are left unchanged.

    Example::

        mtg_prefix_normalisation('ur tempo')  # → 'ur tempo' (already correct)
        mtg_prefix_normalisation('ru tempo')  # → 'ur tempo'
        mtg_prefix_normalisation('bg stompy') # → 'bg stompy'

    Args:
        value (str): A deck-name string, typically lowercase.

    Returns:
        str: The same string with its color prefix reordered to WUBRG, or the
        original value if no reordering is needed.
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
    Translate Ravnica guild names and Khans/Tarkir shard/wedge names to their
    canonical WUBRG color-prefix equivalents (all lowercase).

    Handles three cases in order:
        1. A single bare color letter followed by a space and a deck tag is
           prefixed with ``'mono'`` (e.g. ``'b stompy'`` → ``'mono b stompy'``).
        2. The first token matches a two-color Ravnica guild name (defined in
           ``TWO_COLOR_GUILDS``) and is replaced by the corresponding color
           pair prefix.
        3. The first token matches a three-color Tarkir/Alara name (defined in
           ``THREE_COLOR_GUILDS``) and is replaced by the corresponding triplet.

    Example::

        mtg_guild_normalisation('izzet tempo')   # → 'ur tempo'
        mtg_guild_normalisation('sultai control') # → 'bgu control'
        mtg_guild_normalisation('b stompy')       # → 'mono b stompy'

    Args:
        value (str): A deck-name string, typically lowercase.

    Returns:
        str: The normalised deck-name string, or the original value if no
        known guild/shard name is found at the start.
    """

    if not isinstance(value, str) or not value:
        return value

    # 1) Exactly: one of wubrg, then a space, then anything
    m = re.match(r'^([wubrg])\s+(.*)$', value)
    if m:
        return f"mono {m.group(1)} {m.group(2)}".rstrip()

    # 2) / 3) Replace family name only if it is the first token
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
    Assign a broad archetype label to each row by matching the deck-name string
    in ``source_col`` against a user-supplied keyword dictionary.

    For each entry, the function checks whether any keyword associated with an
    archetype appears as a substring of the (lowercased) deck name. The first
    matching archetype wins. If no keyword matches, the row receives
    ``default_tag``.

    As the metagame shifts from event to event, the keyword dictionary is
    user-defined and should be updated accordingly.

    Example keyword dict::

        {
            'tempo':   ['tempo', 'shadow', 'canadian'],
            'aggro':   ['burn', 'zoo', 'energy'],
            'control': ['control', 'stoneblade'],
        }

    Args:
        df (DataFrame): Match DataFrame to annotate.
        source_col (str): Column whose values are matched against the keywords
            (e.g. ``'user_deck'`` or ``'oppo_deck'``).
        keyword_dict (dict): Mapping of ``{archetype_label: [keyword, ...]}``.  
            Keys are the archetype tag strings; values are lists of substrings
            to search for in the deck name.
        new_col (str): Name of the new column that will hold the archetype label.
        default_tag (str): Fallback label used when no keyword matches
            (e.g. ``'other'``).

    Returns:
        DataFrame: Copy of the input with ``new_col`` added.
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
    Normalise raw row counts into actual run counts and compute trophy totals.

    In the raw data, each game within a run occupies its own row — a ``'4-1'``
    run therefore contributes **5** rows. To recover the true number of runs,
    each value-count is divided by ``wins + losses`` for that result string.
    This is called the *normalised count*.

    Trophy runs are identified as ``'7-0'`` and counted separately: because a
    7-0 run produces 7 rows, ``amount_trophies = row_count('7-0') / 7``.

    Args:
        df (DataFrame): Match DataFrame containing a run-result column.
        run_col (str): Name of the column with run results in ``'W-L'`` format
            (e.g. ``'run_result'``).

    Returns:
        tuple:
            - df (DataFrame): Unchanged copy of the input.
            - amount_trophies (float): Number of complete 7-0 trophies.
            - types_of_run (list[str]): All distinct run strings found, sorted
              by total games then wins then losses.
            - run_counts_out (Series): Raw row counts indexed by run string.
            - normalized_run_counts (Series): Actual run counts (row count
              divided by games per run) indexed by run string.
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
    Print any list or Series as a compact multi-column table for quick visual
    inspection in a notebook or terminal.

    Items are sorted alphabetically (case-insensitive) before being arranged
    into rows of ``n_cols`` columns. Empty cells are padded with ``None``.

    Args:
        items (list | Series): Collection of string-representable values to display.
        n_cols (int, optional): Number of columns in the output table. Defaults to 4.

    Returns:
        None: Prints directly to stdout via ``print``.
    """

    items = sorted(list(items), key=str.lower)
    rows = math.ceil(len(items) / n_cols)
    padded = items + [None] * (rows * n_cols - len(items))
    table = pd.DataFrame([padded[i:i + n_cols] for i in range(0, len(padded), n_cols)])
    return print(table.to_string(index=False, header=False))

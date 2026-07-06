import math
import pandas as pd
import re

from pandas import DataFrame
from .constants import TWO_COLOR_GUILDS, THREE_COLOR_GUILDS, MONO_COLOR_WORDS


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


        mtg_guild_normalisation('izzet tempo')    # → 'ur tempo'
        mtg_guild_normalisation('sultai control') # → 'bgu control'
        mtg_guild_normalisation('b stompy')       # → 'mono b stompy'
        mtg_guild_normalisation('mono-green')     # → 'mono g'
        mtg_guild_normalisation('mono red burn')  # → 'mono r burn'


    Args:
        value (str): A deck-name string, typically lowercase.


    Returns:
        str: The normalised deck-name string, or the original value if no
        known guild/shard name is found at the start.
    """

    if not isinstance(value, str) or not value:
        return value

    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)

    # 0) Normalize spelled-out mono-color names at the start:
    # mono-green, mono green, monogreen -> mono g

    m = re.match(r"^mono[-\s]*(white|blue|black|red|green)\b(?:\s+(.*))?$", value)
    if m:
        color = MONO_COLOR_WORDS[m.group(1)]
        rest = m.group(2) or ""
        return f"mono {color} {rest}".rstrip()

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


def relabel_name(deck, dic):

    for family, aliases in dic.items():
        if deck in aliases:
            return family
    return deck


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


def drop_missing_results(df: DataFrame, result_col: str = "result_vs_oppo") -> DataFrame:
    """
    Remove rows whose match result contains the literal text 'None'.

    Args:
        df (DataFrame): Input DataFrame.
        result_col (str, optional): Column storing the match result.
            Defaults to "result_vs_oppo".

    Returns:
        DataFrame: Copy of the input without rows where ``result_col`` contains 'None'.
    """
    df_new = df.copy()
    mask = ~df_new[result_col].astype(str).str.contains("None", na=False)
    return df_new.loc[mask].copy()

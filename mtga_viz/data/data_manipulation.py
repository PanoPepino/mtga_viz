# Here you will find all required functions to manipulate the full .csv file before performing the analysis.
# Sub-functions within can be found at utils/helpers_*.py


import pandas as pd
from pandas import DataFrame

from mtga_viz.utils.tournament_helpers import build_paths, load_tournament_csv
from mtga_viz.utils.challenge_helpers import add_hour_index, count_runs
from mtga_viz.utils.common_helpers import assign_archetype, mtg_guild_normalisation, mtg_prefix_normalisation, relabel_name


def normalise_wubrg(df,
                    user_deck: str,
                    oppo_deck: str):
    """
    Apply canonical WUBRG color-ordering to the color prefix of both the
    ``user_deck`` and ``oppo_deck`` columns.

    Delegates to :func:`~mtga_viz.utils.common_helpers.mtg_prefix_normalisation` on
    each cell.  Entries whose first token is not a pure color-letter sequence
    (e.g. named decks like ``'burn'``) are left unchanged.

    Args:
        df (DataFrame): Match DataFrame with deck-name columns.
        user_deck (str): Name of the column containing the player's deck names.
        oppo_deck (str): Name of the column containing the opponent's deck names.

    Returns:
        DataFrame: Copy of ``df`` with both deck columns normalised.
    """

    df_new = df.copy()
    df_new[user_deck] = df[user_deck].apply(mtg_prefix_normalisation)
    df_new[oppo_deck] = df[oppo_deck].apply(mtg_prefix_normalisation)

    return df_new


def normalise_guild(df,
                    user_deck: str,
                    oppo_deck: str):
    """
    Replace Ravnica guild names and Tarkir wedge/shard names with their
    canonical WUBRG color-prefix equivalents in both deck columns.

    Same spirit as :func:`normalise_wubrg`, but handles named multi-color
    identities (e.g. ``'izzet'`` → ``'ur'``, ``'sultai'`` → ``'bgu'``) as
    well as bare single-color prefixes (e.g. ``'b stompy'`` → ``'mono b stompy'``).
    Delegates to :func:`~mtga_viz.utils.helpers.mtg_guild_normalisation`.

    Args:
        df (DataFrame): Match DataFrame with deck-name columns.
        user_deck (str): Name of the column containing the player's deck names.
        oppo_deck (str): Name of the column containing the opponent's deck names.

    Returns:
        DataFrame: Copy of ``df`` with both deck columns normalised.
    """

    df_new = df.copy()

    df_new[user_deck] = df[user_deck].apply(mtg_guild_normalisation)
    df_new[oppo_deck] = df[oppo_deck].apply(mtg_guild_normalisation)

    return df_new


def explore_most_played_decks(df: DataFrame,
                              user_deck_col: str,
                              oppo_deck_col: str):
    """
    Explore which deck names appear most frequently in both the user and
    opponent columns, helping you decide how to define archetype keyword
    dictionaries.

    This function is intended as an **exploratory utility**: run it on a
    cleaned DataFrame to see which specific deck names dominate before calling
    :func:`create_new_columns` with a keyword dictionary.

    Args:
        df (DataFrame): Cleaned match DataFrame (typically the output of
            :func:`clean_raw_csv`).
        user_deck_col (str): Column name for the player's deck entries.
        oppo_deck_col (str): Column name for the opponent's deck entries.

    Returns:
        tuple:
            - most_played_common (list[str]): Deck names that appear in both
              the user and opponent columns, sorted by frequency.
            - common_counts (DataFrame): A two-column table (``user_deck``,
              ``oppo_deck``) with the row-count of each common deck name.
    """

    df_new = df.copy()

    # Check how many times each deck repeats in both columns
    most_played_user = df_new[user_deck_col].value_counts()
    most_played_oppo = df_new[oppo_deck_col].value_counts()

    # Compare previous countings and extract the most common played decks in both cases
    most_played_common = most_played_user.index.intersection(most_played_oppo.index).to_list()

    # Creates a table with how many times repeat each most common deck
    common_counts = pd.concat([most_played_user, most_played_oppo], axis=1, join='inner')
    common_counts.columns = ["user_deck", "oppo_deck"]

    return most_played_common, common_counts


# -------------------------------
# MAIN DATAFRAME MODIFIERS
# -------------------------------

def clean_raw_csv(df: DataFrame,
                  user_deck_col: str,
                  oppo_deck_col: str,
                  ):
    """
    Main entry point for cleaning a raw collected ``.csv`` file before any
    analysis.

    The function performs three sequential normalisation steps:

    1. **Lowercase** — both deck columns are lowercased so that string
       comparisons are case-insensitive (``'Izzet'`` and ``'izzet'`` become
       the same entry).
    2. **WUBRG prefix normalisation** — color-letter prefixes are reordered to
       the canonical MTG sequence via :func:`normalise_wubrg`.
    3. **Guild / shard normalisation** — named multi-color identities and bare
       single-color letters are translated to color-prefix form via
       :func:`normalise_guild`.

    Args:
        df (DataFrame): Raw match DataFrame as loaded from the collected CSV.
        user_deck_col (str): Name of the column containing the player's deck names.
        oppo_deck_col (str): Name of the column containing the opponent's deck names.

    Returns:
        DataFrame: Cleaned copy of the input with both deck columns homogenised.
    """

    df_new = df.copy()

    # Important: lowercase user_deck and oppo_deck so that manipulation is easier,
    # as the inputs are strings
    df_new[[user_deck_col, oppo_deck_col]] = df_new[[user_deck_col, oppo_deck_col]].apply(lambda s: s.str.lower())

    # Then normalise WUBRG and guild names
    df_wubrg = normalise_wubrg(df_new,
                               user_deck=user_deck_col,
                               oppo_deck=oppo_deck_col)

    df_guilds = normalise_guild(df_wubrg,
                                user_deck=user_deck_col,
                                oppo_deck=oppo_deck_col)

    return df_guilds


def create_new_columns(df: DataFrame,
                       source_cols: str | list,
                       keyword_dict: dict,
                       new_cols: str | list,
                       def_tag: str,
                       time_col: str | None = None,
                       interval_window: int | None = None,
                       run_col: str | None = None,
                       add_time_window: bool = False,
                       add_run_stats: bool = False,
                       ):
    """
    Enrich a cleaned match DataFrame with additional layers of information
    required for downstream analysis.


    1. **Time window index** — an integer ``time_window`` column can be added by
       :func:`~mtga_viz.utils.helpers.add_hour_index`, bucketing each row into
       an ``interval_window``-hour slot relative to the first timestamp.
    2. **Archetype labels** — for each pair in ``source_cols`` / ``new_cols``,
       :func:`~mtga_viz.utils.helpers.assign_archetype` scans the deck-name
       column against ``keyword_dict`` and writes the matched archetype (or
       ``def_tag``) into the new column.
    3. **Run normalisation** — :func:`~mtga_viz.utils.helpers.count_runs` can be
       called to confirm run integrity; its enriched DataFrame copy is returned.


    This function is flexible enough to work with both challenge-like tables
    such as::


        message_time_stamp,user_name,run_result,user_deck,oppo_deck,result_vs_oppo


    and tournament-like tables such as::


        match_created_utc,user_deck,oppo_deck,result_vs_oppo


    Args:
        df (DataFrame): Cleaned match DataFrame, output of :func:`clean_raw_csv`.
        source_cols (str | list[str]): Column(s) whose values will be matched
            against ``keyword_dict`` to assign archetypes.
        keyword_dict (dict): Mapping of ``{archetype_label: [keyword, ...]}``,
            passed directly to :func:`~mtga_viz.utils.helpers.assign_archetype`.
        new_cols (str | list[str]): Name(s) of the new archetype columns to create.
            Must have the same length as ``source_cols``.
        def_tag (str): Default archetype label for rows that match no keyword
            (e.g. ``'other'``).
        time_col (str | None, optional): Name of the timestamp column used to
            build the time index. Defaults to None.
        interval_window (int | None, optional): Bucket size in hours for the
            time window index. Defaults to None.
        run_col (str | None, optional): Name of the column containing run results
            (e.g. ``'run_result'``). Defaults to None.
        add_time_window (bool, optional): Whether to create the ``time_window``
            column. Defaults to False.
        add_run_stats (bool, optional): Whether to run ``count_runs`` enrichment.
            Defaults to False.


    Returns:
        DataFrame: Enriched copy of the input with archetype columns, and
        optionally ``time_window`` and run-integrity fields.


    Raises:
        ValueError: If ``source_cols`` and ``new_cols`` have different lengths.
        ValueError: If ``add_time_window=True`` but ``time_col`` or
            ``interval_window`` is missing.
        ValueError: If ``add_run_stats=True`` but ``run_col`` is missing.
    """

    df_new = df.copy()

    # First, add a column with an hour index to track all the hours of the event
    if add_time_window:
        if time_col is None or interval_window is None:
            raise ValueError("time_col and interval_window must be provided when add_time_window=True")
        df_w_hour_index, _, _ = add_hour_index(df_new, time_col, interval_window)
    else:
        df_w_hour_index = df_new

    # Then, assign the archetypes to both the user and oppo decks.
    # This creates the requested new columns.
    sources = [source_cols] if isinstance(source_cols, str) else list(source_cols)
    news = [new_cols] if isinstance(new_cols, str) else list(new_cols)

    if len(sources) != len(news):
        raise ValueError("source_cols and new_cols must have the same length")

    df_w_arch = df_w_hour_index

    for source, new in zip(sources, news):
        df_w_arch = assign_archetype(df_w_arch, source, keyword_dict, new, def_tag)

    # Finally, check what are trophies and not
    if add_run_stats:
        if run_col is None:
            raise ValueError("run_col must be provided when add_run_stats=True")
        df_w_trophy, _, _, _, _ = count_runs(df_w_arch, run_col)
        return df_w_trophy

    return df_w_arch


def load_and_merge_data(
    tournament_directory=None,
    league_directory=None,
    tournament_files=None,
    league_files=None,
) -> pd.DataFrame:
    """
    Function that loads all necessary information coming from different tournaments and league. It uses :func:`build_paths` to create proper paths for all files. For tournament files, it will mirror results, for easier match matrix computation later.

    Args:
        tournament_directory (str): Defaults to None.
        league_directory (str): Defaults to None.
        tournament_files (list[str]): Defaults to None.
        league_files (list[str]): Defaults to None.

    Returns:
        pd.DataFrame:The dataframe with all matches merged and mirroed if they belong to tournament files
    """

    tournament_paths = build_paths(tournament_directory, tournament_files)
    league_paths = build_paths(league_directory, league_files)

    parts = []

    for path in tournament_paths:
        parts.append(load_tournament_csv(path))

    for path in league_paths:
        parts.append(pd.read_csv(path))

    if not parts:
        return pd.DataFrame(columns=[
            "match_created_utc",
            "user_deck",
            "oppo_deck",
            "result_vs_oppo",
        ])

    return pd.concat(parts, ignore_index=True)


def relabel_decks(df,
                  user_col,
                  oppo_col,
                  new_names) -> DataFrame:
    """
    Simple function to group decks under some labels:
    ex: ['ub tempo', 'ubr tempo' , 'wub tempo'] -> 'ub tempo'

    Args:
        df (_type_): 
        user_col (str): the user_deck column
        oppo_col (str): the oppo_deck column
        new_names (dict): the dictionary to substitute names

    Returns:
        DataFrame: 
    """

    df_new = df.copy()
    df_new[user_col] = df_new[user_col].apply(relabel_name, args=(new_names,))
    df_new[oppo_col] = df_new[oppo_col].apply(relabel_name, args=(new_names,))

    return df_new

# Here you will find all required functions to manipulate the full .csv file before performing the analysis.
# Sub-functions within can be found at utils/helpers_*.py

import pandas as pd
from pandas import DataFrame

from mtga_viz.utils.tournament_helpers import build_paths, load_tournament_csv
from mtga_viz.utils.challenge_helpers import add_hour_index, count_runs
from mtga_viz.utils.common_helpers import (
    assign_archetype,
    drop_missing_results,
    mtg_guild_normalisation,
    mtg_prefix_normalisation,
    relabel_name,
)


def normalise_wubrg(df: DataFrame,
                    deck_cols: str | list[str]) -> DataFrame:
    """
    Apply canonical WUBRG color-ordering to one or more deck-name columns.

    Delegates to :func:`~mtga_viz.utils.common_helpers.mtg_prefix_normalisation`
    on each selected deck column. Entries whose first token is not a pure
    color-letter sequence (e.g. named decks like ``'burn'``) are left unchanged.

    Args:
        df (DataFrame): DataFrame with deck-name columns.
        deck_cols (str | list[str]): One or more deck-name columns to normalise.

    Returns:
        DataFrame: Copy of ``df`` with the requested deck columns normalised.
    """

    df_new = df.copy()
    cols = [deck_cols] if isinstance(deck_cols, str) else list(deck_cols)

    for col in cols:
        df_new[col] = df_new[col].apply(mtg_prefix_normalisation)

    return df_new


def normalise_guild(df: DataFrame,
                    deck_cols: str | list[str]) -> DataFrame:
    """
    Replace guild, shard, wedge, and bare single-color names with their
    canonical WUBRG color-prefix equivalents in one or more deck-name columns.

    Same spirit as :func:`normalise_wubrg`, but handles named multi-color
    identities (e.g. ``'izzet'`` → ``'ur'``, ``'sultai'`` → ``'bgu'``) as
    well as bare single-color prefixes (e.g. ``'b stompy'`` → ``'mono b stompy'``).
    Delegates to :func:`~mtga_viz.utils.common_helpers.mtg_guild_normalisation`.

    Args:
        df (DataFrame): DataFrame with deck-name columns.
        deck_cols (str | list[str]): One or more deck-name columns to normalise.

    Returns:
        DataFrame: Copy of ``df`` with the requested deck columns normalised.
    """

    df_new = df.copy()
    cols = [deck_cols] if isinstance(deck_cols, str) else list(deck_cols)

    for col in cols:
        df_new[col] = df_new[col].apply(mtg_guild_normalisation)

    return df_new


def explore_most_played_decks(
    df: DataFrame,
    deck_col: str | list[str],
) -> tuple[list[str], DataFrame]:
    df_new = df.copy()
    cols = [deck_col] if isinstance(deck_col, str) else list(deck_col)

    missing_cols = [col for col in cols if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"Missing deck columns: {missing_cols}")

    all_decks = pd.concat([df_new[col] for col in cols], axis=0)

    counts = all_decks.value_counts().reset_index()
    counts.columns = [deck_col if isinstance(deck_col, str) else "deck_col", "count"]

    most_played_common = counts.iloc[:, 0].to_list()

    return most_played_common, counts


# -------------------------------
# MAIN DATAFRAME MODIFIERS
# -------------------------------


def clean_raw_csv(df: DataFrame,
                  deck_cols: str | list[str],
                  result_col: str = "result_vs_oppo") -> DataFrame:
    """
    Main entry point for cleaning a raw collected ``.csv`` file before any
    analysis.

    This function only applies cleaning to deck-name columns, and can be used
    for either a match CSV or a registration CSV.

    The function performs four sequential normalisation steps:

    1. **Drop invalid results** — if ``result_col`` exists, rows whose
       ``result_col`` contains the literal text ``'None'`` are removed.
    2. **Lowercase** — all selected deck columns are lowercased so that string
       comparisons are case-insensitive.
    3. **WUBRG prefix normalisation** — color-letter prefixes are reordered to
       the canonical MTG sequence via :func:`normalise_wubrg`.
    4. **Guild / shard normalisation** — named multi-color identities and bare
       single-color letters are translated to color-prefix form via
       :func:`normalise_guild`.

    Args:
        df (DataFrame): Raw DataFrame as loaded from the collected CSV.
        deck_cols (str | list[str]): One or more deck-name columns to clean.
        result_col (str, optional): Name of the result column. If this column
            does not exist, result filtering is skipped. Defaults to
            ``"result_vs_oppo"``.

    Returns:
        DataFrame: Cleaned copy of the input with requested deck columns
        homogenised.

    Raises:
        ValueError: If any requested deck column is missing from the DataFrame.
    """

    df_new = df.copy()
    cols = [deck_cols] if isinstance(deck_cols, str) else list(deck_cols)

    missing_cols = [col for col in cols if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"Missing deck columns: {missing_cols}")

    if result_col in df_new.columns:
        df_new = drop_missing_results(df_new, result_col=result_col)

    df_new[cols] = df_new[cols].apply(lambda s: s.str.lower())

    df_wubrg = normalise_wubrg(df_new, deck_cols=cols)
    df_guilds = normalise_guild(df_wubrg, deck_cols=cols)

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

    # Then, assign the archetypes to the requested source columns.
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


def load_and_merge_deck_data(
    tournament_directory=None,
    league_directory=None,
    tournament_files=None,
    league_files=None,
) -> pd.DataFrame:
    """
    Load and merge deck-registration CSV files coming from tournaments and leagues.

    Unlike match CSV loading, this function does not call ``load_tournament_csv``.
    It simply reads the raw ``_decks.csv`` files and concatenates them into a
    single DataFrame.

    Expected schema:
        player_name,deck_name

    Args:
        tournament_directory (str): Defaults to None.
        league_directory (str): Defaults to None.
        tournament_files (list[str]): Defaults to None.
        league_files (list[str]): Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with all deck registrations merged together.
    """

    tournament_paths = build_paths(tournament_directory, tournament_files)
    league_paths = build_paths(league_directory, league_files)

    parts = []

    for path in tournament_paths:
        parts.append(pd.read_csv(path))

    for path in league_paths:
        parts.append(pd.read_csv(path))

    if not parts:
        return pd.DataFrame(columns=[
            "player_name",
            "deck_name",
        ])

    return pd.concat(parts, ignore_index=True)


def relabel_decks(df: DataFrame,
                  deck_cols: str | list[str],
                  new_names: dict) -> DataFrame:
    """
    Group deck names under shared labels for one or more deck-name columns.

    Example:
        ['ub tempo', 'ubr tempo', 'wub tempo'] -> 'ub tempo'

    Args:
        df (DataFrame): Input DataFrame.
        deck_cols (str | list[str]): One or more deck-name columns to relabel.
        new_names (dict): Dictionary used to substitute / group deck names.

    Returns:
        DataFrame: Copy of the input with the requested deck columns relabelled.

    Raises:
        ValueError: If any requested deck column is not present in ``df``.
    """

    df_new = df.copy()
    cols = [deck_cols] if isinstance(deck_cols, str) else list(deck_cols)

    missing_cols = [col for col in cols if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"Missing deck columns: {missing_cols}")

    for col in cols:
        df_new[col] = df_new[col].apply(relabel_name, args=(new_names,))

    return df_new

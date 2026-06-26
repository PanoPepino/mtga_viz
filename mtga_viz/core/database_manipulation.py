import pandas as pd
from pandas import DataFrame
from ..utils.helpers import add_hour_index, assign_archetype, count_runs, mtg_guild_normalisation, mtg_prefix_normalisation

# Here you will find all required functions to manipulate the full .csv file before performing the analysis.
# Sub-functions within can be found at utils/helpers.py


def normalise_wubrg(df,
                    user_deck: str,
                    oppo_deck: str):
    """
    Apply canonical WUBRG color-ordering to the color prefix of both the
    ``user_deck`` and ``oppo_deck`` columns.

    Delegates to :func:`~mtga_viz.utils.helpers.mtg_prefix_normalisation` on
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
                       time_col: str,
                       interval_window: int,
                       run_col: str,
                       source_cols: str | list,
                       keyword_dict: dict,
                       new_cols: str | list,
                       def_tag: str
                       ):
    """
    Enrich a cleaned match DataFrame with three additional layers of information
    required for downstream analysis:

    1. **Time window index** — an integer ``time_window`` column is added by
       :func:`~mtga_viz.utils.helpers.add_hour_index`, bucketing each row into
       an ``interval_window``-hour slot relative to the first timestamp.
    2. **Archetype labels** — for each pair in ``source_cols`` / ``new_cols``,
       :func:`~mtga_viz.utils.helpers.assign_archetype` scans the deck-name
       column against ``keyword_dict`` and writes the matched archetype (or
       ``def_tag``) into the new column.
    3. **Run normalisation** — :func:`~mtga_viz.utils.helpers.count_runs` is
       called to confirm run integrity; its enriched DataFrame copy is returned.

    This is typically the **second step** in the pipeline, called after
    :func:`clean_raw_csv`::

        df_clean = clean_raw_csv(df, user_deck_col='user_deck', oppo_deck_col='oppo_deck')
        df_enriched, trophies, run_counts, length_event, intervals = create_new_columns(
            df_clean,
            time_col='message_time_stamp',
            interval_window=1,
            run_col='run_result',
            source_cols=['user_deck', 'oppo_deck'],
            keyword_dict=dictionaries,
            new_cols=['user_deck_arch', 'oppo_deck_arch'],
            def_tag='other',
        )

    Args:
        df (DataFrame): Cleaned match DataFrame, output of :func:`clean_raw_csv`.
        time_col (str): Name of the timestamp column used to build the time index.
        interval_window (int): Bucket size in hours for the time window index.
        run_col (str): Name of the column containing run results (e.g. ``'run_result'``).
        source_cols (str | list[str]): Column(s) whose values will be matched
            against ``keyword_dict`` to assign archetypes.
        keyword_dict (dict): Mapping of ``{archetype_label: [keyword, ...]}``,
            passed directly to :func:`~mtga_viz.utils.helpers.assign_archetype`.
        new_cols (str | list[str]): Name(s) of the new archetype columns to create.
            Must have the same length as ``source_cols``.
        def_tag (str): Default archetype label for rows that match no keyword
            (e.g. ``'other'``).

    Returns:
        DataFrame: Enriched copy of the input with ``time_window``, archetype
        columns, and the run-integrity fields added by ``count_runs``.

    Raises:
        ValueError: If ``source_cols`` and ``new_cols`` have different lengths.
    """

    df_new = df.copy()

    # First, add a column with an hour index to track all the hours of the event
    df_w_hour_index, _, _ = add_hour_index(df_new, time_col, interval_window)

    # Then, assign the archetypes to both the user and oppo decks.
    # This creates two new columns.
    sources = [source_cols] if isinstance(source_cols, str) else list(source_cols)
    news = [new_cols] if isinstance(new_cols, str) else list(new_cols)

    if len(sources) != len(news):
        raise ValueError("source_cols and new_cols must have the same length")

    df_w_arch = df_w_hour_index

    for source, new in zip(sources, news):
        df_w_arch = assign_archetype(df_w_hour_index, source, keyword_dict, new, def_tag)

    # Finally, check what are trophies and not
    df_w_trophy, _, _, _, _ = count_runs(df_w_arch, run_col)

    return df_w_trophy

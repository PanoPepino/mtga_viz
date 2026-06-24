import pandas as pd
from pandas import DataFrame
from ..utils.helpers import add_hour_index, assign_archetype, count_runs, mtg_guild_normalisation, mtg_prefix_normalisation

# Here you will find all required functions to manipulate the full .csv file beforing performing the analysis. Subfunctions within can be found at utils/helpers.py


def normalise_wubrg(df,
                    user_deck: str,
                    oppo_deck: str):
    """
    Take both user_deck and oppo_deck columns and apply WUBRG ordering it that acronym exists.
    """

    df_new = df.copy()
    df_new[user_deck] = df[user_deck].apply(mtg_prefix_normalisation)
    df_new[oppo_deck] = df[oppo_deck].apply(mtg_prefix_normalisation)

    return df_new


def normalise_guild(df,
                    user_deck: str,
                    oppo_deck: str):
    """
    Same spirit as previous function, but with guild names (mono color, dual-ravnica guilds and triple-tarkir guilds)
    """

    df_new = df.copy()

    df_new[user_deck] = df[user_deck].apply(mtg_guild_normalisation)
    df_new[oppo_deck] = df[oppo_deck].apply(mtg_guild_normalisation)

    return df_new


def explore_most_played_decks(df: DataFrame,
                              user_deck_col: str,
                              oppo_deck_col: str):
    """
    This function will help you explore what the most repeated decks, for both user and oppo, so that you can decide how to set the archetype tags (i.e. which decks go to each archetype).

    Returns: the list of the most played decks in both user and oppo and a table with counting of the most repeated entries common to both user and oppo.
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
    This is the main function to clean the .csv you have collected. It aims to homogenise the inputs of user and oppo decks, avoiding things like some entries being izzet and other ur or ru and so on
    """

    df_new = df.copy()

    # Important, lowercase user_deck and oppo_deck, so that manipulation is easier, as the inputs are strings
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

    df_new = df.copy()

    # First, add a column with an hour index to track all the hours of the event
    df_w_hour_index, length_event, intervals = add_hour_index(df_new, time_col, interval_window)

    # Then, assign the archetypes to both the user and oppo decks. This creates two new columns

    sources = [source_cols] if isinstance(source_cols, str) else list(source_cols)
    news = [new_cols] if isinstance(new_cols, str) else list(new_cols)

    if len(sources) != len(news):
        raise ValueError("source_cols and new_cols must have the same length")

    df_w_arch = df_w_hour_index

    for source, new in zip(sources, news):
        df_w_arch = assign_archetype(df_w_arch, source, keyword_dict, new, def_tag)

    # Finally, check what are trophies and not
    df_w_trophy, amount_trophies, types_of_run, _, normalised_run_counts = count_runs(df_w_arch, run_col)

    return df_w_trophy, length_event, intervals, amount_trophies, normalised_run_counts

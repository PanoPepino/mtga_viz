import pandas as pd
import numpy as np
from pandas import DataFrame

from statsmodels.stats.proportion import proportion_confint
from mtga_viz.utils.helpers import count_runs, add_hour_index


def get_table_wr_error(df: DataFrame,
                       result_col: str,  # The column with the results
                       study_col: str,  # The column to study (user_deck or user_deck_arch)
                       alpha=0.05) -> DataFrame:
    """
    Given a Dataframe and a column of study, explore the overall win rate, statistical error and confidence level of the results.

    Args:
        df (DataFrame): The dataframe to pass. Probably the most general one.
        result_col (str): The column where the results (2-0, 2-1, etc) are.
        study_col (str): The column (user_deck or user_deck_archetype) to analyse.

    Returns:
        DataFrame: for each unique element in study col, get columns: study_col, matches_played, wr, error, confidence
    """

    # Parse the wins and losses and group
    win_tbl = (
        df.assign(
            wins=df[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")[0].astype(float),
            losses=df[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")[1].astype(float),
        )
        .assign(won_match=lambda x: x["wins"] > x["losses"])
        .groupby(study_col, as_index=False)
        .agg(
            matches_played=("won_match", "count"),
            matches_won=("won_match", "sum")
        )
    )

    # Compute the win rate
    win_tbl["wr"] = 100 * win_tbl["matches_won"] / win_tbl["matches_played"]

    # Compute the error given your confidence proportionaly (we are looking at 95%)
    ci = win_tbl.apply(
        lambda r: proportion_confint(
            count=int(r["matches_won"]),
            nobs=int(r["matches_played"]),
            alpha=alpha,
            method="wilson"
        ),
        axis=1,
        result_type="expand"
    )

    # Table manipulation
    win_tbl["wr_low"] = 100 * ci[0]
    win_tbl["wr_high"] = 100 * ci[1]
    win_tbl["wr_error"] = (win_tbl["wr_high"] - win_tbl["wr_low"]) / 2

    win_tbl["confidence"] = pd.cut(
        win_tbl["matches_played"],
        bins=[0, 19, 49, 75, float("inf")],
        labels=["very low", "low", "medium", "high"]
    )

    win_tbl["wr"] = win_tbl["wr"].round(1)
    win_tbl["wr_low"] = win_tbl["wr_low"].round(1)
    win_tbl["wr_high"] = win_tbl["wr_high"].round(1)
    win_tbl["wr_error"] = win_tbl["wr_error"].round(1)
    table_wr = (win_tbl[[study_col, 'matches_played', 'wr', 'wr_error', 'confidence']]
                ).sort_values("matches_played", ascending=False)

    return table_wr


def get_table_runs(df: DataFrame,
                   user_deck_col: str = "user_deck",
                   run_col: str = 'run_result',
                   new_run_col_names: dict = None  # How to call the set of columns with the run iterations
                   ):
    """
    This function will take the clean and column added match dataframe and extract the relevant counting of runs, games played and different wins

    Args:
        df (DataFrame): 
        user_deck_col (str, optional): Defaults to "user_deck".
        run_col (str, optional): Defaults to 'run_result'.
        new_run_col_names (dict, optional): Defaults to None

    Returns:
        table_runs: The table with information about the runs.
    """

    # Set a simple dict to substitute string results of type X-Y to just the number of wins
    if new_run_col_names is None:
        new_run_col_names = {'0-1': '0_win',
                             '1-1': '1_win',
                             '2-1': '2_win',
                             '3-1': '3_win',
                             '4-1': '4_win',
                             '5-1': '5_win',
                             '6-1': '6_win',
                             '7-0': '7_win'}

    # Create empty list for each deck
    deck_rows = []

    # Group by the dataframe per type of user deck
    for deck, g in df.groupby(user_deck_col):
        g_out, _, _, _, normalised_run_counts = count_runs(g, run_col)
        deck_rows.append({
            "user_deck_arch": g['user_deck_arch'].iloc[0],
            "user_deck": deck,
            "total_runs": int(normalised_run_counts.sum()),
            "games_played": g_out[g_out[user_deck_col] == deck].value_counts().sum(),
            **normalised_run_counts.fillna(0).to_dict(),
        })

    # Create the dataframe
    table_runs = pd.DataFrame(deck_rows)

    # Manipulate the dataframe
    table_runs.rename(columns=new_run_col_names, inplace=True)

    table_runs = (
        table_runs
        .sort_values("total_runs", ascending=False)
        .reset_index(drop=True)
        .reindex(columns=["user_deck_arch", "user_deck", "total_runs", "games_played", *new_run_col_names.values()])
        .fillna(0))

    table_runs[table_runs.columns.drop(["user_deck_arch", "user_deck"])] = table_runs[table_runs.columns.drop([
        "user_deck_arch", "user_deck"])].astype(int)

    return table_runs


def get_table_event_summary(
        df: DataFrame,
        user_name_col="user_name",
        run_col="run_result",
        result_col="result_vs_oppo",
        time_col="message_time_stamp",
        interval_window=1):
    """
    This function will return a simple summary of the event, with the amount of participating players, run and game counters, overall winrate and different runs counters.

    Args:
        df (DataFrame): The clean and enhanced dataframe.
        user_name_col (str, optional): The column with user names info. Defaults to "user_name".
        run_col (str, optional): Defaults to "run_result".
        result_col (str, optional): Column with 2-0, 2-1 and so on results. Defaults to "result_vs_oppo".
        time_col (str, optional): Defaults to "message_time_stamp".
        interval_window (int, optional): Defaults to 1.

    Returns:
        Series:
    """

    df_time, length_event, _ = add_hour_index(
        df, time_col=time_col, interval_window=interval_window
    )

    _, _, _, _, normalized_run_counts = count_runs(df_time, run_col)

    parsed = df_time[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")
    wins = pd.to_numeric(parsed[0], errors="coerce")
    losses = pd.to_numeric(parsed[1], errors="coerce")
    valid = wins.notna() & losses.notna()

    matches_played = int(valid.sum())
    matches_won = int((wins[valid] > losses[valid]).sum())
    overall_winrate = round(100 * matches_won / matches_played, 1) if matches_played else 0.0

    table_event = pd.Series({
        "players": df_time[user_name_col].nunique(),
        "runs": int(normalized_run_counts.sum()),
        "games": len(df_time),
        "overall_winrate": overall_winrate,
        **normalized_run_counts.to_dict(),
        "event_duration": length_event,
    })

    table_event.loc[table_event.index != "overall_winrate"] = (
        table_event.loc[table_event.index != "overall_winrate"].astype(int)
    )

    return table_event


def get_window_deck_table(
    df: pd.DataFrame,
    time_col: str = "time_window",
    deck_col: str = "user_deck",
    run_col: str = "run_result",
    top_n: int = 20,
    other_label: str = "other",
) -> pd.DataFrame:
    """
    For each time_window, this function will do the following:
    - Keep the top N decks by whole-event game share
    - Gather all other decks into the tag 'other_label'
    - Compute each group's share of games inside that time_window
    - Compute % of games in that time_window with respect the total amount of games
    - count 7-0 trophies for each group in that time_window

    Args:
        df (pd.DataFrame): 
        time_col (str, optional): Defaults to "time_window".
        deck_col (str, optional): Defaults to "user_deck".
        run_col (str, optional): Defaults to "run_result".
        top_n (int, optional): Defaults to 20.
        other_label (str, optional): Defaults to "other".

    Returns:
        pd.DataFrame: 
    """

    # Top N decks by whole-event game share
    global_decks = df.groupby(deck_col).size().reset_index(name="event_games")
    global_decks["event_share"] = (
        global_decks["event_games"] / global_decks["event_games"].sum() * 100
    )
    top_decks = set(
        global_decks.sort_values("event_share", ascending=False)
        .head(top_n)[deck_col]
    )

    # Collapse non-top decks into 'other'
    df2 = df.copy()
    df2["deck"] = df2[deck_col].where(df2[deck_col].isin(top_decks), other_label)

    # Aggregate by time window and grouped deck
    table = (
        df2.groupby([time_col, "deck"], as_index=False)
        .agg(
            games=(deck_col, "size"),
            trophy=(run_col, lambda s: int(s.eq("7-0").sum() / 7)),
        )
    )

    # Compute total games and share within each interval
    table["total_games_in_interval"] = table.groupby(time_col)["games"].transform("sum")
    table["share"] = (100 * table["games"] / table["total_games_in_interval"]).round(1)
    table['share_games_total'] = (100*table["total_games_in_interval"]/len(df[deck_col])).round(1)

    return (
        table[[time_col, "deck", "share", 'share_games_total', "trophy"]]
        .sort_values([time_col, "share"], ascending=[True, False])
        .reset_index(drop=True)
    )

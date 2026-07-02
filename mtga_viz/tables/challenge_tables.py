# This file contains relevant tables for computing data from Metagame Challenge resources

import pandas as pd
import numpy as np
from pandas import DataFrame

from mtga_viz.utils.challenge_helpers import count_runs, add_hour_index


def get_table_runs(df: DataFrame,
                   user_deck_col: str = "user_deck",
                   run_col: str = 'run_result',
                   new_run_col_names: dict = None
                   ):
    """
    Summarise run performance per deck: total runs, games played, and a
    breakdown of how many runs of each type (``'0-1'``, ``'1-1'``, …,
    ``'7-0'``) each deck completed.

    Run counts are *normalised* — each row count is divided by the number of
    games that make up that run result — so the figures represent actual
    completed runs rather than raw row counts. See
    :func:`~mtga_viz.utils.helpers.count_runs` for the normalisation logic.

    Args:
        df (DataFrame): Enriched match DataFrame (output of
            :func:`~mtga_viz.core.database_manipulation.create_new_columns`).
        user_deck_col (str, optional): Column grouping rows by deck.
            Defaults to ``'user_deck'``.
        run_col (str, optional): Column with run results in ``'W-L'`` format.
            Defaults to ``'run_result'``.
        new_run_col_names (dict, optional): Mapping from raw run-result strings
            to human-friendly column names, e.g.
            ``{'7-0': '7_win', '6-1': '6_win', ...}``.  
            If ``None``, a default mapping covering ``'0-1'`` through ``'7-0'``
            is used.

    Returns:
        DataFrame: One row per deck, sorted descending by ``total_runs``,
        with columns:

        - ``user_deck_arch`` — archetype label of the deck.
        - ``user_deck`` — specific deck name.
        - ``total_runs`` — sum of all normalised run counts.
        - ``games_played`` — total number of individual game rows.
        - One column per run type (renamed via ``new_run_col_names``).
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
    Return a high-level summary of the entire event as a labelled Series.

    Combines three helpers to produce a single-row snapshot:

    - :func:`~mtga_viz.utils.helpers.add_hour_index` — for event duration.
    - :func:`~mtga_viz.utils.helpers.count_runs` — for run breakdown.
    - Direct parsing of ``result_col`` — for overall win rate.

    All fields except ``overall_winrate`` are cast to ``int``.

    Args:
        df (DataFrame): Enriched match DataFrame (output of
            :func:`~mtga_viz.core.database_manipulation.create_new_columns`).
        user_name_col (str, optional): Column with participant usernames, used
            to count unique players. Defaults to ``'user_name'``.
        run_col (str, optional): Column with run results. Defaults to
            ``'run_result'``.
        result_col (str, optional): Column with individual match results in
            ``'W-L'`` format. Defaults to ``'result_vs_oppo'``.
        time_col (str, optional): Timestamp column forwarded to
            :func:`~mtga_viz.utils.helpers.add_hour_index`.
            Defaults to ``'message_time_stamp'``.
        interval_window (int, optional): Hour-bucket width forwarded to
            :func:`~mtga_viz.utils.helpers.add_hour_index`. Defaults to ``1``.

    Returns:
        Series: Named scalar fields:

        - ``players`` — number of unique participants.
        - ``runs`` — total number of completed runs (normalised).
        - ``games`` — total number of game rows.
        - ``overall_winrate`` — event-wide win rate in percent (float).
        - One entry per distinct run type (e.g. ``'4-1'``, ``'7-0'``) with its
          normalised run count.
        - ``event_duration`` — total event length in whole hours.
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


def get_table_window_deck(
    df: pd.DataFrame,
    time_col: str = "time_window",
    deck_col: str = "user_deck",
    run_col: str = "run_result",
    top_n: int = 20,
    other_label: str = "other",
) -> pd.DataFrame:
    """
    Build a per-time-window deck-popularity table, keeping the top ``N`` decks
    by whole-event game share and collapsing the rest into ``other_label``.

    Game share is used (rather than run share) because each game row belongs
    to exactly one ``time_window``, avoiding any double-counting across
    intervals that run-normalised counts could introduce.

    For each ``time_window`` the function computes:

    - The share (%) of games that each top-N deck (or the ``other`` bucket)
      accounts for within that interval.
    - The share (%) of total-event games that the interval itself represents
      (``share_games_total``), useful for spotting high/low-activity periods.
    - The number of completed 7-0 trophy runs per deck group per interval.

    Args:
        df (pd.DataFrame): Enriched match DataFrame (output of
            :func:`~mtga_viz.core.database_manipulation.create_new_columns`).
            Must contain a ``time_window`` integer column produced by
            :func:`~mtga_viz.utils.helpers.add_hour_index`.
        time_col (str, optional): Name of the time-bucket column.
            Defaults to ``'time_window'``.
        deck_col (str, optional): Column whose values represent deck names.
            Defaults to ``'user_deck'``.
        run_col (str, optional): Column with run results used to count trophies.
            Defaults to ``'run_result'``.
        top_n (int, optional): Number of most-played decks (by whole-event game
            share) to track individually. All other decks are merged into
            ``other_label``. Defaults to ``20``.
        other_label (str, optional): Label assigned to the catch-all bucket of
            decks outside the top ``N``. Defaults to ``'other'``.

    Returns:
        pd.DataFrame: Sorted by ``time_window`` ascending, then ``share``
        descending, with columns:

        - ``time_window`` — integer hour bucket.
        - ``deck`` — deck name or ``other_label``.
        - ``share`` — percentage of games in this interval played by this deck group.
        - ``share_games_total`` — percentage of all event games that occurred
          in this interval.
        - ``trophy`` — number of completed 7-0 runs for this deck group in
          this interval.
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
    table['share_games_total'] = (100 * table["total_games_in_interval"] / len(df[deck_col])).round(1)

    return (
        table[[time_col, "deck", "share", 'share_games_total', "trophy"]]
        .sort_values([time_col, "share"], ascending=[True, False])
        .reset_index(drop=True)
    )

import pandas as pd


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

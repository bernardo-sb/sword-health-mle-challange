from pathlib import Path

import duckdb
import pandas as pd
from message.config import DATA_DIR, QUERIES_DIR
from message.io import load_exercise_data
from message.transform import (
    aggregate_session_data,
    calculate_performance_metrics,
    add_reason_counts,
    identify_problematic_exercises,
    order_columns,
)

def open_query(query_filename: Path, **kwargs) -> str:
    """Opens a query file and formats it with the provided kwargs.

    Parameters
    ----------
    query_filename : Path
        Name of the query file to open.

    Returns
    -------
    str
        The query file content formatted with the provided kwargs.
    """
    return open(query_filename, "r").read().format(**kwargs)


def transform_features_sql():
    """Loads the exercise results and transforms
    them into features using the features.sql query.
    """
    exercise = pd.read_parquet(
        Path(DATA_DIR, "exercise_results.parquet")
    )  # noqa

    query = open_query(Path(QUERIES_DIR, "features.sql"))

    session = duckdb.sql(query).df()

    session.to_parquet(Path(DATA_DIR, "features.parquet"))


def transform_features_py() -> pd.DataFrame:
    """Loads the exercise results and transforms them into features.
    
    Returns
    -------
    pd.DataFrame
        The transformed features.
    """

    df = load_exercise_data(DATA_DIR)
    grouped = aggregate_session_data(df)
    grouped = calculate_performance_metrics(grouped)
    grouped = add_reason_counts(df, grouped)
    # grouped = identify_problematic_exercises(df, grouped)
    # grouped = order_columns(grouped)

    return grouped


def get_features(session_group: str) -> dict:
    """Gets the features for a given session group.

    Parameters
    ----------
    session_group : str
        Session group to filter the features.

    Returns
    -------
    dict
        The features for the given session group in a dict format.
    """
    session = pd.read_parquet(Path(DATA_DIR, "features_expected.parquet"))

    return session[session["session_group"] == session_group].to_dict(
        orient="records"
    )

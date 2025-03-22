from pathlib import Path

import duckdb
import pandas as pd
from message.config import DATA_DIR, QUERIES_DIR


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
    df = pd.read_parquet(Path(DATA_DIR, "exercise_results.parquet"))

    grouped = df.groupby("session_group").agg(
        patient_id=("patient_id", "first"),
        patient_name=("patient_name", "first"),
        patient_age=("patient_age", "first"),
        pain=("pain", "first"),
        fatigue=("fatigue", "first"),
        therapy_name=("therapy_name", "first"),
        session_number=("session_number", "first"),
        leave_session=("leave_session", "first"),
        quality=("quality", "first"),
        session_is_nok=("session_is_nok", "first"),
        prescribed_repeats=("prescribed_repeats", "sum"),
        training_time=("training_time", "sum"),
        correct_repeats=("correct_repeats", "sum"),
        wrong_repeats=("wrong_repeats", "sum"),
        number_exercises=("exercise_name", "count"),
        number_of_distinct_exercises=("exercise_name", "nunique"),
    ).reset_index()
    
    grouped.set_index("session_group", inplace=True)

    grouped["perc_correct_repeats"] = grouped["correct_repeats"] / (grouped["correct_repeats"] + grouped["wrong_repeats"])
    
    leave_exercise_reasons = ["system_problem", "other", "unable_perform", "pain", "tired", "technical_issues", "difficulty"]
    quality_reasons = ["movement_detection", "my_self_personal", "other", "exercises", "tablet", "tablet_and_or_motion_trackers", "easy_of_use", "session_speed"]

    for reason in leave_exercise_reasons:
        grouped[f"leave_exercise_{reason}"] = df[df["leave_exercise"] == reason].groupby("session_group")["leave_exercise"].count()
        grouped[f"leave_exercise_{reason}"].fillna(0, inplace=True)
    for reason in quality_reasons:
        grouped[f"quality_{reason}"] = df[df["quality"] == reason].groupby("session_group")["quality"].count()
        grouped[f"quality_{reason}"].fillna(0, inplace=True)


    grouped["session_is_nok"] = grouped["session_is_nok"].fillna(False)
    
    df_nonzero_wrong = df[df["wrong_repeats"] > 0]
    if not df_nonzero_wrong.empty:
        most_incorrect = df_nonzero_wrong.loc[df_nonzero_wrong.groupby("session_group")["wrong_repeats"].idxmax(), 
                                            ["session_group", "exercise_name"]]
    else:
        most_incorrect = pd.DataFrame(columns=["session_group", "exercise_name"])  # Empty DataFrame to merge

    grouped = grouped.merge(most_incorrect, on="session_group", how="left")
    grouped.rename(columns={"exercise_name": "exercise_with_most_incorrect"}, inplace=True)

    skipped_exercises = df[df["leave_exercise"].notnull()].sort_values(by=["session_group", "exercise_order"])
    first_skipped = skipped_exercises.groupby("session_group").first().reset_index()[["session_group", "exercise_name"]]
    grouped = grouped.merge(first_skipped, on="session_group", how="left")
    grouped.rename(columns={"exercise_name": "first_exercise_skipped"}, inplace=True)
    
    columns_order = [
        "session_group",
        "patient_id",
        "patient_name",
        "patient_age",
        "pain",
        "fatigue",
        "therapy_name",
        "session_number",
        "leave_session",
        "quality",
        * grouped.columns[grouped.columns.str.startswith("quality_reason_")],
        "session_is_nok",
        * grouped.columns[grouped.columns.str.startswith("leave_exercise_")],
        "prescribed_repeats",
        "training_time",
        "perc_correct_repeats",
        "number_exercises",
        "number_of_distinct_exercises",
        "exercise_with_most_incorrect",
        "first_exercise_skipped",
    ]

    return grouped[columns_order]



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

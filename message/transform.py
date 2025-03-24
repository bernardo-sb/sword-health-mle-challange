"""Data Transformations"""

from message.config import DATA_DIR

import pandas as pd


def aggregate_session_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate exercise data by session group.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw exercise results data.
        
    Returns
    -------
    pd.DataFrame
        Data aggregated by session_group.
    """
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
    return grouped

def calculate_performance_metrics(grouped: pd.DataFrame) -> pd.DataFrame:
    """Calculate performance metrics for each session.
    
    Parameters
    ----------
    grouped : pd.DataFrame
        Aggregated session data.
        
    Returns
    -------
    pd.DataFrame
        Session data with performance metrics added.
    """
    grouped["perc_correct_repeats"] = grouped["correct_repeats"] / (grouped["correct_repeats"] + grouped["wrong_repeats"])
    return grouped


def add_reason_counts(df: pd.DataFrame, grouped: pd.DataFrame) -> pd.DataFrame:
    """Add counts for different reasons for leaving exercises and quality ratings.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw exercise results data.
    grouped : pd.DataFrame
        Aggregated session data.
        
    Returns
    -------
    pd.DataFrame
        Session data with reason counts added.
    """
    leave_exercise_reasons = ["system_problem", "other", "unable_perform", "pain", "tired", "technical_issues", "difficulty"]
    quality_reasons = ["movement_detection", "my_self_personal", "other", "exercises", "tablet", "tablet_and_or_motion_trackers", "easy_of_use", "session_speed"]

    for reason in leave_exercise_reasons:
        grouped[f"leave_exercise_{reason}"] = df[df["leave_exercise"] == reason].groupby("session_group")["leave_exercise"].count()
        grouped[f"leave_exercise_{reason}"].fillna(0, inplace=True)
    for reason in quality_reasons:
        grouped[f"quality_reason_{reason}"] = df[df[f"quality_reason_{reason}"] == reason].groupby("session_group")["quality"].count()
        grouped[f"quality_reason_{reason}"].fillna(0, inplace=True)
    return grouped


def identify_problematic_exercises(df: pd.DataFrame, grouped: pd.DataFrame) -> pd.DataFrame:
    """Identify exercises with problems (most incorrect, first skipped).
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw exercise results data.
    grouped : pd.DataFrame
        Aggregated session data.
        
    Returns
    -------
    pd.DataFrame
        Session data with problematic exercise information added.
    """
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
    return grouped

def order_columns(grouped: pd.DataFrame) -> pd.DataFrame:
    """Order columns in a logical sequence.
    
    Parameters
    ----------
    grouped : pd.DataFrame
        Session data with all features.
        
    Returns
    -------
    pd.DataFrame
        Session data with columns in the specified order.
    """
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
        "quality_reason_movement_detection",
        "quality_reason_my_self_personal",
        "quality_reason_other",
        "quality_reason_exercises",
        "quality_reason_tablet",
        "quality_reason_tablet_and_or_motion_trackers",
        "quality_reason_easy_of_use",
        "quality_reason_session_speed",
        "session_is_nok",
        "leave_exercise_system_problem",
        "leave_exercise_other",
        "leave_exercise_unable_perform",
        "leave_exercise_pain",
        "leave_exercise_tired",
        "leave_exercise_technical_issues",
        "leave_exercise_difficulty",
        "prescribed_repeats",
        "training_time",
        "perc_correct_repeats",
        "number_exercises",
        "number_of_distinct_exercises",
        "exercise_with_most_incorrect",
        "first_exercise_skipped",
        ]
    grouped = grouped[columns_order]
    grouped.to_parquet(DATA_DIR / "session_data.parquet", index=False)
    return grouped

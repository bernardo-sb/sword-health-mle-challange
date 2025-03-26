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
    grouped = (
        df.groupby("session_group")
        .agg(
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
            quality_reason_movement_detection=(
                "quality_reason_movement_detection",
                "first",
            ),
            quality_reason_my_self_personal=(
                "quality_reason_my_self_personal",
                "first",
            ),
            quality_reason_other=("quality_reason_other", "first"),
            quality_reason_exercises=("quality_reason_exercises", "first"),
            quality_reason_tablet=("quality_reason_tablet", "first"),
            quality_reason_tablet_and_or_motion_trackers=(
                "quality_reason_tablet_and_or_motion_trackers",
                "first",
            ),
            quality_reason_easy_of_use=("quality_reason_easy_of_use", "first"),
            quality_reason_session_speed=("quality_reason_session_speed", "first"),
        )
        .reset_index()
    )

    grouped["session_is_nok"] = grouped["session_is_nok"].astype("object")
    grouped["pain"] = grouped["pain"].astype("float64")
    grouped["fatigue"] = grouped["fatigue"].astype("float64")
    grouped["session_number"] = grouped["session_number"].astype("int64")
    grouped["quality"] = grouped["quality"].astype("float64")
    grouped["quality_reason_movement_detection"] = grouped[
        "quality_reason_movement_detection"
    ].astype("int64")
    grouped["quality_reason_my_self_personal"] = grouped[
        "quality_reason_my_self_personal"
    ].astype("int64")
    grouped["quality_reason_other"] = grouped["quality_reason_other"].astype("int64")
    grouped["quality_reason_exercises"] = grouped["quality_reason_exercises"].astype(
        "int64"
    )
    grouped["quality_reason_tablet"] = grouped["quality_reason_tablet"].astype("int64")
    grouped["quality_reason_tablet_and_or_motion_trackers"] = grouped[
        "quality_reason_tablet_and_or_motion_trackers"
    ].astype("int64")
    grouped["quality_reason_easy_of_use"] = grouped[
        "quality_reason_easy_of_use"
    ].astype("int64")
    grouped["quality_reason_session_speed"] = grouped[
        "quality_reason_session_speed"
    ].astype("int64")

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
    grouped["perc_correct_repeats"] = grouped["correct_repeats"] / (
        grouped["correct_repeats"] + grouped["wrong_repeats"]
    )
    return grouped


def add_reason_counts(df: pd.DataFrame, grouped: pd.DataFrame) -> pd.DataFrame:
    """Add counts for different reasons for leaving exercises.

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
    leave_exercise_reasons = [
        "system_problem",
        "other",
        "unable_perform",
        "pain",
        "tired",
        "technical_issues",
        "difficulty",
    ]

    df.set_index("session_group", inplace=True)
    grouped.set_index("session_group", inplace=True)

    for reason in leave_exercise_reasons:
        grouped[f"leave_exercise_{reason}"] = 0
        df_leave_exercise = (
            df[df["leave_exercise"] == reason]
            .groupby("session_group")["leave_exercise"]
            .count()
        )
        grouped.loc[df_leave_exercise.index, f"leave_exercise_{reason}"] = (
            df_leave_exercise.values
        )
        grouped[f"leave_exercise_{reason}"].fillna(0, inplace=True)

    grouped.reset_index(inplace=True)  # this is inefficient...
    return grouped


def identify_most_incorrect_exercise(
    df: pd.DataFrame, grouped: pd.DataFrame
) -> pd.DataFrame:
    """Identify exercises with problems most incorrect.

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

    grouped_wrong_reps = (
        df.groupby(["session_group", "exercise_name"])["wrong_repeats"]
        .sum()
        .reset_index()
    )
    grouped_incorrect_ex = grouped_wrong_reps.loc[
        grouped_wrong_reps.groupby("session_group")["wrong_repeats"].idxmax()
    ].drop(columns="wrong_repeats", axis=1)
    grouped = grouped.merge(grouped_incorrect_ex, on="session_group", how="left")
    grouped = grouped.rename(columns={"exercise_name": "exercise_with_most_incorrect"})

    return grouped


def identify_first_exercise_skipped(
    df: pd.DataFrame, grouped: pd.DataFrame
) -> pd.DataFrame:
    """Identify the first exercise skipped.

    Parameters
    ----------
    df : pd.DataFrame
        Raw exercise results data.
    grouped : pd.DataFrame
        Aggregated session data.

    Returns
    -------
    pd.DataFrame
        Session data with first skipped exercise added.
    """
    skipped_exercises = df[df["leave_exercise"].notnull()].sort_values(
        by=["session_group", "exercise_order"]
    )
    first_skipped = (
        skipped_exercises.groupby("session_group")
        .first()
        .reset_index()[["session_group", "exercise_name"]]
    )
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

    return grouped

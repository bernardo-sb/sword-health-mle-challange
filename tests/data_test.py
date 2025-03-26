from pathlib import Path
import pytest
import pandas as pd
from message.data import transform_features_py
import numpy as np
from numpy.testing import assert_array_equal

DATA_DIR = Path(__file__).parent.parent / "data"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def expected_df():
    df = (
        pd.read_parquet(Path(DATA_DIR, "features_expected.parquet"))
        .reset_index(drop=True)
        .sort_values("session_group")
    )
    return df


# kind of an anti-pattern, but prevents the function from running multiple times
@pytest.fixture(scope="session")
def result_df():
    df = transform_features_py().reset_index(drop=True).sort_values("session_group")
    return df


@pytest.fixture(scope="session")
def exercise_with_most_incorrect_df():
    df = (
        pd.read_parquet(FIXTURES_DIR / "df_exercise_with_most_incorrect.parquet")
        .reset_index(drop=True)
        .sort_values("session_group")
    )
    return df


@pytest.mark.parametrize(
    "column",
    [
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
        "prescribed_repeats",
        "training_time",
        "number_exercises",
        "number_of_distinct_exercises",
    ],
)
def test_transform_features_py_column(result_df, expected_df, column):
    assert_array_equal(result_df[column].values, expected_df[column].values)


def test_perc_correct_repeats(result_df, expected_df):
    # computers don't like floats, so we multiply by 10,000 and convert to int
    # this will give us 2 decimal places precision
    assert_array_equal(
        (result_df["perc_correct_repeats"].values * 10000.0).astype(int),
        (expected_df["perc_correct_repeats"].values * 10000.0).astype(int),
    )


def test_session_is_nok(result_df, expected_df):
    # handle missing values
    assert_array_equal(
        result_df["session_is_nok"].fillna(-1).values,
        expected_df["session_is_nok"].fillna(-1).values,
    )


@pytest.mark.parametrize(
    "column",
    [
        "leave_exercise_system_problem",
        "leave_exercise_other",
        "leave_exercise_unable_perform",
        "leave_exercise_pain",
        "leave_exercise_tired",
        "leave_exercise_technical_issues",
        "leave_exercise_difficulty",
    ],
)
def test_leave_exercise(result_df, expected_df, column):
    assert_array_equal(
        result_df[column].values.astype(int), expected_df[column].values.astype(int)
    )


def test_identify_first_exercise_skipped(result_df, expected_df):
    assert_array_equal(
        result_df["first_exercise_skipped"].fillna("-").values,
        expected_df["first_exercise_skipped"].fillna("-").values,
    )


def test_identify_most_incorrect_exercise(result_df, exercise_with_most_incorrect_df):
    # mast match a least one
    trans_col = (
        result_df["exercise_with_most_incorrect"].fillna("-").values
        == exercise_with_most_incorrect_df["exercise_with_most_incorrect_trans"]
        .fillna("-")
        .values
    )

    session_col = (
        result_df["exercise_with_most_incorrect"].fillna("-").values
        == exercise_with_most_incorrect_df["exercise_with_most_incorrect_session"]
        .fillna("-")
        .values
    )

    assert np.all((trans_col + session_col) > 0)

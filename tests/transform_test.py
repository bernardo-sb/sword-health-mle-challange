from pathlib import Path
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from message.transform import (
    aggregate_session_data,
    calculate_performance_metrics,
    add_reason_counts,
    identify_problematic_exercises,
    order_columns,
)

DATA_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def df_input():
    return pd.read_csv(Path(DATA_DIR, "input.csv")).reset_index(drop=False)

@pytest.fixture
def aggregate_session_data_expected():
    return pd.read_csv(Path(DATA_DIR, "aggregate_session_data.csv"))


@pytest.fixture
def calculate_performance_metrics_input():
    return pd.read_csv(Path(DATA_DIR, "aggregate_session_data.csv"))

@pytest.fixture
def calculate_performance_metrics_expected():
    return pd.read_csv(Path(DATA_DIR, "calculate_performance_metrics.csv"))


@pytest.fixture
def add_reason_counts_input():
    return pd.read_csv(Path(DATA_DIR, "calculate_performance_metrics.csv"))

@pytest.fixture
def add_reason_counts_expected():
    return pd.read_csv(Path(DATA_DIR, "add_reason_counts.csv"))

@pytest.fixture
def identify_problematic_exercises_input():
    return pd.read_csv(Path(DATA_DIR, "add_reason_counts.csv"))

@pytest.fixture
def identify_problematic_exercises_expected():
    return pd.read_csv(Path(DATA_DIR, "identify_problematic_exercises.csv"))

@pytest.fixture
def order_columns_input():
    return pd.read_csv(Path(DATA_DIR, "identify_problematic_exercises.csv"))

@pytest.fixture
def order_columns_expected():
    return pd.read_csv(Path(DATA_DIR, "order_columns.csv"))

def test_aggregate_session_data(df_input, aggregate_session_data_expected):
    result = aggregate_session_data(df_input)
    assert_frame_equal(result, aggregate_session_data_expected)

def test_calculate_performance_metrics(calculate_performance_metrics_input, calculate_performance_metrics_expected):
    result = calculate_performance_metrics(calculate_performance_metrics_input)
    assert_frame_equal(result, calculate_performance_metrics_expected)

def test_add_reason_counts(add_reason_counts_input, add_reason_counts_expected):
    result = add_reason_counts(add_reason_counts_input, add_reason_counts_input)
    assert_frame_equal(result, add_reason_counts_expected)


def test_identify_problematic_exercises(identify_problematic_exercises_input, identify_problematic_exercises_expected):
    result = identify_problematic_exercises(identify_problematic_exercises_input, identify_problematic_exercises_input)
    assert_frame_equal(result, identify_problematic_exercises_expected)

def test_order_columns(order_columns_input, order_columns_expected):
    result = order_columns(order_columns_input)
    assert_frame_equal(result, order_columns_expected)

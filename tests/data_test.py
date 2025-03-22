from pathlib import Path
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from message.data import transform_features_py

DATA_DIR = Path(__file__).parent.parent / "data"

@pytest.fixture
def expected_df():
    return pd.read_parquet(Path(DATA_DIR, "features_expected.parquet"))

def test_transform_features_py(expected_df):
    result_df = transform_features_py()
    assert_frame_equal(result_df, expected_df)

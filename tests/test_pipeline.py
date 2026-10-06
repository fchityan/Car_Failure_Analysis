import numpy as np
import pandas as pd

from src.pipeline import prepare_training_data, tune_threshold


def sample_frame() -> pd.DataFrame:
    rows = []
    for index in range(40):
        failed = 1 if index % 3 == 0 else 0
        rows.append(
            {
                "Car ID": f"CAR-{index:05d}",
                "Model": "SUV" if index % 2 else "Sedan",
                "Color": "Blue",
                "Temperature": 75 + index % 20,
                "RPM": 2000 + index * 20,
                "Factory": "Factory A" if index % 2 else "Factory B",
                "Usage": "Very High" if failed else "Medium",
                "Fuel consumption": 7.0 + (index % 5),
                "Membership": "Gold" if index % 2 else "Basic",
                "Failure A": failed,
                "Failure B": 0,
                "Failure C": 0,
                "Failure D": 0,
                "Failure E": 0,
            }
        )
    return pd.DataFrame(rows)


def test_prepare_training_data_creates_target_without_failure_leakage():
    X, y = prepare_training_data(sample_frame())
    assert "failure_a" not in X.columns
    assert "car_id" not in X.columns
    assert set(y.unique()) == {0, 1}


def test_threshold_tuning_returns_valid_operating_point():
    y = pd.Series([0, 0, 1, 1])
    probabilities = np.array([0.05, 0.30, 0.55, 0.90])
    threshold, table = tune_threshold(y, probabilities)
    assert 0.10 <= threshold <= 0.90
    assert not table.empty
    assert "f2" in table.columns

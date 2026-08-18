import numpy as np
import pandas as pd

from back.data.process import (
    Transformer,
    remove_missing,
    remove_outliers,
    substitute_outliers,
    susbstitute_missing,
)


def test_remove_outliers_returns_original_row_indexes():
    frame = pd.DataFrame({"value": [-100, 1, 2, 3, 100]}, index=[10, 11, 12, 13, 14])

    indexes = remove_outliers(frame, "value", upper_bound=0.75, lower_bound=0.25)

    assert indexes == [10, 14]


def test_adjust_closer_replaces_with_iqr_boundaries():
    frame = pd.DataFrame({"value": [-100, 1, 2, 3, 100]})

    result, count = substitute_outliers(frame, "value", "Adjust closer", 0.75, 0.25)

    assert count == 2
    np.testing.assert_allclose(result["value"], [-2, 1, 2, 3, 6])


def test_missing_value_operations_for_numeric_and_categorical_columns():
    frame = pd.DataFrame({"number": [1.0, np.nan, 3.0], "category": ["a", None, "a"]})

    numeric = susbstitute_missing(frame.copy(), "number", "Mean")
    categorical = susbstitute_missing(frame.copy(), "category", "Mode")

    assert numeric["number"].tolist() == [1.0, 2.0, 3.0]
    assert categorical["category"].tolist() == ["a", "a", "a"]
    assert len(remove_missing(frame, "number")) == 2


def test_minmax_and_label_transformers_can_transform_new_values():
    scaler = Transformer("Normalization (MinMax)", "number")
    transformed = scaler.fit(np.array([[0.0], [10.0]]))

    np.testing.assert_allclose(transformed.ravel(), [0.0, 1.0])
    np.testing.assert_allclose(scaler.transform(np.array([5.0])), [[0.5]])

    encoder = Transformer("Label encoding", "category")
    np.testing.assert_array_equal(encoder.fit(np.array(["b", "a", "b"])), [1, 0, 1])
    np.testing.assert_array_equal(encoder.transform("a"), [0])


def test_one_hot_transformer_returns_named_dataframe():
    transformer = Transformer("One hot encoding", "colour")

    result = transformer.fit(np.array(["red", "blue", "red"]))

    assert list(result.columns) == ["colour_blue", "colour_red"]
    np.testing.assert_array_equal(result.to_numpy(), [[0, 1], [1, 0], [0, 1]])

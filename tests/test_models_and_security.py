import io
import os
import pickle

import numpy as np
import pytest
from sklearn.metrics import recall_score

from back.ML.model import ModelImplementation
from back.task import Task, _RestrictedTaskUnpickler


def test_regression_metrics_use_standard_definitions():
    model = ModelImplementation("Linear Regression")
    model.model.fit([[0], [1], [2]], [0, 2, 4])
    y = np.array([0.0, 1.0, 5.0])
    model.estimator_type = "regressor"

    scores = model.get_score(np.array([[0], [1], [2]]), y)
    predictions = model.model.predict([[0], [1], [2]])
    expected_mse = np.mean((y - predictions) ** 2)

    assert np.isclose(scores["mse"], expected_mse)
    assert np.isclose(scores["rmse"], np.sqrt(expected_mse))
    assert np.isclose(scores["nrmse"], np.sqrt(expected_mse) / np.ptp(y))


def test_classifier_recall_uses_true_labels_first():
    model = ModelImplementation("Random Forest")
    X = np.arange(12).reshape(-1, 1)
    y = np.array(["a"] * 8 + ["b"] * 4)
    model.model.fit(X, y)
    model.estimator_type = "classifier"
    model.class_names = np.unique(y)
    model.n_classes = 2

    scores = model.get_score(X, y)
    prediction = model.model.predict(X)

    assert np.isclose(scores["recall"], recall_score(y, prediction, pos_label="a"))


def test_model_parameter_updates_use_keyword_arguments():
    model = ModelImplementation("Linear Regression")

    model.set_params({"fit_intercept": False})

    assert model.model.fit_intercept is False


def test_restricted_task_loader_round_trips_task_instances():
    task = Task.__new__(Task)
    task.task_name = "roundtrip"

    loaded = _RestrictedTaskUnpickler(io.BytesIO(pickle.dumps(task))).load()

    assert isinstance(loaded, Task)
    assert loaded.task_name == "roundtrip"


def test_restricted_task_loader_rejects_arbitrary_globals():
    class Malicious:
        def __reduce__(self):
            return os.system, ("echo unsafe",)

    with pytest.raises(pickle.UnpicklingError, match="forbidden object"):
        _RestrictedTaskUnpickler(io.BytesIO(pickle.dumps(Malicious()))).load()

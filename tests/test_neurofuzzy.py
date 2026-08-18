import pickle

import numpy as np

from back.ML.neurofuzzy import NeuroFuzzy


def make_model(X, y, types, memberships=2, regularization=1e-9):
    return NeuroFuzzy(
        input=np.asarray(X, dtype=object),
        input_names=[f"x{i}" for i in range(np.asarray(X).shape[1])],
        output=np.asarray(y, dtype=float),
        output_name="target",
        n_membership_input=memberships,
        n_membership_output=2,
        types=types,
        regularization=regularization,
    )


def test_three_variable_rule_strengths_use_every_variable():
    model = make_model(
        [[0, 0, 0], [1, 1, 1]], [0, 1], [float, float, float]
    )
    memberships = np.array([0.2, 0.8, 0.3, 0.7, 0.4, 0.6])

    actual = model.multivariate_memb(memberships)
    expected = np.kron(np.kron(memberships[:2], memberships[2:4]), memberships[4:])

    assert model.n_rules == 8
    np.testing.assert_allclose(actual, expected)


def test_normalized_rule_strengths_sum_to_one():
    model = make_model([[0, 0], [1, 1], [2, 2]], [0, 1, 2], [float, float])
    design, covered = model._design_matrix([[0.25, 1.75], [1.5, 0.5]])

    assert covered.all()
    np.testing.assert_allclose(design.sum(axis=1), 1.0)
    assert np.all((design >= 0) & (design <= 1))


def test_ridge_consequents_recover_simple_linear_relation():
    X = np.linspace(0, 10, 21).reshape(-1, 1)
    y = 2 * X[:, 0] + 1
    model = make_model(X, y, [float]).fit()

    predictions = model.predict(X)

    np.testing.assert_allclose(predictions, y, atol=1e-5)
    assert model.metrics["r2"] > 0.999999
    assert len(model.get_rules()) == model.n_rules


def test_categorical_inputs_fit_predict_and_handle_unknown_category():
    X = np.array([[0, "red"], [1, "red"], [0, "blue"], [1, "blue"]], dtype=object)
    y = np.array([1, 2, 10, 11], dtype=float)
    model = make_model(X, y, [float, object]).fit()

    predictions = model.predict(X)
    unknown = model.predict([[0.5, "green"]])

    assert model.n_rules == 4
    np.testing.assert_allclose(predictions, y, atol=1e-5)
    np.testing.assert_allclose(unknown, [np.mean(y)])


def test_predictions_outside_numeric_training_range_are_finite():
    model = make_model([[0], [1], [2]], [0, 1, 2], [float]).fit()
    predictions = model.predict([[-100], [100]])

    assert np.isfinite(predictions).all()


def test_fit_rejects_missing_values():
    with np.testing.assert_raises_regex(ValueError, "missing or infinite"):
        make_model([[0], [np.nan]], [0, 1], [float])


def test_pickle_round_trip_preserves_predictions():
    model = make_model([[0], [1], [2]], [0, 1, 2], [float]).fit()
    restored = pickle.loads(pickle.dumps(model))

    np.testing.assert_allclose(restored.predict([[0.5], [1.5]]), model.predict([[0.5], [1.5]]))


def test_legacy_state_is_migrated_by_refitting():
    legacy_state = {
        "X": np.array([[0], [1], [2]], dtype=object),
        "X_names": ["x"],
        "y": np.array([0.0, 1.0, 2.0]),
        "y_name": "target",
        "n_membership": 2,
        "n_membership_output": 2,
        "types": [float],
        "memb_func": "default",
        "trained": True,
    }
    migrated = NeuroFuzzy.__new__(NeuroFuzzy)

    migrated.__setstate__(legacy_state)

    assert migrated.trained
    assert np.isfinite(migrated.predict([[0.5]])).all()

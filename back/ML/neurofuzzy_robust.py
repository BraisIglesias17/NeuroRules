"""Deterministic zero-order Takagi-Sugeno fuzzy regressor."""

from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from pandas.api.types import is_numeric_dtype
from sklearn.metrics import mean_squared_error, r2_score
from skfuzzy import control as ctrl


class NeuroFuzzy:
    """Fixed-antecedent fuzzy regressor with ridge-fitted consequents.

    The public API is compatible with the original GUI integration. Numerical
    variables use triangular memberships and categorical variables use singleton
    memberships. Rules use the product T-norm and constant Sugeno consequents.
    """

    def __init__(self, input, input_names, output, output_name,
                 n_membership_input, n_membership_output, types,
                 memebership_function="default", regularization=1e-6):
        self.X = np.asarray(input, dtype=object)
        if self.X.ndim == 1:
            self.X = self.X.reshape(-1, 1)
        self.y = np.asarray(output, dtype=float).reshape(-1)
        if self.X.ndim != 2 or self.X.shape[0] != self.y.size:
            raise ValueError("Input and output must contain the same number of rows")
        if self.X.shape[1] != len(input_names):
            raise ValueError("Inconsistent number of variables and names")
        if not 1 <= n_membership_input <= 4 or not 1 <= n_membership_output <= 4:
            raise ValueError("Membership counts must be between 1 and 4")
        if not np.all(np.isfinite(self.y)):
            raise ValueError("Output contains missing or infinite values")
        if regularization < 0:
            raise ValueError("Regularization must be non-negative")

        self.n_variables = self.X.shape[1]
        self.X_names = list(input_names)
        self.y_name = output_name
        self.types = list(types)
        if len(self.types) != self.n_variables:
            raise ValueError("One data type is required for every input variable")
        self.n_membership = n_membership_input
        self.n_membership_output = n_membership_output
        self.memb_func = memebership_function
        self.regularization = float(regularization)
        self.trained = False
        self.done = False

        self.antecedents = []
        self.nominal_variables = []
        self.term_names = []
        self.categories = {}
        self.mebm_info = {}
        self._numeric_bounds = {}
        self._build_antecedents()
        self.n_rules = int(np.prod([len(terms) for terms in self.term_names]))
        self.weigths = np.zeros(self.n_rules, dtype=float)
        self.weights = self.weigths
        self.rules = []
        self._create_rules_template()
        self.consecuence = self._build_consequent()

        self.fuzz_X = None
        self.layer_1_output = None
        self.layer_2_output = None
        self.layer_3_output = None
        self.layer_4_output = None
        self.metrics = {"r2": np.nan, "mse": np.nan, "rmse": np.nan, "nrmse": np.nan}
        self.historic_weigths = None
        self.historic_error = None
        self.historic_r2 = None
        self.y_pred = None
        self._fallback_value = float(np.mean(self.y))

    def __setstate__(self, state):
        """Load current models and migrate models saved by the legacy class."""
        if "term_names" in state:
            self.__dict__.update(state)
            return
        self.__init__(
            input=state["X"],
            input_names=state["X_names"],
            output=state["y"],
            output_name=state["y_name"],
            n_membership_input=state["n_membership"],
            n_membership_output=state["n_membership_output"],
            types=state["types"],
            memebership_function=state.get("memb_func", "default"),
        )
        if state.get("trained", False):
            self.fit()

    @staticmethod
    def NAMES(number):
        names = {1: ["Medium"], 2: ["Low", "High"],
                 3: ["Low", "Medium", "High"],
                 4: ["Low", "Medium_1", "Medium_2", "High"]}
        if number not in names:
            raise ValueError("Membership count must be between 1 and 4")
        return names[number]

    def _is_numeric(self, index):
        return is_numeric_dtype(self.types[index])

    def _build_antecedents(self):
        for index, name in enumerate(self.X_names):
            column = self.X[:, index]
            if self._is_numeric(index):
                try:
                    values = np.asarray(column, dtype=float)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Numerical input '{name}' contains non-numeric values") from exc
                if not np.all(np.isfinite(values)):
                    raise ValueError(f"Input '{name}' contains missing or infinite values")
                low, high = float(values.min()), float(values.max())
                if low == high:
                    padding = max(abs(low) * 0.01, 1.0)
                    low, high = low - padding, high + padding
                universe = np.linspace(low, high, 501)
                antecedent = ctrl.Antecedent(universe, name)
                labels = self.NAMES(self.n_membership)
                centers = np.linspace(low, high, self.n_membership)
                if self.n_membership == 1:
                    antecedent[labels[0]] = np.ones_like(universe)
                else:
                    for term_index, label in enumerate(labels):
                        points = [centers[max(0, term_index - 1)], centers[term_index],
                                  centers[min(self.n_membership - 1, term_index + 1)]]
                        antecedent[label] = fuzz.trimf(universe, points)
                self._numeric_bounds[index] = (low, high)
            else:
                categories = list(dict.fromkeys(column.tolist()))
                labels = [str(value) for value in categories]
                if not categories or len(set(labels)) != len(labels):
                    raise ValueError(f"Categorical input '{name}' has invalid or ambiguous labels")
                universe = np.arange(max(2, len(categories)), dtype=float)
                antecedent = ctrl.Antecedent(universe, name)
                for category_index, label in enumerate(labels):
                    membership = np.zeros_like(universe)
                    membership[category_index] = 1.0
                    antecedent[label] = membership
                self.nominal_variables.append(index)
                self.categories[index] = categories
            self.antecedents.append(antecedent)
            self.term_names.append(labels)
            self.mebm_info[name] = len(labels)

    def _build_consequent(self):
        low, high = float(self.y.min()), float(self.y.max())
        if low == high:
            padding = max(abs(low) * 0.01, 1.0)
            low, high = low - padding, high + padding
        consequent = ctrl.Consequent(np.linspace(low, high, 501), self.y_name)
        labels = self.NAMES(self.n_membership_output)
        centers = np.linspace(low, high, self.n_membership_output)
        if len(labels) == 1:
            consequent[labels[0]] = np.ones_like(consequent.universe)
        else:
            for index, label in enumerate(labels):
                points = [centers[max(0, index - 1)], centers[index],
                          centers[min(len(labels) - 1, index + 1)]]
                consequent[label] = fuzz.trimf(consequent.universe, points)
        return consequent

    def _fuzzify_column(self, values, index):
        if index in self.nominal_variables:
            return np.column_stack(
                [values == category for category in self.categories[index]]
            ).astype(float)
        numeric = np.asarray(values, dtype=float)
        if not np.all(np.isfinite(numeric)):
            raise ValueError(f"Input '{self.X_names[index]}' contains missing or infinite values")
        antecedent = self.antecedents[index]
        result = np.column_stack([
            fuzz.interp_membership(antecedent.universe, antecedent[label].mf, numeric)
            for label in self.term_names[index]
        ])
        low, high = self._numeric_bounds[index]
        result[numeric < low, 0] = 1.0
        result[numeric > high, -1] = 1.0
        return result

    def _fuzzify(self, values):
        array = np.asarray(values, dtype=object)
        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.ndim != 2 or array.shape[1] != self.n_variables:
            raise ValueError(f"Expected {self.n_variables} input variables")
        return [self._fuzzify_column(array[:, i], i) for i in range(self.n_variables)]

    @staticmethod
    def _cartesian_strengths(groups):
        strengths = groups[0]
        for group in groups[1:]:
            strengths = (strengths[:, :, None] * group[:, None, :]).reshape(
                strengths.shape[0], -1)
        return strengths

    def _design_matrix(self, values):
        strengths = self._cartesian_strengths(self._fuzzify(values))
        totals = strengths.sum(axis=1)
        covered = totals > np.finfo(float).eps
        normalized = np.zeros_like(strengths)
        normalized[covered] = strengths[covered] / totals[covered, None]
        return normalized, covered

    def fuzzyfication(self, C=0.3):
        del C
        self.fuzz_X = np.concatenate(self._fuzzify(self.X), axis=1)
        return self.fuzz_X

    def to_fuzzy(self, input):
        return np.concatenate(self._fuzzify(input), axis=1)

    def multivariate_memb(self, input):
        flat = np.asarray(input, dtype=float).reshape(-1)
        groups, start = [], 0
        for terms in self.term_names:
            end = start + len(terms)
            groups.append(flat[start:end].reshape(1, -1))
            start = end
        if start != flat.size:
            raise ValueError("Incorrect number of membership values")
        return self._cartesian_strengths(groups)[0]

    def normalization_layer(self, input):
        values = np.asarray(input, dtype=float)
        total = values.sum()
        return values / total if total > np.finfo(float).eps else np.zeros_like(values)

    def fit(self, learning_rate=0.01, epochs=25):
        """Fit consequents with ridge regression (legacy arguments are ignored)."""
        del learning_rate, epochs
        self.fuzzyfication()
        design, covered = self._design_matrix(self.X)
        if not np.any(covered):
            raise ValueError("No training observation activates any fuzzy rule")
        phi, target = design[covered], self.y[covered]
        system = phi.T @ phi + self.regularization * np.eye(self.n_rules)
        rhs = phi.T @ target
        try:
            self.weigths = np.linalg.solve(system, rhs)
        except np.linalg.LinAlgError:
            self.weigths = np.linalg.lstsq(system, rhs, rcond=None)[0]
        self.weights = self.weigths
        self.trained = True
        predictions = self.predict(self.X)
        self.metrics = self._scores(self.y, predictions)
        self.y_pred = predictions.reshape(-1, 1)
        self.historic_weigths = self.weigths.reshape(1, -1).copy()
        self.historic_error = np.array([[self.metrics["mse"]]])
        self.historic_r2 = np.array([[self.metrics["r2"]]])
        self.rules_consecuences()
        return self

    @staticmethod
    def _scores(y_true, y_pred):
        y_true, y_pred = np.asarray(y_true, dtype=float), np.asarray(y_pred, dtype=float)
        mse = mean_squared_error(y_true, y_pred)
        rmse, target_range = float(np.sqrt(mse)), np.ptp(y_true)
        return {"r2": r2_score(y_true, y_pred), "mse": mse, "rmse": rmse,
                "nrmse": rmse / target_range if target_range != 0 else np.nan}

    def get_scores(self, X, y):
        return self._scores(y, self.predict(X))

    def predict(self, input):
        if not self.trained:
            raise ValueError("The model must be fitted before prediction")
        design, covered = self._design_matrix(input)
        predictions = design @ self.weigths
        predictions[~covered] = self._fallback_value
        return predictions

    def nn(self, input):
        self.layer_2_output = self.multivariate_memb(input)
        self.layer_3_output = self.normalization_layer(self.layer_2_output)
        self.layer_4_output = self.calculate_output(self.layer_3_output, self.weigths)
        return self.layer_4_output

    @staticmethod
    def calculate_output(x, weights):
        return float(np.dot(x, weights))

    @staticmethod
    def min_tnorm(a, b):
        return np.minimum(a, b)

    @staticmethod
    def product_tnorm(a, b):
        return np.multiply(a, b)

    def _create_rules_template(self):
        conditions = [[f"{name} is {term}" for term in terms]
                      for name, terms in zip(self.X_names, self.term_names)]
        self.rules = [" AND ".join(parts) for parts in product(*conditions)]

    def rules_consecuences(self):
        self._create_rules_template()
        labels, completed = self.NAMES(self.n_membership_output), []
        for antecedent, weight in zip(self.rules, self.weigths):
            confidences = [float(fuzz.interp_membership(
                self.consecuence.universe, self.consecuence[label].mf, weight
            )) for label in labels]
            if weight < self.consecuence.universe[0]:
                confidences[0] = 1.0
            elif weight > self.consecuence.universe[-1]:
                confidences[-1] = 1.0
            best = int(np.argmax(confidences))
            completed.append(f"{antecedent} THEN {self.y_name} = {weight:.6g} "
                             f"({labels[best]}, membership {confidences[best]:.2f})")
        self.rules = completed

    def get_predictions_on_train(self):
        self.y_pred = self.predict(self.X).reshape(-1, 1)
        return self.y_pred

    def get_weigths(self):
        return self.weigths

    def get_rules(self):
        return self.rules

    def plot_membership_functions(self):
        for antecedent in self.antecedents:
            antecedent.view()
        self.consecuence.view()

    def plot_trend(self):
        if self.n_variables != 1 or not self.trained or 0 in self.nominal_variables:
            return
        values = np.asarray(self.X[:, 0], dtype=float)
        x = np.linspace(values.min(), values.max(), 100)
        _, axis = plt.subplots()
        axis.plot(x, self.predict(x.reshape(-1, 1)), label="Predicted value")
        axis.set(xlabel=self.X_names[0], ylabel=self.y_name, title="Trend")
        axis.legend()
        plt.show()

    def plot_precisewise(self):
        predictions = self.predict(self.X)
        _, axis = plt.subplots()
        for index, variable in enumerate(self.X_names):
            if index in self.nominal_variables:
                continue
            values = np.asarray(self.X[:, index], dtype=float)
            order = np.argsort(values)
            axis.plot(values[order], predictions[order], label=f"{variable}: predicted")
            axis.plot(values[order], self.y[order], label=f"{variable}: actual")
        axis.set(ylabel=self.y_name, title="Training outputs")
        axis.legend()
        plt.show()

    def _plot_history(self, values, ylabel):
        _, axis = plt.subplots()
        axis.plot(np.arange(len(values)), values, label=ylabel)
        axis.set(xlabel="Fit", ylabel=ylabel, title="Fit result")
        axis.legend()
        plt.show()

    def plot_r2_evolution(self):
        self._plot_history(self.historic_r2, "R²")

    def plot_historic_error(self):
        self._plot_history(self.historic_error, "MSE")

    def plot_historic_weight(self):
        _, axis = plt.subplots()
        for index, values in enumerate(self.historic_weigths.T):
            axis.plot(np.arange(len(values)), values, label=f"w{index}")
        axis.set(xlabel="Fit", ylabel="Consequent", title="Fitted consequents")
        axis.legend()
        plt.show()

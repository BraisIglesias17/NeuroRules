import numpy as np

from back.statistic.statistic import StatisticTest


def test_pearson_detects_perfect_linear_relationship():
    result = StatisticTest.pearson([1, 2, 3, 4], [2, 4, 6, 8])

    assert np.isclose(result.statistic, 1.0)
    assert result.pvalue < 0.01


def test_non_parametric_two_sample_tests_return_valid_probabilities():
    first = [1, 2, 3, 4, 5]
    second = [10, 11, 12, 13, 14]

    mann_whitney = StatisticTest.mann_whitney_u(first, second)
    kruskal = StatisticTest.kruskal_wallis(first, second)
    kolmogorov = StatisticTest.kolmorov_smirnov(first, second)

    for result in (mann_whitney, kruskal, kolmogorov):
        assert 0 <= result.pvalue <= 1


def test_chi_squared_is_a_goodness_of_fit_test():
    result = StatisticTest.chi_squared([10, 10, 10, 10])

    assert np.isclose(result.statistic, 0.0)
    assert np.isclose(result.pvalue, 1.0)


def test_normality_and_homogeneity_checks_return_booleans():
    rng = np.random.default_rng(42)
    first = rng.normal(size=100)
    second = rng.normal(loc=0.2, size=100)

    assert isinstance(StatisticTest.check_normality(first), (bool, np.bool_))
    assert isinstance(StatisticTest.check_homogeneity(first, second), (bool, np.bool_))

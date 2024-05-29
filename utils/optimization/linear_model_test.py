import numpy as np
from absl.testing import absltest

from utils.optimization.linear_model import (ComplexLassoModel, LassoModel,
                                             LinearRegression)


class LinearModelTestCase(absltest.TestCase):

    X = np.array([
        [1, 1],
        [2, 1],
    ])
    y = np.array([-1, -3])
    w = np.array([-2, 1])


class LinearRegressionTestCase(LinearModelTestCase):

    def test_fit_line(self):
        linear_regression = LinearRegression(self.X, self.y)
        linear_regression.solve()
        self.assertIsNone(
            np.testing.assert_allclose(linear_regression.get_coefficients(),
                                       self.w))


class LassoRegressionTestCase(LinearModelTestCase):

    def test_fit_line(self):
        lasso_model = LassoModel(self.X, self.y, 0.01)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(lasso_model.get_coefficients(),
                                       np.array([-1.898882, 0.838323]),
                                       atol=1e-6))

        lasso_model = LassoModel(self.X, self.y, 0.001)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(lasso_model.get_coefficients(),
                                       np.array([-1.988821, 0.982232]),
                                       atol=1e-6))


class ComplexLassoRegressionTestCase(LassoRegressionTestCase):

    def test_fit_real_line(self):
        lasso_model = ComplexLassoModel(self.X, self.y, 0.01)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(lasso_model.get_coefficients(),
                                       np.array([-1.9, 0.84]),
                                       atol=1e-5))

        lasso_model = ComplexLassoModel(self.X, self.y, 0.001)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(lasso_model.get_coefficients(),
                                       np.array([-1.99, 0.984]),
                                       atol=1e-5))

    def test_fit_complex_line(self):
        X = np.array([
            [1, 1j],
            [2, 1j],
        ])
        y = np.array([2 - 1j, 3])

        lasso_model = ComplexLassoModel(X, y, 0.01)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(
                lasso_model.get_coefficients(),
                np.array([0.9988 + 0.9200j, -1.8711 - 0.9971j]),
                atol=1e-4))

        lasso_model = ComplexLassoModel(X, y, 1e-6)
        lasso_model.solve()
        self.assertIsNone(
            np.testing.assert_allclose(lasso_model.get_coefficients(),
                                       np.array([1 + 1j, -2 - 1j]),
                                       atol=1e-4))


if __name__ == "__main__":
    absltest.main()

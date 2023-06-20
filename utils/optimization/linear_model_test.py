import numpy as np
from absl.testing import absltest

from utils.optimization.linear_model import LassoModel, LinearRegression


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


if __name__ == "__main__":
    absltest.main()

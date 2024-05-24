import numpy as np
from absl.testing import absltest

from utils.solver.least_squares_solver import (
    LeastSquaresMatrixMatrixSolver, LeastSquaresMatrixVectorSolver,
    TotalLeastSquaresMatrixVectorSolver)


class LeastSquaresMatrixMatrixSolverTestCase(absltest.TestCase):

    def test_solve(self):
        A = np.array([[1, 1], [2, 1], [3, 2], [5, 3]])
        Y = np.array([[2, 3], [5, -1], [9, -2], [3, 3]])
        X = np.array([[-2 / 3, -2], [10 / 3, 11 / 3]])
        solver = LeastSquaresMatrixMatrixSolver(A, Y)
        self.assertIsNone(np.testing.assert_allclose(solver.solution, X))

    def test_solve_weighted(self):
        A = np.array([[1, 1], [2, 1], [3, 2], [5, 3]])
        Y = np.array([[2, 3], [5, -1], [9, -2], [3, 3]])
        w = np.array([1, 1, 0, 1])
        X = np.array([[1.5, -11 / 3], [-1, 7]])
        solver = LeastSquaresMatrixMatrixSolver(A, Y, w)
        self.assertIsNone(np.testing.assert_allclose(solver.solution, X))


class LeastSquaresMatrixVectorSolverTestCase(absltest.TestCase):

    def test_solve(self):
        A = np.array([[1, 1], [2, 1], [3, 2], [5, 3]])
        b = np.array([2, 5, 9, 3])
        x = np.array([-2 / 3, 10 / 3])
        solver = LeastSquaresMatrixVectorSolver(A, b)
        self.assertIsNone(np.testing.assert_allclose(solver.solution, x))

    def test_solve_weighted(self):
        A = np.array([[1, 1], [2, 1], [3, 2], [5, 3]])
        b = np.array([2, 5, 9, 3])
        w = np.array([1, 0, 1, 1])
        x = np.array([-11 / 3, 47 / 6])
        solver = LeastSquaresMatrixVectorSolver(A, b, w)
        self.assertIsNone(np.testing.assert_allclose(solver.solution, x))


class TotalLeastSquaresMatrixVectorSolverTestCase(absltest.TestCase):

    def test_solve(self):
        A = np.array([[1, 1], [2, 3]])
        b = np.array([0, -1])
        x = np.array([1, -1])
        solver = TotalLeastSquaresMatrixVectorSolver(A, b)
        self.assertIsNone(np.testing.assert_allclose(solver.solution, x))

    def test_solve_with_error(self):
        A = np.array([[1, 0], [0, 1], [1, 1]])
        b = np.array([2, -1, 5])
        x = np.array([4.361123, -0.218185])
        solver = TotalLeastSquaresMatrixVectorSolver(A, b)
        self.assertIsNone(
            np.testing.assert_allclose(solver.solution, x, atol=1e-6))


if __name__ == "__main__":
    absltest.main()

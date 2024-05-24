import numpy as np
from absl.testing import absltest

from utils.solver.solver import MatrixMatrixSolver, MatrixVectorSolver


class MatrixMatrixSolverTestCase(absltest.TestCase):

    def test_incompatible_dimensions(self):
        A = np.zeros((3, 2))
        Y = np.zeros((4, 3))
        with self.assertRaises(ValueError):
            solver = MatrixMatrixSolver(A, Y)

    def test_solve(self):
        A = np.array([[1, 2], [1, -1]])
        Y = np.array([[-1, 5], [5, 5]])
        X = np.array([[3, 5], [-2, 0]])
        solver = MatrixMatrixSolver(A, Y)
        self.assertIsNone(np.testing.assert_array_equal(solver.solution, X))


class MatrixVectorSolverTestCase(absltest.TestCase):

    def test_incompatible_dimensions(self):
        A = np.zeros((3, 2))
        b = np.zeros(2)
        with self.assertRaises(ValueError):
            solver = MatrixVectorSolver(A, b)

    def test_solve(self):
        A = np.array([[1, 2], [1, -1]])
        b = np.array([-1, 5])
        x = np.array([3, -2])
        solver = MatrixMatrixSolver(A, b)
        self.assertIsNone(np.testing.assert_array_equal(solver.solution, x))


if __name__ == "__main__":
    absltest.main()

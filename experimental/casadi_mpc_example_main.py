# Adapted from https://github.com/johnviljoen/231A_project/blob/main/mpc_minimal_point_mass.py.

import casadi as ca
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
from absl import app

import utils.visualization.mpl_config

# Cylinder obstacle.
XC = 1
YC = 1
RC = 0.5


class System:
    """State-space system.

    Attributes:
        num_states: Number of states.
        num_inputs: Number of inputs.
    """

    A = np.array([
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ])

    B = np.array([
        [0.0, 0.0],
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
    ])

    @property
    def num_states(self) -> int:
        """Returns the number of states."""
        return self.A.shape[1]

    @property
    def num_inputs(self) -> int:
        """Returns the number of inputs."""
        return self.B.shape[1]

    def xdot(self, x: np.ndarray, u: np.ndarray) -> np.ndarray:
        """State-space model of the system.

        Args:
            x: State vector.
            u: Input vector.

        Returns:
            The xdot vector.
        """
        return self.A @ x + self.B @ u


class Mpc:
    """Model-predictive controller.

    Attributes:
        system: System to control.
        N: Number of finite horizon steps.
        t_step: Time step in seconds.

        opti: Optimization problem.
        X: State progression matrix.
        U: Input progression matrix.
        x_initial: Initial state vector.
        x_final: Final staet vector.
    """

    def __init__(self, system: System, N: int, t_step: float) -> None:
        self.system = system
        self.N = N
        self.t_step = t_step

        self._init_optimization_problem()

    @property
    def num_states(self) -> int:
        """Returns the number of states."""
        return self.system.num_states

    @property
    def num_inputs(self) -> int:
        """Returns the number of inputs."""
        return self.system.num_inputs

    def solve(self, x_initial: np.ndarray,
              x_final: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Solve the optimization problem with the given initial state and reference.

        Args:
            x_initial: Initial state.
            x_final: Final state.

        Returns:
            A 2-tuple consisting of the state progression and the optimal input.
        """
        self.opti.set_value(self.x_initial, x_initial)
        self.opti.set_value(self.x_final, x_final)
        self.opti.set_initial(self.X, np.zeros((self.num_states, self.N + 1)))
        self.opti.set_initial(self.U, np.zeros((self.num_inputs, self.N + 1)))
        solution = self.opti.solve()
        x_solution = solution.value(self.X)
        u_solution = solution.value(self.U)
        return x_solution, u_solution[:, 0]

    def _init_optimization_problem(self) -> None:
        """Initialize the optimization problem."""
        # Define the optimization problem variables.
        self.opti = ca.Opti()
        self.X = self.opti.variable(self.num_states, self.N + 1)
        self.U = self.opti.variable(self.num_inputs, self.N + 1)
        self.x_initial = self.opti.parameter(self.num_states, 1)
        self.x_final = self.opti.parameter(self.num_states, 1)

        # Define the weights.
        Q = np.diag(np.ones(self.num_states)) * 5
        R = np.diag(np.ones(self.num_inputs)) * 0.1

        # Define the bounding box.
        for k in range(self.N + 1):
            self.opti.subject_to(self.X[:, k] < np.array([3, 3, 3, 3]))
            self.opti.subject_to(self.X[:, k] > np.array([-3, -3, -3, -3]))
            self.opti.subject_to(self.U[:, k] < np.array([1, 1]))
            self.opti.subject_to(self.U[:, k] > np.array([-1, -1]))

        # Define the dynamics.
        for k in range(self.N):
            self.opti.subject_to(
                self.X[:, k + 1] == self.X[:, k] +
                self.system.xdot(self.X[:, k], self.U[:, k]) * self.t_step)

        # Define the initial condition.
        self.opti.subject_to(self.X[:, 0] == self.x_initial)

        # Define the cylinder constraint.
        for k in range(self.N - 1):
            # Apply the constraint starting from 2 timesteps in the future.
            t_current = ca.sum1(k * self.t_step)
            multiplier = 1 + t_current * 0.1
            self.opti.subject_to(RC**2 *
                                 multiplier <= (self.X[0, k + 2] - XC)**2 +
                                 (self.X[1, k + 2] - YC)**2)

        # Define the solver and the objective.
        self.opti.solver("ipopt", {
            "ipopt.print_level": 0,
            "print_time": 0,
            "ipopt.tol": 1e-6,
        })
        cost = ca.MX(0)
        for k in range(self.N + 1):
            x_error = self.x_final - self.X[:, k]
            cost += x_error.T @ Q @ x_error + self.U[:, k].T @ R @ self.U[:, k]
        self.opti.minimize(cost)


def main(argv):
    assert len(argv) == 1, argv

    # Define the time range in seconds.
    t_initial = 0
    t_final = 7.5
    t_step = 0.1

    # Define the initial and final states.
    x = np.array([2, 2, 0, 0]).astype(float)
    x_final = np.array([-2, -2, 0, 0]).astype(float)

    system = System()
    mpc = Mpc(system, N=35, t_step=t_step)

    x_history = [np.copy(x)]
    for t in np.arange(t_initial, t_final, t_step):
        _, u = mpc.solve(x, x_final)
        x += system.xdot(x, u) * t_step
        x_history.append(np.copy(x))
    x_history = np.vstack(x_history)

    # Plot the state as a function of time.
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x_history[:, 0], x_history[:, 1])
    ax.add_patch(matplotlib.patches.Circle([XC, YC], RC))
    ax.set_aspect("equal")
    plt.show()


if __name__ == "__main__":
    app.run(main)

"""The Ritz model assembles the stiffness and mass matrices of the plate."""

from simulation.chladni.basis import LegendreBasis2D
from simulation.chladni.integrator import Function, Integrator
from simulation.chladni.material import Material
from simulation.chladni.shape import Shape


class RitzModel:
    """Stiffness and mass matrices of the plate in terms of the basis functions.

    For the basis coefficients c, the bending energy is defined as 1/2 * c^T *
    stiffness * c, and the kinetic energy is defined as 1/2 * c'^T * mass * c'.

    Attributes:
        basis: Basis functions.
        stiffness: Stiffness matrix.
        mass: Mass matrix.
    """

    def __init__(
        self,
        shape: Shape,
        material: Material,
        degree: int,
        num_integration_points_per_side: int,
    ) -> None:
        self.basis = LegendreBasis2D(shape.bounding_box, degree)
        xy = self._derivative(0, 0)
        dxdx = self._derivative(2, 0)
        dydy = self._derivative(0, 2)
        dxdy = self._derivative(1, 1)
        integrator = Integrator(shape, num_integration_points_per_side)
        self.stiffness = material.bending_rigidity * (
            integrator.integrate(dxdx, dxdx) +
            integrator.integrate(dydy, dydy) + material.nu *
            (integrator.integrate(dxdx, dydy) +
             integrator.integrate(dydy, dxdx)) + 2 *
            (1 - material.nu) * integrator.integrate(dxdy, dxdy))
        self.mass = (material.density * material.thickness *
                     integrator.integrate(xy, xy))

    def _derivative(self, x_order: int, y_order: int) -> Function:
        """Returns a derivative of the basis functions as a function of the x-
        and y-coordinates.

        Args:
            x_order: Number of derivatives in x.
            y_order: Number of derivatives in y.
        """
        return lambda x, y: self.basis.evaluate(x, y, x_order, y_order)

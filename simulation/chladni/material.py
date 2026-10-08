"""The material class describes what the plate is made of."""


class Material:
    """Plate material and thickness.

    Attributes:
        E: Stiffness of the material (Young's modulus) in Pa.
        nu: How much the material narrows when stretched (Poisson's ratio).
        density: Density in kg/m^3.
        thickness: Plate thickness in m.
    """

    def __init__(
        self,
        E: float,
        nu: float,
        density: float,
        thickness: float = 1.0e-3,
    ) -> None:
        self.E = E
        self.nu = nu
        self.density = density
        self.thickness = thickness

    @property
    def bending_rigidity(self) -> float:
        """Returns how hard the plate is to bend, E * h^3 / (12 * (1 - nu^2)),
        in Nm.
        """
        return (self.E * self.thickness**3 / (12 * (1 - self.nu**2)))


# 1 mm thick aluminum plate.
ALUMINUM = Material(E=69e9, nu=0.33, density=2700)

# 1 mm thick copper plate.
COPPER = Material(E=117e9, nu=0.34, density=8960)

# Map from material names to material properties.
MATERIALS = {
    "aluminum": ALUMINUM,
    "copper": COPPER,
}

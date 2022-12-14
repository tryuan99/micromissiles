"""The radar class represents a physical radar."""

import numpy as np
import scipy.constants

from simulation.noise import GaussianNoise
from simulation.target import Target
from utils import constants


class Radar:
    """Represents a radar."""

    c = 299792458  # Speed of light in m/s.

    def __init__(self, oversampling: int = 1):
        # Radar parameters. These values are based on TI's IWR6843AOP radar.
        # See https://www.ti.com/lit/ds/symlink/iwr6843aop.pdf for the data sheet.
        self.tx_eirp = 15  # EIRP in dBm.
        self.rx_gain = -1  # RX gain in dB.
        self.noise_figure = 9  # Noise figure in dB.

        # Chirp parameters.
        self.f0 = 60e9  # Chirp starting frequency in Hz.
        self.mu = 1.25e12  # Chirp slope in Hz/s.
        self.fs = 1.067e6  # Sampling frequency in Hz.
        self.Tc = 250e-6  # Chirp-to-chirp time in s.
        self.N_r = 256  # Number of ADC samples.
        self.N_v = 512  # Number of chirps.

        # Antenna parameters.
        self.N_tx = 3  # Number of TX antennas.
        self.N_rx = 4  # Number of RX antennas.
        self.d_tx_hor = [0, 2, 2]  # TX antenna horizontal spacing in lambda/2.
        self.d_tx_ver = [0, 2, 0]  # TX antenna vertical spacing in lambda/2.
        self.d_rx_hor = [1, 0, 1, 0]  # RX antenna horizontal spacing in lambda/2.
        self.d_rx_ver = [1, 1, 0, 0]  # RX antenna vertical spacing in lambda/2.
        assert len(self.d_tx_hor) == self.N_tx
        assert len(self.d_tx_ver) == self.N_tx
        assert len(self.d_rx_hor) == self.N_rx
        assert len(self.d_rx_ver) == self.N_rx
        assert np.min(self.d_tx_hor) >= 0
        assert np.min(self.d_tx_ver) >= 0
        assert np.min(self.d_rx_hor) >= 0
        assert np.min(self.d_rx_ver) >= 0
        assert np.min(self.d_tx_hor + self.d_rx_hor) == 0
        assert np.min(self.d_tx_ver + self.d_rx_ver) == 0

        # Time axis.
        self.t_axis_chirp = (
            np.arange(self.N_r) / self.fs
        )  # Time axis for the samples of a single chirp.
        self.t_chirp_start = (
            np.arange(self.N_v) * self.Tc
        )  # Starting times for each chirp.

        # FFT parameters.
        self.N_bins_r = 256 * oversampling  # Number of range bins.
        self.N_bins_v = 512 * oversampling  # Number of Doppler bins.
        self.N_bins_az = 32  # Number of bins in azimuth.
        self.N_bins_el = 32  # Number of bins in elevation.
        assert self.N_bins_r >= self.N_r
        assert self.N_bins_v >= self.N_v
        assert self.N_bins_az >= np.max(self.d_tx_hor) + np.max(self.d_rx_hor) - (
            np.min(self.d_tx_hor) + np.min(self.d_rx_hor)
        )
        assert self.N_bins_el >= np.max(self.d_tx_ver) + np.max(self.d_rx_ver) - (
            np.min(self.d_tx_ver) + np.min(self.d_rx_ver)
        )

    @property
    def lambda0(self) -> float:
        """Wavelength at the starting frequency in m."""
        return self.c / self.f0

    @property
    def T0(self) -> float:
        """Sampling duration of a single chirp in s."""
        return self.N_r / self.fs

    @property
    def B(self) -> float:
        """Sampled bandwidth in Hz."""
        return self.mu * self.T0

    @property
    def fc(self) -> float:
        """Center frequency in Hz."""
        return self.f0 + self.B / 2

    @property
    def lambdac(self) -> float:
        """Wavelength at the center frequency in m."""
        return self.c / self.fc

    @property
    def pri(self) -> float:
        """Pulse reptition interval in s."""
        return self.Tc

    @property
    def prf(self) -> float:
        """Pulse repetition frequency in Hz."""
        return 1 / self.Tc

    @property
    def cpi(self) -> float:
        """Coherent processing interval, or frame time, in s."""
        return self.N_v * self.Tc

    @property
    def duty_cycle(self) -> float:
        """Duty cycle."""
        return self.N_r / self.fs / self.pri

    @property
    def t_axis(self) -> np.ndarray:
        """2D time axis for the samples of all sweeps.

        The time axis has dimensions (number of chirps) x (number of ADC samples).
        """
        return (
            np.repeat([self.t_axis_chirp], self.N_v, axis=0)
            + self.t_chirp_start[:, np.newaxis]
        )

    @property
    def r_res(self) -> float:
        """Range resolution in m."""
        return self.c / (2 * self.B)

    @property
    def r_max(self) -> float:
        """Maximum range in m."""
        return self.fs * self.c / (2 * self.mu)

    @property
    def r_axis(self) -> np.ndarray:
        """Range axis in m."""
        return np.linspace(0, self.r_max, self.N_bins_r, endpoint=False)

    @property
    def v_res(self) -> float:
        """Doppler resolution in m/s."""
        return self.lambdac / (2 * self.cpi)

    @property
    def v_max(self) -> float:
        """Unambiguous Doppler in m/s."""
        return self.lambdac / (4 * self.Tc)

    @property
    def v_axis(self) -> np.ndarray:
        """Doppler axis in m/s."""
        return np.linspace(-self.v_max, self.v_max, self.N_bins_v, endpoint=False)

    @property
    def az_res(self) -> float:
        """Angular resolution in rad."""
        return 2 / (
            np.max(self.d_tx_hor)
            + np.max(self.d_rx_hor)
            - (np.min(self.d_tx_hor) + np.min(self.d_rx_hor))
        )

    @property
    def az_axis(self) -> np.ndarray:
        """Azimuth axis in rad."""
        # The FFT outputs a positive spatial frequency if the phase increases
        # in the positive x-direction. In our coordinate system, the phase
        # increases in the negative x-direction.
        return -np.arcsin(np.linspace(-1, 1, self.N_bins_az, endpoint=False))

    @property
    def el_res(self) -> float:
        """Elevational resolution in rad."""
        return 2 / (
            np.max(self.d_tx_ver)
            + np.max(self.d_rx_ver)
            - (np.min(self.d_tx_ver) + np.min(self.d_rx_ver))
        )

    @property
    def el_axis(self):
        """Elevation axis in rad."""
        # The FFT outputs a positive spatial frequency if the phase increases
        # in the positive y-direction. In our coordinate system, the phase
        # increases in the negative y-direction.
        return -np.arcsin(np.linspace(-1, 1, self.N_bins_el, endpoint=False))

    @property
    def window_r(self) -> np.ndarray:
        """Normalized Blackman window for the range FFT."""
        window = np.blackman(self.N_r + 2)[1:-1]
        return window / np.linalg.norm(window)

    @property
    def window_v(self) -> np.ndarray:
        """Normalized Hann window for the Doppler FFT."""
        window = np.hanning(self.N_v + 2)[1:-1]
        return window / np.linalg.norm(window)

    @property
    def noise_factor(self) -> float:
        """Noise factor."""
        return constants.db2power(self.noise_figure)

    def get_fft_processing_gain_r(self, noise=False, window=True) -> float:
        """Returns the range FFT processing gain."""
        window_samples = self.window_r if window else np.ones(self.N_r)
        if noise:
            return np.linalg.norm(window_samples)
        return np.sum(window_samples)

    def get_fft_processing_gain_v(self, noise=False, window=True) -> float:
        """Returns the Doppler FFT processing gain."""
        window_samples = self.window_v if window else np.ones(self.N_v)
        if noise:
            return np.linalg.norm(window_samples)
        return np.sum(window_samples)

    def get_fft_processing_gain(self, noise=False, window=True) -> float:
        """Returns the 2D FFT processing gain."""
        return self.get_fft_processing_gain_r(
            noise, window
        ) * self.get_fft_processing_gain_v(noise, window)

    def get_range_doppler_bin_indices(
        self, target: Target, fft_shifted: bool = True
    ) -> tuple[int, int]:
        """Returns the range-Doppler indices corresponding to the target."""
        # TODO(titan): This could be made more accurate by considering velocity and acceleration.
        average_range = (
            target.range
            + (
                target.range
                + target.range_rate * self.cpi
                + 1 / 2 * target.acceleration * self.cpi**2
            )
        ) / 2
        average_range_rate = (
            target.range_rate + (target.range_rate + target.acceleration * self.cpi)
        ) / 2
        range_bin_index = (average_range * self.N_bins_r / self.r_max) % self.N_bins_r
        doppler_bin_index = (
            (average_range_rate * self.N_bins_v / 2) / self.v_max
        ) % self.N_bins_v
        if fft_shifted:
            doppler_bin_index = (doppler_bin_index + self.N_bins_v // 2) % self.N_bins_v
        return int(np.round(range_bin_index)), int(np.round(doppler_bin_index))

    def generate_noise(self, shape: tuple[int, ...], temperature: float) -> np.ndarray:
        """Generates the noise in the ADC samples, including thermal noise,
        quantization noise, and phase noise, all scaled by the noise figure.

        Args:
            shape: Shape of the noise.
            temperature: Temperature in Celsius.

        Returns:
            Noise in the ADC samples.
        """
        # TODO(titan): Add quantization and phase noise.
        return self.generate_thermal_noise(shape, temperature)

    def get_noise_amplitude(self, temperature: float) -> float:
        """Returns the noise amplitude considering the noise figure, thermal
        noise, quantization noise, and phase noise.

        Args:
            temperature: Temperature in Celsius.
        """
        return self.get_thermal_noise_amplitude(temperature)

    def generate_thermal_noise(
        self, shape: tuple[int, ...], temperature: float
    ) -> np.ndarray:
        """Generates thermal noise in the ADC samples.

        Args:
            shape: Shape of the noise.
            temperature: Temperature in Celsius.

        Returns:
            Thermal noise in the ADC samples.
        """
        return GaussianNoise(shape, self.get_thermal_noise_amplitude(temperature))

    def get_thermal_noise_amplitude(self, temperature: float) -> float:
        """Returns the thermal noise amplitude.

        Args:
            temperature: Temperature in Celsius.
        """
        # The sqrt(2) factor is because the I and Q samples are sampled
        # independently and added together.
        return constants.power2mag(
            scipy.constants.k
            * scipy.constants.convert_temperature(temperature, "Celsius", "Kelvin")
            * self.fs
            / 2
            * np.sqrt(2)
            * self.noise_factor
        )

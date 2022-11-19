"""The radar class represents a physical radar."""

import numpy as np


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
        self.mu = 6e12  # Chirp slope in Hz/s.
        self.fs = 10.24e6  # Sampling frequency in Hz.
        self.Tc = 100e-6  # Chirp-to-chirp time in s.
        self.N_r = 512  # Number of ADC samples.
        self.N_v = 512  # Number of chirps.

        # Antenna parameters.
        # TODO(titan): Change the antenna array parameters.
        self.N_tx = 3  # Number of TX antennas.
        self.N_rx = 4  # Number of RX antennas.
        self.d_tx_hor = [0, 2, 2]  # TX antenna horizontal spacing in lambda/2.
        self.d_tx_ver = [0, 2, 0]  # TX antenna vertical spacing in lambda/2.
        self.d_rx_hor = [1, 0, 1, 0]  # RX antenna horizontal spacing in lambda/2.
        self.d_rx_ver = [1, 1, 0, 0]  # RX antenna vertical spacing in lambda/2.
        assert len(self.d_tx_hor) == len(self.d_tx_ver) == self.N_tx
        assert len(self.d_rx_hor) == len(self.d_rx_ver) == self.N_rx

        # Time axis.
        self.t_axis_chirp = (
            np.arange(self.N_r) / self.fs
        )  # Time axis for the samples of a single chirp.
        self.t_chirp_start = (
            np.arange(self.N_v) * self.Tc
        )  # Starting times for each chirp.

        # FFT parameters.
        self.N_bins_r = 512 * oversampling  # Number of range bins.
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
    def pri(self):
        """Pulse reptition interval in s."""
        return self.Tc

    @property
    def prf(self):
        """Pulse repetition frequency in Hz."""
        return 1 / self.Tc

    @property
    def cpi(self):
        """Coherent processing interval, or frame time, in s."""
        return self.N_v * self.Tc

    @property
    def duty_cycle(self):
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
    def az_res(self):
        """Angular resolution in rad."""
        return 2 / (
            np.max(d_tx_hor) + np.max(d_rx_hor) - (np.min(d_tx_hor) + np.min(d_rx_hor))
        )

    @property
    def el_res(self):
        """Elevational resolution in rad."""
        return 2 / (
            np.max(d_tx_ver) + np.max(d_rx_ver) - (np.min(d_tx_ver) + np.min(d_rx_ver))
        )

    @property
    def wnd_r(self):
        """Normalized Blackman window for the range FFT."""
        wnd = np.blackman(self.N_r + 2)[1:-1]
        return wnd / np.linalg.norm(wnd)

    @property
    def wnd_v(self):
        """Normalized Hann window for the Doppler FFT."""
        wnd = np.hanning(self.N_v + 2)[1:-1]
        return wnd / np.linalg.norm(wnd)

import numpy as np
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Constants
C_AIR = 343.2  # Speed of sound in air (m/s) at 20C
RHO_AIR = 1.2041  # Density of air (kg/m^3) at 20C

try:
    import cupy as cp
    HAS_GPU = cp.cuda.is_available()
except (ImportError, Exception):
    HAS_GPU = False
    cp = None

def get_cylinder_impedance(f: np.ndarray, radius: float, length: float) -> np.ndarray:
    """
    Calculate the transfer matrix or impedance of a cylindrical section.
    For TMM, we return the Transfer Matrix components or process the chain.
    Here we implement a simplified TMM step.

    This function is a helper, but the main logic usually iterates over segments.
    """
    # This is a placeholder for the lower level physics logic which will be in the PhysicsEngine class
    pass

class PhysicsEngine:
    """
    Core physics engine for acoustic simulation using Transfer Matrix Method (TMM).
    Supports CPU (numpy) and GPU (cupy) backends.
    """

    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu and HAS_GPU
        self.xp = cp if self.use_gpu else np
        logger.info(f"PhysicsEngine initialized. Backend: {'GPU' if self.use_gpu else 'CPU'}")

    def compute_impedance_curve(self,
                              bore_profile: List[Tuple[float, float]],
                              freq_range: Tuple[float, float] = (100, 2000),
                              freq_step: float = 2.0,
                              temperature: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes the Input Impedance Z_in(f) for the given bore profile.

        Args:
            bore_profile: List of (x, radius) points in mm.
            freq_range: (min_freq, max_freq) in Hz.
            freq_step: Step size in Hz.
            temperature: Air temperature in Celsius.

        Returns:
            (frequencies, impedance_magnitude)
        """
        # Adjust constants for temperature
        # c = 331.3 + 0.606 * T
        c_sound = 331.3 + 0.606 * temperature
        rho = 1.2041 * (293.15 / (273.15 + temperature))

        freqs = self.xp.arange(freq_range[0], freq_range[1], freq_step)
        omega = 2 * self.xp.pi * freqs
        k = omega / c_sound

        # Initial Radiation Impedance (Open End Approximation)
        # Z_L = j * rho * c * tan(k * 0.61 * r_end) ? Or piston radiation?
        # Levine & Schwinger: Z_rad approx 0.25*(k*a)^2 + j*0.61*(k*a) * Z0 (for low ka)
        # Simplified: Z_load = 0 (ideal open) or characteristic Z_c.
        # For a flanged pipe, end correction is ~0.85a. Unflanged ~0.61a.
        # Let's use a standard approximation for the load at the end of the instrument.
        # Note: bore_profile is the BARREL + BODY.
        # If we only have the barrel, we must assume a body.
        # We will treat the profile as the entire air column for simulation purposes.

        # Extract geometry segments
        # We convert the profile points into a series of cylinders/cones.
        # x is in mm, radius is in mm. Convert to meters.

        x_pts = self.xp.array([p[0] for p in bore_profile]) / 1000.0
        r_pts = self.xp.array([p[1] for p in bore_profile]) / 1000.0

        # We assume open end at the last point
        r_exit = r_pts[-1]
        area_exit = self.xp.pi * r_exit**2
        z0_exit = rho * c_sound / area_exit

        # Radiation impedance (piston in infinite baffle approx for robustness)
        # ka = k * r_exit
        # Z_rad = z0_exit * (0.25 * (ka)**2 + 1j * 0.61 * ka)  <-- Approximation for low freq
        # Let's use a simpler formulation suitable for TMM iteration
        # Start with P/U at the end.
        # P_out = Z_rad * U_out. Let U_out = 1, then P_out = Z_rad.
        # State vector [P, U] = [Z_rad, 1]

        ka = k * r_exit
        # Radiation Impedance (Levine & Schwinger approximation for unflanged pipe)
        # Real part: 0.25 * (ka)**2
        # Imag part: 0.6133 * ka
        # Z_rad normalized by Z0
        z_rad_real = 0.25 * (ka**2)
        z_rad_imag = 0.6133 * ka
        Z_L = z0_exit * (z_rad_real + 1j * z_rad_imag)

        # Initial State Vector (at the open end)
        # We need to broadcast this for all frequencies
        # Shape: (2, N_freqs)
        P = Z_L  # Pressure
        U = self.xp.ones_like(freqs, dtype=self.xp.complex128) # Flow

        # Iterate backwards from open end to mouthpiece
        for i in range(len(x_pts) - 1, 0, -1):
            length = x_pts[i] - x_pts[i-1]
            r_avg = (r_pts[i] + r_pts[i-1]) / 2.0
            area = self.xp.pi * r_avg**2
            Z_c = rho * c_sound / area

            # Lossy wavenumber (thermoviscous losses)
            # alpha approx 3e-5 * sqrt(f) / r
            alpha = (3e-5 * self.xp.sqrt(freqs)) / r_avg
            gamma = alpha + 1j * k

            # Transfer Matrix Components for this segment
            # [ P_in ]   [ cosh(gamma L)      Z_c sinh(gamma L) ] [ P_out ]
            # [ U_in ] = [ (1/Z_c)sinh(gamma L)  cosh(gamma L)  ] [ U_out ]

            cosh_gL = self.xp.cosh(gamma * length)
            sinh_gL = self.xp.sinh(gamma * length)

            P_prev = P
            U_prev = U

            P = P_prev * cosh_gL + U_prev * Z_c * sinh_gL
            U = P_prev * (sinh_gL / Z_c) + U_prev * cosh_gL

        # Z_in at the mouthpiece
        Z_in = P / U

        if self.use_gpu:
            return freqs.get(), self.xp.abs(Z_in).get()
        else:
            return freqs, self.xp.abs(Z_in)

    def find_peaks(self, freqs: np.ndarray, impedance: np.ndarray, height_threshold: float = 1e5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Finds resonance peaks.
        """
        # Basic peak finding
        # We can't use scipy.signal on GPU arrays directly inside the GPU block easily without transfer
        # So we assume input is already CPU numpy arrays (as returned by compute_impedance_curve)

        from scipy.signal import find_peaks
        peaks, properties = find_peaks(impedance, height=np.mean(impedance)*0.5, distance=10)
        return freqs[peaks], impedance[peaks]

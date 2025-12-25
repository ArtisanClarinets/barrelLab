import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from backend.physics import PhysicsEngine
except ImportError:
    st.error("Could not import Physics Engine.")
    PhysicsEngine = None

logger = logging.getLogger(__name__)

def render():
    st.subheader("Acoustic Simulation Suite (TMM)")

    if not PhysicsEngine:
        return

    # Initialize Engine
    engine = PhysicsEngine(use_gpu=True)

    # Get Profile
    profile = st.session_state.bore_profile

    # Simulation Parameters
    col1, col2 = st.columns(2)
    with col1:
        temp = st.slider("Temperature (°C)", 0.0, 40.0, 20.0)
    with col2:
        max_freq = st.number_input("Max Frequency (Hz)", 1000, 5000, 2500)

    if st.button("Run Simulation"):
        with st.spinner("Calculating Impedance Spectrum..."):
            # Compute
            freqs, Z_mag = engine.compute_impedance_curve(
                bore_profile=profile,
                freq_range=(50, max_freq),
                freq_step=2.0,
                temperature=temp
            )

            # Find Peaks
            peaks_idx, _ = find_peaks(Z_mag, height=np.mean(Z_mag), distance=10)
            peak_freqs = freqs[peaks_idx]
            peak_mags = Z_mag[peaks_idx]

            # Store last result in session?
            st.session_state.last_sim_results = {
                "freqs": freqs,
                "impedance": Z_mag,
                "peaks": peak_freqs
            }

            # Plot
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(freqs, Z_mag, label="Input Impedance |Z|")
            ax.plot(peak_freqs, peak_mags, "rx", label="Resonances")
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Impedance Magnitude (Ω)")
            ax.set_title("Bore Input Impedance")
            ax.grid(True, which='both', alpha=0.3)
            ax.legend()
            st.pyplot(fig)

            # Analysis
            st.markdown("### Resonance Analysis")
            cols = st.columns(len(peak_freqs) if len(peak_freqs) < 6 else 4)
            for i, f in enumerate(peak_freqs[:8]): # Show top 8
                cols[i%4].metric(f"Mode {i+1}", f"{f:.1f} Hz")

            if len(peak_freqs) > 0:
                fundamental = peak_freqs[0]
                st.info(f"Fundamental Frequency: **{fundamental:.2f} Hz**")

                # Deviation from A4 (440) or target
                target = st.session_state.target_freq
                cents = 1200 * np.log2(fundamental / target)
                st.metric("Tuning (Cents relative to Target)", f"{cents:.1f}", delta_color="inverse")

    elif "last_sim_results" in st.session_state:
        # Re-render last result if exists
        res = st.session_state.last_sim_results
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(res["freqs"], res["impedance"], label="Input Impedance |Z|")
        ax.plot(res["peaks"], res["impedance"][np.isin(res["freqs"], res["peaks"])], "rx") # Simplified matching
        # Note: recovering exact peak height for simple replot might be tricky if not stored,
        # but good enough for UI persistence.
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Impedance Magnitude")
        ax.grid(True)
        st.pyplot(fig)

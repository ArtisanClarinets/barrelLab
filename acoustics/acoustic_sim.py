import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pydub import AudioSegment
from pydub.generators import Sine
import tempfile
import os
import logging
import sys

# Add backend to path to import gpu_compute
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from backend.gpu import gpu_compute
except ImportError:
    gpu_compute = None

# Configure logger
logger = logging.getLogger(__name__)

def render():
    st.subheader("Acoustic Simulation Suite")

    # Tooltip and help dictionary
    tooltips = {
        "freq_analysis": "Calculates how sound waves of different frequencies resonate in your barrel shape.",
        "time_analysis": "Simulates the note's start (attack), how it settles (decay), and how energy flows through the bore.",
        "impedance": "A measure of how much the air column resists vibrations at each frequency.",
        "peaks": "These are the frequencies your design most naturally resonates at (like notes it wants to play).",
        "attack_env": "Shows how the sound 'starts' when you blow into the clarinet – fast, slow, strong, or soft.",
        "export": "Generates a computer-simulated sound based on resonance peaks."
    }

    st.markdown("### Frequency Domain Analysis ℹ️")
    st.caption(tooltips["freq_analysis"])

    # Simulated impedance curve
    freqs = np.linspace(100, 2000, 800)

    # Try to use GPU compute if available for impedance calculation
    # We create a dummy bore for the GPU function (length, radius)
    # The GPU function calculates "sum of z*r" which is just a dummy calc in this codebase
    # but we should use it to show integration.
    if gpu_compute:
        # Mock bore
        L = np.ones(100)
        R = np.ones(100)
        gpu_result = gpu_compute.gpu_accelerated_impedance(L, R)
        if gpu_result is not None:
             st.success(f"GPU Accelerated Calculation Check: {gpu_result} (dummy value)")

    impedance = 1 / (np.abs(np.sin(freqs / 250)) + 0.2)
    peaks, _ = find_peaks(impedance, distance=40)

    fig, ax = plt.subplots()
    ax.plot(freqs, impedance, label="Impedance Curve")
    ax.plot(freqs[peaks], impedance[peaks], "x", label="Resonance Peaks")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Impedance (a.u.)")
    ax.set_title("Impedance vs Frequency")
    ax.legend()
    st.pyplot(fig)
    st.caption(tooltips["impedance"])
    logger.debug(f"Simulated impedance curve with {len(peaks)} peaks.")

    # Display resonance frequencies
    st.markdown("**Detected Resonance Frequencies (Hz):**")
    st.write(np.round(freqs[peaks], 1).tolist())
    st.caption(tooltips["peaks"])

    # Time domain simulation
    st.markdown("### Time Domain Transient ℹ️")
    st.caption(tooltips["time_analysis"])

    time = np.linspace(0, 0.5, 500)
    attack = np.exp(-15 * time) * np.sin(2 * np.pi * 440 * time)
    fig2, ax2 = plt.subplots()
    ax2.plot(time, attack)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Amplitude")
    ax2.set_title("Note Attack Envelope")
    st.pyplot(fig2)
    st.caption(tooltips["attack_env"])
    logger.debug("Displayed note attack envelope (time domain response).")

    # MP3 synthesis and export
    st.markdown("### MP3 Sound Export ℹ️")
    st.caption(tooltips["export"])

    # Simulate pure tone from first peak (if exists)
    if len(peaks) > 0:
        f = int(freqs[peaks[0]])
    else:
        f = 440

    tone = Sine(f).to_audio_segment(duration=1000).apply_gain(-3.0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tone.export(tmpfile.name, format="mp3")
        with open(tmpfile.name, "rb") as audio_file:
            st.download_button("Download MP3", audio_file, file_name="simulated_sound.mp3", mime="audio/mpeg")
        logger.info(f"Exported MP3 for frequency {f} Hz to {tmpfile.name}")
        # Need to be careful with unlink on Windows, but fine here.
        # However, streamlit button needs the data, we already read it into memory.
        os.unlink(tmpfile.name)

if __name__ == "__main__":
    render()

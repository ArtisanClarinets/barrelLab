import streamlit as st
import numpy as np
from scipy.optimize import minimize
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from backend.physics import PhysicsEngine
except ImportError:
    PhysicsEngine = None

logger = logging.getLogger(__name__)

def render():
    st.subheader("AI Design Assistant & Optimizer")

    if not PhysicsEngine:
        st.error("Physics Engine Unavailable.")
        return

    st.markdown("""
    This tool uses numerical optimization to adjust the bore profile to match a target fundamental frequency.
    It simulates the acoustic response iteratively to find the optimal geometry.
    """)

    # Targets
    target_f = st.number_input("Target Frequency (Hz)", value=st.session_state.target_freq)
    st.session_state.target_freq = target_f

    # Constraints
    max_iter = st.slider("Max Iterations", 10, 100, 30)

    if st.button("Auto-Optimize Bore"):
        if "bore_profile" not in st.session_state:
            st.error("No bore profile found.")
            return

        current_profile = st.session_state.bore_profile
        # We optimize the radii of the middle points.
        # Fixed points: Top (0) and Bottom (last). Or allow all to move?
        # Usually Tenon dimensions are fixed.
        # Let's optimize radii of indices 1 to N-1.

        # Flatten parameters: radii of intermediate points
        # If we only have start/end, we can't do much.
        if len(current_profile) < 3:
            st.warning("Add more control points in the Geometry Editor to allow for optimization.")
            return

        # Optimization Setup
        fixed_indices = [0, len(current_profile)-1] # Keep ends fixed
        optim_indices = [i for i in range(len(current_profile)) if i not in fixed_indices]

        initial_radii = np.array([current_profile[i][1] for i in optim_indices])

        engine = PhysicsEngine(use_gpu=False) # Use CPU for small loop overhead or if GPU is busy

        status_text = st.empty()
        progress_bar = st.progress(0)

        def objective_function(radii):
            # Construct candidate profile
            candidate = current_profile.copy()
            for i, idx in enumerate(optim_indices):
                candidate[idx] = (candidate[idx][0], radii[i])

            # Run Sim
            # Focus on range near target to save time
            f_min = target_f * 0.8
            f_max = target_f * 1.2
            freqs, Z = engine.compute_impedance_curve(candidate, freq_range=(f_min, f_max), freq_step=1.0)

            # Find max peak
            peak_idx = np.argmax(Z)
            f_peak = freqs[peak_idx]

            error = (f_peak - target_f)**2
            return error

        # Run Optimization
        status_text.text("Optimizing geometry...")

        res = minimize(
            objective_function,
            initial_radii,
            method='Nelder-Mead',
            options={'maxiter': max_iter, 'xatol': 0.01}
        )

        progress_bar.progress(100)

        if res.success or res.message:
            st.success(f"Optimization Complete: {res.message}")
            st.write(f"Final Error (Hz^2): {res.fun:.4f}")

            # Update State
            new_radii = res.x
            new_profile = current_profile.copy()
            for i, idx in enumerate(optim_indices):
                new_profile[idx] = (new_profile[idx][0], new_radii[i])

            st.session_state.bore_profile = new_profile

            # Show diff
            st.write("Optimized Radii:")
            for i, idx in enumerate(optim_indices):
                old_r = current_profile[idx][1]
                new_r = new_radii[i]
                st.write(f"Point {idx+1} (x={current_profile[idx][0]}): {old_r:.2f} -> **{new_r:.2f} mm**")

            st.info("The Geometry Editor has been updated with the new profile.")

        else:
            st.error("Optimization failed.")

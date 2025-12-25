import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def render():
    st.subheader("Material Properties & Aging")

    # Database
    materials = {
        "Grenadilla": {"density": 1300, "stiffness": 15.0, "damping": 0.005},
        "Cocobolo": {"density": 1100, "stiffness": 14.0, "damping": 0.006},
        "Boxwood": {"density": 950, "stiffness": 10.0, "damping": 0.010},
        "Hard Rubber": {"density": 1150, "stiffness": 3.0, "damping": 0.020},
        "ABS Plastic": {"density": 1050, "stiffness": 2.5, "damping": 0.015},
        "3D Print (PLA)": {"density": 1240, "stiffness": 3.5, "damping": 0.018}
    }

    current_mat = st.session_state.material
    if current_mat not in materials:
        current_mat = "Grenadilla"

    choice = st.selectbox("Select Material", list(materials.keys()), index=list(materials.keys()).index(current_mat))

    st.session_state.material = choice
    props = materials[choice]

    col1, col2, col3 = st.columns(3)
    col1.metric("Density (kg/m³)", props["density"])
    col2.metric("Stiffness (GPa)", props["stiffness"])
    col3.metric("Damping Factor", props["damping"])

    st.markdown("---")
    st.subheader("Aging Simulation")

    years = st.slider("Years of Use", 0, 50, 0)
    humidity_var = st.slider("Seasonal Humidity Delta (%)", 0, 50, 20)

    # Simulation Logic
    # Wood density changes slightly with resin loss (-0.5% per decade)
    # Stiffness increases with age (hardening) (+1% per decade)
    # Dimensional change: Shrinkage. Radial shrinkage ~0.1% per year approx?
    # Let's model Bore Shrinkage.

    shrinkage_factor = 0.0
    if choice in ["Grenadilla", "Cocobolo", "Boxwood"]:
        # Wood shrinks
        shrinkage_factor = 0.0005 * years * (1 + humidity_var/100.0)

    new_density = props["density"] * (1 - 0.0005 * years)
    new_stiffness = props["stiffness"] * (1 + 0.001 * years)

    st.write(f"**Predicted effects after {years} years:**")
    st.write(f"- Bore Shrinkage: {shrinkage_factor*100:.2f}% (approx {(shrinkage_factor*15.0):.3f} mm reduction)")
    st.write(f"- Density Change: {new_density:.1f} kg/m³")

    if st.button("Apply Aging to Geometry"):
        # Apply shrinkage to current bore
        profile = st.session_state.bore_profile
        new_profile = []
        for x, r in profile:
            new_r = r * (1.0 - shrinkage_factor)
            new_profile.append((x, new_r))
        st.session_state.bore_profile = new_profile
        st.success(f"Applied {shrinkage_factor*100:.2f}% shrinkage to bore profile.")

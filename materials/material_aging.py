import streamlit as st
import pandas as pd
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

def render():
    st.subheader("Material System and Aging Simulator")

    # Default wood database
    wood_data = {
        "Grenadilla": {"density": 1300, "stiffness": 15000, "damping": 0.005},
        "Cocobolo": {"density": 1100, "stiffness": 14000, "damping": 0.006},
        "Boxwood": {"density": 850, "stiffness": 10000, "damping": 0.01},
        "Maple": {"density": 700, "stiffness": 9000, "damping": 0.012},
    }

    # Display editable table
    df = pd.DataFrame(wood_data).T
    st.dataframe(df.style.format({"density": "{:.0f}", "stiffness": "{:.0f}", "damping": "{:.3f}"}))
    logger.debug("Displayed material database.")

    # Select wood
    wood_choice = st.selectbox("Select Wood", df.index.tolist())
    props = df.loc[wood_choice].to_dict()

    # Aging parameters
    years = st.slider("Years of Aging", 0, 50, 10, step=5)
    seasonal_humidity = st.slider("Average Seasonal Humidity Variation (%)", 0, 40, 15)

    # Simple humidity cycling + resinification model
    def simulate_aging(density, stiffness, damping, years, humidity_cycle):
        humidity_stress = 1 + 0.005 * humidity_cycle
        resin_effect = 1 - 0.0025 * years
        aged_density = density * (1 + 0.0008 * years * humidity_stress)
        aged_stiffness = stiffness * resin_effect * (1 - 0.001 * humidity_cycle)
        aged_damping = damping * (1 + 0.0009 * years * humidity_stress)
        return aged_density, aged_stiffness, aged_damping

    aged = simulate_aging(props["density"], props["stiffness"], props["damping"], years, seasonal_humidity)

    st.markdown("### Projected Aged Properties:")
    st.write(f"**Density**: {aged[0]:.1f} kg/m³")
    st.write(f"**Stiffness**: {aged[1]:.1f} MPa")
    st.write(f"**Damping**: {aged[2]:.4f}")

    logger.info(f"Aged properties for {wood_choice} at {years}y, ΔRH={seasonal_humidity}%: {aged}")

if __name__ == "__main__":
    render()

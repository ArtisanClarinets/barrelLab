import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import logging

# Setup logger
logger = logging.getLogger(__name__)

def render():
    st.subheader("Historical Bore Shape Viewer")

    # Define example bore profiles (length vs radius, in mm)
    bore_presets = {
        "Mozart Era Clarinet (~1780s)": {
            "length": np.linspace(0, 60, 60),
            "radius": np.interp(np.linspace(0, 60, 60), [0, 30, 60], [6.5, 7.2, 6.9]),
            "context": "Used in classical-era instruments. Small bore, optimized for soft articulation and even intonation with narrow tuning bands. Similar to early German clarinets."
        },
        "German Reform Boehm (~1930s)": {
            "length": np.linspace(0, 60, 60),
            "radius": np.interp(np.linspace(0, 60, 60), [0, 20, 40, 60], [7.2, 7.5, 7.3, 7.0]),
            "context": "Designed for rich tone and smooth resistance in orchestral settings. Still used in some European symphonic traditions today."
        },
        "Modern French Barrel (~1990s)": {
            "length": np.linspace(0, 60, 60),
            "radius": np.interp(np.linspace(0, 60, 60), [0, 15, 45, 60], [7.1, 7.3, 7.2, 6.95]),
            "context": "Standardized for balanced intonation with plastic and wooden clarinets. Often copied in student instruments."
        },
        "Jazz/Ebony Barrel (~Today)": {
            "length": np.linspace(0, 60, 60),
            "radius": np.interp(np.linspace(0, 60, 60), [0, 20, 60], [7.3, 7.7, 7.5]),
            "context": "Preferred by jazz artists for open airflow and projection. Usually paired with custom mouthpieces for expressive attack."
        }
    }

    # User selection
    preset_name = st.selectbox("Select Historical Bore Shape", list(bore_presets.keys()))
    preset = bore_presets[preset_name]
    z = preset["length"]
    r = preset["radius"]
    logger.info(f"Loaded preset: {preset_name}")

    # Optional overlay toggle
    overlay = st.checkbox("Overlay with My Design", value=True)

    # Load or simulate user design
    user_z = np.linspace(0, 60, 60)
    user_r = np.interp(user_z, [0, 20, 60], [7.0, 7.3, 7.0])

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=z, y=r, mode="lines", name=preset_name, line=dict(width=3)))
    if overlay:
        fig.add_trace(go.Scatter(x=user_z, y=user_r, mode="lines", name="My Design", line=dict(dash="dash")))

    fig.update_layout(
        title="Bore Radius vs Length",
        xaxis_title="Length Along Barrel (mm)",
        yaxis_title="Inner Radius (mm)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show modern-use context
    st.markdown("### Context (Modern Use)")
    st.info(preset["context"])

    logger.debug(f"Displayed bore profile and context for {preset_name}")

if __name__ == "__main__":
    render()

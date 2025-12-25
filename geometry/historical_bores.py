import streamlit as st
import numpy as np
import logging

logger = logging.getLogger(__name__)

def render():
    st.subheader("Historical Bore Shapes")

    presets = {
        "Mozart Era (Small Bore)": [
            (0.0, 14.2), (20.0, 14.4), (40.0, 14.3), (60.0, 13.8)
        ],
        "German Reform (Cylindrical)": [
             (0.0, 15.0), (30.0, 15.0), (60.0, 15.0)
        ],
        "Modern French (Polycylindrical)": [
             (0.0, 15.0), (15.0, 14.85), (45.0, 14.85), (66.0, 14.65)
        ],
        "Jazz/Open (Large Bore)": [
             (0.0, 15.2), (25.0, 15.1), (50.0, 15.0), (65.0, 14.8)
        ]
    }

    selected = st.selectbox("Choose a historical preset:", list(presets.keys()))

    st.info("Loading a preset will overwrite your current bore design.")

    if st.button("Load Preset"):
        st.session_state.bore_profile = presets[selected]
        st.success(f"Loaded {selected} profile.")
        st.rerun()

    # Preview
    st.markdown("### Preview Data")
    st.write(presets[selected])

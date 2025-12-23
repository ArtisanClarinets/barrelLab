import streamlit as st
import numpy as np
import logging

# Logging
logger = logging.getLogger(__name__)

def render():
    st.subheader("AI Design Assistant")

    # Target frequency input
    target_freq = st.slider("Target Fundamental Frequency (Hz)", 100, 2000, 440)
    st.caption("🎯 We'll suggest bore tweaks to match this frequency more accurately.")

    # Style preference slider
    style = st.select_slider("Design Style Preference", options=["Historical", "Orchestral", "Jazz", "Experimental"])
    st.caption("🎼 This helps the assistant shape the bore to match common tonal goals in different playing styles.")

    # Manufacturability constraints
    min_wall = st.slider("Minimum Wall Thickness Allowed (mm)", 0.5, 5.0, 1.0)
    st.caption("🛠️ Ensures the AI doesn't suggest geometries too thin to drill or print.")

    # Simulated input data (mocked for prototype)
    length_mm = 60
    radius_profile = np.linspace(7.0, 7.4, 60)  # simulate radius profile
    bore_volume = np.pi * np.mean(radius_profile)**2 * length_mm

    # AI Suggestion Logic (placeholder rules)
    predicted_freq = 343 / (2 * length_mm / 1000)
    deviation = abs(predicted_freq - target_freq)

    if deviation > 20:
        suggestion = "Try lengthening the bore by 3–5mm or increasing mid-radius slightly."
    elif deviation > 5:
        suggestion = "Minor tuning needed – small adjustment to end taper radius."
    else:
        suggestion = "Design closely matches target frequency. Good job!"

    # Defect predictions
    crack_risk = "Low" if min_wall > 1.5 else "Moderate"
    intonation_risk = "Minimal" if deviation < 10 else "Possible Issues"

    # Material suggestion logic
    material_rec = {
        "Historical": "Boxwood",
        "Orchestral": "Grenadilla",
        "Jazz": "Cocobolo",
        "Experimental": "Maple"
    }.get(style, "Grenadilla")

    # Display AI output
    st.markdown("### Optimization Result")
    st.write(f"Predicted Frequency: {predicted_freq:.1f} Hz")
    st.write(f"Deviation from Target: {deviation:.1f} Hz")
    st.success(suggestion)

    st.markdown("### Design Risk Predictions")
    st.write(f"⚠️ Cracking Risk: **{crack_risk}**")
    st.write(f"⚠️ Intonation Stability: **{intonation_risk}**")

    st.markdown("### Recommended Material")
    st.info(f"🎋 Suggested Wood: **{material_rec}** based on your tonal goals.")

    logger.info(f"Target: {target_freq}, Predicted: {predicted_freq}, Style: {style}, Suggestion: {suggestion}")

if __name__ == "__main__":
    render()

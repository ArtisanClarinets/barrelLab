import streamlit as st
import plotly.graph_objects as go
import logging

logger = logging.getLogger(__name__)

def render():
    st.subheader("2D Bore Cross-Section Editor")

    # Load from session state
    points = st.session_state.bore_profile

    # Sort by X to ensure validity
    points.sort(key=lambda p: p[0])

    # Unpack
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers+lines',
        name="Bore Profile",
        line=dict(shape='spline', smoothing=0.3)
    ))

    fig.update_layout(
        title="Current Profile",
        xaxis_title="Length (mm)",
        yaxis_title="Radius (mm)",
        height=400,
        hovermode="x"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Edit Points")
    st.caption("Adjust the geometry points below. Click 'Update Profile' to save.")

    # Dynamic form for points
    # We allow adding/removing points in a somewhat manual way for robustness

    with st.form("bore_edit_form"):
        col_list = st.columns(3)
        new_points = []

        # Display existing points
        for i, (x, r) in enumerate(points):
            with col_list[i % 3]:
                st.markdown(f"**Point {i+1}**")
                new_x = st.number_input(f"X (mm)", value=float(x), key=f"bx_{i}", min_value=0.0, max_value=200.0)
                new_r = st.number_input(f"Radius (mm)", value=float(r), key=f"br_{i}", min_value=1.0, max_value=30.0)
                new_points.append((new_x, new_r))

        # Add new point option
        st.markdown("---")
        add_point = st.checkbox("Add a new point at end?")

        submitted = st.form_submit_button("Update Profile")

        if submitted:
            if add_point:
                last_x = new_points[-1][0]
                new_points.append((last_x + 10.0, new_points[-1][1]))

            # Sort and Save
            new_points.sort(key=lambda p: p[0])
            st.session_state.bore_profile = new_points
            st.success("Profile updated!")
            st.rerun()

    # Reset
    if st.button("Reset to Standard 66mm"):
        st.session_state.bore_profile = [
            (0.0, 15.0),
            (20.0, 14.8),
            (40.0, 14.8),
            (66.0, 14.6)
        ]
        st.rerun()

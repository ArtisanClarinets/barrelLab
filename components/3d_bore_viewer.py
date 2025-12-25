import streamlit as st
import pyvista as pv
from pyvista import themes
import numpy as np
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

def render():
    st.subheader("3D Bore Viewer")

    # Get profile from state
    profile = st.session_state.bore_profile
    x_nodes = np.array([p[0] for p in profile])
    r_nodes = np.array([p[1] for p in profile])

    # Interpolate for smoother visual
    z_smooth = np.linspace(x_nodes[0], x_nodes[-1], 100)
    r_smooth = np.interp(z_smooth, x_nodes, r_nodes)

    # Create Mesh using StructuredGrid
    theta = np.linspace(0, 2*np.pi, 60)
    Z, Theta = np.meshgrid(z_smooth, theta)
    R = np.tile(r_smooth, (len(theta), 1))

    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)

    # Create StructuredGrid
    # X, Y, Z must be flattened in Fortran order
    grid = pv.StructuredGrid(X, Y, Z)

    # Plotting
    pv.set_plot_theme(themes.DocumentTheme())
    plotter = pv.Plotter(off_screen=True, notebook=False)

    # Add bore (inner surface)
    plotter.add_mesh(grid, color="tan", opacity=1.0, show_edges=False, smooth_shading=True)

    # Add outer surface (simple cylinder for context)
    # Outer radius approx 15mm + 5mm wall = 20mm
    outer_r = 20.0
    R_out = np.full_like(R, outer_r)
    X_out = R_out * np.cos(Theta)
    Y_out = R_out * np.sin(Theta)
    grid_out = pv.StructuredGrid(X_out, Y_out, Z)
    plotter.add_mesh(grid_out, color="brown", opacity=0.3, show_edges=False)

    plotter.add_axes()
    plotter.view_xy() # View from top?
    # Better view
    plotter.camera_position = 'yz'
    plotter.camera.azimuth = 45
    plotter.camera.elevation = 30

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            plotter.show(screenshot=tmpfile.name)
            st.image(tmpfile.name, caption="3D Representation (Inner & Outer)", use_container_width=True)
        os.unlink(tmpfile.name)
    except Exception as e:
        st.error(f"Error rendering 3D view: {e}")
        logger.error(f"3D Render Error: {e}")

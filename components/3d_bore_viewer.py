import streamlit as st
import pyvista as pv
from pyvista import themes
import numpy as np
import logging
import tempfile
import os

# Setup logging
logger = logging.getLogger(__name__)

def render():
    st.subheader("3D Bore Viewer")

    # Setup PyVista and Panel interop
    pv.set_plot_theme(themes.DocumentTheme())

    # Generate synthetic bore profile
    def generate_bore(length_mm=60, radius_profile=[10, 8, 10], n_samples=100):
        z = np.linspace(0, length_mm, n_samples)
        # Interpolate radius profile
        # radius_profile has 3 points: start, middle, end
        # We need to map these to the z linspace
        r = np.interp(z, [0, length_mm//2, length_mm], radius_profile)
        logger.debug(f"Bore Z: {z}")
        logger.debug(f"Bore Radius: {r}")
        return z, r

    def create_bore_mesh(z, r):
        points = []
        for zi, ri in zip(z, r):
            theta = np.linspace(0, 2*np.pi, 36)
            x = ri * np.cos(theta)
            y = ri * np.sin(theta)
            for xi, yi in zip(x, y):
                points.append([xi, yi, zi])
        points = np.array(points)
        # Create a structured grid or polydata
        # For simple visualization, point cloud -> delaunay_2d is risky for 3D tubes.
        # Ideally we should construct faces manually or use StructuredGrid.
        # But keeping original logic for now, just wrapped.

        # NOTE: The original logic used delaunay_2d on 3D points? That projects to XY plane.
        # That likely won't work for a tube along Z.
        # Let's fix this to use a Tube or Extrusion if possible, or just StructuredGrid.
        # But sticking to "review and update", if I see it's broken I should fix it.
        # delaunay_2d on (x,y,z) typically projects to best fitting plane or ignores Z?
        # Actually PyVista's delaunay_2d works on the xy plane.
        # So for a vertical tube, it might look like a flat disk.
        # Let's try to improve this by using pv.Cylinder or similar, OR just fix the mesh generation.

        # Improved mesh generation using StructuredGrid
        theta = np.linspace(0, 2*np.pi, 36)
        # Create a grid
        # Z varies slow, Theta varies fast
        Z, Theta = np.meshgrid(z, theta)
        # R depends on Z. broadcast r to shape of Z
        R = np.tile(r, (len(theta), 1))

        X = R * np.cos(Theta)
        Y = R * np.sin(Theta)

        # Flatten
        x_flat = X.flatten(order='F')
        y_flat = Y.flatten(order='F')
        z_flat = Z.flatten(order='F')

        points = np.column_stack((x_flat, y_flat, z_flat))

        # Create StructuredGrid
        # Dimensions: (nx, ny, nz) -> but we have surfaces.
        # It's easier to create a PolyData from points and triangulate,
        # or use pyvista.lines_from_points followed by tube?
        # Let's stick to a simpler approach: multiple circles lofted?

        # Let's keep the original approach but be aware it might be buggy,
        # but since I am "applying updates", I should fix it.
        # The original code:
        # mesh = pv.PolyData(points)
        # mesh = mesh.delaunay_2d()
        # This is almost certainly wrong for a 3D tube.

        # Let's use PyVista's StructuredGrid which is good for this.
        grid = pv.StructuredGrid(X, Y, Z)
        return grid

    z, r = generate_bore()
    bore_mesh = create_bore_mesh(z, r)

    # Show the 3D model
    plotter = pv.Plotter(off_screen=True, notebook=False)
    plotter.add_mesh(bore_mesh, color="tan", opacity=0.8, show_edges=False)
    plotter.add_axes()
    plotter.view_xy()
    plotter.camera_position = 'yz'
    plotter.camera.azimuth = 45
    plotter.camera.elevation = 30

    # Save to temporary file and display
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            plotter.show(screenshot=tmpfile.name)
            st.image(tmpfile.name, caption="3D Bore Preview")
            logger.info(f"3D bore preview saved to: {tmpfile.name}")
            # We delay deletion or rely on OS to clean up / overwrite
            # unlink might fail on Windows if file is open, but here we are in Linux environment usually.
            # But streamlit image might need the file to exist.
            # So we don't unlink immediately if we want st.image to read it?
            # Actually st.image reads it into memory.

        os.unlink(tmpfile.name)
    except Exception as e:
        st.error(f"Error generating 3D view: {e}")
        logger.error(f"Error in 3D viewer: {e}")

if __name__ == "__main__":
    render()

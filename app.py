import streamlit as st
import logging

# Import components
# Using local imports to avoid circular dependency issues if any, although unlikely here
try:
    import importlib
    bore_viewer = importlib.import_module("components.3d_bore_viewer")
except ImportError as e:
    st.error(f"Failed to load 3D Viewer: {e}")

from geometry import bore_editor, historical_bores
from acoustics import acoustic_sim
from ai_assistant import ai_designer
from materials import material_aging

# Setup logging
import logging.config
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Clarinet Barrel Lab", layout="wide")

st.sidebar.title("Clarinet Barrel Lab")
section = st.sidebar.radio("Go to", [
    "Interactive Geometry",
    "Acoustic Simulation",
    "AI Design Assistant",
    "Material & Aging",
    "Manufacturing Tools",
    "Extended Reality",
    "Education"
])

st.title("Clarinet Barrel Design Platform")

if section == "Interactive Geometry":
    st.info("This section includes the 2D Bore Editor, 3D Visualizer, Insert Designer, and more.")

    tab1, tab2, tab3 = st.tabs(["2D Editor", "3D Viewer", "Historical Shapes"])

    with tab1:
        bore_editor.render()

    with tab2:
        bore_viewer.render()

    with tab3:
        historical_bores.render()

elif section == "Acoustic Simulation":
    st.info("This section includes Impedance calculators, resonance visualizers, and waveform export.")
    acoustic_sim.render()

elif section == "AI Design Assistant":
    st.info("AI-guided optimization and historical style transfer tools.")
    ai_designer.render()

elif section == "Material & Aging":
    st.info("Material DB, aging simulation, and sustainability tracker.")
    material_aging.render()

elif section == "Manufacturing Tools":
    st.info("G-code export, 3D print analyzer, tolerance checker, cost estimator.")
    st.warning("Module under development.")

elif section == "Extended Reality":
    st.info("AR/VR-based overlay preview and acoustic projection simulator.")
    st.warning("Module under development.")

elif section == "Education":
    st.info("Bore design sandbox, acoustics 101, and historical clarinet library.")
    st.warning("Module under development.")

import streamlit as st
import importlib
import logging.config

# Setup logging
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Initialize Session State for the "Barrel Project"
if "bore_profile" not in st.session_state:
    # Default Profile: List of (x_mm, radius_mm)
    # A standard clarinet barrel is ~66mm.
    # A standard bore is ~14.6mm to 15mm.
    st.session_state.bore_profile = [
        (0.0, 15.0),    # Top (Receiver)
        (20.0, 14.8),   # Upper Taper
        (40.0, 14.8),   # Lower Taper
        (66.0, 14.6)    # Bottom (Tenon)
    ]

if "material" not in st.session_state:
    st.session_state.material = "Grenadilla"

if "target_freq" not in st.session_state:
    st.session_state.target_freq = 440.0 # A4

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

# Dynamic Imports to avoid heavy startup and circular deps
def load_module(name):
    try:
        return importlib.import_module(name)
    except ImportError as e:
        st.error(f"Failed to load module {name}: {e}")
        return None

if section == "Interactive Geometry":
    st.info("Design your barrel profile using the editor below. The 3D view updates automatically.")

    bore_editor = load_module("geometry.bore_editor")
    bore_viewer = load_module("components.3d_bore_viewer")
    historical_bores = load_module("geometry.historical_bores")

    tab1, tab2, tab3 = st.tabs(["2D Editor", "3D Viewer", "Historical Shapes"])

    with tab1:
        if bore_editor: bore_editor.render()

    with tab2:
        if bore_viewer: bore_viewer.render()

    with tab3:
        if historical_bores: historical_bores.render()

elif section == "Acoustic Simulation":
    st.info("Simulate the acoustic response using Transfer Matrix Method (TMM).")
    acoustic_sim = load_module("acoustics.acoustic_sim")
    if acoustic_sim: acoustic_sim.render()

elif section == "AI Design Assistant":
    st.info("AI-guided optimization to tune your barrel to a specific frequency.")
    ai_designer = load_module("ai_assistant.ai_designer")
    if ai_designer: ai_designer.render()

elif section == "Material & Aging":
    st.info("Select materials and simulate aging effects on dimensions and density.")
    material_aging = load_module("materials.material_aging")
    if material_aging: material_aging.render()

elif section == "Manufacturing Tools":
    st.info("G-code export, 3D print analyzer, tolerance checker, cost estimator.")
    st.warning("Module under development. Future updates will include G-Code generation.")

elif section == "Extended Reality":
    st.info("AR/VR-based overlay preview and acoustic projection simulator.")
    st.warning("Module under development.")

elif section == "Education":
    st.info("Bore design sandbox, acoustics 101, and historical clarinet library.")
    st.warning("Module under development.")

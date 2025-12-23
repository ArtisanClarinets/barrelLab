# gpu_compute.py
import logging
import numpy as np

# Try importing cupy, but don't fail if it's not available or if CUDA is missing
try:
    import cupy as cp
    # Check if a GPU is actually available and working
    try:
        if cp.cuda.is_available():
             HAS_GPU = True
        else:
             HAS_GPU = False
    except Exception:
        HAS_GPU = False
except ImportError:
    HAS_GPU = False
    cp = None

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def gpu_accelerated_impedance(lengths, radii):
    """
    Computes impedance. Uses GPU if available, otherwise falls back to CPU (numpy).
    """
    if HAS_GPU and cp:
        logger.info("Running GPU impedance computation...")
        try:
            z = cp.array(lengths) * cp.array(radii)
            result = cp.sum(z)
            logger.info("GPU computation successful.")
            return result.get()
        except Exception as e:
            logger.error(f"GPU error: {e}. Falling back to CPU.")
            # Fallback to CPU if GPU computation fails
            pass

    logger.info("Running CPU impedance computation (fallback)...")
    z = np.array(lengths) * np.array(radii)
    result = np.sum(z)
    return result

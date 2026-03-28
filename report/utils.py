import pickle
from pathlib import Path


# Absolute path to the root of the project directory
project_root = Path(__file__).parent.parent

# Path to the trained ML model file inside assets folder
model_path = project_root / "assets" / "model.pkl"


def load_model():
    """Load and return the trained ML model from disk."""
    with model_path.open('rb') as file:
        model = pickle.load(file)
    return model
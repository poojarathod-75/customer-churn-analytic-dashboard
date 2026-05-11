"""
Handles file loading
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def load_csv(file) -> pd.DataFrame:
    """
    Load CSV file into DataFrame.

    Args:
        file: Uploaded file

    Returns:
        pd.DataFrame

    Example:
        df = load_csv(file)
    """
    try:
        df = pd.read_csv(file)
        logging.info("CSV loaded successfully")
        return df
    except Exception as e:
        logging.error(f"Error loading CSV: {e}")
        raise ValueError("Invalid CSV file")
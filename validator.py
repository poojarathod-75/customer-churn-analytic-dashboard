"""
Input validation
"""

import logging

logging.basicConfig(level=logging.INFO)

def validate_file(filename: str) -> bool:
    """
    Validate file type

    Args:
        filename (str)

    Returns:
        bool
    """
    try:
        return filename.endswith(".csv")
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return False
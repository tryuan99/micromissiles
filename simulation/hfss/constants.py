"""HFSS constants."""


def ghz(value: float) -> float:
    """Converts GHz to Hz for readable HFSS configuration.
    
    Args:
        value: Value in GHz.
    
    Returns:
        The value in HZ.
    """
    return value * 1e9

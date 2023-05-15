# https://github.com/octaprog7/SCD4x/blob/master/sensor_pack/converter.py
def pa_mmhg(value: float) -> float:
    """Convert air pressure from Pa to mm Hg."""
    return 7.50062E-3 * value

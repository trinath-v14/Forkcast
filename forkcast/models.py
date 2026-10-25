from typing import Any
LENS_LABELS={"practical":"Practical Fit","risk":"Risk & Resilience","growth":"Future Growth"}
def number(value: Any, default: float=0.0)->float:
    try:
        result=float(value)
        return result if result==result else default
    except (TypeError,ValueError):
        return default

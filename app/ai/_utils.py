# app/ai/_utils.py
from datetime import datetime, timedelta
import numpy as np

def safe_div(a, b):
    try:
        return a / b if b else 0.0
    except Exception:
        return 0.0
    
def days_since(dt):
    if not dt:
        return None
    return (datetime.utcnow() - dt).days

def normalize_scores(arr):
    arr = np.array(arr, dtype=float)
    if len(arr) == 0:
        return []
    mn, mx = arr.min(), arr.max()
    if mx == mn:
        return (arr - mn)  # zeros
    return (arr - mn) / (mx - mn)

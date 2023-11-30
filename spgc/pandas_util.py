def idxwhere(boolean_series, x=None):
    if x is None:
        x = boolean_series
    return x[boolean_series].index

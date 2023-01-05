import numpy as np


def hour_angle_to_rad(h, m=None, s=None):
    # https://en.wikipedia.org/wiki/Right_ascension
    if m is None:
        return np.pi * h / 12
    else:
        return np.pi * (h / 12 + m / 720 + s / 43200)

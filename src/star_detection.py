import numba as nb
import numpy as np
import cv2

_argmax = lambda I: np.array(np.unravel_index(np.argmax(I), I.shape))[::-1]
_argsort2d = lambda I: np.array(np.unravel_index(np.argsort(I, axis=None), I.shape)).T


@nb.njit
def gaussian_window_filter(img, w=5):
    """find stars using probability theory"""
    assert w % 2 == 1
    hw = w // 2
    img_filtered = np.zeros((img.shape[0] - w, img.shape[1] - w), dtype="uint8")
    for iy in range(img.shape[0] - w):
        for ix in range(img.shape[1] - w):
            m = np.mean(img[iy : iy + w, ix : ix + w])
            v = np.var(img[iy : iy + w, ix : ix + w])
            std = np.sqrt(v)
            img_filtered[iy, ix] = (
                img[iy + hw, ix + hw] if (img[iy + hw, ix + hw] >= m + 2 * std) else 0
            )
            # img_filtered[iy, ix] = 255 if (img[iy+hw, ix+hw] >= m+2*std) else 0
    return img_filtered


def detect_stars(img, radius=15, treshold=70, max_stars=30):
    """star-detection: finding local maxima via treshold, size = cumulated luminocity in blurred neighborhood"""
    I = np.copy(img)
    blurred = cv2.GaussianBlur(I, (31, 31), 0)
    ordered_minima = _argsort2d(I)[::-1]  # from highest value to lowest
    visited_mask = np.zeros(len(ordered_minima), dtype=bool)
    local_minima = np.zeros((max_stars, 2))
    minima_brightness = np.zeros(max_stars)
    n_stars = 0  # number of detected stars
    i_star = 0
    for i, idx in enumerate(ordered_minima):
        iy = idx[0]
        ix = idx[1]
        if (I[iy, ix] < treshold) or (i_star >= max_stars):
            n_stars = i_star
            print(f"[star detection] detected {n_stars} stars")
            break
        if visited_mask[i] == True:
            continue

        # remove all indices in radius from ordered minima
        # (currently square instead of circle)
        nghb = (np.abs(ordered_minima[:, 0] - iy) <= radius) & (
            np.abs(ordered_minima[:, 1] - ix) <= radius
        )
        visited_mask = visited_mask | nghb

        # look up how deep idx can be seen in scalespace
        minima_brightness[i_star] = np.sum(
            blurred[
                np.max([iy - radius, 0]) : np.min([iy + radius, blurred.shape[0]]),
                np.max([ix - radius, 0]) : np.min([ix + radius, blurred.shape[1]]),
            ]
        )
        local_minima[i_star, :] = idx
        i_star += 1
    return local_minima[:n_stars], minima_brightness[:n_stars]

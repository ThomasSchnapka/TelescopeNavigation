"""class representing grid to choose stars in. Mainly used for storing parameters"""
from copy import deepcopy
import numpy as np

is_rad = lambda x: (x >= 0) & (x <= 2 * np.pi)


class Grid:
    """
    Class representing grid to choose stars in.

    For each grid cell, the `n_brgh` brightest stars are used for the hashing procedure.
    The grid gets halved "depth" times, resulting in 4 times more cells per iteration.

    Because RA points from west to east, ra_start must be larger than ra_end.

    Attributes:
    ----------
        ra_start:  float, right ascension of 'lower left' grid corner, in RAD
        dec_start: float, declination of 'lower left' grid corner, in RAD
        ra_end:    float, right ascension of 'upper right' grid corner, in RAD
        dec_end:   float, declination of 'upper right' grid corner, in RAD
        n_ra:      int, number of cells in eastward direction
        n_dec:     int, number of cells in northward direction
        n_brgh:    int, number of brightest stars to choose per cell
        depth :    int, how often the grid of depth 0 is halved
    """

    def __init__(
        self, ra_start, dec_start, ra_end, dec_end, n_ra, n_dec, n_brgh, depth
    ):
        assert is_rad(ra_start), ra_start
        assert is_rad(dec_start), dec_start
        assert is_rad(ra_end), ra_end
        assert is_rad(dec_end), dec_end
        assert ra_start > ra_end, (ra_start, ra_end)  # RA increases eastwards
        assert dec_start < dec_end, (dec_start, dec_end)

        self.ra_start = ra_start
        self.dec_start = dec_start
        self.ra_end = ra_end
        self.dec_end = dec_end
        self.n_ra = n_ra
        self.n_dec = n_dec
        self.n_brgh = n_brgh
        self.depth = depth

        self.ra_width = (ra_end - ra_start) / n_ra
        self.dec_width = (dec_end - dec_start) / n_dec

    def descend(self):
        """return grid with halved grid width"""
        deep_grid = deepcopy(self)
        deep_grid.n_ra = self.n_ra * 2
        deep_grid.n_dec = self.n_dec * 2

        deep_grid.ra_width = (self.ra_end - self.ra_start) / deep_grid.n_ra
        deep_grid.dec_width = (self.dec_end - self.dec_start) / deep_grid.n_dec
        return deep_grid

"""class representing grid to choose stars in. Mostly used for storing parameters"""
from copy import deepcopy
import numpy as np


class Grid():
    '''class representing grid to choose stars in'''
    def __init__(self, D0_ra=0.99, D0_dec=0.42, n_ra=10, n_dec=10, d_ra=0.01,
                 d_dec=0.01, n_brgh=2, f_decr=3, n_iter=2):
        self.D0_ra  = D0_ra   # grid center
        self.D0_dec = D0_dec  # grid center
        self.n_ra   = n_ra    # number of cells
        self.n_dec  = n_dec   # number of cells
    
        self.d_ra   = d_ra    # initial cell width (right ascension)
        self.d_dec  = d_dec   # initial cell width (declination)
        self.n_brgh = n_brgh  # max amount of stars to permutate from each cell
        self.f_decr = f_decr  # fraction by which subgrid is decreased
        self.n_iter = n_iter  # number of subgrids
        
        self.origin_ra = D0_ra - (n_ra*d_ra)/2
        self.origin_dec = D0_dec - (n_dec*d_dec)/2
        
    def copy(self, frac):
        """return subgrid with fraction"""
        subgrid = deepcopy(self)
        subgrid.d_ra  = subgrid.d_ra/frac
        subgrid.d_dec = subgrid.d_dec/frac
        subgrid.n_ra  = subgrid.n_ra*frac
        subgrid.n_dec = subgrid.n_dec*frac
        return subgrid
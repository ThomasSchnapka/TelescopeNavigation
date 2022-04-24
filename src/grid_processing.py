import pandas as pd
import numpy as np
from copy import deepcopy

class Grid():
    def __init__(self, D0_ra=0.99, D0_dec=0.42, n_ra=10, n_dec=10, d_ra=0.02,
                 d_dec=0.02, n_brgh=2, f_decr=2, n_iter=2):
        self.D0_ra  = D0_ra   # grid center (for testing)
        self.D0_dec = D0_dec  # grid center (for testing)
        self.n_ra   = n_ra    # number of cells (determines total grid width, for testing)
        self.n_dec  = n_dec   # number of cells (determines total grid width, for testing)
    
        self.d_ra   = d_ra    # initial cell width (right ascension)
        self.d_dec  = d_dec   # initial cell width (declination)
        self.n_brgh = n_brgh  # amount of stars to permutate from each cell
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


def stars_in_grid(df, grid):
    """
    return matrix containing stars in cells. if no star is found, the row is 
    filled with -1

    Matrix cols: grid_col | grid_row | mag_order | star_id
    
    This function is designed to be called for each subgrid individually. Use
    iterative_stars_in_grid(..) for whole grid

    Parameters
    ----------
    df : dataFrame containing stars
    grid : Grid() object

    Returns
    -------
    mat : (n, 4) matrix where n is the number of choosen stars

    """
    mat = np.ones((grid.n_ra*grid.n_dec*grid.n_brgh, 4), dtype=int)*-1
    
    grid_ra = grid.origin_ra   + np.arange(0, grid.n_ra +1)*grid.d_ra
    grid_dec = grid.origin_dec + np.arange(0, grid.n_dec+1)*grid.d_dec
    
    # find and plot brightest stars in cell
    for i_ra in range(grid.n_ra):
        for i_dec in range(grid.n_dec):
            choice = (  (df["ra"]  < grid_ra[i_ra+1])   & (df["ra"] >= grid_ra[i_ra])
                      & (df["dec"] < grid_dec[i_dec+1]) & (df["dec"] >= grid_dec[i_dec]))
            in_grid = df.loc[choice]
            brightest = in_grid.sort_values(by="mag").iloc[:grid.n_brgh]
            for i_br in range(len(brightest)):
                i_mat = (i_ra*grid.n_ra + i_dec)*grid.n_brgh + i_br
                mat[i_mat, 0] = i_ra
                mat[i_mat, 1] = i_dec
                mat[i_mat, 2] = i_br
                mat[i_mat, 3] = brightest.iloc[i_br].name
    return mat


def stars_in_total_grid(df, grid):
    """
    return matrix containing stars in cells, including all subgrids. If no star 
    is found in a cell, the row is filled with -1

    Matrix cols: i_iter | grid_col | grid_row | mag_order | star_id

    Parameters
    ----------
    df : dataFrame containing stars
    grid : Grid() object

    Returns
    -------
    tot_mat : (n, 5) matrix where n is the number of choosen stars

    """
    
    tot_mat = np.empty((0,5), dtype=int)
    for i_gi in range(grid.n_iter):
        # construct subgrid
        frac = grid.f_decr**i_gi
        subgrid = grid.copy(frac)
        
        # find stars in grid
        mat = stars_in_grid(df, subgrid)
        
        # add i_iter information and add to total grid
        mat = np.hstack((i_gi*np.ones((mat.shape[0],1), dtype=int), mat))
        tot_mat = np.vstack((tot_mat, mat))
    return tot_mat
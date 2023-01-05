import numpy as np
from copy import deepcopy

from src import hashing as hsh
from src.BrightestInGrid import BrightestInGrid
from src.HashTable import HashTable
from src.Grid import Grid
from src.StarChart import StarChart


def _stars_in_subgrid(sc, grid):
    """
    return matrix containing stars in cells. if no star is found, the row is 
    filled with -1

    Matrix cols: grid_col | grid_row | mag_order | star_id

    Parameters
    ----------
    sc : StarChart() object with sorted stars
    grid : Grid() object

    Returns
    -------
    StarsInGridCells object with brightest stars in grid cell

    """
    grid_stars = BrightestInGrid(grid)
    
    # grid coordinates
    grid_ra  = grid.ra_start  + np.arange(0, grid.n_ra +1)*grid.ra_width  # decreasing
    grid_dec = grid.dec_start + np.arange(0, grid.n_dec+1)*grid.dec_width # increasing
    
    # find brightest stars in cell
    for i_ra in range(grid.n_ra):
        for i_dec in range(grid.n_dec):
            in_grid = np.argwhere(  
                        (sc.ra  > grid_ra[i_ra+1])   & (sc.ra <= grid_ra[i_ra])
                      & (sc.dec < grid_dec[i_dec+1]) & (sc.dec >= grid_dec[i_dec])
                      ).flatten()
            for i_br in range(np.min([grid.n_brgh, len(in_grid)])):
                grid_stars.add_star(i_ra, i_dec, i_br, in_grid[i_br])
    return grid_stars


def brightest_star_per_cell(star_chart, grid):
    """
    return matrix containing stars in cells, including all subgrids. If no star 
    is found in a cell, the row is filled with -1

    Parameters
    ----------
    star_chart : StarChart() object
    grid : Grid() object

    Returns
    -------
    grid_stars_vec : vector (list) of grid_stars objects

    """
    
    grid_stars_vec = []
    for i_gi in range(grid.n_iter):
        # construct subgrid
        frac = grid.f_decr**i_gi
        subgrid = grid.copy(frac)
        
        # find and appends stars in subgrid
        subgrid_stars = _stars_in_subgrid(star_chart, subgrid)
        grid_stars_vec.append(subgrid_stars)
        
    return grid_stars_vec


def permute_and_hash(sc, grid_stars, i_ra, i_dec):
    # stars id's of adjacent grid cells
    idc_a = grid_stars.get_cell_stars(i_ra,   i_dec  )
    idc_b = grid_stars.get_cell_stars(i_ra+1, i_dec  )
    idc_c = grid_stars.get_cell_stars(i_ra,   i_dec+1)
    idc_d = grid_stars.get_cell_stars(i_ra+1, i_dec+1)
    
    if (len(idc_a)==0 | len(idc_b)==0 | len(idc_c)==0 | len(idc_d)==0):
        return HashTable(0)
    subhtable = HashTable(len(idc_a)*len(idc_b)*len(idc_c)*len(idc_d))
    for i_a in idc_a:
        for i_b in idc_b:
            for i_c in idc_c:
                for i_d in idc_d:
                    
                    pos = np.array([[sc.ra[i_a], sc.dec[i_a]],
                                    [sc.ra[i_b], sc.dec[i_b]],
                                    [sc.ra[i_c], sc.dec[i_c]],
                                    [sc.ra[i_d], sc.dec[i_d]]])
                    code, origin, alpha, scale = hsh.generate_quad_code(pos, return_geometry=True)
                    idc = np.array([i_a, i_b, i_c, i_d])
                    subhtable.add_row(code, origin, alpha, scale, idc)
    return subhtable
                    
            
def build_hashtable(star_chart, grid_spec):
    """
    create hashtable based on given grids, where the subgrids are build by halving the original
    grid with `width` times.
    

    Parameters
    ----------
    star_chart : StarChart() object
    grid_spec : dict, keyword dict for first grid object with depth 0

    Returns
    -------
    table : HashTable, reference table with hashcodes and stars

    """

    grid = Grid(**grid_spec)
    htable = HashTable(0)

    for i_depth in range(grid.depth):
        print(f"[build_hashtable()] depth {i_depth}")
        #brightest_in_grid = _stars_in_subgrid(star_chart, grid)
        for i_ra in range(grid.n_ra-1):
            for i_dec in range(grid.n_dec-1):
                brightest_in_grid = _stars_in_subgrid(star_chart, grid)
                subhtable = permute_and_hash(star_chart, brightest_in_grid, i_ra, i_dec)
                htable.append(subhtable)

        grid = grid.descend()

    if len(htable.codes)==0:
        raise RuntimeError("No hashcodes for given configuration")

    return htable
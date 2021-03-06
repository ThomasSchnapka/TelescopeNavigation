import numpy as np
from copy import deepcopy
from src import hashing as hsh
from src import GridStars
from src import HashTable


def _stars_in_subgrid(sc, grid):
    """
    return matrix containing stars in cells. if no star is found, the row is 
    filled with -1

    Matrix cols: grid_col | grid_row | mag_order | star_id
    
    This function is designed to be called for each subgrid individually. Use
    iterative_stars_in_grid(..) for whole grid

    Parameters
    ----------
    sc : StarChart() object with sorted stars
    grid : Grid() object

    Returns
    -------
    mat : (n, 4) matrix where n is the number of choosen stars

    """
    grid_stars = GridStars(grid)
    
    # grid coordinates
    grid_ra  = grid.origin_ra  + np.arange(0, grid.n_ra +1)*grid.d_ra
    grid_dec = grid.origin_dec + np.arange(0, grid.n_dec+1)*grid.d_dec
    
    # find brightest stars in cell
    for i_ra in range(grid.n_ra):
        for i_dec in range(grid.n_dec):
            in_grid = np.argwhere(  
                        (sc.ra  < grid_ra[i_ra+1])   & (sc.ra >= grid_ra[i_ra])
                      & (sc.dec < grid_dec[i_dec+1]) & (sc.dec >= grid_dec[i_dec])
                      ).flatten()
            for i_br in range(np.min([grid.n_brgh, len(in_grid)])):
                grid_stars.add_star(i_ra, i_dec, i_br, in_grid[i_br])
    return grid_stars


def stars_in_total_grid(sc, grid):
    """
    return matrix containing stars in cells, including all subgrids. If no star 
    is found in a cell, the row is filled with -1


    Parameters
    ----------
    sc : StarChart() object
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
        subgrid_stars = _stars_in_subgrid(sc, subgrid)
        grid_stars_vec.append(subgrid_stars)
        
    return grid_stars_vec


def permute_and_hash(sc, grid_stars, i_ra, i_dec):
    # stars id's of adjacent grid cells
    idc_a = grid_stars.get_cell_stars(i_ra,   i_dec  )
    idc_b = grid_stars.get_cell_stars(i_ra+1, i_dec  )
    idc_c = grid_stars.get_cell_stars(i_ra,   i_dec+1)
    idc_d = grid_stars.get_cell_stars(i_ra+1, i_dec+1)
    
    if (len(idc_a)==0 | len(idc_b)==0 | len(idc_c)==0 | len(idc_d)==0):
        return np.empty((0, 12))
    subhtable = HashTable((len(idc_a)*len(idc_b)*len(idc_c)*len(idc_d)), 12)
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
                    subhtable.add(code, origin, alpha, scale, idc)
    return subhtable
                    
            
def reference_grid_hashtable(sc, grid_stars_vec, grid):
    """
    create reference hashtable based on grid. grid_stars are calculated outside
    this function to use them for plots.
    
    The reference table structure is
    ( code | code | code | code | origin | origin | alpha | scale | iA | iB | iC | iD )
     - 'code' 4 hashcode values
     - 'origin' origin of hash coordinate system in celectial coordiantes
     - 'scale'  scale of hash cordinate system
     - 'i*'     indices of stars creating hash coordinate system corresponding
                to dataframe
    

    Parameters
    ----------
    sc : StarChart() object
    grid_stars : matrix containing stars in cells, 
                 as returned by stars_in_total_grid()
    grid : Grid() instance

    Returns
    -------
    table : reference table with hashcodes and stars

    """
    
    # allocate memory with predicted length
    htable = HashTable(0)
    
    i_cnt = 0
    for i_iter in range(grid.n_iter):
        #i_iter | grid_col | grid_row | mag_order | star_id
        print(f"[reference hashtable] Hash generation iteration {i_iter}")
        frac = grid.f_decr**i_iter
        subgrid_stars = grid_stars_vec[i_iter]
        for i_ra in range(grid.n_ra*frac-1):
            for i_dec in range(grid.n_dec*frac-1):
                subhtable = permute_and_hash(sc, subgrid_stars, i_ra, i_dec)
                htable.append(subhtable)
    return htable
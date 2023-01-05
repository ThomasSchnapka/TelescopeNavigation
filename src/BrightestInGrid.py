"""Table containing brightest stars per grid cell"""
from numba.experimental import jitclass
import numpy as np

#@jitclass
class BrightestInGrid():
    def __init__(self, grid):
        """
        Table containing brightest stars in grid cells. Each subgrid has its
        own StarsInGridCells object. Number of stars per cell is grid.n_brgh
        
        star_id corresponds to entry in star chart
        """
        
        shape = (grid.n_ra, grid.n_dec, grid.n_brgh)
        
        self.grid      = grid
        self.star_id   = np.ones(shape, dtype=int)*-1
        
        
    def add_star(self, i_ra, i_dec, i_brgh, star_id):
        self.star_id[i_ra, i_dec, i_brgh] = star_id
        
        
    def get_cell_stars(self, i_ra, i_dec):
        """get up to n_brigh brightest stars for specific cell, -1 values are filtered"""
        stars = self.star_id[i_ra, i_dec, :]
        return stars[stars>0]
    
    
    def __repr__(self):
        return f"GridStars table with shape {self.star_id.shape} entries"
    
    
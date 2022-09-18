import pandas as pd
import numpy as np

 # allow imports from parent folder
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src import plot
from src import grid_processing as gp
from src import hashing as hsh
from src.Grid import Grid

##### Data Handling ########################################################

# downloaded from https://github.com/astronexus/HYG-Database

df = pd.read_csv("data/hygdata_v3.csv", sep=",")
df = df[["ra", "dec", "proper", "mag"]]

# convert to rad (hour angle and deg)
df.loc[:,"ra"] = np.pi*df["ra"]/12
df.loc[:,"dec"] = np.pi*df["dec"]/180

##### CREATE GRID ########################################################
    
grid = Grid()
grid_stars = gp.stars_in_total_grid(df, grid)
hashcodes = gp.reference_grid_hashtable(df, grid_stars, grid)


##### PLOT ################################################################

# parameters
ra_center, dec_center = df[["ra", "dec"]].loc[df["proper"]=="Alcyone"].values[0] + [0.01, 0.01]
fov = 8*np.pi/180
#ra_center, dec_center = df[["ra", "dec"]].loc[df["proper"]=="Alioth"].values[0]
#fov = 2*np.pi/30 #160

# plot stars
fig, ax = plot.plot_star_selection(df, ra_center, dec_center, fov, tan_proj=False)
fig.suptitle("Pleiades", size=40)

# plot grid and grid stars
plot.draw_grid_cells(ax, grid)
plot.draw_grid_stars(ax, grid_stars, df)

























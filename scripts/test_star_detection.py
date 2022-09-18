import numpy as np
import numba as nb
import cv2
import matplotlib.pyplot as plt
import matplotlib.colors as colors

 # allow imports from parent folder
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src import plot
from src import hashing as hsh
from src import star_detection as sd
from src import grid_processing as gp
from src import hashing as hsh
from src.StarChart import StarChart
from src.Grid import Grid

### IMAGE #####################################################################
# img_name = "Pleiades-DJ-900px.jpg"
img_name = "bitterli.jpg"
# #img_name = "aachen.jpg"
img = cv2.imread("data/"+img_name, cv2.IMREAD_GRAYSCALE)
                 
                                
img_filtered = sd.gaussian_window_filter(img, 25)
local_minima, minima_brightness = sd.detect_stars(img_filtered)
imgcode, imgA, imgalpha, imgscale = hsh.generate_hash_codes(local_minima, minima_brightness)


### CATALOGUE #################################################################

star_chart = StarChart()
    
grid = Grid()
grid_stars = gp.stars_in_total_grid(star_chart, grid)
hashtable = gp.reference_grid_hashtable(star_chart, grid_stars, grid)

#### COMPARISON OF HASHCODES ###############################################

nghb_hash = np.argmin(np.linalg.norm(hashtable.codes - imgcode, axis=1))
idx_A = hashtable.idc[nghb_hash, 1]
nn_ra, nn_dec = hashtable.origin[nghb_hash]
nn_alpha, nn_scale = hashtable.alpha[nghb_hash], hashtable.scale[nghb_hash]

# todo: draw image frame onto star plot

  
##### PLOT ################################################################

# catalogue
i_center = np.nonzero(star_chart.name=="Alcyone")[0][0]
ra_center = star_chart.ra[i_center] + 0.01
dec_center = star_chart.dec[i_center] + 0.01
fov = 4*np.pi/180
#ra_center, dec_center = df[["ra", "dec"]].loc[df["proper"]=="Alioth"].values[0]
#fov = 2*np.pi/30 #160

# plot stars
fig, ax = plot.plot_star_selection(star_chart, ra_center, dec_center, fov, tan_proj=False)
fig.suptitle("Pleiades", size=40)

# plot grid and grid stars
plot.draw_grid_cells(ax, grid)
plot.highlight_grid_stars(ax, grid_stars, star_chart)


# image
fig, ax = plt.subplots(ncols=2, dpi=150, figsize=(7,5))

im = ax[0].imshow(img, cmap="gray")
ax[0].set_title("original")
fig.colorbar(im, ax=ax.ravel().tolist(), orientation='horizontal')
ax[1].set_title("filtered")
im2 = ax[1].imshow(img_filtered, cmap="viridis", norm=colors.PowerNorm(gamma=0.3))
for i, idx in enumerate(local_minima):
    ax[1].add_patch(plt.Circle(tuple(idx[::-1]), 
                               radius=50*minima_brightness[i]/np.max(minima_brightness),
                               color='w', fill=False))
fig.colorbar(im2, ax=ax.ravel().tolist(), orientation='horizontal', ticks=None)
plt.show()
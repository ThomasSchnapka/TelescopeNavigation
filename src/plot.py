import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def plot_star_selection(df, ra_center, dec_center, fov, deg_ticks=False, 
                        tan_proj=False):
    """
    draw stars in fov around center

    Parameters
    ----------
    df:         dataFrame with stars
    ra_center:  center right ascension (rad)
    dec_center: center declination (rad)
    fov:        field of view (rad)
    deg_ticks:  whether to write ticks in deg instead of rad
    tan_proj:   wheter to use tangential projection

    Returns
    -------
    fig, ax of plot

    """
    # extract data from dataFrame
    choice = (  (df["ra"]  < ra_center + fov/2) &  (df["ra"] > ra_center - fov/2)
              & (df["dec"] < dec_center + fov/2) &  (df["dec"] > dec_center - fov/2))
    ra = df["ra"].loc[choice].to_numpy()
    dec = df["dec"].loc[choice].to_numpy()
    mag = df["mag"].loc[choice].to_numpy()

    size = 100*(1.5**-mag)
    
    if tan_proj==True:
        ra = np.tan(ra - ra_center) + ra_center
        dec = np.tan(dec - dec_center) + dec_center

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12,12))
    ax.set_xlim(ra_center-fov/2, ra_center+fov/2)
    ax.set_ylim(dec_center-fov/2, dec_center+fov/2)
    ax.scatter(ra, dec, s=size, c="w")
    ax.set_ylabel("dec [rad]")
    ax.set_xlabel("ra [rad]")
    ax.invert_xaxis()
    ax.set_aspect("equal")

    if deg_ticks==True:
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        ax.set_xticks(xticks, [f"{ang:.3f}°" for ang in xticks*180/np.pi],
                      rotation=-30)
        ax.set_yticks(yticks, [f"{ang:.3f}°" for ang in yticks*180/np.pi])
    
    # add names
    names = df["proper"].loc[choice].to_numpy()
    for i, name in enumerate(names):
        if name is not np.nan:
            #plt.text(X[i], Y[i], name)
            plt.text(ra[i], dec[i], name)
            
    return fig, ax


def draw_grid_stars(ax, grid_stars, df):
    """draw grid and encircle brightest stars"""
    for i in range(grid_stars.shape[0]):
        if grid_stars[i, -1]>0:
            loc = (df.iloc[grid_stars[i, -1]]["ra"], 
                   df.iloc[grid_stars[i, -1]]["dec"])
            ax.add_patch(plt.Circle(loc, 0.005/(grid_stars[i, 0]+1), color="pink", fill=False, alpha=0.5))
            
            
def draw_grid_cells(ax, grid):
    """
    draw grid on ax

    Parameters
    ----------
    ax : matplotlib axis instance
    grid : Grid object
    
    """
    
    for i in range(grid.n_iter):
        kwargs = {"linewidth": 1, "color":"r", "alpha":0.6/(i+1)}
        
        # calculate grid
        frac = grid.f_decr**i
        grid_ra = grid.origin_ra   + np.arange(0, frac*grid.n_ra )*grid.d_ra/frac
        grid_dec = grid.origin_dec + np.arange(0, frac*grid.n_dec)*grid.d_dec/frac
        
        # plot grid
        for ra in grid_ra: ax.axvline(ra, np.pi, -np.pi, **kwargs)
        for dec in grid_dec: ax.axhline(dec, np.pi, -np.pi, **kwargs)


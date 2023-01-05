import numpy as np
from matplotlib import pyplot as plt
from copy import deepcopy

# https://www.astronomy.ohio-state.edu/ryden.1/ast162_2/notes9.html
BETELGEUSE_RAD = 0.125 * (1 / 3600) * np.pi / 180  # angular size in RAD
BETELGEUSE_MAG = 0.58

FIGSIZE_INCH = 12  # figure is square
FIG_DPI = 150


def plot_star_selection(
    sc, ra_center, dec_center, fov, deg_ticks=False, tan_proj=False
):
    """
    draw stars in fov around center

    Parameters
    ----------
    sc:         StarChart object
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
    choice = (
        (sc.ra < ra_center + fov / 2)
        & (sc.ra > ra_center - fov / 2)
        & (sc.dec < dec_center + fov / 2)
        & (sc.dec > dec_center - fov / 2)
    )
    ra = sc.ra[choice]
    dec = sc.dec[choice]
    mag = sc.mag[choice]

    # size = 100*(1.5**-mag)

    # size relative to FOV
    # relative_size = (BETELGEUSE_RAD/fov)*BETELGEUSE_MAG/mag#/(2.512**-BETELGEUSE_MAG)*(2.512**-mag)
    relative_size = (
        (BETELGEUSE_RAD / fov) / (2.512**-BETELGEUSE_MAG) * (2.512**-mag)
    )
    points_in_fov = FIGSIZE_INCH * FIG_DPI
    size = 1e3 * 4 * points_in_fov * relative_size

    if tan_proj == True:
        ra = np.tan(ra - ra_center) + ra_center
        dec = np.tan(dec - dec_center) + dec_center

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(FIGSIZE_INCH, FIGSIZE_INCH), dpi=FIG_DPI)
    ax.set_xlim(ra_center - fov / 2, ra_center + fov / 2)
    ax.set_ylim(dec_center - fov / 2, dec_center + fov / 2)
    ax.scatter(ra, dec, s=size, c="w")
    ax.set_ylabel("dec [rad]")
    ax.set_xlabel("ra [rad]")
    ax.invert_xaxis()  # ra coordinates point from west to east
    ax.set_aspect("equal")

    if deg_ticks == True:
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()
        ax.set_xticks(
            xticks, [f"{ang:.3f}°" for ang in xticks * 180 / np.pi], rotation=-30
        )
        ax.set_yticks(yticks, [f"{ang:.3f}°" for ang in yticks * 180 / np.pi])
        ax.set_ylabel("dec [deg]")
        ax.set_xlabel("ra [deg]")

    # add names
    names = sc.name[choice]
    for i, name in enumerate(names):
        if name is not np.nan:
            # plt.text(X[i], Y[i], name)
            plt.text(ra[i], dec[i], name)

    return fig, ax


def highlight_grid_stars(ax, hashtable, starchart, r_circ=0.001):
    """
    encircle brightest stars per grid cell

    Parameters
    ----------
    ax : pyplot axis to draw on
    hashtable : HashTable instance (containing brightest stars)
    starchart : StarChart instance
    r_circ : (optional) circle radius
    """
    idx_brightest = np.unique(hashtable.idc)

    for i_star in idx_brightest:
        ra = starchart.ra[i_star]
        dec = starchart.dec[i_star]
        ax.add_patch(plt.Circle((ra, dec), r_circ, color="pink", fill=False, alpha=0.5))


def draw_grid_cells(ax, grid):
    """
    draw grid on ax

    Parameters
    ----------
    ax : matplotlib axis instance
    grid : Grid object

    """

    _grid = deepcopy(grid)

    for i in range(_grid.depth):
        kwargs = {
            "linewidth": 1,
            "color": "r",
            "alpha": 0.6 / (i + 1),
            "label": "cells",
        }

        # calculate grid
        grid_ra = _grid.ra_start + np.arange(0, _grid.n_ra + 1) * _grid.ra_width
        grid_dec = _grid.dec_start + np.arange(0, _grid.n_dec + 1) * _grid.dec_width

        # plot grid
        for ra in grid_ra:
            ax.axvline(ra, np.pi, -np.pi, **kwargs)
        for dec in grid_dec:
            ax.axhline(dec, np.pi, -np.pi, **kwargs)

        _grid = _grid.descend()

    # for i in range(grid.n_iter):
    #     kwargs = {"linewidth": 1, "color":"r", "alpha":0.6/(i+1), "label":"cells"}

    #     # calculate grid
    #     frac = grid.f_decr**i
    #     grid_ra = grid.origin_ra   + np.arange(0, frac*grid.n_ra )*grid.d_ra/frac
    #     grid_dec = grid.origin_dec + np.arange(0, frac*grid.n_dec)*grid.d_dec/frac

    #     # plot grid
    #     for ra in grid_ra: ax.axvline(ra, np.pi, -np.pi, **kwargs)
    #     for dec in grid_dec: ax.axhline(dec, np.pi, -np.pi, **kwargs)

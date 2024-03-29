## Roadmap/ To-Do

1. build hashed star catalogue ("StarChart") based on HYG database
    1. add unit tests
    2. develop hashing procedure catalogue --> star chart

2. find image in StarChart
    1. add unit tests
    2. locate stars in noisy images
    3. hash stars in images
    4. construct hypothesis test for all occurring hashes

3. test image location systematically
    1. find bottlenecks
    2. estimate accuracy
    3. estimate if image location can be used inside feedback loop
    4. check the influence and necessity of image stacking for localization

4. build loop to orient telescope based on shown images
    1. (build hardware)
    2. develop architecture incl. image capturing requirements, Earth movement
    3. test with hardware





## Workflow

### Reference hashtable generation
For later localization, the hashtable contains an extensive collection of star-quadruplets, their location and the corresponding hashcode, which can be used for association. 

This hashtable is generated on a set of parameters summarized as a `Grid` object. Illustrativly, this grid is placed onto the star chard and for each individual cell, the brightest star is stored for further processing. To account for several possible scales ("zooms"), this process is repeaded iterativly with smaller subgrids, where the number of iterations is given by `grid.n_iter` and the descaling factor of the grid by `grid.f_decr`.

The brightest stars in each individual cell are stored in a list of `StarsInGridCell` objects, where each list entry corresponds to a subgrid iteration. 

Next, a hashtable for all stored stars is generated by generating hashcodes for individual four adjacent gridcell stars across all levels of subgrids. This table is given as a `HashTable` object and contains the following entries:
( code | code | code | code | origin | origin | alpha | scale | iA | iB | iC | iD )
>- 'code' 4 hashcode values
>- 'origin' origin of hash coordinate system in celectial coordiantes
>- 'scale'  scale of hash cordinate system
>- 'i*'     indices of stars creating hash coordinate system correspondingto dataframe

### Hash generation
Based on Land et. al "Astrometry. net: Blind astrometric calibration of arbitrary astronomical images", a star hash consits of four entries encodes the normalized relative position of four given stars. Basicly, two outer stars span a local coordinate system and the location of two inner stars are the four resulting hash values.


### Star detection in images
TODO

### Search in hashtable and hypothesis test
TODO




## Modules

(name, description, most important functions)

### HashTable.py
table structure containing star locations and hashcodes. This custom structure might get replaced
by a Pandas datafrage or an SQL database
- add_row(..)
- append(HashTable)

### Grid.py
class representing grid to choose stars in. Mostly used for storing parameters
- copy(frac) --> used for creating sub-grids

### StarsInGridCells.py
Data representation containing brightest stars per grid cell
- add_star(...)
- get_cell_stars(grid cell coordinate)

### StarChart.py
chart containing star data from database (ra, dec, mag, name)

### hashing.py
functions for generating hashcodes for star quadruples. 
- generate_quad_code(quadruplet star coordinates) 

### grid_processing.py
function for turning data and grid to an usable hashtable
- brightest_stars_per_subgrid(Grid, StarChart) ---> return stars entries in grid and all subgrids as list of GridStars
- create_reference_hashtable(StarChart, [GridStars], Grid) ---> return hashtable that can be used for localization



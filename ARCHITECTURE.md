## Roadmap/ To-Do

1. build hashed star catalogue ("StarChart") based on HYG database
    0. add unit tests
    1. develop hashing procedure catalogue --> star chart

2. find image in StarChart
    0. add unit tests
    1. locate stars in noisy images
    2. hash stars in images
    3. construct hypothesis test for all occurring hashes

3. test image location systematically
    1. find bottlenecks
    2. estimate accuracy
    3. estimate if image location can be used inside feedback loop
    4. check the influence and necessity of image stacking for localization

4. build loop to orient telescope based on shown images
    0. (build hardware)
    1. develop architecture incl. image capturing requirements, Earth movement
    2. test with hardware

## Modules

(name, description, most important functions)

### HashTable.py
table structure containing star locations and hashcodes. This custom structure might get replaced
by a Pandas datafrage or an SQL database. Entries:
( code | code | code | code | origin | origin | alpha | scale | iA | iB | iC | iD )
>- 'code' 4 hashcode values
>- 'origin' origin of hash coordinate system in celectial coordiantes
>- 'scale'  scale of hash cordinate system
>- 'i*'     indices of stars creating hash coordinate system correspondingto dataframe
- add_row(..)
- append(HashTable)

### Grid.py
class representing grid to choose stars in. Mostly used for storing parameters
- copy(frac) --> used for creating sub-grids

### GridStars.py
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
- stars_in_total_grid(Grid, StarChart) ---> return stars entries in grid and all subgrids as list of GridStars
- reference_grid_hashtable(StarChart, [GridStars], Grid) ---> return hashtable that can be used for localization



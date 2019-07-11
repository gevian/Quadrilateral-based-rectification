#### Introduction
This Python script allows the automated, vectorized georeferencing of map sheets displaying rectangular coordinate grids. It represents the final step of process described in the article:

_Heitzler M., Gkonos C., Tsorlini A., Hurni L. (2018). A modular process to improve the georeferencing of the Siegfried map. Proceedings of the 13th Conference on Digital Approaches to Cartographic Heritage (DACH), 18-20 April 2018, Madrid, Spain._

The script has three required arguments:
1. The location of the scanned, distorted map.
2. The location of the final, georeferenced image file.
3. The location of a shapefile containing the points of the grid intersections.
4. The location of a shapefile containing the coordinates written on the borders of the map.

Furthermore, the script may receive four optional arguments:
1. The resolution [m/pixel] of the georeferenced target image. The default is 1.25m/pixel.
2. The minimum distance [m] under which two grid lines are considered separate. The default is 250m.
3. The resampling method. Currently supported are "nearest neighbour" and "bilinear". The default is "bilinear".
4. The transformation method. Currently only an approximate transformation between the historical coordinate reference system to the new Swiss reference system LV95 is supported. Hence, the default is "Siegfried2LV95".

Use the "-h" option to list the respective argument names.


#### Examples
To illustrate the usage of the script, an example has been placed in this repository. Due to the large size of Siegfried map sheets, this example remains rather rudimentary, but should illustrate the approach. To execute the script, run the following command:

python georeferenceImage.py "./example/in.png" "./example/out.tif" "./example/intersections.shp" "./example/coordinates.shp"


#### References
Some of the used equations are based on the article on quad interpolation published here: https://www.particleincell.com/2012/quad-interpolation/ (2017.11.6)






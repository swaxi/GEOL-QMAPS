# WAXI_QF
 QGIS Plugin to help QFIELD usage   
 
## Install
Save repository to disk as a zip file. Use QGIS Plugin Manager to load directly from zip file.

## Usage
1. Select the plugin using the WAXI logo   
2. To clip all layers to surrent Canvas, select the Clip check box and define a new directory to contain all the layers
3. And/or Define new User and their Description
4. Click on OK, new Clipped Project will be created and/or new user will be added to *User list.csv*

## Roadmap
1) Add users, rock types, etc to csv lists

c.f. addUserName code OR via upload of csvs

2) Spatial subset extraction to new project

Done but what to do about GEOGRAPHY & ORTHOPHOTO directories, and qgz project file?   

3) Merge projects

Done but not sure how to handle GEOGRAPHY & ORTHOPHOTO directories, and qgz project file  

4) Export geometries to produce single shapefiles (structures, litho, stops, zones, petrophysics)

define export path to folder   
   
load relevant layers   
outer join   
save as shape files   

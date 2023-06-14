# WAXI_QF
 QGIS Plugin to help QFIELD usage related to the WAXI QFIELD Template V 0.3 (ctrl click on the link to access latest template): https://zenodo.org/record/7882352 
 
## Install
Save repository to disk as a zip file. Use QGIS Plugin Manager to load directly from zip file.

## Usage
1. Select the plugin using the WAXI logo   ![waxi_icon](icon.png) 

 ![waxi_qf dialog](dialog.png) 

2. To clip all layers to surrent Canvas, select the Clip check box and define a new directory to contain all the layers
3. And/or select the Add New item to CSV file check box and select which file to add item to and define Value and it's Description
4. And/or select select the Merge Projects check box and two existing project directories and a new one to store newly merged projects, with duplicates removed. An existing project must be open at the moment.
5. And/or select select the Export layers to common themes check box and directory so zones, structures and lithologies can be merged as 3 composite shapefiles
6. And/or Update the Project name for a new field season.
7. And/or Create single layer with Virtual Stops to cluster diferent types of observations according to locality
8. Click on OK to perform action

## Roadmap

Done (for now)
   
## Credits    
Plugin construction - Mark Jessell using QGIS Plugin Builder Plugin    
QFIELD Template - Julien Perret    

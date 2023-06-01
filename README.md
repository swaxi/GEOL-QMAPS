# WAXI_QF
 QGIS Plugin to help QFIELD usage   
 
## Install
Save repository to disk as a zip file. Use QGIS Plugin Manager to load directly from zip file.

## Usage
1. Select the plugin using the WAXI logo   
2. Define new User and their Description
3. Click on OK, new user will be added to *User list.csv*

## Roadmap
1) Add users, rock types, etc to csv lists

c.f. addUserName code

2) Spatial subset extraction to new project

e = iface.mapCanvas().extent()   
e.xMaximum()   
e.yMaximum()   
e.xMinimum()   
e.yMinimum()   

#### Specify the input layer to be clipped
project = QgsProject.instance()
input_layer = project.mapLayersByName("layer_name")

#### Specify the output path for the clipped layer
output_path = "path_to_output_file.shp"  # Replace with the desired output file path

#### Specify the extent for clipping (xmin, xmax, ymin, ymax)
extent = QgsRectangle(xmin, ymin, xmax, ymax)  # Replace with the desired extents

#### Clip the layer to the specified extent
processing.run("native:clip", {   
    'INPUT': input_layer,   
    'OUTPUT': output_path,   
    'MASK': extent   
})   

#### Load the clipped layer back into QGIS 
clipped_layer = QgsVectorLayer(output_path, "Clipped Layer", "ogr")   
QgsProject.instance().addMapLayer(clipped_layer)   


3) Merge projects

define principal local new_principal paths to folders   
   
loop through shp.csv    
load same files from principal and local folders    
concat to new shapefile   
drop duplicates on location and time   
save as new shapefile to new_principal folder according to directory code for subdirectory   

4) Export geometries to produce single shapefiles (structures, litho, stops, zones, petrophysics)

define export path to folder   
   
load relevant layers   
outer join   
save as shape files   

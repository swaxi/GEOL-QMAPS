# WAXI_QF
 QGIS Plugin to help QFIELD usage related to the latest GEOL-QMAPS digital geological mapping solution (ctrl + click on the link to access latest template): https://doi.org/10.5281/zenodo.7834717
 
## Install
Save repository to disk as a zip file. Use QGIS Plugin Manager to load directly from zip file.

## Usage
**Select the plugin using the WAXI logo**   ![waxi_icon](icon.png)   

**An existing WAXI QFIELD project must be open to run this plugin, otherwise the Dialog will not display.**

## Functionality
- **Import Layers** Convert pre-existing data into a QGIS GEOL-QMAPS template ready for merging, uses fuzzy logic to suggest best choices for lithology labels.   

![dialog1](dialog1.png)

- **Clip to current canvas**: Select checkbox to clip all GEOL-QMAPS field data layers to current QGIS Canvas, select the Clip check box and define a new directory to contain all the layers. Optionally select a polygon shapefile to be the clipping polygon. You can use the **Merge Projects** tool to recombine any modififications you have made to this clipped region  back into the global dataset.      
- **Edit items in Dictionaries**: Select checkbox and select which file to add or delete item to and define Value and its Description. This will update the relevant csv file, so it becomes available in the GEOL-QMAPS field data dropdown menus.    
- **Set User by Default**: Assign an existing or new user to be the default for one layer or all layers going forward.
- **Update project name and region**: Select checkbox to update the project name and field region for a new field campaign.
- **Save changes made to the field data forms**: Allows a custom style file to be created for template. Users supplies directory path.   
- **Toggle Auto-Increment of Stop numbers**: Select checkbox and toggle Stop Number autoincrementing behaviour when a new stop is defined.       

![dialog2](dialog2.png)

- **Merge two projects**: Select checkbox to merge two existing GEOL-QMAPS projects by selecting two existing project directories and a new one to store newly merged projects. Duplicate rows in each layer will be deleted.
- **Export layers to common themes**: Select checkbox and define directory to export all point, polygon and polyline which are combined to three  shapefiles for zones, structures and lithologies.  
- **Create Virtual Stops**: Select checkbox and define clustering distance to add a cluster code to all diferent types of points observations according to locality, using a DBSCAN algorithm. This will create a new layer called *Virtual_Stops_datestamp*.  This can be very slow for large datasets, so probably best applied to clipped data for a region of interest.     
- **Stereographic projection settings**: Select Stereonet checkbox to control WAXI fork of Stereonet plugin display (https://github.com/swaxi/qgis-stereonet).
- **Picture storage**: Allows a new directory to be defined for the storage of field and sampling pictures.  
     
![dialog3](dialog3.png)


## Roadmap
Add centroids of polygon and line features when creating virtual stop layer.
Generate default symbols when adding new values to dictionaries if appropriate.
Implement a tool that change saturation of symbols for preexisting field data, to distinguish them frm newly entered entities.
   
## Credits    
Plugin construction - Eliott Betend GUI and Import Tool    
Plugin construction - Mark Jessell using QGIS Plugin Builder Plugin     
Manual - Eliott Betend and Mark Jessell   
QGIS digital mapping tool - Julien Perret 

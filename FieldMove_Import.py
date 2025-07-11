# Importing Fieldmove Data to QFIELD.
# Author: Mark Jessell
# Version 0.0.1

import pandas as pd
import os
import shutil

from qgis.core import QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer, QgsProject
from qgis.core import QgsField
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsRasterLayer

class FM_Import:
    """
    A class for converting the geophysical data to Tomofast-x inputs.
    """

    def __init__(self,df):
        self.df = df

    def csv_to_pandas(self, gpkg_path, layer_name):
        # Load the CSV layer from the GeoPackage
        layer = QgsVectorLayer(f"{gpkg_path}|layername={layer_name}", layer_name, "ogr")

        # Check if the layer is valid
        if not layer.isValid():
            raise ValueError("Failed to load the CSV layer from the GeoPackage.")

        # Extract attributes
        data = []
        for feature in layer.getFeatures():
            data.append([feature["Valeur"], feature["Description"]])

        # Convert to Pandas DataFrame
        df = pd.DataFrame(data, columns=["Valeur", "Description"])

        return df,layer
        
    # Import specific files within the FieldMove project directory into current project
    def import_FM_data(self,basePath,projectDirectoryPath):

        # Prepare the 'FIELD MOVE PROJECTS' group at top of the Tree
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        fm_group = root.findGroup("FIELD MOVE PROJECTS")
        if not fm_group:
            fm_group = root.insertGroup(0, "FIELD MOVE PROJECTS")

        # Prepare the 'projectDirectoryPath' subgroup within the "FIELD MOVE PROJECTS" group
        proj_name = os.path.basename(os.path.normpath(projectDirectoryPath))
        imported_fm_group = fm_group.findGroup(proj_name)
        if not imported_fm_group:
            imported_fm_group = fm_group.insertGroup(0, proj_name)

        # copy QGIS Project and FieldMove Project directories to local
        self.basePath=basePath
        self.projectDirectoryPath=projectDirectoryPath
        if(os.path.exists(self.projectDirectoryPath) and projectDirectoryPath != ""):
            
            # define specific file paths
            imagesPath=self.projectDirectoryPath+'/images'
            DCIMPath=self.basePath+'/0_FIELD_DATA/DCIM/'
            geologyPath=self.basePath+'/6_GEOLOGY/'
            if os.path.exists(self.projectDirectoryPath+'/rock-units.csv'):
                dataType='FieldMove'
            else:
                dataType='Clino'

            mainCompGpkgPath = self.mynormpath(
                    self.basePath + "99_COMMAND_FILES_PLUGIN/Dictionaries.gpkg"
                )
            local_df,local_layer = self.csv_to_pandas(mainCompGpkgPath,"Local lithologies__List of lithologies")
            all_litho_df,litho_layer = self.csv_to_pandas(mainCompGpkgPath,"General__List of all lithologies")


            # Import different file types
            self.import_FM_rock_types(self.projectDirectoryPath,all_litho_df,litho_layer,local_df,local_layer,mainCompGpkgPath,dataType=dataType)
            self.import_FM_map_images(self.projectDirectoryPath,geologyPath,imported_fm_group=imported_fm_group)
            self.import_FM_polylines(imported_fm_group=imported_fm_group)
            self.import_FM_lineations(dataType=dataType,imported_fm_group=imported_fm_group)
            self.import_FM_localities(imported_fm_group=imported_fm_group)
            self.import_FM_photos(imagesPath,DCIMPath,imported_fm_group=imported_fm_group)
            self.import_FM_planar_structures(dataType=dataType,imported_fm_group=imported_fm_group)
        else:
            print("FieldMove project directory does not exist or is empty.")
        return
            
    def mynormpath(self, path):
        return r"" + os.path.normpath(path).replace("\\", "/")
    
    # import lithology name file and store new rock names in QFIELD csv dictionaries (Local lithologies)
    def import_FM_rock_types(self,projectDirectoryPath,lithoQFIELD,litho_layer,localQField,local_layer,mainCompGpkgPath,dataType):

        if dataType=='FieldMove':
            litho=pd.read_csv(projectDirectoryPath+'/rock-units.csv',index_col=None)
            litho=litho.drop(columns=['unitId',' type',' color'])
            litho=litho.rename(columns={' name':'Valeur'})
            litho.Valeur=litho.Valeur.str.lstrip()
            litho['Description']=litho['Valeur']
        else: # Clino import
            names=['Horizon','Colour','Rock Type','Age','Thickness','horizonId']
            litho=pd.read_csv(projectDirectoryPath+'/stratcolumn.csv',names=names,skiprows=7,index_col=None)
            litho=litho.iloc[3:].reset_index(drop=True)
            litho=litho.drop(columns=['Colour','Rock Type','Age','Thickness','horizonId'])
            litho=litho.rename(columns={'Horizon':'Valeur'})
            litho.Valeur=litho.Valeur.str.lstrip()
            litho['Description']=litho['Valeur']


        for i,dic in enumerate([lithoQFIELD,localQField]):
            newLitho=[]
            for i,lithoObject in litho.iterrows():
                if(not lithoObject['Description'] in dic['Description']):
                    # New row data
                    new_row = {'Valeur': lithoObject['Description'], 'Description': lithoObject['Description']}

                    # Append new row using append()
                    self.add_row_to_csv_layer(mainCompGpkgPath, "General__List of all lithologies", new_row)
                    self.add_row_to_csv_layer(mainCompGpkgPath, "Local lithologies__List of lithologies", new_row)


        self.reload_csv(mainCompGpkgPath,"General__List of all lithologies",litho_layer)
        self.reload_csv(mainCompGpkgPath,"Local lithologies__List of lithologies",local_layer)
    
    def add_row_to_csv_layer(self, gpkg_path, layer_name, new_row):
            """
            Add a row to a CSV layer in a GeoPackage.

            Parameters:
                gpkg_path (str): Path to the GeoPackage file.
                layer_name (str): The name of the CSV layer in the GeoPackage.
                new_row (dict): A dictionary representing the new row to add.
                                The keys must match the column names of the layer.

            Returns:
                None
            """
            import fiona
            try:
                # Open the GeoPackage layer in read mode to retrieve metadata
                with fiona.open(gpkg_path, layer=layer_name, mode="r") as src:
                    layer_crs = src.crs
                    layer_schema = src.schema
                    features = list(src)  # Load existing features

                # Validate new_row keys match the schema's properties
                for key in new_row.keys():
                    if key not in layer_schema["properties"]:
                        raise ValueError(
                            f"Invalid column name '{key}'. Column does not exist in the layer."
                        )

                # Create a new feature from the new_row
                new_feature = {
                    "type": "Feature",
                    "geometry": None,  # CSV layers typically don't have geometries
                    "properties": new_row,
                }

                # Append the new feature to the features list
                features.append(new_feature)

                """# Create a backup of the original GeoPackage
                backup_path = f"{gpkg_path}.bak"
                os.rename(gpkg_path, backup_path)
                """
                # Write the updated features back to the GeoPackage
                with fiona.open(
                    gpkg_path,
                    mode="w",
                    driver="GPKG",
                    layer=layer_name,
                    schema=layer_schema,
                    crs=layer_crs,
                ) as dst:
                    dst.writerecords(features)

                # print(f"Row added successfully to the layer '{layer_name}'.")
                # print(f"A backup of the original GeoPackage was created at: {backup_path}")

            except Exception as e:
                print(f"Error adding row to the GeoPackage layer: {e}")

                
    def reload_csv(self,dictionaries_path,current_layer,layer_csv):
        # Clear all features in the existing layer
        layer_csv.startEditing()
        layer_csv.dataProvider().truncate()  # Deletes all features efficiently
        layer_csv.commitChanges()

        # Load new data from the CSV file
        new_table = QgsVectorLayer(f"{dictionaries_path}|layername={current_layer}", current_layer, "ogr")
        
        if new_table.isValid():
            # Ensure the schema matches (field names and types)
            new_fields = new_table.fields()
            existing_fields = layer_csv.fields()
            
            if new_fields.names() != existing_fields.names():
                print("The schema of the new data does not match the existing layer. Update failed.")
            else:
                # Add new features to the existing layer
                layer_csv.startEditing()
                features = new_table.getFeatures()
                for feature in features:
                    layer_csv.dataProvider().addFeatures([feature])
                layer_csv.commitChanges()
        else:
            print(f"Failed to load new data from {dictionaries_path}.")


    # import polylines defined as points and convert to polyline layer in memory
    def import_FM_polylines(self, imported_fm_group):
        polyline=pd.read_csv(self.projectDirectoryPath+'/polyline.csv',index_col=None)
        polyline_attributes=pd.read_csv(self.projectDirectoryPath+'/polyline-attributes.csv',index_col=None)
        polyline_attributes=polyline_attributes.set_index(' dataId')

        # Step 1: Create a new vector layer to store the polyline
        layer = QgsVectorLayer('LineString?crs=EPSG:4326', 'PolylineLayer', 'memory')

        # Step 2: Start editing the layer
        layer.startEditing()
        layer.dataProvider().addAttributes([
            QgsField('localityName', QVariant.String),
            QgsField('rockUnit', QVariant.String),
            QgsField('thickness', QVariant.Int),
            QgsField('opacity', QVariant.Int),
            QgsField('style', QVariant.String),
            QgsField('filled', QVariant.Int),
            QgsField('timedate', QVariant.String),
            QgsField('notes', QVariant.String)
        ])   
        layer.updateFields()

        # Step 3: Convert points to polylines or polygons

        uniqueDataId=polyline.dataId.unique()
        for pID in uniqueDataId:
            onePolyline=polyline[polyline["dataId"]==pID]
            self.points_to_Polyline(onePolyline,polyline_attributes.loc[" "+pID],layer) # needs leading space!!


        # Step 4: Commit the changes
        layer.commitChanges()

        # Step 5: Add the layer to the project
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        imported_fm_group.insertLayer(0, layer)


    # import lineations and convert to points layer in memory
    def import_FM_lineations(self,dataType, imported_fm_group):
        lineation=pd.read_csv(self.projectDirectoryPath+'/line.csv',index_col=None)

        # Step 1: Create a new vector layer to store the polyline
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'LineationLayer', 'memory')

        # Step 2: Start editing the layer
        if dataType=='FieldMove':
            rockUnit='rockUnit'
        else: # Clino import
            rockUnit='unitId'

        layer.startEditing()
        layer.dataProvider().addAttributes([
            QgsField('localityName', QVariant.String),
            QgsField('altitude', QVariant.Int),
            QgsField('horiz_precision', QVariant.Int),
            QgsField('vert_precision', QVariant.Int),
            QgsField('lineationType', QVariant.String),
            QgsField('plunge', QVariant.Int),
            QgsField('plungeAzimuth', QVariant.Int),
            QgsField('declination', QVariant.Int),
            QgsField(rockUnit, QVariant.String),
            QgsField('timedate', QVariant.String),
            QgsField('notes', QVariant.String),
        ])  
        layer.updateFields()

        # Step 3: define attributes for one object 
        for i,lin in lineation.iterrows():
            attributes=[
            str(lin[' localityName']),
            int(lin[' altitude']),
            int(lin[' horiz_precision']),
            int(lin[' vert_precision']),
            str(lin[' lineationType']),
            int(lin[' plunge']),
            int(lin[' plungeAzimuth']),
            int(lin[' declination']),
            str(lin[' '+rockUnit]),
            str(lin[' timedate']),
            str(lin[' notes'])                      
            ]
            self.points_to_points(lin,layer,attributes) # needs leading space!!

        # Step 4: Commit the changes
        layer.commitChanges()

        # Step 5: Add the layer to the project
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        imported_fm_group.insertLayer(0, layer)

    # import planare structures and store as point layer
    def import_FM_planar_structures(self,dataType, imported_fm_group):
        planes=pd.read_csv(self.projectDirectoryPath+'/plane.csv',index_col=None)

        # Step 1: Create a new vector layer to store the polyline
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'PlaneLayer', 'memory')

        # Step 2: Start editing the layer
        if dataType=='FieldMove':
            rockUnit='rockUnit'
        else: # Clino import
            rockUnit='unitId'
        
        layer.startEditing()
        layer.dataProvider().addAttributes([
            QgsField('localityName', QVariant.String),
            QgsField('altitude', QVariant.Double),
            QgsField('horiz_precision', QVariant.Int),
            QgsField('vert_precision', QVariant.Int),
            QgsField('planeType', QVariant.String),
            QgsField('dip', QVariant.Int),
            QgsField('dipAzimuth', QVariant.Int),
            QgsField('strike', QVariant.Int),
            QgsField('declination', QVariant.Int),
            QgsField(rockUnit, QVariant.String),
            QgsField('timedate', QVariant.String),
            QgsField('notes', QVariant.String),
        ])   
        layer.updateFields()

        # Step 3: define attributes for one object 
        for i,pl in planes.iterrows():
            attributes=[
            str(pl[' localityName']),
            float(pl[' altitude']),
            int(pl[' horiz_precision']),
            int(pl[' vert_precision']),
            str(pl[' planeType']),
            int(pl[' dip']),
            int(pl[' dipAzimuth']),
            int(pl[' strike']),
            int(pl[' declination']),
            str(pl[' '+rockUnit]),
            str(pl[' timedate']),
            str(pl[' notes'])                      
            ]
            self.points_to_points(pl,layer,attributes) # needs leading space!!

        # Step 4: Commit the changes
        layer.commitChanges()

        # Step 5: Add the layer to the project
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        imported_fm_group.insertLayer(0, layer)

    # Function to search for files with specific extensions
    def find_files_with_extensions(self,directory, extensions):
        matching_files = []
        
        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if the file ends with one of the specified extensions
                if file.endswith(tuple(extensions)):
                    matching_files.append(os.path.join(root, file))
        
        return matching_files

    # import photos metadata and copy over files to new location
    def import_FM_photos(self,directory_to_search,images_directory, imported_fm_group):

        images=pd.read_csv(self.projectDirectoryPath+'/image.csv',index_col=None)


        # Step 1: Create a new vector layer to store the polyline
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'PhotosLayer', 'memory')

        # Step 2: Start editing the layer
        layer.startEditing()
        layer.dataProvider().addAttributes([
            QgsField('id', QVariant.Double),
            QgsField('Photo ID', QVariant.String),
            QgsField('Azimut', QVariant.Double),
            QgsField('Photo', QVariant.String),
            QgsField('Date', QVariant.String),
            QgsField('Mission', QVariant.String),
            QgsField('Country', QVariant.String),
            QgsField('Stop_ID', QVariant.String),
            QgsField('Layer', QVariant.String),
            QgsField('Virtual_ID', QVariant.Int),
            QgsField('Source', QVariant.String),
            QgsField('CRS', QVariant.String),
            QgsField('Comments', QVariant.String),
            QgsField('UUID', QVariant.String),
            QgsField('User', QVariant.String),
            QgsField('path', QVariant.String),
        ])   
        layer.updateFields()

        # Step 3: define attributes for one object 
        for i,im in images.iterrows():
            attributes=[
            float(0.0),
            str(""),
            float(im[' heading']),
            str(""),
            str(im[' timedate'])  ,                    
            str(""),
            str(""),
            str(im[' localityName']),
            str("PhotosLayer"),
            int(0),
            str("FieldMove Import"),
            str("EPSG:4326")  ,                    
            str(im[' notes'])  ,                    
            str(im[' dataId']),
            str(''),
            str("file:///"+images_directory+'/'+str(im[' image name']).replace(" ","")).replace(" ","%20").replace("#","%23")]
            
            self.points_to_points(im,layer,attributes) # needs leading space!!

        # Step 4: Commit the changes
        layer.commitChanges()

        # Step 5: Add the layer to the project
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        imported_fm_group.insertLayer(0, layer)

        extensions = ['.jpg']
        # Get the list of matching files
        file_list = self.find_files_with_extensions(directory_to_search, extensions)
        for fileName in file_list:
            shutil.copy2(fileName, os.path.join(images_directory, os.path.basename(fileName)))

    # import basemaps and store in new location
    def import_FM_map_images(self,directory_to_search,map_directory, imported_fm_group):
        extensions = ['.tif','.tiff','.TIF','.TIFF','.mbtiles','.MBTILES']
        # Get the list of matching files
        file_list = self.find_files_with_extensions(directory_to_search, extensions)


        for fileName in file_list:
            shutil.copy2(fileName, os.path.join(map_directory, os.path.basename(fileName)))

            # Create a QgsRasterLayer object
            raster_layer = QgsRasterLayer(os.path.join(map_directory, os.path.basename(fileName)), os.path.basename(fileName))

            # Check if the raster was loaded successfully
            if not raster_layer.isValid():
                print("Failed to load the raster layer.")
            else:
                # Add the raster layer to the QGIS project
                QgsProject.instance().addMapLayer(raster_layer, addToLegend=False)
                imported_fm_group.insertLayer(0, raster_layer)

    # import localities file and load as points layer
    def import_FM_localities(self, imported_fm_group):
        localities=pd.read_csv(self.projectDirectoryPath+'/localities.csv',index_col=None)

        # Step 1: Create a new vector layer to store the polyline
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'LocationsLayer', 'memory')

        # Step 2: Start editing the layer
        layer.startEditing()
        layer.dataProvider().addAttributes([
            QgsField('localityName', QVariant.String),
            QgsField('altitude', QVariant.Int),
            QgsField('horiz_precision', QVariant.Int),
            QgsField('vert_precision', QVariant.Int),
            QgsField('timedate', QVariant.String),
            QgsField('description', QVariant.String),
        ])   
        layer.updateFields()
        
        # Step 3: define attributes for one object 
        for i,loc in localities.iterrows():
            attributes=[
            str(loc[' name']),
            int(loc[' altitude']),
            int(loc[' horiz_precision']),
            int(loc[' vert_precision']),
            str(loc[' timedate']),
            str(loc[' description'])                      
            ]
            self.points_to_points(loc,layer,attributes) # needs leading space!!

        # Step 4: Commit the changes
        layer.commitChanges()

        # Step 5: Add the layer to the project
        QgsProject.instance().addMapLayer(layer, addToLegend=False)
        imported_fm_group.insertLayer(0, layer)

    # convert point info into layer point object
    def points_to_points(self,df,layer,attributes):
        # Step 1: Define the points (replace with your actual points)
        pointsx = df[' longitude']
        pointsy = df[' latitude']
        
        # Step 2: Create a polyline from the points
        allPts = QgsGeometry.fromPointXY(QgsPointXY(pointsx,pointsy))

        # Step 5: Create a new feature and assign the polyline geometry to it
        feature = QgsFeature()
        feature.setGeometry(allPts)

        feature.setAttributes(attributes)

        # Step 6: Add the feature to the layer
        layer.addFeature(feature)

    # convert a series of points into a layer poyline object
    def points_to_Polyline(self,dfPolyline,dfPolylineAttributes,layer):

        # Step 1: Define the points (replace with your actual points)
        allPointsx = dfPolyline[' longitude'].values
        allPointsy = dfPolyline[' latitude'].values
        points=[]
        for p in range(0,len(allPointsx)):       

            points.append(QgsPointXY(allPointsx[p],allPointsy[p]))

        # Step 2: Create a polyline from the points
        polyline = QgsGeometry.fromPolylineXY(points)

        # Step 3: Create a new feature and assign the polyline geometry to it
        feature = QgsFeature()
        feature.setGeometry(polyline)

        # Step 4: define attributes for one object 
        feature.setAttributes([
        str(dfPolylineAttributes[' localityName']),
        str(dfPolylineAttributes[' rockUnit']),
        int(dfPolylineAttributes[' thickness']),
        int(dfPolylineAttributes[' opacity']),
        str(dfPolylineAttributes[' style']),
        int(dfPolylineAttributes[' filled']),
        str(dfPolylineAttributes[' timedate']),
        str(dfPolylineAttributes[' notes'])                      
        ])

        # Step 5: Add the feature to the layer
        layer.addFeature(feature)

# =================================================================================
def main(self):
    pass

# ============================================================================
if __name__ == "__main__":
    main()

### from https://gist.github.com/ajzeigert/7cdd9a8301f540764a001bb4a380e4b3
# Convert KML/KMZ to Shapefile
# This script converts an input KML/KMZ file to an ESRI Shapefile
# and additionally parses any HTML table found in the "description" field
# and converts the data to actual fields

# Dependencies must be installed first: gdal, fiona, lxml

# Example usage: python KMLtoSHP.py inFile.kmz outFile.shp

import os
import sys
import json
import ogr
import copy
import fiona ### AZ: was not yet installed :: pip3 install fiona
from lxml import etree

from zipfile import ZipFile

if len(sys.argv) < 3:
    print("This script requires an input and output file, for example: python KMLtoSHP.py inFile.kml outfile.shp")
else:
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    reader = ogr.Open(inFile)
    layer = reader.GetLayer(0)
    features = []
    for feature in layer:
        features.append(json.loads(feature.ExportToJson()))
    layer.ResetReading() # Allows us to iterate from the beginning later

    # Process description field
    # This script checks for a description field, and tres to parse any table it finds and add those to the properties list
    for feature in features:
         print(feature)
###        if 'description' in feature['properties']:
###            table = etree.HTML(feature['properties']['description'])
###            xpath1 = '/html/body/table'
###            rows = table.xpath(xpath1)[0].findall('tr')
###            if len(rows) > 0:
###                for row in rows:
###                    cells = row.getchildren()
###                    feature['properties'][cells[0].text] = cells[1].text
###
###                del feature['properties']['description']
###                print("Found data in description table, converting")

    # Set the correct driver
    output_driver = 'ESRI Shapefile'
    # Get the spatial reference of the source layer
    output_srs = layer.GetSpatialRef().ExportToWkt()

    # Create an array of the properties and assign them all as a string type
    tempArray = []
    for property in features[0]['properties'].keys():
        tempProp = (property, 'str')
        tempArray.append(tempProp)

    # Create an output schema for our features to conform to
    output_schema = {
        'type': 'Feature',
        'geometry': 'Point',
        'properties': tempArray
    }


    # Open our new file
    with fiona.open(
        outFile,
        'w',
        driver=output_driver,
        crs=output_srs,
        schema=output_schema
        ) as c:
            # Loop through our features and write to the new file
            for feature in features:
                print("Writing feature")
                c.write(feature)
    print(inFile + " converted to " + outFile)

##    zipfile = ZipFile("xxxxx.zip", "w")
##    os.chdir(outFile)
##    for fname in os.listdir("."):
##        print (fname)
##        ##zipfile.write(os.path.join(outFile, fname))
##        zipfile.write(fname)
##    zipfile.close()
##    os.chdir("..")
##    import shutil
##    shutil.rmtree(outFile)



    
    

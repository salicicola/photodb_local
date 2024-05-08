import sys, os, xml.dom.minidom, shutil, fiona
from zipfile import ZipFile
import geopandas as gpd
from django.http import HttpResponse
try:
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
except:
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
BASEDIR="data/static/WRK"

APP_DIR = os.path.dirname(__file__)
KML_DOTS = open(os.path.join(APP_DIR, "KML_DOTS.kml")).read()
KML_AREA = open(os.path.join(APP_DIR, "KML_AREA.kml")).read()

def waypoints_kml(request, basename, output_file=None, download=False):
    if not output_file:
       output_file=basename ## 
    if basename:
        print ("converting %s.gpx to %s.kml" % (basename, output_file))
        input_path = os.path.join("data/static/WRK", basename +".gpx")
        output_path = os.path.join("data/static/WRK", output_file +".kml")
        if not os.path.exists(input_path):
            raise IOError("missing %s" % input_path)
    else:
        print (input_path, os.path.exists(input_path), output_path)
        raise IOError("missing input file name")
    KML = xml.dom.minidom.parseString(KML_DOTS)
    print (KML)
    INPUT = xml.dom.minidom.parse(input_path)
    print (INPUT)
    n = 0
    folder = KML.getElementsByTagName("Folder")[0]
    folder.appendChild(KML.createElement("name")) ## XXX
    for wpt in INPUT.getElementsByTagName("wpt"):
        n += 1
        try:
            _name = wpt.getElementsByTagName("name")[0].firstChild.nodeValue
        except:
            _name = str(n)
        ##print (wpt)
        placemark = KML.createElement("Placemark")
        name = KML.createElement("name")
        name.appendChild(KML.createTextNode(_name))
        placemark.appendChild(name)
        ##description
        ##styleurl
        point = KML.createElement("Point")
        ## altitudeMode
        coordinates = KML.createElement("coordinates")
        lonlat = "%s,%s" % (wpt.getAttribute("lon"), wpt.getAttribute("lon"))
        coordinates.appendChild(KML.createTextNode(lonlat))
        point.appendChild(coordinates)
        placemark.appendChild(point)
        print (placemark.toxml())
        folder.appendChild(placemark)
    if not download:
        out=open(output_path, "w")
        out.write(KML.toxml())
        print(out)
    if request:
        return HttpResponse(KML.toxml(), "text/xml")
    else:
        return KML

def track_kml(request, basename, output_file=None, download=False):
    if not output_file:
       output_file=basename 
    if basename:
        print ("converting %s.gpx to %s.kml" % (basename, output_file))
        input_path = os.path.join("data/static/WRK", basename +".gpx")
        output_path = os.path.join("data/static/WRK", output_file +".kml")
        if not os.path.exists(input_path):
            raise IOError("missing %s" % input_path)
    else:
        print (input_path, os.path.exists(input_path), output_path)
        raise IOError("missing input file name")
    KML = xml.dom.minidom.parseString(KML_AREA)
    print (KML)
    INPUT = xml.dom.minidom.parse(input_path)
    print (INPUT)
    coordinates = []
    for pt in INPUT.getElementsByTagName("trkpt"):
        lat = pt.getAttribute("lat")
        lon = pt.getAttribute("lon")
        coordinates.append((lon,lat))
        ##print (coordinates)
    print (coordinates[0])
    print (coordinates[-1])
    if not coordinates[0] == coordinates[-1]:
        first = coordinates[0]
        coordinates.append(first)
        print ("closed", coordinates[0], '=', coordinates[-1])
    coord_text = ""
    for lonlat in coordinates:
        txt = "%s,%s " % (lonlat[0], lonlat[1])
        coord_text += txt
    coord_text = coord_text.strip()
    print (coord_text)
    ele = KML.getElementsByTagName("coordinates")[0]
    ele.appendChild(KML.createTextNode(coord_text))
    if not download:
        out = open(output_path, "w")
        out.write(KML.toxml())
        out.close()
        print (out)
    if request:
        return HttpResponse(KML.toxml(), "text/xml")
    else:
        return KML

def toshape(request, basename, download=False):
    folder = "%s/%s" % (BASEDIR, basename)
    
    def compress(basename):
        curdir = os.getcwd()
        zip_path = "%s/%s.zip" % (BASEDIR, basename)
        zipfile = ZipFile(zip_path, "w")
        os.chdir(folder)    
        for fname in os.listdir("."):
            zipfile.write(fname)
            print (fname)
        zipfile.close()
        os.chdir(curdir)
        shutil.rmtree(folder)
        return zip_path

    # Read the KML file into a GeoDataFrame
    kml_file = "%s/%s.kml" % (BASEDIR, basename)
    gdf = gpd.read_file(kml_file, driver='KML')

    # Write the GeoDataFrame to a shapefile
    folder = "%s/%s" % (BASEDIR, basename)
    if not os.path.exists(folder):
        os.mkdir(folder)
        print ("creating folder", "%s" % folder)
    shp_file = "%s/%s.shp" % (folder, basename)
    gdf.to_file(shp_file, driver='ESRI Shapefile')
    print (shp_file, os.path.exists(shp_file))
    zip_file = compress(basename)
    if download:
        contents = open(zip_file, "rb").read()
        response = HttpResponse(contents, content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s.zip" % basename
        os.unlink(zip_file) 
        return response
    else:
        return HttpResponse(shp_file)
     
    

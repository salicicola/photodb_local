import os, sys, xml.dom.minidom, shutil, time
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from gisapp.models import Locality, Town, Openspace, USCounty

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import fromfile

from django.conf import settings
ROOT_DIR = settings.BASE_DIR
APP_DIR = os.path.dirname(__file__)
SRC_PATH = "data/WORK"

def test_kml(file_path):
    dom = xml.dom.minidom.parse(file_path)
    mgs = dom.getElementsByTagName("MultiGeometry")
    if not mgs:
        print ("no MultiGeometry tag found")
        return False
    if len(mgs) == 1:
        return True
    else:
        print ("more than one MultiGeometry tag found")
        return False

def create_valid_kml(file_path):
    shutil.copy2(file_path, file_path+".orig")
    print ("created backup")
    dom = xml.dom.minidom.parse(file_path)
    pm = dom.getElementsByTagName("Placemark")[0]
    coordinates = pm.getElementsByTagName("coordinates")[0]
    coord = coordinates.firstChild.nodeValue
    print (coord)
    points = coord.strip().split()
    p0 = points[0]
    p1 = points[-1]
    if not p0 == p1:
        coord = coord.strip()
        coord += " %s" % p0
        print ("corrected coordinates", coord)
        coordinates = dom.createElement("coordinates")
        coordinates.appendChild(dom.createTextNode(coord))
        print (coordinates.toxml())
    remove = pm.getElementsByTagName("LineString")[0]
    pm.removeChild(remove)
    lring = dom.createElement("LinearRing")
    boundary = dom.createElement("outerBoundaryIs")
    poly = dom.createElement("Polygon")
    mgeom = dom.createElement("MultiGeometry")
    lring.appendChild(coordinates)
    boundary.appendChild(lring)
    poly.appendChild(boundary)
    mgeom.appendChild(poly)
    pm.appendChild(mgeom)
    """ MultiGeometry><Polygon><outerBoundaryIs><LinearRing>"""
    print (pm.toxml())
    out = open(file_path, "w")
    dom.writexml(out)
    out.close()
    return True

def import_kml(request, lcid):
    print ("start running import_kml() with lcid", lcid)
    file_path = os.path.join(ROOT_DIR, SRC_PATH, lcid + ".kml.xml")
    may_try = test_kml(file_path)
    if not may_try:
        create_valid_kml(file_path)
        print ("re-created?")
        time.sleep(1)
    try:
        ds = DataSource(file_path)
        print ("got DataSource", type(ds))
    except:
        print ("bad", lcid+".kml.xml")
        raise
    print ("datasource", ds)
    lyr = ds[0]
    print (lyr)
    geom = None
    for feat in lyr:
        print (feat)
        name = feat.get('NAME')
        geom = feat.geom
        print ("geom", geom, type(geom), name)
        ###? geos_geom = GEOSGeometry(geom)
        geos_geom = geom.geos
        print ("geos_geom", geom, type(geom))
        break
    try:
        lrec = Locality.objects.get(lcid = lcid)
        print ("found", lrec)
    except:
        print (sys.exc_info())
        lrec = Locality()
        lrec.lcid = lcid
        print ("Can only create Locality yet without geom", lrec)
    ## added 2023-10-16
    town = ""
    try:
        towns = Town.objects.filter(geom__contains=geom.geos)
        if len(towns) == 1:
            town = towns[0].town
            print ("got single town", town)
        else:
            towns = Town.objects.filter(geom__intersects=geom.geos)
            print ("using intersect", towns)
            if towns:
                towns_ = []
                for t in towns:
                    towns_.append(t.town)
                town = ", ".join(towns_)
            else:
                town = ""
    except:
        town = str(sys.exc_info())       
    ## geom: Cannot use object with type MultiPolygon for a spatial lookup parameter, but worked with geom.geos
    lrec.name = name
    lrec.area = 0
    lrec.lon = 0
    lrec.lat = 0
    if town:
        lrec.region = "MA" ## FIXME 
        lrec.subregion = town ## subregion refers to Town[s], not county
    else:
        lrec.region = "?"
        lrec.subregion = "?"
    ## XXX if area partially outside MA, this part ignored: regions shown as MA and subregion only MA towns###
    #lrec.geometry = geom
    lrec.geometry = geos_geom
    center = geos_geom.centroid
    print ("center", center)
    lrec.lat = round(center.y, 4)
    lrec.lon = round(center.x, 4)
    print ("Updated Locality with geom", lrec)
##    print ("Created and saved Locality", lrec, "FIXME")
##    self.polygon.transform(32118) 
##    meters_sq = self.polygon.area.sq_m
    print ("initially area", geos_geom.area)
    geos_geom.transform(26986) ## 32118 this is for NY !! ## MA ? 26986 
    print (type(geos_geom))
    meters_sq = geos_geom.area
    print (meters_sq, "sq m raw")
    meters_sq = round(meters_sq/100, 0)
    meters_sq = int(meters_sq * 100)
    print (meters_sq, "sq m rounded")
    acres = meters_sq * 0.000247105381
    print (meters_sq, acres, "sq meters, acres")
    lrec.area = meters_sq
    lrec.save()

    """ should be 64973 m2	699366 ft.2 6.50 ha	16.06 acres
    got
    66801.0590624 sq m
    16.5069011508 acres for Bridgewater: fiels and meadows off Elm St.
    """
    return HttpResponseRedirect("/admin/gisapp/locality/%s/change/" % lrec.pk)

##def import_kml_oliver(request, lcid="MA.Nrf.Ded.202001011", name="Wilson Mt. Res."):
##    print ("start running import_kml() with lcid", lcid)
##    file_path = lcid + ".kml.xml"
##    try:
##        ds = DataSource(file_path)
##        print ("got DataSource", type(ds))
##    except:
##        print ("bad", lcid+".kml.xml")
##        raise
##    print ("datasource", ds)
##    lyr = ds[0]
##    print (lyr)
##    lrec = Locality()
##    lrec.lcid = lcid
##    geom = None
##    for feat in lyr:
##        print (feat)
####        try:
####            name = feat.get('NAME')
####        except:
####            name = "University Field"
##        geom = feat.geom
##        print ("geom", geom, type(geom), name)
#####?        geos_geom = GEOSGeometry(geom)
##        geos_geom = geom.geos
##        print ("geos_geom", geom, type(geom))
##        lrec.name = name
##        lrec.area = 0
##        lrec.lon = 0
##        lrec.lat = 0
##        lrec.region = "MA"
##        lrec.subregion = "Norfolk"
##        #lrec.geometry = geom
##        try:
##            lrec.geometry = geos_geom
##            print ("passed geos_geom without modifications")
##        except:
##            lrec.geometry = MultiPolygon((geos_geom, ))
##            print ("made multi polygon")
##        center = geos_geom.centroid
##        print ("center", center)
##        ##print dir(center)
##        lrec.lat = center.y
##        lrec.lon = center.x
##        print ("Updated Locality with geom", lrec)
##        lrec.save()
##        print ("Created and saved Locality", lrec, "Fixme")
##    ##    self.polygon.transform(32118) 
##    ##    meters_sq = self.polygon.area.sq_m
##        print ("initially area", geos_geom.area)
##        geos_geom.transform(32118) ## this is for NY !!
##        print (type(geos_geom))
##        meters_sq = geos_geom.area
##        print (meters_sq, "sq m")
##        acres = meters_sq * 0.000247105381
##    return HttpResponse("testing Polygon as Multiopolygon")

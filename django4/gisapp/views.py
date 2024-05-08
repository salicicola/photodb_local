import sys
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis.geos import Point, Polygon
from gisapp.models import Locality, Town, Openspace 
from photodb.models import *


VERSION = "0.2.8+" ## beta ## "0.2.7+ alpha"
VERSION = "0.2.10+" ## (27 Apr 2024 or later)"
UPDATED = "16 Oct 2023" ## "15 Oct 2023"
UPDATED = "27 Apr 2024" 

def gis_index(request):
    from gisapp.new_kml_import import SRC_PATH
    ## imported here because views may not be initialized otherwise
    return render(request, "gis_index.htm",
                  {"version":VERSION, "updated":UPDATED,
                   "SRC_PATH":SRC_PATH})

def imid_is_valid(imid):
    print ("imid_is_valid()", imid, len(imid))
    if len(imid) < 17:
        return False
    tokens =  (imid[:8], imid[8:13], imid[13:17])
    if tokens[0].isdigit() and imid[13:17].isdigit() and imid[8:13].isalpha():
        return True
    else:
        return False
    

## new as 2024-04-27
def get_location(request, imid=None, lat=None, lon=None):
    print ("running get_location", imid, lat, lon)
    html = "<html><head></head><body><h2>Simple GIS Query (Massachusetts Only)<br/>Supply plant photo ID or latitude and longitude (slash separated)</h2>"
    if lat and lon:
        lat = float(lat)
        lon = float(lon)
        html += "<div> Using explicit coordinates %s %s<div>" % (lat, lon)
    elif imid:
        if not imid_is_valid(imid):
           return HttpResponse("wrong IMID format" % imid)
        ##phid = 
        recs = VascularImage.objects.filter(imid=imid)
        print ("photo recs for %s: %s" % (imid, recs))
        if recs:
            rec = recs[0]
            if rec.gps:
                lat, lon = rec.gps.split('-')
                lon = '-' + lon
                lat = float(lat)
                lon = float(lon)
                html += "<div> Using coordinates from photo DB: image %s with gps coordinates %s %s<div>" % (imid, lat, lon)
            else:
                if rec.inid:
                    try:
                        ## e.g., ind.15306.42.64179-71.95431
                        tokens=rec.inid.split('.')
                        print (tokens)
                        lat=tokens[2]
                        print (lat)
                        x,y = tokens[3].split('-')
                        print (x, y)
                        lat="%s.%s" % (lat, x)
                        print ("lat", lat)
                        lon = "-%s" % y
                        print ("lon", lon)
                        lon = "%s.%s" % (lon, tokens[4])
                        print ("lon", lon)
                        lat = float(lat)
                        lon = float(lon)
                        html += "<div> Using coordinates from photo DB: image %s with individual ID coordinates %s %s<div>" % (imid, lat, lon)
                    except:
                        print (sys.exc_info())
                        return HttpResponse("imid %s without gps and suitable indID" % imid)
                else:
                    return HttpResponse("imid %s without gps and indID" % imid)
        else:
            return HttpResponse("Photo with imid ID %s not found" % imid)
    print ("using", lat, lon, type(lat), type(lon))
    pnt = Point(lon, lat)
    sm = Locality.objects.filter(geometry__intersects=pnt)
    towns = Town.objects.filter(geom__contains=pnt)
    areas = Openspace.objects.filter(geom__contains=pnt)
    html += "<div><br/></div>" 
    if towns:
        html += "<div>This point located in %s</div>" % towns[0]
    else:
        html += "<div>Can not find town. Maybe the point is outside MA</div>"
    if sm:
        html += "<div>Locality: %s</div>" % sm[0]
    else:
        html += "<div>No locality for this point in DB</div>"
    if areas:
        html += "<div>Open Space: %s</div>" % areas[0]
    else:
        html += "<div>No 'Open Space' for this location in DB or OpenSpace records are not enabled</div>"
    print ("locality", sm)
    print ("Town", towns)
    print ("areas", areas)
    html += "</body></html>"
    print (html)
    if request:
        return HttpResponse(html)


                     

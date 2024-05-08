import os, sys, xml.dom.minidom
from django.shortcuts import render
##from django.conf import settings
from django.http import HttpResponse
from django.contrib.gis.geos import Point, Polygon
from gisapp.models import Locality, Town, Openspace 
##from django.contrib.gis.shortcuts import render_to_kml
##from django.contrib.gis.gdal import DataSource

print ("starting update_lcid_gps module at", os.getcwd())
xgeneric = xml.dom.minidom.parse("data/ma_towns.xml") 
print ("xgeneric", xgeneric)
lcids_generic = {}
for record in xgeneric.getElementsByTagName("record"):
    try:
        town = record.getElementsByTagName("town")[0].firstChild.nodeValue
        lcid = record.getElementsByTagName("locID")[0].firstChild.nodeValue
        print (town, lcid)
        lcids_generic[town.lower()] = lcid
    except:
        pass

def update_gpx(request):
    path = ""
    try:
        path = request.GET["path"]
    except:
        try:
            day = request.GET["day"]
            day = day.strip()
            year = day[2:4]
            if day:
                path = "/media/data/data/NewPhotos" + year + "/" + day + "/" + day + "_mapped.gpx"
            else:
                return HttpResponse("supply absolute path to GPX file or day as YYYMMDD")
        except:
            return HttpResponse("supply absolute path to GPX file or day as YYYMMDD")
    if path:
        import xml.dom.minidom
        try:
            dom = xml.dom.minidom.parse(path)
            print (dom)
            recs = dom.getElementsByTagName("wpt")
            s = ""
            for rec in recs:
                lat=rec.getAttribute("lat")
                lon=rec.getAttribute("lon")
                name_elem = rec.getElementsByTagName("name")[0]
                photo = name_elem.firstChild.nodeValue
                s += "<br/>" + photo
                lat = float(lat)
                lon = float(lon)
                pnt = Point(lon, lat)
                sm = Locality.objects.filter(geometry__intersects=pnt)
                towns = Town.objects.filter(geom__contains=pnt)
                areas = Openspace.objects.filter(geom__contains=pnt)
                loc = ""
                lcid = ""
                twn = ""
                ops = ""
                for o in sm:
                    s += ":: " + o.name + " :: " + o.lcid
                    lcid = o.lcid + " "
                    loc = o.name + " "
                for t in towns:
                    s += " " + t.town
                    twn += t.town + " "
                for osp in areas:
                    s += " " + osp.site_name
                    ops += osp.site_name + " "
                s += " [" + str(lat) + ", " + str(lon) + "] "
                lcid = lcid.strip()
                loc = loc.strip()
                if lcid:
                    rec.setAttribute("LCID", lcid)
                else:
                    _lcid = lcids_generic.get(twn.strip().lower(), "")
                    print ("setting generic lcid for town", twn, _lcid)
                    rec.setAttribute("LCID", _lcid)
                    s += " -- generic ID: %s" % _lcid
                rec.setAttribute("OPS", ops.strip())
                rec.setAttribute("town", twn.strip())
            if not os.path.exists(path + ".orig"):
                os.rename(path, path + ".orig")
            out = open(path, "w")
            dom.writexml(out)
            out.close()
            return HttpResponse(s)
        except:
            return HttpResponse("Perhaps path to GPX file is not valid: [" + path + "]<br/>" + str(sys.exc_info()[1]))
    else:
        return HttpResponse("No day or valid path to GPX file supplied")



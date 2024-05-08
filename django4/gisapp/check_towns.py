import os, sys, xml.dom.minidom
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.gis.geos import Point, Polygon
from gisapp.models import Locality, Town, Openspace 
from photodb.models import *

checked = []

def check_towns(request, year=2019, category="vascular"):
    ## hardcoded FIXME
    num = 0
    err = 0
    recs=VascularImage.objects.filter(phid__startswith=str(year))
    for rec in recs:
        num += 1
        if rec in checked:
            continue
        try:
            ##print (rec)
            if rec.gps:
                lat, lon = "", ""
                if ' ' in rec.gps:
                    lat, lon = rec.gps.split()
                elif ',' in rec.gps:
                    lat, lon = rec.gps.split(',')
                elif '-' in rec.gps:
                    lat, lon = rec.gps.split('-')
                    lon = "-%s" % lon
                lat = lat.strip()
                lon = lon.strip()
                ##print (rec.gps, lat, lon)
            elif rec.inid and len(rec.inid.split('.')) == 5 and '-' in rec.inid.split('.')[3]:
                rec.inid=rec.inid.replace(',','')
                try:
                    tokens = rec. inid.split('.')
                    x,y=tokens[3].split('-')
                    lat="%s.%s" % (tokens[2], x)
                    lon = "-%s.%s" % (y, tokens[4])
                    ##print (rec.inid, lat,lon)
                except:
                    lat, lon = None, None
                    print("None", sys.exc_info())
                    raise
            else:
                lat,lon=None,None
            if lat and lon:
                lat = float(lat)
                lon = float(lon)
                pnt = Point(lon, lat)
                ##sm = Locality.objects.filter(geometry__intersects=pnt)
                towns = Town.objects.filter(geom__contains=pnt)
                ##areas = Openspace.objects.filter(geom__contains=pnt)
                if towns:
                    if towns[0].town.lower() == rec.locality.town.lower():
                        ##print (towns[0], '=', rec.location, '=', rec.locality.town)
                        ##print ("OK")
                        pass
                    else:
                        err += 1
                        ## XXXX 20190429olymp1103 empty towns
                        print (len(checked), "ERROR in", rec)
                        print (num, rec.gps, rec.inid, towns, rec.location, rec.locality.town)
                        print ("http://192.168.1.9:9090/photodb/gallery/view/%s/%s/" % (rec.plant.pnid, rec.imid))
                        if err > 0:
                            break
                else:
                    print ("empty towns XXX")
        except:
            print (sys.exc_info())
            print ("inid", rec.inid)
            print ("gps", rec.gps)
            raise
        checked.append(rec)

## should not be here, must be in photodb FIXME
def correct_triosteum():
    inids=["ind.13412.41.66896-70.617040","ind.13412.41.66895-70.61709"] ## ind.13412.41.66895-70.61709
    perf=Name.objects.get(pnid=13412)
    aura=Name.objects.get(pnid=15732)
    recs=VascularImage.objects.filter(plant=perf)
    for rec in recs:
        if rec.inid in inids:
            print ("skip perfoliatum", rec)
        else:
            rec.plant=aura
            print ("MOVED TO aurant.", rec)
            rec.save()

def correct_triosteum2():
    perf=Name.objects.get(pnid=13412)
    aura=Name.objects.get(pnid=15732)
    recs=VascularImage.objects.filter(plant=perf)
    for rec in recs:
        if "Woburn" in rec.location:
            rec.plant=aura
            print ("should MOVED TO aurant.", rec)
            rec.save()

def correct_triosteum3():
    perf=Name.objects.get(pnid=13412)
    aura=Name.objects.get(pnid=15732)
    recs=VascularImage.objects.filter(plant=perf)
    for rec in recs:
        if len(rec.imid) == 17:
            rec.plant=aura
            print ("MOVED TO aurant.", rec, len(rec.imid))
            rec.save()

            
##MA.Mid.Wob.2019100101

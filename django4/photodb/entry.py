import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
import codecs
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import *
from common.models import Location
from .admin_lib import *
##from .admin_import import lcids, TOMCAT_ROOT they are in admin_lib

from django.utils import timezone, dateparse
from django.utils.timezone import get_current_timezone

SRC = "/home/salicarium/django3/TDM/"
print ("FIED: date from iso format to ~January 21")
## tested with "committed_log/1632677034_tree.xml" but will works as URL only as _tree.xml
## done 2021-01-21, failed 27, 04-16 done ?
## works from /salicarium/django3 link at Desktop

##new
from names.models import Name

def get_fid(request, pnid):
    pnid = int(pnid)
    sp = Name.objects.get(pnid=pnid)
    if sp.level == 'species':
        fam = sp.upper.upper
        print ("got family", fam, "from", sp)
        return HttpResponse(fam.pnid)
    else:
        return HttpResponseBadRequest("error")


def get_gid(request, pnid):
    pnid = int(pnid)
    sp = Name.objects.get(pnid=pnid)
    if sp.level == 'species':
        genus = sp.upper
        print ("got genus", genus, "from", sp)
        return HttpResponse(genus.pnid)
    else:
        return HttpResponseBadRequest("error")

def create_species_xml(request):
    dom = xml.dom.minidom.parseString("<data/>")
    spp = Name.objects.filter(level='species')
    for sp in spp:
        try:
            meta = SpeciesMeta.objects.get(sp=sp.pnid)
        except:
            meta = {}
        species = dom.createElement("species")
        species.setAttribute("status", "valid")
        species.setAttribute("rank", sp.rank)
##        
##        if sp.ccss:
##            species.setAttribute("CCSS", str(sp.ccss))
##        else:
##        species.setAttribute("CCSS", "")
        ele = dom.createElement("PNID")
        txt = str(sp.pk)
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)
        try:
            if sp.upper.upper:
                txt = str(sp.upper.upper.pnid)
            else:
                txt = "999999"
        except:
            txt = "999999"
        ele = dom.createElement("fileID")
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)
        if sp.upper:
            txt = "%s %s" % (sp.upper.latname, sp.latname)
        else:
            txt = "%s %s" % ('???', sp.latname)
        ele = dom.createElement("latname")
##        if meta:
##            if not meta.counties:
##                txt += " s.l."
        if sp.longname:
            ele.appendChild(dom.createTextNode(sp.longname))
        else:
            ele.appendChild(dom.createTextNode(txt))
        ##ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)

        txt = "%s" % sp.authors
        ele = dom.createElement("authors")
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)

        txt = "%s" % sp.colnames
        ele = dom.createElement("colname")
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)

        txt = "%s" % sp.category
        ele = dom.createElement("category")
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)

        txt = "%s" % sp.modified
        ele = dom.createElement("modified")
        ele.appendChild(dom.createTextNode(txt))
        species.appendChild(ele)
        print (species.toxml())
        dom.documentElement.appendChild(species)

    out = open("static/scripts/photos/entry/species.xml", "w")
    dom.documentElement.writexml(out)
    out.close()
    print (out)

    return HttpResponse(dom.toxml(), "text/xml")
        


def save_from(request, fname):
    saved = 0
    path = os.path.join(SRC, fname)
    dom = xml.dom.minidom.parse(path)
    print (dom)
    for family in dom.getElementsByTagName("family"):
        fid = int(family.getAttribute("PNID"))
        famname = Name4.objects.get(pk=fid).latname
        for sp in family.getElementsByTagName("species"):
            spid = int(sp.getAttribute("PNID"))
            latname = sp.getAttribute("_latname")
            authors = sp.getAttribute("_authors")
            colnames = sp.getAttribute("_colname")
            name = Name4.objects.get(pk=spid)
            try:
                genus = name.legacy_parent
                genname = genus.latname
            except:
                print ("genus not found")
                print (sys.exc_info())
                genname = ""
            category = name.category
            print (category, name)
            for ind in sp.getElementsByTagName("individual"):
                inid = ind.getAttribute("IndID")
                print (" inid=", inid)
                for photo in ind.getElementsByTagName("photo"):
                    phid = photo.getAttribute("PHID")
                    nr = float(photo.getAttribute("nr"))
                    gps = photo.getAttribute("gps")
                    date = photo.getAttribute("created")
                    created = photo.getAttribute("recorded")
                    uid = photo.getAttribute("by")
                    lcid = photo.getElementsByTagName("LCID")[0].firstChild.nodeValue
                    loc = Location.objects.get(pk=lcid)
                    location = loc.public_name
                    town = loc.town
                    try:
                        extensions = photo.getElementsByTagName("extensions")[0].firstChild.nodeValue.split()
                    except:
                        extensions = ["",]
                    try:
                        caption = photo.getElementsByTagName("caption")[0].firstChild.nodeValue
                    except:
                        caption = ""
                    try:
                        gps_error = photo.getElementsByTagName("gps_error")[0].firstChild.nodeValue
                    except:
                        gps_error = ""
                    try:
                        herb_id = photo.getElementsByTagName("herbNum")[0].firstChild.nodeValue
                    except:
                        herb_id = ""
                    try:
                        tags = photo.getElementsByTagName("tags")[0].firstChild.nodeValue
                    except:
                        tags = ""
                    
                    try:
                        reintroduced = photo.getElementsByTagName("tags")[0].firstChild.nodeValue
                    except:
                        reintroduced = ""
                    ## NOT from entry form:: is_verified, status, is_planted
                    try:
                        note = photo.getElementsByTagName("comments")[0].firstChild.nodeValue
                    except:
                        note = ""
                    print ("  imids:", phid, nr, gps, date, created, uid, lcid, extensions, caption, note)
                    for ext in extensions:
                        imid = phid + ext
                        print ("    imid", imid)
                        manager = None
                        if category == 'vascular':
                            manager = VascularImage.objects
                        elif category == 'nonvascular':
                            manager = NonVascularImage.objects
                        elif category == 'animals':
                            manager = AnimalImage.objects
                        else:
                            manager = VariaImage.objects
                        existed = manager.filter(imid=imid).filter(spid=spid)
                        if existed:
                            print ("should not happen: already existed", existed[0])
                        else:
                            print ("    will add record:")
                            rec = manager.create(imid=imid, notes=note, caption=caption, lcid=lcid,
                                                 committed=created, date=date, gps = gps, nr=nr, phid=phid, inid=inid,
                                                 spid=spid, fid=fid, latname=latname, authors=authors,
                                                 colnames=colnames, modified=datetime.datetime.now(tz=get_current_timezone()),
                                                 famname=famname, genname=genname, town=town, location=location,
                                                 reintroduced=reintroduced, tags=tags, herb_id=herb_id, gps_error=gps_error)
                            print ("    ", rec)
                            date_date = dateparse.parse_date(rec.date)
                            print (date_date)
                            date_str = date_date.strftime("%B %Y")
                            print (date_str)
                            rec.date = date_str
                            rec.save()
                            saved += 1
                            print ("saved", rec.date)
    return HttpResponse("data enry, saved %s" % saved)


"""
Next ... will try to commit to django and clean:: server MUST run at localhost:9090
http://localhost:9090/photoDB/entry/from/_tree.xml 200
Now ... will clean
_tree.xml committed_log/1632686893_tree.xml True
_tree.html committed_log/1632686893_tree.html True
_photos.xml committed_log/1632686893_photos.xml True
_normalized.xml committed_log/1632686893_normalized.xml True
_individuals.xml committed_log/1632686893_individuals.xml True
_images.xml committed_log/1632686893_images.xml True
_identifications.xml committed_log/1632686893_identifications.xml True
normalized.xml committed_log/1632686893normalized.xml True
entry.txt committed_log/1632686893entry.txt False
ERROR
(<class 'FileNotFoundError'>, FileNotFoundError(2, 'No such file or directory'), <traceback object at 0x7fbd42110d00>)
"""

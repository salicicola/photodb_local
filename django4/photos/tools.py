import os, sys, xml.dom.minidom
from django.http import HttpResponse
from names.models import *
from common.models import Location

def update_options(request, filtering='MA.'):
    html = "<option value="">None selected</option>\n"
    locs = Location.objects.filter(lcid__startswith=filtering).order_by('alias')
    
    for rec in locs:
        _html = '<option value="%s">%s : %s</option>\n' % (rec.lcid, rec.alias, rec.lcid)
        print (_html)
        html += _html
    path = "photodb/templates/photodb/locations_options"
    os.rename(path, path+".backup")
    out = open("photodb/templates/photodb/locations_options", "w")
    out.write(html)
    out.close()
    if request:
        return HttpResponse(html, "text/plain")
    else:
        return True

def update_names(request=None):

    def make(name, meta=None):
        ##print (name, meta, meta.counties)
        xrec=xroot.createElement("species")
        xrec.setAttribute("rank", "species")
        xrec.setAttribute("status", "valid") ## FIXME see above
        ele=xroot.createElement("PNID")
        ele.appendChild(xroot.createTextNode(str(name.pnid)))
        xrec.appendChild(ele)
        try:
            ele=xroot.createElement("fileID")
            fid = name.upper.upper.pnid
            ele.appendChild(xroot.createTextNode(str(fid)))
            xrec.appendChild(ele)
        except:
            pass
            ##print (name, sys.exc_info())

        ele=xroot.createElement("latname")
        if name.longname:
            ele.appendChild(xroot.createTextNode(name.longname))
        elif name.upper:
            ele.appendChild(xroot.createTextNode("%s %s" % (name.upper.latname, name.latname)))
        else:
            print ("something wrong with", name)
        xrec.appendChild(ele)

        ele=xroot.createElement("authors")
        ele.appendChild(xroot.createTextNode(name.authors))
        xrec.appendChild(ele)

        ele=xroot.createElement("colname")
        ele.appendChild(xroot.createTextNode(name.colnames))
        xrec.appendChild(ele)

        ele=xroot.createElement("category")
        ele.appendChild(xroot.createTextNode(name.category))
        xrec.appendChild(ele)

        ele=xroot.createElement("modified")
        ele.appendChild(xroot.createTextNode(str(name.modified)))
        xrec.appendChild(ele)

        xroot.documentElement.appendChild(xrec)

    xroot=xml.dom.minidom.parseString("<data/>")
    names=Name.objects.filter(level='species') ## except disabled, etc ## fix rank
    for name in names:
        meta = SpeciesMeta.objects.filter(spid=name.pnid)
        if meta:
            meta = meta[0]
            if meta.counties:
                make(name, meta)
            else:
                pass
                ##print (name, meta, "no counties")                
        else:
            if name.upper and name.upper.upper:
                if not name.category == 'vascular':
                    make(name, None)
                    if name.category == 'other':
                        print ("non vascular?", name)
                else:
                    ##pass
                    print (sys.exc_info())
            else:
                pass
                ##print (name, name.upper)
    path = "data/static/scripts/photos/entry/species.xml"           
    os.rename(path, path+".backup") 
    out=open(path, "w")
    out.write(xroot.toxml())
    print (out)
    
    
    

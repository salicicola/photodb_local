from django.shortcuts import render
import xml.dom.minidom, os, shelve, pickle, datetime, sys, time, shutil
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from photodb.models import *

TOMCAT_ROOT = "/media/data/data/tomcat/webapps/ROOT"
import codecs

lcids = {}
if not lcids:
    dom = xml.dom.minidom.parse("ma_towns.xml") ## django/ removed
    print (dom)
    for rec in dom.getElementsByTagName("record"):
        try:
            town = rec.getElementsByTagName("town")[0].firstChild.nodeValue.strip()
            lcid = rec.getElementsByTagName("locID")[0].firstChild.nodeValue.strip()
            lcids[lcid] = town
        except:
            pass
            ##print (sys.exc_info())

    print (len(lcids), "towns")

    dom = xml.dom.minidom.parse("locations.xml") ## django/ removed /media/data/data/django3/data/
    print (dom)


    for rec in dom.getElementsByTagName("location"):
        try:
            town = rec.getElementsByTagName("town")[0].firstChild.nodeValue.strip()
            lcid = rec.getElementsByTagName("LocID")[0].firstChild.nodeValue.strip()
            lcids[lcid] = town
        except:
            pass

def make_note_xml(source, text):
    xstring = "<x>%s</x>" % text
    temp_xml = xml.dom.minidom.parseString(xstring)
    for child in temp_xml.documentElement.childNodes:
        if child.nodeType == child.TEXT_NODE:
            print (child.nodeValue)
            source.appendChild(dom.createTextNode(child.nodeValue))
        else:
            print (child.toxml())
            source.appendChild(child)
    return source

def get_value(ele, name):
   value = ""
   for child in ele.childNodes:
      if child.nodeType==ele.ELEMENT_NODE:
         if child.nodeName == name:
            if child.hasChildNodes:
               try:
                  value = child.firstChild.nodeValue.strip()
                  value = " ".join(value.split())
               except:
                  ##print sys.exc_info()
                  pass
            else:
               pass
   return value

def get_value_ele(element):
    if element.hasChildNodes:
        try:
            value = element.firstChild.nodeValue.strip()
            return " ".join(value.split())
        except:
            return ""
    else:
        return ""

def get_value_html(element):
    if element.hasChildNodes:
        value = ""
        for child in element.childNodes:
            if child.nodeType == child.TEXT_NODE:
                value += child.nodeValue
            elif child.nodeType == child.ELEMENT_NODE:
                value += child.toxml()
        value = value.strip()
        value = " ".join(value.split())
        return value
    else:
        return ""


def make_missing_thumbnails(request):
    from .Thumbnails import make_thumbnail
    total = 0
    made = 0
    for Class in [VariaImage, AnimalImage, NonVascularImage, VascularImage]:
        recs = Class.objects.all()
        for r in recs:
            total += 1
            imid = r.imid
            src = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "photos", imid[:6], imid+".jpg")
            ##print (src, os.path.exists(src))
            trg = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "thm", "photos", imid[:6], imid+".jpg")
            ##print (trg, os.path.exists(trg))
            if not os.path.exists(trg):
                print ("\tshould make thum", src, trg)
                if not os.path.exists(src):
                    print (src, "do not exists")
                else:
                    try:
                        if not os.path.exists(os.path.split(trg)[0]):
                            os.makedirs( os.path.split(trg)[0] )
                            print ("dir created", os.path.split(trg)[0])
                        make_thumbnail(src, trg, size=(100000, 100))
                        made += 1
                        print ("created", trg, os.path.exists(trg))
                        ##raise Exception("debug, one done")
                    except:
                        print (sys.exc_info()[0])
                        print (sys.exc_info()[1])
                        raise
            else:
                pass
                ##print ("skip existed", trg)
    message = "done %s of %s" % (made, total)
    print (message)
    if request:
        return HttpResponse(message)

def save_autoscale(request, spid, imid, category='vascular'):
    version = "alpha 2022-06-05" ## do category, do templates, do existed, etc...
    from .Thumbnails import make_thumbnail
    url = request.path
    if url.endswith("/"):
        url = url[:-1]
    phid = url.split("/")[-1]
    url = url + "a"
    url = url.replace("/autoscale/", "/")
    imid = phid + "a"
    print ("running save_autoscale with", url, phid, imid)
    src = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "photos", phid[:6], phid+".jpg")
    trg = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "photos", imid[:6], imid+".jpg")
    if os.path.exists(trg):
        result = True
    else:
        result = make_thumbnail(src, trg, size=(100000, 600))
    if result:
        try:
            rec = VascularImage.objects.get(imid=phid)
        except:
            print (sys.exc_info())
            try:
               rec = VariaImage.objects.get(imid=phid)
               print (rec)
            except:
               print ("raise")
               raise 
        if category == "vascular":
            ##rec = VascularImage.objects.get(imid=phid)
            rec.imid = imid
            rec.save()
            print (rec)
            return HttpResponseRedirect(url)
        else:
            print ("not implemented")
            return HttpResponseBadRequest("not yet implemented")
    else:
        print ("error")
        return HttpResponseBadRequest("something wrong")
    

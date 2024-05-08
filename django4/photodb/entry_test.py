import os, sys, xml.dom.minidom, datetime, time
import photodb.Thumbnails as Thumbnails
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import *
from common.models import Location
from .admin_lib import *
from django.utils import timezone, dateparse
from django.utils.timezone import get_current_timezone

MONTHES = "January Febrary March April May June July August September October November December".split()

def entry_one(request):
    if request.POST:
        return save_photo_records(request)
        ##return HttpResponse("debug :" + str(request.POST), "text/plain")
    else:
        print ("running entry_one GET: %s" % request.GET)
        path = request.GET.get("path")
        if not path:
            return HttpResponseBadRequest("path to image file not supplied")
        elif not path.endswith(".jpg"):
            return HttpResponseBadRequest("supplied path %s must ends with .jpg" % path)
        elif not os.path.exists(path):
            return HttpResponseBadRequest("supplied path %s not valid (file do not exists)" % path)
        elif not path.startswith("/media/data/data/tomcat/webapps/ROOT/photos/"):
            return HttpResponseBadRequest("currently works only with files at tomcat directory, supplied path %s is different" % path)                             
        else:
            fname = os.path.split(path)[1]
            imid = os.path.splitext(fname)[0]
            phid = imid[:17]
            extensions = imid[17:]
            camera = imid[8:13]
            date = "%s-%s-%s" % (imid[:4], imid[4:6], imid[6:8])
            print ("ready to go with params", phid, "+", extensions, camera, date)
            return render(request, "photodb/entry_single.htm", locals())

from .Thumbnails import make_thumbnail as makethumbnail
def make_thumbnail(imid):
    print ("running making thumbnail() for", imid)
    src = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "photos", imid[:6], imid+".jpg")
    trg = os.path.join("/media/data/data/tomcat/webapps/ROOT",
                               "thm", "photos", imid[:6], imid+".jpg")
    if not os.path.exists(src):
        src = os.path.join("data", "static", "photos", imid[:6], imid+".jpg")
        trg = os.path.join("data", "static", "thm", "photos", imid[:6], imid+".jpg")
    print (src, os.path.exists(src))
    print ("in", trg, os.path.exists(trg))
    if not os.path.exists(trg):
        print ("\tshould make thum")
        try:
            if not os.path.exists(os.path.split(trg)[0]):
                os.makedirs( os.path.split(trg)[0] )
                print ("dir[s] created", os.path.split(trg)[0])
            print ("will now call Thumbnails.make_thumbnail from")
            print (src, os.path.exists(src))
            print ("to", trg, os.path.exists(os.path.dirname(trg)))
            Thumbnails.make_thumbnail(src, trg)
            print ("done?", trg, os.path.exists(trg))
            ##makethumbnail(src, trg, size=(100000, 100))
        except:
            print (sys.exc_info()[0])
            print (sys.exc_info()[1])
            raise
        return trg
    else:
        return "existed %s" % trg

def move_deleted_photo(request, imid):
    src_path = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (imid[2:4], imid[:8], imid)
    del_dir = "/media/data/data/NewPhotos%s/%s/DELETED" % (imid[2:4], imid[:8])
    if not os.path.exists(del_dir):
        os.mkdir(del_dir)
    trg_path = "/media/data/data/NewPhotos%s/%s/DELETED/%s.jpg" % (imid[2:4], imid[:8], imid)
    print ("will move")
    print (src_path)
    print (trg_path)
    ret = os.rename(src_path, trg_path)
    print (ret)
    return HttpResponse("OK")   

## debugging
def save_photo_records(request, saved=[]):
    print ("running save_photo_records with saved=", saved)
    if request.POST:
        meta = request.POST
    elif request.GET:
        meta = request.GET
    phid = meta.get("PHID")
    pnid = meta.get("PNID")
    lcid = meta.get("LCID")
    pnid = int(pnid)
    print("debug: %s %s %s" % (lcid, pnid, phid))
    if not lcid:
        print (meta)
        raise Exception("LCID is now obligatory")    
    name = Name.objects.get(pnid=pnid)
    print ("will save to name", name)
    category = name.category
    if category == "vascular":
        table = VascularImage
    elif category == "nonvascular":
        table = NonVascularImage
    elif category == "animals":
        table = AnimalImage
    else:
        table = VariaImage
    print ("will create record according category and table", category, table)   
    existed = table.objects.filter(plant_id=pnid).filter(phid=phid)
    print ("existed", existed)
    if existed:
        print ("records with such %s and %s already exists" % (pnid, phid))
        print ("records with such %s already exists" % phid)
        for r in existed:
            print (r)
        raise Exception ("record %s already exists" % phid)
    extensions = meta.get("extensions")
    location = Location.objects.get(lcid=lcid)
    print ("found location", location)
###    raise Exception("debug XXX") ##
    if not extensions:
        extensions = [""]
    else:
        extensions = extensions.split() ## ,
    print ("debug: extensions", extensions)
    for ext in extensions:
        imid = phid + ext
        print ("will save %s" % imid)
        rec = table()
        rec.imid = imid
        plant = Name.objects.get(pk=int(pnid))
        rec.plant = plant
        rec.phid = phid
        ##rec.fid = name.fid
##        try:
##            rec.genname = name.upper.latname ## FIXME might be None
##            rec.famname = name.upper.upper.latname ## FIXME might be None
##        except:
##            rec.genname = name.legacy_parent.latname ## FIXME might be None
##            rec.famname = name.legacy_parent.legacy_parent.latname ## FIXME might be None
##            print ("tried legacy parent instead of upper")
##        rec.latname = name.latname
##        rec.colnames = name.colnames
##        rec.authors = name.authors
        rec.lcid_temp = meta.get("LCID", "")
        print (meta.get("LCID"), rec.lcid_temp) ## passed
##        raise Exception("debug XXX") ##
        locality = Location.objects.get(pk=rec.lcid_temp)
        rec.locality = locality
        rec.inid  = meta.get("IndID", "")
        if not rec.inid:
            inid = "ind.%s.%s" % (rec.spid, lcid)
            rec.inid = inid
            print ("enforce making indID", rec.inid)
        rec.location  = location.public_name
        rec.town  = location.town
        print ("set location", rec.lcid, rec.town, rec.location)
        rec.date  = get_date_formatted(meta.get("created"))
        rec.caption  = meta.get("caption", "***") ## FIXME: still empty
##        raise Exception("debug XXX, location locality set")
        if not rec.caption:
            rec.caption = "***"
        ## new 2022-06-08
        if rec.caption and 'PLANTED' in rec.caption.upper():
            rec.is_planted = 'yes' ## FIXME  OK ?
            print ("set planted")
        rec.gps  = meta.get("gps", "")
        rec.nr  = float(meta.get("nr", 100))
        ##rec.status = meta.get("status", "")
        ##rec.is_verified = meta.get("is-verified", "")
        ##rec.is_planted = meta.get("is_planted", "")
        rec.herb_id = meta.get("herbNum", "")
        rec.tags = meta.get("tags", "")
        rec.notes = meta.get("comments", "")
        rec.gps_error = meta.get("gps_error", "")
        rec.reintroduced = meta.get("reintroduced", "")
        rec.committed = timezone.now()
        rec.modified = rec.committed
        print ("ready to save debug::", rec, ":", rec.town, ":", rec.location, ":", rec.inid, ":", rec.caption)
        rec.save()
        print ("saved", rec)
        print ("XXX should now move image to final destination, together with original")
        print ("should update File Record")
### FIXME patched if not using tomcat 
        if os.path.exists("/media/data/data/tomcat/webapps/ROOT/photos/"):
            trg_path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (rec.imid[:6], rec.imid)
        else:
            trg_path = "data/static/photos/%s/%s.jpg" % (rec.imid[:6], rec.imid)
        print ("edited", trg_path, os.path.exists(trg_path))
##        raise Exception("debug XXX")
        src_path = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.imid)
        if not os.path.exists(src_path):
            src_path = "data/WORK/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.imid)
### end of patched, existence of other locationss not checked
        trg_dir = os.path.split(trg_path)[0]
        if not os.path.exists(trg_dir):
            os.mkdir(trg_dir)
            print ("created", trg_dir, os.path.exists(trg_dir))
        print (src_path, os.path.exists(src_path))
        try:
            os.rename(src_path, trg_path)
        except (OSError):
            print (sys.exc_info())
            print ("will try shutil")
            shutil.copy2(src_path, trg_path)
            print ("will norr try to delete file")
            os.unlink(src_path)
            print ("deleted, will call make thumb")
        ret = make_thumbnail(rec.imid)
        print ("tried making a thumbnails: %s" % ret)
        if rec.plant.longname:
            _log = "<a target='show' href='/photodb/gallery/view/%s/%s'>%s</a> %s [%s]<br/>" % (rec.plant.pk, rec.imid, rec.plant.longname, rec.location, rec.inid)
        else:
            longname = "%s %s" % (rec.plant.upper.latname, rec.plant.latname)
            _log = "<a target='show' href='/photodb/gallery/view/%s/%s'>%s</a> %s [%s]<br/>" % (rec.plant.pk, rec.imid, longname, rec.location, rec.inid)            
        saved.append(_log)
        ##saved.append((rec.inid, rec.location, rec.plant.pk, rec.plant.longname))
    if extensions:
        print ("need move also original")
        src_path = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.phid)
        print ("orig", src_path, os.path.exists(src_path))
        if not os.path.exists(src_path):
            src_path = "data/WORK/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.phid)
        trg_path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (rec.imid[:6], rec.phid)
        if not os.path.exists("/media/data/data/tomcat/webapps/ROOT/photos/"):
            trg_path = "data/static/photos/%s/%s.jpg" % (rec.imid[:6], rec.phid)
        print (trg_path, os.path.exists(trg_path))
        if os.path.exists(src_path):
            try:
                os.rename(src_path, trg_path)
            except(OSError):
                shutil.copy2(src_path, trg_path)
                os.unlink(src_path)
    print ("FIXME and should redirect to next image if exists", saved)
    log = open("saved.log", "w")
    log.write(str(saved))
    log.close()
    print ("debug end of def will sent OK", log)
    return HttpResponse("OK")    

from photos import tools
def entry_form(request, template="photodb/entry_legacy.htm"):
    done = []
    if request.POST:
        print (request.POST)
        return HttpResponseBadRequest("entry_form is not used for POST requests anymore") 
##        meta = request.POST
##        phid = request.POST.get("PHID")
##        pnid = request.POST.get("PNID")
##        pnid = int(pnid)
##        name = Name.objects.get(pnid=pnid)
##        print ("will save to ", name)
##        category = name.category
##        if category == "vascular":
##            table = VascularImage
##        elif category == "nonvascular":
##            table = NonVascularImage
##        elif category == "animals":
##            table = AnimalImage
##        else:
##            table = VariaImage
##        print ("will create record according", category, table)
##        existed = table.objects.filter(plant=name).filter(phid=phid)
##        if existed:
##            print ("records with such %s already exists" % phid)
##            raise Exception ("record %s already exists" % phid)
##        extensions = request.POST.get("extensions")
##        try:
##            location = Location.objects.get(lcid=lcid)
##        except:
##            location = None
##            raise Exception("no locaction for %s" % lcid)
##        if not extensions:
##            extensions = [""]
##        else:
##            extensions = extensions.split(',')
##        for ext in extensions:
##            imid = phid + ext
##            print ("will save %s" % imid)
##            rec = table()
##            rec.imid = imid
##            ##plant = Name.objects.get(pk=int(pnid))
##            rec.plant = name
##            ##rec.spid = int(pnid)
##            rec.phid = phid
##            ##rec.fid = name.fid
##            ##rec.famname = name.upper.upper.latname
##            ##rec.genname = name.upper.latname
##            ##rec.latname = name.latname
##            ##rec.colnames = name.colnames
##            ##rec.authors = name.authors
##            rec.lcid_temp = meta.get("LCID", "")
##            try:
##                location = Location.objects.get(pk=rec.lcid_temp)
##                rec.locality = location
##            except:
##                print("cannot set locality")
##            rec.inid  = meta.get("IndID", "")
##            done.append((name.longname, pnid, rec.inid)) ## FIXME: new
##            rec.location  = location.public_name
##            rec.town  = location.town
##            rec.date  = get_date_formatted(meta.get("created"))
##            rec.caption  = meta.get("caption", "***")
##            rec.gps  = meta.get("gps", "")
##            rec.nr  = float(meta.get("nr", 100))
##            ##rec.status = meta.get("status", "")
##            ##rec.is_verified = meta.get("is-verified", "")
##            ##rec.is_planted = meta.get("is_planted", "")
##            rec.herb_id = meta.get("herbNum", "")
##            rec.tags = meta.get("tags", "")
##            rec.notes = meta.get("comments", "")
##            rec.gps_error = meta.get("gps_error", "")
##            rec.reintroduced = meta.get("reintroduced", "")
##            rec.committed = timezone.now()
##            rec.modified = rec.committed
##            print ("ready", rec)
#####            rec.save()
##            print ("saved", rec)
##            print ("XXX should now move image to final destination, together with original")
##            print ("should update File Record")
##            trg_path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (rec.imid[:6], rec.imid)
##            print (trg_path, os.path.exists(trg_path))
##            src_path = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.imid)
##            print (src_path, os.path.exists(src_path))
##            if not os.path.exists(src_path):
##                src_path = "%s/%s.jpg" % (meta.get("path", "XXX"), rec.imid)
##                print (src_path, os.path.exists(src_path))
##            if not os.path.exists(src_path):
##                src_path = "/home/salicarium/oldhome/_data/_data/NewPhotos09/EUROPE/20090926_turenki/Spentandra/%s.jpg" % rec.imid
##            print (src_path, os.path.exists(src_path))
##            try:
##                os.rename(src_path, trg_path)
##            except OSError:
##                import shutil
##                path = meta.get("path")
##                print ("base path from GET/POST", path)
##                shutil.copy2(src_path, trg_path)
##                if os.path.exists(trg_path):
##                    print ("copied", os.path.exists(trg_path))
##                    os.unlink(src_path)
##                    print ("delete original?")
##                else:
##                    raise OSError("something wrong")
####        if extensions and extensions.strip(): 'list' object has no attribute 'strip'
####            print ("need move also original")
####            print ("XXX not yet ready for cross link etc")
####            src_path = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.phid)
####            print (src_path, os.path.exists(src_path))
####            trg_path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (rec.imid[:6], rec.phid)
####            print (trg_path, os.path.exists(trg_path))
####            os.rename(src_path, trg_path)
####        print ("FIXME and should redirect to next image if exists")
##        ttarget = make_thumbnail(rec.imid)
##        print ("made thumbnail @", ttarget)
##        return HttpResponse("""<a href="/photodb/gallery/view/%s/%s/">%s</a>""" % (pnid, rec.imid, rec)) ## pk ne rabotaet
    ## 'VascularImage' object has no attribute 'plant__pnid'
    else:       
        area = request.GET.get("area")
        print ("entry_form no POST", done, "filteringby", area)
        if area:
            ret = tools.update_options(None, filtering=area)
            print (ret)
        else:
            ret = tools.update_options(None)
            print (ret)
        return render (request, template, locals())


## ex ~/django3/photos/views
def send_image(request, fname):
    ''' for .jpg fname not in use yet'''
    import os
    print ("running send_jpg at", os.getcwd())
    print ("request.META['PATH_INFO'][1:]", request.META['PATH_INFO'][1:])
    get = request.GET
    if get:
        for item in get:
            print ("get", item, get[item])
        if get["path"]:
            jpg = request.META['PATH_INFO'][1:].split("/")[-1]
            abspath = os.path.join(get["path"], jpg)
        else:
            ## FIXME jpg
            abspath = os.path.join(os.getcwd(), request.META['PATH_INFO'][1:])  ## 'photos',
    else:
        jpg = "favicon.ico" ## FIXME
        abspath = "/home/salicarium/django3/favicon.ico" ## FIXME
    abspath = os.path.normpath(abspath)
    print (abspath, os.path.exists(abspath), "exists")
    if os.path.exists(abspath):
        content = open(abspath, "rb").read()
        if jpg.endswith("jpg"):
            return HttpResponse(content, "image/jpeg")
        elif jpg.endswith("png"):
            return HttpResponse(content, "image/png")
        elif jpg.endswith("ico"):
            return HttpResponse(content, "image/ico")
        elif jpg.endswith("gif"):
            return HttpResponse(content, "image/gif")
        else:
            return HttpResponse(content, "image/gif") ## XXX
    else:
        return HttpResponse("NOT FOUND: <br/>" + abspath)



def get_date_formatted(date):
    year, month, day = date.split('-')
    month = int(month)
    month = MONTHES[month-1]
    if day.startswith('0'):
        day = day[1:]
    formatted = "%s %s," % (month, day)
    print (date, "to", formatted)
    return formatted

def commit_prepared(request, imid):
    phid = imid[:17]
    ROOT = "/media/data/data/"
    prepared = "%sNewPhotos%s/%s/_tree.xml" % (ROOT, phid[2:4], phid[:8])
    dom = xml.dom.minidom.parse(prepared)
    print ("looking for", phid, dom)
    meta = {}
    for photo in dom.getElementsByTagName("photo"):
        if phid == photo.getAttribute("PHID"):
            print ("find prepared")
            sp = photo.parentNode.parentNode.parentNode
            meta = {"phid": phid, "latname": sp.getAttribute("_latname"), "authors": sp.getAttribute("_authors"), "colnames": sp.getAttribute("_colname"),
                    "spid": int(sp.getAttribute("PNID")), "nr": float(photo.getAttribute("nr")), "gps": photo.getAttribute("gps"), "camera": photo.getAttribute("camera"),
                    "created": photo.getAttribute("created"), "creator": photo.getAttribute("by"), "recorded": photo.getAttribute("recorded"),
                    "lcid": photo.getElementsByTagName("LCID")[0].firstChild.nodeValue,
                    "fid": photo.getElementsByTagName("FID")[0].firstChild.nodeValue,
                    "inid": photo.getElementsByTagName("IndID")[0].firstChild.nodeValue,
                    "imid": imid,
                    "famname": "",
                    "genname": "",
                    "location": "XXX",
                    "town": "XXX",
                    "date": "XXX",
                    "status": "",
                    "is_verified": "",
                    "is_planted": "",
                    "herb_id": "",
                    "tags": "",
                    "notes": "",
                    "gps_error": "",
                    "reintroduced": "",
                    }
            try:
                meta["caption"] = photo.getElementsByTagName("caption")[0].firstChild.nodeValue
            except:
                pass
            try:
                meta["notes"] = photo.getElementsByTagName("comments")[0].firstChild.nodeValue
            except:
                pass
            print (meta)
            break
    name = Name.objects.get(pnid=meta.get("spid"))
    print ("name", name)
    genus = name.legacy_parent
    family = genus.legacy_parent
    meta["famname"] = family.latname
    meta["genname"] = genus.latname
    meta["date"] = meta.get("created")
    print ("updated", meta)
    try:
        loc = Location.objects.get(lcid = meta.get("lcid"))
        print (loc)
        meta["town"] = loc.town
        meta["location"] = loc.public_name
    except:
        if meta.get("lcid") == "MA.Frn.Nro.202105181":
            meta["location"] = "Northfield State Forest, Northfield"
            meta["town"] = "Northfield"
        else:
            raise
    meta["latname"] = "%s %s" % (genus.latname, name.latname)
    meta["authors"] = name.authors
    meta["colnames"] = name.colnames
    print ("final", meta)
    category = name.category
    
    print ("will create record according", category)
    if category == "vascular":
        table = VascularImage
        manager = table.objects
        existed = manager.filter(spid=meta.get("spid")).filter(imid=meta.get("imid"))
        if existed:
            existed = existed[0]
            print ("record already exists", existed)
        else:
            existed = manager.filter(spid=meta.get("spid")).filter(imid__startswith=meta.get("phid"))
            if existed:
                existed = existed[0]            
                print ("record already exists", existed)           
            else:
                print ("may create new record")
                rec = table()
                rec.imid = meta.get("imid", "")
                rec.spid = int(meta.get("spid"))
                rec.phid = meta.get("phid", "")
                rec.fid = int(meta.get("fid"))
                rec.famname = meta.get("famname", "")
                rec.genname = meta.get("genname", "")
                rec.latname = meta.get("latname", "")
                rec.colnames = meta.get("colnames", "") 
                rec.authors = meta.get("authors", "")
                rec.lcid = meta.get("lcid", "")
                rec.inid  = meta.get("inid", "")
                rec.location  = meta.get("location", "")
                rec.town  = meta.get("town", "")
                rec.date  = meta.get("date", "")
                rec.caption  = meta.get("caption", "***")
                rec.gps  = meta.get("gps", "")
                rec.nr  = meta.get("nr", 100)
                rec.status = meta.get("status", "")
                rec.is_verified = meta.get("is-verified", "")
                rec.is_planted = meta.get("is_planted", "")
                rec.herb_id = meta.get("herb_id", "")
                rec.tags = meta.get("tags", "")
                rec.notes = meta.get("notes", "")
                rec.gps_error = meta.get("gps_error", "")
                rec.reintroduced = meta.get("reintroduced", "")
                rec.committed = timezone.now()
                rec.modified = rec.committed
                formatted = get_date_formatted(rec.date)
                rec.date = formatted
                print ("ready", rec)
###                rec.save()
                print ("saved", rec)
                url = "http://192.168.1.9:9090/photoDB/gallery/view/%s/%s/%s/" % (rec.fid, rec.spid, rec.imid)
                print (url)
                imid_path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (rec.imid[:6], rec.imid)
                print (imid_path, os.path.exists(imid_path))
                if not os.path.exists(imid_path):
                    imid_src = "/media/data/data/NewPhotos%s/%s/%s.jpg" % (rec.imid[2:4], rec.imid[:8], rec.imid)
                    print (imid_src, os.path.exists(imid_src))
                    if os.path.exists(imid_src):
                        os.rename(imid_src, imid_path)
                        print ("still need to update FileRecords")
                    else:
                        print ("something wrong files not found", imid_src, imid_path)
                        raise IOError("imid file not found: %s" % imid)
                else:
                    print ("file already in tomcat", imid_path)
                return HttpResponseRedirect(url)
    return HttpResponseBadRequest("something wrong, cannot commit %s from prepared in NewPhotos" % imid)
    
""" can prefill: models: any rec
    imid = models.CharField(max_length=50)
    spid = models.IntegerField()
    phid = models.CharField(max_length=50)
    fid = models.IntegerField()
    ## initial / temporary fields
    famname = models.CharField(max_length=150, null=True, blank=True)
    genname = models.CharField(max_length=150, null=True, blank=True)
    latname = models.CharField(max_length=150, null=True, blank=True)
    colnames = models.CharField(max_length=250, null=True, blank=True)
    authors = models.CharField(max_length=150, null=True, blank=True)
    
    lcid = models.CharField(max_length=150, null=True, blank=True)
    inid = models.CharField(max_length=150, null=True, blank=True)
    location =  models.CharField(max_length=150, null=True, blank=True) 
    town = models.CharField(max_length=150, null=True, blank=True) ## redundant
    date = models.CharField(max_length=150, null=True, blank=True) 
    caption = models.TextField(null=True, blank=True) 
    gps = models.CharField(max_length=150, null=True, blank=True)
    nr = models.FloatField(null = True)

    status = models.CharField(max_length=150, null=True, blank=True)
    is_verified = models.CharField(max_length=10, null=True, blank=True)
    is_planted = models.CharField(max_length=10, null=True, blank=True) ## verbose
    herb_id = models.CharField(max_length=10, null=True, blank=True) ## irrelevant
    tags = models.CharField(max_length=256, null=True, blank=True) 
    notes = models.CharField(max_length=256, null=True, blank=True) ## text field

    ## more to add
    gps_error = models.CharField(max_length=10, null=True, blank=True) ## irrelevant ?
    reintroduced = models.CharField(max_length=10, null=True, blank=True) ## irrelevant

"""

def commit_gpx(request, imid, category):
    phid = imid[:17]
    ROOT = "/media/data/data/"
    url = "http://192.168.1.9:9090/admin/photodb/%s/add/?imid=%s&phid=%s" % (category, imid, phid)
    mapped = "%sNewPhotos%s/%s/%s_mapped.gpx" % (ROOT, phid[2:4], phid[:8], phid[:8])
    print (mapped, os.path.exists(mapped))
    if not os.path.exists(mapped):
        mapped = "%s/tomcat/webapps/ROOT/photos/%s/%s_mapped.gpx" % (ROOT, phid[2:4], phid[:8], phid[:8]) ## so far not in use
        print (mapped, os.path.exists(mapped))
    if not os.path.exists(mapped):
        print ("XXX: always presume vascular Image")
        ##return HttpResponseRedirect(url)
    else:
        meta = {}
        dom = xml.dom.minidom.parse(mapped)
        print(dom)
        for wpt in dom.getElementsByTagName("wpt"):
            name = wpt.getElementsByTagName("name")[0]
            phid_ = name.firstChild.nodeValue
            print (phid_, wpt.toxml())
            if phid == phid_:
                print ("found")
                meta = {"phid": phid, "lcid": wpt.getAttribute("LCID"),
                        "ops": wpt.getAttribute("OPS"),
                        "lat": wpt.getAttribute("lat"),
                        "lon": wpt.getAttribute("lon"),
                        "town": wpt.getAttribute("town"),
                        "created":wpt.getElementsByTagName("time")[0].firstChild.nodeValue.replace(' ', 'T')
                        }
                print (meta)
                break
        if meta:
            if meta.get("lcid"):
                url += "&lcid=%s" % meta.get("lcid")
            if meta.get("town"):
                url += "&town=%s" % meta.get("town")
            if meta.get("lat") and meta.get("lon"):
                url += "&gps=%s%s" % (meta.get("lat"), meta.get("lon"))
            url += "&notes=%s %s" % (meta.get("ops", ""), meta.get("created"))
            print (url)
            ##return HttpResponseRedirect(url)
        else:
            print (url)
            ##return HttpResponseRedirect(url)
    return HttpResponse("yet not practical using %s" % url)
    ##return HttpResponseRedirect(url)

def commit_tomcat (request, imid, category):
    phid = imid[:17]
    ROOT = "/media/data/data/"
    prepared = "%sNewPhotos%s/%s/_tree.xml" % (ROOT, phid[2:4], phid[:8])
    print (prepared, os.path.exists(prepared))
    if not os.path.exists(prepared):
        prepared = "/media/data/data/tomcat/webapps/ROOT/photos/%s/_tree.xml" % phid[:6]
        print (prepared, os.path.exists(prepared))
    if os.path.exists(prepared):
        dom = xml.dom.minidom.parse(prepared)
        print ("looking for", imid, "in", dom)
        print ("will use commit prepared")
        return commit_prepared(request, imid)
    else:
        print ("will try mapped gpx")
        return commit_gpx(request, imid, category)
        
###FIXME common.models.DoesNotExist: Location matching query does not exist. MA.Frn.Nro.202105181
        


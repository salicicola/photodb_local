import os, sys, time, xml.dom.minidom, datetime, urllib
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from . import EXIF, EXIF_PIL
try:
    from . import garmin_tools
except:
    garmin_tools = None
    print ("Garmin tools are not available")
SITE_ROOT = str(settings.BASE_DIR)
SOURCE = "%s/data/WORK" % SITE_ROOT

print ("photos.process:: modules loaded:", EXIF, EXIF_PIL, garmin_tools)
##try:
##    from . import correct_tz, process_tracks
##except:
##    correct_tz = None
##    process_tracks = None
##    print ("synchronizing photos by GPS unit is not available on this server")
##print ("USAGE in shell: import module and then run {module}.process_dir(ymd) in format YYYYMMDD")

GPX_EMPTY = """<?xml version="1.0" ?><gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
                xmlns:wptx1="http://www.garmin.com/xmlschemas/WaypointExtension/v1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="" version="1.1"
                xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3
                http://www8.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/WaypointExtension/v1 http://www8.garmin.com/xmlschemas/WaypointExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1
                http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"><metadata>
		<time>%s</time></metadata><trk></trk></gpx>""" % datetime.datetime.now().isoformat()

## FIXME globals ::
dom = xml.dom.minidom.parseString("<files/>") ### XXX global
root = dom.documentElement
processed = {}
processing = {}
_camera = "xxxxx"                                   ## XXX
_date_ = "xxxxx"
try:
    log = open ("data/RENAME/last_number.txt")
    NUM_START = int(log.read())
    log.close()
except:
    NUM_START = 0
fnum = NUM_START
print ("initial fnum", fnum)

SITE_ROOT = str(settings.BASE_DIR)
print ("SITE_ROOT", SITE_ROOT)
SOURCE = "%s/data/WORK" % SITE_ROOT
print ("valid dir for New photos:", SOURCE)

def process(request):
    return render (request, "photos/rename.htm")

def rename(request, ymd):
    SRC = "%s/NewPhotos%s/%s/" % (SOURCE, ymd[2:4], ymd) ## FIXME
    print ("debugging", SRC, os.path.exists(SRC))         
    if not os.path.exists(SRC):
        raise IOError("%s NOT AVAILABLE" % SRC)
    try:
        log = open ("%s/data/RENAME/last_number.txt" % SITE_ROOT)
        print(log)
        fnum = int(log.read().strip())
        print (fnum)
    except:
        fnum = 0
        print ("will not allow to set automatically fnum to zero: potentially may lead to errors", fnum, "> will raise Exception")
        raise Exception("set initial file number (e.g., 0) in data/RENAME/last_number.txt, and run again")
    print ("running rename first step: initial fnum", fnum)
    raw_images = []
    for f in os.listdir(SRC):
        ##if os.path.splitext(f)[1] == ".JPG": ## XXX
        if os.path.splitext(f)[1].lower() == ".jpg":
            if len (f) < 21:  ## FIXME
                raw_images.append(f)
                print ("appended", f)
    if not raw_images:
        print ("nothing to rename")
        return HttpResponse("nothing to do")
    else:
        rename_exif_files(SRC, fnum)
        print ("done first pass")
    print ("patching using PIL for coordinates processing with SRC=", SRC)
    print ("i.e., will try to get coordinates from exif")
    embedded = setlatlon(SRC, ymd) ## > MUST generating {ymd}_mapped.gpx if possible
    if embedded:
        print ("%s embedded gps found and recorded" % embedded)
        mapped = "%s/%s_mapped.gpx" % (SRC, ymd)
        print ("created %s, %s bytes" % (mapped, os.path.getsize(mapped)))
    garmin = update_by_garmin (None, ymd)
    if garmin:
        print ("updated by sync with garmin")
    else:
        print ("cannot sync by garmin")
    return update_by_GIS(request, ymd)
    ##return HttpResponse("%s files should have been renamed and exif extracted, if possible with coordinates" % len(raw_images))

def rename_exif_files(start, fnum):
    """ from exif_rename.process_dir etc. """
    print ("running .rename_exif_files(%s)" % start)
    
    START_DIR = "."
    empty = open("photos/empty.jpg", "rb") ## FIXME
    JPGS = empty.read()
    empty.close()
    print("loading...", len(JPGS), "empty jpg loaded")
    ##dom = xml.dom.minidom.parseString("<files/>") in global
    root = dom.documentElement
    root.setAttribute("engine_used", "Python/" + sys.version.split(' ')[0])
    root.setAttribute("parser_used", "EXIF.py (1.1.0) and " + os.path.split(__file__)[1])
    root.setAttribute("generated_at", time.asctime())
    print(root)
    ROOT_DIR = os.getcwd()
    print(root.toxml(), "ready to process from", fnum)
    exif_dir = os.path.join(start, "exif")
    if not os.path.exists(exif_dir):
        os.mkdir(exif_dir)
        print("made exif dir")
    else:
        print("exif dir already exists")
    files = []
    for f in os.listdir(start):
        if os.path.splitext(f)[1].lower() == ".jpg" or os.path.splitext(f)[1].lower() == ".avi" or os.path.splitext(f)[1].lower() == ".mov":
            if len(f) == 12:
                print(f)
                t = os.path.getmtime(os.path.join(start, f))
                files.append((t, f))
            elif len(f) == 19 and '_' in f:
                print(f, "ex phone")
                t = os.path.getmtime(os.path.join(start, f))
                files.append((t, f))
            else:
                print(f, "unknown origin")
                t = os.path.getmtime(os.path.join(start, f))
                files.append((t, f))
    files.sort()
    print ("files", files)
    for tf in files:
        parse_file(os.path.join(start, tf[1]))
        try:
            out = os.path.join(start, processing["now"][1])
            os.rename(processing["now"][0], out)
            print("\trenamed", processing["now"][0], out)
        except:
            print("error::", sys.exc_info())
            ### XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    print("---")
    print (processed)
    print (processed.keys())
    outxml = os.path.join(start, "exifdata" + list(processed.keys())[0] + ".xml")
    print("out", outxml)
    print("outxml", outxml)
    if not os.path.exists(outxml):
        writer = open(outxml, "w")
        root.writexml(writer)
        writer.close()
    else:
        print("EXIF FILE ALREADY EXISTS")
        if os.path.exists(outxml + ".bak"):
            os.unlink(outxml + ".bak")
            print("EXIF bsk FILE ALREADY EXISTS, DELETED")
        domold = xml.dom.minidom.parse(outxml)
        print("old dom", dom)
        recs = root.getElementsByTagName("file")
        for rec in recs:
            ## no export in Python ?
            domold.documentElement.appendChild(rec)
        print("xml dom updated")
        os.rename(outxml, outxml + ".bak")
        print("BAK file created")
        writer = open(outxml, "w")
        domold.writexml(writer)
        writer.close()
        print("DONE with new XML")       
    print("current max number = ", fnum)

def parse_file(fname):
    global fnum, _camera, _date_                    ## XXX and dom ?
    fdir = os.path.split(fname)[0]
    fsize = os.path.getsize(fname)
    _modified = os.path.getmtime(fname)
    modified = time.ctime(_modified)
    f = open(fname, "rb")
    try:
        fnum += 1
        print("fnum", fnum, fname)
        log = open (os.path.join("data/RENAME/last_number.txt"), "w") ## ROOT_DIR removed
        log.write(str(fnum))
        log.flush()
        log.close()
        log = None
        time.sleep(0.5)
        log = open (os.path.join("data/RENAME/last_number.txt")) ## ROOT_DIR, 
        log.close()
        log = None
        time.sleep(0.5)
        print ("got to line 51")
    except:
        print ("error in parse_file", fname)
        raise
        print(sys.exc_info()[0], sys.exc_info()[1])
    ######################################### exif reading if JPG
    if os.path.splitext(fname)[1].lower() == ".jpg":
        try:
            print ("here")
            tags = EXIF.process_file(f, details=False)
            print (tags) ##{}
            keys = list(tags.keys())
            print (keys) ##[]
            keys.sort()
            timestamp = None
            camera = None
        except:
            print(sys.exc_info())
            tags = []
            keys = []
            timestamp = None
            camera = None
        try:
            for key in keys:
                value = tags[key]
                if value:
                    if key.find("DateTimeOriginal") > -1:
                        timestamp = str(value)
                    if key.find("Image Make") > -1:
                        camera = str(value)
        except:
            print(sys.exc_info())
        try:    
            _date = timestamp.split()[0].replace(":", "")
            _date_ = _date
            _fname = "%s%s%04d.jpg" % (_date, camera[:5].lower(), fnum)
            _camera = camera[:5].lower()
        except:
            print("ERROR", sys.exc_info())
            _date = ""
            _date_ = _date
            _fname = "20150000xxxxx" + fnum
            _camera = "xxxxx"
        text_name = "%s%s%04d.txt" % (_date, camera[:5].lower(), fnum)
        out_txt = open(os.path.join(fdir, "exif", text_name), "w")
        s = '"FileName","%s"\n' % _fname
        out_txt.write(s)
        for key in keys:
            if key == 'JPEGThumbnail':
                pass
            else:
                try:
                    value = "%s" % tags.get(key, "")
                    s = '"%s","%s"\n' % (key, value) 
                    out_txt.write(s)
                except:
                    print("error in", key, sys.exc_info())
                    s = '"%s","%s"\n' % (key, "parsed error: " + str(sys.exc_info()[1]))
                    print("catched", s)
                    out_txt.write(s)
        out_txt.close()

        def setTag(dom, record, tagname, text):
            print("running setTag with", dom, record, tagname, text)
            txt = dom.createTextNode(text)
            field = dom.createElement(tagname)
            field.appendChild(txt)
            record.appendChild(field)

        def setRecord():
            print("running setRecord")
            record = dom.createElement("file")
            record.setAttribute("ID", os.path.splitext(_fname)[0])
            record.setAttribute("orig_name", fname)
            record.setAttribute("file_name", _fname)
            record.setAttribute("modified", modified)
            record.setAttribute("bytes", str(fsize))
            setTag(dom, record, "FileName", _fname)
            setTag(dom, record, "Make", str(tags["Image Make"]))
            setTag(dom, record, "Model", str(tags["Image Model"]))
            setTag(dom, record, "Saturation", str(tags.get("EXIF Saturation", "")))
            setTag(dom, record, "Sharpness", str(tags.get("EXIF Sharpness", "")))
            setTag(dom, record, "ExposureTime", str(tags.get("EXIF ExposureTime", "")))
            setTag(dom, record, "ExposureProgram", str(tags.get("EXIF ExposureProgram", "",)))

            setTag(dom, record, "DateTime", str(tags.get("EXIF DateTimeOriginal", "")))
            setTag(dom, record, "DateTimeOriginal", str(tags.get("EXIF DateTimeOriginal", "")))
            setTag(dom, record, "DateTimeDigitized", str(tags.get("EXIF DateTimeDigitized", "")))
            
            setTag(dom, record, "ApertureValue", str(tags.get("EXIF ApertureValue", "")))       
            setTag(dom, record, "FNumber", str(tags.get("EXIF FNumber", "")))
            try:
                setTag(dom, record, "MeteringMode", str(tags["EXIF MeteringMode"]))
            except:
                print("error setting MeteringMode, skip it")
            setTag(dom, record, "Flash", str(tags.get("EXIF Flash", "")))
            setTag(dom, record, "FocalLength", str(tags.get("EXIF FocalLength", "")))
            setTag(dom, record, "ExifImageWidth", str(tags.get("EXIF ExifImageWidth", "")))
            setTag(dom, record, "ExifImageHeight", str(tags.get("EXIF ExifImageLength", "")))
            setTag(dom, record, "ExposureMode", str(tags.get("EXIF ExposureMode", "")))
            setTag(dom, record, "WhiteBalance", str(tags.get("EXIF WhiteBalance", "")))
            setTag(dom, record, "SceneCaptureType", str(tags.get("EXIF SceneCaptureType", "")))
            for key in list(tags.keys()):
                if key.find("GPS ") > -1:
                    tagname = key.split()[1]
                    value = "%s" % tags.get(key, "")
                    setTag(dom, record, tagname, value)
            ## root was not defined restored as global
            root.appendChild(record)

        setRecord()
    else:
        print("not JPG", fname, _camera, _date_)
##        _fname = "%s%s%04d.avi" % (_date_, _camera, fnum)       ## XXX : _camera
##        _fname = "%s%s%04d.mov" % (_date_, _camera, fnum)       ## XXX : _camera
        ext = os.path.splitext(fname)[1].lower()
        _fname = "%s%s%04d.%s" % (_date_, _camera, fnum, ext)
    x = processed.get(_fname[:8], 0)
    processed[_fname[:8]] = x + 1
    processing["now"] = (fname, _fname)
    print("processed", fname, _fname, processed, processing)  

def setlatlon(SRC_DIR, ymd):
    xdata = xml.dom.minidom.parse("%s/exifdata%s.xml" % (SRC_DIR, ymd))
    gpx = xml.dom.minidom.parseString(GPX_EMPTY)
    outname = "%s/%s_mapped.gpx" % (SRC_DIR, ymd)
    print (xdata, outname, os.path.exists(outname), gpx)
    with_gps = 0
    
    for filetag in xdata.getElementsByTagName("file"):
        imid = filetag.getAttribute("ID")
        path = "%s/%s.jpg" % (SRC_DIR, imid)
        if os.path.exists(path):
            print (path)
        else:
            raise IOError("path do not exists", path)
##            path = "/media/data/data/tomcat/webapps/ROOT/photos/%s/%s.jpg" % (imid[:6], imid) ## XXX MAY NOT EXIST
##            if os.path.exists(path):
##                print (path)
##            else:
##                raise IOError("do not exists %s" % path)
        image = Image.open(path)
        exif = EXIF_PIL.get_exif_data(image)
        (lat, lon) = EXIF_PIL.get_lat_lon(exif)
        print (path, lat, lon)
        if (lat and lon):
            with_gps += 1
            lat = round(lat, 6)
            lon = round(lon, 6)
            filetag.setAttribute("lat", str(lat))
            filetag.setAttribute("lon", str(lon))
            print (filetag.toxml())
            out = open("temp.xml", "w")
            out.write(filetag.toxml())
            out.close()
            out = None
            wpt = gpx.createElement("wpt")
            wpt.setAttribute("lat", str(lat))
            wpt.setAttribute("lon", str(lon))
            name = gpx.createElement("name")
            name.appendChild(gpx.createTextNode(imid))
            wpt.appendChild(name)                
            time = gpx.createElement("time")
            datetime = filetag.getElementsByTagName("DateTime")[0].firstChild.nodeValue
            time.appendChild(gpx.createTextNode(datetime))
            wpt.appendChild(time)
            print (wpt.toxml())
            gpx.documentElement.appendChild(wpt)
    print ("with gps coordinates", with_gps)
    if with_gps:
        out = open(os.path.join(SRC_DIR, outname), "w")
        out.write(gpx.toxml())
        out.close()
        print (out)
        out = None
        os.rename(os.path.join(SRC_DIR, "exifdata%s.xml" % ymd), os.path.join(SRC_DIR, "exifdata%s.bak.xml" % ymd))
        out = open(os.path.join(SRC_DIR, "exifdata%s.xml" % ymd), "w")
        out.write(xdata.toxml())
        print (out)
        out.close()
    else:
        print ("nothing to do, left unchanged", os.path.join(SRC_DIR, "exifdata%s.xml" % ymd))
    return with_gps


### XXX/FIXME: 'empty.gpx' should be present @SITE_ROOT, not at @SITE_ROOT/photos

def update_by_garmin (request, ymd):    
    SRC_DIR = os.path.join(SOURCE, "NewPhotos%s" % ymd[2:4], ymd)
    print (SRC_DIR, os.path.exists(SRC_DIR))
    print ("will check if any JPG left not renamed")    
    for fname in os.listdir(SRC_DIR):
        print (fname, len(fname))
        files = []
        if os.path.splitext(fname)[1] == ".JPG":
            raise Exception(fname)
        elif os.path.splitext(fname)[1] == ".jpg":
            if len(fname) < 21:
                raise Exception(fname)
            else:
                files.append(fname)
    exif_file="exifdata%s.xml" % ymd
    exif_file_path = os.path.join(SRC_DIR, exif_file)
    print ("total renamed files", len(files))
    print ("exif was processed?", exif_file_path, os.path.exists(exif_file_path))
    raw_garmin_path=os.path.join(SRC_DIR, "Current.gpx")
    print ("GPX from Garmin raw? ", raw_garmin_path, os.path.exists(raw_garmin_path) )
    garmin_file = "%s_trk.gpx" % ymd
    garmin_path = os.path.join(SRC_DIR, garmin_file)
    print ("GPX from Garmin prepared? ", raw_garmin_path, os.path.exists(garmin_path) )
    if os.path.exists(raw_garmin_path):
        if not os.path.exists(garmin_path):
            print ("will run correct timestamps for GPX file from Garmin")
            garmin_tools.correct_tz(ymd) ## (_root) ## XXX should run if NOT exists "%s/%s_trk.gpx" % (SRC, ymd)
            print ("%s/%s_trk.gpx" % (SRC_DIR, ymd), os.path.exists("%s/%s_trk.gpx" % (SRC_DIR, ymd)))
        garmin_tools.process_one_day(ymd) ## FIXME if running after setlatlon will overwrite *.mapped.gpx        
    else:
        if os.path.exists(garmin_path):
            print ("raw garmin file missing but present", garmin_path)
            print ("will run process_one_day() anyway")
            garmin_tools.process_one_day(ymd)
        print ("something wrong or nothing todo")
        if request:
            return HttpResponse("nothing todo")
        else:
            return None
    if request:
        return HttpResponse("processed")
    else:
        print ("returning True")
        return True
    """ final example output:
    20240413_trk_wpt.gpx
    20240413_mapped_skipped.txt
    20240413_mapped.html
    20240413_mapped.gpx
    20240413_trk.gpx
    exifdata20240413.xml
    Current.gpx
    """

## yet use old approach, using /media/data/data locations, and without errors checking
def update_by_GIS (request, ymd):
    URL_GIS=""
    print ("yet using almost unmodified old version, assuming gisapp enabled on this server and new photos outside this app")
    url_external = "%s/gis/update/photos/?path=/media/data/data/NewPhotos24/%s/%s_mapped.gpx&day=%s" % (URL_GIS, ymd, ymd, ymd)
    url_external = "/gis/update/photos/?path=data/WORK/NewPhotos%s/%s/%s_mapped.gpx&day=%s" % (ymd[2:4], ymd, ymd, ymd)
    print (url_external)
    return HttpResponseRedirect(url_external)
""" e.g.,
    url="/gis/update/photos/?path=/media/data/data/NewPhotos24/20240413/20240413_mapped.gpx&day=20240413">
"""


    

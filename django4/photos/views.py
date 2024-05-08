import os, sys, datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from .process import * ## may create circular refs ## FIXME
## XXX changed current dir, must return to BASE_DIR

"""
Responsible for only preprocessing photos by day, located in predefined location and dirname ($SOURCE/NewPhotos{YY}/{YYYYMMDD}
For preprocessing database is not used, file numbers kept in text file, without locking ($SITE_ROOT/data/RENAME/lastnum.txt);
the number is useually reset to 0 manually with a start of next year photos.
Coordinates can be retrived from EXIF or/and by synchronizing with GPS Unit (may not be available in published version).
To find town and location ID from coordinates implemented by redirecting to GIS enabled server (if not available at the same server).
Actual data entry performed by redirecting to another URL (photodb package).
"""

SITE_ROOT = str(settings.BASE_DIR)
print ("SITE_ROOT", SITE_ROOT)
##SOURCES = [os.path.abspath(os.path.join(SITE_ROOT, "..")), "/media/data/data"]
##print ("valid dirs for NewPhotos:", SOURCES)
from . import start_edit4
from .process import SOURCE

def index(request, template="photos/index.htm"):
    return render (request, template)

##def rename(request, template="photos/rename.htm"):
##	return render (request, template)
##	## will redirect and use the following function
##
##def rename_new(request, ymd):
##    return process_dir2(request, ymd)
##    ##return process_dir(request, ymd)


def entry(request, template="photos/entry.htm"):
    return render (request, template)

def entry_day(request, ymd):
    ymd = str(ymd)
    root_path="%s/NewPhotos%s/%s/" % (SOURCE, ymd[2:4], ymd)
    print ("starting views.entry_day() for source path", root_path)
    return start_edit4.start(request, root_path)

def last_committed(request):
    html = "<html><head></head><body>%s --- <a href='/photos/entry/'>back to entry</a><ul>" % datetime.datetime.now().isoformat()
    f = open("saved.log")
    log = f.read()
    log = eval(log)
    f.close()
    for item in log:
        html += "<li>%s</li>\n" % item.replace("<br/>", "")
    html += "</ul></body></html>"
    return HttpResponse(html)


##from . import start_edit4
##def entry_day(request, ymd):
##    ymd = str(ymd)
##    root_path="%s/NewPhotos%s/%s/" % (SOURCES[0], ymd[2:4], ymd)
##    print ("starting views.entry_day() for source path", root_path)
##    return start_edit4.start(request, root_path)


## may not work with IDLE plus bug changing working dir
##
####
####def do_gps(request, ymd):
####    print ("running photos.gps(), testing [hardoded]", ymd)
####    yy = ymd[2:4]
####    src_dir = "data/WRK/NewPhotos%s/%s" % (yy, ymd)
####    print (src_dir, os.path.exists(src_dir))
####    exifname = "exifdata%s.xml" % ymd
####    srcpath = os.path.join(src_dir, exifname)
####    srcpath = os.path.abspath(srcpath)
####    print (srcpath, os.path.exists(srcpath))
####    gpxpath = os.path.join(src_dir, "Current.gpx")
####    gpxpath = os.path.abspath(gpxpath)
####    processed = os.path.join(src_dir, "20230522_trk.gpx")
####    print (gpxpath, os.path.exists(gpxpath))
####    if os.path.exists(srcpath) and os.path.exists(gpxpath):
####        trg = os.path.join("data/GPS", exifname)
####        os.rename(srcpath, trg)
####        print ("moved", os.path.exists(trg))
####        os.rename(gpxpath, os.path.join("data/GPS", "Current.gpx"))
####        print ("moved", os.path.exists( os.path.join("data/GPS", "Current.gpx")))
####        get_gps1(None)
####        get_gps2(None)
####        return get_gps_copy(request)
####    elif os.path.exists(processed):
####        get_gps2(None)
####        return HttpResponse(processed)                
####    else:
####        return HttpResponseBadRequest("something wrong")
####    return HttpResponse("debug")           
####
####XXX= """
####photos/entry/ will go to photodb/dir, then produce empty::
####[04/Apr/2023 09:29:53] "GET /static/scripts/photos/entry/tracker.js HTTP/1.1" 304 0
####[04/Apr/2023 09:29:53] "GET /static/scripts/photos/entry/names.js HTTP/1.1" 304 0
####[04/Apr/2023 09:29:53] "GET /static/scripts/photos/entry/files_json.js HTTP/1.1" 200 475
####[04/Apr/2023 09:29:53] "GET /static/scripts/photos/entry/species.xml HTTP/1.1" 304 0
####
####"""
####
####def get_gps1(request):
####    print ("correcting time and generating {date}_trk.gpx")
####    ret = os.system("cd data/GPS; python3 correct_tz_summer.py")
####    if request:
####        return HttpResponse("done %s" % ret)
####    else:
####        return ret
####
####def get_gps2(request):
####    print ("processing exifdata{date}.xml and {date}_trk.gpx")
####    ret = os.system("cd data/GPS; python3 process_all_tracks_exif_new_olymp.py")
####    if request:
####        return HttpResponse("done %s" % ret)
####    else:
####        return ret
####
###### not suitable: needs password
######def get_gps_local(request):
######    ret = os.system("cd data/GPS; python3 copy_upload_move_log_htm.py")
######
######    return HttpResponse("done %s" % ret)
####
####def get_gps_copy(request):
####    ret = os.system("cd data/GPS; python3 copy_files.py")
####
####    return HttpResponse("done %s" % ret)
####
####def update_gps(request, date):
####    try:
####        import gisapp.view
####        print ("running update_gps with GIS enabled server")
####        return HttpResponseRedirect("/photos/gps/update?date=%s" % date)
####    except ModuleNotFoundError:
####        print (sys.exc_info())
####        print ("GIS is not enabled on this server")
####        path = "data/WRK/NewPhotos%s/%s/%s_mapped.gpx" % (date[2:4], date, date)
####        abspath = os.path.abspath(path)
####        print (abspath, os.path.exists(abspath))
####        return HttpResponseRedirect("http://localhost:8000/gis/update/photos/?path=%s" % abspath)
####
######def entry(request):
######    ret = os.system("cd data/ENTRY; python3 start_edit_gui_python3.py")
######    ##ret = os.system("idle-python3.8 -r /media/data/data/django3/data/ENTRY/start_edit_gui_python3.py")
######    return HttpResponse("done %s" % ret)
####
######def entry_day(request, date):
######    ##ret = os.system("cd data/ENTRY; python3 start_edit_gui_python3.py")
######    ##ret = os.system("idle-python3.8 -r /media/data/data/django3/data/ENTRY/start_edit_gui_python3.py")
######    year = str(date)[2:4]
######    print ("running entry_date()", year, date)
######    ret = os.system("cd data/ENTRY; python3 start_edit3.py /media/data/data/NewPhotos%s/%s" % (year, date))
######    return HttpResponse("done %s" % ret)


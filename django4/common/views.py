import sys, django, os, datetime, xml.dom.minidom, time, email, pickle
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest,  HttpResponseNotFound, HttpResponseRedirect
## HttpResponseRedirect, , Http404
## from .bugs_views import *
VERSION = "0.1.2 (revno #55+) alpha" ##2021-02-20 bug reports improved, revno 8+
LAST_UPDATED = "26 March 2024" #  24 February 2024 "4 February 2023" ## "15 January 2023" #"26 October 2022"
ALTSERVERS = ["http://localhost:9090", "http://192.168.1.9:9090", "http:172.104.19.75"]


## to check corresponding files in static/images
MONTH_TITLE = {
	'January': 'Wintergreen (Gaultheria  procumbens)',
	'February': '',
	'March': '',
	'April': '',
        'May': 'poison ivy (Toxicodendron radicans)',
	'June': 'grass-pink (Calopogon tuberosus)',
	'July': 'waterschield (Brasenia schreberi)',
	'August': 'squarepod seedbox (Ludwigia alternifolia)',
	'September': 'New York ironweed (Vernonia noveboracensis)',
	'October': 'Round-fruited seedbox (Ludwigia sphaerocarpa)',
	'November': '',
	'December': '',
}

## STUB :: images='35,839', taxa='2,055', flora='1,984'
IMAGES = 37080 ## 37058 # 36208 # 36138 ##35839
TAXA =  2190 ## 2187 # 2095 # 2090 ## 2055
FLORA = 2066 ## 2065 #2022 # 2016 ##1984
print ("default", IMAGES, TAXA, FLORA)
if os.path.exists('spp.pickle'):
    f = open('spp.pickle', 'rb')
    p = pickle.load(f)
    f.close()
##    IMAGES = p["images"]
##    TAXA = p["taxa"]
##    FLORA = p["flora"]
    print ("from pickle",  p["images"], p["taxa"], p["flora"])
                    

APPPATH = __file__
WORKING_DIR = os.getcwd()
print ("initializing", APPPATH, VERSION)
print ("working dir of common.views", WORKING_DIR)
BASE_DIR = "static/photos"
TEMP_DIRS = ["static/temp", "data/static/temp/scaled"]
if not os.path.exists(BASE_DIR):
    BASE_DIR = "data/static/photos"
    TEMP_DIRS = ["data/static/photos/temp", "data/static/photos/temp/scaled"]
##if os.path.exists("/media/data/data/NewPhotos21"):
PATTERN_DIR = "/media/data/data/NewPhotos"
##else:
##    PATTERN_DIR = None

print ("common.views [servlet] initialized, will use", BASE_DIR, TEMP_DIRS, "%s??" % PATTERN_DIR, "to search images")

if os.path.exists("data/static/images/notfound.png"):
    f = open("data/static/images/notfound.png", "rb")
    bad_png = f.read()
    f.close()
elif os.path.exists("static/images/notfound.png"):
    f = open("static/images/notfound.png", "rb")
    bad_png = f.read()
    f.close()
else:
    bad_png = None
if bad_png:
    print ("will send not found image")
else:
    print ("will send standard not found page for images")

## updated 2022-03-14 and then 07 Aug modified at  docker_salicicola

import calendar, datetime
def get_calendar():
    t = datetime.datetime.today()
    cal = calendar.HTMLCalendar(calendar.SUNDAY)
    s= cal.formatmonth (t.year,t.month)
    cal = s.replace('>%i<'%t.day, ' style="text-align:center;vertical-align:middle;height:3ex;background-color:yellow">%i<'%t.day)
    return (cal, t.strftime("%B"))

## XXX images, taxa, flora hardcoded    
def salicicola(request): ## , images='35,839', taxa='2,055', flora='1,984'
    images = IMAGES
    taxa = TAXA
    flora = FLORA
    last_updated = LAST_UPDATED
    print ("running salicicola index with hardcoded numbers", images, taxa, flora)
    print ("XXX: TODO first: no search, no non-vascular, no animals") 
    cal, month = get_calendar()
    month_title = MONTH_TITLE.get(month, '')
    return render(request, "salicicola.htm", locals())
##    print ("running salicicola index")
##    JAR = "/media/data/data/tomcat/webapps/ROOT/WEB-INF/lib/saxon9.jar"
##    LOCATION = "common/XSLT"
##    CACHE = "common/CACHE/salicicola.html"
##    if os.path.exists(JAR) and os.path.exists(LOCATION):
##        command = "java -jar %s %s/index.xml %s/index.xsl > %s" % (JAR, LOCATION, LOCATION, CACHE)
##        print (command)
##        os.system(command)    
##        html = open(CACHE).read()
##        print ("cache regenerated")
##        return HttpResponse(html)        
##    if os.path.exists(CACHE):
##        print ("cache exists", os.path.getsize(CACHE), "bytes")
##        html = open(CACHE).read()
##        print ("read %s bytes", len(html))
##        return HttpResponse(html)
##    else:
##        print ("cache not found", CACHE)
##        return HttpResponseNotFound("cannot find cache")


def add_static(request):
    print (request.path, request.path_info, request.get_full_path_info())
    orig = request.get_full_path_info()
    url = "/static%s" % orig
    print ("url", url)
    path = "data/static%s" % orig
    path = os.path.abspath(path)
    print (path, os.path.exists(path))
    if url.endswith('/'):
        url = "%s%s" % (url, "index.html") ## FIXME
    return HttpResponseRedirect(url)

def correct_imid(imid):
    print ("old style imid", imid,)
    a, bc = imid.split('$')
    b = bc[:5]
    c = "0%s" % bc[5:]
    imid = "%s%s%s" % (a, b, c)
    print ("corrected", imid)
    return imid        

import urllib.request
print (urllib.request)

def GetImage(request):
    imid = request.GET.get("id")
    if '$' in imid:
        imid = correct_imid(imid)
    y = imid[:4]
    m = imid[4:6]
    d = imid[6:8]
    path = "%s/%s%s/%s.jpg" % (BASE_DIR, y, m, imid)
    print ("testing", path, os.path.exists(path))
    if not os.path.exists(path):
        for temp_dir in TEMP_DIRS:
            path = os.path.join(temp_dir, imid + ".jpg")
            print ("testing", os.path.abspath(path), os.path.exists(path))
            if os.path.exists(path):
                break
    if not os.path.exists(path) and PATTERN_DIR:
        path = "%s%s/%s%s%s/%s.jpg" % (PATTERN_DIR, y[2:], y, m, d, imid)
        print ("testing", path, os.path.exists(path))
    if not os.path.exists(path):
        ## FIXME new, only in docker version so far
        for SERVER in ALTSERVERS:
           url = "%s/servlet/GetImage?id=%s" % (SERVER, imid)
           print ("will try alt url", url)
           ##import requests ## No module named 'requests'
           ##response = requests.get(url)
##           if response.status_code == 200:
##               print('Web site exists', url)
##               return HttpResponseRedirect(url)
##           else:
##               print('Web site does not exist') 
##               continue

### XXX somewhere here the critical error
           req = urllib.request.Request(url)
           with urllib.request.urlopen(req) as response:
               f = response.read()
               print('Web site exists', url)
               ##image = f.read()
               return HttpResponse(f, "image/jpeg")
               ##return HttpResponseRedirect(url)


           
##           import httplib ## no such module when running in docker
##           c = httplib.HTTPConnection(url)
##           c.request("HEAD", '')
##           if c.getresponse().status == 200:
##               print('web site exists')
##               return HttpResponseRedirect(url)
##           
##           import httplib2 ## no such module at least when running in docker
##           h = httplib2.Http()
##           resp = h.request(url, 'HEAD')
##           assert int(resp[0]['status']) < 400
##           print('Web site exists', url)
##           return HttpResponseRedirect(url)
           """ XXX: for Docker containers, either you need to run them in network_mode: host to use the host’s network systemd,
                or you need to bind to the container’s IP address. You can not bind to the host’s IP address from the contaienr unless using network_mode: host!
                But you can forward the ports from the host, binding to a specific IP address.
           """
          ## with urllib.request.urlopen(url) as response:
          ##     f = response.read()
          ##     image = f.read()
          ##     return HttpResponse(image, "image/jpeg")
        """
            If you wish to retrieve a resource via URL and store it in a temporary location, you can do so via the shutil.copyfileobj() and tempfile.NamedTemporaryFile() functions:
            import shutil
            import tempfile
            import urllib.request

            with urllib.request.urlopen('http://python.org/') as response:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    shutil.copyfileobj(response, tmp_file)
            with open(tmp_file.name) as html:
                pass
        """
        if bad_png:
            print ("will send 404 with image", len(bad_png))
            return HttpResponseNotFound(bad_png, "image/png")
        else:
            print ("will send 404 html")
            return HttpResponseNotFound("not found") ## FIXME add not found GIF
    else:
        f = open(path, "rb")
        image = f.read()
        f.close()
        print ("sending file", f)
        return HttpResponse(image, "image/jpeg")

## not yet in use
def sitemap(request):
    return render(request, "sitemap.htm")

## from old views::

def robots(request):
    return HttpResponse("")

def CaptionEditor(request):
    return HttpResponse("")

### NEW defs needed for the web version + modified urls.py
def redirect_tidmarsh(request):
    path = request.path
    newpath = ""
    if 'map' in path:
        words = path.split('/')
        if path.endswith('/'):
            spid = words[-2]
        else:
            spid = words[-1]
        if spid.isdigit():
            newpath = "/photodb/tidmarsh/map/%s/" % spid
    if newpath:
        html = """<h2>All Tidmarsh related pages moved to <a href="/photodb/tidmarsh/">/photodb/tidmarsh/</a></h2>
                  <p>Try this <a href="%s">url</a> for the map</h2>""" % newpath
    else:
        html = """<h2>All Tidmarsh related pages moved to <a href="/photodb/tidmarsh/">/photodb/tidmarsh/</a></h2>"""
    return HttpResponseBadRequest(html)
""" valid urls
        /photodb/tidmarsh/map/15610/
    not valid from log:
        /tidmarsh/map/preview/plant/3152/
"""

def redirect_gallery(request, delay=7):
    path = request.path
    newpath = path.replace('mobile', 'view')
    newpath = "/photodb%s" % newpath
    url = newpath
    html = """<html><head><meta http-equiv="refresh" content="%s;URL='%s'" /></head><body><h2>Wrong address [%s].</h2> 
              <p>URL starting with /gallery/ are moved to /photodb/, but views for mobile devices are temporarily disabled.<br/>
                 If you are not redirected in a %s seconds, try this link 
                 <a href="%s">%s</a></p></body></html>
           """ % (delay, newpath, path, delay, newpath, newpath)
    return HttpResponseBadRequest(html)


from .bugs_views import *



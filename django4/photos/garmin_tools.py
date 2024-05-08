#!/usr/bin/python3
import xml.dom.minidom, sys, os, time, datetime
from django.conf import settings
SITE_ROOT = str(settings.BASE_DIR)
def correct_tz(ymd=None, path=None, hours=-4):
    if not (ymd) and not (path):
        raise Exception("neither date, nor path provided")
    if ymd:
        year_short=ymd[2:4]
        path = "/media/data/data/NewPhotos%s/%s" % (year_short, ymd)
        print (path)
    if not path:
        raise Exception("no path provided")
    if not os.path.exists(path):
        ## NEW
        year_short=ymd[2:4]
        path = "%s/data/WORK/NewPhotos%s/%s" % (SITE_ROOT, year_short, ymd)
        print (path, os.path.exists(path))
        if not os.path.exists:
            raise Exception("path %s do not exists" % path)
    delta = datetime.timedelta(hours=hours) ## -6
    dom = xml.dom.minidom.parse(os.path.join(path, "Current.gpx"))
    print (dom)
    dtm = None
    pts = dom.getElementsByTagName("trkpt")
    _dtm = pts[0].getElementsByTagName("time")[0].firstChild.nodeValue
    _dtm = _dtm.replace('-', '')
    _dtm = _dtm[:8]

    for pt in pts:
        telement = pt.getElementsByTagName("time")[0]
        tvalue = telement.firstChild
        t = tvalue.nodeValue
        _dt = time.strptime (t, "%Y-%m-%dT%H:%M:%SZ")
        dt = datetime.datetime(_dt[0], _dt[1], _dt[2], _dt[3], _dt[4], _dt[5])
        ndt = dt + delta
        print (dt)
        print (ndt)
        txt = dom.createTextNode(str(ndt).replace(' ', 'T') + 'Z')
        telement.replaceChild(txt, tvalue)
        print()
        
    print (_dtm)
    fname = "%s_trk.gpx" % _dtm
    outpath = os.path.join(path, fname)
    out = open(outpath, "w")
    dom.writexml(out)
    out.close()
    print (out)


## old process_tracks.process_one_day(SRC, ymd[0:4], ymd[4:6], ymd[6:])
STEP = 5.0 ## was 30
MAX_STEPS = 4 ## ok 20
SECONDS_OFFSET = 0 ## 60 * 60 ## -30 ## for the first day -60*60
##SECONDS_OFFSET = 60 * 60 + 50 ## -30 ## for the first day -60*60
YEAR="2020"
MONTH="09"
DAY = "13"
T_FILE = None
E_FILE = None
O_FILE = None
C_FILE = None
dict_points = {}
files_normalized = []
files_combined = []    

bak = """
        if f.startswith('gpx'):
            if os.path.isfile(f):
                new_name = f[4:12] + "_trk.gpx"
                print new_name
                os.rename(f, new_name)
"""
## old ##def process_one_day(ROOT, YEAR, MONTH, DAY):
def process_one_day(ymd):
    global T_FILE, E_FILE, O_FILE, C_FILE, dict_points, files_normalized, files_combined
    ##ROOT="/media/data/data/NewPhotos%s" % ymd[2:4]
    ##if not os.path.exists(ROOT):
    ROOT="%s/data/WORK/NewPhotos%s" % (SITE_ROOT, ymd[2:4])
    if not os.path.exists(ROOT):
        raise IOError("no root to ROOT", ROOT)
    YEAR = ymd[0:4]
    MONTH = ymd[4:6]
    DAY = ymd[6:]
    print ("starting", YEAR, MONTH, DAY, "@", ROOT)
    T_FILE = "%s/%s/%s%s%s_trk.gpx" % (ROOT, ymd, YEAR, MONTH, DAY)
    E_FILE = "%s/%s/exifdata%s%s%s.xml" % (ROOT, ymd, YEAR, MONTH, DAY)
    O_FILE = "%s/%s/%s%s%s_mapped.gpx" % (ROOT, ymd, YEAR, MONTH, DAY) ## XXX empty?
    C_FILE = "%s/%s/%s%s%s_trk_wpt.gpx" % (ROOT, ymd, YEAR, MONTH, DAY) ## XXX empty
    
    dict_points = {}
    files_normalized = []
    files_combined = []    
    print (T_FILE, os.path.exists(T_FILE))
    print (E_FILE, os.path.exists(E_FILE))
    print (O_FILE, os.path.exists(O_FILE))
    print (C_FILE, os.path.exists(C_FILE))
    ##raise Exception("test")
    if os.path.exists(T_FILE):
        print (T_FILE)
        if os.path.exists(E_FILE):
            print (E_FILE)
##            raise Exception("DEBUG")
##            return
            
            set_tracks_normalized()
            print ("set1")
            set_shots_normalized()
            print ("set2")
            combine()
            print ("combined")
            write_html_acme()
            write_gpx()
            
##            try:
##                os.rename(T_FILE, os.path.join(os.getcwd(), "gpxdata", os.path.split(T_FILE)[1]))
##                return
##                os.rename(E_FILE, os.path.join(os.getcwd(), "exifdata", E_FILE))
##                os.rename(O_FILE, os.path.join(os.getcwd(), "mapped_gpx", O_FILE))
##                os.rename(C_FILE, os.path.join(os.getcwd(), "combo_tracks", C_FILE))
##                fname = "%s%s%s_mapped.html" % (YEAR, MONTH, DAY)
##                os.rename(fname, os.path.join(os.getcwd(), "mapped_htm", fname))
##                print ("end", YEAR, MONTH, DAY)
##            except :
##                print ("error")
##                ##raise
        else:
            print (E_FILE, "doesn't exists")
    else:
        print (T_FILE, "doesn't exists")
    ##print "processed", YEAR, MONTH, DAY

def write_xml():
    print ("write_xml()", "combined", len(files_combined))
    return
    if files_combined:
        impl = xml.dom.minidom.getDOMImplementation()
        newdoc = impl.createDocument(None, "files", None)
        top_element = newdoc.documentElement
        for f in files_combined:
            record = newdoc.createElement("file")
            record.setAttribute("ID", str(f[1]))
            record.setAttribute("file_name", str(f[2]))
            record.setAttribute("timestamp", str(f[3]))
            record.setAttribute("rnd_sec", str(f[0]))
            record.setAttribute("rounded", time.asctime(time.localtime((f[0]))))
            if f[4]: record.setAttribute("lat", str(round(f[4], 5)))
            if f[5]: record.setAttribute("lon", str(round(f[5], 5)))
            if f[6]: record.setAttribute("alt", str(int(round(f[6], 0))))    ## better than just int() ?       
            top_element.appendChild(record)
        out = open(O_FILE, "w")
        print (O_FILE.toxml())
        newdoc.writexml(out, "", "\t", "\n")
        out.close
    else:
        print ("nothing to write")
    print ("done")

def write_gpx():
    print ("running write_gpx()", len(files_combined))
    if files_combined:
        olddoc = xml.dom.minidom.parse(T_FILE)
        old_top_element = olddoc.documentElement
        newdoc = xml.dom.minidom.parse("empty.gpx")
        top_element = newdoc.documentElement
        fname = O_FILE[:-4] + "_skipped.txt"
        out = open ( fname, "w")        
        for f in files_combined:
            if f[4] and f[5]:
                record = newdoc.createElement("wpt")                
                record.setAttribute("lat", str(round(f[4], 5)))               
                record.setAttribute("lon", str(round(f[5], 5)))
                if f[6]: 
                    e = newdoc.createElement("ele")
                    t = newdoc.createTextNode(str(int(round(f[6], 0))))
                    e.appendChild(t)
                    record.appendChild(e)
                e = newdoc.createElement("name")
                t = newdoc.createTextNode(str(f[1]))
                e.appendChild(t)
                record.appendChild(e)
                e = newdoc.createElement("time")
                t = newdoc.createTextNode(str(f[3]))
                e.appendChild(t)
                record.appendChild(e)
                top_element.appendChild(record)
                old_top_element.appendChild(record.cloneNode(True))
            else:
                print ("skipped", f)
                out.write(str(f[1]) + "\t" + str(f[3]) + "\t\n")
        out.close()
        print ("skipped file", os.path.getsize(fname))
        if os.path.getsize(fname) == 0:
            os.unlink(fname)
            print ("removed")
        fname = O_FILE[:-4] + ".gpx"
        out = open ( fname, "w")
        newdoc.writexml(out)
        out.close()
        out = open (C_FILE, "w")
        olddoc.writexml(out)
        out.close()
        
def write_html_acme():
    if files_combined:
        impl = xml.dom.minidom.getDOMImplementation()
        newdoc = impl.createDocument(None, "html", None)
        top_element = newdoc.documentElement
        head = newdoc.createElement("head")
        title = newdoc.createElement("title")
        text = newdoc.createTextNode("mapped")
        title.appendChild(text)
        head.appendChild(title)
        top_element.appendChild(head)
        body = newdoc.createElement("body")
        header = newdoc.createElement("h1")
        ###text = newdoc.createTextNode("Photos taken at " + YEAR + "-" + MONTH + "-" + DAY)
        ###header.appendChild(text)
        body.appendChild(header)
        header = newdoc.createElement("h2")
        text = newdoc.createTextNode("Mapped using web service: ACME Mapper 2.0")
        header.appendChild(text)
        body.appendChild(header)        
        for f in files_combined:
            if f[4] and f[5]:
                record = newdoc.createElement("a")
                record.setAttribute("ID", str(f[1]))
                href = "http://mapper.acme.com/?ll=%s,%s&z=14&t=M&marker0=%s%%2C%s%%2CN%s%%20W%s" % (
                    str(round(f[4], 5)), str(round(f[5], 5)),
                    str(round(f[4], 5)), str(round(f[5], 5)),
                    str(round(f[4], 5)), str(-round(f[5], 5))
                    )
                record.setAttribute("href", href)
                record.setAttribute("target", "_blank")
            
                text_ = str(f[2]) + " : " + str(f[3]) + " lat=" + str(round(f[4], 5)) + \
                    " lon="  + str(round(f[5], 5))  + " alt=" + str(int(round(f[6], 0)))   
                text = newdoc.createTextNode(text_)
                record.appendChild(text)
                body.appendChild(record)
            img = newdoc.createElement("img")
            img.setAttribute("src", str(f[2]))
            img.setAttribute("height", "50")
            body.appendChild(img)
            body.appendChild(newdoc.createElement("br"))
        top_element.appendChild(body)
        ## print "\n", newdoc.toprettyxml()
        out = open(O_FILE[:-4] + ".html", "w")
        newdoc.writexml(out, "", "\t", "\n")
        out.close
    else:
        print ("nothing to write")
    print ("done")

def combine():
    if files_normalized and dict_points:
        for f in files_normalized:
            if f[0] in dict_points.keys():
                files_combined.append( (f[0], f[1], f[2], f[3],
                                        dict_points[f[0]][0],
                                        dict_points[f[0]][1],
                                        dict_points[f[0]][2])
                                    )
            else:
                files_combined.append( (f[0], f[1], f[2], f[3],
                        None,
                        None,
                        None )
                    )
    else:
        print ("error: empty input")
    print ("combined", len(files_combined))

def set_shots_normalized():
    print ("set_shots_normalized")
    tDOM = xml.dom.minidom.parse(E_FILE)
    print (tDOM, E_FILE)
    pELES = tDOM.getElementsByTagName('file')
    print (len(pELES))
    for f in pELES:
        fid = f.getAttribute('ID')
        print (fid)
        fname = f.getAttribute('file_name')
        print (fname, f.getElementsByTagName('DateTime'))
        unparsed = f.getElementsByTagName('DateTime')[0].childNodes[0].nodeValue
        print ("unparsed", unparsed)
        format = "%Y:%m:%d %H:%M:%S"
        ##format = "%Y-%m-%dT%H:%M:%S"
        str_t = time.strptime(unparsed, format) 
        sec_t = int(time.mktime(str_t)) + SECONDS_OFFSET
        rnd_t = int(round(sec_t/STEP) * STEP) ## should enforce non integer division
        files_normalized.append( (rnd_t,
                                  str(fid),
                                  str(fname),
                                  str(unparsed) )
                                )
        files_normalized.sort()
    print ("normalized", len(files_normalized))
    f = open("files.txt", "w")
    for flist in files_normalized:
        f.write(str(flist) + "\n")
    f.close()
    print ("passed shots normalized")
 
def set_tracks_normalized():
    raw_points = []
    rnd_points = []
    segment = 0
    tDOM = xml.dom.minidom.parse(T_FILE)
    pSEGM = tDOM.getElementsByTagName('trkseg')
    for seg in pSEGM:
        segment += 1
        pELES = seg.getElementsByTagName('trkpt')
        for xPoint in pELES:
            unparsed = xPoint.getElementsByTagName('time')[0].childNodes[0].nodeValue
            format = "%Y-%m-%dT%H:%M:%SZ"
            str_t = time.strptime(unparsed, format) 
            sec_t = int(time.mktime(str_t))
            rnd_t = int(round(sec_t/STEP) * STEP)
            raw_points.append( (rnd_t,
                                float(xPoint.getAttribute('lat')),
                                float(xPoint.getAttribute('lon')), 
                                float(xPoint.getElementsByTagName('ele')[0].childNodes[0].nodeValue),
                                segment)
                             )       
    former = 0
    current = 0
    f = open("steps.txt", "w")
    for i in range(len(raw_points)):
        if current:
            former = raw_points[i-1][0]
        current = raw_points[i][0]
        if current - former == STEP or former == 0:
            pass
        else:
            print (current, former, STEP)
            _steps = range ((current - former)//round(STEP)) ## FIXED/HACKED
            ## python3 'float' object cannot be interpreted as an integer, try round instead of int() and //
            f.write(str(len(_steps)) + "\t" + str(raw_points[i]) + "\n")
            ## if len(_steps) < MAX_STEPS :
            if raw_points[i-1][4] == raw_points[i][4]:
                ### doesn't work :: or (raw_points[i][1]-raw_points[i-1][1]) < 0.00001
                ### XXXX' may only try segments
                for j in range (1, (current - former)//round(STEP)): ## was int(STEP)
                    rnd_points.append ((former + STEP * j,
                                        raw_points[i-1][1] + ((raw_points[i][1]-raw_points[i-1][1])/len(_steps)) * j,
                                        raw_points[i-1][2] + ((raw_points[i][2]-raw_points[i-1][2])/len(_steps)) * j,
                                        raw_points[i-1][3] + ((raw_points[i][3]-raw_points[i-1][3])/len(_steps)) * j
                                        ))
            else:
                print (len(_steps), \
                      round((raw_points[i][1]-raw_points[i-1][1]), 5), \
                      round((raw_points[i][2]-raw_points[i-1][2]), 5), \
                      round((raw_points[i][3]-raw_points[i-1][3]),5))
                print (raw_points[i-1])
                print (raw_points[i])
                print (raw_points[i-1][4], raw_points[i][4])
                pass        
        rnd_points.append(raw_points[i])
    f.close()
    for point in rnd_points:
        ## list may have duplicates because two raw data run in the same range
        ## removed in {} version
        dict_points[point[0]] = ( point[1], point[2], point[3] )
    print ("raw", len (raw_points))
    print ("rounded", len(rnd_points))
    print ("dictionary", len(dict_points))
    f = open("raw.txt", "w")
    for r in raw_points:
        f.write(str(r) + "\n")
    f.close()
    
    f = open("rounded.txt", "w")
    for r in rnd_points:
        f.write(str(r) + "\n")
    f.close()
    
    f = open("dict.txt", "w")
    keys = dict_points.keys()
    ## python3 AttributeError: 'dict_keys' object has no attribute 'sort' 
    keys = list(keys)
    keys.sort()
    for key in keys:
        f.write("%s\t%s\n" % (key, dict_points[key]))
    f.close()
    print ("passed tracks normalized")

##main()


    

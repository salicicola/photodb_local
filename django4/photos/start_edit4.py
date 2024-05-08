#!/usr/bin/python3
import os, sys, pickle, json, xml.dom.minidom, webbrowser, urllib.request, urllib.parse, urllib.error, time
import shutil
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
try:
    from . import Thumbnails
except:
    from photos import Thumbnails
from django.conf import settings
django_dir = str(settings.BASE_DIR)
print (django_dir)

def start(request, root):
        jpg_files = {}
        jpg_files_list = []
        gps = {}
        phids = []
        lcids = {}      ###
        towns = {}
        openspace = {}
        
        ##django_dir = os.getcwd()
        if not root == ".":
                os.chdir(root)
                print("change cwd to target:", root)
        files = os.listdir(".")
        gpx_files = []
        for f in files:
                if os.path.splitext(f)[1] == ".jpg":
                        ##print "found", f
                        jpg_files_list.append(f)
                        phid = f[:17]	
                        suffix = os.path.splitext(f)[0][17:]
                        if phid in jpg_files:
                                jpg_files[phid].append(suffix)
                        else:
                                jpg_files[phid] = [suffix,]
                else:
                        if os.path.splitext(f)[1] == ".gpx":
                                print(" ----- GPX found ", os.path.splitext(f)[0])
                                if os.path.splitext(f)[0].endswith("mapped"):
                                        os.path.splitext(f)[1]
                                        print("correct")
                                        gpx_files.append(f)
        print(len(list(jpg_files.keys())), "photos")
        print(len(jpg_files_list), "all jpg files")
        small_path = "%s/data/static/small" % django_dir
        print("will start making small versions", small_path, os.path.exists(small_path))
        Thumbnails.make_thumbnails_from_list(root, small_path, size=(600, 100000), files=jpg_files_list)
        print("small versions created")
        ##################################################################
        phids = list(jpg_files.keys())
        print(phids)
        _phids = []
        for phid in phids:
            fname = phid + ".jpg"
            print(fname, end=' ')
            t = os.path.getmtime(os.path.join(root, fname))
            print(t)
            _phids.append( (t, phid) )
        _phids.sort()
        print(len (_phids), _phids[0])
        phids = []
        for item in _phids:
            phids.append(item[1])
        print(len(phids), phids[0], "resorted")
        print("phids", phids)
        print("should be at least one GPX file, found", len(gpx_files))
        if len(gpx_files):
                processed = 0
                for gpx_file in gpx_files:
                        gpx_file = gpx_files[0]
                        print("will try to parse", gpx_file)
                        try:
                                doc = xml.dom.minidom.parse(gpx_file)
                                print(doc)
                                records = doc.documentElement.getElementsByTagName('wpt')
                                for record in records:
                                        name = record.getElementsByTagName("name")[0]
                                        name = name.firstChild.nodeValue
                                        if name in phids:
                                                lat = record.getAttribute("lat")
                                                lon = record.getAttribute("lon")
                                                lcid = record.getAttribute("LCID")
                                                town = record.getAttribute("town")
                                                ops = record.getAttribute("OPS")
                                                gpsID = str(lat) + str(lon)
                                                gps[name] = gpsID
                                                if lcid:
                                                        lcids[name] = lcid
                                                if town:
                                                        towns[name] = town
                                                if ops:
                                                        openspace[name] = ops
                                for k in list(gps.keys()):
                                        ##print k, gps[k]
                                        pass
                                print(len(list(gps.keys())), "JPG files with GPS")
                                processed += 1
                        except:
                                print(sys.exc_info())
                                print("cannot process GPX file")
                print(processed, "GPS files processed, total", len(list(gps.keys())), "JPG files with GPS info; ", len(list(lcids.keys())), "with LCID")
        else:
                print("no GPX files present")
        print("DEBUG")
        print(os.getcwd())
        writer = open("files_json.js", "w")
        print ("debug", writer)
        writer.write("phids = ")
        json.dump(phids, writer)
        writer.write(";\n")
        writer.write("jpg_files = ")
        json.dump(jpg_files, writer)
        writer.write(";\n")
        writer.write("gpsdata = ")
        json.dump(gps, writer)
        writer.write(";\n")
        ###
        writer.write("lcid_data = ")
        json.dump(lcids, writer)
        writer.write(";\n")
        ## updated2015-02-06
        writer.write("town_data = ")
        json.dump(towns, writer)
        writer.write(";\n")
        writer.write("ops_data = ")
        json.dump(openspace, writer)
        writer.write(";\n")
        print ("debug", writer)
        ## NEW or revived XXX ##
        try:
            ident = open("journal_expanded.txt").read()
            writer.write(ident)
            writer.write("\n")
            print("found and copied journal entries.ident")
        except:
            import sys
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
        ###
        writer.close()
        print ("debug", writer)
        print ("DEBUG", os.path.exists(os.path.join(django_dir, "files_json.js")))
        print("currently", os.getcwd()) ## at root
        if os.path.exists(os.path.join(django_dir, "files_json.js")):
                os.unlink(os.path.join(django_dir, "files_json.js"))
                print("Old files_json.js deleted @", django_dir)       
        try:
                ##os.rename("files_json.js", os.path.join(django_dir, "files_json.js"))
                print ("at", os.getcwd(), "django_dir", django_dir)
                shutil.copy2("files_json.js", os.path.join(django_dir, "files_json.js"))
                print (os.path.join(django_dir, "files_json.js"), "?copied")
                shutil.copy2("files_json.js", os.path.join("%s/data/static/scripts/photos/entry" % django_dir, "files_json.js"))
                os.unlink("files_json.js")
                print ("shutil passed without error")
        except:
                import sys
                print(sys.exc_info()[0])
                print(sys.exc_info()[1])
                print(sys.exc_info()[2])
                
                ret = shutil.copy2("files_json.js", os.path.join(django_dir, "files_json.js"))
                print("copy/delete", ret)
                print("WILL COPY FILE TO ANOTHER DJANGO")
                shutil.copy2("files_json.js", os.path.join(django_dir, "static/scripts/photos/entry", "files_json.js"))
                print("copy/delete", ret)
                os.unlink("files_json.js")
                print("?done")
        os.chdir(django_dir)
        print("pre-processing finished, returning to  base dir", os.getcwd(), "will try start entry")
        return start_entry(request, root, "") ## request undefined
                
def start_entry(request, path, area=None):
        print("start_edit4.start_entry() with", path)
        url_start = "http://localhost:8000/photodb/entry/legacy/?path=" + path + "&DIR=NEW" ## XXX
        url_start = "http://localhost:9090/photodb/entry/legacy/?path=" + path + "&DIR=NEW"
        url_start = "/photodb/entry/legacy/?path=" + path + "&DIR=NEW"
        if area:
             url_start = url_start + "&area=" + area
        print (url_start)
        ##webbrowser.open(url_start)
        return HttpResponseRedirect(url_start) 

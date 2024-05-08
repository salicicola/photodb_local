#!/usr/bin/python3
import os, sys, time
from PIL import Image

DEF_SIZE = (100000, 100)
print ("Thumbnails default size", DEF_SIZE)
print ("modified for django4 needed?")

def make_thumbnail(in_path, out_path, size=(100000, 100)):
    print ("will make thumbnail from", in_path, os.path.exists(in_path), os.path.getsize(in_path), "bytes")
    if os.path.exists(in_path):
        if os.path.exists(out_path):
            print ("skip existing", out_path)
        else:
            try:
                img = Image.open(in_path)
                print ("debug", img)
                img.thumbnail(size)
                print ("debug", img)
                if os.path.exists(out_path):
                    os.unlink(out_path)
                    print ("\tdeleted old version", out_path)
                img.save(out_path, "JPEG")
                print ("creating", out_path)
                if os.path.exists(out_path):
                    print (os.path.getsize(out_path), "bytes", time.asctime(time.localtime(os.path.getmtime(out_path))))
                else:
                    print ("unexpected error creating", out_path)
            except:
                print ("cannot create thumbnail for", in_path, size)
                for e in sys.exc_info():
                    print (e)
                raise Exception("fatal debug")

def make_thumbnails_from_list(in_root, out_root, size=(10000, 100), files=[]):
    if in_root == out_root:
        print ("Overwriting source files is not allowed")
        print (in_root, "is equal", out_root)
        print ("will exit")
        return
    print ("will need to process", len(files), "files")
    for item in files:
        infile = os.path.join(in_root, item)
        outfile = os.path.join(out_root, item)
        make_thumbnail(infile, outfile, size)

def test():
    make_thumbnails_from_list("G:\\xxx", "G:\\xxx\\out", DEF_SIZE, ("20111114olymp3657.jpg", "20111114olymp3657.jpg", "20111114olymp3656.jpg"))
    
    
##test()

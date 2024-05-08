import os, sys, time
from PIL import Image

DEF_SIZE = (100000, 100)
print ("Thumbnails default size", DEF_SIZE)

def make_thumbnail(in_path, out_path, size=(100000, 100)):
    if os.path.exists(in_path):
        if os.path.exists(out_path):
            print ("skip existing", out_path)
            return False
        else:
            print ("trying..")
            try:
                img = Image.open(in_path)
                img.thumbnail(size)
                if os.path.exists(out_path):
                    os.unlink(out_path)
                    print ("\tdeleted old version", out_path)
                else:
                    print ("saving", img)
                img.save(out_path, "JPEG")
                print ("creating", out_path)
                if os.path.exists(out_path):
                    print (os.path.getsize(out_path), "bytes", time.asctime(time.localtime(os.path.getmtime(out_path))))
                    return True
                else:
                    print("unexpected error creating", out_path)
                    return False
            except:
                print ("cannot create thumbnail for", in_path, size)
                for e in sys.exc_info():
                    print (e)
                return False
    else:
        print (in_path, "do not exists")
        return False

def make_thumbnails_from_list(in_root, out_root, size=(100000, 100), files=[]):
    if in_root == out_root:
        ##print "Overwriting source files is not allowed"
        ##print in_root, "is equal", out_root
        ##print "will exit"
        return
    print ("will need to process", len(files), "files")
    for item in files:
        infile = os.path.join(in_root, item)
        outfile = os.path.join(out_root, item)
        make_thumbnail(infile, outfile, size)

def test():
    make_thumbnails_from_list("G:\\xxx", "G:\\xxx\\out", DEF_SIZE, ("20111114olymp3657.jpg", "20111114olymp3657.jpg", "20111114olymp3656.jpg"))
    
    
##test()

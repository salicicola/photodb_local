import os, datetime

PACKAGE = os.path.dirname(__file__).split('/')[-1]
if os.path.exists("Dockerfile"):
    DOCKERIZED = True
else:
    DOCKERIZED = False
if os.path.exists('data/data_db.sqlite3'):
    DB_MODIFIED = os.path.getmtime('data/data_db.sqlite3')
else:
    DB_MODIFIED = os.path.getmtime('db.sqlite3')
DB_MODIFIED = datetime.datetime.fromtimestamp(DB_MODIFIED)
if os.path.exists("photodb/urls.py"):
    PHOTODB_AVAILABLE = True
else:
    PHOTODB_AVAILABLE = False
if os.path.exists("data/static/thm/photos/"):
    PHOTOS_AVAILABLE = True
else:
    PHOTOS_AVAILABLE = False
print ("loading  [%s]" % PACKAGE)
print ("DOCKERIZED/DB_MODIFIED/PHOTODB_AVAILABLE/PHOTOS_AVAILABLE", DOCKERIZED, DB_MODIFIED, PHOTODB_AVAILABLE, PHOTOS_AVAILABLE)
debug_mode=False
print ("names:: debug mode", debug_mode)


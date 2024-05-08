import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
try:
    from names.models import Name, SpeciesMeta
except:
    print ("cannot import Name and SpeciesMeta from names, should have them in .models")
from .models import *
from .__init__ import VERSION
PYTHON_VERSION = sys.version.split()[0]
DJANGO_VERSION = django.get_version()
from .views_lib import PYTHON_VERSION, DJANGO_VERSION, REVISION ## get_area, get_editdomain, DOMAIN, , get_image_table

def three_level(request, template, upper=11648):
    if request.user.username == 'salicarium' or request.user.username == 'gmp' or request.user.username == 'IK':
        public = False
    else:
        public = True
    print ("running three_level() with", upper)
    xxx_names=[]
    version = VERSION
    python_version = PYTHON_VERSION
    django_version = DJANGO_VERSION
    revision = REVISION
    total_photos = 0
    total_species = 0
    root = Name.objects.get(pk=upper)
    data = {"upper": root, "fams":[]}
    print ("ini", data)
    fams = Name.objects.filter(parent=root).order_by('latname') ## parent/upper filter(level='family') birds'level is family !!!
    print ("fams", fams)
    for fam in fams:
        print ("fam", fam, fam.level, fam.rank)
        family = {"family":fam, "genera":[], "photos":0}
        for gen in Name.objects.filter(parent=fam).order_by('latname'): ## XXX parent > only one fam
            print ("...", gen)
            genus = {"genus":gen, "species":[], "photos":0}
            for sp in Name.objects.filter(parent=gen).order_by('latname'):
                if public:
                    images = AnimalImage.objects.filter(plant=sp).filter(nr__gt=0).filter(nr__lt=100).order_by('nr')
                else:
                    images = AnimalImage.objects.filter(plant=sp).order_by('nr')
                if images:
                    total_species +=1
                    total_photos += len(images)
                    genus["photos"] += len(images)
                    family["photos"] += len(images)
                    try:
                        meta = SpeciesMeta.objects.get(spid=sp.pnid)
                    except:
                        meta = {}
                    genus["species"].append({"species":sp, "images":images, "meta":meta})
                    xxx_names.append("%s %s" % (gen.latname, sp.latname))
                print ("... ...", sp, images)
            if genus["photos"]:
                family["genera"].append(genus)
        if family["photos"]:
            data["fams"].append(family)
    xxx_names.sort()
    print (len(xxx_names))
    print (xxx_names)
    return render (request, template, locals())

   

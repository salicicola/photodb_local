import os, datetime, pickle, sys
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
try:
    from survey.models import GenericRecord
except:
    print ("available in here?")
from .models import *
try:
    from names.models import Name, SpeciesMeta
    from common.models import Town, Location
except:
    print ("should be in .models")
from .views_lib import get_area, get_editdomain, PYTHON_VERSION, DJANGO_VERSION, DOMAIN, REVISION, get_image_table
from .__init__ import VERSION
from django.db.models import Q


def latnames(request, template="photodb/latnames_adm.htm", cache=False):
    cached = os.path.join("photodb", "CACHE", "latnames_admin.html")
    if not cache:
        if os.path.exists(cached):
            html = open(cached).read()
            return HttpResponse(html)
    names = Name.objects.filter(rank='species').filter(category='vascular').exclude(upper__isnull=True).order_by('upper__latname').order_by('latname')
    ## soring did not work
    spp = {}
    for name in names:
        longname = (name.upper.latname, name.latname, name.pk)
        meta = SpeciesMeta.objects.filter(spid=name.pk)
        if meta:
            meta = meta[0]
        else:
            meta = {}
        spp[longname] = (name, meta)
    species = spp.items()
    species = list(species)
    species.sort()
    for sp in species:
        print (sp)
    print (len(names), "species names")
    return render(request, template, locals())

##    images = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
##    print ("running latnames/colnames mode latnames=%s, %s relevant images; do cache=%s" % (latnames, len(images), cache))
##    records = {}
##    for image in images:
##        plant = image.plant
##        latname = plant.latname
##        genname = plant.upper.latname
##        name = "%s %s" % (genname, latname)
##        colnames = plant.colnames
##        authors = plant.authors
##        fid = plant.upper.upper.pk
##        if latnames:
##            key = (name, colnames, authors, fid, plant.pk)
##        else:
##            key = (colnames, name, authors, fid, plant.pk)
##        if not key in records:
##            records[key] = 1
##            ##print (key)
##        else:
##            records[key] += 1 
##    items = records.items()
##    items = list(items)
##    items.sort()
##    print (len(items))
##    print (items[0])
##    generated = timezone.now()
##    if cache:
##        from django.template.loader import get_template
##        t = get_template(template)
##        html = t.render(locals())
##        out = open(cached, "w")
##        out.write(html)
##        out.close()
##        print ("cached", out)
##        return HttpResponse(html)
##    else:
##        return render(request, template, locals())


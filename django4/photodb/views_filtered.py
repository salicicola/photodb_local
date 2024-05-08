import os, datetime, pickle, sys
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
try:
    from survey.models import GenericRecord
except:
    print ("available in .models?")
from .models import *
try:
    from names.models import Name, SpeciesMeta
    from common.models import Town, Location
except:
    print ("should be in .models")
from .views_lib import get_area, get_editdomain, PYTHON_VERSION, DJANGO_VERSION, DOMAIN, REVISION, get_image_table
from .__init__ import VERSION

from django.db.models import Q
TCOUNTIES = [
("BE", "Berkshire"),
("FR", "Franklin"),
("HS", "Hampshire"),
("HD", "Hampden"),
("WO", "Worcester"),
('MI', "Middlesex"),
("ES", "Essex"),
("SU", "Suffolk"),
("NO", "Norfolk"),
("BR", "Bristol"),
("PL", "Plymouth"),
("BA", "Barnstable"),
("DU", "Dukes"),
("NA", "Nantucket")
    ]

def thumview_species_filtered(request, pnid, template, county=None):
    print ("running views_filtered.thumview_species_filtered", pnid, template, county)
    max_thums = 10000000
    county_name=""
    if not county:
        return HttpResponseBadRequest("no county supplied")
    else:
        for c in TCOUNTIES:
            if c[0] == county:
                county_name = c[1]
    if not county_name:
        print ("error with pnid", pnid, "county", county)
        return HttpResponseBadRequest("no valid county supplied") 
    if request.user.is_authenticated:
        print (request.user.username)
        ##request.user.username == 'salicarium' or request.user.username == 'gmp':
        authorized = True
    else:
        authorized = False
        return HttpResponseBadRequest("not authorized")
    debug_starts = datetime.datetime.now()
    edit_domain = get_editdomain()
    total_species, total_photos = 0, 0
    gnum = 0
    tree = []
    version = VERSION
    python_version = PYTHON_VERSION
    django_version = DJANGO_VERSION
    domain = DOMAIN
    revision = REVISION.split()[0]
    root_name = Name.objects.get(pnid=pnid)
    rank = root_name.level ## rank
    print ("view_photo_records() got", root_name, rank)
    if not rank == 'species':
        return HttpResponseBadRequest("filtered query designed only for taxa at species level, this one is %s" % rank)
    species = root_name
    print ("doing species", species.category)
    genus = root_name.upper
    family = genus.upper
    group = family.upper
    grp = ["", "", "", group.pnid, [], 0]
    tree.append(grp)
    fam = ["", "", "", family.pnid, [], 0]
    grp[4].append(fam)
    gen = [genus.latname.replace('_', ' '), genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
    fam[4].append(gen)
    table = get_image_table(species)
    print ("using", table, "gen", genus)
    photos = table.objects.filter(nr__gt=0).filter(plant__pnid = species.pnid).filter(locality__pk__startswith="MA.").filter(locality__county=county_name).order_by('nr')
    try:
        meta = SpeciesMeta.objects.get(pk=species.pnid)
    except:
        meta = "?" + str(sys.exc_info()) ### XXX
    print ("got %s photos" % len(photos))
    syns = Name.objects.filter(parent=species).order_by('latname') 
    spec = [species.latname, species.colnames, species.authors, species.pnid,
       syns, len(photos), photos, meta, [], species.caption, species.rank, species] ## removed=[]
    gen[4].append(spec)
    gen[5] += len(photos)
    fam[5] += len(photos)
    grp[5] += len(photos)
    total_species += 1
    total_photos += len(photos)
    print (tree)
    return render(request, template, locals())

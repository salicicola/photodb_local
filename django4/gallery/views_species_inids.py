import os, datetime, pickle, sys
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from .views_nonlegacy2 import TCOUNTIES
from names.models import *
from .views_lib import get_area, get_editdomain, PYTHON_VERSION, DJANGO_VERSION, DOMAIN, REVISION, get_image_table
from photodb.__init__ import VERSION

from photodb.models import *
def check_inid(pnid, inid, category='vascular'):
    if not inid:
        raise Exception("must set inid first")
    if not category == 'vascular':
        raise Exception("implemented for VacularImage only")
    recs = VascularImage.objects.filter(inid=inid)
    for rec in recs:        
        if not rec.plant.pnid==pnid:
            print (rec.plant.longname, rec.plant.pnid, rec.inid, "Error") 
            raise Exception("wrong plant ID? should be %s for indID %s" % (pnid, inid))
        else:
            print (rec.plant.longname, rec.plant.pnid, rec.inid, "OK")    
    return True

def bulk_reidentify(oldpnid, inid, newpnid, category='vascular'):
    if not inid:
        raise Exception("must set inid first")
    if not category == 'vascular':
        raise Exception("implemented for VacularImage only")
    check = check_inid(oldpnid, inid, category='vascular')
    if not check:
        raise Exception("fix inids first and run again")
    newsp = Name.objects.filter(category=category).filter(level='species').get(pnid=newpnid)
    print ("will set to", newsp)
    recs = VascularImage.objects.filter(inid=inid) ## FIXME again
    for rec in recs:
        print ("old", rec, rec.inid, rec.plant)
        rec.plant=newsp
        print (" will set to", rec.plant)
        rec.save()
        print ("saved", rec.modified)

        


def view_photo_records_species(request, pnid=None, template="photodb/photos/gallery_thums_byinid.htm"):
    ##tcounties = TCOUNTIES
    ##max_thums = 1000
    total_photos = 0
    tree = []
    doc = "LC/static/spp/%s.html" % pnid
    if not os.path.exists(doc):        
        ######################################raise IOError(doc)
        doc = None
    ## authorized
    version = VERSION
    python_version = PYTHON_VERSION
    django_version = DJANGO_VERSION
    domain = DOMAIN
    revision = REVISION.split()[0]
    if pnid:
        root_name = Name.objects.get(pnid=pnid)
        rank = root_name.level ## rank
        if rank == 'species':
            species = root_name
            print ("doing species", species.category)
            genus = root_name.upper
            family = genus.upper
            group = family.upper
            grp = ["", "", "", group.pnid, [], 0]
            tree.append(grp)
            fam = [family.latname.replace('_', ' '), family.colnames, family.authors,  family.pnid, [], 0]
            grp[4].append(fam)
            gen = [genus.latname.replace('_', ' '), genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
            fam[4].append(gen)
            table = get_image_table(species) ## may work for animals etc
            print ("using", table, "gen", genus)
            photos = table.objects.filter(nr__gt=0).filter(plant__pnid = species.pnid).order_by("inid", "nr")
            try:
                meta = SpeciesMeta.objects.get(pk=species.pnid)
            except:
                meta = "?" + str(sys.exc_info()) ### XXX
            print ("got %s photos" % len(photos))
            syns = Name.objects.filter(upper=species).filter(level='synonym').order_by('latname') ##.order_by("latname") BUG FIXING 2023-0120
            spec = [species.latname, species.colnames, species.authors, species.pnid,
                   syns, len(photos), photos, meta, [], species.caption, species.rank, species.parent] ## XXXX added two ## removed removed
            gen[4].append(spec)
            gen[5] += len(photos)
            fam[5] += len(photos)
            grp[5] += len(photos)
            total_photos += len(photos)
            ##print (tree)
            print (photos) ## in template use just photos
    else:
        raise Exception("xxx")
    ## FIXME
    
    
    return render(request, template, locals())


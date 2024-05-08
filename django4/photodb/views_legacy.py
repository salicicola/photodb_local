from django.shortcuts import render
import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
try:
    from names.models import Name, LegacyName, SpeciesMeta
except:
    print ("should be available in models")
from .models import *
from django.views.decorators.cache import cache_page
from .__init__ import VERSION

DEBUG = True

IMAGES = {}
for indexed in NameIndex.objects.all():
    spid = indexed.spid
    images = indexed.images
    IMAGES[spid] = images
print ("checked cached index of images", len(IMAGES), "species with images")

def newflat_checklist(request, template=""):    
    tree = []
    for ugid in [301319, 301314, 301309, 301308, 301307, 301299, 299123]:
        higher = Name.objects.get(pk=ugid)
        print (higher.latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            family = {"fam": fam, "genera": []}
            group["fams"].append(family)     
            for gen in Name.objects.filter(upper=fam).order_by('latname'):
                genus = {"genus": gen, "species":[]}
                family["genera"].append(genus)
                if gen.sal_latname == "Coronopus":
                    print ("debug", gen)
                for sp in Name.objects.filter(upper=gen).order_by('latname'):
                    colnames = sp.colnames
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    images = IMAGES.get(sp.pnid, 0)
                    species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images}
                    genus["species"].append(species)
                    for syn in Name.objects.filter(upper=sp).order_by('sal_latname'):
                        synonym = {"syn": syn}
                        species["synonyms"].append(synonym)
    return render (request, "photodb/checklist_flat.htm", locals())        


def legacy_checklist_family(request, fid, template="photodb/checklist_legacy.htm"):
    start = datetime.datetime.now()
    fam = LegacyName.objects.get(pk=int(fid))
    print (fam)
    family = {"fam": fam, "genera": []}
    ##group["fams"].append(family)     
    for gen in LegacyName.objects.filter(legacy_parent=fam).order_by('sal_latname'):
        genus = {"genus": gen, "species":[]}
        family["genera"].append(genus)
        if gen.sal_latname == "Coronopus":
            print ("debug", gen)
        for sp in LegacyName.objects.filter(legacy_parent=gen).order_by('sal_latname'):
            if gen.sal_latname == "Coronopus":
                print ("debug species", sp)
            try:
                colnames = Name.objects.get(pk=sp.pk).colnames
            except:
                colnames = "XXX"
            try:
                meta = PlantMeta.objects.get(pk=sp.pk)
            except:
                meta = {}
            images = IMAGES.get(sp.pnid, 0)
            species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images}
            genus["species"].append(species)
            for syn in LegacyName.objects.filter(legacy_parent=sp).order_by('sal_latname'):
                if gen.sal_latname == "Coronopus":
                    print ("debug synonym", sp)
                synonym = {"syn": syn}
                species["synonyms"].append(synonym)
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds(), 3)
    print (delta.total_seconds(), "seconds")
    return render (request, template, locals())

def legacy_checklist_families(request, template=""):
    start = datetime.datetime.now()
    tree = []
    for ugid in [5410, 5403, 5402, 5401, 11974]:
        higher = LegacyName.objects.get(pk=ugid)
        print (higher.sal_latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in LegacyName.objects.filter(legacy_parent=higher).order_by('sal_latname'):
            print (fam)
            family = {"fam": fam, "genera": []}
            group["fams"].append(family)     
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds())
    print (delta.total_seconds(), "seconds")
    return render (request, "photodb/checklist_legacy_fast.htm", locals())        

##@cache_page(60 * 1) ## e.g., 60 * 1 == 1 minute]
def legacy_checklist(request, template=""):
    start = datetime.datetime.now()
    tree = []
    for ugid in [5410, 5403, 5402, 5401, 11974]:
        higher = LegacyName.objects.get(pk=ugid)
        print (higher.sal_latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in LegacyName.objects.filter(legacy_parent=higher).order_by('sal_latname'):
            print (fam)
            family = {"fam": fam, "genera": []}
            group["fams"].append(family)     
            for gen in LegacyName.objects.filter(legacy_parent=fam).order_by('sal_latname'):
                genus = {"genus": gen, "species":[]}
                family["genera"].append(genus)
                if gen.sal_latname == "Coronopus":
                    print ("debug", gen)
                for sp in LegacyName.objects.filter(legacy_parent=gen).order_by('sal_latname'):
                    if gen.sal_latname == "Coronopus":
                        print ("debug species", sp)
                    try:
                        colnames = Name.objects.get(pk=sp.pk).colnames
                    except:
                        colnames = "XXX"
                    try:
                        meta = PlantMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    images = IMAGES.get(sp.pnid, 0)
                    species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images}
                    genus["species"].append(species)
                    for syn in LegacyName.objects.filter(legacy_parent=sp).order_by('sal_latname'):
                        if gen.sal_latname == "Coronopus":
                            print ("debug synonym", sp)
                        synonym = {"syn": syn}
                        species["synonyms"].append(synonym)
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds())
    print (delta.total_seconds(), "seconds")
    return render (request, "photodb/checklist_legacy.htm", locals())        



def animals_index(request, template="photodb/animals_index.htm"):
    insects = {"orders":[],}
    insecta = Name.objects.get(pk=12104)
    orders = Name.objects.filter(legacy_parent=insecta).order_by('latname')
    for order in orders:
        r = {"pnid": order.pk, "name": order.latname}
        insects["orders"].append(r)
    
    
    return render(request, template, locals())


def make_legacy_families(request):
    fams = Name.objects.filter(rank='family').filter(category='vascular').exclude(legacy_parent__isnull=True).order_by('sal_latname')
    html = """<html><head></head>
        <body><h2>Vascular Plants: Alphabetic List of Families Using Legacy Classification</h2>
    """
    for fam in fams:
        latname = fam.sal_latname
        if not latname:
            latname = fam.latname
        html += '<div><a href="/photodb/family/legacy/%s">%s</a></div>' % (fam.pnid, latname)
    html += "</body></html>"
    return HttpResponse(html)

vascular_groups = [{"name": "Pteridophyta (Ferns and Allies)", "pnid": 5410, "fams":[]},
              {"name": "Gymnospermae (Conifers)", "pnid": 5403, "fams":[]},
              {"name": "Monocotyledonae (Monocots)", "pnid": 5402, "fams":[]},
              {"name": "Dicotyledonae (Dicots)", "pnid": 5401, "fams":[]},
              {"name": "UNNAMED_PLANTS (UNNAMED_PLANTS)", "pnid": 11974, "fams":[]}]

nonvascular_groups = [ {"name": "Ochrophyta", "pnid": 16479, "fams":[]},
        {"name": "Rhodophyta", "pnid": 16478, "fams":[]},
        {"name": "Chlorophyta", "pnid": 16477, "fams":[]},
        {"name": "Lichenophyta", "pnid": 16476, "fams":[]},
        {"name": "Marchantiophyta", "pnid": 16002 , "fams":[]},
        {"name": "Bryophyta", "pnid":11876 , "fams":[]},
        {"name": "Fungi", "pnid": 11998, "fams":[]},
    ]
animals_groups = [##{"name": "ARTHROPODS", "pnid": 12224, "fams":[]},
                 {"name": "INSECTS", "pnid": 12104, "fams":[]},
                 {"name": "ANIMALS (except of insects)", "pnid": 12100, "fams":[]},
    ]
varia_groups = [
                 ##{"name": "HUMANS", "pnid": 14844, "fams":[]}, ## moved to PHOTOS_VARIA, no changes in taxa absolutely necessary, since fid the same
                 {"name": "PHOTOS_VARIA", "pnid": 12108, "fams":[]},
    ]

## details=True, errors=""): ## WERE not in use
## No matching records in DB found when http://localhost:9090/photodb/gallery/view/16446/
## 2021-10-04 :: changed in spe sal_*
def index_legacy_simplified(request, category='vascular', template="photodb/index_vascular_simplified.htm"):
    print ("simplified from views_legacy.index_vascular for category", category)
    print ("will use Name, without cache")
    start = datetime.datetime.now()
    groups = []
    print (category, "using groups", str(groups), len(groups))
    if category == 'vascular':
        groups = vascular_groups
    elif category == 'nonvascular':
        groups = nonvascular_groups
    elif category == 'animals':
        groups = animals_groups
    elif category == 'varia':
        groups = varia_groups
    else:
        return HttpResponseBadRequest("illegal parameter %" % category)
    for x in groups:
        x["fams"] = []  ## fixed strange bug
    print (category, "using groups", len(groups), str(groups))
    for gr in groups:
        g = Name.objects.get(pnid=gr["pnid"])
        fams = Name.objects.filter(legacy_parent = g).order_by('sal_latname')
        ##print (" ", len(fams), "fams")
        for fam in fams:
            fid = fam.pnid
            ##images=VascularImage.objects.filter(fid=fid).filter(nr__gte=0)
            family = {"latname": fam.sal_latname, "fid": fid, "total_photos": 0, "total_species": 0, "species_pub": 0, "genera":[]}
            genera = Name.objects.filter(legacy_parent = fam).order_by('sal_latname')
            for gen in genera:
                gid = gen.pnid
                genus = {"latname": gen.sal_latname, "fid": fid, "gid": gid, "total_photos": 0, "total_species": 0, "species_pub": 0, "species":[]}
                family["genera"].append(genus)
                species = Name.objects.filter(legacy_parent = gen).order_by('sal_latname')
                for spec in species:
                    spid = spec.pnid
                    family["total_species"] += 1
                    ##photos = images.filter(spid=spid)
                    genus["total_photos"] += 0 ##
                    ##published_photos = photos.filter(nr__lte=100).count()
                    published_photos = 0
                    if published_photos:
                        family["species_pub"] +=1
                    if spec.sal_latname:
                        spe = {"latname": spec.sal_latname, "fid": fid, "gid": gid, "pnid": spid,
                               "total_photos": 0, "published": published_photos,
                               "colnames": spec.colnames, "authors": spec.sal_authors,
                               "CCSS": spec.ccss, "NID": spec.pnid,
                               "SPID": spec.pnid, "modified": spec.modified.isoformat()[:19]} ## for compatibility with tomcat version
                    else:
                        ## XXX
                        spe = {"latname": spec.latname + " [XXX]", "fid": fid, "gid": gid, "pnid": spid,
                               "total_photos": 0, "published": published_photos,
                               "colnames": spec.colnames, "authors": spec.sal_authors,
                               "CCSS": spec.ccss, "NID": spec.pnid,
                               "SPID": spec.pnid, "modified": spec.modified.isoformat()[:19]} ## for compatibility with tomcat version
                        
                    genus["species"].append(spe)
            gr["fams"].append(family)
    ends = datetime.datetime.now()
    delta = ends - start
    print (delta) ## 0:01:30 0:01:28 0:01:28 0:01:27
    return render(request, template, locals())

## URL compare/
def species_latnames(request):
    sp_names = Name.objects.filter(legacy=True).filter(rank='species')
    print ("%s legacy species names by legacy" % len(sp_names))
    sp_names = Name.objects.exclude(fid=None).filter(rank='species')
    print ("%s legacy species names by fid present" % len(sp_names))
    ## same 2522 names
    records = []
    for sp in sp_names:
        longname = "%s %s" % (sp.legacy_parent.sal_latname, sp.sal_latname)
        if sp.parent:
            altname = "%s %s" % (sp.upper.latname, sp.latname)
        else:
            altname = "???"
        images = VascularImage.objects.filter(spid=sp.pnid).filter(nr__lt=100).count() ## > 0 FIXME
        rec = (longname, altname, sp, images)
        records.append(rec)
    records = sorted(records, key=lambda record: record[0])
    for rec in records:
        print (rec[0], '=', rec[1], ":", rec[3])
    return render (request, "photodb/names_compare.htm", locals())

## clear all caches and re-generate legacy page
def clear_index_cache(request, details=True):
    print ("will clear cache before running index_vascular")
    files = []
    try:
        for f in os.listdir("CACHE"):
            files.append(f)
        for f in files:
            path = os.path.join("CACHE", f)
            os.unlink(path)
            print ("removed", path)
        ##return index_vascular(request, details) ## 
        return HttpResponseRedirect('/photodb/gallery/vascular/')
    except:
        print ("error, cannot clear the cache")
        return index_vascular(request, details, errors="cannot clear the cache")

## FIXME, too slow yet
@cache_page(None) ## one month, ## e.g., 60 * 1 == 1 minute] max 30 days in memcache: 60 * 60 * 24 * 30
def index_vascular(request, details=True, errors=""):
    ## FIXME hardcoded in template "/photodb/gallery/cache/clear/" to clear the cache
    print ("running index_vascular")
    start = datetime.datetime.now()
    groups = [{"name": "Pteridophyta (Ferns and Allies)", "pnid": 5410, "fams":[]},
              {"name": "Gymnospermae (Conifers)", "pnid": 5403, "fams":[]},
              {"name": "Monocotyledonae (Monocots)", "pnid": 5402, "fams":[]},
              {"name": "Dicotyledonae (Dicots)", "pnid": 5401, "fams":[]},
              {"name": "UNNAMED_PLANTS (UNNAMED_PLANTS)", "pnid": 11974, "fams":[]}]
    for gr in groups:
        g = Name.objects.get(pnid=gr["pnid"])
        print (g.pnid, g.latname, g.sal_latname, g.colnames)
        fams = Name.objects.filter(legacy_parent = g).order_by('sal_latname')
        print (" ", len(fams), "fams")
        for fam in fams:
            fid = fam.pnid
            images=VascularImage.objects.filter(fid=fid).filter(nr__gte=0)
            family = {"latname": fam.sal_latname, "fid": fid, "total_photos": len(images), "total_species": 0, "species_pub": 0, "genera":[]}
            genera = Name.objects.filter(legacy_parent = fam).order_by('sal_latname')
            for gen in genera:
                gid = gen.pnid
                genus = {"latname": gen.sal_latname, "fid": fid, "gid": gid, "total_photos": 0, "total_species": 0, "species_pub": 0, "species":[]}
                family["genera"].append(genus)
                species = Name.objects.filter(legacy_parent = gen).order_by('sal_latname')
                for spec in species:
                    spid = spec.pnid
                    family["total_species"] += 1
                    photos = images.filter(spid=spid)
                    genus["total_photos"] += len(photos)
                    published_photos = photos.filter(nr__lte=100).count()
                    if published_photos:
                        family["species_pub"] +=1
                    spe = {"latname": spec.latname, "fid": fid, "gid": gid, "pnid": spid,
                               "total_photos": len(photos), "published": published_photos,
                               "colnames": spec.colnames, "authors": spec.authors,
                               "CCSS": spec.ccss, "NID": spec.pnid,
                               "SPID": spec.pnid, "modified": spec.modified.isoformat()[:19]} ## for compatibility with tomcat version
                    ##print (spe)
                    genus["species"].append(spe)
            gr["fams"].append(family)
    ends = datetime.datetime.now()
    delta = ends - start
    print (delta) ## 0:01:30 0:01:28 0:01:28 0:01:27
    print ("will use", "photodb/index_vascular.htm")
    out = open("photodb/index_generated.timestamp", "w")
    out.close()
    generated = datetime.datetime.now()
    print ("generated at %s" % os.path.getmtime("photodb/index_generated.timestamp"))
    return render(request, "photodb/index_vascular.htm", locals())


""" old style very slow
running index_vascular
5410 Pteridophyta Pteridophyta Ferns and Allies
  16 fams
5403 Gymnospermae Gymnospermae Conifers
  4 fams
5402 Monocotyledonae Monocotyledonae Monocots
  25 fams
5401 Dicotyledonae Dicotyledonae Dicots
  123 fams
11974 UNNAMED_PLANTS UNNAMED_PLANTS UNNAMED_PLANTS
  1 fams
0:01:59.091394
"""
def index_families(request, category='vascular'):
    print ("rewritten from simplified from views_legacy.index_vascular for category", category)
    print ("will use Name, without cache")
    start = datetime.datetime.now()
    groups = []
    legacy_fams = []
    print (category, "using groups", str(groups), len(groups))
    if category == 'vascular':
        groups = vascular_groups
    elif category == 'nonvascular':
        groups = nonvascular_groups
    elif category == 'animals':
        groups = animals_groups
    elif category == 'varia':
        groups = varia_groups
    else:
        return HttpResponseBadRequest("illegal parameter %" % category)
    for x in groups:
        x["fams"] = []  ## fixed strange bug
    print (category, "using groups", len(groups), str(groups))
    for gr in groups:
        g = Name.objects.get(pnid=gr["pnid"])
        fams = Name.objects.filter(legacy_parent = g).order_by('latname')
        ##print (" ", len(fams), "fams")
        for fam in fams:
            legacy_fams.append(fam)
            fid = fam.pnid
            ##images=VascularImage.objects.filter(fid=fid).filter(nr__gte=0)
            family = {"latname": fam.sal_latname, "fid": fid, "total_photos": 0, "total_species": 0, "species_pub": 0, "genera":[]}
            genera = Name.objects.filter(legacy_parent = fam).order_by('latname')
            for gen in genera:
                gid = gen.pnid
                genus = {"latname": gen.sal_latname, "fid": fid, "gid": gid, "total_photos": 0, "total_species": 0, "species_pub": 0, "species":[]}
                family["genera"].append(genus)
                species = Name.objects.filter(legacy_parent = gen).order_by('latname')
                for spec in species:
                    spid = spec.pnid
                    family["total_species"] += 1
                    ##photos = images.filter(spid=spid)
                    genus["total_photos"] += 0 ##
                    ##published_photos = photos.filter(nr__lte=100).count()
                    published_photos = 0
                    if published_photos:
                        family["species_pub"] +=1
                    spe = {"latname": spec.latname, "fid": fid, "gid": gid, "pnid": spid,
                               "total_photos": 0, "published": published_photos,
                               "colnames": spec.colnames, "authors": spec.authors,
                               "CCSS": spec.ccss, "NID": spec.pnid,
                               "SPID": spec.pnid, "modified": spec.modified.isoformat()[:19]} ## for compatibility with tomcat version
                    genus["species"].append(spe)
            gr["fams"].append(family)
    ends = datetime.datetime.now()
    delta = ends - start
    print (delta) ## 0:01:30 0:01:28 0:01:28 0:01:27
    for fam in Name.objects.filter(category=category).filter(rank='family'):
        if fam in legacy_fams:
            ##print ("in legacy", fam)
            if not fam.upper or not fam.parent:
                print ("only legacy", fam)
        else:
            ##print ("only new", fam)
            pass
            
    return render(request, "photodb/index_vascular_simplified.htm", locals())

def get_fams_meta():
    fams = Name.objects.filter(rank='family')
    data = []
    for fam in fams:
        upper = fam.upper
        if upper:
            upper = upper.latname
        legacy = fam.legacy_parent
        if legacy:
            legacy = fam.legacy_parent.latname
            if not legacy:
                legacy = fam.legacy_parent.sal_latname
        rec = {"fid":fam.pk, "ccss": fam.ccss, "category":fam.category, "latname":fam.latname,
               "sal_latname":fam.latname, "colnames": fam.colnames, "colnames": fam.colnames,
               "upper": upper, "legacy":legacy}
        data.append(rec)
        for f in data:
            print (f)
        import pickle
        out = open("photodb/famiilies_meta.pickle", "wb")
        pickle.dump(data, out)
        out.close()
        print (out)

 
def latnames(request, template="photodb/latnames.htm", latnames=True):
    images = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
    print (len(images))
    records = {}
    for image in images:
        plant = image.plant
        latname = plant.sal_latname
        genname = plant.legacy_parent.sal_latname
        name = "%s %s" % (genname, latname)
        colnames = plant.colnames
        authors = plant.authors
        fid = plant.legacy_parent.legacy_parent.pk
        if latnames:
            key = (name, colnames, authors, fid, plant.pk)
        else:
            key = (colnames, name, authors, fid, plant.pk)
        if not key in records:
            records[key] = 1
            print (key)
        else:
            records[key] += 1 
            ##
    items = records.items()
    items = list(items)
    items.sort()
    print (len(items))
    print (items[0])
    return render(request, template, locals())
       
def legacy_gallery (request, template):    
    tree = []
    total_species = 0 
    total_images = 0 
    for ugid in [5410, 5403, 5402, 5401]:
        higher = Name.objects.get(pk=ugid)
        print (higher.latname)
        group = {"higher": higher, "fams": [], "images":0, "taxa": 0} 
        tree.append( group )
        for fam in Name.objects.filter(legacy_parent=higher).order_by('latname'):
            print (fam)
            family = {"fam": fam, "genera": [], "images":0, "taxa": 0}## NEW
            group["fams"].append(family)     
            for gen in Name.objects.filter(legacy_parent=fam).order_by('latname'):
                genus = {"genus": gen, "species":[], "images":0, "taxa": 0 }## NEW "fid": gen.legacy_parent.pk maybe None
                family["genera"].append(genus)
                for sp in Name.objects.filter(legacy_parent=gen).order_by('latname'):
                    colnames = sp.colnames
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    images = VascularImage.objects.filter(plant_id=sp.pk).filter(nr__lt=100).filter(nr__gt=0).count()
                    genus["images"] += images       ## NEW
                    family["images"] += images       ## NEW
                    group["images"] += images       ## NEW
                    if images:
                        genus["taxa"] += 1
                        family["taxa"] += 1
                        group["taxa"] += 1
                        total_species += 1
                        total_images += images
                    species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images, }
                    ## None: "fid": sp.legacy_parent.legacy_parent.pk
                    genus["species"].append(species)
                    for syn in Name.objects.filter(legacy_parent=sp).order_by('sal_latname'):
                        synonym = {"syn": syn}
                        species["synonyms"].append(synonym)
    return render (request, template, locals())        


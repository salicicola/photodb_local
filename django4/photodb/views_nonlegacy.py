import os, datetime, pickle, sys
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

##import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
##f
##from .models import Name4, Name4, NameIndex
#### patch
##from .models import Name4 as Name
##from .models import PlantMeta, VascularImage
##from django.views.decorators.cache import cache_page
##from .views import VERSION
##from django.views.decorators.cache import cache_page
##from common.models import Town, Location

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


## .views_photos
from .views_lib import get_area, get_editdomain, PYTHON_VERSION, DJANGO_VERSION, DOMAIN, REVISION, get_image_table
from .__init__ import VERSION

from django.db.models import Q

DEBUG = True
IMAGES = {}
for indexed in NameIndex.objects.all():
    spid = indexed.spid
    images = indexed.images
    IMAGES[spid] = images
print ("checked cached index of images", len(IMAGES), "species with images")

try:
    COUNTIES = pickle.load(open("photodb/CACHE/counties/counties.pickle", "rb"))
except:
    COUNTIES = {}

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

TCOUNTIES2 = [
["BE", "Berkshire",  ""],
["FR", "Franklin",  ""],
["HS", "Hampshire",  ""],
["HD", "Hampden",  ""],
["WO", "Worcester",  ""],
['MI', "Middlesex",  ""],
["ES", "Essex",  ""],
["SU", "Suffolk",  ""],
["NO", "Norfolk",  ""],
["BR", "Bristol",  ""],
["PL", "Plymouth",  ""],
["BA", "Barnstable",  ""],
["DU", "Dukes",  ""],
["NA", "Nantucket", ""]
    ]

def fill_counties():
    recs = {}
    meta = SpeciesMeta.objects.all()
    ##m1 = meta[0]
    for m in meta:
        cc = m.counties.split()
        spid = m.spid
        rec = {}
        if cc:
            for i in range(len(TCOUNTIES)):
                c = TCOUNTIES[i][0]
                v = cc[i]
                if v == '*':
                    v = ''
                rec[c] = v
            recs[spid] = rec
            print (spid, rec)
    out = open("photodb/meta2.pickle", "wb")
    pickle.dump(recs, out)
    out.close()
    print (out, len(recs))

county_data = pickle.load(open("photodb/meta2.pickle", "rb"))


def get_county_status(spid, cname):    
    for c in TCOUNTIES:
        print ("checking", c)
        abb = ""
        if c[1] == cname:
            abb=c[0]
            print ("using", abb)
            try:
                existed = county_data[spid][abb]
                print ("check", spid, cname, abb, existed)
                return existed
            except KeyError:
                print (sys.exc_info())
                print ("will try to recreate county data")
                fill_counties()
                print ("will try get existed again")
                try:
                    print (abb, ":", county_data.get(spid))
                    existed = county_data[spid][abb]
                    print ("check again", spid, cname, abb, existed)
                except:
                    return ""
                
    return "" 


def get_towns(spid):
    recs = VascularImage.objects.filter(plant__pk=int(spid)) ## was spid=spid
    recs2 = GenericRecord.objects.filter(plant__pk=int(spid))
    print ("running get_towns for", spid, "got", len(recs), "records")
    print ("non photo records", len(recs2))
    if recs2:
        print (recs2[0], recs2[0].lcid, recs2[0].town, recs2[0].kind)
##        if recs2[0].kind:
##            raise Exception("debug")
    towns = []
    towns2 = {}
    lcids = {}
    for r in recs:
        lcid = r.lcid
        if not lcid:
            lcid = r.lcid_temp
        if lcid and not lcid in lcids:
            if lcid.startswith("MA"):
                try:
                    locrec = Location.objects.get(lcid=lcid)
                    town = locrec.town
                    if town and not town in towns:
                        towns.append(town)
                        if towns2.get(town):
                            towns2[town]["imids"].append(r.imid)
                        else:
                            towns2[town]={"imids":[r.imid]}
                    lcids[lcid] = None
                except:
                    print ("not fatal error, no lcid in", r)
                    print (sys.exc_info())
    for r in recs2:
        lcid = r.lcid
        if lcid:
            if not lcid in lcids:
                if lcid.startswith("MA"):
                    try:
                        locrec = Location.objects.get(lcid=lcid)
                        town = locrec.town
                        if town and not town in towns:
                            towns.append(town)
                            towns2[town] = {"generic": r.pk}
                            print ("added town by lcid", town)
                        lcids[lcid] = None
                    except:
                        print ("not fatal error, no lcid in", r)
                        print (sys.exc_info())
        else:
            town = r.town
            if town and not town in towns:
                towns.append(town)
                towns2[town] = {"generic": r.pk, "kind": r.kind}
                print ("added town", town, towns2[town])
##                if towns2[town]["kind"]:
##                    raise Exception("debug")

    towns.sort()
    print (towns)
    return (towns, towns2)

## FIXME: trying to update for GenericRecord
def get_counties(spid):
    counties = []
    external = []
    deleted = []
    towns, towns2 = get_towns(spid)
    print ("run get_counties for", spid, "got", len(towns))
    for town in towns:
        try:
            townrec = Town.objects.get(town=town)
            county = townrec.county
            if not county in counties:
                counties.append(county)
                if towns2.get(town).get("generic"):
                    external.append(county)
                    print ("kind", towns2.get(town).get("kind"))
                    if towns2.get(town).get("kind") and not towns2.get(town).get("kind") == 'add': ## newer
                        deleted.append(county)       ## newer
                print (county)
        except:
            print (sys.exc_info())
    COUNTIES[spid] = counties
    out = open("photodb/CACHE/counties/counties.pickle", "wb")
    pickle.dump(COUNTIES, out)
    out.close()
    print ("counties / external /deleted", counties, external, deleted)
##    if external:
##        raise Exception("external")
    return (counties, external, deleted)

IMAGES_TDM = {}
IMAGES_BBR = {}
## FIXME lcid_temp {{alpha version
def get_tdm_images():
    for obj in VascularImage, NonVascularImage, AnimalImage, VariaImage:
        _images = obj.objects.filter(lcid_temp__startswith="MA.TDM")
        for img in _images:
            if IMAGES_TDM.get(img.spid):
                IMAGES_TDM[img.spid] += 1
            else:
                IMAGES_TDM[img.spid] = 1
        print ("so far", len(IMAGES_TDM), "tdm_images")
    print ("checked cached index of TDM images", len(IMAGES_TDM), "species with images")      

def get_bbr_images():
    for obj in VascularImage, NonVascularImage, AnimalImage, VariaImage:
        _images = obj.objects.filter(lcid_temp__startswith="MA.BBR")
        for img in _images:
            if IMAGES_BBR.get(img.spid):
                IMAGES_BBR[img.spid] += 1
            else:
                IMAGES_BBR[img.spid] = 1
        print ("so far", len(IMAGES_BBR), "BBR_images")
    print ("checked cached index of TDM images", len(IMAGES_BBR), "species with images")      

def get_grr_images():
    data = {}
    for obj in VascularImage, NonVascularImage, AnimalImage, VariaImage:
        _images = obj.objects.filter(lcid_temp__startswith="MA.GRR")
        for img in _images:
            if data.get(img.spid):
                data[img.spid] += 1
            else:
                data[img.spid] = 1
        print ("so far", len(data), "GGR_images")
    print ("checked cached index ... images", len(data), "species with images") 
    return data     

get_tdm_images()    
get_bbr_images()
IMAGES_GRR = get_grr_images()


def newflat_checklist_filtered(request, lcid="MA.TDM", mode="", template="photodb/checklist_flat_tidmarsh.htm"):
    starts = datetime.datetime.now()
    tree = []
    spp = []
    species_found = 0
    images_present = 0
    ##return HttpResponse(html)
    for ugid in [301319, 301314, 301309, 301308, 301307, 301299, 299123]:
        higher = Name.objects.get(pk=ugid)
        print (higher.latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            family = {"fam": fam, "genera": [], "images":0}
            ##group["fams"].append(family)     
            for gen in Name.objects.filter(upper=fam).order_by('latname'):
                genus = {"genus": gen, "species":[], "images":0}
                ##family["genera"].append(genus)
                for sp in Name.objects.filter(upper=gen).order_by('latname'):
                    colnames = sp.colnames
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    if lcid=="MA.TDM":
                        images = IMAGES_TDM.get(sp.pnid, 0)
                    elif lcid=="MA.BBR":
                        images = IMAGES_BBR.get(sp.pnid, 0)
                    elif lcid=="MA.GRR":
                        images = IMAGES_GRR.get(sp.pnid, 0)
                    species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images}
                    for syn in Name.objects.filter(upper=sp).order_by('sal_latname'):
                        synonym = {"syn": syn}
                        species["synonyms"].append(synonym)
                    if images:
                        lname = "%s %s" % (gen.latname, sp.latname)
                        spp.append(lname)
                        images_present += images
                        species_found += 1
                        genus["species"].append(species) ## filtered
                        genus["images"] += images
                        counties = COUNTIES.get(sp.pnid, [])
                        if not counties:
                            counties = get_counties(sp.pnid)
                        counties = str(counties).replace("'", "").replace('"', '')
                        species["counties"] = counties
                if genus["images"]:
                    family["genera"].append(genus)
                    family["images"] += genus["images"]
            if family["images"]:
                group["fams"].append(family)
    print (type(spp), len(spp), "spp")
    if mode == "list":
        spp.sort()
        for sp in spp:
            print (sp)
    generated = datetime.datetime.now()
    delta = generated - starts
    print ("used %s" % (delta))
    secs = round(delta.total_seconds())
    return render (request, template, locals())        

## RESTORED 2021-02-01 updated @ 2022-02-03 from file 3425 [where django4==django3)
## OK: still errors syns without authors, e.g., = Isoetes macrospora <> correct at photodb/gallery/new/checklist/all/12963/ : Dur. [edit]
## OK check photodb/checklist_flat.htm 2022-02-02 14:30:19 >> had sal_authors >>> OK
## OK present  Metasequoia, Taxodium

## newer version : filtered = default: cultivated+exotic or any combination of exotic cultivated persistent or "" for None
def newflat_checklist(request, template="", filtered="exotic,cultivated"):
    cache = "photodb/CACHE/plantgallery.html"
    if filtered == "exotic,cultivated" and os.path.exists(cache):
        html = open(cache).read()
        print ("newflat_checklist uses cached file")
        return HttpResponse(html)        
    filtered = filtered.split(',')    
    start = datetime.datetime.now()
    tree = []
    grandtotal_species = 0
    total_species = 0 ## NEW
    total_images = 0 ## NEW ## [301319, 301314, 301309, 301308, 301307, 301299, 299123]
    excluded = []
    exotic = []
    cultivated = []
    persistent = []
    for ugid in [301319, 301314, 301309, 301307, 301308, 301299]:
        higher = Name.objects.get(pk=ugid)
        higher.latname = higher.latname.replace('_', ' ')
        print (higher.latname)
        group = {"higher": higher, "fams": [], "images":0, "taxa": 0} ## NEW
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            family = {"fam": fam, "genera": [], "images":0, "taxa": 0}## NEW
            group["fams"].append(family)     
            for gen in Name.objects.filter(upper=fam).filter(level='genus').order_by('latname'):
                genus = {"genus": gen, "species":[], "images":0, "taxa": 0 }## NEW "fid": gen.legacy_parent.pk maybe None
                family["genera"].append(genus)
                for sp in Name.objects.filter(upper=gen).filter(level='species').exclude(excluded=True).order_by('longname'): ## NEW ## fixing soring not latname 
                    colnames = sp.colnames
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    images = VascularImage.objects.filter(plant_id=sp.pk).filter(nr__lt=100).filter(nr__gt=0).count() ## i.e., ALL published
                    genus["images"] += images       ## NEW
                    family["images"] += images       ## NEW
                    group["images"] += images       ## NEW
                    if images:
                        genus["taxa"] += 1
                        family["taxa"] += 1
                        group["taxa"] += 1
                        total_images += images
                        grandtotal_species += 1
                        species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images, }
                        for syn in Name.objects.filter(upper=sp).order_by('sal_latname'):
                            if syn.latname:
                                synonym = {"syn": syn}
                                species["synonyms"].append(synonym)
                        if isinstance(species.get("meta"), type(SpeciesMeta())) and species.get("meta").introduced=='cultivated':
                                print ("cultivated", species)
                                cultivated.append(species)
                                if 'cultivated' in filtered:
                                    excluded.append(species)
                        elif isinstance(species.get("meta"), type(SpeciesMeta())) and species.get("meta").introduced=='exotic':
                                print ("exotic", species)
                                exotic.append(species)
                                if 'exotic' in filtered:
                                    excluded.append(species)
                        elif isinstance(species.get("meta"), type(SpeciesMeta())) and species.get("meta").introduced=='persistent':
                                print ("persistent", species)
                                persistent.append(species)
                                if 'persistent' in filtered:
                                    excluded.append(species)
                        if not filtered:
                            genus["species"].append(species)
                            total_species += 1
                        else:
                            if species in excluded:
                                print ("excluding", species)
                            else:
                                genus["species"].append(species)
                                total_species += 1
                    else:
                        print ("no images for", sp)
                ## add genus here to family XXX
            ## end of family here ?
        ## end of higher group, nothing to do
    end = datetime.datetime.now()
    seconds = int((end-start).total_seconds())
    print ( "seconds",  seconds)
    print ("total spp", total_species)
    print ("grand total spp", grandtotal_species)
    print ("excluded", len(excluded))
    print ("were using filter", filtered)
    print ("exotic", exotic)
    print ("cultivated", cultivated)
    
    return render (request, template, locals())        


   
def new_checklist_families(request, template="photodb/checklist_nonlegacy_fast.htm"):
    from . import checklist_wrk
    photodb_installed = checklist_wrk.photodb_available
    start = datetime.datetime.now()
    relevant = Name.objects.filter(category='vascular').filter(level='species').exclude(excluded=True).exclude(disabled=True).exclude(upper__isnull=True).count()
    tree = []
    for ugid in [301319, 301314, 301309, 301308, 301307, 301299, 299123]:
        higher = Name.objects.get(pk=ugid)
        higher.latname = higher.latname.replace('_', ' ')
        print (higher.latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            genera = Name.objects.filter(level='genus').filter(upper=fam)
            spp = 0
            for g in genera:
                species = Name.objects.filter(level='species').filter(upper=g).exclude(disabled=True).exclude(excluded=True)
                for sp in species:
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                        if meta.introduced == 'cultivated':
                            pass
                        else:
                            spp += 1
                    except:
                        print (sys.exc_info())
            family = {"fam": fam, "genera": genera, "species": spp}
            
            ## FIXME
            group["fams"].append(family)     
    ends = datetime.datetime.now()
    delta = ends - start
    print ("estimated reelevant species without meta recs", relevant)
    print ("used %s" % (delta))
    secs = round(delta.total_seconds())
    print (delta.total_seconds(), "seconds")
    return render (request, template, locals())        

def new_checklist_family_old(request, fid, counties_rewrite=True, template="photodb/checklist_nonlegacy_family.htm"):
    start = datetime.datetime.now()
    fam = Name.objects.get(pk=int(fid))
    print (fam)
    family = {"fam": fam, "genera": []}
    for gen in Name.objects.filter(upper=fam).order_by('latname'):
        genus = {"genus": gen, "species":[], "images":0}
        family["genera"].append(genus)
        for sp in Name.objects.filter(upper=gen).filter(level='species').order_by('latname'):
            try:
                colnames = Name.objects.get(pk=sp.pk).colnames
            except:
                colnames = "XXX"
            try:
                meta = SpeciesMeta.objects.get(pk=sp.pk)
            except:
                meta = {}
            images = IMAGES.get(sp.pnid, 0)
            if counties_rewrite:
                counties = []
            else:
                counties = COUNTIES.get(sp.pnid, [])
            if not counties:
                counties = get_counties(sp.pnid)
            counties = str(counties).replace("'", "").replace('"', '')
            print ("finally for", sp.pnid, "counties", counties)
            species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images, "counties": counties}
            genus["species"].append(species)
            genus["images"] += images
            for syn in Name.objects.filter(upper=sp).order_by('latname'):
                synonym = {"syn": syn}
                species["synonyms"].append(synonym)
            if sp.latname == 'alba' or sp.pnid==301809:
                print ("debug", "N. alba")
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds(), 3)
    print (delta.total_seconds(), "seconds")
    return render (request, template, locals())

def view_photo_records(request, pnid=None, lcid=None, exclude=None, thumbs=True, view="gallery", template="photodb/photos/gallery_index.htm", save=False, legacy=False, public=True, lcid_starts=None, fid=None):
    if fid:
        print ("running in compatibility mode, fid, spid", fid, pnid)
    tcounties = TCOUNTIES
    ## XXX
    if request.user.username == 'salicarium' or request.user.username == 'gmp':
        authorized = True
    else:
        authorized = False
    debug_starts = datetime.datetime.now()
    max_thums = 5000  ## not in use anywere below anyway ? why do not shoe ? XXX
    area = get_area(lcid)    
    edit_domain = get_editdomain()
    total_species, total_photos = 0, 0
    gnum = 0
    tree = []
    version = VERSION
    python_version = PYTHON_VERSION
    django_version = DJANGO_VERSION
    domain = DOMAIN
    revision = REVISION.split()[0]
    TDM = ""
    if lcid_starts:
        TDM = "tidmarsh/"
    if pnid:
        root_name = Name.objects.get(pnid=pnid)
        rank = root_name.level ## rank
        print ("view_photo_records() got", root_name, rank)
        
        if rank == 'group':
            group = root_name
            grp = [group.latname.replace('_', ' '), group.colnames, group.authors, group.pnid, [], 0]
            print ("pass", grp)
            tree.append(grp)
            for family in Name.objects.filter(upper=group).order_by('latname'): ## .order_by("sal_latname")
                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
                print ("pass fam", fam)
                grp[4].append(fam)
                for genus in Name.objects.filter(upper=family).order_by("latname"):
                    gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos, public, lcid_starts)
                    fam[4].append(gen) ## XXX integer
        elif rank == 'family':
            print ("using family")
            
            family = root_name
            group = root_name.upper
            print (group)
            ##return HttpResponse("debug")
            grp = ["", "", "", group.pnid, [], 0]
            tree.append(grp)
            try:
                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
            except:
                fam = [family.sal_latname.replace('_', ' '), family.colnames, family.sal_authors, family.pnid, [], 0]
            print ("pass fam", fam)
            grp[4].append(fam)
            for genus in Name.objects.filter(upper=family).order_by("latname"):
                print ("pass genus", genus)
                gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos, public, lcid_starts)
                fam[4].append(gen) ## XXX integer
        elif rank == 'genus':
            print ("using genus")
            ##return HttpResponse("debug")
            genus = root_name
            family = genus.upper
            group = family.parent
            grp = ["", "", "", group.pnid, [], 0]
            tree.append(grp)
            ## FIXME was ["", "", "", family.pnid, [], 0]
            fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
            grp[4].append(fam)
            gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos, public, lcid_starts)
            fam[4].append(gen)
        elif rank == 'species':
            species = root_name
            print ("doing species", species.category)
            genus = root_name.upper
            family = genus.upper
            group = family.upper
            grp = ["", "", "", group.pnid, [], 0]
            tree.append(grp)
            ## FIXME was ["", "", "", family.pnid, [], 0]
            fam = [family.latname.replace('_', ' '), family.colnames, family.authors,  family.pnid, [], 0]
            grp[4].append(fam)
            gen = [genus.latname.replace('_', ' '), genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
            fam[4].append(gen)
            table = get_image_table(species)
            print ("using", table, "gen", genus)
            if public:
                print ("public mode")
                photos = table.objects.filter(nr__gt=0).filter(nr__lt=100).filter(plant__pnid = species.pnid).order_by("nr")
            else:
                photos = table.objects.filter(nr__gt=0).filter(plant__pnid = species.pnid).order_by("nr")
            if lcid_starts:
                ##photos = photos.filter(locality__pk__startswith=lcid_starts)
                ##print ("debug for TDM", photos)
                ##photos = photos.filter(locality__pk__startswith="MA.BDC")
                ##print ("debug for BDC", photos)
                photos = photos.filter(Q(locality__pk__startswith='MA.TDM') | Q(locality__pk__startswith='MA.BDC') | Q(lcid_temp__startswith='MA.BDC'))
                print ("filtered", lcid_starts, '+ MA.BDC')
            removed = table.objects.filter(nr__lte=0).filter(plant__pnid = species.pnid)
            print ('removed', removed, "photos")
            ### FIXME 2021-10-23
            try:
                meta = SpeciesMeta.objects.get(pk=species.pnid)
            except:
                meta = "?" + str(sys.exc_info()) ### XXX
            ##meta = "XXX"
            print ("got %s photos" % len(photos))
            ##photos = VascularImage.objects.filter(spid = species.pnid)
            if legacy:
                syns = Name.objects.filter(legacy_parent=species).order_by('sal_latname') ##.order_by("latname")
                spec = [species.sal_latname, species.colnames, species.sal_authors, species.pnid,
                   syns, len(photos), photos, meta, removed, species.caption, species.rank, species.parent]
            else:
                syns = Name.objects.filter(upper=species).filter(level='synonym').order_by('latname') ##.order_by("latname") BUG FIXING 2023-0120
                spec = [species.latname, species.colnames, species.authors, species.pnid,
                   syns, len(photos), photos, meta, removed, species.caption, species.rank, species.parent] ## XXXX added two
            gen[4].append(spec)
            gen[5] += len(photos)
            fam[5] += len(photos)
            grp[5] += len(photos)
            total_species += 1
            total_photos += len(photos)
            print (tree)
        else:
            return HttpResponseBadRequest("illegal %s" % pnid)
    else:
        ## too much time: to cache it
        start =1
        ends = 25
        for group in Name.objects.filter(level='group').order_by('pnid'):
            ## repeated from above FIXME
            grp = [group.latname.replace('_', ' '), group.colnames, group.authors, group.pnid, [], 0]
            print ("pass", grp)
            tree.append(grp)
            for family in Name.objects.filter(legacy_parent=group).order_by("latname"):
                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
                print ("pass fam", fam)
                grp[4].append(fam)
                for genus in Name.objects.filter(upper=family).order_by("latname"):
                    ##print ("pass genus", genus)
                    gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos)
                    fam[4].append(gen) ## XXX integer
        if save:            
            debug_ends = datetime.datetime.now()
            print (debug_ends, "will start rendering")
            time_spent = debug_ends - debug_starts
            content = render_to_string(template, locals())
            with open('photos/cache/index_list.html', 'w') as static_file:
                static_file.write(content)
            print ("debugging performance") ### 0:01:14.787926
            print ("spent time", time_spent)
            return view_cached_list(request)
    debug_ends = datetime.datetime.now()
    print ("debugging performance") ### 0:01:14.787926
    time_spent = debug_ends - debug_starts
    print ("spent", time_spent)
    print ("end def from views_nonlegacy XXXX in photodb")
    if legacy:
        method='legacy'
    else:
        method='simple'
    print ("will use template", template)
    return render(request, template, locals())

def process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos, public, lcid_starts):
    print ("calling process_genus for ", grp, fam, genus)
    if genus.latname:
        gen = [genus.latname.replace('_', ' '), genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
    elif genus.sal_latname:
        gen = [genus.sal_latname.replace('_', ' '), genus.colnames, genus.sal_authors, genus.pnid, [], 0, "genus"]
    else:
        gen = ["", genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
    print ("processing", gen)
    print ("will find species", Name.objects.filter(upper=genus).order_by("latname"))
    for species in Name.objects.filter(upper=genus).order_by("longname"):  ##latname
        print ("processing species", species)
        table = get_image_table(species)
        print ("got", table)
        ## FIXME temporarily using lcid_temp and replacing spid
        ##all_photos = table.objects.exclude(lcid__isnull=True).exclude(lcid__exact='').filter(spid = species.pnid)
        all_photos = table.objects.filter(plant__pk = species.pnid)                                                    ## XXX: remove: exclude(lcid_temp__isnull=True).exclude(lcid_temp__exact='').
        print ("got %s photos" % len(all_photos))
        ##photos = VascularImage.objects.exclude(lcid__isnull=True).exclude(lcid__exact='').filter(spid = species.pnid)
        ##print ("found %s photos" % len(photos))
        if not lcid:
            if exclude:
                photos = all_photos.filter(nr__gt=0).exclude(lcid__contains='MA').order_by("nr")
            else:
                photos = all_photos.filter(nr__gt=0).order_by("nr")
        else:
            if exclude:
                photos = all_photos.filter(nr__gt=0).exclude(lcid__contains=lcid).order_by("nr")
            else:
                photos = all_photos.filter(nr__gt=0).filter(lcid__contains=lcid).order_by("nr")
        if public:
            photos = photos.filter(nr__lt=100)
            print ("using public mode")
        if lcid_starts:
            photos = photos.filter(Q(locality__pk__startswith='MA.TDM') | Q(locality__pk__startswith='MA.BDC'))
            print ("filtered", lcid_starts, ' or MA.BDC', 'got', photos)
        if not lcid:
            if exclude:
                removed = all_photos.filter(nr__lte=0).exclude(lcid__contains='MA').order_by("nr")
            else:
                removed = all_photos.filter(nr__lte=0).order_by("nr")
        else:
            if exclude:
                removed = all_photos.filter(nr__lte=0).exclude(lcid__contains=lcid).order_by("nr")
            else:
                removed = all_photos.filter(nr__lte=0).filter(lcid__contains=lcid).order_by("nr")

                
        print ("PATCH::: final %s photos %s removed" % (len(photos), len(removed)))
        try:
            meta = SpeciesMeta.objects.get(pk=species.pnid)
        except:
            meta = "[]"
        ## XXX 2021-10-23
        if photos:
           syns = Name.objects.filter(upper=species).order_by('latname')
           spec = [species.latname, species.colnames, species.authors, species.pnid,
                   syns, len(photos), photos, meta, removed, species.caption, species.rank, species.parent]
           gen[5] += len(photos)
           fam[5] += len(photos)
           grp[5] += len(photos)
           gen[4].append(spec)
           total_photos += len(photos)
           total_species += 1
           ##print ("debug", gen[4], total_species, total_photos)
    return (gen, total_species, total_photos)

def animals_index(request, template="photodb/animals_index.htm"):
    family_views = ["Birds", "Odonata"]
    total_images = 0
    total_taxa = 0
    public = True
    if request.user.is_authenticated:
        if request.user.username == "salicarium" or request.user.username=="IK":
            public = False
    insects = {"orders":[],}
    meta = {}
    for family in Name.objects.filter(category='animals').filter(level="family"):
        pk = family.pk
        if public:
            images = AnimalImage.objects.filter(nr__gt=0).filter(nr__lt=100).filter(plant__upper__upper=family)
        else:
            images = AnimalImage.objects.filter(plant__upper__upper=family)
        pnids = images.values_list("plant__pk")
        pnids = list(pnids)
        pnids = set(pnids)
        pnids = len(pnids)
        images = len(images)
        total_images += images
        total_taxa += pnids
        meta[pk]= {"taxa":pnids, "images":images}

    insecta = Name.objects.get(pk=12104)
    orders = Name.objects.filter(legacy_parent=insecta).order_by('latname')
    for order in orders:
        ## XXX palliativ !
        if public:
            images = AnimalImage.objects.filter(nr__gt=0).filter(nr__lt=100).filter(plant__upper__upper=order)
        else:
            images = AnimalImage.objects.filter(plant__upper__upper=order)
        pnids = images.values_list("plant__pk")
        images = len(images)
        print (pnids)
        pnids = list(pnids)
        print (pnids)
        pnids = set(pnids)
        pnids = len(pnids)
        print (pnids)
        r = {"pnid": order.pk, "name": order.latname, "colnames": order.colnames, "taxa":pnids, "images":images}
        print (r)
        if order.latname == 'Odonata':
            r["pubimages"]= images
        else:
            r["pubimages"] = images
        insects["orders"].append(r)
    if public:
        url_token = "view"
    else:
        url_token = "simple"
    return render(request, template, locals())

import copy
def new_checklist_family(request, fid, counties_rewrite=True, template="photodb/checklist_nonlegacy_family.htm"):
    start = datetime.datetime.now()
    tcounties = TCOUNTIES
    fam = Name.objects.get(pk=int(fid))
    print (fam)
    authorized = True ## FIXME
    family = {"fam": fam, "genera": []}
    for gen in Name.objects.filter(upper=fam).filter(level='genus').order_by('latname'):
        genus = {"genus": gen, "species":[], "images":0}
        family["genera"].append(genus)
        for sp in Name.objects.filter(upper=gen).filter(level='species').order_by('latname'):
            ##relocated = TCOUNTIES2[:]
            relocated = copy.deepcopy(TCOUNTIES2) ## ?? maybe just copy?
            print ("[re]define empty relocated for sp", relocated, sp)
            try:
                colnames = Name.objects.get(pk=sp.pk).colnames
            except:
                colnames = "XXX"
            try:
                meta = SpeciesMeta.objects.get(pk=sp.pk)
            except:
                meta = {}
            ### XXX cache better disabl for individual family
##            images = IMAGES.get(sp.pnid, 0)
            ##print (sp.pnid, "cached images", images)
            images = VascularImage.objects.filter(plant__pnid=sp.pnid).count()
            print (sp.pnid, "actual images", images)
            if counties_rewrite:
                counties = []
            else:
                counties = COUNTIES.get(sp.pnid, [])
            if not counties:
                counties, external, deleted = get_counties(sp.pnid)  ## FIXME somewerelse counties =
            print (counties, external, deleted)
            counties.sort()
            county_relocated = []
            grecs = GenericRecord.objects.filter(plant=sp).filter(GUID__startswith="http")
            print ("generic", grecs, "for plant", sp)
            for county in counties:
                status = get_county_status(sp.pnid, county)
                print ("from", county, "as status", status, external, deleted)
                county_relocated.append((county, status))
                if not status:
                    status = "X"
                for c in relocated:
                    if county == c[1]:
                        c[2] = status
                        if deleted:
                            if c[1] in deleted:
                                c[2] = "DEL"
                                print (county, c, "deleted:", deleted)
                                ##raise Exception("XXX")
##            if sp.pk==301904:
##                raise Exception("debug")
##                        ##print ("DEBUG set relocated status", status)
##                        ##raise Exception("debug: updated", relocated)
            ##print ("updated", relocated)
            counties = str(counties).replace("'", "").replace('"', '')
            species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [], "images":images, "counties": counties, 
                        "relocated":relocated, "counties_relocated": county_relocated, "external": external, "grecs":grecs}
            print (species)
            genus["species"].append(species)
            genus["images"] += images
            for syn in Name.objects.filter(upper=sp).order_by('latname'):
                synonym = {"syn": syn}
                species["synonyms"].append(synonym)
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds(), 3)
    print (delta.total_seconds(), "seconds")
    return render (request, template, locals())

##def species_latnames(request, template):
##    sp_names = Name.objects.filter(level='species').exclude(excluded=True).exclude(disabled=True)
##    records = []
##    for sp in sp_names:
##        if sp.upper:
##            longname = "%s %s" % (sp.upper.latname, sp.latname)
##            images = VascularImage.objects.filter(spid=sp.pnid).filter(nr__lt=100).count() 
##            rec = (longname, "", sp, images)
##            records.append(rec)
##    records = sorted(records, key=lambda record: record[0])
##    for rec in records:
##        print (rec[0], ":", rec[3])
##    return render (request, latname, locals())

## from legacy_view for newer classification
## FIXME needs cache
def latnames(request, template="photodb/latnames.htm", latnames=True, cache=False):
    ## by default it will use cached file if exists and will NOT create it
    ## using cache=True, will enforce using current data and create/re-create cache
    if latnames:
        cached = os.path.join("photodb", "CACHE", "latnames.html")
    else:
        cached = os.path.join("photodb", "CACHE", "comnames.html")
    if not cache:
        if os.path.exists(cached):
            html = open(cached).read()
            return HttpResponse(html)
    images = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
    print ("running latnames/colnames mode latnames=%s, %s relevant images; do cache=%s" % (latnames, len(images), cache))
    records = {}
    for image in images:
        plant = image.plant
        latname = plant.latname
        genname = plant.upper.latname
        ##name = "%s %s" % (genname, latname)
        name = plant.longname
        colnames = plant.colnames
        authors = plant.authors
        fid = plant.upper.upper.pk
        if latnames:
            key = (name, colnames, authors, plant.upper.upper, plant.pk)
        else:
            key = (colnames, name, authors, plant.upper.upper, plant.pk)
        if not key in records:
            records[key] = 1
            ##print (key)
        else:
            records[key] += 1 
    items = records.items()
    items = list(items)
    items.sort()
    print (len(items))
    print (items[0])
    generated = timezone.now()
    if cache:
        from django.template.loader import get_template
        t = get_template(template)
        html = t.render(locals())
        out = open(cached, "w")
        out.write(html)
        out.close()
        print ("cached", out)
        return HttpResponse(html)
    else:
        return render(request, template, locals())


def flagged (request, kind="exotic", template="photodb/gallery_append.htm"):
    is_native = False
    if kind=='naturalized':
        key = 'introduced'
    elif kind == 'no longer extant' or kind == 'noextant':
        key = 'no longer extant'
    else:
        key = kind
    print ("running flagged(): will filter by introduced=%s" % key)
    if kind == 'invasive':
        pnids = SpeciesMeta.objects.exclude(invasive__isnull=True).exclude(invasive='').values_list('spid', flat=True)
    elif kind.isupper():
        is_native = True
        pnids = SpeciesMeta.objects.filter(rare=kind).values_list('spid', flat=True)
    else:
        pnids = SpeciesMeta.objects.filter(introduced=key).values_list('spid', flat=True)
    pnids = list(pnids)
    names = Name.objects.in_bulk(pnids)
    recs = names.values()
    spp = []
    for rec in recs:
        if rec.upper:
            name = "%s %s" % (rec.upper.latname,  rec.latname)
        elif rec.legacy_parent:   ## '<' not supported between instances of 'Name' and 'Name' #921  ???
            name = "%s %s" % (rec.legacy_parent.latname,  rec.latname)
            print (rec, name)
            ##raise Exception("no rec.upper")
        else:
            print ("DISABLED ORPHAN", rec)
            name = None
        if name:
            species = (name, rec, VascularImage.objects.filter(plant=rec).filter(nr__gt=0).filter(nr__lt=100).order_by('nr'))
            spp.append( species )
    print ("will sort by first element in list of %s" % len(spp))
    spp.sort(key=lambda y: y[0]) ## <' not supported between instances of 'Name' and 'Name'
    return render (request, template, locals())

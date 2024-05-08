import os, sys, datetime, inspect
from names.models import Name, SpeciesMeta, NameAnnotation

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import render_to_string

## simplified from checklist.checklist_wrk ::
## added longname in species_info()
## modified template photodb/checklist_nonlegacy_family_new.htm {may work with checklist' version}

## ??? [iNat saved 3 recs 2022-02-07] 3 obs XXX

package_name = os.path.dirname(__file__)
module_name = os.path.splitext(os.path.split(__file__)[-1])[0]
RARE = {"H": "Historic", "WL": "Watch-Listed", "SC": "Special Concern", "T": "Threatened", "E": "Endangered"}
COUNTIES = [
    ["BE", "Berkshire",  [], []],
    ["FR", "Franklin",  [], []],
    ["HS", "Hampshire",  [], []],
    ["HD", "Hampden",  [], []],
    ["WO", "Worcester",  [], []],
    ['MI', "Middlesex",  [], []],
    ["ES", "Essex",  [], []],
    ["SU", "Suffolk",  [], []],
    ["NO", "Norfolk",  [], []],
    ["BR", "Bristol",  [], []],
    ["PL", "Plymouth",  [], []],
    ["BA", "Barnstable",  [], []],
    ["DU", "Dukes",  [], []],
    ["NA", "Nantucket", [], []]
]
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
VERSION = "2.1.1"
VERSION = "2.1.2" ## revno 38+
VERSION = "2.1.3" ## revno 40+ (improved CNH records in townmapper5 & checklist: light-green if verified)
##[mostly normalized: latnames at rank species and below without space; 'var/ssp' not included in authors
## yet to do empty rank in some genera : to check if valid
## used check_names.* to validate
VERSION = "2.1.4" ## starts using herbarium samples in photodb.checklist* ## 2023-07-18+

from . import * ## DOCKERIZED DB_MODIFIED PHOTODB_AVAILABLE PHOTOS_AVAILABLE debug_mode PACKAGE
package_name = PACKAGE
photodb_available = PHOTODB_AVAILABLE
print ("loading [%s.%s]" % (package_name, module_name))

## FIXME state should be always "" when running @ /names// ?
def taxa_index (request, mode, template, state='MA'):
    if mode == 'fixed':
        return new_checklist_families(request, template)
    elif mode == 'flexible':
        return get_families(request, template, state)
    else:
        return HttpResponseBadRequest("wrong attribute")

def new_checklist_families(request, template):
    caller = inspect.stack()[0][3]
    print ("running", caller)
    version = VERSION
    db_modified = DB_MODIFIED
    start = datetime.datetime.now()
    photodb_installed=photodb_available
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

## not using XML ! flat ! from checklist
def get_families(request, template, state): ## ="photodb/checklist_nonlegacy_fast.htm"
    version = VERSION
    caller = inspect.stack()[0][3]
    mode = 'tree'
    db_modified = DB_MODIFIED
    print ("running %s.%s.%s" % (package_name, module_name, caller))
    start = datetime.datetime.now()
    photodb_installed=photodb_available
    relevant = Name.objects.filter(category='vascular').filter(level='species').exclude(excluded=True).exclude(disabled=True).exclude(upper__isnull=True).count()
    tree = []
    print ("checklist_xml.get_families", start, photodb_installed, relevant, "species",  tree)
    for ugid in [301319, 301314, 301309, 301308, 301307, 301299, 299123]:
        higher = Name.objects.get(pk=ugid)
        higher.latname = higher.latname.replace('_', ' ')
        print (higher.latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            genera = Name.objects.filter(level='genus').filter(upper=fam).order_by('latname')
            spp = 0
            for g in genera:
                species = Name.objects.filter(level='species').filter(upper=g).exclude(disabled=True).exclude(excluded=True).order_by('latname')
                subgenera = Name.objects.filter(parent=g).exclude(level="species").exclude(rank="hybrid").exclude(rank="synonym").order_by("latname") ## FIXME sorting; hybrdi added to patch Spirantes x intermedia
                if subgenera:
                    print (subgenera)
                    sgenera = []
                    for subgenus in subgenera:
                        sgenera.append( {"pnid": subgenus.pnid, "latname": subgenus.latname, "rank":subgenus.rank})
                    g.__dict__["subgenera"] = sgenera
                    print (g, g.__dict__.get("subgenera"))
                g.__dict__["species"] = 0
                for sp in species:
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                        if meta.introduced == 'cultivated' or meta.introduced == 'exotic':
                            pass
                        else:
                            spp += 1
                            g.__dict__["species"]  += 1
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


def get_nhesp_counties(spid):
    return []

def species_info(sp, use_photorecords=True):    
    try:
        meta = SpeciesMeta.objects.get(pk=sp.pnid)
    except:
        print ("fatal error for", sp.upper, sp, sys.exc_info())
        raise
    syns = Name.objects.filter(upper=sp).exclude(latname__isnull=True).exclude(latname="").order_by('latname') ## fixing empty entries: by excludw
    images = 0 
    all_images = 0 
    colnames = sp.colnames
    (counties, cnh_updated) = counties_info2(sp, meta)
    total_cnh = 0
    for c in counties:
        total_cnh += c["cnh"]  ### NEW
    ext_urls = [] ## XXX generic_urls(sp)
    _authors = ""
    if sp.latname == sp.parent.latname:
        _authors = sp.parent.authors
        if not _authors:
            _authors = sp.authors
    if sp.rank == 'species':
        longname = "<i>%s</i>" % sp.latname
    elif sp.rank == 'variety':
        longname = "<i>%s</i> %s var. <i>%s</i>" % (sp.parent.latname, _authors, sp.latname)
    elif sp.rank == 'subspecies':
        longname = "<i>%s</i> %s ssp. <i>%s</i>" % (sp.parent.latname, _authors, sp.latname)
    elif sp.rank == 'forma':
        longname = "<i>%s</i> %s f. <i>%s</i>" % (sp.parent.latname, _authors, sp.latname)
    elif sp.rank == 'cultivar':
        longname = "<i>%s</i>  %s" % (sp.parent.latname, sp.latname)
    else:
        longname = "<i>%s</i>" % sp.latname
    if sp.pk == 13340:
        print ("DEBUG [", sp, "]", sp.rank, longname, "latname:", sp.latname)
        ##raise Exception("debug")
    if _authors:
        authors = ""
    else:
        authors = sp.authors
    species = {"species": sp, "longname": longname, "authors": authors,
               "colnames": sp.colnames, "meta": meta, "synonyms": syns, "images":images,
               "all_images": all_images, "counties": counties, "grecs": ext_urls, "total_cnh":total_cnh, "cnh_updated":cnh_updated,
               "nhesp_counties": get_nhesp_counties(sp.pnid)}
    if sp.caption:
        species["caption"] = sp.caption
    if meta.rare:
        rare = meta.rare
        meta.rare = RARE.get(rare, "ERROR")
    return species

def checklist_family(request, fid, mode=None, template="names/checklist_nonlegacy_family_new.htm", authorized_cnh=False,
                     use_photorecords=False): ##  all | public | None
    caller = inspect.stack()[0][3]
    photodb_installed=photodb_available
    print ("running %s.%s.%s" % ("names", "xxx", caller))
    version = VERSION
    db_modified = DB_MODIFIED
    townmapped = []
    islocal = False ## is_local(request)
    townmapper_installed=False ## townmapper_available
    server="http://172.104.19.75"
    tcounties = COUNTIES
    start = datetime.datetime.now()
    fam = Name.objects.get(pk=int(fid))
    authorized = True ## FIXME
    family = {"fam": fam, "genera": []}
    total_species=0
    total_images=0
    total_published_images = 0
    irrelevant = []
    for gen in Name.objects.filter(upper=fam).filter(level='genus').order_by('latname'):
        genus = {"genus": gen, "species":[], "images":0}
        for sp in Name.objects.filter(upper=gen).filter(level='species').exclude(disabled=True).exclude(excluded=True).order_by('longname'):
            meta = SpeciesMeta.objects.filter(pk=sp.pk)
            if meta:
                meta = meta[0]
                if not meta.counties:
                    print ("skip without counties", sp)
                    continue
                if not mode and (meta.introduced == 'exotic' or meta.introduced == 'cultivated'):
                    print("skip exotic/cultivated", sp)
                    irrelevant.append(sp)
                    pass
                else:
                    species = species_info(sp, use_photorecords)
                    print (species)
                    species["mapped"] = False
                    species["inat_gpx"] = False
                    total_images =0
                    total_published_images =0
                    total_species += 1
                    external_sample = NameAnnotation.objects.filter(plant=sp).filter(kind='sample').values_list('plant', flat=True) ## 
                    if external_sample:
                        species["external_sample"] = list(external_sample)
                    external_photos = NameAnnotation.objects.filter(plant=sp).filter(kind='photo').values_list('url', flat=True)
                    external_cached = NameAnnotation.objects.filter(plant=sp).filter(kind='photo').values_list('cached', flat=True)
                    external_results = []
                    if external_photos:
                        species["external_photos"] = external_photos
                        for fname in external_cached:
                            external_results.append("/static/photos/CACHE/%s" %  fname)
                        if external_results:
                            species["external_cached"] = external_results
                    external_notes = NameAnnotation.objects.filter(plant=sp).filter(kind='note').values_list('note', flat=True) ## better to use explicit note != ''/None
                    if external_notes:
                        species["external_notes"] = list(external_notes)                                                    
                    genus["species"].append(species)
                    genus["images"] += species.get("images", 0)
            else:
                print ("error", sp)
                raise Exception("species without meta")
        family["genera"].append(genus)
    ends = datetime.datetime.now()
    delta = ends - start
    print ("used %s" % (delta))
    secs = round(delta.total_seconds(), 3)
    print (delta.total_seconds(), "seconds")
    print ("finished %s.%s.%s" % (package_name, module_name, inspect.stack()[0][3]))
    print ("irrelevant skipped", irrelevant)
    return render (request, template, locals())    

def counties_info2(sp, meta, use_photorecords=True):
    counties = [
        {"abr":"BE", "name":"Berkshire",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"FR", "name":"Franklin",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"HS", "name":"Hampshire",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"HD", "name":"Hampden",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"WO", "name":"Worcester",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":'MI', "name":"Middlesex",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"ES", "name":"Essex",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"SU", "name":"Suffolk",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"NO", "name":"Norfolk",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"BR", "name":"Bristol",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"PL", "name":"Plymouth",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"BA", "name":"Barnstable",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"DU", "name":"Dukes",  "images":[], "planted": [], "records":0, "cnh":0},
        {"abr":"NA", "name":"Nantucket", "images":[], "planted": [], "records":0, "cnh":0},
    ]
    cnh_updated = ""
    return (counties, cnh_updated)



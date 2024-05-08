from django.shortcuts import render
from django.views.decorators.cache import cache_page
from .models import *
from names.models import *
from common.models import *

def set_planted(spid, lcid=None):
    name = Name.objects.get(pk=spid)
    recs = VascularImage.objects.filter(plant=name)
    print ("name", name, len(recs))
    if lcid:
        recs = recs.filter(locality__pk__contains=lcid)
        print ("lcid/name", lcid, name, len(recs))
    for r in recs:
        r.is_planted='yes'
        r.save()
        print (r.imid, r.locality, r.is_planted) 

##from photodb.checklist import counties_info

def counties_info(towns, sp, meta):
    counties = [
        {"abr":"BE", "name":"Berkshire",  "images":[], "planted": []},
        {"abr":"FR", "name":"Franklin",  "images":[], "planted": []},
        {"abr":"HS", "name":"Hampshire",  "images":[], "planted": []},
        {"abr":"HD", "name":"Hampden",  "images":[], "planted": []},
        {"abr":"WO", "name":"Worcester",  "images":[], "planted": []},
        {"abr":'MI', "name":"Middlesex",  "images":[], "planted": []},
        {"abr":"ES", "name":"Essex",  "images":[], "planted": []},
        {"abr":"SU", "name":"Suffolk",  "images":[], "planted": []},
        {"abr":"NO", "name":"Norfolk",  "images":[], "planted": []},
        {"abr":"BR", "name":"Bristol",  "images":[], "planted": []},
        {"abr":"PL", "name":"Plymouth",  "images":[], "planted": []},
        {"abr":"BA", "name":"Barnstable",  "images":[], "planted": []},
        {"abr":"DU", "name":"Dukes",  "images":[], "planted": []},
        {"abr":"NA", "name":"Nantucket", "images":[], "planted": []},
    ]
    county_status = {}
    _meta_counties = meta.counties.split()
    for i in range(len(_meta_counties)):
        county_status[counties[i]["abr"]] = _meta_counties[i]
    ##print (_meta_counties)                  
    for county in counties:
        for town in towns:
            if towns[town]["county"] == county["name"]:
                county["images"].extend(towns[town]["imids"])
                county["planted"].extend(towns[town]["planted"])
                county["status"] = county_status[county["abr"]]
                county["generic"] = towns[town].get("generic")
                county["kind"] = towns[town].get("kind")
                if towns[town].get("sal_herb"):
                    county["sal_herb"] = True
    ## TRYING NEW APPROACH
    recs = VascularImage.objects.filter(plant=sp).filter(nr__lt=101).filter(nr__gt=0).exclude(is_verified='no').exclude(is_planted='yes')
    for r in recs:
        lcid = r.lcid
        if not lcid:
            lcid = r.lcid_temp
        if lcid:
            if lcid.startswith("MA"):
                try:
                    locrec = Location.objects.get(lcid=lcid)
                    county = locrec.county
                    ##print (county)
                    j = -1
                    for c in counties:
                        j += 1
                        if c["name"] == county:
                            ##print ("currently", c)
                            status = county_status[c["abr"]]
                            if not r.imid in c["images"]:
                                c["images"].append(r.imid)
                                c["status"] = status #  XXX
                                ##print ("set status")
                                ##c["generic"] = towns[town].get("generic")
                            ##print ("new", c["images"])
                except:
                    pass
    ##print (counties)
    return counties

def towns_info(spid):
    recs = VascularImage.objects.filter(plant__pk=int(spid)).filter(nr__lt=900).filter(nr__gt=0).exclude(is_verified='no').exclude(is_planted='yes')
    ##recs2 = GenericRecord.objects.filter(plant__pk=int(spid))
    towns = {}
    for r in recs:
        lcid = r.lcid
        if not lcid:
            lcid = r.lcid_temp
        if lcid:
            if lcid.startswith("MA"):
                try:
                    locrec = Location.objects.get(lcid=lcid)
                    town = locrec.town
                    ##print (town)
                    if town:
                        county = Town.objects.get(town=town).county
                        if not town in towns:
                            towns[town] = {"county": county, "imids": [r.imid]}
                            if r.is_planted and r.is_planted == 'yes' :  ## FIXME ? corrected
                                towns[town]["planted"] = [r.imid]
                            else:
                                towns[town]["planted"] = []
                        else:
                            towns[town]["imids"].append(r.imid)
                            if r.is_planted and r.is_planted == 'yes' :
                                towns[town]["planted"].append(r.imid)
                except:
                    print (sys.exc_info())
    ##print (towns)
    return towns


def species_info(sp):
    meta = SpeciesMeta.objects.get(pk=sp.pnid)
    images = VascularImage.objects.filter(plant=sp).filter(nr__lt=100).filter(nr__gt=0).exclude(is_verified='no').exclude(is_planted='yes').count()
    colnames = sp.colnames
    towns = towns_info(sp.pnid)
    counties = counties_info(towns, sp, meta)
    species = {"species": sp, "colnames": sp.colnames, "meta": meta, "images":images, "counties": counties}
    return species

@cache_page(60 * 30)
def get_new_county_records(request):
    data = []
    spp = Name.objects.filter(category='vascular').filter(level='species').exclude(excluded=True).exclude(upper__isnull=True)
    spp = spp.exclude(upper__latname = 'Unidentified').exclude(latname__contains = 'spp.').exclude(latname__contains='unknown')
    spp = spp.exclude(latname__contains='unidentified').exclude(latname__contains='sp.').exclude(latname='sp2')
    ##.exclude=(upper__isnull=True)
    ## did not work.order_by('upper__latname').order_by('latname')
    for sp in spp:
        meta = SpeciesMeta.objects.filter(spid=sp.pk)
        try:
            fid = sp.upper.upper.pk
        except:
            fid = None
        if meta: ## and not 'sp.' in sp.latname and not 'unidentified' in sp.latname:
            meta = meta[0]
            if not meta.introduced =='cultivated': 
                try:
                    species = species_info(sp)
                except:
                    species = {}
                for c in species.get("counties", []):
                    if c.get("images"):
                        if len(c.get("images")) == len(c.get("planted")):
                            pass
                        else:
                            if c.get("status") == '*':
                                ## remove herbaitum sdan
                                ##print ("species", species)
                                latname = "%s %s" % (species.get("species").upper.latname, species.get("species").latname)
                                data.append(
                                    (latname, sp, c.get("abr"), len(c.get("images")), len(c.get("planted")), meta, fid )
                                    )
                                print (species.get("species").upper, species.get("species"), c.get("abr"), "=", c.get("name"), len(c.get("images")), "/", len(c.get("planted")))
    data.sort(key=lambda y: y[0])
    for r in data:
        print (r)
    return render(request, 'photodb/counties_new.htm', locals())
    

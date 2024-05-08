import xml.dom.minidom, os, sys, datetime
from urllib import request
from html.parser import HTMLParser
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from .models import *
from names.models import *
from .models import SpeciesPublished, ImagePublished, VascularImage
from django.utils import timezone

def spp_published_year(request, year=None):
    ## FIXME it works without converting to int
    ## FIXME if str return standard 404
    print ("running spp_published_year for year =", year)
    if not year:
        year = timezone.now().year
        print ("using current year,", year)
    if year < 2005:
        return HttpResponseBadRequest("Invalid year %s" % year)
    elif year > timezone.now().year:
        return HttpResponseBadRequest("Invalid year %s (in a future)" % year)
    elif year in [2012, 2013, 2014, 2015, 2016, 2017]:
        return HttpResponseRedirect("http://salicicola.com/news/%s/" % year)
    elif year < 2022:
        return HttpResponseBadRequest("Years before 2022 are not yet supported at this server")
    generated = timezone.now()
    recs= SpeciesPublished.objects.filter(published__year=year).order_by('plant__longname')
##    html=""
##    for rec in recs:
##        html += "<div>%s</div>" % rec.plant.longname
    print (generated)
    return render(request, 'photodb/news_by_year.htm', locals())
    ##return HttpResponse(html)

def set_current(pubdate="2022-03-14"):
    start = datetime.datetime.now()
    print ("starting", start)
    prepared = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
    for p in prepared:
        imid = p.imid
        print (imid)
        pubs = ImagePublished.objects.filter(imid=imid)
        if pubs:
            print ("existed", pubs[0])
            pubs[0].current = pubdate
            pubs[0].save()
            print ("old", pubs[0], pubs[0].current)
        else:
            pub = ImagePublished()
            pub.imid = imid
            pub.plant = p.plant
            pub.published = pubdate
            pub.current = pubdate
            pub.status = "newest"
            pub.save()
            print ("new", pub, pub.current)
    ends = datetime.datetime.now()
    print ("ends")
    print (ends-start)
 
##        
def set_species_last():
    spp = SpeciesPublished.objects.all()
    for sp in spp:
        sp.last = datetime.datetime(2021, 12, 31)
        sp.save()
        print (sp, sp.published, sp.last)
  
def set_species_current(pubdate="2022-03-14"):
    spp ={}
    newsp = 0
    images = ImagePublished.objects.exclude(current__isnull=True)
    for im in images:
        plant = im.plant
        if not plant:
            print ("fatal error in", im, im.plant)
            continue
        if not plant in spp:
            spp[plant] = None
            try:
                existed = SpeciesPublished.objects.filter(plant=plant)
            except:
                existed = []
                print ("should never happen, but ignore")
            if existed:
                existed[0].current=pubdate
                existed[0].save()
                print ("rec existed", existed[0], existed[0].current)
            else:
                newsp += 1
                rec = SpeciesPublished()
                rec.plant = plant
                rec.ID = plant.pk
                rec.published = pubdate
                rec.last = None
                rec.current = pubdate
                rec.status = "newest"
                rec.save()
                print ("new", plant, rec)
        else:
            ##print ("pass", plant)
            pass
    print ("total spp", len(spp), "new", newsp)
               
##def update_images(pubdate="2022-03-14"):
##    recs = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
##    print ("vascular pub images", len(recs))
##    n = 0
##    for r in recs:
##        imid = r.imid
##        plant = r.plant
##        match = ImagePublished.objects.filter(imid=imid).filter(plant=plant)
##        if match:
##            ##print ("existed", match)
##            pass
##        else:
##            n += 1
##            ##print (n, "missing", r.nr, r)
##            ##raise Exception("debug")
##            ## 123 missing [ was total 35069 ]
##            rec = ImagePublished()
##            rec.plant = plant
##            rec.imid = imid
##            rec.published = None
##            rec.last = None
##            rec.current = pubdate
##            rec.status = "newest?"
##            rec.save()
##            print ("new", n, imid, plant, rec)
##            ## total now 35,192 image published (with dups)
##
##def update_species_current(pubdate="2022-03-14"):
##    spp ={}
##    newsp = 0
##    images = ImagePublished.objects.exclude(current__isnull=True)
##    for im in images:
##        plant = im.plant
##        if not plant:
##            print ("fatal error in", im, im.plant)
##            raise Exception("fatal error, no plant")
##        else:
##            existed = SpeciesPublished.objects.filter(plant=plant)
##            if existed:
##                ##existed[0].current=pubdate
##                ##existed[0].save()
##                ##print ("rec existed", existed[0], existed[0].current)
##                pass
##            else:
##                newsp += 1
##                rec = SpeciesPublished()
##                rec.plant = plant
##                rec.ID = plant.pk
##                rec.published = pubdate
##                rec.last = None
##                rec.current = pubdate
##                rec.status = "newest2"
##                rec.save()
##                print (newsp, "new", plant, rec)
##    ## 9 news total now 2021 instead of 2011

#### final from DB
##def make_news(request, template="photodb/make_news.htm"):
##    pubdate = timezone.now().strftime("%-d %B %Y")
##    previous = datetime.datetime(2021, 12, 31)
##    prev =  previous.strftime("%-d %B %Y")
##    numeric_prev=previous.strftime("%Y%m%d")
##    species = SpeciesPublished.objects.exclude(current__isnull=True)
##    (species_total, photos_total)  =  (len(species), ImagePublished.objects.all().count())
##    print ("total", species_total, photos_total)
##    new_species = species.filter(last__isnull=True).order_by('plant__upper__latname')
##    newsp = 0
##    for sp in new_species:
##        newsp += 1
##        print (newsp, sp.plant.upper.latname, sp.plant.latname)
##
##    print ("total %s photos of %s species" % (species_total, photos_total))
##    return render(request, template, locals())


"""
1 Anisocampium niponicum
2 Calendula officinalis
3 Calycanthus floridus var. glaucus
4 Chrysanthemum ×morifolium
5 Echinacea pallida
6 Gaillardia pulchella
7 Galium album
8 Hieracium kalmii
9 Persicaria coccinea
10 Pinus sylvestris
11 Platycodon grandiflorus
12 Prunus cerasifera
13 Pseudotsuga menziesii ssp. glauca
14 Quercus ×stelloides
15 Salix ×sepulcralis
16 Salix pentandra
17 Salix aurita
18 Viola blanda var. palustriformis
19 ×Sorbaronia fallax
total 2019 photos of 35192 species
"""
## Installed 35192 object(s) from 1 fixture(s)
## Installed 2021 object(s) from 1 fixture(s)

## from getnews:: modified
def new_plants():
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    new_recs = []
    n = 0
    processed = {}
    for r in recs:        
        plant = r.plant
        spid = plant.pnid
        if spid in processed:
            ##print ("processsed", spid)
            pass
        else:
            if SpeciesPublished.objects.filter(ID=spid):
                processed[spid] = True
            else:
                n += 1
                url = "http://localhost:9090/photodb/gallery/view/%s/" % plant.pk
                print (n, "new", plant.upper.latname, plant.latname, url)
                new_recs.append({"plant": plant, "new":True})
                processed[spid] = True
    print ("total", len(new_recs))
    ## total 19

##1 new Crocus ×stellaris http://localhost:9090/photodb/gallery/view/301970/ {{planted or persistent?}}
## --- remved 2 new Unidentified spp. http://localhost:9090/photodb/gallery/view/11980/ ## NOT FRANKENIA! set > 100
##3 new Orthilia secunda http://localhost:9090/photodb/gallery/view/16669/ ## to check ID
##4 new Eranthis hyemalis http://localhost:9090/photodb/gallery/view/302022/ {{ is it cultivated?}}
##5 new Crocus sieberii http://localhost:9090/photodb/gallery/view/16866/ {{planted introduced in WO}}
##6 new Erica x darleyensis http://localhost:9090/photodb/gallery/view/302043/ {{planted}}
##7 new Erica carnea http://localhost:9090/photodb/gallery/view/302042/ {{cultivated}}

## from getnews, to be modified
def make_news(request, template="photodb/make_news.htm", usecache=True):
    start = datetime.datetime.now()
    cache="photodb/CACHE/news_preview.html"
    if os.path.exists(cache) and usecache:
        html = open(cache).read()
        return HttpResponse(html)
    pubdate = timezone.now().strftime("%-d %B %Y")
    ##previous = datetime.datetime(2022, 3, 14) ## XXX
    latest = SpeciesPublished.objects.latest('current')
    previous = latest.current
    prev =  previous.strftime("%-d %B %Y")
    numeric_prev=previous.strftime("%Y%m%d")
    (species_total, photos_total) = get_totals()
    print ("total", species_total, photos_total)
    new_recs = new_photos()
    species_total = get_total_species(new_recs)
    print ("total corrected", species_total, photos_total)
    items = new_recs.items()
    items = list(items)
    items.sort()
    for item in items:
        if not item[1]["existed"]:
            ##print ("adding", item)
            pass
    print ("---------")
##    for item in items:
##        if item[1]["existed"]:
##            pass
##            ##print ("add image", item[0], item[1]["images"])
    print ("total %s photos of %s species" % (species_total, photos_total))
    end = datetime.datetime.now()
    print ("generated", end - start)
    return render(request, template, locals())

def get_total_species(new_recs):
    spp = []
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    for r in recs:
        plant = r.plant
        if plant.pnid in spp:
            pass
        else:
            spp.append(plant.pnid)
    return len(spp)


def get_totals():
    species = {}
    photos = 0
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    for r in recs:
        photos += 1
        spid = r.plant.pnid
        if spid in species:
            pass
        else:
            species[spid] = None
    print ("old version, species", len(species))
    return (len(species), photos)

SPECIAL = {
           "CO.": "from Colorado",
           "FI.": "from Finland",
           "RU.": "from Russia",
           }

## used by news
def new_photos():
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    imnum = 0
    spnum = 0
    addsp = 0
    new_recs = {}
    for r in recs:
        imid = r.imid
        if r.is_planted:
            planted = 1
        else:
            planted = 0
        existed = ImagePublished.objects.filter(imid=imid)
        if existed:
            plant = r.plant
            spid = plant.pnid
### XXX fixing ID = numeric            is_old = SpeciesPublished.objects.filter(ID=spid)
            is_old = SpeciesPublished.objects.filter(plant=plant)
            if not is_old:
                name = "%s %s" % (plant.upper.latname, plant.latname)
                ##new 2023-12-05
                name = plant.longname
                meta = SpeciesMeta.objects.get(spid=spid)
                
                if not name in new_recs:
                    new_recs[name] = {"plant": plant, "existed":bool(is_old),
                                          "newname": True, "meta":meta, "images": [imid], "planted": planted}
                    addsp += 1
                    print ("debug reidentiified", addsp, name, new_recs[name])
                else:
                    new_recs[name]["images"].append(imid)
                    new_recs[name]["planted"] += planted
        else:
            imnum += 1
            plant = r.plant
            spid = plant.pnid
            name = "%s %s" % (plant.upper.latname, plant.latname)
            ## new 2023-12-05
            name= plant.longname
            area = ""
            for lcid_ in SPECIAL:
               if r.locality.lcid.startswith(lcid_):
                   area = SPECIAL[lcid_]
            ## FIXME will use only one rec 
##            if r.locality.lcid.startswith('MA.Nrf'):
##                area = "from Norfolk"
##            else:
##                area=""
            if name in new_recs:
                new_recs[name]["images"].append(imid)
            else:
                is_old = SpeciesPublished.objects.filter(ID=spid)
                try:
                    meta = SpeciesMeta.objects.get(spid=spid)
                except:
                    meta = {}
                new_recs[name] = {"plant": plant, "existed":bool(is_old), "meta":meta, "images": [imid], "planted": planted, "area": area} ## XXX defined by first occ.
                ##debug
                if not is_old:
                    addsp += 1
                    print ("debug", addsp, name, new_recs[name])
##        if planted:
##            raise Exception(planted)
    print ("total", len(new_recs), "added", addsp)
    return new_recs
    ## total 46        
    
def update_images_new(pubdate="2024-02-24"): ## 2023-12-19 2023-10-06 2022-06-26 2023-06-08 2023-08-06
    start = datetime.datetime.now()
    print ("step one", start.isoformat())
    prev_recs = ImagePublished.objects.exclude(current__isnull=True)
    done = 0
    for pub in prev_recs:
        done += 1
        current = pub.current
        latest = current
        current = None
        pub.save()
        print (done, "moved current to latest", pub)
    print ("step two")
    recs = VascularImage.objects.filter(nr__gt=0).filter(nr__lt=100)
    print ("vascular pub images", len(recs))
    n = 0
    for r in recs:
        imid = r.imid
        plant = r.plant
        match = ImagePublished.objects.filter(imid=imid).filter(plant=plant)
        if match:
            match = match[0] ## should be alsways 1 FIXME ?
            match.current = pubdate
            match.save()
            print ("existed", match, "reset current")
        else:
            n += 1
            rec = ImagePublished()
            rec.plant = plant
            rec.imid = imid
            rec.published = pubdate
            rec.last = None
            rec.current = pubdate
            rec.status = "newest!"
            rec.save()
            print ("new", n, imid, plant, rec)
    end = datetime.datetime.now()
    print ("end", end.isoformat())
    print (end-start)
## end 2023-06-11T12:26:22.386564
## 3:21:25.352734
#### end 2023-08-06T12:05:05.341259
#### 3:22:29.378457
## 1:26:51.554263
## end 2023-12-18T12:31:08.750891 3:20:00.896687

def update_species_new(pubdate="2024-02-24"): ## 2022-06-26 ="2022-08-31" 2023-01-15 2023-04-23 2023-06-08
    start = datetime.datetime.now()
    print ("update_species_new", start.isoformat())
    spp ={}
    newsp = 0
    images = ImagePublished.objects.exclude(current__isnull=True)
    for im in images:
        plant = im.plant
        if not plant:
            print ("fatal error in", im, im.plant)
            raise Exception("fatal error, no plant")
        else:
            existed = SpeciesPublished.objects.filter(plant=plant)
            if existed:
                existed.last = existed[0].current
                existed[0].current=pubdate
                existed[0].save()
                print ("rec existed, reset current", existed[0], existed[0].current)
            else:
                newsp += 1
                rec = SpeciesPublished()
                rec.plant = plant
                rec.ID = plant.pk
                rec.published = pubdate
                rec.last = None
                rec.current = pubdate
                rec.status = "newest!!!"
                rec.save()
                print (newsp, "new", plant, rec)
    ## 9 news total now 2021 instead of 2011
    ## extremely slow FIXME
    end = datetime.datetime.now()
    print ("end", end.isoformat())
    print (end-start)
## end 2023-06-11T14:29:28.818963
## 1:32:14.890029


#### XXX 'dict' object has no attribute 'plant'               
##def update_species_newest(pubdate="2022-08-31"): ## 2022-06-27
##    recs = ImagePublished.objects.exclude(current__isnull=True).values('plant')
##    plants = {}
##    for rec in recs:
##        spid = rec.plant.pk
##        if not spid in plants:
##            plants[spid] = rec.plant
##    print ("total %s plants in species published" % len(plants))
##    for spid in plants:
##        plant = plants[spid]
##        existed = SpeciesPublished.objects.filter(plant=plant)
##        if existed:
##            existed.last = existed[0].current
##            existed[0].current=pubdate
##            existed[0].save()
##            print ("rec existed, reset current", existed[0], existed[0].current)
##        else:
##            newsp += 1
##            rec = SpeciesPublished()
##            rec.plant = plant
##            rec.ID = plant.pk
##            rec.published = pubdate
##            rec.last = None
##            rec.current = pubdate
##            rec.status = "newest!"
##            rec.save()
##            print (newsp, "new", plant, rec)
##    finished =   SpeciesPublished.objects.all().count()
##    print ("finished", finished, "species")

def new_unpublished(request, year=0, month=0, day=0, template="photodb/adm_new_photos.htm", days=20):   ## date="2022-03-14"
    if not year or not month or not day:
        today = timezone.now()
        start = today - datetime.timedelta(days)
        print ("set start automatically", start)
    else:
        if int(year) < 100:
            print (year)
            year = 2000 + int(year)
            print ("set year from two digits >", year)
        start = datetime.date(int(year), int(month), int(day))
        print ("start from", start)
    date = start.isoformat()[:10]
    photos = VascularImage.objects.filter(committed__gt=start).filter(nr=100)
    print (len(photos), "photos")
    spp = {}
    for photo in photos:
        plant = photo.plant
        gname = plant.upper.latname
        lname = plant.latname
        latname = "%s %s" % (gname, lname)
        spid = plant.pk
        meta = SpeciesMeta.objects.get(spid=spid)
        if meta.introduced == 'cultivated' or meta.introduced == 'exotic':
            print ("skip")
            continue
        key = ((latname, spid))
        if not key in spp:
            spp[key] = [photo]
        else:
            spp[key].append(photo)
    items = spp.items()
    items = list(items)
    items.sort()
    print (len(items), "sorted spp")
    return render(request, template, locals())
    
def new_published(request, date="2022-10-28"):
    y, m, d = date.split('-')
    start = datetime.date(int(y), int(m), int(d))
    photos = VascularImage.objects.filter(modified__gt=start).filter(nr__lt=100).filter(nr__gt=0)
    ## not committed
    print (len(photos), "published photos")
    # ~ html = "<html><head></head><body><h2>To check: %s published photo records since %s presumably with captions [FIXME]</h2><ol>" % (len(photos), date)
    # ~ print (html)
    # ~ for photo in photos:
        # ~ if not photo.caption.strip() == "***":
            # ~ _html = """<li>[<a target='_blank' href='http://192.168.1.9:9090/photodb/gallery/view/%s/%s'>edit</a>] %s
                # ~ [<a target='_blank' href='http://192.168.1.9:9090/admin/photodb/vascularimage/%s/change/'>in django</a>]</li>\n""" % (photo.plant.pk, photo.imid, photo.caption.strip(), photo.pk)
            # ~ print (_html)
            # ~ html += _html
        # ~ else:
            # ~ if not photo.caption:
                # ~ _html = "<li><a target='_blank' href='http://192.168.1.9:9090/photodb/gallery/view/%s/%s'><i>%s</i></a></li>\n" % (photo.plant.pk, photo.imid, "error: empty caption")
                # ~ print (_html)
                # ~ html += _html
            
    # ~ html += "</ol></body></html>"
    # ~ out = open("published.html", "w")
    # ~ out.write(html)
    # ~ out.close()
    # ~ print (out)
    return render(request, "photodb/new_captions.htm", locals())
    ##return HttpResponse(html)
## end 2023-12-18T14:14:35.745143 1:33:41.776534

    
           
       

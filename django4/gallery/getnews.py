import xml.dom.minidom, os, sys, datetime
from urllib import request
from html.parser import HTMLParser
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound

class NewsParser(HTMLParser):
    spids = []
    imids = []
    fids = []
    def __init__(self):
        #Since Python 3, we need to call the __init__() function  of the parent class
            super().__init__()
            self.reset()

    def handle_starttag(self, tag, attrs):
        ##print("Start tag: ", tag)
        for a in attrs:
            if a[0] == "href":
                value = a[1]
                ##if len(value) > 25 and "salicicola" in value:
                if len(value) > 20 and "/photos/" in value:
                    last = a[1].split('/')[-1]
                    prev = a[1].split('/')[-2]
                    if last.isdigit():
                        self.spids.append(int(last))
                        ##print ("new sp", last)
                    else:
                        self.imids.append(last)
                        print ("new imid for old sp", last)
                    if prev.isdigit():
                        if not int(prev) in self.fids:
                            self.fids.append(int(prev))
### not OK                            
 
    def handle_data(self, data):
        ##print("Here's the data: ", data)
        pass
 
    def handle_endtag(self, tag):
        ##print("End tag: ", tag)
        pass
        
##x  = request.urlopen("http://salicicola.com/news/")
##html = x.read()
##html2 = html.decode("utf-8")
##x.close()
##print (x)
##print (type(html), len(html), "chars")
##parser = NewsParser()
####testParser.feed("<html><head><title>Testing Parser</title></head></html>")
##parser.feed(html2)
##print ("-----------")
##print (parser.spids)

from .models import * ## SpeciesPublished, ImagePublished, VascularImage
from django.utils import timezone

try:
    ##from survey.models import GenericRecord
    from names.models import Name, SpeciesMeta
except:
    print ("should already imported from .", Name, SpeciesMeta)

##for spid in parser.spids:
##    rec = SpeciesPublished(pk=spid)
##    name = Name.objects.get(pk=spid)
##    rec.plant = name
##    rec.published = timezone.datetime(2021, 12, 31)
##    rec.status = "new"
##    rec.save()
##    
##for imid in parser.imids:
##    rec = ImagePublished(imid=imid)
##    name = VascularImage.objects.get(imid=imid).plant
##    rec.plant = name
##    rec.published = timezone.datetime(2021, 12, 31)
##    rec.status = "new"
##    rec.category = "vascular"
##    rec.save()
##for spid in parser.spids:
##    added = 0
##    ##print (spid)
##    plant = Name.objects.get(pk=spid)
##    ##print (plant.fid, plant)
##    if not plant.fid:
##        raise Exception("%s %s" % (spid, plant))
##    xmlname= "%s.xml" % plant.fid
##    print (xmlname)
##    url = "http://salicicola.com/photos/plants/XML/F/%s" % xmlname
##    try:
##        x  = request.urlopen(url)
##        btext = x.read()
##        text = btext.decode("utf-8")
##        x.close()
##        dom = xml.dom.minidom.parseString(text)
##    except:
##        print (sys.exc_info())
##        print ("error with", spid, plant.upper__latname, plant.latname, xmlname, url)
##        raise
##    ##print (dom)
##    for sp in dom.getElementsByTagName("species"):
##        if sp.getAttribute("SPID") == str(spid):
##            ##print ("found sp", sp)
##            for image in sp.getElementsByTagName("image"):
##                href= image.getAttribute('href')
##                imid = os.path.split(href)[-1]
##                imid = os.path.splitext(imid)[1]
##                rec = ImagePublished()
##                rec.imid = imid
##                rec.plant = plant
##                rec.category = "vascular"
##                rec.published = timezone.datetime(2021, 12, 31)
##                rec.status = "new"
##                rec.save()
##                added += 1
##                print (added, "saved", rec)
##            break
##                
##            
##
##url = "http://www.salicicola.com/photos/plantgallery/latnames.html"
##added = 0
##existed = 0
##x  = request.urlopen(url)
##bhtml = x.read()
##print (type(bhtml))
##html = bhtml.decode("utf-8")
##x.close()
##print (type(html))
##parser = NewsParser()
##parser.feed(html)
##print (parser.fids)
##for fid in parser.fids:
##    url = "http://salicicola.com/photos/plants/XML/F/%s.xml" % fid
##    try:
##        x  = request.urlopen(url)
##        btext = x.read()
##        text = btext.decode("utf-8")
##        x.close()
##        dom = xml.dom.minidom.parseString(text)
##        print (dom)
##    except:
##        print (sys.exc_info())
##        print ("error with", spid, plant.upper__latname, plant.latname, xmlname, url)
##        raise
##    for sp in dom.getElementsByTagName("species"):
##        spid = sp.getAttribute("SPID")
##        try:
##            plant = Name.objects.get(pnid = int(spid))
##        except:
##            plant = None
##        for image in sp.getElementsByTagName("image"):
##            href = image.getAttribute('url')
##            print ("url", href)
##            imid = os.path.split(href)[-1]
##            print ("file", imid)
##            imid = os.path.splitext(imid)[0]
##            print ("imid", imid)
##            recs = ImagePublished.objects.filter(imid = imid)
##            print (recs)
##            if recs:
##                rec = recs[0]
##                existed += 1
##                print (existed, imid, "existed", rec)
##            else:
##                rec = ImagePublished()
##                rec.imid = imid
##                if not plant:
##                    rec.note = spid
##                    rec.plant = None
##                else:
##                    rec.plant = plant
##                rec.category = "vascular"
##                rec.published = timezone.datetime(1, 12, 31)
##                rec.status = "old"
##                rec.save()
##                added += 1
##                print (added, "saved", rec)
##                ##raise Exception("saved debug")
        
def set_species():
    ##plants = ImagePublished.objects.distinct('plant') ## DISTINCT ON fields is not supported by this database backend
    spids = []
    recs = ImagePublished.objects.all()
    for r in recs:
        plant = r.plant
        if plant:
            spid = plant.pnid
##            genname = plant.upper.latname
##            latname = plant.latname
            existed = SpeciesPublished.objects.filter(ID=spid)
            if existed:
                print ("registered", existed[0])
            else:
                if spid in spids:
                    print ("just registered", spid)
                    continue
                else:
                    spids.append(spid) ## wrong order, but shoudl work
                    sprec = SpeciesPublished()
                    sprec.ID = spid
                    sprec.plant = plant
                    sprec.published = timezone.datetime(1, 12, 31)
                    sprec.status = "old"
                    sprec.save()

## first version: do not show re-identified species
def new_photos():
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    imnum = 0
    spnum = 0
    addsp = 0
    new_recs = {}
    for r in recs:
        imid = r.imid
        existed = ImagePublished.objects.filter(imid=imid)
        if existed:
            plant = r.plant
            spid = plant.pnid
            is_old = SpeciesPublished.objects.filter(ID=spid)
            if not is_old:
                name = "%s %s" % (plant.upper.latname, plant.latname)
                meta = SpeciesMeta.objects.get(spid=spid)
                if not name in new_recs:
                    new_recs[name] = {"plant": plant, "existed":bool(is_old),
                                          "newname": True, "meta":meta, "images": [imid]}
                    addsp += 1
                    print ("debug reidentiified", addsp, name, new_recs[name])
                else:
                    new_recs[name]["images"].append(imid)
        else:
            imnum += 1
            plant = r.plant
            spid = plant.pnid
            name = "%s %s" % (plant.upper.latname, plant.latname)
            if name in new_recs:
                new_recs[name]["images"].append(imid)
            else:
                is_old = SpeciesPublished.objects.filter(ID=spid)
                try:
                    meta = SpeciesMeta.objects.get(spid=spid)
                except:
                    meta = {}
                new_recs[name] = {"plant": plant, "existed":bool(is_old), "meta":meta, "images": [imid]}
                ##debug
                if not is_old:
                    addsp += 1
                    print ("debug", addsp, name, new_recs[name])
    print ("total", len(new_recs), "added", addsp)
    return new_recs
    ## total 46


## with bug fixed in a version above                    
def new_photos1():
    recs = VascularImage.objects.filter(nr__lt=100).filter(nr__gt=0)
    imnum = 0
    spnum = 0
    new_recs = {}
    for r in recs:
        imid = r.imid
        existed = ImagePublished.objects.filter(imid=imid)
        if existed:
            pass
        else:
            plant = r.plant
            spid = plant.pnid
            name = "%s %s" % (plant.upper.latname, plant.latname)
            if name in new_recs:
                new_recs[name]["images"].append(imid)
            else:
                is_old = SpeciesPublished.objects.filter(ID=spid)
                try:
                    meta = SpeciesMeta.objects.get(spid=spid)
                except:
                    meta = {}
                new_recs[name] = {"plant": plant, "existed":bool(is_old), "meta":meta, "images": [imid]}
                ##debug
                if not is_old:
                    spnum += 1
                    print ("debug", spnum, name, new_recs[name])
    print ("total", len(new_recs))
    return new_recs
    ## total 46

## XXX: bug do not count re-identiified records
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

def old_news(request, yyyymmdd):
    print ("passed", yyyymmdd)
##    if "html" in yyyymmdd:
##        yyyymmdd = yyyymmdd.split('.html')[0]
##        if 'index' in yyyymmdd:
##            yyyymmdd = yyyymmdd.split('index')[1]
##        else:
##            yyyymmdd = yyyymmdd.split('news')[1]
##        print ("making yyyymmdd", yyyymmdd)
    cache = "photodb/CACHE/index%s.html" %  yyyymmdd
    print ("looking for", cache, os.path.exists(cache))
    if os.path.exists(cache):
        html = open(cache).read()
        return HttpResponse(html)
    else:
        return HttpResponseNotFound("wrong date")
    
def make_news(request, template="photodb/make_news.htm"):
    ##pubdate = "1 March 2022"
    cache="photodb/CACHE/news.html"
    if os.path.exists(cache):
        html = open(cache).read()
        return HttpResponse(html)
    pubdate = timezone.now().strftime("%-d %B %Y")
    previous = datetime.datetime(2021, 12, 31)
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
    return render(request, template, locals())
                
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
                print (n, "new", plant.upper.latname, plant.latname)
                new_recs.append({"plant": plant, "new":True})
                processed[spid] = True
    print ("total", len(new_recs))
    ## total 19
"""
1 new Pseudotsuga menziesii ssp. glauca
2 new Calendula officinalis
3 new Hieracium kalmii
4 new Echinacea pallida
5 new Gaillardia pulchella
6 new Quercus ×stelloides
7 new Persicaria coccinea
8 new ×Sorbaronia fallax
9 new Prunus cerasifera
10 new Galium album
11 new Salix ×sepulcralis
12 new Viola blanda var. palustriformis
13 new Calycanthus floridus var. glaucus
14 new Chrysanthemum ×morifolium
15 new Platycodon grandiflorus
16 new Anisocampium niponicum
17 new Pinus sylvestris 
18 new Salix pentandra
19 new Salix aurita
"""
    
                
        

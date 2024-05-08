import sys, os, socket, datetime, xml ##, timezone ## os, sys not in use ?`
from django.conf import settings
from django.shortcuts import render ## _to_response  
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from .models import * ## VascularImage, TidmarshRecord
try:
    from survey.models import GenericRecord
    from names.models import Name, SpeciesMeta
except:
    print ("should already imported from .", Name, SpeciesMeta, GenericRecord)
from .views_nonlegacy import COUNTIES, get_counties
##from .tdm_mapper import *
##from .views_lib import DJANGO_VERSION, PYTHON_VERSION
from .__init__ import VERSION
from .views_lib import DJANGO_VERSION, PYTHON_VERSION
print ("VERSION", VERSION)
TDM_OLD_SPIDS = [6013, 6014, 6017, 6027, 6031, 13196, 6039, 6046, 6063, 13181, 6077, 6088, 6090, 6091, 6100, 6101, 6102, 5365, 6504, 6510, 6519, 6520, 10001, 10003, 10004, 10005, 10006, 10007, 15982, 12772, 15552, 13139, 12552, 12572, 13141, 12646, 10009, 13144, 13145, 15309, 10011, 15321, 13433, 15106, 15034, 10012, 15330, 10013, 14240, 15307, 4747, 15098, 13160, 15327, 10014, 15544, 13158, 15365, 14382, 12496, 13164, 11834, 11786, 15803, 10016, 10017, 13178, 12096, 11984, 14784, 14790, 14414, 13958, 13205, 14422, 13360, 13361, 15795, 12656, 14424, 14954, 16256, 10020, 12086, 15582, 14962, 14380, 10021, 12520, 11696, 15074, 15208, 15150, 10022, 10023, 13259, 13260, 15833, 10024, 15952, 13781, 13262, 15820, 14284, 12618, 11504, 13268, 5159, 10029, 10030, 13273, 10032, 10033, 5187, 10036, 10038, 10041, 10042, 13331, 12848, 13109, 12768, 14858, 10050, 12578, 12304, 14250, 15241, 15056, 14900, 13727, 15801, 15576, 15574, 12084, 14430, 12750, 10051, 12610, 10053, 14432, 14812, 14192, 13194, 10055, 14252, 14186, 13209, 15206, 14735, 12744, 14080, 12612, 13219, 12672, 10057, 10058, 14076, 10059, 15399, 15396, 15253, 14254, 11784, 14256, 13312, 14434, 11656, 15022, 15335, 15393, 5064, 5070, 12494, 13333, 12592, 10060, 15916, 11744, 11814, 13383, 15104, 13535, 15002, 15046, 15032, 14743, 14960, 14987, 15884, 15367, 10064, 13439, 14354, 10066, 10067, 10068, 12564, 10069, 10070, 13960, 7004, 10118, 7167, 7144, 13168, 11838, 12820, 7013, 12570, 13709, 14166, 7165, 7103, 7104, 7122, 7015, 7022, 10103, 7024, 7025, 7163, 12624, 7009, 13501, 7021, 7027, 12810, 12828, 7028, 15956, 7030, 7031, 12818, 7032, 7034, 12172, 7035, 14258, 13129, 13827, 14260, 13130, 14264, 14262, 7162, 15491, 7055, 12728, 7056, 11872, 13172, 10109, 7078, 11594, 12092, 12764, 11800, 11926, 10112, 10111, 13619, 11714, 13613, 13239, 11794, 12176, 12460, 7094, 14438, 10113, 10115, 7161, 13263, 7109, 12298, 11798, 7114, 10116, 15540, 12404, 11684, 4430, 15816, 10119, 11716, 7136, 15401, 13849, 7138, 13391, 13392, 14278, 12816, 11756, 12814, 12812, 13847, 7141, 13396, 11720, 7143, 12292, 4491, 14806, 7105, 7038, 7158, 7007, 7041, 7043, 11672, 4071, 13817, 10101, 13120, 15713, 11738, 14004, 13994, 12476, 3044, 11730, 12682, 16193, 13365, 14608, 14910, 13817, 7045, 2529, 12310, 10104, 16127, 12800, 7117, 7118, 7148, 4141, 10120, 10124, 10125, 13889, 15654, 15517, 11606, 13186, 15626, 13976, 2803, 13385, 15504, 12526, 15273, 11922, 13400, 2830, 10106, 7080, 13789, 11734, 14246, 7093, 15298, 14052, 2938, 13265, 14022, 12826, 7057, 13255, 12626, 7098, 7099, 7100, 10114, 15709, 15624, 7059, 7061, 7134, 15404, 16368, 7064, 7073, 3472, 13201, 7018, 14344, 7054, 7076, 7089, 7090, 13861, 7091, 7107, 7166, 7115, 7120, 15592, 12458, 15580, 7127, 7149, 15550, 7150, 7169, 7151, 10123, 7012, 7036, 14763, 15613, 13835, 7068, 12380, 14308, 7111, 7112, 7113, 13271, 7119, 13843, 13285, 12524, 16570, 12602, 3437, 11636, 10122, 11612, 13410, 13409, 12536, 12506, 7147, 7156, 13583, 2655, 2656, 2657, 2658, 2659, 2665, 2664, 2667, 2670, 13231, 3640, 13298, 12858, 2614, 2642, 11718, 15744, 13280, 13281, 3901, 13287, 13525, 13288, 13291, 13966, 13795, 15530, 3956, 2514, 2515, 12014, 13962, 11748, 15084, 12808, 3486, 3490, 2510, 2913, 12068, 12080, 11626, 3135, 2649, 2650, 2651, 13305, 2526, 3526, 12288, 10129, 11812, 15152, 3512, 3515, 15614, 15629, 13715, 3631, 2691, 12684, 15437, 3966, 3967, 3595, 13833, 13217, 11824, 2841, 13319, 14412, 12038, 14244, 2848, 12098, 13321, 13322, 11678, 14410, 2859, 12642, 13218, 14242, 2871, 12550, 13371, 11726, 13918, 3151, 3152, 15542, 3161, 3125, 2539, 13169, 12884, 13352, 2563, 3571, 12296, 3224, 15965, 3227, 12318, 10128, 13223, 12266, 12268, 3269, 3271, 12588, 3282, 3291, 3293, 3297, 16080, 15717, 3311, 11906, 3317, 3319, 15148, 3325, 3326, 15317, 3330, 13368, 12062, 3351, 4107, 13225, 13229, 4130, 5393, 10133, 14346, 11896, 11341, 11334, 11323, 11338, 11237, 11632, 11889, 11373, 3535, 13106, 3991, 3995, 11990, 13193, 4009, 11818, 13952, 4020, 4025, 15622, 13316, 16294, 4048, 13419, 12504, 13503, 15988, 3622, 12720, 16302, 11592, 3772, 15440, 11740, 15537, 15066, 2616, 12640, 12032, 15632, 15673, 11808, 2953, 13425, 2947, 2954, 2955, 13483, 10146, 3577, 3580, 3581]
print (len(TDM_OLD_SPIDS), "species in 2018 report")
NOTES = {}
##notes = xml.dom.minidom.parse("photodb/tidmarsh/XML/notes.xml")
##for note in notes.getElementsByTagName("note"):
##    spid = int(note.getAttribute("spid"))
##    text = note.firstChild.nodeValue
##    NOTES[spid] = text

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
("NA", "Nantuckett")
    ]            

### FIXME
try:
    LAST_MODIFIED = VascularImage.objects.filter(lcid_temp__startswith="MA.TDM").latest('committed').committed
    modified = VascularImage.objects.filter(lcid_temp__startswith="MA.BDC").latest('committed').committed
    print (LAST_MODIFIED, modified)
    if modified > LAST_MODIFIED:
        LAST_MODIFIED = modified
    ##modified = TidmarshRecord.objects.all().latest('created') XXX text field
    modified = GenericRecord.objects.filter(lcid__startswith="MA.TDM").latest('committed').committed
    print (LAST_MODIFIED, modified)
    if modified > LAST_MODIFIED:
        LAST_MODIFIED = modified
    print (LAST_MODIFIED)
except:
    print ("perhasp empty DB")
    LAST_MODIFIED = modified = datetime.datetime(1, 1, 1)
    print ("set last modified to", LAST_MODIFIED)
    
    
##
debug = True
IMAGES_TDMBOX = {}
IMAGES_TDMBOX_PUB = {}

#### XXX for only alpha test version
def get_authorized(request):
    if request.user.is_authenticated:
        if request.user.username == 'salicarium':
            return True
        else:
            return False
    return False

def tidmarsh_inaturalist(request):
    fname = "photodb/CACHE/tidmarsh_inaturalist.htm"
    if not os.path.exists(fname):
        return HttpResponseRedirect("/photodb/tidmarsh/inaturalist/make/")
    f = open(fname)
    html = f.read()
    f.close()
    return HttpResponse(html)


def tidmarsh_index(request, template="photodb/tidmarsh/tidmarsh_index.htm"):
    authorized = get_authorized(request)
    version = VERSION
    print ("tidmarsh_index", version)
    django_version = DJANGO_VERSION
    python_version = PYTHON_VERSION ## not in use? yet
    return render(request, template, locals())

## more simple than imageview, no ID, name edits, no navigation
def show_image(request, spid, imid, template="photodb/tidmarsh/imgview.htm"):
    authorized = get_authorized(request)
    version = VERSION
    django_version = DJANGO_VERSION
    python_version = PYTHON_VERSION ## not in use? yet
    try:
        name = Name.objects.get(pk=spid)
        print ("show_image, found name", name)
        category =  name.category
        print ("category", category)
        if category == 'vascular':
            manager = VarscularImage.objects
            print (manager)
        elif category == 'nonvascular':
            manager = NonVascularImage.objects
            print (manager)
        elif category == 'animals':
            manager = AnimalImage.objects
            print (manager)
        elif category == 'varia':
            manager = VariaImage.objects
            print (manager)
        elif category == 'other':
            manager = VariaImage.objects
            print (manager)
        else:
            manager = None
            print ("no suitable manager for", category, "manager =", manager)
            return HttpResponseBadRequest("fatal error")
        print ("will use manager", manager)
        irec = manager.filter(plant=name).filter(imid=imid)
        print (irec)
        irec = irec[0]
        print (irec)
        ## palliative  FIXME
        if not authorized and irec.caption.strip() == "***":
            irec.caption = " "
        if authorized:
            if not irec.caption.strip():
                irec.caption = "***" 
    except:
        print ("fatal error", sys.exc_info())
        return HttpResponseBadRequest("Fatal Error")
    return render(request, template, locals())

## FIXME lcid_temp {{alpha version
GPS_NUMS = {}
def get_tdm_images_box():
    global IMAGES_TDMBOX, IMAGES_TDMBOX_PUB, GPS_NUMS
    IMAGES_TDMBOX = {}
    IMAGES_TDMBOX_PUB = {}
    for obj in VascularImage, NonVascularImage, AnimalImage, VariaImage:
        _images = obj.objects.filter(lcid_temp__startswith="MA.TDM").exclude(is_verified='no')
        print (len(_images))
        _images = _images.union(obj.objects.filter(lcid_temp__startswith="MA.BDC.Ply").exclude(is_verified='no'))
        print (len(_images))
        for img in _images:
            if img.gps:
                if GPS_NUMS.get(img.spid):
                    GPS_NUMS[img.spid][img.gps] = None
                else:
                    GPS_NUMS[img.spid] = {img.gps:None}
            if img.nr < 100 and img.nr > 0:
                if IMAGES_TDMBOX_PUB.get(img.spid):
                    IMAGES_TDMBOX_PUB[img.spid] += 1
                else:
                    IMAGES_TDMBOX_PUB[img.spid] = 1                
            if True: ## img.nr < 100 and img.nr > 0:
                if IMAGES_TDMBOX.get(img.spid):
                    IMAGES_TDMBOX[img.spid] += 1
                else:
                    IMAGES_TDMBOX[img.spid] = 1
        print ("so far", len(IMAGES_TDMBOX), "tdm_bbox_images")
    print ("checked cached index of TDM images", len(IMAGES_TDMBOX), "species with images")      
##
##
##EXPLICIT_RECORDS = {}
##
def get_explicit():
    global EXPLICIT_RECORDS, GPS_NUMS
    EXPLICIT_RECORDS = {}
    grecs = GenericRecord.objects.filter(lcid__startswith='MA.TDM').exclude(source='salicicola:plantgallery') ## photos like tidem old unverified
    print (len(grecs))
    for grec in grecs:
        try:
            pnid = grec.plant.pk
            if pnid in EXPLICIT_RECORDS:
                EXPLICIT_RECORDS[pnid].append(grec.GUID) ##
            else:
                EXPLICIT_RECORDS[pnid] = [grec.GUID,]
            if grec.gps:
                if GPS_NUMS.get(pnid):
                    GPS_NUMS[pnid] = {grec.gps:None}
                else:
                    GPS_NUMS[pnid][grec.gps] = None
        except:
            pass
## XXX
##            print ("nearly fatal error")
##            print (sys.exc_info()[0])
##            print (grec, grec.plant, grec.explicit_name)
    ## FIXME Tidmarsh Record
    print ("finished Generic", len(EXPLICIT_RECORDS))
    trecs = TidmarshRecord.objects.all()
    for trec in trecs:
        try:
            pnid = int(trec.plant_id)
            if pnid in EXPLICIT_RECORDS:
                EXPLICIT_RECORDS[pnid].append(trec.pk)
            else:
                EXPLICIT_RECORDS[pnid] = [trec.pk,]
        except:
            print ("nearly fatal error")
            print (sys.exc_info()[0])
            print (trec, trec.plant_id, trec.plantname)            
    print ("finished get_explicit()", len(EXPLICIT_RECORDS))

get_explicit()
print ("initialized EXPLICIT_RECORDS", type(EXPLICIT_RECORDS), len(EXPLICIT_RECORDS), "keys")
##
####get_tdm_images_box()
##
#### ex newflat_checklist_filtered
def checklist(request, lcid="MA.TDM", template="photodb/tidmarsh/checklist_vascular_tidmarsh.htm"):
    authorized = get_authorized(request)
    tcounties = TCOUNTIES
    notes = {}
    cache = "photodb/CACHE/tidmarsh_checklist.html"
    if os.path.exists(cache):
        html = open(cache).read()
        print ("using cached tidmarsh checklist")
        return HttpResponse(html)
    rnotes = ChecklistNote.objects.filter(checklist='Tidmarsh')
    for r in rnotes:
        if r.note:
            spid = r.plant.pk
            text = r.note.strip()
            notes[spid] = text
    print ("made notes from DB", len(notes))
        
    if True: ##not IMAGES_TDMBOX:
        get_tdm_images_box()
    if True: ##not EXPLICIT_RECORDS:
        get_explicit()
    starts = datetime.datetime.now()
    tree = []
    species_found = 0
    images_present = 0
    explicit_records = 0
    for ugid in [301319, 301314, 301309, 301308, 301307, 301299]: ## removing , 299123 UNPLACED
        higher = Name.objects.get(pk=ugid)
        higher.latname = higher.latname.replace('_', ' ')
        print (higher.latname)
        group = {"higher": higher, "fams": []}
        tree.append( group )
        for fam in Name.objects.filter(upper=higher).order_by('latname'):
            print (fam)
            family = {"fam": fam, "genera": [], "images":0, "records":0}
            ##group["fams"].append(family)     
            for gen in Name.objects.filter(upper=fam).order_by('latname'):
                genus = {"genus": gen, "species":[], "images":0, "records":0, "public":0}
                ##family["genera"].append(genus)
                for sp in Name.objects.filter(upper=gen).order_by('latname'):
                    colnames = sp.colnames
                    try:
                        meta = SpeciesMeta.objects.get(pk=sp.pk)
                    except:
                        meta = {}
                    ##images = IMAGES_TDM.get(sp.pnid, 0)
                    images = IMAGES_TDMBOX.get(sp.pnid, 0)
                    published = IMAGES_TDMBOX_PUB.get(sp.pnid, 0)
                    records = EXPLICIT_RECORDS.get(sp.pnid, [])
                    explicit_records += len(records)
                    if records or sp.pnid == 15084:
                        print ("DEBUG: explicit for %s" % sp.pnid, records, len(records), "total", explicit_records, notes.get(sp.pnid, ""))
                    old = sp.pnid in TDM_OLD_SPIDS
                    species = {"species": sp, "colnames": colnames, "meta": meta, "synonyms": [],
                               "images":images, "records": records, "old":old, "public":published,
                               "inat":[], "note":notes.get(sp.pnid, ""), "gps": GPS_NUMS.get(sp.pnid, {})}
                    print ("debug", species, species["gps"])
                    for r in records:
                        if isinstance(r, int):
                            pass
                        elif r.startswith('http'):
                            species["inat"].append(r)
                    for syn in Name.objects.filter(upper=sp).order_by('sal_latname'):
                        synonym = {"syn": syn}
                        species["synonyms"].append(synonym)
                    if images or records:
                        images_present += images
                        species_found += 1
                        genus["species"].append(species) ## filtered
                        genus["images"] += images
                        genus["public"] += published
                        genus["records"] += len(records)
                        counties = COUNTIES.get(sp.pnid, [])
                        if not counties:
                            counties = get_counties(sp.pnid)
                        counties = str(counties).replace("'", "").replace('"', '')
                        species["counties"] = counties
                if genus["images"] or genus["records"]:
                    family["genera"].append(genus)
                    family["images"] += genus["images"]
                    family["records"] += genus["records"]
            if family["images"] or family["records"]:
                group["fams"].append(family)
    generated = datetime.datetime.now()
    delta = generated - starts
    print ("used %s" % (delta))
    secs = round(delta.total_seconds())
    explicit = int((explicit_records / 100)) * 100
    photodb_version = VERSION
    last_modified = LAST_MODIFIED
    return render (request, template, locals())        
##
def getvaria(request, template='photodb/tidmarsh/varia.htm'):
    authorized = get_authorized(request)
    version = VERSION
    django_version = DJANGO_VERSION
    python_version = PYTHON_VERSION ## not in use? yet
    category = 'varia'
    photos = VariaImage.objects.filter(locality__lcid__startswith='MA.TDM')
    for photo in photos:
        print (photo.plant)
    return render (request, template, locals())
    
def getnonvascular(request, template):
    authorized = get_authorized(request)
    print ("running getnonvascular(), authorised", authorized)
    version = VERSION
    django_version = DJANGO_VERSION
    python_version = PYTHON_VERSION ## not in use? yet
    category = 'nonvascular'
    genera = Name.objects.filter(category='nonvascular').filter(level='genus').order_by("latname")
    data = []
    fam = [1, 1, 1, data, data]
    for gen in genera:
        genus = {"latname": gen.latname.replace('_unidentified', ''), "species": [], "photos": 0}
        species = Name.objects.filter(category='nonvascular').filter(level='species').filter(legacy_parent=gen).order_by("latname")
        for sp in species:
            photos = NonVascularImage.objects.filter(locality__lcid__startswith='MA.TDM').filter(plant__pk=sp.pk)
            if photos:
                species = {"genus": gen.latname, "latname": sp.latname, "pk": sp.pk, "imids": []}
                for photo in photos:
                    species["imids"].append(photo.imid)
                genus["photos"] += len(species["imids"])
                genus["species"].append(species)
                print (species)
        if genus["photos"]:
            ##print "relevant genus", genus
            data.append(genus)
            ##fam[3].append(genus)
            ##fam[4].append(genus)
            ##tree[0]["genera"].append(genus)
            ## 2 species name FIXME
    html = """<html><head></head><body><h2>Photos Non Vascular</h2>"""
    for genus in data:
        gname = genus["latname"]
        for species in genus["species"]:
            html += "<div>%s %s</div>" % (gname, species["latname"])
            for photo in species["imids"]:
                html += """<img src="" width="100" height="100"/>"""
## 
##    
##    photos = NonVascularImage.objects.filter(locality__lcid__startswith='MA.TDM').order_by('plant__upper.latname').order_by('plant__latname')
##    html = """<html><head></head><body><h2>Photos Non Vascular</h2>"""
##    for photo in photos:
##        html += """<img width="100" height="100" alt="image" title="%s" src="/static/thum/photos/%s/%s.jpg"/>""" % (photo.plant, photo.imid[:6], photo.imid)
    html += "</body><html>"
    return render (request, template, locals())
##    return HttpResponse (html)
##   
##
##
##
def vertebrates(request, template="photodb/tidmarsh/vertebrates.htm"):
    fams = [
        {"pnid": 11550, "name": "Fishes", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 12110, "name": "Frogs, toads, and salamanders", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 17040, "name": "Snakes", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 17041, "name": "Turtles", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11950, "name": "Birds", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11938, "name": "Mammals", "family":{"latname": "", "genera": [], "photos":0}},
    ]
    for item in fams:
        fam = Name.objects.get(pk=item["pnid"])
        genera = Name.objects.filter(category='animals').filter(level='genus').filter(legacy_parent=fam).order_by("latname")
        item["family"]["latname"] = fam.latname
        family = item["family"]
        for gen in genera:
            species = Name.objects.filter(category='animals').filter(level='species').filter(legacy_parent=gen).order_by("latname")
            genus = {"latname": gen.latname, "species": [], "photos": 0}
            print ("genus", genus)
            for sp in species:
                print ("  test", sp)
                photos = AnimalImage.objects.filter(locality__lcid__startswith='MA.TDM').filter(plant__pk=sp.pk)
                ##print (sp, photos)
                if photos:
                    species = {"genus": gen.latname, "latname": sp.latname, "pk": sp.pk, "imids": []}
                    for photo in photos:
                        species["imids"].append(photo.imid)
                    genus["photos"] += len(species["imids"])
                    genus["species"].append(species)
                    print ("    OK", species)
            if genus["photos"]:
                family["photos"] += genus["photos"]
                family["genera"].append(genus)
    print ("end")
    print (fams)
    return render(request, template, locals())

def invertebrates(request, template="photodb/tidmarsh/invertebrates.htm"):
    fams = [
        {"pnid": 301406, "name": "Freshwater sponge", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 14222, "name": "Seaurchin", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 12112, "name": "Molluscs", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 301474, "name": "Millipeds", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 301410, "name": "Crustacea", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 301409, "name": "Chelicerata: Arachnida", "family":{"latname": "", "genera": [], "photos":0}},

{"pnid": 11564, "name": "Coleoptera", "family":{"latname": "", "genera": [], "photos":0}},
{"pnid": 12120, "name": "Diptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11664, "name": "Hemiptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 301627, "name": "Homoptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 12122, "name": "Hymenoptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11556, "name": "Lepidoptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11850, "name": "Neuroptera", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 11648, "name": "Dragonflies and damselflies", "family":{"latname": "", "genera": [], "photos":0}},
        {"pnid": 12116, "name": "Orthoptera", "family":{"latname": "", "genera": [], "photos":0}},
    ]
    for item in fams:
        fam = Name.objects.get(pk=item["pnid"])
        genera = Name.objects.filter(category='animals').filter(level='genus').filter(legacy_parent=fam).order_by("latname")
        item["family"]["latname"] = fam.latname
        family = item["family"]
        for gen in genera:
            species = Name.objects.filter(category='animals').filter(level='species').filter(legacy_parent=gen).order_by("latname")
            genus = {"latname": gen.latname, "species": [], "photos": 0}
            print ("genus", genus)
            for sp in species:
                print ("  test", sp)
                photos = AnimalImage.objects.filter(locality__lcid__startswith='MA.TDM').filter(plant__pk=sp.pk)
                ##print (sp, photos)
                if photos:
                    species = {"genus": gen.latname, "latname": sp.latname, "pk": sp.pk, "imids": []}
                    for photo in photos:
                        species["imids"].append(photo.imid)
                    genus["photos"] += len(species["imids"])
                    genus["species"].append(species)
                    print ("    OK", species)
            if genus["photos"]:
                family["photos"] += genus["photos"]
                family["genera"].append(genus)
    print ("end")
    print (fams)
    return render(request, template, locals())
##
def tidmarsh_search(request, template):
    if not request.GET:
        return render(request, template)
    else:
        qs = request.META.get('QUERY_STRING')
        print (qs)
        return HttpResponseRedirect("/photodb/search/?%s" % qs)

## from old tidmarsh module:: views
def introducing(request):
    return render(request, "photodb/tidmarsh/tidmarsh_adding.htm")


def unwanted(request):
    dom = xml.dom.minidom.parse("photodb/tidmarsh/XML/unwanted.xml")
    print (dom)
    recs = []
    for record in dom.getElementsByTagName("record"):
        try:
            rec = {}
            rec["spid"] = record.getElementsByTagName("spid")[0].firstChild.nodeValue
            rec["latname"] = record.getElementsByTagName("latname")[0].firstChild.nodeValue
            rec["colname"] = record.getElementsByTagName("colname")[0].firstChild.nodeValue
            try:
                notes = record.getElementsByTagName("notes")[0].firstChild.nodeValue
                rec["notes"] = notes
            except:
                pass
            print (rec)
            recs.append(rec)
        except:
            print ("skip empty record", record.toxml())
    return render(request, "photodb/tidmarsh/tidmarsh_unwanted.htm", locals())
##
from .nogis_lib import *
from .nogis_lib import _plants_box_count
##
def tidmarsh_bbox(request, width=100, height=100, lat=41.9014, lon=-70.57052):
    c = get_all_params(request)
    ## migrating to python 3 :: replace request.REQUEST to request.GET
    if not "width" in request.GET:
        c["width"] = width
    else:
        c["width"] = int(request.GET["width"])
    if not "height" in request.GET:
        c["height"] = height
    else:
        c["height"] = int(request.GET["height"])
    if not "lat" in request.GET:
        c["lat"] = lat
    else:
        c["lat"] = float(request.GET["lat"])
    if not "lon" in request.GET:
        c["lon"] = lon
    else:
        c["lon"] = float(request.GET["lon"])
    c["start"] = (c["lon"], c["lat"])
    c["times"] = 1
    c["map_zoom"] = 15
    if c.get("show_records", None):
        c["points"] = get_all_dots()
        if c["points"]:
            c["total_photos"] = sum(c["points"].values()) 
            c["total_dots"] = len(c["points"])
        else:
            c["total_photos"] = 0 
            c["total_dots"] = 0          
    else:
        c["points"] = {}   
    found = {}
    counted = []
    lastfound = []
    boxes = [] 
    _width = c["width"]
    _height = c["height"]
    for i in range(c["times"]):
        (found, boxes, stub) = _plants_box_count(c["lat"], c["lon"], _width, _height, found, boxes)
        _counted = len(found)
        counted.append(_counted)
        _width += c["width"]
        _height += c["height"]
    print ("FOUND", found)
    box = boxes[-1]
    lastfound = list(stub)
    lastfound.sort()
    c["found"] = found
    print ("debug", found)
    c["box"] = box
    c["boxes"] = boxes
    c["counted"] = counted
    c["lastfound"] = lastfound
    c["square_meters"] = (_width - c["width"]) * (_height - c["height"])
    c["all_species"] = get_species_from_found(found)
    c["version"] = VERSION
    c["data_modified"] = data_modified
    return render(request, 'photodb/tidmarsh/flora_tidmarsh.htm', c)
##
#### test URL=http://localhost:9090/photodb/tidmarsh/map/bbox/?lat=41.91629&lon=-70.570013&width=50&height=50
#### must show Cabomba from iNaturalist {9 species}
####def index(request, template="tidmarsh_index.htm"):
##def monitor_index(request, template="tidmarsh_index.htm"):
##    version = VERSION
##    django_version = DJANGO_VERSION
##    try:
##        user = request.user
##        ##print dir(user)
##        if user.is_authenticated:
##            uid = user.username
##            user = User.objects.get(username = uid)
##            prof = Profile.objects.get(user = user)
##            mask = prof.phidcode
##            mode="owner"
##            if 'admin' in uid:
##                mode='admin'
##        else:
##            uid = 'guest'
##            mask = 'guest'
##            mode='guest'
##        records = get_records(uid)
##        print (user)
##        print ("UID", uid)
##        raise (IOError)
##        return render(request, template, locals())
##    except:
##        version = "0.1 (revno 25+) draft"
##        version = VERSION
##        print ('in tidmarsh.views.index: intentionally raised IOError temporarily', sys.exc_info())
##        ##raise
##        return render(request, template, locals())

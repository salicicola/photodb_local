""" copied and modified from photos.views """
from django.shortcuts import render
import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import *
from .__init__ import VERSION
from django.template.loader import render_to_string
import django
import urllib


REVISION = "#132+ 2021-10-04" ## 
DOMAIN = "http://172.104.19.75" ## debug/draft keeping even thums at main server
AREA = "Tidmarsh Farms / Sanctuary and Vicinity"
EDIT_DOMAIN = "http://192.168.1.9:9090/photodb/"  ## was 8080
python_version = sys.version.split()[0]
django_version = django.get_version()

PYTHON_VERSION = sys.version.split()[0]
DJANGO_VERSION = django.get_version()
recordset = None
tree = []
total_photos = 0
total_species = 0  
HIGHER_ABBR = {"dicots": 1, "monocots": 2, "conifers":3, "ferns": 4, "mosses": 5, "unnamed": 6,
               "fungi": 7, "animals":8,
               "insects":9, "sawflies":10, "varia": 11, "algae": 12, "arthropods": 13, "humans":14,
               "liverworts": 15, "lichens": 16, "chlorophyta": 17, "rhodophyta": 18, "ochrophyta":19,
               "all":-1, "vascular": (1,4),
    }

def in_db(request, phid):
    for Categorized in VascularImage, NonVascularImage, AnimalImage, VariaImage:
        recs = Categorized.objects.filter(phid=phid)
        if recs:
            print ("db", recs)
            if not request:
                return True
            else:
                return HttpResponse("OK")
    print ("no such %s in DB" % phid)
    if not request:
        return False
    else:
        return HttpResponseBadRequest("not found in DB")

def get_editdomain():
    edit_domain = EDIT_DOMAIN
    ## XXX bad in linode
    return None
    try:
        code = urllib.request.urlopen(EDIT_DOMAIN).getcode()
        if code == 200:
            print (edit_domain, "available")
        else:
            print (edit_domain, "NOT AVAILABLE")
            edit_domain = None
    except:
        print (sys.exc_info())
        print ("network is not available?")
        edit_domain = None
    return edit_domain

def get_area(lcid):
    if lcid:
        if 'BBR' in lcid:
            area = 'Beaver Brook Reservation (Waltham, Belmont)'
        elif 'BHR' in lcid:
            area = 'Blue Hills Reservation'
        elif 'MSF' in lcid:
            area = 'Miles Standish State Park'
        elif lcid == 'TDM':
            area = 'Tidmarsh Farms / Sanctuary and Vicinity'
        elif 'TDM.' in lcid:
            area = 'Tidmarsh Farms / Sanctuary'
        elif lcid == 'MA' or lcid == 'MA.':
            area = "Massachusetts"
        else:
            area = lcid
    else:
        area = ""
    return area

##def process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos):
##    print ("calling process_genus for ", grp, fam, genus)
##    if genus.latname:
##        gen = [genus.latname.replace('_', ' '), genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
##    elif genus.sal_latname:
##        gen = [genus.sal_latname.replace('_', ' '), genus.colnames, genus.sal_authors, genus.pnid, [], 0, "genus"]
##    else:
##        gen = ["", genus.colnames, genus.authors, genus.pnid, [], 0, "genus"]
##    print ("processing", gen)
##    for species in Name4.objects.filter(legacy_parent=genus).order_by("sal_latname"):
##        ##print ("processing species", species)
##        table = get_image_table(species)
##        print ("got", table)
##        all_photos = table.objects.exclude(lcid__isnull=True).exclude(lcid__exact='').filter(spid = species.pnid)
##        print ("got %s photos" % len(all_photos))
##        ##photos = VascularImage.objects.exclude(lcid__isnull=True).exclude(lcid__exact='').filter(spid = species.pnid)
##        ##print ("found %s photos" % len(photos))
##        if not lcid:
##            if exclude:
##                photos = all_photos.filter(nr__gt=0).exclude(lcid__contains='MA').order_by("nr")
##            else:
##                photos = all_photos.filter(nr__gt=0).order_by("nr")
##        else:
##            if exclude:
##                photos = all_photos.filter(nr__gt=0).exclude(lcid__contains=lcid).order_by("nr")
##            else:
##                photos = all_photos.filter(nr__gt=0).filter(lcid__contains=lcid).order_by("nr")
##                
##        if not lcid:
##            if exclude:
##                removed = all_photos.filter(nr__lte=0).exclude(lcid__contains='MA').order_by("nr")
##            else:
##                removed = all_photos.filter(nr__lte=0).order_by("nr")
##        else:
##            if exclude:
##                removed = all_photos.filter(nr__lte=0).exclude(lcid__contains=lcid).order_by("nr")
##            else:
##                removed = all_photos.filter(nr__lte=0).filter(lcid__contains=lcid).order_by("nr")
##
##                
##        print ("PATCH::: final %s photos %s removed" % (len(photos), len(removed)))
##        try:
##            meta = PlantMeta.objects.get(pk=species.pnid)
##        except:
##            meta = "[]"
##        ## XXX 2021-10-23
##        if photos:
##           syns = Name4.objects.filter(legacy_parent=species).order_by('sal_latname')
##           spec = [species.sal_latname, species.colnames, species.sal_authors, species.pnid,
##                   syns, len(photos), photos, meta, removed]
##           gen[5] += len(photos)
##           fam[5] += len(photos)
##           grp[5] += len(photos)
##           gen[4].append(spec)
##           total_photos += len(photos)
##           total_species += 1
##           ##print ("debug", gen[4], total_species, total_photos)
##    return (gen, total_species, total_photos)
##
def get_image_table(species):
    if species.category == 'vascular':
        print ("will use VascularImage")
        return VascularImage
    elif species.category == 'nonvascular':
        print ("will use NonVascularImage")
        return NonVascularImage
    elif species.category == 'animals':
        print ("will use AnimalImage")
        return  AnimalImage
    else:
        print ("will use VariaImage")
        return VariaImage
##
#### main one
##def view_photo_records(request, pnid=None, lcid=None, exclude=None, thumbs=True, view="gallery", template="photodb/photos/gallery_index.htm", save=False, legacy=True):
####    if not pnid and not save and os.path.exists("photos/cache/index_list.html"):
####        print ("will use cache, since not enforced")
####        return view_cached_list(request)
####    if request.GET and request.GET.get('sql_edit'):
####        sql_edit = True
####    ## is it relevant?
##    debug_starts = datetime.datetime.now()
##    ##max_thums = 500
##    max_thums = 5000  ## not in use anywere below anyway ? why do not shoe ? XXX
##    area = get_area(lcid)    
##    edit_domain = get_editdomain()
##    total_species, total_photos = 0, 0
##    gnum = 0
##    tree = []
##    version = VERSION
##    python_version = PYTHON_VERSION
##    django_version = DJANGO_VERSION
##    domain = DOMAIN
##    revision = REVISION.split()[0]
##    if pnid:
##        ##root_name = Name4.objects.get(pnid=pnid)
##        root_name = Name4.objects.get(pnid=pnid)
##        rank = root_name.rank
##        print ("view_photo_records() got", root_name, rank)
##        ## not yet XXX updated
##        if rank == 'group':
##            group = root_name
##            grp = [group.latname.replace('_', ' '), group.colnames, group.authors, group.pnid, [], 0]
##            print ("pass", grp)
##            tree.append(grp)
##            for family in Name4.objects.filter(legacy_parent=group).order_by('sal_latname'): ## .order_by("sal_latname")
##                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
##                print ("pass fam", fam)
##                grp[4].append(fam)
##                for genus in Name4.objects.filter(legacy_parent=family).order_by("latname"):
##                    ##print ("pass genus", genus)
##                    gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos)
##                    fam[4].append(gen) ## XXX integer
##        elif rank == 'family':
##            family = root_name
##            group = root_name.legacy_parent
##            grp = ["", "", "", group.pnid, [], 0]
##            tree.append(grp)
##            try:
##                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
##            except:
##                fam = [family.sal_latname.replace('_', ' '), family.colnames, family.sal_authors, family.pnid, [], 0]
##            print ("pass fam", fam)
##            grp[4].append(fam)
##            for genus in Name4.objects.filter(legacy_parent=family).order_by("latname"):
##                print ("pass genus", genus)
##                gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos)
##                fam[4].append(gen) ## XXX integer
##        elif rank == 'genus':
##            genus = root_name
##            family = genus.parent
##            if not family:
##                family = genus.legacy_parent
##            group = family.parent
##            if not group:
##                group = family.legacy_parent
##            grp = ["", "", "", group.pnid, [], 0]
##            tree.append(grp)
##            fam = ["", "", "", family.pnid, [], 0]
##            grp[4].append(fam)
##            gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos)
##            fam[4].append(gen)
##        elif rank == 'species':
##            species = root_name
##            print ("doing species", species.category)
##            genus = root_name.parent
##            family = genus.parent
##            group = family.parent
##            grp = ["", "", "", group.pnid, [], 0]
##            tree.append(grp)
##            fam = ["", "", "", family.pnid, [], 0]
##            grp[4].append(fam)
##            gen = [genus.sal_latname.replace('_', ' '), genus.colnames, genus.sal_authors, genus.pnid, [], 0, "genus"]
##            fam[4].append(gen)
##            table = get_image_table(species)
##            print ("using", table, "gen", genus)
##            photos = table.objects.filter(nr__gte=0).filter(spid = species.pnid).order_by("nr")
##            removed = table.objects.filter(nr__lte=0).filter(spid = species.pnid)
##            print ('removed', removed, "photos")
##            ### FIXME 2021-10-23
##            try:
##                meta = PlantMeta.objects.get(pk=species.pnid)
##            except:
##                meta = "?" + str(sys.exc_info()) ### XXX
##            ##meta = "XXX"
##            print ("got %s photos" % len(photos))
##            ##photos = VascularImage.objects.filter(spid = species.pnid)
##            if legacy:
##                syns = Name4.objects.filter(legacy_parent=species).order_by('sal_latname') ##.order_by("latname")
##                spec = [species.sal_latname, species.colnames, species.sal_authors, species.pnid,
##                   syns, len(photos), photos, meta, removed]
##            else:
##                syns = Name4.objects.filter(parent=species).order_by('latname') ##.order_by("latname")
##                spec = [species.latname, species.colnames, species.authors, species.pnid,
##                   syns, len(photos), photos, meta, removed]
##            gen[4].append(spec)
##            gen[5] += len(photos)
##            fam[5] += len(photos)
##            grp[5] += len(photos)
##            total_species += 1
##            total_photos += len(photos)
##            print (tree)
##        else:
##            return HttpResponseBadRequest("illegal %s" % pnid)
##    else:
##        ## too much time: to cache it
##        start =1
##        ends = 25
##        for group in Name4.objects.filter(rank='group').order_by('pnid'):
##            ## repeated from above FIXME
##            grp = [group.latname.replace('_', ' '), group.colnames, group.authors, group.pnid, [], 0]
##            print ("pass", grp)
##            tree.append(grp)
##            for family in Name4.objects.filter(legacy_parent=group).order_by("latname"):
##                fam = [family.latname.replace('_', ' '), family.colnames, family.authors, family.pnid, [], 0]
##                print ("pass fam", fam)
##                grp[4].append(fam)
##                for genus in Name4.objects.filter(legacy_parent=family).order_by("latname"):
##                    ##print ("pass genus", genus)
##                    gen, total_species, total_photos = process_genus(grp, fam, genus, lcid, exclude, total_species, total_photos)
##                    fam[4].append(gen) ## XXX integer
##        if save:            
##            debug_ends = datetime.datetime.now()
##            print (debug_ends, "will start rendering")
##            time_spent = debug_ends - debug_starts
##            content = render_to_string(template, locals())
##            with open('photos/cache/index_list.html', 'w') as static_file:
##                static_file.write(content)
##            print ("debugging performance") ### 0:01:14.787926
##            print ("spent time", time_spent)
##            return view_cached_list(request)
##    debug_ends = datetime.datetime.now()
##    print ("debugging performance") ### 0:01:14.787926
##    time_spent = debug_ends - debug_starts
##    print ("spent", time_spent)
##    return render(request, template, locals())

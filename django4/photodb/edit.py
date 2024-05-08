import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
try:
    from names.models import Name, SpeciesMeta
except:
    print ("cannot import Name and SpeciesMeta from names, should have them in .models")

from photodb.models import *


### FIXME
### NOT CHECKED THAT ALL NEEDED

## was in views

##def update_legacy(POST, legrec):
##    if legrec:
##        changed = False
##        if not legrec.sal_latname == POST.get("sal_latname"):
##            changed = True
##            legrec.sal_latname = POST.get("sal_latname")
##        if not legrec.sal_authors == POST.get("sal_authors"):
##            changed = True
##            legrec.sal_authors = POST.get("sal_authors")
##        if changed:
##            legrec.save()
##            print ("saved legacy record", legrec)
##            return True
##        else:
##            return False
##    else:
##        return False
        


##def update_meta(POST):
##    spid = POST.get("spid", "")
##    if not spid:
##        return "no meta data"
##    try:
##        mrec = SpeciesMeta.objects.get(pk=int(spid))
##        print ("existed meta record", mrec)
##        changed = False
##    except:
##        mrec = SpeciesMeta(spid=int(spid))
##        print (str(sys.exc_info()))
##        print ("new meta record", mrec)
##        changed = True
##    print ("passed", POST)
##    for fname in "rank initial_name evergreen introduced invasive invasive_mipag origin rare evergreen".split(): ### XXX
##        if not POST.get(fname) == mrec.__dict__.get(fname): ## POST.get(fname) and  ## FIXME to allow set None
##            mrec.__dict__[fname] = POST.get(fname, "")
##            changed = True
##            print ("set", mrec.__dict__.get(fname))
####    ## ignore su_ba
####    if POST.get("initial_name") and not POST.get("initial_rank") == mrec.initial_rank:
####        mrec.rank = POST.get("initial_name")
####        changed = True
####        print ("set", mrec)
####    if POST.get("introduced") and not POST.get("introduced") == mrec.introduced:
####        mrec.rank = POST.get("introduced")
####        changed = True
####        print ("set", mrec)
####    if POST.get("invasive") and not POST.get("invasive") == mrec.invasive:
####        mrec.rank = POST.get("invasive")
####        changed = True
####        print ("set", mrec)
##        
##    if changed:
##        mrec.save()
##        return ("meta created/updated: %s" % mrec.updated)
##    else:
##        return ("no change in meta record")


##@login_required(login_url='/admin/login/')
##def edit_name_mini(request, pnid):
##    print ("start edit_name_mini", pnid)
##    print ("newer version: using two tables")
##    req_dict = request.GET
##    if not req_dict:
##        req_dict = request.POST
##    if not request.GET and not request.POST:
##        try:
##            rec = Name.objects.get(pk=int(pnid))
##        except:
##            return HttpResponseBadRequest(str(sys.exc_info()))
##        famname = genname = ""
##        try:
##            genname = rec.legacy_parent.latname
##        except:
##            pass
##        if not genname:
##            try:
##                genname = rec.upper.latname
##            except:
##                pass
##        try:
##            famname = rec.legacy_parent.legacy_parent.sal_latname
##        except:
##            pass
##        if not famname:
##            try:
##                famname = rec.legacy_parent.legacy_parent.latname
##            except:
##                pass
##            if not famname:
##                try:
##                    famname= rec.upper.upper.latname
##                except:
##                    famname = ""
##        meta = SpeciesMeta.objects.filter(spid=pnid)
##        if meta:
##            meta = meta[0]
##        else:
##            meta = SpeciesMeta(spid=pnid)
##            meta.initial_name = "%s %s" % (genname, rec.latname)
##            meta.su_ba = "yes"
##            meta.rank="species"
##            meta.evergreen = ""
##            meta.origin = ""
##            meta.rare = ""
##            ## status, counties
##        print ("meta", meta)
##
##    else:
##        rec = Name.objects.get(pk=int(req_dict["pnid"]))
##        try:
##            legrec = LegacyName.objects.get(pk=int(req_dict["pnid"]))
##        except:
##            legrec = {}
##        if request.POST :
##            POST = request.POST
##        else:
##            POST = request.GET
##        meta_changed = update_meta(POST)
##        legacy_changed = update_legacy(POST, legrec)
##        changed = ""
##        if req_dict.get("parent_null", "") == "on":
##            print("MUST SET PARENT TO NONE")
##            rec.parent = None
##            ##rec.latname = ""
##            ##rec.authors = ""
##            changed += " SET PARENT TO NONE, "
##        if not rec.latname == req_dict.get("latname", ""):
##            rec.latname = req_dict.get("latname", "").strip()
##            changed += req_dict.get("latname", "") + ","
##        if not rec.sal_latname == req_dict.get("sal_latname", ""):
##            rec.sal_latname = req_dict.get("sal_latname", "").strip()
##            changed += req_dict.get("sal_latname", "") + ","
##        if not rec.sal_authors == req_dict.get("sal_authors", ""):
##            rec.sal_authors = req_dict.get("sal_authors", "").strip()
##            changed += req_dict.get("sal_authors", "") + ","
##        if not rec.authors == req_dict.get("authors", ""):
##            rec.authors = req_dict.get("authors", "").strip()
##            changed += req_dict.get("authors", "") + ","
##        if not rec.colnames == req_dict.get("colnames", ""):
##            rec.colnames = req_dict.get("colnames", "").strip()
##            changed += req_dict.get("colnames", "") + ","
##        if not rec.note == req_dict.get("note", ""):
##            rec.note = req_dict.get("note", "").strip()
##            changed += req_dict.get("note", "") + ","
##        if not rec.caption == req_dict.get("caption", ""):
##            rec.caption = req_dict.get("caption", "").strip()
##            changed += req_dict.get("caption", "") + ","
##
##        if changed:
##            rec.uid = req_dict.get("uid", "") ## modified_by
##            changed = "modified by %s: %s" % (rec.uid, changed[:-1])
##            rec.save()
##            return HttpResponse("changed: " + changed + "\n" + meta_changed + "\nlegacy updated ? " + str(legacy_changed), "text/plain")
##        else:
##            return HttpResponse("not changed: "  + str(rec)+ "\n" + meta_changed, "text/plain")
##    return render(request, "photodb/form_namemini.htm", locals())



##def add_syn(request, spid):
##    r = Name()
##    parent = Name.objects.get(pk=spid)
##    r.level="synonym"
##    r.parent = parent
##    r.upper = parent
##    r.legacy_parent = parent
##    r.latname = parent.upper.latname + " ?"
##    r.authors = "XXX"
##    r.sal_authors = "XXX"
##    r.sal_latname = "XXX"
##    r.save()
##    pnid = r.pk
##    print ("saved", r)
##    return HttpResponseRedirect("/photodb/edit/name/%s/" % pnid)

##def delete_name_legacy_name(request, pnid):
##    name = Name.objects.get(pk=pnid)
#### no more Legacy as a standalone table
####    try:
####        legacy = LegacyName.objects.get(pk=pnid)
####    except:
####        legacy = None
####    if legacy:
####        legacy.delete()
##    name.delete()
##    return HttpResponse("deleted: %s" % (name)) ## , legacy  & %s

def check_suffix(rec, suffix, url, category=""):
    print ("testing suffix", suffix, rec, category)
    print ("was url", url)
    if url.endswith("/"):
        url = url[:-1]
        print ("normalized", url)
        imid = os.path.split(url)[1]
        imid = os.path.splitext(imid)[0]
        old_suffix = imid[17:]
        print (rec.imid, len(rec.imid), imid, old_suffix, "new", suffix)
        if not rec.imid == imid:
            raise Exception("system error")
        if old_suffix == suffix:
            print ("nothing to do")
            return HttpResponseRedirect(url)
        else:
            print ("should copy record and set nr in old one to -100, but old rec dissapeared because imid is not a pk")
            new_imid = imid[:17] + suffix
            print ("new record should have imid", new_imid)
            rec.imid = new_imid
            rec.save()
            new_url = os.path.split(url)[0] + "/" + new_imid + "/"
            print (new_url)
##            ## old rec dissapeared entirely because imid is not a pk
##            print ("dup record", rec)
##            
##            old_rec = VariaImage.objects.filter(imid=imid).filter(spid=int(rec.pnid))
##            print ("old", old_rec)
##            old_rec.nr = -100
##            ord_rec.save()
##            print ("duplicated and set")
            return HttpResponseRedirect(new_url)
    

def set_remove(rec, url):
    old = rec.nr
    rec.nr = -old ## -100
    rec.save()
    print ("saved record", rec, "with nr", rec.nr)
    return HttpResponseRedirect(url)
    ## the form is yet accessible but not visiblle in thumbview, and can be accessed by navigation from imageview FIXME
    ##raise Exception("debug")

## not yet changing extension location, date ... only caption, nr ...
def CaptionEditor(request):
    changed = False
    pars = request.POST
    if not pars:
        pars = request.GET
    pnid = int(pars.get("pnid"))
    image_id = pars.get("image_id")
    image_id = os.path.split(image_id)[1]
    imid = os.path.splitext(image_id)[0]
    name = Name.objects.get(pk=pnid)
    ##print (pars)
    if pars.get("append") == "on":
        print ("dup mode: will redirect to duplicate() with" + "spid, oldimid, newimid:", pnid, imid, pars.get("image_id_suffix"))
        return duplicate(request, pnid, imid, pars.get("image_id_suffix"))
    print ("matched ID", name)
    if name.category == "vascular":
        rec = VascularImage.objects.filter(imid=imid).filter(plant__pnid=int(pnid))
    elif name.category == "nonvascular":
        rec = NonVascularImage.objects.filter(imid=imid).filter(plant__pnid=int(pnid))
    elif name.category == "animals":
        rec = AnimalImage.objects.filter(imid=imid).filter(plant__pnid=int(pnid))
    else:
        rec = VariaImage.objects.filter(imid=imid).filter(plant__pnid=int(pnid)) 
    if len(rec) == 1:
        rec = rec[0]
        print (rec)
    else:
        raise VariaImage.DoesNotExist("should never happen")
    url = pars.get("url")
    role = pars.get("role") ## FIXME not yet in use
    fname = pars.get("file") ## FIXME  not yet in use
    mode = pars.get("mode") ## FIXME  not yet in use
    toremove = pars.get("arhive") ## FIXME no field
    if not toremove or toremove == '0':
        pass
    else:
        print("will mark as removed", toremove, type(toremove))
        return set_remove(rec, url) ## will not process further
    caption = pars.get("editcaption")
    if role == 'locality':
        if rec.location == caption:
            print ("using role locality, no changes found", rec.location, caption)
        else:
            print ("using role locality", rec.location, "!=", caption)
            rec.location = caption
            changed = True
    elif role == 'date':
        if rec.date == caption:
            print ("using role date, no changes found", rec.date, caption)
        else:
            print ("using role date", rec.date, "!=", caption)
            rec.date = caption
            changed = True        
    else:
        print ("using role", role)
        old_caption = rec.caption
        if not old_caption == caption:
            rec.caption = caption
            changed = True
    image_number = float(pars.get("image_number")) ## FIXME why +
    print ("nr", image_number, type(image_number))
    if not image_number == rec.nr:
        rec.nr = image_number
        changed = True
    phid = pars.get("photo_id") ## should never be changed
    suffix = pars.get("image_id_suffix") ## XXX > it will be new reco ### not shown XXX
    print ("suffix", suffix) ## suffix None though actually s it is image_id_suffix not suffix
    ##
    ##
    ##
    lcid = pars.get("LCID")
    if rec.locality.lcid == lcid:
        print ("no change in lcid", lcid)
    else:
        try:
            locality = Location.objects.get(pk=lcid)
            rec.locality = locality
            ##rec.lcid = lcid
            print ("changed lcid XXX should change location") ### XXX
            changed = True
        except:
            return HttpResponseBadRequest("cannot assign location")
    if not pars.get("INID") == rec.inid:
        rec.inid = pars.get("INID")
        print ("set new INID", rec.inid)
        changed = True
    verified = pars.get("verified")
    print ("verified", verified)
    oldverified = rec.is_verified
    if verified == rec.is_verified:
        print ("verified not changed", rec.is_verified, verified)
        pass
    else:
        rec.is_verified = verified
        changed = True
## added fields    
    herb_id = pars.get("herb_id")
    if not herb_id == rec.herb_id: ## XXX no such field
       rec.herb_id = herb_id
       changed = True   
    if not pars.get("notes") == rec.notes:
        rec.notes = pars.get("notes")
        changed = True
    ## no notes
    if pars.get("tags"):
        rec.tags = pars.get("tags")
        changed = True
    ## correcting
    is_planted = pars.get("is_planted")
    if rec.is_planted == is_planted:
        print ("no changes in is _planted")
    else:
        rec.is_planted = is_planted
        changed = True
    ## XXX: to change all None to "" if string    
    print (locals())
    if changed:
        rec.modified = timezone.now()
        print (rec.modified)
        rec.save()
        print ("record saved, will reload by url", url)
    print ("debug", "archive", pars.get("arhive"), "duplicate", pars.get("append"))
    print ("should check yet if changed suffix, check_suffix(rec, suffix)", rec, suffix, url)
    ## as revno 87:
    ## FIXME not yet planted
    ## FIXME not working yet herb_id, notes, tags, duplicate [on]
    ## FIXME partially "remove (arhive)", "verified" (verified saved but not shown)
    ## fixed date
    return check_suffix(rec, suffix, url, name.category)
    ##return HttpResponseRedirect(url)

## testging lcid original MA.Nrf.Wey.200614700 = Weymouth

## from admin_images2
## changed from legacy to new classification : changed legacy_parent to upper
## using longnames since 2024-02-10
def identify_get_names(request, fid):
    print ("running identify_get_names for fid", fid)
    family = Name.objects.get(pnid=int(fid))
    fragment = '<option value="">None Selected</option>'
    for gen in Name.objects.filter(upper=family).order_by('latname'):
        gname = gen.latname
        for sp in Name.objects.filter(upper=gen).order_by('latname'):
            if not sp.longname:
                fragment += '<option value="%s">%s</option>' % (sp.pnid, "%s %s" % (gname, sp.sal_latname))
            else:
                fragment += '<option value="%s">%s</option>' % (sp.pnid, sp.longname)
            print (fragment)
        fragment += '<option value="%s">%s [genus generic]</option>' % (gen.pnid, "%s" % gen.latname)
    fragment += '<option value="%s">%s [family generic]</option>' % (fid, "%s" % family.latname)
                                                    
    return HttpResponse(fragment)

## FIXME so far hardcoded for one category, vascular, presumably for sal names
## will try to any initial category
## changig from legacy to new class
def identify(request):
    if request.GET:
        print (request.GET)
        url = request.GET.get("url")
        latname = request.GET.get("name")
        if url.endswith("/"):
            url = url[:-1]
        print (url, latname)
        tokens = url.split('/')
        fid, spid, imid = tokens[-3], tokens[-2], tokens[-1]
        print (fid, spid, imid)
        name = Name.objects.get(pk=int(spid))
        category = name.category
        print (name, category)
        ## FIXME: 202310-22
        if name.level == 'family':
            genus = None
            family = name
        else:
            genus = name.upper
            family = genus.upper
        print ("genus", genus)
        print ("family", family)
        famname = family.latname
        fid = family.pnid
        print (famname)
        fams = []
        for f in Name.objects.filter(level='family').filter(category=category).order_by('latname'):
            latname = f.latname
            if not latname:
                latname = f.sal_latname
            fam = {"fid": f.pk, "famname": latname}
            fams.append(fam)
        print (len(fams), "total fams")
        names = []
        for g in Name.objects.filter(upper=family):
            gname = g.latname
            for s in Name.objects.filter(upper=g):
                pnid = s.pnid
                latname = "%s %s" % (gname, s.latname)
                names.append( (latname, pnid))
        names.sort()
        print (names)            
##        if category == 'vascular':
##            rec = VascularImage.objects.filter(imid=imid).filter(spid=spid)[0]
##        elif category == 'animals':
##            rec = AnimalImage.objects.filter(imid=imid).filter(spid=spid)[0]
##        elif category = 'nonvascular':
##            rec = NonVascularImage.objects.filter(imid=imid).filter(spid=spid)[0]
##        else:
##            rec = VariaImage.objects.filter(imid=imid).filter(spid=spid)[0]
        print ("will pass", fid, spid, imid)
        return render(request, "photodb/identify.htm", locals())
    else:
        return HttpResponseBadRequest("empty request")
    
def identify_save(request):
    print ("using request.POST", request.POST)
    old_fid = int(request.POST.get("fid"))
    old_spid = int(request.POST.get("spid"))
    new_spid = int(request.POST.get("new_spid"))
    new_fid = int(request.POST.get("new_fid"))
    imid = request.POST.get("imid")
    old_name = Name.objects.get(pk=int(old_spid))
    print ("from", old_name, old_fid, old_spid, imid)
    new_name = Name.objects.get(pk=int(new_spid))
    print ("to", new_name, new_fid, new_spid, imid)
    category = old_name.category
    if category == 'vascular':
        rec = VascularImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0] ## spid=old_spid
    elif category == 'animals':
        rec = AnimalImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    elif category == 'nonvascular':
        rec = NonVascularImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    else:
        rec = VariaImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    print ("was", rec, rec.pk, rec.latname)
    new_plant = Name.objects.get(pk=new_spid)
    rec.plant = new_plant
    ##rec.spid = new_spid
    ##rec.fid = new_fid
    
    ##rec.famname = new_name.legacy_parent.legacy_parent.latname
    ##rec.genname = new_name.legacy_parent.latname
    ##rec.latname = new_name.latname ## loose generic name in image view
    ##rec.authors = new_name.authors
    ##rec.colnames = new_name.colnames
    ##rec.inid = "XXX"
    rec.save()
    print ("new", rec, rec.pk, rec.latname)
    new_url = "/photodb/gallery/view/%s/%s/%s/" % (new_fid, new_spid, imid)
    new_url = "/photodb/gallery/view/%s/%s/" % (new_spid, imid)
    return HttpResponseRedirect(new_url)
    return HttpResponse("test")

## FIXME need POST
def add_genus_species(request):
    print ("running add_genus")
    if request.GET:
        url = request.GET.get("url")
        uid = request.GET.get("uid")
        fid = request.GET.get("fid")
        category = request.GET.get("category")
        genus_latname = request.GET.get("genus_latname").strip()
        latname = request.GET.get("latname").strip()
        existed = Name.objects.filter(latname=genus_latname)
        if existed and len(existed) == 1:
            genus = existed[0]
        elif len(existed) > 1:
            return HttpResponseBadRequest("Latname for valid genus name (%s) should be unique" % genus_latname)
        else:
            genus = Name()
            genus.category=category
            genus.level="genus"
            genus.latname=genus_latname.strip()
            genus.fid=fid
            genus.parent_id=fid
            genus.upper_id=fid
            genus.legacy_parent_id=fid
            genus.sal_latname=genus_latname
            genus.authors = "" ## XXX not null constr!
            genus.sal_authors = "" ## XXX
            genus.colnames = "" ## XXXNOT NULL constraint failed: photodb_Name.colnames
            genus.longname = "" ##
            genus.note = ""
            genus.level = ""
            print ("saving", genus)
            genus.save()
            print ("saved", genus.pnid)
        existed = Name.objects.filter(latname=latname).filter(upper=genus)
        if existed:
            return HttpResponseBadRequest("record exists")
        else:
            species = Name()
            species.category = category
            species.level = "species"
            species.latname = request.GET.get("latname")
            species.sal_latname = request.GET.get("latname")
            species.authors = request.GET.get("authors", "")
            species.sal_authors = request.GET.get("authors", "")
            if not species.sal_authors:
                species.sal_authors = ""
            species.colnames = request.GET.get("colnames", "")
            species.longname = "" #XXX
            species.note = "" ## XXX
            species.level = "" ## XXX should not be a broblem becasue it was null=True but why : NOT NULL constraint failed: photodb_Name.level
            species.parent = genus
            species.upper = genus
            species.legacy_parent = genus
            print ("saving", species)
            species.save()
            print ("saved", species.pk)
            introduced = request.GET.get("introduced")
            invasive = request.GET.get("invasive")
            print (introduced, invasive)
            if introduced or invasive:
                print ("will call enter meta record")
                try:
                    name = "%s %s" % (species.legacy_parent.latname, species.latname)
                except:
                    name = "%s %s" % (species.upper.latname, species.latname)
                done = add_meta_record(species.pk, introduced, invasive, name)
                print ("created meta?", done)
            return HttpResponseRedirect(url)

def add_meta_record(spid, introduced, invasive, name = ""):
    if invasive:
        introduced = True
    print ("running add_meta_record with params", spid, bool(introduced), bool(invasive), name)
    existed = SpeciesMeta.objects.filter(pk=spid)
    if existed:
        print (existed[0], "already exists, exit")
        return None
    else:
        meta = SpeciesMeta()
        meta.spid = int(spid)
        if introduced:
            meta.introduced = "yes"
        if invasive:
            meta.invasive = "yes"
        meta.initial_name = name
        print (meta)
        meta.save()
        return meta


def copy_to(request):
    oldcat = request.GET.get("oldcat")
    newcat = request.GET.get("newcat")
    spid = request.GET.get("spid")
    imid =  request.GET.get("imid")
    fams = []
    for f in Name.objects.filter(level='family').filter(category=newcat).order_by('sal_latname'): ## filter(legacy=True).
        latname = f.sal_latname
        if not latname:
            latname = f.latname
        fam = {"fid": f.pk, "famname": latname}
        fams.append(fam)
    ##fams.sort()
    print (len(fams), "total fams")
    names = []
    return render(request, "photodb/identify_copy.htm", locals())

def save_copied(request):
    oldcat = request.POST.get("oldcat")
    newcat = request.POST.get("newcat")
    old_spid = request.POST.get("spid")
    new_spid = request.POST.get("new_spid")
    new_fid = request.POST.get("new_fid")
    imid =  request.POST.get("imid")
    if oldcat == 'vascular':
        oldrec = VascularImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    elif oldcat == 'animals':
        oldrec = AnimalImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    elif oldcat == 'nonvascular':
        oldrec = NonVascularImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    else:
        oldrec = VariaImage.objects.filter(imid=imid).filter(plant__pnid=old_spid)[0]
    ## XXX: to check for dup
    if newcat == 'vascular':
        rec = VascularImage()
        existed = VascularImage.objects.filter(imid=imid).filter(plant__pnid=int(new_spid))
    elif newcat == 'animals':
        rec = AnimalImage()
        existed = AnimalImage.objects.filter(imid=imid).filter(plant__pnid=int(new_spid))
    elif newcat == 'nonvascular':
        rec = NonVascularImage()
        existed = NonVascularImage.objects.filter(imid=imid).filter(plant__pnid=int(new_spid))
    else:
        rec = VariaImage()
        existed =VariaImage.objects.filter(imid=imid).filter(plant__pnid=int(new_spid))    ## XXX: to check for dup, done?
    if existed:
        error = "fatal error: imid %s already exists in records with spid %s" % (imid, new_spid)
        print (error)
        return HttpResponseBadRequest(error)
    name = Name.objects.get(pnid=new_spid)
    rec.imid=oldrec.imid
    ##rec.spid=int(new_spid)
    rec.plant = name
    rec.phid=oldrec.phid
    ##rec.fid=int(new_fid)
    ##try:
    ##    rec.famname=name.upper.upper.latname
    ##except:
    ##    rec.famname=name.legacy_parent.legacy_parent.latname
    ##try:
    ##    rec.genname = name.upper.latname
    ##except:
    ##    rec.genname = name.legacy_parent.latname
    ##rec.latname = name.latname
    ##rec.colnames = name.colnames
    ##rec.authors = name.authors
    rec.locality = oldrec.locality
    ##rec.lcid=oldrec.lcid                                   ## FIXME ?? OK?
    rec.inid=oldrec.inid ###
    rec.location=oldrec.location
    rec.town=oldrec.town
    rec.date=oldrec.date
    rec.caption=oldrec.caption
    rec.gps=oldrec.gps
    rec.status=oldrec.status
    rec.is_planted=oldrec.is_planted
    rec.is_verified=oldrec.is_verified
    rec.nr=oldrec.nr
    rec.herb_id=oldrec.herb_id
    rec.tags=oldrec.tags
    rec.notes=oldrec.notes
    rec.gps_error=oldrec.gps_error
    rec.reintroduced=oldrec.reintroduced
    committed = datetime.datetime.now()
    modified = datetime.datetime.now()
    new_url = "/photodb/gallery/view/%s/%s/%s/" % (new_fid, new_spid, imid)
    new_url = "/photodb/gallery/view/%s/%s/" % (new_spid, imid)
    print ("to be saved", rec)
    rec.save()
    print ("saved", rec)
    print ("redirect to", new_url)
    return HttpResponseRedirect(new_url)

       
##    return HttpResponse("to be saved " + str(rec))

def duplicate(request, spid, oldimid, newimid=None):
    if not newimid:
        newimid = oldimid + "XXX"
    elif len(newimid) < 5:
        newimid = oldimid[:17] + newimid
    else:
        pass
    oldrecs = VascularImage.objects.filter(imid=oldimid).filter(plant__pnid=int(spid))
    print ("vascular", spid, oldimid, "recs", oldrecs)
    if not oldrecs:
        oldrecs = NonVascularImage.objects.filter(imid=oldimid).filter(plant__pnid=int(spid))
        print ("nonvascular", spid, oldimid, "recs", oldrecs)
        if not oldrecs:
            oldrecs = AnimalImage.objects.filter(imid=oldimid).filter(plant__pnid=int(spid))
            print ("animals", spid, oldimid, "recs", oldrecs)
            if not oldrecs:
                oldrecs = VariaImage.objects.filter(imid=oldimid).filter(plant__pnid=int(spid))
                print ("varia", spid, oldimid, "recs", oldrecs)
    oldrec = oldrecs[0]
    ## assuming that len() == 1 as it should
    print ("oldrec", oldrec)
    ##category = Name.objects.get(pnid=spid).category
    model = oldrec.__class__ ## replace upper lines FIXME
    newrec = model()
    print ("empty newrec", newrec)
    for field in oldrec._meta.local_fields:
        fieldname = field.name
        if not field.name == "id" and not field.name == 'plant' and not field.name == 'locality': ## FIXME 2022-03-21
            print ("using", fieldname)
            newrec.__dict__[fieldname] = oldrec.__dict__[fieldname]
    newrec.locality = oldrec.locality ## FIXME 2022-03-21 added
    newrec.plant = oldrec.plant      ## FIXME 2022-03-21 added
    ## change new values
    newrec.imid = newimid
    newrec.phid = newimid[:17]
    timestamp = timezone.now()
    newrec.committed = timestamp
    newrec.modified = timestamp
    print ("ready to save", newrec)
    newrec.save()
    print ("saved", newrec)
    frec = FileRecord.objects.filter(imid=newimid) ### FIXME
    if len(frec) == 1:
        frec = frec[0]
        frec.committed = True
        if not frec.tables:
            frec.tables = model.__name__
        frec.save()
        print ("saved frec", frec)
    else:
        print ("XXX fix it manually", frec)
    if request:
        return HttpResponseRedirect("/photodb/gallery/view/%s/%s/" % (spid, newrec.imid))
        ##return HttpResponse("saved %s" % newrec)
    else:
        return newrec.pk
    

    
    
        
        

                

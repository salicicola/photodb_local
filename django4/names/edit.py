import xml.dom.minidom, os, shelve, pickle, datetime, sys, time
from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from names.models import Name, SpeciesMeta

## 3 public:: edit_name... :: add_syn() delete_name...()
## 1 used internally update_meta
## 1 template photodb/form_namemini.htm >> to move into names/template/
## to do add authorized :: view | change | delete perms [only Name enough?]


## these two defs are used by edit_name_mini()
def check_authorized(user, perm):
    print ("checking permission", perm, "for", user)
    if user.has_perm(perm):
        return True
    else:
        raise PermissionDenied ##
        ## 403.html in root template directory, or if this file does not exist, instead serves the text “403 Forbidden”

def update_meta(POST):
    spid = POST.get("spid", "")
    if not spid:
        return "no meta data"
    try:
        mrec = SpeciesMeta.objects.get(pk=int(spid))
        print ("existed meta record", mrec)
        changed = False
    except:
        mrec = SpeciesMeta(spid=int(spid))
        print (str(sys.exc_info()))
        print ("new meta record", mrec)
        changed = True
    print ("passed", POST)
    for fname in "rank initial_name evergreen introduced invasive invasive_mipag origin rare evergreen".split(): ### XXX
        if not POST.get(fname) == mrec.__dict__.get(fname): ## POST.get(fname) and  ## FIXME to allow set None
            mrec.__dict__[fname] = POST.get(fname, "")
            changed = True
            print ("set", mrec.__dict__.get(fname))        
    if changed:
        mrec.save()
        return ("meta created/updated: %s" % mrec.updated)
    else:
        return ("no change in meta record")

@login_required(login_url='/admin/login/')
def edit_name_mini(request, pnid, template=""):
    print ("start names.edit.edit_name_mini", pnid)
    req_dict = request.GET
    if not req_dict:
        req_dict = request.POST
    if not request.GET and not request.POST:
        try:
            rec = Name.objects.get(pk=int(pnid))
        except:
            return HttpResponseBadRequest(str(sys.exc_info()))
        famname = genname = ""
        try:
            genname = rec.legacy_parent.latname
        except:
            pass
        if not genname:
            try:
                genname = rec.upper.latname
            except:
                pass
        try:
            famname = rec.legacy_parent.legacy_parent.sal_latname
        except:
            pass
        if not famname:
            try:
                famname = rec.legacy_parent.legacy_parent.latname
            except:
                pass
            if not famname:
                try:
                    famname= rec.upper.upper.latname
                except:
                    famname = ""
        meta = SpeciesMeta.objects.filter(spid=pnid)
        if meta:
            meta = meta[0]
        else:
            meta = SpeciesMeta(spid=pnid)
            meta.initial_name = "%s %s" % (genname, rec.latname)
            meta.su_ba = "yes"
            meta.rank="species"
            meta.evergreen = ""
            meta.origin = ""
            meta.rare = ""
            ## status, counties
        print ("meta", meta)
    else:
        print ("else part : saving... will now check if authortized")
        check_authorized(request.user, "names.change_name")
        check_authorized(request.user, "names.change_speciesmeta") ## return True or raise ...
        rec = Name.objects.get(pk=int(req_dict["pnid"]))
##        try:
##            legrec = LegacyName.objects.get(pk=int(req_dict["pnid"]))
##            ## LegacyName' is not defined >> can remove it
##        except:
##            print (sys.exc_info())
##        legrec = {}
        if request.POST :
            POST = request.POST
        else:
            POST = request.GET
        meta_changed = update_meta(POST)
        print ("finish running meta_changed...", meta_changed)
##        legacy_changed = update_legacy(POST, legrec)
##        print ("finish running legacy_changed...", legacy_changed)
        changed = ""
        if req_dict.get("parent_null", "") == "on":
            print("MUST SET PARENT TO NONE")
            rec.parent = None
            ##rec.latname = ""
            ##rec.authors = ""
            changed += " SET PARENT TO NONE, "
        if not rec.latname == req_dict.get("latname", ""):
            rec.latname = req_dict.get("latname", "").strip()
            changed += req_dict.get("latname", "") + ","
        if not rec.sal_latname == req_dict.get("sal_latname", ""):
            rec.sal_latname = req_dict.get("sal_latname", "").strip()
            changed += req_dict.get("sal_latname", "") + ","
        if not rec.sal_authors == req_dict.get("sal_authors", ""):
            rec.sal_authors = req_dict.get("sal_authors", "").strip()
            changed += req_dict.get("sal_authors", "") + ","
        if not rec.authors == req_dict.get("authors", ""):
            rec.authors = req_dict.get("authors", "").strip()
            changed += req_dict.get("authors", "") + ","
        if not rec.colnames == req_dict.get("colnames", ""):
            rec.colnames = req_dict.get("colnames", "").strip()
            changed += req_dict.get("colnames", "") + ","
        if not rec.note == req_dict.get("note", ""):
            rec.note = req_dict.get("note", "").strip()
            changed += req_dict.get("note", "") + ","
        if not rec.caption == req_dict.get("caption", ""):
            rec.caption = req_dict.get("caption", "").strip()
            changed += req_dict.get("caption", "") + ","
        if changed:
            rec.uid = req_dict.get("uid", "") ## modified_by
            changed = "modified by %s: %s" % (rec.uid, changed[:-1])
            rec.save()
            print ("saved", rec)
            return HttpResponse("changed: " + changed + "\n" + meta_changed, "text/plain")
        else:
            return HttpResponse("not changed: "  + str(rec)+ "\n" + meta_changed, "text/plain")
    return render(request, template, locals())

@login_required(login_url='/admin/login/')
@permission_required('names.add_name', raise_exception=True)
def add_syn(request, spid):
    print ("running add_synonym for parent's ID", spid, "by", request.user.username)
    r = Name()
    parent = Name.objects.get(pk=spid)
    r.level="synonym"
    r.parent = parent
    r.upper = parent
    r.legacy_parent = parent
    r.latname = parent.upper.latname + " ?"
    r.authors = "XXX"
    r.sal_authors = "XXX"
    r.sal_latname = "XXX"
    r.save()
    pnid = r.pk
    print ("saved", r)
    return HttpResponseRedirect("/names/edit/name/%s/" % pnid)

@login_required(login_url='/admin/login/')
@permission_required('names.delete_name', raise_exception=True)
@permission_required('names.delete_speciesmeta', raise_exception=True)
def delete_name_legacy_name(request, pnid):
    print ("running delete_name with an ID", pnid, "by", request.user.username)
    name = Name.objects.get(pk=pnid)
    name.delete()
    return HttpResponse("deleted: %s" % (name)) ## , legacy  & %s
        

####not in use
##def add_meta_record(spid, introduced, invasive, name = ""):
##    if invasive:
##        introduced = True
##    print ("running add_meta_record with params", spid, bool(introduced), bool(invasive), name)
##    existed = SpeciesMeta.objects.filter(pk=spid)
##    if existed:
##        print (existed[0], "already exists, exit")
##        return None
##    else:
##        meta = SpeciesMeta()
##        meta.spid = int(spid)
##        if introduced:
##            meta.introduced = "yes"
##        if invasive:
##            meta.invasive = "yes"
##        meta.initial_name = name
##        print (meta)
##        meta.save()
##        return meta

## not needed, since legrec obj deleted
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



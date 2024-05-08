import datetime, os, sys
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from .models import *
try:
    from names.models import Name
except:
    print ("loaded from .models?")
from .__init__ import VERSION, get_authorized
from django.db.models import Q
##from django.template import Context ## not needed can use {} ?
from django.template.loader import get_template

def allphotos_fromimid(request, imid='20230425olymp0382s'):
    irec = VascularImage.objects.get(imid=imid)
    inid = irec.inid
    print (irec, "inid:", inid)
    irecs = VascularImage.objects.filter(inid=inid)
    print ("got", irecs)
    html = "<html><head></head><body><h2 title='using indID field'>Photographs from the same population as %s.jpg</h2>" % imid
    for irec in irecs:
        url = "/servlet/GetImage?id=%s" % irec.imid
        print ("url", url)
        html += '<img height="300" src="%s"/> ' % url
    html += "</body></html>"
    return HttpResponse(html)


def show_note(request, pnid):
    tname = "photodb/note%s.htm" % pnid
    try:
        t = get_template(tname)
        html = t.render({}) ## Context({})
        return HttpResponse(html)
    except:
        return HttpResponseNotFound("not found")
    
##    if pnid == 301314:
##        html = """<html><head></head><body>
##        <b>Monilophytes</b><br/>
##        <span style="font-size:90%">
##        Name alluding to Latin <i>moniliformis</i>, necklace-like.
##        Monilophytes share a distinctive anatomical feature of vessels:
##        protoxylem confined to lobes of xylem strand (Stein 1993),
##        forming a necklace-shaped pattern.
##        Image from IFAS (University of Florida): </span>       
##        <img style="max-width:400px"
##        src="https://propg.ifas.ufl.edu/images/01-biology/02-cell-types/celltypesxylem/image6.jpg"/>
##        </body></html>"""
##        ##django.template.loader.get_template(template_name)
##        return HttpResponse(html)
##    else:
##        ##raise Http404
##        return HttpResponseNotFound("not found")

## Image copyright: Quizlet <img src="https://o.quizlet.com/i/bspPdDh1zTd3IagqaP4L6A.jpg"/>
## <img align="right" src="/static/1642865397804blob.png"/>
## [XXX Inline image :: cannot see it] <!--
##        https://www.google.com/url?sa=i&url=https%3A%2F%2Fquizlet.com%2F393535332%2F9-phyla-monilophyta-flash-cards%2F&psig=AOvVaw18W1bUMa2yO5LKJzQ_vAQS&ust=1642951660160000&source=images&cd=vfe&ved=0CAgQjRxqFwoTCKC1tZDWxfUCFQAAAAAdAAAAABAN
##        -->

def front_page(request, template="photodb/front_page.htm"):
    version = VERSION ## "1.5.0 (2022-01-24)"
    if request.user.is_authenticated:
        authorized = True
    else:
        authorized = False
    print ("will render", template, "authorized", authorized)
    return render(request, template, locals())

def image_view(request, spid, imid, fid=0, template="photodb/imageview.htm", legacy=True, lcid_starts=None): ## "MA.TDM"
    print ("running photodb.views.image_view()with 3 params", fid, spid, imid)
    print ("at least fid ignored, spid may be needed in current version")
    authorized = False
    ## XXX
    if request.user.is_authenticated:
        print ("permission?", request.user.has_perm('photodb.change_vascularimage'))
        if request.user.has_perm('photodb.change_vascularimage'):
            authorized = True
    print ("user:", request.user, "authorized?", authorized)
    name = Name.objects.get(pnid=spid)
    cat = name.category
    print ("category", cat)   
    if cat == 'vascular':
        manager = VascularImage.objects 
    elif cat == 'nonvascular':
        manager = NonVascularImage.objects 
    elif cat == 'animals':
        manager = AnimalImage.objects 
    elif cat == 'other' or cat == 'varia':
        manager = VariaImage.objects 
    else:
        return HttpResponseBadRequest("DB error")
    if authorized:
        irecs = manager.filter(plant__pnid=int(spid), imid=imid) ## FIXME ? rabotaet li ???
        print ("authorized", len(irecs), "irecs")
    else:
        irecs = manager.filter(plant__pnid=int(spid), imid=imid).filter(nr__lt=100).filter(nr__gt=0) ## FIXME ? rabotaet li ???
        print ("guest", len(irecs), "irecs")
    print ("all", len(irecs), "irecs")
    ## 2022-01-12 adding filtering
    if lcid_starts:
##        irecs = irecs.filter(locality__pk__startswith=lcid_starts)
        irecs.filter(Q(locality__pk__startswith='MA.TDM') | Q(locality__pk__startswith='MA.BDC'))
        print ("filtered by lcid", len(irecs), "irecs")
    if len(irecs) == 0:
        if authorized:
            return HttpResponseBadRequest("No matching record in DB")
        else:
            return HttpResponseBadRequest("Photo %s.jpg is not published" % imid)
    elif len(irecs) > 1:
        return HttpResponseServerError("DB error: returns more than one record")
    else:
        irec = irecs[0]
        if authorized:
            irecs = manager.filter(plant__pnid=int(spid)).order_by('nr')
        else:
            irecs = manager.filter(plant__pnid=int(spid)).filter(nr__lt=100).filter(nr__gt=0).order_by('nr')
        print ("authorized?", authorized, len(irecs), "total")
        ## 2022-01-12 adding filtering
        if lcid_starts:
##            irecs = irecs.filter(locality__pk__startswith=lcid_starts)
            irecs = irecs.filter(Q(locality__pk__startswith='MA.TDM') | Q(locality__pk__startswith='MA.BDC'))
            print ("filtered by lcid", len(irecs), "irecs")
        try:
            locality = Location.objects.get(lcid=irec.lcid) ## field so far missing
            print ("matched location", locality)
        except:
            locality = {}
            print ("no matched locality", locality, sys.exc_info())
        irec.__dict__["locality"] = locality
        print ("set att.locality to irec")
        imids = []
        curnum = 0
        previmg = None
        nextimg = None
        for i in range(len(irecs)):
            rec = irecs[i]
##            ## XXX fixing not needed changed in template using name and name.parent XXX :: which one: parent, legacy_parent or upper ???
##            rec.latname = name.latname
##            rec.authors = name.authors ## FIXME: patching
            imids.append(rec.imid)
            if rec.imid == imid:
                curnum = i + 1

        if authorized:
            pass
        else:
            print (irec.caption)
            irec.caption = irec.caption.replace('***', '')
            print ("delete *** if present:", irec.caption)
        if curnum > 1:
            previmg = irecs[curnum - 2].imid
        if curnum < len(irecs):
            nextimg = irecs[curnum].imid
        total = len(irecs)
        print ("curr", imid, curnum, "of", total)
        print ("prev", previmg)
        print ("next", nextimg)
        ##if irec.herb_id:
        print ("DEBUG:", irec)
        print ("DEBUG: herb_id", irec.herb_id)
        print ("DEBUG: gps", irec.gps)
        total = len(irecs)
        return render(request, "photodb/imageview.htm", locals())


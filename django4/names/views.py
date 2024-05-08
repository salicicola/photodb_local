import os, sys, datetime, inspect, xml.dom.minidom
import lxml.etree as ET ## for using XSLT 1

from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError

from . import * ## DOCKERIZED DB_MODIFIED PHOTODB_AVAILABLE PHOTOS_AVAILABLE debug_mode PACKAGE
from .models import *

package_name = PACKAGE
module_name = os.path.splitext(os.path.split(__file__)[-1])[0]
print ("loading [%s.%s]" % (package_name, module_name))
photodb_available = PHOTODB_AVAILABLE

def get_core(request):
    return render(request, "names/core.htm")

## copied then modified from checklist_adm (not needed deleted)
def get_xml(request, pnid, state="", template=None):
    print ("running %s.%s.%s" % (package_name, module_name, inspect.stack()[0][3]), request, pnid)
    print (Name.objects.get(pnid=pnid))
    print ('has caption?', Name.objects.get(pnid=pnid).caption)

    def get_rank(taxon):
        taxon_rank = taxon.rank
        if not taxon_rank:
            taxon_rank = taxon.level
        return taxon_rank        

    def set_annotations(species, element):
        annotations = NameAnnotation.objects.filter(plant=species)
        for annotation in annotations:
            ann = dom.createElement("annotation")
            if annotation.note:
                note = "<note>%s</note>" % annotation.note
                try:
                    xnote=xml.dom.minidom.parseString(note)
                    ann.appendChild(xnote.documentElement)
                except:
                    ## STR 33 & 35.
                    print (note)
                    print (sys.exc_info())
                    xnote = dom.createElement("note")
                    cdata = dom.createCDATASection(annotation.note)
                    xnote.appendChild(cdata)
                    ann.appendChild(xnote)
                    print (xnote.toxml())
            ann.setAttribute("kind", annotation.kind)
            ann.setAttribute("cached", annotation.cached)
            ann.setAttribute("url", annotation.url)
            ann.setAttribute("by", annotation.by)
            element.appendChild(ann)
            print (ann.toxml())

    def set_meta(species, element):       
        meta = SpeciesMeta.objects.get(pk=species.pnid)
        print ("running get_xml.set.meta for %s, %s [introduced=%s]" % (species, element, meta.introduced))
        element.setAttribute("counties", meta.counties)
        counties = meta.counties.split()
        for c in counties:
            if c == "*":
                c = "&#160;"
            county = dom.createElement("county")
            county.appendChild(dom.createTextNode(c))
            element.appendChild(county)
        if meta.introduced:
            element.setAttribute("nonnative", meta.introduced.capitalize())
        if meta.invasive:
            element.setAttribute("invasive", meta.invasive)
        if meta.rare:
            rare=meta.rare
            if rare == 'T':
                rare = 'Threatened'
            elif rare == 'E':
                rare = 'Endangered'
            elif rare == 'SC':
                rare = 'Special Concern'
            elif rare == 'WL':
                rare = 'Watch Listed'
            elif rare == 'H':
                rare = 'Historic'
            element.setAttribute("rare", rare)
        element.setAttribute("status", meta.status)


    def process(taxa, ele):
        for taxon in taxa:
            if taxon.level == 'species':
                meta = SpeciesMeta.objects.get(spid=taxon.pnid)
##                if state == 'MA' and meta.introduced == 'exotic' or meta.introduced == 'cultivated':
##                    print ("should skip", taxon, "irrelevant for", state)
##                   continue
            if taxon.latname: ## patching:: empty syns
                taxon_rank = get_rank(taxon)
                element = dom.createElement(taxon_rank.capitalize())
                if taxon_rank == 'variety':
                    element.setAttribute("abbr", "var.")
                elif taxon_rank == 'subspecies':
                    element.setAttribute("abbr", "ssp.")
                elif taxon_rank == 'forma':
                    element.setAttribute("abbr", "f.")
                _latname = taxon.latname.split()
                if len(_latname) > 1:
                    latname = _latname[-1]
                    if taxon_rank == 'variety':
                        element.setAttribute("latname", latname)
                        ##
                    elif taxon_rank == 'subspecies':
                        element.setAttribute("latname", latname)
                    elif taxon_rank == 'forma':
                        element.setAttribute("latname", latname)                        
                    else:
                        element.setAttribute("latname", taxon.latname)
                else:
                    element.setAttribute("latname", taxon.latname)
                if taxon.colnames:
                    element.setAttribute("colnames", taxon.colnames)                    
                if taxon.authors:
                    if taxon.latname in taxon.authors:
                        element.setAttribute("nominal", "yes")
                        abbr = element.getAttribute("abbr")
                        if not abbr:
                            if 'var.' in taxon.authors:
                                abbr = 'var.'
                            elif 'ssp.' in taxon.authors:
                                abbr = 'ssp.'
                            elif 'f.' in taxon.authors:
                                abbr = 'f.'
                            else:
                                raise Exception("should never happen %s" % element.toxml())
                            element.setAttribute("abbr", abbr)
                        value = "%s %s" % (abbr, taxon.latname)
                        authors = taxon.authors.replace(value, "").strip()
                        element.setAttribute("authors", authors)
                    else:                    
                        element.setAttribute("authors", taxon.authors)
                element.setAttribute("pnid", str(taxon.pk))
                ele.appendChild(element)
                if taxon.level == 'species':
                   set_meta(taxon, element)
##                   set_photos(taxon, element)
##                   set_generic(taxon, element)
##                   set_nhesp(taxon, element)
##                   set_cnh(taxon, element)
                   set_annotations(taxon, element)
                   if taxon.note:
                       try:
                           text = "<prv_note>%s</prv_note>" % taxon.note
                           if '&' in text:
                               text = text.replace('&', '&amp;')
                           note = xml.dom.minidom.parseString(text)
                           element.appendChild(note.documentElement)
                       except:
                           ##print (x)
                           ##raise
                           note = dom.createElement("prv_note")
                           note.appendChild(dom.createTextNode(taxon.note))
                           element.appendChild(note)
                   if taxon.caption:
                       try:
                           text = "<pub_note>%s</pub_note>" % taxon.caption
                           if '&' in text:
                               text = text.replace('&', '&amp;')
                           caption = xml.dom.minidom.parseString(text)
                           element.appendChild(caption.documentElement)
                       except:
                           caption = dom.createElement("pub_note")
                           caption.appendChild(dom.createTextNode(taxon.caption))
                           element.appendChild(caption)      
                lower=Name.objects.filter(parent=taxon).exclude(disabled=True).exclude(excluded=True).order_by("latname")
                if lower:
                   process(lower, element) 
    
    pnid = int(pnid)
    base = Name.objects.get(pk=pnid)
    base_rank = get_rank(base)
    if 'higher' in base_rank:
        print ('higher', base_rank)
        raise Exception("not implemented for taxa higher than family")
    root = base.upper
    root_rank = get_rank(root)
    dom = xml.dom.minidom.parseString("""<%s latname="%s" pnid="%s" generated="%s"/>""" % (root_rank, root.latname,
                                                                root.pnid, timezone.localtime().isoformat()))
    print ("empty dom", dom)
    doc = dom.documentElement
    if root.caption:
       try:
           text = "<pub_note>%s</pub_note>" % root.caption
           if '&' in text:
               text = text.replace('&', '&amp;')
           caption = xml.dom.minidom.parseString(text)
           doc.appendChild(caption.documentElement)
       except:
           print (sys.exc_info())
           caption = dom.createElement("pub_note")
           caption.appendChild(dom.createTextNode(root.caption))
           doc.appendChild(caption)              
    base_ele = dom.createElement(base_rank.capitalize())
    base_ele.setAttribute("latname", base.latname)
    if base.caption:
        xtext = "<pub_note>%s</pub_note>" % base.caption
        caption = xml.dom.minidom.parseString(xtext)
        base_ele.appendChild(caption.documentElement)
    base_ele.setAttribute("pnid", str(base.pnid)) ## XXX must be simple text  
    doc.appendChild(base_ele)
    print (doc)
    taxa = Name.objects.filter(parent=base).exclude(disabled=True).exclude(excluded=True).order_by("latname")
    print ("will process", base_ele, len(taxa), "taxa")
    process(taxa, base_ele)
    if request:
        if template:
            ##
            pass ## XXX
        else:
            return HttpResponse(dom.toxml(), "text/xml")
    else:
        print (dom.toxml())
        return dom

## modified, always lxml, perm? process_flexible.xslt in names/templates                    
def get_html(request, pnid, state='', use="lxml", xslpath="names/templates/names/process_flexible.xslt"):
    print ("running %s.%s.%s" % (package_name, module_name, inspect.stack()[0][3]))
    if photodb_available:
        server = ""
    else:
        server = "http://172.104.19.75"
    perm = 'townmapper4.view_cnhrecord'
    print ("testing ...", pnid, "using method", use, "external:", server)
    if use=="lxml":
        x = get_xml(None, pnid, state)
        print ("mini dom", x, type(x))
        x.documentElement.setAttribute("server", server)
        if state == 'MA':
            x.documentElement.setAttribute("state", "MA")
        else:
            x.documentElement.setAttribute("state", "")
        print ("set server", x.documentElement.getAttribute("server"))
        if debug_mode:
            x.documentElement.setAttribute("debug", "yes")
        if request.user.is_authenticated:
            x.documentElement.setAttribute("logged", request.user.username)
            if request.user.has_perm(perm):
                x.documentElement.setAttribute("authorized", "yes")
        print ("debug mode?", x.documentElement.getAttribute("debug"))
        if debug_mode:
            xmlpath = os.path.join(package_name, "XML/%s.xml" % pnid)
            f = open(xmlpath, "w")
            f.write(x.toxml())
            f.close()       
            ##dom = ET.parse(xmlpath)
        dom = ET.fromstring(x.toxml())
        print ("dom2", dom, type(dom))
        xslt = ET.parse(xslpath)
        transform = ET.XSLT(xslt)
        newdom = transform(dom)
        html = ET.tostring(newdom, pretty_print=False)
        print (len(html), "html")
    else:
        return HttpResponseServerError("501: not implemeted")
    return HttpResponse(html)

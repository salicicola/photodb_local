from names.models import *
from photodb.models import *
from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import render_to_string

def exotic(request):
    ##XXX disabled, nr < 0
    names=Name.objects.filter(level='species').filter(speciesmeta__introduced='exotic').order_by('longname')
    ##html = "<html><head></head><body><h2>Plant names marked 'exotic'</h2><ol>"
    for name in names:
##        print (name.pk, name.longname)
        photos = VascularImage.objects.filter(plant=name).count()
        published = VascularImage.objects.filter(plant=name).filter(nr__lt=100).count() ## XXX disabled, nr < 0
        name.__dict__["published"] = published
        name.__dict__["total"] = photos
##        url = "http://192.168.1.9:9090/photodb/gallery/view/%s/" % name.pk
##        edit = "http://192.168.1.9:9090/names/edit/name/%s/" % name.pk
##        _html = '<li><a target="_blank" href="%s">%s</a> [<a target="_blank" href="%s">edit</a>] [%s/%s photos]</li>' % (url, name.longname, edit, published, photos)
##        html += _html
##    html += "</ol></body></html>"
##    out = open("exotic.html","w")
##    out.write(html)
##    if request:
    return render(request, "names/exotic.htm", locals())
        ##return HttpResponse(html)
        
##names=Name.objects.filter(level='species').filter(speciesmeta__introduced='exotic')
##>>> for name in names:
##...   print (name.longname)
##Grindelia cordifolia
##Salix myricoides/glaucophylloides
##Ilex vomitoria
##Rubus parviflorus
##Solidago simplex var. simplex
##Persicaria posumbu
##Artemisia suksdorfii
##Castanea crenata
##Heracleum sosnowskyi
##Salix pentandra
##Salix aurita
##Salix myrsinifolia
##Veratrum californicum var. californicum
##---- no longname ---- 17196 >>> Salix fargesii parent = 12136=Tree >> changed to 4 ... and fixed species meta
##Maianthemum amplexicaule
##Lysichiton americanus
##Calamagrostis canadensis var. langsdorffii
##Salix daphnoides
##Salix planifolia
##Salix glauca/brachypodas planifolia Salix
##Castilleja sulphurea
##Castilleja rhexifolia
##Potentilla gracilis
##Packera crocata
##Helianthella uniflora
##Salix drummondiana
##Lonicera involucrata
##Pedicularis bracteosa
##Hackelia micrantha
##Aquilegia coerulae
##Salix glauca
##Salix monticola
##Saxifraga bronchialis
##Cryptogramma acrostichoides
##Antennaria rosea
##Erigeron speciosus
##Berberis repens
##Vaccinium ovalifolium
##Heterotheca villosa
##Salix scouleriana
##Populus angustifolia
##Salix exigua ssp. exigua
##Quercus gambelii
##Amelanchier alnifolia
##Ribes cereum
##Herrickia glauca
##Juniperus scopulorum
##Mertensia ciliata

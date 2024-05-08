from django.test import TestCase

# Create your tests here.
from names.models import Name
def check_longname():
    out = open("longname.err","w")
    spp = Name.objects.filter(category='vascular').filter(level='species').filter(rank='species')
    spp = spp.exclude(excluded=True).exclude(disabled=True)
    for sp in spp:
        calcname = "%s %s" % (sp.upper.latname, sp.latname)
        longname = sp.longname
        if calcname == longname:
            ##print ("OK", longname, '=', calcname)
            pass
        else:
            print ("ERR", longname, '!=', calcname, sp.pk)
            out.write("%s != %s [calculated] %s\n" % (longname, calcname, sp.pk))
    spp = Name.objects.filter(category='vascular').filter(level='species').filter(rank='variety')
    spp = spp.exclude(excluded=True).exclude(disabled=True)
    for sp in spp:
        calcname = "%s %s var. %s" % (sp.upper.latname, sp.parent.latname, sp.latname)
        longname = sp.longname
        if calcname == longname:
            ##print ("OK", longname, '=', calcname)
            pass
        else:
            print ("ERR", longname, '!=', calcname, sp.pk)
            out.write("%s != %s [calculated] %s\n" % (longname, calcname, sp.pk))
    spp = Name.objects.filter(category='vascular').filter(level='species').filter(rank='subspecies')
    spp = spp.exclude(excluded=True).exclude(disabled=True)
    for sp in spp:
        calcname = "%s %s ssp. %s" % (sp.upper.latname, sp.parent.latname, sp.latname)
        longname = sp.longname
        if calcname == longname:
            ##print ("OK", longname, '=', calcname)
            pass
        else:
            print ("ERR", longname, '!=', calcname, sp.pk)
            out.write("%s != %s [calculated] %s\n" % (longname, calcname, sp.pk))
            
    out.close()
    print (out)
    
## forma cultivar hybrid

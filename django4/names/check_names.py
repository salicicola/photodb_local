from names.models import *

UGIDS_VASCULAR = [301319, 301314, 301309, 301307, 301308, 301299]

def check_category(category='vascular'):
    def check_child(child):
        print ('checkling', child, child.category)
        if not child.category==category:
            print (child, child.category)
            assert False
        else:
            for name in Name.objects.filter(parent=child):
                check_child(name)
                
    for ugid in UGIDS_VASCULAR:
        upper = Name.objects.get(pnid=ugid)
        if not upper.category == category:
            print (upper, upper,category)
            assert False
        else:
            for child in Name.objects.filter(parent=upper):
                check_child (child)

def check_parent():
    errors = Name.objects.filter(category='vascular').filter(parent__isnull=True).exclude(disabled=True).exclude(level='higher_taxon').exclude(level='upper_group').exclude(excluded=True)
    print (len(errors))
    for er in errors:
        print ("   http://192.168.1.9:9090/admin/names/name/%s/" % er.pk)
        if er.legacy_parent:
            print ("  perhaps legacy only")
        else:
            print (er, repr(er.parent), er.upper, "disabled?", er.disabled, er.level)
    assert len(errors) == 0, "%s errors" % len(errors)

def check_latnames():
    spp = Name.objects.filter(category='vascular').exclude(rank='hybrid').exclude(rank='synonym').exclude(level='synonym').exclude(rank='section').exclude(level='section')
    spp = spp.exclude(level='unplaced').exclude(level='higher_taxon').exclude(rank='species_group').exclude(level='species_group').exclude(disabled=True).exclude(excluded=True)
    errors = []
    for sp in spp:
        if ' ' in sp.latname:
            print ("http://192.168.1.9:9090/admin/names/name/%s/" % sp.pk, sp.latname, sp.level, sp.rank)
            if not sp in errors: errors.append(sp)
            ##assert False 
        if ' var. ' in sp.authors:
            print (sp.authors, sp.level, sp.rank)
            if not sp in errors: errors.append(sp)
            ##assert False 
        if ' sp. ' in sp.authors:
            print (sp.authors, sp.level, sp.rank)
            if not sp in errors: errors.append(sp)
            ##assert False 
    print ("%s errors" % len(errors))
    
def check_rank():
    recs = Name.objects.filter(rank__isnull=True)
    print ("records without rank: %s" % len(recs))
    for r in recs:
        print (r)
    recs = Name.objects.filter(category='vascular').filter(rank="").exclude(excluded=True).exclude(disabled=True).exclude(level='synonym')
    print ("records with empty rank: %s" % len(recs))
    for r in recs:
        if r.level == 'family':
            r.rank = 'family'
            r.save()
            print ("saved for family")
        elif r.level == 'section':
            r.rank = 'section'
            r.save()
            print ("saved for section")
        elif r.level == 'subsection':
            r.rank = 'subsection'
            r.save()
            print ("saved for subsection")
        elif r.level == 'subgenus':
            r.rank = 'subgenus'
            r.save()
            print ("saved for subgenus")
        elif r.level == 'tribe':
            r.rank = 'tribe'
            r.save()
            print ("saved for tribe")
        else:
            print ("http://192.168.1.9:9090/admin/names/name/%s" % r.pk, r, r.level)
    print ("total %s records" % len(recs))
 ## total 1037 records of genera [to check if valid] XXX
 ## to check synonyms if legacy 
     
def check_level():
    recs = Name.objects.filter(level__isnull=True)
    ##print ("records without rank: %s" % len(recs))
    for r in recs:
        print (r)
       
        
## admin_tools.def set_longname()
## error with Quercus ×warei  != new >>  Quercus robur ×warei 302062

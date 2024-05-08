import sys
from django.contrib import admin
from .models import *
from names.models import *

def get_genus(rec):
    if rec.parent.level == 'genus' :
        return rec.parent
    else:
        return get_genus(rec.parent)

def set_upper():
    recs = Name.objects.filter(category='vascular').filter(level='species').exclude(disabled=True).exclude(parent__isnull=True).exclude(rank='species_complex')
    for r in recs:
        genus = get_genus(r)
        if r.upper == genus:
            pass
        else:
            print ("error in ", r, "upper/should be", r.upper, "!=", genus)

def  get_long_name(rec, lnames=[], ranks=[]):
    lnames.append(rec.latname)
    rank = rec.rank
    if not rank:
        rank = rec.level
    if rank == 'genus':
        ##print ("finalizing")
        ranks.append("genus")
        s = ""
        ranks.reverse()
        lnames.reverse()
        for i in range(len(lnames)):
            if ranks[i] == 'subspecies':
                s += 'ssp. '
            elif ranks[i] == 'variety':
                s += "var. "
            elif ranks[i] == 'forma':
                s += 'f. '
            elif ranks[i] == 'hybrid':
                s = "%s %s" % (lnames[0], lnames[-1])
                print ("hybrid >>", s)
                break
            if ranks[i] == 'section' or ranks[i] == 'subsection' or ranks[i] == 'subgenus' or ranks[i] == 'species_group' or ranks[i] == 'species_complex' or ranks[i] == 'species_coll' or ranks[i] == 'unplaced':
                ##print (ranks[i], "FIXME", lnames, ranks, ">>", s)
                pass
            else:
                s += lnames[i] + " "
        return s.strip()
    else:
        ranks.append(rank)
        return get_long_name(rec.parent, lnames, ranks)

def set_longname():
        recs = Name.objects.filter(category='vascular').filter(level='species').exclude(disabled=True).exclude(parent__isnull=True)
        print ("total %s" % len(recs))
        i, j = 0, 0
        for rec in recs:
            i += 1
            if rec.rank == "species_complex" or rec.rank=='species_coll':
                longname = "%s %s s.l." % (rec.upper.latname, rec.latname)
            else:
                longname = get_long_name(rec, [], [])
            if rec.longname == longname:
                pass
            else:
                j += 1
                print (i, '/', j, rec.longname, " != new >> ", longname, rec.pk)
                x = input ("Yes ? ")
                if x.lower() == 'y':
                    rec.longname = longname
                    rec.save()
                    print ('saved', rec.longname)
                else:
                    pass
        return
    
##      XXX Prunus', 'Prunus', 'Prunocerasus — New World plums', 'americana'
##  Juncus effusus ssp. solutus  != new:  Juncus effusus ssp. effusus ssp. solutus
##  Maianthemum racemosum  != new:  Maianthemum racemosum racemosum
##  Prunella vulgaris  ssp. lanceolata  != new:  Prunella vulgaris ssp. \ lanceolata
##  Viola fimbriatula J. E. Smith  != new:  Viola sagittata var. sagittata
##  Salix sp.  != new:  Salix spp. or hybrids sp.
##  Symphyotrichum var. lanceolatum  != new:  Symphyotrichum lanceolatum ssp. lanceolatum var. latifolium
##  Amelanchier nantucketensis  != new:  Amelanchier nantucketensis nantucketensis
##   Carex sp.  != new:  Carex Unplaced taxa sp.
##   Prunus sp.  != new:  Prunus Unplaced taxa sp.
##   pansy  != new:  Viola ×wittrockiana
    
##   Viola fimbriatula J. E. Smith  != new:  Viola sagittata var. sagittata
##   Rumex persicarioides var. fueginus  != new:  Rumex persicarioides var. persicarioides var. fueginus

## Coleataenia longifolia ssp. rigidula  != new:  Coleataenia longifolia ssp. longifolia ssp. rigidula
## Poa pratensis ssp. angustifolia  != new:  Poa pratensis ssp. pratensis ssp. angustifolia
## Spiranthes var. lacera  != new:  Spiranthes lacera lacera var. lacera
## Hypericum boreale f. callitrichoides  != new:  Hypericum boreale f. f. callitrichoides
## Potamogeton foliosus  != new:  Potamogeton foliosus foliosus
## Symphyotrichum praealtum ssp. angustior  != new:  Symphyotrichum praealtum ssp. . angustior
## Salix atrocinerea/cinerea  != new:  Salix
## Dichanthelium oligosanthes ssp. scribnerianum  != new:  Dichanthelium oligosanthes ssp. oligosanthes ssp. scribnerianum
## Panicum philadelphicum ssp. gattingeri  != new:  Panicum philadelphicum ssp. philadelphicum ssp. gattingeri
## Dichanthelium ovale ssp. villosissimum  != new:  Dichanthelium ovale ssp. ovale ssp. villosissimum
## Dichanthelium ovale ssp. pseudopubescens  != new:  Dichanthelium ovale ssp. ovale ssp. pseudopubescens
## Dichanthelium dichotomum ssp. microcarpon  != new:  Dichanthelium dichotomum ssp. dichotomum ssp. microcarpon
## Dichanthelium dichotomum ssp. mattamuskeetense  != new:  Dichanthelium dichotomum ssp. dichotomum ssp. mattamuskeetense
## Arrhenatherum elatius ssp. bulbosum  != new:  Arrhenatherum elatius ssp. elatius ssp. bulbosum
## Puccinellia distans ssp. borealis  != new:  Puccinellia distans ssp. distans ssp. borealis
## Festuca rubra ssp. pruinosa  != new:  Festuca rubra ssp. rubra ssp. pruinosa

## Salix atrocinerea/cinerea  != new >>  Salix
##      2531 / 3 Festuca rubra ssp. fallax  != new >>  Festuca rubra ssp. rubra ssp. fallax
##      2533 / 4 Festuca rubra ssp. commutata  != new >>  Festuca rubra ssp. rubra ssp. commutata
##  2534 / 5 Eragrostis mexicana  ssp. virescens  != new >>  Eragrostis mexicana ssp. virescens
## 2553 / 6 Bromus hordeaceus ssp. thominei  != new >>  Bromus hordeaceus ssp. hordeaceus ssp. thominei
## 2555 / 7 Bromus hordeaceus ssp. pseudothominei  != new >>  Bromus hordeaceus ssp. hordeaceus ssp. pseudothominei
## 2564 / 9 Poa saltuensis ssp. languida  != new >>  Poa saltuensis ssp. saltuensis ssp. languida
## 2570 / 12 Elymus glabriflorus var. australis  != new >>  Elymus glabriflorus australis
## 2576 / 14 Leptochloa fusca ssp. uninervia  != new >>  Leptochloa fusca ssp. fusca ssp. uninervia
## 2577 / 15 Leptochloa fusca ssp. fascicularis  != new >>  Leptochloa fusca ssp. fusca ssp. fascicularis
## 2582 / 16 Cyperus ×caespitosa  != new >>  Spartina ×caespitosa
## 2646 / 24 Elymus trachycaulus ssp. glaucus  != new >>  Elymus trachycaulus ssp. trachycaulus ssp. glaucus
## 2666 / 30 Najas guadalupensis ssp. olivacea  != new >>  Najas guadalupensis ssp. guadalupensis ssp. olivacea
## 2862 / 45 Amelanchier stolonifera Weig. f. micropetala (B.L. Robins). Rehder  != new >>  Amelanchier micropetala
## 2982 / 58 Bouteloua curtipendula  != new >>  Bouteloua curtipendula curtipendula

##2862 / 2 Amelanchier stolonifera Weig. f. micropetala (B.L. Robins). Rehder  != new >>  Amelanchier micropetala
##3192 / 19 Deschampsia cespitosa ssp. glauca  != new >>  Deschampsia cespitosa ssp. cespitosa ssp. glauca
##3552 / 39 Corallorhiza odontorhiza  != new >>  Corallorhiza odontorhiza odontorhiza
##3675 / 50 Pseudotsuga menziesii ssp. glauca  != new >>  Pseudotsuga menziesii ssp. menziesii ssp. glauca
##3711 / 54 Ranunculus trichophyllus  != new >>  Ranunculus aquatilis trichophyllus
##3712 / 55 Ranunculus longirostris  != new >>  Ranunculus aquatilis longirostris
##3736 / 56 Sorghum bicolor ssp. drummondii  != new >>  Sorghum bicolor ssp. bicolor ssp. drummondii
##3745 / 58 Ulmus glabra  f. cornuta  != new >>  Ulmus glabra f. glabra  f. cornuta
##3786 / 62 Amelanchier nantucketensis  != new >>  Amelanchier
##4008 / 65   != new >>  Pteridium aquilinum

 
def format_longname(longname="Ptelea trifoliata ssp. trifoliata var. trifoliata"):
    html = ""
    if 'ssp.' and 'var.' in longname:
        first, second = longname.split('ssp.')
        html = "<i>%s</i> ssp. " % first.strip()
        tokens = second.strip().split('var.')   
        html += "<i>%s</i> var. <i>%s</i>" % (tokens[0].strip(), tokens[1].strip())
        return html

def problematic():
    problems = Name.objects.filter(category='vascular').filter(parent__isnull=True).exclude(level='higher_taxon').exclude(level='synonym').exclude(rank='synonym')
    problems = Name.objects.filter(category='vascular').filter(parent__isnull=True).exclude(level='higher_taxon').exclude(level='upper_group').exclude(level='synonym').exclude(rank='synonym').exclude(disabled=True)
    for name in problems:
        print (name, 'level=', name.level, 'rank=', name.rank)
"""
10110: americanus / americanus level= species rank= species
10130: sp. / sp. level= species rank= species
11614: strigosus Muhl. ex Willd. var. strigosus / strigosus var. discoideus level= species rank= variety
11912: carpinifolia / carpinifolia level= species rank= species
12726: pungens / pungens level= species rank= species
12762: sp. / sp. level= species rank= species
12777:  / longisetum level= species rank= species
13137: parviflora / parviflora level= species rank= species
13248: canadense / canadense level= species rank= species
13264: galeobdolon / galeobdolon level= species rank= species
13364: oxyacanthoides / oxyacanthoides level= species rank= species
13423: opulus / trilobum level= species rank= species
14049: fortunei / fortunei level= species rank= species
15202: americana / americana level= species rank= species
16111: retusus / retusus level= species rank= species
16273:  / bushianum level= species rank= species
17114: divaricata / divaricata level= species rank= species
17135: emersum / emersum level= species rank= species
17188: acuminatum s.l. / acuminatum s.l. level= species rank= species

recs =  Name.objects.filter(category='vascular').filter(level='species').filter(latname__contains=' ').exclude(rank='hybrid').exclude(disabled=True)
recs =  Name.objects.filter(category='vascular').filter(level='species').filter(authors__contains=' ssp. ').exclude(rank='hybrid').exclude(disabled=True)

url="http://192.168.1.9:9090/admin/names/name/%s/" % r.pk

"""
def check_infra():
    n = 0
    recs = Name.objects.filter(category='vascular').filter(level='species').filter(latname__contains=' ').exclude(rank='hybrid').exclude(rank='cultivar')
    recs = recs.exclude(disabled=True).exclude(latname__contains=" s.l.")##.exclude(rank='species')
    ## 118 species
    for rec in recs:
        n += 1
        try:
            if rec.upper == rec.parent:
                calculated_genus = Name.objects.filter(latname=rec.parent.latname).filter(category='vascular').filter(level='genus')
                if len(calculated_genus) == 1:
                    latname = rec.latname.strip().split()[0]
                    calculated_genus = calculated_genus[0]
                    calculated_species = Name.objects.filter(upper=calculated_genus).filter(latname=latname)
                    print (calculated_genus, latname, calculated_species)
                    if not calculated_species:
                       if ' ssp. ' in rec.latname:
                           rank = 'subspecies'
                       elif ' var. ' in rec.latname:
                           rank = 'variety'
                       else:
                           rank = None
                       sp = Name()
                       sp.uid="AZ"
                       sp.latname = latname
                       sp.upper=calculated_genus
                       sp.legacy_parent=calculated_genus
                       sp.parent = calculated_genus
                       sp.category='vascular'
                       sp.level='species'
                       sp.rank='species'
                       sp.save()
                       ##print ("created", sp)
                       meta= SpeciesMeta()
                       meta.spid = sp.pk
                       meta.species = sp
                       meta.counties = ""
                       meta.initial_name = "%s %s" % (calculated_genus.latname, latname)
                       meta.save()
                       rec.parent=sp
                       if rank:
                           rec.rank = rank
                           print ("set rank", rank)
                       rec.save()
                       print ("created", sp, meta, "modified", rec)
                       print ("check http://localhost:8000/admin/names/name/%s/" % rec.pk)
                       ##print ("http://localhost:8000/admin/names/name/%s/" % sp.pk)
                       ##print ("http://localhost:8000/admin/names/speciesmeta/%s/" % meta.pk)
                       break
                       
                    ##print (n, rec.pk, rec.upper.latname, rec.parent.latname, rec.latname, rec.level, rec.rank) ## , "disabled", rec.disabled
                    ##print ("\n")
        except:
            print (n, rec.pk, rec.upper, rec.parent, rec.latname, rec.level, rec.rank)
            raise

ABBR = {"variety": "var.", "subspecies": "ssp."}
def correct_infra(rank='subspecies'):
    log = open("names/correct_infra.log", "a")
    abbr = ABBR.get(rank)
    recs = Name.objects.filter(category='vascular').filter(level='species').filter(rank=rank).exclude(disabled=True)
    for rec in recs:
        family = rec.upper.upper
        if family.pk == 1428:
            continue
        latname=rec.latname.strip()
        if ' ' in latname:
            try:
                print (rec.upper.latname, rec.parent.latname, rec.latname)
                words = latname.split()
                if len(words) == 3 and words[1] == ABBR.get(rank):
                    if rec.upper == rec.parent:
                        print ("  fatal error, correct manually")
                    else:
                        print ("  can correct automatically")
                        log.write("%s %s to %s by AZ!\n" % (rec.pk, rec.latname, words[2]))
                        rec.latname = words[2]
                        rec.uid="AZ"
                        rec.save()
                        print (" corrected", rec)
                        ##break          
                else:
                    print ("  to Correct Manually")
                    log.write("correct manually: http://localhost:8000/admin/names/name/%s/\n" % rec.pk)
            except:
                print (sys.exc_info(), "to Correct Manually")
                log.write("correct manually (None): http://localhost:8000/admin/names/name/%s/\n" % rec.pk)
        else:
            if rec.upper == rec.parent:
                print ("error", rec.upper, rec.parent, rec.latname)
            else:
                pass
                ##print ("OK", rec.upper, rec.parent, rec.latname)
    log.close()
    

def set_upper_parent():
    recs = Name.objects.filter(upper__isnull=True).filter(parent__isnull=True)
    print (len(recs))
    for r in recs:
        legacy = r.legacy_parent
        if legacy:
            print (r, "?", r.parent, r.upper, legacy)
            r.upper = legacy
            r.parent = legacy
            print (r, "?", r.parent, r.upper, legacy)
            r.save()

names="Icteridae Anatidae Alcidae Ardeidae".split()
names="Accipitridae Cathartidae Cardinalidae Turdidae Tyrannidae Charadriidae".split()
names="Columbidae Picidae Corvidae Mimidae Gruidae Fringillidae Emberiridae Laridae Scolopacidae Meleagrididae Phalacrocoracidae Scolopacidae Passerellidae Paridae".split()
colnames = "Doves;Woodpeckers;Crows, Ravens, Jays, Rooks;Catbirds, Cowbirds, Mockingbirds;Cranes;Finches;American Sparrows, Juncos;Gulls, Terms, Skimmers;Sandpipers, Yellowlegs, Willets;Turkeys;Cormorants;Woodcocks;Towhees, Sparrows;Fitmice, Chickadees".split(';')
            
def add_actual_family(names=names, below=11950, category="animals"):
    parent = Name.objects.get(pnid=below)
    print ("parent/upper", parent)
    for i in range(len(names)):
    ##for name in names:
        name = names[i]
        ##colnames = colnames[i]
        r = Name()
        r.category = category
        r.rank = 'inter'
        r.actual_rank = "family"
        r.colnames = colnames[i]
        r.latname = name
        r.sal_latname = name
        r.parent = parent
        r.upper = parent
        r.legacy_parent = parent
        r.fid = parent.pnid
        r.colnames = ""
        r.save()
        print (r)
        
##def back_invasive():
##    recs = SpeciesMeta.objects.all()
##    for r in recs:
##        if r.invasive:
##            value = r.invasive
##            r.old_invasive = value
##            r.save()
##            print (r.pk, r.invasive, ">>", r.old_invasive, r.updated)

##def back_introduced():
##    recs = SpeciesMeta.objects.all()
##    for r in recs:
##        if r.introduced:
##            value = r.introduced
##            r.nonnative = value
##            r.save()
##            print (r.pk, r.introduced, ">>", r.nonnative, r.updated)

def set_introduced():
   recs = SpeciesMeta.objects.all()
   for r in recs:
       if r.invasive:
           print (r.invasive, "NN was", r.nonnative)
           r.nonnative = "invasive"
           r.save()
           print ("   >", r.nonnative, r.updated)
    
    
    

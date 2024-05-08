from .models import *

## to be used in checklist or plantlists, not in the gallery
## exclude (combine/unite) for rank='forma' done implicetlsy

#for 14346 Species_complex atrocinerea/cinerea
EXCLUDE = [
        11330, ## atrocinerea
        11746, ## cinerea
        11898, ## * bebbiana
        11897, ## * discolor
        11896, ## * humilis
        ## 15844, ## * occidentalis
        ## * aegyptiaca ## not yet in names
    ]
## likewise can manage vars --- to make checklist items in * County Flora style

## for the next version
## different case:: species 17008 Carya ovalis to reassign to another species
## to reassign photo rec in memory from, to
JOIN_TAXA = {
        17008:2642, ## Carya ovalis to Caria glabra
        11330:14346, ## atrocinerea > atrocinerea complex
        16288:10139, ## 'Asplenifolia' > Frangula alnus
        ##11746:14346, ## cinerea
        ##11898:14346, ## * bebbiana
        ##11897:14346, ## * discolor
        ##11896:14346, ## * humilis
        ##15844, ## * occidentalis
        ## * aegyptiaca ## not yet in names
    }

print (" excluded", len(EXCLUDE))
EXCLUDED_IDS = [11330, 11746, 11898, 11897, 11896, 17008, 11330, 16288 ]
print ("total excluded", len(EXCLUDED_IDS))

try:
    from photodb.models import *
    
    def modify_photorecords(rset):
        rset_log = {}
        for rec in rset:
            plant = rec.plant
            if plant.rank == 'forma' or plant.pnid in EXCLUDE:
                print (rec, plant.rank)
                parent = plant.parent
                print (parent)
                rec.plant = parent
                print ("reset", rec)
                if parent.pk in rset_log:
                   rset_log[parent.pk].append(plant)
                else:
                   rset_log[parent.pk] = [plant,] 
                ## 1st version : rset_log[parent.pk] = plant.longname ## only one for sy
        return (rset, rset_log)

    def modify_photorecords2(rset):
        rset_log = {}
        for rec in rset:
            plant = rec.plant
            if plant.rank == 'forma':
                print (rec, plant.rank)
                parent = plant.parent
                print (parent)
                rec.plant = parent
                print ("reset", rec)
                if parent.pk in rset_log:
                    if not plant in rset_log[parent.pk]:
                        rset_log[parent.pk].append(plant)
                else:
                    rset_log[parent.pk] = [plant,] 
                ## 1st version : rset_log[parent.pk] = plant.longname ## only one for sy
            if plant.pnid in JOIN_TAXA:
                parent = Name.objects.get(pnid=JOIN_TAXA[plant.pnid])
                rec.plant = parent
                if parent.pk in rset_log:
                    if not plant in rset_log[parent.pk]:
                        rset_log[parent.pk].append(plant)
                else:
                    rset_log[parent.pk] = [plant,]
                print ("reset explicitly", rec)
            if rec.imid == '20190509olymp1260cs':
                print ("debug ovalis", rec, rec.plant)
                ##raise Exception("xxx debug")
        return (rset, rset_log)

except:
    modify_photorecords   = None
    ##print ("photodb not avallable, modift recordset", modify_photorecords)
        
print ("names.lib: debug:")
for spid in EXCLUDE:
    print ("explicitle suppresss in checklist", Name.objects.get(pnid=spid))
    
print ("loaded names.lib with modify_photo_records", modify_photorecords)
           

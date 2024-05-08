from django.contrib import admin

from .models import *

def get_genus(rec):
    if rec.parent.level == 'genus' :
        return rec.parent
    else:
        return get_genus(rec.parent)

def get_long_name(rec, lnames=[], ranks=[]):
    lnames.append(rec.latname)
    rank = rec.rank
    if not rank:
        rank = rec.level
    if rank == 'genus':
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
                pass
            else:
                s += lnames[i] + " "
        return s.strip()
    else:
        ranks.append(rank)
        return get_long_name(rec.parent, lnames, ranks)


class NameAdmin(admin.ModelAdmin):
    list_display = ('pnid', 'rank', 'level', 'latname', 'longname')
                    ##'parent', 'upper', 'legacy_parent',) colnames', 'created', 'modified') ## 'authors', 'colnames', 
    search_fields = ('pnid', 'latname', 'parent__latname', 'sal_latname',
                     'legacy_parent__latname', 'colnames', 'note')
    list_filter = ('category', 'level', 'rank')
    raw_id_fields = ('parent', 'upper', )
##    exclude = ('legacy_parent', 'sal_latname', 'sal_authors', 'fid', 'disabled', 'longname', 'ccss') ## to be moved later
##    fields = ('category', ('rank', 'legacy'), 'level', 'latname', 'authors', 'colnames', 'parent', 'upper', 'note')
##    list_editable = ['latname', 'authors' ]
    fields = (('category', 'disabled', 'excluded'),
              ('rank', 'level'),
              ('latname', 'authors',),
              ('parent', 'colnames', ),
              ('upper',  'longname', ), ## 'legacy', 'fid', 
              ('uid', ),
              ##'note', 'caption',
              )
    ##readonly_fields = ('upper', 'longname', )

##    def save_model(self, request, obj, form, change):
##        if not obj.uid:
##            uid = str(request.user.username)
##            if uid == 'GMP':
##                uid = 'IK'
##            elif uid == 'salicarium':
##                uid = 'AZ'
##            obj.uid = uid
##        if obj.level == 'species':
##            obj.longname = ""
##            longname = get_long_name(obj)
##            obj.longname = longname
##            genus = get_genus(obj)
##            obj.upper = genus
##        super().save_model(request, obj, form, change)
   
class PlantMetaAdmin(admin.ModelAdmin):
    list_display = ('spid', 'species', 'initial_name', 'introduced', 'invasive', 'invasive_mipag', 'notes', ) ## ) ##  'rank', , 'updated' 'status', 'rare', 'introduced', 'invasive' 'counties'
    search_fields = ('spid', 'initial_name')
    list_filter = ('introduced', 'invasive', 'rare', )
    ##list_editable = ('invasive', 'invasive_mipag')
    raw_id_fields = ('species',)
    exclude = ('spid',)

    def save_model(self, request, obj, form, change):
        try:
            pnid = obj.species.pnid
            if not obj.spid:
                obj.spid = pnid
        except:
            raise
        super().save_model(request, obj, form, change)
            
class CommonNameAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ref_name', 'colname', 'created')
    search_fields = ('colname',)

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'genus', 'species', 'kind', 'note', 'url', 'by', 'cached', 'page', 'modified')
    raw_id_fields = ('plant',)
    search_fields = ('plant__pnid', )
    list_filter = ('kind',)
    exclude = ('id',)

    def genus(self, obj):
        return obj.plant.upper.latname

    def species(self, obj):
        return obj.plant.latname

    def save_model(self, request, obj, form, change):
        if not obj.by:
            uid = str(request.user.username)
            if uid == 'GMP':
                uid = 'IK'
            obj.by = uid
        super().save_model(request, obj, form, change)

class AnnotationAdmin2(admin.ModelAdmin):
    list_display = ('UUID', 'genus', 'species', 'kind', 'url', 'by', 'cached', 'page', 'modified')
    raw_id_fields = ('plant',)
    search_fields = ('plant__pnid', )
    list_filter = ('kind',)
    exclude = ('id',)

    def genus(self, obj):
        return obj.plant.upper.latname

    def species(self, obj):
        return obj.plant.latname

    def save_model(self, request, obj, form, change):
        if not obj.by:
            uid = str(request.user.username)
            if uid == 'GMP':
                uid = 'IK'
            obj.by = uid
        super().save_model(request, obj, form, change)




admin.site.register(Name, NameAdmin)  
admin.site.register(SpeciesMeta, PlantMetaAdmin)
admin.site.register(NameAnnotation, AnnotationAdmin2)


import os, django
print (os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE']='django4.settings'
django.setup()

import names.models

recs = names.models.Name.objects.filter(disabled=True)
print ("disabled", recs[:10], '...')
for rec in recs:
    meta = names.models.SpeciesMeta.objects.filter(spid=rec.pnid)
    if meta:
        meta.delete()
recs.delete()

recs = names.models.Name.objects.filter(excluded=True)
print ("excluded", recs[:10], '...')
for rec in recs:
    meta = names.models.SpeciesMeta.objects.filter(spid=rec.pnid)
    if meta:
        meta.delete()
recs.delete()

recs = names.models.Name.objects.filter(level='species').filter(parent=None)
print ("no parent", recs[:10], '...')
for rec in recs:
    meta = names.models.SpeciesMeta.objects.filter(spid=rec.pnid)
    if meta:
        meta.delete()
recs.delete()

recs = names.models.Name.objects.filter(level='species').filter(upper=None)
print ("no upper", recs[:10], '...')
for rec in recs:
    meta = names.models.SpeciesMeta.objects.filter(spid=rec.pnid)
    if meta:
        meta.delete()
recs.delete()


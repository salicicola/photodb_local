import os
from django.shortcuts import render ## _to_response  
from photodb.models import *
from names.models import *


def doimport():
    f = open("XXXXX")
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        name, url = line.split('::')
        tmp = os.path.split(url)[1]
        spid = os.path.splitext(tmp)[0]
        spid = int(spid)
        ##print (spid, type(spid))
        plant = Name.objects.get(pk=spid)
        ##print (plant)
        meta = SpeciesMeta.objects.get(pk=spid)
        ##print (plant, meta)
        ##print (spid, name.strip(), url.strip())
        rec = TODO()
        rec.spid = spid
        rec.name = name.strip()
        rec.counties = meta.counties
        rec.status = meta.introduced + meta.rare
        if not rec.status:
            rec.status = "N"
        rec.url = url.strip()
        rec.save()
        print ("saved", rec, rec.status)
        ##break

def todo_views(request, season="", status=""):
    print ("running todo")
    if season:
        recs = TODO.objects.filter(season=season)
    elif status:
        recs = TODO.objects.filter(status=status)
    else:
        recs = TODO.objects.all()
    recs = recs.order_by('name')
    print ("recs", len(recs))
    return render(request, "todo.htm", locals())

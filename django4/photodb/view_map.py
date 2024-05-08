import xml.dom.minidom, os, sys, datetime
from urllib import request
from html.parser import HTMLParser
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseNotFound
from .models import *
from names.models import *
from .models import * ## SpeciesPublished, ImagePublished, VascularImage
from django.utils import timezone

def acmemap_gps(request, gps):
    lat, lon = gps.split('-')
    lon = '-%s' % lon
    url = "https://mapper.acme.com/?ll=%s,%s&z=17&t=M&marker0=%s,%s" % (lat, lon, lat, lon)
    print (url)
    return HttpResponseRedirect(url)

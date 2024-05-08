import sys, django, os, datetime, xml.dom.minidom, time, email
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest,  HttpResponseNotFound, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from .models import BugRecord

VERSION = "0.0.2" ## adding RSS for bug report
VERSION = "0.1.0 (revno #45+) alpha" ##2021-02-19
VERSION = "0.1.1 (revno #52+) alpha" ##2021-02-20 adding RSS for bug report
VERSION = "0.1.2 (revno #55+) alpha" ##2021-02-20 bug reports improved, revno 8+
VERSION = "0.1.3 (revno #3+) alpha (2021-12-05)" ## replaced datetime to timezone; other major improvements; TODO: authenticated to authorized, rss_template universal  
VERSION = "0.1.3 (revno #4+) alpha (2021-12-05 15:25:00 + )"
VERSION = "0.1.4 (revno #6+) alpha" ## to improve models and allow edit delete own recs in XML
VERSION = "0.1.5 (revno #8+) alpha"  ## essentially imporved, including design, still need to change GET to POST to be beta
##VERSION = "0.2.0 (revno #10+) beta" ## to test for stability, etc, to correct links in photodb/remove explicit in main urls, rss improved
## revno 12+ added two fields in model: priority and status (committed|fixed etc)
VERSION = "0.2.1 (revno #26+) alpha" ## registered and authenticated except superuser will use their own XML [ 2022-09-28 20:24:59 ]


APPPATH = __file__
WORKING_DIR = os.getcwd()
print ("bugs module initializing", APPPATH, VERSION)
print ("working dir of common.bugs", WORKING_DIR)

rss_template = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
    <title>Last Bug Report</title>
    <link>http://%s/bugs/</link> 
    <description>Last bug reported</description>
    <atom:link href="http://%s/bugs/" rel="self"></atom:link>
    <language>en-us</language>
    <lastBuildDate>%s</lastBuildDate>
    <item>
        <title>%s</title>
        <link>http://%s/bugs/</link>
        <description>%s</description>
        
    </item>
    </channel>
    </rss>"""
## URL URL date, title, URL, description
## <guid>172.104.19.75/bugs/</guid>

BUGS_LOCK_PATH = os.path.join(os.path.split(APPPATH)[0], "XML", "bugs.lock")
BUGS_LOCK_TIMEOUT = 60 * 1 ## 60*10 = 10 minutes

def get_perms(request):
    status = {}
    if request.user.is_authenticated:
        uid = request.user.username
        status["uid"] = uid
        user = request.user
        if user.has_perm('common.edit_bugrecord'):
            status['authorized'] = True
        elif user.has_perm('common.add_bugrecord'):
            status["registered"] = True
        else:
            status["authenticated"] = True
    print ("user", request.user, "perms status", status)
    return status

def bugs_index(request):
    version = VERSION
    return render(request, "bugs/index.htm", locals())

def disallowed(request):
    res = HttpResponse("cannot process")
    res.status_code = 401
    return res

def lock_file(path=None):
    if not path:
        path = BUGS_LOCK_PATH
    if os.path.exists(path):
        locked = int(os.path.getmtime(path))
        print (locked, type(locked))
        now = int(time.time())
        print (now, type(now))
        delta = now - locked
        print (delta, type(delta))
        print (locked, now, type(locked), type(now))
        if delta < BUGS_LOCK_TIMEOUT:
            print ("file recenty locked %s minutes ago" % (delta/60))
            raise BlockingIOError("file locked %s minutes ago, wait..." % (delta/60.0))
            ##return HttpResponse("file locked %s minutes ago, wait..." % (delta/60.0))
        else:
            print ("too old lock %s minutes ::  can re-lock" % (delta/60.0))
    else:
        print ("no lock file, willcreate it")
    lock = open(path, "w")
    lock.close()
    print ("locked", path, os.path.exists(path))
    return os.path.exists(path)

def release_lock(path=None):
    if not path:
        path = BUGS_LOCK_PATH
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(path):
        print ("cannot release lock")
        return False
    else:
        print ("released")
        return True

def bug_entry(request, template="bugs/bugentry.htm"):
    user_status = get_perms(request)
    django_version = django.get_version()
    python_version = sys.version.split()[0]
    version = VERSION
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    rfcdt = email.utils.formatdate(nowtimestamp)
    created = timezone.now().isoformat()
    if not request.POST:
        reporter = request.user
        component = "bug"
        if request.GET.get("category"):
            component = request.GET.get("category")
        url = request.META.get("HTTP_REFERER")
        return render(request, template, locals())
    else:
        print (request.POST)
        reporter = request.POST.get("reporter")
        component = request.POST.get("component")
        summary = request.POST.get("summary")
        url = request.POST.get("url")
        notes = request.POST.get("notes")
        if user_status.get("authorized"): ## debugging: newer at server:  request.user.is_authenticated:
            print ('authenticated as', request.user, "authorized", user_status)
            record = BugRecord()
            record.reporter = reporter
            record.component = component
            record.summary = summary
            record.url = url
            record.notes = notes ## no such field
            record.description = notes
            record.save()
            print ("saved in DB", record, record.modified)
        else:
            print ("not authorized, will use XML")
            if user_status.get("registered") or user_status.get("authenticated"):
                fname = "bugs_%s.txt" % user_status.get("uid")
            else:
                fname = "bugs.txt"
            print ("will save to %s" % fname)
            dom = xml.dom.minidom.parseString("<record/>")
            for key in request.POST.keys():
                if not key == "csrfmiddlewaretoken":
                    value = request.POST.get(key)
                    if value:
                        fld = dom.createElement(key)
                        fld.appendChild(dom.createTextNode(value))
                        dom.documentElement.appendChild(fld)
            if not request.POST.get("created"):
                created = timezone.now().isoformat()
                fld = dom.createElement("created")
                fld.appendChild(dom.createTextNode(created))
                dom.documentElement.appendChild(fld)
            else:
                modified = timezone.now().isoformat()
                fld = dom.createElement("modified")
                fld.appendChild(dom.createTextNode(modified))
                dom.documentElement.appendChild(fld)
            print (dom.documentElement.toxml())
            path = os.path.split(APPPATH)[0] ## absolute since python3.8 already ? but how it will work in python 3.6?
            print (path)
            if not user_status:
                try:
                    lock_file()
                except BlockingIOError:
                    return HttpResponse("please  wait... go back and repeate operation")
            path = os.path.join(path, "XML", fname)
            print ("will save to", path)
            out = open(path, "a")
            out.write(dom.documentElement.toxml())
            out.write("\n")
            out.close()
            print (out)
            print ("TODO: to inform admin")
            domain = request.META['HTTP_HOST']
            rss = rss_template % (domain, domain, rfcdt, summary, domain, notes)
            ##print (rss)
            out = open(os.path.join(os.path.split(APPPATH)[0], "XML", "last_bug.rss"), "w") ## for xml not wb
            ##out.write(rss) ## needs bytes in this python version
            xml.dom.minidom.parseString(rss).writexml(out)
            out.close()
            print(out)
            if not user_status:
                success = release_lock()
                print ("data written and lock released", success)
            else:
                print ("data saved to XML or SQL DB")
        ##return render(request, template, locals())
        return view_all_bugs(request, reporter)
        ##return HttpResponseRedirect("/bugs/view/")

def view_bug_rss(request):
    if os.path.exists(os.path.join(os.path.split(APPPATH)[0], "XML", "last_bug.rss")):
        x = open(os.path.join(os.path.split(APPPATH)[0], "XML", "last_bug.rss")).read()
        return HttpResponse(x, "text/xml") ## "application/rss+xml"
    else:
        return HttpResponseBadRequest("<nothing_found/>", "text/xml")

def get_value(ele, name):
    try:
        value = ele.getElementsByTagName(name)[0].firstChild.nodeValue
    except:
        value = ""
    return value

def parse_line(line):
    line = line.strip()
    dom = xml.dom.minidom.parseString(line)
    reporter = get_value(dom.documentElement, "reporter")
    actual_user =get_value(dom.documentElement, "actual_user")
    component = get_value(dom.documentElement, "component")
    summary = get_value(dom.documentElement, "summary")
    notes = get_value(dom.documentElement, "notes")
    url= get_value(dom.documentElement, "url")
    severity = get_value(dom.documentElement, "priority_severity")
    created = get_value(dom.documentElement, "created")
    print (dom.getElementsByTagName("priority_severity"), created)
    print ("returning", reporter, actual_user, component, summary, notes, url, severity, created)
    return (reporter, actual_user, component, summary, notes, url, severity, created)

@login_required(login_url='/admin/login/')
##@permission_required('common.delete_bugrecord', login_url='/bugs/401/')
def delete_bug(request, params):
    print ("starting delete bug with", request, params)
    ### move to internal def
    user_status = get_perms(request)
    if user_status.get("registered"):
        fname_ = "bugs_%s" % user_status.get("uid")
        print ("registered and fname", fname_)
    else:
        fname_ = "bugs"
        print ("not registered and fname", fname_)            
        try:
            lock_file()
        except BlockingIOError:
            return HttpResponse("please  wait... go back and repeate operation")
    timestamp = params.get("created")
    timestamp = timestamp.replace(' ', '+')
    print ("deleting bug:", timestamp)
    ## FIXME
    if fname_ == "bugs_salicarium":
        fname_ = "bugs"
    x = open(os.path.join(os.path.split(APPPATH)[0], "XML", "%s.txt" % fname_))
    y = open(os.path.join(os.path.split(APPPATH)[0], "XML", "%s.$$$.txt" % fname_), "w")
    print(x)
    print (y)
    lines = x.readlines()
    for line in lines:
        if line.strip():
            (reporter, actual_user, component, summary, notes, url, severity, created) = parse_line(line)
            ##print ("testing", timestamp, created, timestamp==created)
            if created == timestamp:
                print ("skip", line)
            else:
                y.write(line)
                y.write("\n")
    x.close()
    y.close()
    orig = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.txt" % fname_)
    temp = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.$$$.txt" % fname_)
    bak = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.bak.txt" % fname_)
    os.rename(orig, bak)
    print (orig, "renamed to", bak)
    os.rename(temp, orig)
    print ("renamed", temp, "to", orig)
    if fname_ == "bugs":
        release_lock()
    if request:
        ##return HttpResponse("record deleted")
        return HttpResponseRedirect("/bugs/view/")
    else:
        return True

##@login_required(login_url='/admin/login/')
@permission_required('common.add_bugrecord', login_url='/bugs/401/')
def submit_bug(request, params):
    rec = BugRecord()
    rec.reporter = params.get("reporter", "")
    rec.actual_user = params.get("actual_user", "")
    rec.component = params.get("component", "")
    rec.summary = params.get("summary", "")
    rec.description = params.get("notes", "")
    rec.url = params.get("url", "")
    rec.severity = params.get("priority_severity", "")
    rec.created = params.get("created", timezone.now().isoformat())
    print (rec)
    rec.save()
    print ("saved", rec)
    ##result = delete_bug(None, params) ## 'NoneType' object has no attribute 'user'
    result = delete_bug(request, params)
    return render(request, "bugs/committed.htm", locals())

@login_required(login_url='/admin/login/')
def save_bug(request, params):
    user_status = get_perms(request)
    rec = xml.dom.minidom.parseString("<record></record>")
    for key, value in params.items():
        if not key == 'save':
            print (key, value)
            field = rec.createElement(key)
            if not value:
                value = ""
            field.appendChild(rec.createTextNode(value))
            rec.documentElement.appendChild(field)
    newline = rec.documentElement.toxml()
    print (newline)
    ## from ...
    timestamp = params.get("created")
    timestamp = timestamp.replace(' ', '+')
    if user_status.get("registered"):
        fname_ = "bugs_%s" % user_status.get("uid")
        print ("registered and fname", fname_)
    else:
        fname_ = "bugs.txt"
        try:
            lock_file()
        except BlockingIOError:
            return HttpResponse("please  wait... go back and repeate operation")
    
    print ("deleting bug:", timestamp)
    x = open(os.path.join(os.path.split(APPPATH)[0], "XML", "%s.txt" % fname_))
    y = open(os.path.join(os.path.split(APPPATH)[0], "XML", "%s.$$$.txt" % fname_), "w")
    lines = x.readlines()
    for line in lines:
        if line.strip():
            (reporter, actual_user, component, summary, notes, url, severity, created) = parse_line(line)
            print ("testing", timestamp, created, timestamp==created)
            if created == timestamp:
                print ("skip", line)
            else:
                y.write(line)
                y.write("\n")
    y.write(newline)
    y.write("\n")
    x.close()
    y.close()
    orig = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.txt" % fname_)
    temp = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.$$$.txt" % fname_)
    bak = os.path.join(os.path.split(APPPATH)[0], "XML", "%s.bak.txt" % fname_)
    os.rename(orig, bak)
    print ("renamed to bak")
    os.rename(temp, orig)
    print ("renamed temp to orig name")
    if fname_ == "bugs.txt":
        release_lock()
        print ("released?")
    return HttpResponseRedirect("/bugs/view/")
##    return HttpResponse(rec.toxml(), "text/xml")
###<reporter>me</reporter><actual_user>tester</actual_user><component>bug</component><summary>dddfdfs</summary><url>None</url><created>2021-12-06T19:25:36.733882+00:00</created><modified>2021-12-06T19:25:45.389338+00:00</modified></record>

##@login_required(login_url='/admin/login/')
##@permission_required('common.add_bugrecord', login_url='/bugs/401/')
def manage_bug(request):
    print ("running manage_bug(); authenticated?", request.user.is_authenticated)
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    params = request.POST
    ## next two lines not in use XXX
    ##authorized = request.user.has_perm('common.view_bugrecord')
    user_status = get_perms(request)
    authorized = user_status.get("authorized", False)
    print ("POST params", params)
    print (user_status)
    print ("authorized from user_status", authorized)
    if authorized: ## FIXME need improvement
        if not params:
            params = request.GET
        if params.get("delete") and authorized:
            action = "delete"
            return delete_bug(request, params)
        elif params.get("delete") and params.get('reporter') == request.user.username:
            print ("may delete your own record", params.get('reporter'), request.user.username)
            return delete_bug(request, params)
        elif params.get("save") and params.get('reporter') == request.user.username:
            print ("saving")
            return save_bug(request, params)
        elif params.get("submit"):
            action = "submit"
            return submit_bug(request, params)
    else:
        print ("to test if uid=reporter, registered")
        if params.get("reporter") == user_status.get("uid") and user_status.get("registered"):
            print ("should allow to edit/delete in XML file", params.get("reporter"), user_status.get("uid"), user_status.get("registered"))
            print (params)
            if params.get("delete"):
                return delete_bug(request, params)
            elif params.get("submit"):
                return save_bug(request, params)               
            else:
                print ("should not happen")
                return HttpResponse('Unauthorized', status=401)
        else:
            return HttpResponse('Unauthorized', status=401)
        ##return HttpResponse(str(request.GET), "text/plain")

## tester 123!@#$%
def get_path(user_status, uid=None):
    if user_status.get("authorized") and uid:
        fname = "bugs_%s.txt" % uid
    elif user_status.get("registered"):
        fname = "bugs_%s.txt" % user_status.get("uid", "")
    else:
        fname = "bugs.txt"
    path = os.path.join(os.path.split(APPPATH)[0], "XML", fname)
    return path

##@login_required(login_url='/admin/login/')
def edit_bug(request):
    if not request.GET or not request.GET.get('id'):
        return HttpResponseBadRequest("Cannot get user ID")
    user_status = get_perms(request)
    nr, timestamp = request.GET.get('id').split('::')
    timestamp = timestamp.replace(' ', '+')
    print ("edit bug:", nr, timestamp)
    path = get_path(get_perms(request), nr)
    print (path)
    if not os.path.exists(path):
        path = "common/XML/bugs.txt"
    x = open(path)
    lines = x.readlines()
    for line in lines:
        if line.strip():
            (reporter, actual_user, component, summary, notes, url, severity, created) = parse_line(line)
            print ("testing", timestamp, created, timestamp==created)
            if created == timestamp:
                return render(request, "bugs/edit_bug.htm", locals())
    return HttpResponseBadRequest("not found")

""" $submitted to be used only if run by admin ('authorized')
    if None or '' >> will use SQLDB
    if unknown > will use bugs.txt
    else: will use bugs_{submitted} where submitted should be reporter field
"""    
def view_all_bugs(request, submitted=""):
    print ("running view_all_bugs")
    user_status = get_perms(request)
    print ("running view_all_bugs() $submitted = %s" % submitted)
    print ("user", user_status)
    fname = None
    if user_status.get("authorized"):
        print ("admin running for [%s]" % submitted)
        if not submitted:
            return HttpResponseRedirect("/admin/common/bugrecord")
        elif submitted=="unknown":
            fname = "bugs.txt"
            print ("will use default XML file %s in admin mode" % fname)
        else:
            fname = "bugs_%s.txt" % submitted
            print ("will use XML file %s in admin mode" % fname)
    elif user_status.get("registered") or user_status.get("authenticated"):
        print ("not admin, but registered or authenticated")
        fname = "bugs_%s.txt" % user_status.get("uid", "")
        print ("will use XML file %s in common mode" % fname)
    else:
        fname = "bugs.txt"
        print ("will use default XML file", fname)
    print ("finally", fname)
    if not user_status:
        lock = os.path.join(os.path.split(APPPATH)[0], "XML", "bugs.lock")
        if os.path.exists(lock):
            locked = os.path.getmtime(lock)
            locked = datetime.datetime.fromtimestamp(locked)
            diff = datetime.datetime.now() - locked
            print ("locked", locked, "ago", diff)
            minutes = int(diff.total_seconds()/60)
            print (minutes)
            if minutes > 15:
                release_lock()
                print ("lock file released -- is it still exists?", os.path.exists(lock))
            else:
                return HttpResponse("file locked, %s minutes ago, wait" % minutes)
    path = os.path.join(os.path.split(APPPATH)[0], "XML", fname)
    print ("finally", path)
    if not os.path.exists(path):
        ## if authorized should be here
        if user_status.get("authorized"):
            return HttpResponseRedirect("/bugs/")
        else:
            return HttpResponseNotFound("no appropriate data file found")
    x = open(path)
    total = 0
    records = []
    authorized = False
    if request.user.is_authenticated:
        authorized = request.user.has_perm('common.view_bugrecord')
    print ("users perm to view_bugrecord", authorized)        
    if not submitted:
        submitted = request.user.username
        print ("submitted by according to srequest", submitted)
    for line in x.readlines():
        if line.strip():
            total += 1
            (reporter, actual_user, component, summary, notes, url, severity, created) = parse_line(line)
            rec = {"nr":total, "reporter":reporter, "actual_user": actual_user, "component":component, "summary": summary, "notes": notes, "url": url, "severity": severity, "created": created}
            print ("notes", rec.get("notes"))
            if authorized:
                print ("appending all", request.user, rec)
                records.append(rec)
            else:
                if reporter == submitted:
                    records.append(rec)
                    print ("appending relevant", rec)
                else:
                    print ("skip", rec)
    records.reverse()
    return render(request, "bugs/submitted.htm", locals())
## XXX    else:
##        return HttpResponseBadRequest("<nothing_found/>", "text/xml")

def admin_default(request):
    return HttpResponse("")

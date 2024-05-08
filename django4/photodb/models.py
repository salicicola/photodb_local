from django.utils import timezone
from django.db import models
from common.models import Location
from names.models import Name

import datetime
import django
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TODO(models.Model):
    spid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, default="", null=True, blank=True)
    status = models.CharField(max_length=10, default="", null=True, blank=True)
    counties = models.CharField(max_length=100, default="", null=True, blank=True)
    url = models.CharField(max_length=100, default="", null=True, blank=True)
    coord = models.CharField(max_length=250, default="", null=True, blank=True)
    season = models.CharField(max_length=100, default="", null=True, blank=True)
    notes = models.CharField(max_length=256, default="", null=True, blank=True)
    inat_id = models.IntegerField(null=True, blank=True)
    found = models.BooleanField(default=False)

    def __str__ (self):
        return "%s: %s [%s] {%s}" % (self.pk, self.name, self.status, self.counties)

class SpeciesPublished(models.Model):
    ID = models.IntegerField(primary_key=True)
    plant = models.ForeignKey(Name, on_delete=models.CASCADE) ##  ??? XXX
    published = models.DateField(null=True, blank=True)
    last = models.DateField(null=True, blank=True) ## previous
    current = models.DateField(null=True, blank=True) ## newest
    status = models.CharField(max_length=10, default="")
    modified = models.DateTimeField(auto_now=True)

    def __str__ (self):
        return "%s: %s [publisdhed: %s] %s [%s]" % (self.pk,
                                   self.plant, self.published,
                                   self.status, self.modified)

##### could not be unique should use unique together (imid and spid)
##class ImagePublishedOld(models.Model):
##    imid = models.CharField(max_length=10, primary_key=True)
##    category = models.CharField(max_length=10, default="vascular")
##    plant = models.ForeignKey(Name, blank=True, null=True, on_delete=models.SET_NULL) ##  ??? XXX
##    published = models.DateField(null=True, blank=True)
##    last = models.DateField(null=True, blank=True) ## previous
##    current = models.DateField(null=True, blank=True) ## newest
##    status = models.CharField(max_length=10, default="")
##    note = models.CharField(max_length=10, blank=True, null=True, default="")
##    modified = models.DateTimeField(auto_now=True)
##
##    def __str__ (self):
##        return "%s: %s [published: %s] %s [%s]" % (self.pk,
##                                   self.plant, self.published,
##                                   self.status, self.modified)

class ImagePublished(models.Model):
    ##ID
    imid = models.CharField(max_length=30)
    category = models.CharField(max_length=10, default="vascular")
    plant = models.ForeignKey(Name, blank=True, null=True, on_delete=models.SET_NULL) ##  ??? XXX
    published = models.DateField(null=True, blank=True)
    last = models.DateField(null=True, blank=True) ## previous
    current = models.DateField(null=True, blank=True) ## newest
    status = models.CharField(max_length=10, default="")
    note = models.CharField(max_length=10, blank=True, null=True, default="")
    modified = models.DateTimeField(auto_now=True)

    def __str__ (self):
        return "%s: %s [published: %s] %s [%s]" % (self.pk,
                                   self.plant, self.published,
                                   self.status, self.modified)
    class Meta:
        unique_together = ['imid', 'plant']
        ## Use UniqueConstraint with the constraints option instead.


##class SpeciesPublished(models.Model):
##    ID = models.IntegerField(primary_key=True)
##    plant = models.ForeignKey(Name, on_delete=models.CASCADE) ##  ??? XXX
##    published = models.DateField(null=True, blank=True)
##    status = models.CharField(max_length=10, default="")
##    modified = models.DateTimeField(auto_now=True)
##
##    def __str__ (self):
##        return "%s: %s [publisdhed: %s] %s [%s]" % (self.pk,
##                                   self.plant, self.published,
##                                   self.status, self.modified)
##
##### could not be unique should use unique together (imid and spid)
##class ImagePublished(models.Model):
##    imid = models.CharField(max_length=10, primary_key=True)
##    category = models.CharField(max_length=10, default="vascular")
##    plant = models.ForeignKey(Name, blank=True, null=True, on_delete=models.SET_NULL) ##  ??? XXX
##    published = models.DateField(null=True, blank=True)
##    status = models.CharField(max_length=10, default="")
##    note = models.CharField(max_length=10, blank=True, null=True, default="")
##    modified = models.DateTimeField(auto_now=True)
##
##    def __str__ (self):
##        return "%s: %s [published: %s] %s [%s]" % (self.pk,
##                                   self.plant, self.published,
##                                   self.status, self.modified)

class ChecklistNote(models.Model):

    plant = models.ForeignKey(Name, on_delete=models.CASCADE)
    note = models.TextField(max_length=256, null=True, blank=True)
    comments = models.CharField(max_length=256, null=True, blank=True)
    checklist = models.CharField(max_length=100, default="Tidmarsh")
    uid = models.CharField(max_length=10, default="salicarium")
    modified = models.DateTimeField(auto_now=True)

##from survey.models import GenericRecord
## from Tidmarsh moved here as
class TidmarshRecord (models.Model):   
    coordinates= models.CharField(max_length=100, null=True, blank=True)
    created= models.CharField(max_length=100, null=True, blank=True)
    lat= models.CharField(max_length=100, null=True, blank=True)
    lon= models.CharField(max_length=100, null=True, blank=True)
    lcid= models.CharField(max_length=100, null=True, blank=True)
    location= models.CharField(max_length=256, null=True, blank=True)
    notes= models.TextField(null=True, blank=True)
    observed= models.CharField(max_length=256, null=True, blank=True)
    photo_url= models.CharField(max_length=256, null=True, blank=True)
    plant_id= models.CharField(max_length=256, null=True, blank=True)
    plantname= models.CharField(max_length=256, null=True, blank=True)
    rid= models.IntegerField(null=True, blank=True) ## primary_key=True
    uid= models.CharField(max_length=100, null=True, blank=True)
    ## extra from entry module
    actual_uid = models.CharField(max_length=5, null=True, blank=True)
    category = models.CharField(max_length=5, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    files = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (("uid", "created", "rid"),)

    def __str__ (self):
        if self.location:
            return "#%s: %s @ %s" % (self.pk, self.plantname, self.location)
        elif self.lat and self.lon:
            return "#%s: %s @ %s %s" % (self.pk, self.plantname, self.lat, self.lon)
        else:
            return "#%s: %s" % (self.pk, self.plantname)



class AbstractImageRecord(models.Model):
    """ normalized  """ 
    imid = models.CharField(max_length=50)
    plant =  models.ForeignKey(Name, null=True, blank=True, on_delete=models.SET_NULL)
    phid = models.CharField(max_length=50) 
    lcid_temp = models.CharField(max_length=150, null=True, blank=True)
    locality =  models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    inid = models.CharField(max_length=150, null=True, blank=True)
    location =  models.CharField(max_length=150, null=True, blank=True) ## +
    town = models.CharField(max_length=150, null=True, blank=True) ## +
    date = models.CharField(max_length=150, null=True, blank=True) ## +
    caption = models.TextField(null=True, blank=True) ##html
    gps = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=150, null=True, blank=True)
    is_planted = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.CharField(max_length=10, null=True, blank=True)
    native_status = models.CharField(max_length=10, null=True, blank=True, default= "") ## newer FIXME
    nr = models.FloatField(null = True) ## from GalleryPhoto
    herb_id = models.CharField(max_length=10, null=True, blank=True) ## irrelevant
    tags = models.CharField(max_length=256, null=True, blank=True) 
    notes = models.CharField(max_length=256, null=True, blank=True) ## text field
    gps_error = models.CharField(max_length=10, null=True, blank=True) ## irrelevant ?
    reintroduced = models.CharField(max_length=10, null=True, blank=True) ## irrelevant
    
    committed = models.DateTimeField(null=True, blank=True) ## XXX: to change name: taken from file timestamp
    modified = models.DateTimeField(null=True, blank=True) ## auto_now=True

    class Meta:
        abstract = True
        unique_together= (('imid','plant.pnid'),)

    def __str__(self):
        s = "%s : %s/%s %s -- %s @ %s %s" % (self.phid, self.fid, self.spid, 
                               self.latname, self.inid, self.lcid, 
                               self.committed)
        if self.caption:
            s += " --- " + self.caption 
        return s

    @property
    def lcid(self):
        try:
            return self.location.pk
        except:
            return ""


    @property
    def spid(self):
        try:
            return self.plant.pnid
        except:
            return ""

    @property
    def latname(self):
        try:
            return self.plant.latname
        except:
            return ""
    
    @property
    def genname(self):
        try:
            return self.plant.upper.latname
        except:
            return ""

    @property
    def famname(self):
        try:
            return self.plant.upper.upper.latname
        except:
            return ""

    @property
    def authors(self):
        try:
            return self.plant.authors
        except:
            return ""

    @property
    def colnames(self):
        try:
            return self.plant.colnames
        except:
            return ""

    @property
    def fid(self):
        try:
            return self.plant.upper.upper.pnid
        except:
            return None

class VascularImage(AbstractImageRecord):
    class Meta:
        verbose_name_plural = 'Vascular Images'

class NonVascularImage(AbstractImageRecord):
    class Meta:
        verbose_name_plural = 'Non Vascular Images'

class AnimalImage(AbstractImageRecord):
    class Meta:
        verbose_name_plural = 'Animal Images'

class VariaImage(AbstractImageRecord):
    class Meta:
        verbose_name_plural = 'Varia Images'

class DeletedImage(models.Model):
    imid = models.CharField(max_length=50)
    spid = models.IntegerField(null=True, blank=True)
    phid = models.CharField(max_length=50, null=True, blank=True)
    fid = models.IntegerField(null=True, blank=True)
    ## initial / temporary fields
    famname = models.CharField(max_length=150, null=True, blank=True)
    genname = models.CharField(max_length=150, null=True, blank=True)
    latname = models.CharField(max_length=150, null=True, blank=True)
    colnames = models.CharField(max_length=250, null=True, blank=True)
    authors = models.CharField(max_length=150, null=True, blank=True)
    
    lcid = models.CharField(max_length=150, null=True, blank=True)
    inid = models.CharField(max_length=150, null=True, blank=True)
    location =  models.CharField(max_length=150, null=True, blank=True) 
    town = models.CharField(max_length=150, null=True, blank=True) ## redundant
    date = models.CharField(max_length=150, null=True, blank=True) 
    caption = models.TextField(null=True, blank=True) 
    gps = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=150, null=True, blank=True)
    is_verified = models.CharField(max_length=10, null=True, blank=True)
    nr = models.FloatField(null = True)

    is_planted = models.CharField(max_length=10, null=True, blank=True) ## verbose
    herb_id = models.CharField(max_length=10, null=True, blank=True) ## irrelevant
    tags = models.CharField(max_length=256, null=True, blank=True) 
    notes = models.CharField(max_length=256, null=True, blank=True) ## text field

    ## more to add
    gps_error = models.CharField(max_length=10, null=True, blank=True) ## irrelevant ?
    reintroduced = models.CharField(max_length=10, null=True, blank=True) ## irrelevant
    ## ignore posted = > created
    ## ignore att shedevr => ? never used and if can ignore
    committed = models.DateTimeField(null=True, blank=True) 
    modified = models.DateTimeField(null=True, blank=True) ## auto_now=True
    reason = models.CharField(max_length=255)
    uid = models.CharField(max_length=20)

    class Meta:
        unique_together= (('imid','spid'),)
        
    def __str__(self):
        s = "%s : %s %s -- %s @ %s %s" % (self.phid, self.spid, 
                               self.latname, self.inid, self.lcid, 
                               self.committed)
        if self.caption:
            s += " --- " + self.caption 
        return s
         
class FileRecord(models.Model):
    PID = models.CharField(max_length=256, primary_key=True, verbose_name='abspath') ## PID = abspath
    imid = models.CharField(max_length=50) ##redundant or path without name
    device = models.CharField(max_length=50, blank=True) 
    part = models.CharField(max_length=50, blank=True) ## partition
    ## if not empty, PID starts with <device>:<part>:<abspath>
    year = models.IntegerField(blank=True, null=True) ## redundant, for only filtering
    ## abspath = pid without device and part
    md5 = models.CharField(max_length=250, blank=True)
    committed = models.BooleanField(default=False) ## 
    tables = models.CharField(max_length=256, blank=True)
    size = models.IntegerField(null=True, blank=True)
    modified = models.DateTimeField(blank=True)

    scanned = models.DateTimeField(blank=True, default=timezone.now)
    status = models.CharField(max_length=20, blank=True, default="tomcat") 
    ## duplicate tomcat newphoto version (same imid differerent md5)

    def __str__(self):
        s = "%s : %s -- %s [%s]" % (self.imid, self.PID, self.tables,
                               self.modified)
        return s

## to be RE-GENERATED by debugging.name_index_update
class NameIndex(models.Model):
    spid = models.IntegerField()
    name = models.CharField(max_length=200)
    classification = models.CharField(max_length=5)
    category = models.CharField(max_length=15)
    images = models.IntegerField(default=0)
    pubimages = models.IntegerField(null=True, default=0)
    status = models.CharField(max_length=15, null=True, default="valid")  ## valid, legacy, synonym
    long_name = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s [%s]" % (self.name, self.spid, self.category)

## from Tidmarsh
##class Profile(models.Model):
##    user = models.OneToOneField(User, on_delete=models.CASCADE)
##    phidcode = models.CharField(max_length=5, null=True, blank=True)
##    
##    def __str__ (self):
##        return "%s: %s" % (self.user.username, self.phidcode)

##@receiver(post_save, sender=User)
##def create_user_profile(sender, instance, created, **kwargs):
##    if created:
##        Profile.objects.create(user=instance)

##@receiver(post_save, sender=User)
##def save_user_profile(sender, instance, **kwargs):
##    instance.profile.save()

## also from Tidmarsh module
## needs /data/static/uploaded/
class Upload(models.Model):
    ## id = num
    record = models.ForeignKey(TidmarshRecord, null=True, blank=True, on_delete=models.SET_NULL)
    origname = models.CharField(max_length=100, null=True, blank=True)
    tempname = models.CharField(max_length=100, null=True, blank=True)
    savedname = models.CharField(max_length=23, null=True, blank=True)
    size = models.IntegerField()
    scaled = models.CharField(max_length=5, null=True, blank=True)
    browser = models.CharField(max_length=250, null=True, blank=True)
    uid = models.CharField(max_length=5)
    submitted_by = models.CharField(max_length=10, null=True, blank=True)
    latlon = models.CharField(max_length=100, null=True, blank=True)
    taken = models.DateTimeField(null = True, blank=True)
    uploaded = models.DateTimeField(null=True, blank=True)
    
    def __str__ (self):
        return "[%s]: %s from %s [%s] %s %s" % (self.pk, self.savedname,
                                                self.origname, self.size,
                                                self.scaled,
                                                self.uploaded)
 

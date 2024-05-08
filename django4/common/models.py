from django.db import models

## modified from bugzilla form
class BugRecord(models.Model):
    product  = models.CharField(max_length=100, null=True, blank=True, default="salicicola")
    component = models.CharField(max_length=100, null=True, blank=True, default="default")
    version = models.CharField(max_length=100, null=True, blank=True, default="") ## not in use
    reporter = models.CharField(max_length=100, null=True, blank=True, default="AZ", verbose_name="user name")
    actual_user = models.CharField(max_length=50, null=True, blank=True, default="", verbose_name="submitted by")
    severity = models.CharField(max_length=100, null=True, blank=True, default="medium") ## add priority
    priority = models.CharField(max_length=100, null=True, blank=True, default="") ## new
    hardware = models.CharField(max_length=100, null=True, blank=True, default="server") ## not in use
    OS = models.CharField(max_length=100, null=True, blank=True, default="linux") ## not in use
    summary = models.CharField(max_length=50, null=True, blank=True, default="")
    description = models.TextField(null=True, blank=True, default="")
    ##attachement
    ##--- not in bugzilla form ---
    url = models.CharField(max_length=100, null=True, blank=True, default="")
    status = models.CharField(max_length=100, null=True, blank=True, default="committed") ## committed fixed ... not rejected
    created = models.DateTimeField(auto_now_add=True) 
    modified = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return "%s %s %s" % (self.created, self.reporter, self.summary)   

class Town(models.Model):
    locID = models.CharField(max_length=100, primary_key=True)
    state = models.CharField(max_length=100, default="Massachusetts")
    state_abbr = models.CharField(max_length=2, default="MA")
    county = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    modified = models.DateTimeField(null=True)

    def __str__(self):
        return "%s %s %s" % (self.locID, self.county, self.town)

class Location(models.Model):
    lcid = models.CharField(max_length=100, primary_key=True)
    alias = models.CharField(max_length=100, null=True, blank=True)
    long_name = models.CharField(max_length=100, null=True, blank=True)
    public_name = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, default="Massachusetts")
    state_abbr = models.CharField(max_length=2, default="MA")
    county = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    coordinates = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.IntegerField(null=True, blank=True)
    modified = models.DateTimeField(null=True)

    def __str__(self):
        return "%s %s: %s [%s]" % (self.lcid, self.county, self.town, self.public_name)



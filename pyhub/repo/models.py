from django.db import models

class Repo(models.Model):
    path = models.CharField(max_length=255)
    
    def __unicode__(self):
        return "<Repo: %s>" % self.path
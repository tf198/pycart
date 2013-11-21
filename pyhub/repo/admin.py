'''
Created on 21/11/2013

@author: tris
'''
from django.contrib import admin
from repo import models

admin.site.register(models.Repo)
'''
Created on 09/04/2014

@author: tris
'''
import anydbm
import settings

cache_dir = getattr(settings, 'CACHE_DIR', '/tmp')
cache = anydbm.open(cache_dir + '/pycart.db', 'c', 0600)
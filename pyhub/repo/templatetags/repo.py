'''
Created on 21/11/2013

@author: tris
'''
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def timestamp(text):
    from datetime import datetime
    return datetime.fromtimestamp(int(text))
register.filter('timestamp', timestamp)

import re

git_author = re.compile(r'(.*?)\s*<(.*)>')

def gravatar(email, size=20):
    import hashlib
    print email
    url = "http://www.gravatar.com/avatar/{0}?s={1}".format(hashlib.md5(email.strip().lower()).hexdigest(), size)
    return mark_safe('<img src="{0}"/>'.format(url))
register.filter('gravatar', gravatar)

def glyphicon(name):
    return mark_safe('<i class="glyphicon glyphicon-{0}"></i>'.format(name))
register.filter('glyphicon', glyphicon)

def author_link(text):
    match = git_author.match(text)
    if match:
        return mark_safe('<a href="mailto:{1}">{0}</a>'.format(*match.groups()))
    return text
register.filter('author_link', author_link)

def author_gravatar(text, size=20):
    match = git_author.match(text)
    
    if match:
        return gravatar(match.group(2), size)
    return ""
register.filter('author_gravatar', author_gravatar)

def commit_link(sha):
    return mark_safe('<a href="/repo/commit/{0}">{1}</a>'.format(sha, sha[:10]))
register.filter('commit_link', commit_link)
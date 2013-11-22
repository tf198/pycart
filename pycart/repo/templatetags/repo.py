'''
Created on 21/11/2013

@author: tris
'''
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

def timestamp(text):
    ' Convert a timestamp into a datetime '
    from datetime import datetime
    return datetime.fromtimestamp(int(text))
register.filter('timestamp', timestamp)

def gravatar(email, size=20):
    ' Generate <img> tag for gravatar '
    import hashlib
    url = "http://www.gravatar.com/avatar/{0}?s={1}".format(hashlib.md5(email.strip().lower()).hexdigest(), size)
    return mark_safe('<img src="{0}"/>'.format(url))
register.filter('gravatar', gravatar)

def glyphicon(name):
    ' Return bootstrap glyphicon '
    return mark_safe('<i class="glyphicon glyphicon-{0}"></i>'.format(name))
register.filter('glyphicon', glyphicon)

_git_author = re.compile(r'(.*?)\s*<(.*)>')

def _parse_author(text):
    ' Parse git author into name and email '
    match = _git_author.match(text)
    if match:
        return match.groups()
    return text

def author_link(text):
    ' Return a mailto: link for the git author '
    author, email = _parse_author(text)
    if author:
        return mark_safe('<a href="mailto:{0}">{1}</a>'.format(email, author))
    return text
register.filter('author_link', author_link)

def author_gravatar(text, size=20):
    ' Return a gravatar for the git author '
    _author, email = _parse_author(text)
    if email:
        return gravatar(email, size)
    return ""
register.filter('author_gravatar', author_gravatar)

def commit_link(context, sha):
    ' Return a short link to a specific commit '
    from django.core.urlresolvers import reverse
    url = reverse('repo_commit', kwargs={'repo': context['repo'], 'sha': sha})
    return mark_safe('<a href="{0}">{1}</a>'.format(url, sha[:10]))
register.simple_tag(takes_context=True)(commit_link)

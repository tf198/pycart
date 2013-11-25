'''
Created on 21/11/2013

@author: tris
'''
import re
from datetime import datetime

def filemode(mode):
    ' Convert int mode to string representation '
    mask = "rwxrwxrwx"
    
    i = 0400
    result = []
    for x in mask:
        result.append(x if mode & i else '-')
        i >>= 1
    return "".join(result)

def timestamp(text):
    ' Convert a timestamp into a datetime '
    return datetime.fromtimestamp(int(text))

def _timeago(c, unit, plural='s'):
    return '{0} {1}{2}'.format(int(c), unit, plural if c != 1 else '')

def timesince(text):
    ' Convert unix timestamp to a single readable figure e.g. 23 minutes or 3 months'
    d = datetime.now() - timestamp(text)
    
    if d.seconds < 60:
        return _timeago(d.seconds, 'second')
    
    if d.seconds < 3600:
        return _timeago(d.seconds/60, 'minute')
    
    if d.days < 1:
        return _timeago(d.seconds/3600, 'hour')
    
    if d.days < 30:
        return _timeago(d.days, 'day')
    
    if d.days< 365:
        return _timeago(d.days/30.5, 'month')
    
    return _timeago(d.days/365, 'year')

def gravatar(email, size=20):
    ' Generate <img> tag for gravatar '
    import hashlib
    url = "http://www.gravatar.com/avatar/{0}?s={1}".format(hashlib.md5(email.strip().lower()).hexdigest(), size)
    return '<img src="{0}"/>'.format(url)

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
        return '<a href="mailto:{0}">{1}</a>'.format(email, author)
    return text

def author_gravatar(text, size=20):
    ' Return a gravatar for the git author '
    _author, email = _parse_author(text)
    if email:
        return gravatar(email, size)
    return ""


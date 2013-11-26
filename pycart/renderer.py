'''
Created on 23/11/2013

@author: tris
'''
import logging, os

logger = logging.getLogger(__name__)

import sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

modules = {'pygments': False,
           'docutils': False,
           'markdown': False,}

rest_exts = ['rst']
markdown_exts = ['markdown', 'mdown', 'mkdn', 'mkd', 'md']

for mod in modules.keys():
    try:
        __import__(mod)
        modules[mod] = True
        logger.info("Found module: {0}".format(mod))
    except:
        logger.info("Skipping module: {0}".format(mod))

def get_style():
    style = []
    if modules['pygments']:
        from pygments.formatters import HtmlFormatter
        style.append(HtmlFormatter().get_style_defs('.highlight'))
        
    return '\n'.join(style)

def render_file(filename, data):
    # do basic filename identification first
    _root, ext = os.path.splitext(filename)
    
    if modules['docutils'] and ext.lower()[1:] in rest_exts:
        return render_rest(filename, data)
    
    if modules['markdown'] and  ext.lower()[1:] in markdown_exts:
        return render_markdown(filename, data)
    
    if modules['pygments']:
        return render_pygments(filename, data)
    
    # fall back to pre
    return "<pre>{0}</pre>".format(data), {'language': ''}

def render_diff(data):
    if not modules['pygments']:
        return "<pre>{0}</pre>".format(data)
    
    from pygments import lexers, formatters, highlight
    return highlight(data, lexers.DiffLexer(), formatters.HtmlFormatter())

# MODULE SPECIFIC RENDERERS

def render_pygments(filename, data):
    from pygments import lexers, formatters, highlight
    try:
        lexer = lexers.guess_lexer_for_filename(filename, data)
    except:
        lexer = lexers.TextLexer()
    formatter = formatters.HtmlFormatter(linenos=False)
    return highlight(data, lexer, formatter), {'language': lexer.name}

def render_rest(filename, data):
    from docutils.core import publish_parts
    return publish_parts(data, writer_name='html')['html_body'], {'language': 'ReSTructured Text'}

def render_markdown(filename, data):
    import markdown
    return markdown.markdown(data), {'language': 'Markdown'}

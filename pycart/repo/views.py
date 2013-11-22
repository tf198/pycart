# Create your views here.
from django.views.generic import TemplateView, RedirectView
from django.views.generic.base import TemplateResponseMixin
from django.http import Http404
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from django.conf import settings

from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

import git, os, logging

logger = logging.getLogger(__name__)

ACTION_ICONS = {'add': 'file',
                'modify': 'align-left',
                'delete': 'trash'}

def filemode(mode):
    mask = "rwxrwxrwx"
    
    i = 0400
    result = []
    for x in mask:
        result.append(x if mode & i else '-')
        i >>= 1
    return "".join(result)
        

class RepoMixin(TemplateResponseMixin):
    
    def get_repo_path(self):
        
        if not 'repo' in self.kwargs:
            raise Http404("Need to provide a repo")
        
        mappings = getattr(settings, "REPOS", {})
        try:
            return mappings[self.kwargs['repo']]
        except KeyError:
            raise Http404("No such repo: " + self.kwargs['repo'])
        
    def get_repo(self):
        return git.repo(self.get_repo_path())
    
    def get_context_data(self, **kwargs):
        context = super(RepoMixin, self).get_context_data(**kwargs)
        
        self.repo = self.get_repo()
        
        sha = self.kwargs['sha']
        if sha in self.repo:
            context['ref_name'] = sha[:10]
            context['ref_link'] = sha
            self.sha = self.repo[sha]
        else:
            context['ref_name'] = context['ref_link'] = sha
            self.sha = git.get_branch(self.repo, sha)
        
        context['sha'] = self.sha.id
        context['branches'] = git.branches(self.repo)
        context['tags'] = git.tags(self.repo)
        
        path = self.kwargs.get('path', '').strip('/')
        context['path'] = path
        context['breadcrumbs'] = path.split('/') if path else []
        
        return context
        

class RepoListView(RepoMixin, TemplateView):
    template_name = "repo/list.html"
    
    def get_repos(self):
        return getattr(settings, 'REPOS', {})
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        context['repos'] = self.get_repos()
        return context

class RepoSummaryView(RedirectView):
    
    def get_redirect_url(self, **kwargs):
        from django.core.urlresolvers import reverse
        
        return reverse('repo_tree', kwargs={'repo': kwargs['repo'],
                                            'sha': 'master',
                                            'path': ''})
     
class RepoTreeView(RepoMixin, TemplateView):
    template_name = "repo/tree.html"
    
    def get_context_data(self, **kwargs):
        from datetime import datetime
        
        context = super(RepoTreeView, self).get_context_data(**kwargs)
        
        path = context['path']
        listing = []
        data = None
        
        try:
            node = git.get_by_path(self.repo, self.sha, context['breadcrumbs'])
        except IndexError:
            context['error'] = "{0} does not exist in this branch".format(path)
            return context
        
        if hasattr(node, 'items'): # is directory
            last_commit = None
            for e in node.items():
                commit = git.get_commit(self.repo, self.sha, os.path.join(path, e.path))
                
                is_file = e.mode & 0100000
                
                icon = 'file' if is_file else 'folder-open'
                mode = filemode(e.mode) if is_file else ""
                
                listing.append((icon,
                                e.path,
                                commit.message ,
                                mode,
                                datetime.fromtimestamp(commit.commit_time)))
                
                if last_commit is None or commit.commit_time > last_commit.commit_time:
                    last_commit = commit
                
                if e.path.lower().startswith('readme'):
                    data = self.repo[e.sha].data
                    filename = "{0}/{1}".format(context['path'], e.path)
            context['commit'] = last_commit
        else: # is a file
            data = node.data
            context['commit'] = git.get_commit(self.repo, self.sha, path)
            filename = path
        
        if data is not None:
            try:
                lexer = lexers.guess_lexer_for_filename(filename, data)
            except:
                lexer = lexers.TextLexer()
            formatter = HtmlFormatter(linenos=False)
            data = mark_safe(highlight(data, lexer, formatter))
            context['language'] = lexer.name
            context['filename'] = filename
        
        context['data'] = data
        context['listing'] = listing
        context['inline_style'] = HtmlFormatter().get_style_defs('.highlight')
                
        return context
       
class RepoCommitView(RepoMixin, TemplateView):
    template_name = "repo/commit.html"
    
    def get_context_data(self, **kwargs):
        context = super(RepoCommitView, self).get_context_data(**kwargs)
        
        try:
            commit = self.repo[self.kwargs['sha']]
        except KeyError:
            raise Http404("No such commit")
        
        if commit.__class__.__name__ != "Commit":
            raise Http404("Not a valid commit")
        
        files = []
        for change in git.get_changes(self.repo, commit):
            if change.type == 'delete':
                files.append((ACTION_ICONS.get('delete'), change.old.path, commit.parents[0], 'Deleted'))
            else:
                diff = git.unified_diff(self.repo, change.old, change.new)
                html = mark_safe(highlight(diff, lexers.DiffLexer(), HtmlFormatter()))
                
                files.append((ACTION_ICONS.get(change.type, 'fire'), change.new.path, commit.id, html))
        
        context['inline_style'] = HtmlFormatter().get_style_defs('.highlight')
                  
        context['files'] = files
        context['branch'] = commit.id
        context['commit'] = commit
        context['branch_name'] = commit.id[:10]
        
        
        return context
    
class RepoHistoryView(RepoMixin, TemplateView):
    template_name = "repo/history.html"
    
    def get_context_data(self, **kwargs):
        context = super(RepoHistoryView, self).get_context_data(**kwargs)
        
        walker = self.repo.get_walker(include=[self.sha.id], paths=[context['path']])
        context['history'] = [ entry.commit for entry in walker ]
        
        return context
    
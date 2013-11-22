# Create your views here.
from django.views.generic import TemplateView
from django.http import Http404

from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

import git, os
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe
from django.conf import settings

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
        

class RepoMixin(object):
    fixed_repo = None
    
    def get_repo(self):
        
        if self.fixed_repo is not None:
            return self.fixed_repo
        
        if 'repo' in self.kwargs:
            mappings = getattr(settings, "REPOS", {})
            try:
                return mappings[self.kwargs['repo']]
            except KeyError:
                raise Http404("No such repo: " + self.kwargs['repo'])
        
        raise ImproperlyConfigured("Need to provide a repo")

class RepoSummaryView(RepoMixin, TemplateView):
    template_name = "repo/status.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        return context
     
class RepoTreeView(RepoMixin, TemplateView):
    template_name = "repo/tree.html"
    
    def get_context_data(self, **kwargs):
        from datetime import datetime
        import stat
        
        context = TemplateView.get_context_data(self, **kwargs)
        
        path = self.kwargs['path'].strip('/')
        parts = path.split('/') if path else []
        
        repo = git.repo(self.get_repo())
        
        branch = self.kwargs['branch']
        if len(branch) == 40:
            context['branch_name'] = branch[:10]
            branch = repo[branch]
        else:
            context['branch_name'] = branch
            branch = git.get_branch(repo, self.kwargs['branch'])
        
        listing = []
        data = None
        
        context['breadcrumbs'] = parts
        context['branches'] = git.branches(repo)
        
        try:
            node = git.get_by_path(repo, branch, parts)
        except IndexError:
            context['error'] = "{0} does not exist in this branch".format(path)
            return context
        
        if hasattr(node, 'items'): # is directory
            last_commit = None
            for e in node.items():
                commit = git.get_commit(repo, branch, os.path.join(path, e.path))
                
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
                    data = repo[e.sha].data
                    context['path'] = "{0}/{1}".format(context['path'], e.path)
                    filename = e.path
            context['commit'] = last_commit
        else: # is a file
            data = node.data
            context['commit'] = git.get_commit(repo, branch, path)
            filename = path
        
        if data is not None:
            try:
                lexer = lexers.guess_lexer_for_filename(filename, data)
            except:
                lexer = lexers.TextLexer()
            formatter = HtmlFormatter(linenos=False)
            print "LEXER", lexer
            data = mark_safe(highlight(data, lexer, formatter))
            print lexer.filenames
            context['language'] = lexer.name
        
        context['data'] = data
        context['listing'] = listing
        context['inline_style'] = HtmlFormatter().get_style_defs('.highlight')
                
        return context
       
class RepoCommitView(RepoMixin, TemplateView):
    template_name = "repo/commit.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        repo = git.repo(self.get_repo())
        try:
            commit = repo[self.kwargs['commit']]
        except KeyError:
            raise Http404("No such commit")
        
        if commit.__class__.__name__ != "Commit":
            raise Http404("Not a valid commit")
        
        files = []
        for change in git.get_changes(repo, commit):
            print change
            if change.type == 'delete':
                files.append((ACTION_ICONS.get('delete'), change.old.path, commit.parents[0], 'Deleted'))
            else:
                diff = git.unified_diff(repo, change.old, change.new)
                html = mark_safe(highlight(diff, lexers.DiffLexer(), HtmlFormatter()))
                
                files.append((ACTION_ICONS.get(change.type, 'fire'), change.new.path, commit.id, html))
        
        context['inline_style'] = HtmlFormatter().get_style_defs('.highlight')
                  
        context['files'] = files
        context['branch'] = commit.id
        context['commit'] = commit
        
        return context
    
class RepoHistoryView(RepoMixin, TemplateView):
    template_name = "repo/history.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        path = self.kwargs['path'].strip('/')
        
        repo = git.repo(self.get_repo())
        
        branch = self.kwargs['branch']
        if len(branch) == 40:
            context['branch_name'] = branch[:10]
            branch = repo[branch]
        else:
            context['branch_name'] = branch
            branch = git.get_branch(repo, self.kwargs['branch'])
        
        walker = repo.get_walker(include=[branch.id], paths=[path])
        context['history'] = [ entry.commit for entry in walker ]
        
        return context
    
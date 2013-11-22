# Create your views here.
from django.views.generic import TemplateView
from django.http import Http404

import git, os

class RepoSummaryView(TemplateView):
    template_name = "repo/status.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        repo = Repo('.')
        context['repo'] = repo
        
        return context
        
class RepoTreeView(TemplateView):
    template_name = "repo/tree.html"
    repo = "."
    
    def get_context_data(self, **kwargs):
        from datetime import datetime
        
        context = TemplateView.get_context_data(self, **kwargs)
        
        path = self.kwargs['path'].strip('/')
        parts = path.split('/') if path else []
        
        repo = git.repo(self.repo)
        
        branch = git.get_branch(repo, self.kwargs['branch'])
        
        listing = []
        
        context['breadcrumbs'] = parts
        context['branches'] = git.branches(repo)
        context['repo'] = self.repo
        
        try:
            node = git.get_by_path(repo, branch, parts)
        except IndexError:
            context['error'] = "{0} does not exist in this branch".format(path)
            return context
        
        if hasattr(node, 'items'): # is directory
            last_commit = 0
            for e in node.items():
                print e
                commit = git.get_commit(repo, branch, os.path.join(path, e.path))
                listing.append((e.path, commit.message , datetime.fromtimestamp(commit.commit_time)))
                if commit.commit_time > last_commit:
                    last_commit = commit
                if e.path.lower().startswith('readme'):
                    context['data'] = repo[e.sha].data
                    context['path'] = "{0}/{1}".format(context['path'], e.path)
            context['commit'] = last_commit
        else: # is a file
            context['data'] = node.data
            context['commit'] = git.get_commit(repo, branch, path)
        
        context['listing'] = listing
        
        
        
        return context
        

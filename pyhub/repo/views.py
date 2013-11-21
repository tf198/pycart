# Create your views here.
from django.views.generic import TemplateView
from django.http import Http404

from dulwich.repo import Repo

class RepoSummaryView(TemplateView):
    template_name = "repo/status.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        repo = Repo('.')
        context['repo'] = repo
        
        return context
        
class RepoTreeView(TemplateView):
    template_name = "repo/tree.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        path = self.kwargs['path'].strip('/')
        path = path.split('/') if path else []
        print "PATH", path
        
        repo = Repo('.')
        
        head = repo[repo.head()]
        
        node = repo[head.tree]
        
        for p in path:
            print "Node", repr(node)
            
            found = False
            for entry in node.items():
                print "Checking", entry
                if entry.path == p:
                    node = repo[entry.sha]
                    found = True
                    break
                
            if not found:
                raise Http404()
            
        if hasattr(node, 'items'):
            print dir(node)
            context['items'] = [ x.path for x in node.items() ]
        else:
            print dir(node)
            context['blob'] = node
            
        w = repo.get_walker(paths=['/'.join(path)])
        context['commit'] = next(w.__iter__()).commit
        
        return context
        

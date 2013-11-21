# Create your views here.
from django.views.generic import TemplateView
import git

class RepoSummaryView(TemplateView):
    template_name = "repo/status.html"
    
    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        repo = git.Repo('.')
        context['repo'] = repo
        
        return context
        

from django.conf.urls import patterns, include, url
import repo.views

urlpatterns = patterns('',
    url(r'^$', repo.views.RepoListView.as_view(), name="repo_list"),
    url(r'^(?P<repo>\w+)/', include('repo.urls')),
)

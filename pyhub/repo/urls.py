from django.conf.urls import patterns, url
from repo import views

urlpatterns = patterns('',
    url(r'^$', views.RepoSummaryView.as_view()),
    url(r'tree/(?P<branch>\w+)/(?P<path>.*)$', views.RepoTreeView.as_view(repo='.'), name="repo_tree"),
    url(r'history/(?P<branch>\w+)/(?P<path>.*)$', views.RepoHistoryView.as_view(repo='.'), name="repo_history"),
    url(r'commit/(?P<commit>\w+)$', views.RepoCommitView.as_view(repo='test_repo'), name="."),
)

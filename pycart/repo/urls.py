from django.conf.urls import patterns, url
from repo import views

urlpatterns = patterns('',
    url(r'^$', views.RepoSummaryView.as_view()),
    url(r'tree/(?P<sha>\w+)/(?P<path>.*)$', views.RepoTreeView.as_view(), name="repo_tree"),
    url(r'history/(?P<sha>\w+)/(?P<path>.*)$', views.RepoHistoryView.as_view(), name="repo_history"),
    url(r'commit/(?P<sha>\w+)$', views.RepoCommitView.as_view(), name="repo_commit"),
)

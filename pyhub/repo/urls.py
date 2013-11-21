from django.conf.urls import patterns, include, url
from repo import views

urlpatterns = patterns('',
    url(r'^$', views.RepoSummaryView.as_view()),
    url(r'tree/master(?P<path>.*)$', views.RepoTreeView.as_view()),
)

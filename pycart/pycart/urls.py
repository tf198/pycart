from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<repo>\w+)/', include('repo.urls')),
)

"""inspection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from dashboard.views import index
from dashboard.views import pages
from dashboard.views import page
from dashboard.views import daemon
from dashboard.views import login_view
from dashboard.views import logout_view
from dashboard.views import fp_view

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^login/$', login_view),
    url(r'^logout/$', logout_view),
    url(r'^scan/(?P<org_id>\w+)/$',index),
    url(r'^alerts/$',pages),
    url(r'^alerts/(?P<time_frame>\w+)/$',pages),
    url(r'^fp$', fp_view),
    url(r'^org/(?P<org_id>\w+)/$',page),
    url(r'^daemon/$',daemon),
    url(r'^daemon/(?P<jobid>\w+)/$',daemon),
]

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'SleepAssistant.views.home', name='home'),
    # url(r'^SleepAssistant/', include('SleepAssistant.foo.urls')),
    url(r'^sleep/$', 'SleepAssistant.apps.journal.views.sleep'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

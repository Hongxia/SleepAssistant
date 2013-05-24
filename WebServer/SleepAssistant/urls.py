from django.conf.urls import patterns, include, url
import SleepAssistant.apps.journal.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'SleepAssistant.views.home', name='home'),
    # url(r'^SleepAssistant/', include('SleepAssistant.foo.urls')),
    #url(r'^sleep/$', 'SleepAssistant.apps.journal.views.sleep'),
    
    # django-user-accounts
	url(r'^account/login/$', SleepAssistant.apps.journal.views.LoginView.as_view(), name='account_login'),
	url(r'^account/signup/$', SleepAssistant.apps.journal.views.SignupView.as_view(), name='account_signup'),
 	url(r'^account/', include('account.urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

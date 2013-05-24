from django.conf.urls import patterns, include, url
import SleepAssistant.apps.journal.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# journal app
    url(r'^sleep/$', 'SleepAssistant.apps.journal.views.sleep', name='sleep'),
    url(r'^wakeup/$', 'SleepAssistant.apps.journal.views.wakeup', name='wakeup'),
    url(r'^summary/$', 'SleepAssistant.apps.journal.views.summary', name='summary'),
    url(r'^record/(?P<record_id>\d+)/$', 'SleepAssistant.apps.journal.views.record', name='record'),

    # django-user-accounts
	url(r'^account/login/$', SleepAssistant.apps.journal.views.LoginView.as_view(), name='account_login'),
	url(r'^account/signup/$', SleepAssistant.apps.journal.views.SignupView.as_view(), name='account_signup'),
 	url(r'^account/', include('account.urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

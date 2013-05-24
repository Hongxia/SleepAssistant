from django.conf.urls import patterns, include, url
import SleepAssistant.apps.journal.views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# journal app
    url(r'^sleep/$', 'SleepAssistant.apps.journal.views.sleep', name='sleep'),
    url(r'^getup/$', 'SleepAssistant.apps.journal.views.getup', name='getup'),
    url(r'^getup_questions/$', 'SleepAssistant.apps.journal.views.getup_questions', name='getup_questions'),
    url(r'^summary/$', 'SleepAssistant.apps.journal.views.summary', name='summary'),
    url(r'^data/(?P<record_id>\d+)/$', 'SleepAssistant.apps.journal.views.data', name='data'),

    # django-user-accounts
	url(r'^account/login/$', SleepAssistant.apps.journal.views.LoginView.as_view(), name='account_login'),
	url(r'^account/signup/$', SleepAssistant.apps.journal.views.SignupView.as_view(), name='account_signup'),
 	url(r'^account/', include('account.urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

from django.conf.urls import patterns, include, url
import SleepAssistant.apps.journal.views

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
	# journal app
    url(r'^sleep/$', 'SleepAssistant.apps.journal.views.sleep', name='sleep'),
    url(r'^getup/$', 'SleepAssistant.apps.journal.views.getup', name='getup'),
    url(r'^getup_questions/$', 'SleepAssistant.apps.journal.views.getup_questions', name='getup_questions'),
    url(r'^summary/$', 'SleepAssistant.apps.journal.views.summary', name='summary'),
    url(r'^journal/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'SleepAssistant.apps.journal.views.journal_entry', name='journal_entry'),
    url(r'^journal/update/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'SleepAssistant.apps.journal.views.update_journal_entry', name='update_journal_entry'),

    # django-user-accounts
	url(r'^account/login/$', SleepAssistant.apps.journal.views.LoginView.as_view(), name='account_login'),
	url(r'^account/signup/$', SleepAssistant.apps.journal.views.SignupView.as_view(), name='account_signup'),
 	url(r'^account/', include('account.urls')),

    url(r'^$', 'SleepAssistant.apps.journal.views.landingpage', name='landing'),

    # admin
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #url(r'^admin/', include(admin.site.urls)),
)

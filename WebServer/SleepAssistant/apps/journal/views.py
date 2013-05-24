# django imports
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, resolve

# django-user-accounts
import account.views

# models import
from SleepAssistant.apps.journal.models import *

# import forms
from SleepAssistant.apps.journal.forms import *

import sys

class SignupView(account.views.SignupView):
	form_class = SignupForm

	def after_signup(self, form):
		self.create_user_profile(form)
		super(SignupView, self).after_signup(form)

	def create_user_profile(self, form):
		profile = UserProfile(user=self.created_user)
		profile.first_name = form.cleaned_data['first_name']
		profile.last_name = form.cleaned_data['last_name']
		profile.birthday = form.cleaned_data['birthday']
		profile.save()

	def generate_username(self, form):
		username = form.cleaned_data['email']
		return username

class LoginView(account.views.LoginView):
    form_class = LoginEmailForm

@login_required
def sleep(request):
	if request.method == 'POST':
		user = request.user
		profile = UserProfile.objects.get(user=user)
		form = SleepForm(request.POST)
		# should always be valid
		if form.is_valid():
			is_sleep = form.cleaned_data['is_sleep']
			if is_sleep:
				profile.sleep()
			else:
				profile.nap()

			return HttpResponseRedirect(reverse('getup'))
	else:
		form = SleepForm()

	return render(request, 'sleep.html', {
		'form' : form,
	})

@login_required
def getup(request):
	if request.method == 'POST':
		user = request.user
		profile = UserProfile.objects.get(user=user)
		
		# should always be valid
		if profile.is_sleep():
			inbed, getup, time = profile.getup()
			record = profile.get_create_today_record()
			record.record_sleep(inbed, getup)
			return HttpResponseRedirect(reverse('getup_questions'))
		elif profile.is_nap():
			inbed, getup, time = profile.getup()
			record = profile.get_create_today_record()
			record.add_nap_time(time)
			return HttpResponseRedirect(reverse('summary'))

	return render(request, 'getup.html', {})

@login_required
def getup_questions(request):
	if request.method == 'POST':
		user = request.user
		profile = UserProfile.objects.get(user=user)
		form = GetupQuestionsForm(request.POST)
		
		# custom validation required
		if form.is_valid():
			minutes_to_sleep = form.cleaned_data['minutes_to_sleep']
			minutes_to_getup = form.cleaned_data['minutes_to_getup']
			hours_awake_in_sleep = form.cleaned_data['hours_awake_in_sleep']

			record = profile.get_create_today_record()
			record.add_sleep_details(minutes_to_sleep, minutes_to_getup, hours_awake_in_sleep)
			return HttpResponseRedirect(reverse('summary'))
	else:
		form = GetupQuestionsForm()

	return render(request, 'getup_questions.html', {
		'form' : form,
	})

@login_required
def summary(request):
	return render(request , 'summary.html')

@login_required
def data(request, record_id):
	return render(request, 'data.html')
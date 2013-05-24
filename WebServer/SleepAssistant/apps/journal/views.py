# django imports
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required

# django-user-accounts
import account.views

# models import
from SleepAssistant.apps.journal.models import *

# import forms
from SleepAssistant.apps.journal.forms import *

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

def sleep(request):
	pass

def wakeup(request):
	pass

def summary(request):
	pass

def record(request, record_id):
	pass
# django imports
from django import forms
from django.forms.extras.widgets import SelectDateWidget

# django-user-accounts
import account.forms

# models import
from SleepAssistant.apps.journal.models import *

# python import
import sys

class SignupForm(account.forms.SignupForm):
	first_name = forms.CharField(
		max_length=UserProfile._meta.get_field('first_name').max_length,
		required=not UserProfile._meta.get_field('first_name').blank)
	last_name = forms.CharField(
		max_length=UserProfile._meta.get_field('last_name').max_length,
		required=not UserProfile._meta.get_field('last_name').blank)
	birthday = forms.DateField(widget=SelectDateWidget(years=range(1960, 2010)))

	def __init__(self, *args, **kwargs):
		super(SignupForm, self).__init__(*args, **kwargs)
		del self.fields['username']
		self.fields['email'].widget.attrs = { 'placeholder':'you@stanford.edu' }
		self.fields['password'].widget.attrs = { 'placeholder':'password' }
		self.fields['password_confirm'].widget.attrs = { 'placeholder':'password again' }
		self.fields['first_name'].widget.attrs = { 'placeholder':'First Name' }
		self.fields['last_name'].widget.attrs = { 'placeholder':'Last Name' }

class LoginEmailForm(account.forms.LoginEmailForm):
	def __init__(self, *args, **kwargs):
		super(LoginEmailForm, self).__init__(*args, **kwargs)
		self.fields['email'].widget.attrs = { 'placeholder':'you@stanford.edu' }
		self.fields['password'].widget.attrs = { 'placeholder':'password' }

class SleepForm(forms.Form):
	is_sleep = forms.BooleanField(required=False)

class GetupQuestionsForm(forms.Form):
	minutes_to_sleep = forms.IntegerField(required=True)
	minutes_to_getup = forms.IntegerField(required=True)
	hours_awake_in_sleep = forms.DecimalField(required=True, max_digits=4, decimal_places=2)

	def __init__(self, *args, **kwargs):
		super(GetupQuestionsForm, self).__init__(*args, **kwargs)
		self.fields['minutes_to_sleep'].widget.attrs = { 'placeholder':'in minutes' }
		self.fields['minutes_to_getup'].widget.attrs = { 'placeholder':'in minutes' }
		self.fields['hours_awake_in_sleep'].widget.attrs = { 'placeholder':'in hours, x.xx'}
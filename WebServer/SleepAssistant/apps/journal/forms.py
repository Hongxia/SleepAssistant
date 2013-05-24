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
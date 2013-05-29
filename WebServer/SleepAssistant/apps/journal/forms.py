# django imports
from django import forms
from django.forms import ModelForm
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

class JournalEntryForm(ModelForm):
	FEELING_CHOICES = (
    	('1', 'Good'),
    	('2', '2'),
   	   	('3', '3'),
   	  	('4', '4'),
   	  	('5', '5'),
   	   	('6', '6'),
   	   	('7', '7'),
   	   	('8', '8'),
   	   	('9', '9'),
   	   	('10', 'Bad'),
   	)
	DATE_CHOICES = (('0', 'Today'), ('-1', 'Yesterday'))

	in_bed_date = forms.ChoiceField(choices=DATE_CHOICES)
	fall_asleep_date = forms.ChoiceField(choices=DATE_CHOICES)
	in_bed = forms.TimeField(required=False)
	fall_asleep = forms.TimeField(required=False)
	wake_up = forms.TimeField(required=False)
	out_bed = forms.TimeField(required=False)

   	overall_feeling = forms.ChoiceField(choices=FEELING_CHOICES)
   	optimal_time = forms.TimeField(required=False)

	class Meta:
		model = SleepRecord
		fields = ('awake_hours', 'napping_hours', 'grogginess', 'zero_two', 'two_four','four_six', 'six_eight', 'eight_ten', 
			'ten_twelve','twelve_fourteen','fourteen_sixteen', 'sixteen_eighteen',
			'eighteen_twenty' ,'twenty_twenty_two', 'twenty_two_zero')
		widgets = {
			'in_bed': forms.TimeInput(format='%H:%M'),
			'fall_asleep': forms.TimeInput(format='%H:%M'),
			'wake_up': forms.TimeInput(format='%H:%M'),
			'out_bed': forms.TimeInput(format='%H:%M'),
			'optimal_time': forms.TimeInput(format='%H:%M'),
			'in_bed_date': forms.Select(),
			'fall_asleep_date': forms.Select(),
		}

	def __init__(self, *args, **kwargs):
		super(JournalEntryForm, self).__init__(*args, **kwargs)
		self.fields['in_bed'].widget.attrs={'placeholder': 'hh:mm'}	
		self.fields['fall_asleep'].widget.attrs={'placeholder': 'hh:mm'}	
		self.fields['wake_up'].widget.attrs={'placeholder': 'hh:mm'}	
		self.fields['out_bed'].widget.attrs={'placeholder': 'hh:mm'}
		self.fields['awake_hours'].widget.attrs={'placeholder': 'In hours'}
		self.fields['napping_hours'].widget.attrs={'placeholder': 'In hours'}
		self.fields['grogginess'].widget.attrs={'placeholder': 'In Minutes'}

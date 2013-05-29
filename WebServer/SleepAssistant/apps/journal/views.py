# django imports
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, resolve

# django-user-accounts
import account.views

# models import
from SleepAssistant.apps.journal.models import *

# import forms
from SleepAssistant.apps.journal.forms import *

# python imports
import sys
from datetime import date, timedelta

def home(request):
	return HttpResponseRedirect(reverse('summary'))

class SignupView(account.views.SignupView):
	form_class = SignupForm

	def after_signup(self, form):
		self.create_user_profile(form)
		super(SignupView, self).after_signup(form)

	def create_user_profile(self, form):
		profile = UserProfile(user=self.created_user)
		profile.first_name = form.cleaned_data['first_name']
		profile.last_name = form.cleaned_data['last_name']
		profile.save()

	def generate_username(self, form):
		username = form.cleaned_data['email']
		return username

class LoginView(account.views.LoginView):
    form_class = LoginEmailForm

@login_required
def sleep(request):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.is_not_awake():
		return HttpResponseRedirect(reverse('getup'))

	if request.method == 'POST':
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
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if not profile.is_not_awake():
		return HttpResponseRedirect(reverse('sleep'))

	if request.method == 'POST':
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

	return render(request, 'getup.html', {
		"is_sleep" : profile.is_sleep(),
		'in_bed' : profile.onset,
	})

@login_required
def getup_questions(request):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.is_not_awake():
		return HttpResponseRedirect(reverse('getup'))

	if request.method == 'POST':
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

def get_sleep_debt(records):
	debt = 0
	count = 0
	if len(records) > 0:
		for record in records:
			count += 1
			debt += (8 - record.total_time_asleep())

	if count == 0:
		return '-'

	return debt

def get_average_sleep_hours(records):
	total = 0
	count = 0
	if len(records) > 0:
		for record in records:
			count += 1
			total += record.total_time_asleep()

	if count > 0:
		return decimal.Decimal(total)/count
	else: 
		return '-'

def get_average_grogginess(records):
	total = 0
	count = 0
	if len(records) > 0:
		for record in records:
			count += 1
			total += record.grogginess

	if count > 0:
		return decimal.Decimal(total)/count 
	else: 
		return '-'
'''
def get_average_overall_feeling(records):
	total = 0
	count = 0
	for record in records:
		count += 1
		total += record.overall

	if count > 0:
		return decimal.Decimal(total)/count 
	else: 
		return '-'
		'''

@login_required
def summary(request):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.is_not_awake():
		return HttpResponseRedirect(reverse('getup'))

	all_completed_records = SleepRecord.objects.all_completed_records(user)

	return render(request, 'summary.html', {
		'record_count' : len(all_completed_records),
		'sleep_debt' : get_sleep_debt(all_completed_records),
		'average_sleep_hours' : get_average_sleep_hours(all_completed_records),
		'average_grog' : get_average_grogginess(all_completed_records),
		#'average_overall' : get_average_overall_feeling(all_records),
	})

@login_required
def journal_entry(request, year, month, day):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.is_not_awake():
		return HttpResponseRedirect(reverse('getup'))

	try:
		current_date = date(int(year), int(month), int(day))
	except ValueError:
		return HttpResponseNotFound('<h1>Date not valid.</h1>')
	
	''' verifies that record exists '''
	record = SleepRecord.objects.daily_record(user, current_date)

	''' find next_date '''
	next_date = current_date + timedelta(days=1)
	if next_date > datetime.today().date():
		next_date = None

	''' find prev_date '''
	prev_date = current_date - timedelta(days=1)

	# next_date is None if current record is today's record
	return render(request, 'journal_entry.html', {
		'date' : current_date,
		'record' : record,
		'next_date' : next_date,
		'prev_date' : prev_date,
	})

@login_required
def update_journal_entry(request, year, month, day):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if profile.is_not_awake():
		return HttpResponseRedirect(reverse('getup'))

	try:
		current_date = date(int(year), int(month), int(day))
	except ValueError:
		return HttpResponseNotFound('<h1>Date not valid.</h1>')
	
	record = SleepRecord.objects.daily_record(user, current_date)
	if request.method == 'POST':
		if record:
			form = JournalEntryForm(request.POST, instance=record)
		else:
			form = JournalEntryForm(request.POST)

		if form.is_valid():
			record = form.save(commit=False)
			in_bed_time = form.cleaned_data['in_bed']
			fall_asleep_time = form.cleaned_data['fall_asleep']
			wake_up_time = form.cleaned_data['wake_up']
			out_bed_time = form.cleaned_data['out_bed']
			opt_time = form.cleaned_data['optimal_time']

			if in_bed_time:
				if form.cleaned_data['in_bed_date'] == -1:
					yesterday = current_date - timedelta(days=1)
					record.in_bed = datetime.combine(yesterday, in_bed_time)
				else:
					record.in_bed = datetime.combine(current_date, in_bed_time)
			else:
				record.in_bed = None

			if fall_asleep_time:
				if form.cleaned_data['fall_asleep_date'] == -1:
					yesterday = current_date - timedelta(days=1)
					record.fall_asleep = datetime.combine(yesterday, fall_asleep_time)
				else:
					record.fall_asleep = datetime.combine(current_date, fall_asleep_time)
			else:
				record.fall_asleep = None

			if wake_up_time:
				record.wake_up = datetime.combine(current_date, wake_up_time)
			else:
				record.wake_up = None

			if out_bed_time:
				record.out_bed = datetime.combine(current_date, out_bed_time)
			else:
				record.out_bed = None

			if opt_time:
				record.optimal_time = datetime.combine(current_date, opt_time)
			else:
				record.optimal_time = None

			record.user = user
			record.date = current_date
			record.save()

			return HttpResponseRedirect(reverse('journal_entry', args=(year,month,day)))
	else:
		if record is None: 
			form = JournalEntryForm()
		else:

			if record.in_bed and record.in_bed.date() != current_date:
				in_bed_date = -1
			else:
				in_bed_date = 0
				
			if record.fall_asleep and record.fall_asleep.date() != current_date:
				fall_asleep_date = -1
			else:
				fall_asleep_date = 0

			if record.in_bed:
				in_bed = record.in_bed.strftime('%H:%M')
			else:
				in_bed = ''

			if record.fall_asleep:
				fall_asleep = record.fall_asleep.strftime('%H:%M')
			else:
				fall_asleep = ''

			if record.wake_up:
				wake_up = record.wake_up.strftime('%H:%M')
			else:
				wake_up = ''

			if record.out_bed:
				out_bed = record.out_bed.strftime('%H:%M')
			else:
				out_bed = ''

			if record.optimal_time:
				optimal_time = record.optimal_time.strftime('%H:%M')
			else:
				optimal_time = ''

			form = JournalEntryForm(instance=record, initial={ 
				'in_bed' : in_bed,
				'fall_asleep' : fall_asleep,
				'wake_up' : wake_up,
				'out_bed' : out_bed,
				'in_bed_date' : in_bed_date,
				'fall_asleep_date' : fall_asleep_date,
				'optimal_time': optimal_time,
			})

	# next_date is None if current record is today's record
	return render(request, 'update_journal_entry.html', {
		'form' : form,
		'date' : current_date,
		'record' : record,
	})

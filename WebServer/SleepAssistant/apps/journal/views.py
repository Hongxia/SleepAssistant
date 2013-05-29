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

def get_sleep_debt(records):
	debt = 0
	count = 0
	for record in records[0:len(records)-1]:
		count += 1
		debt += (8 - record.total_time_asleep())

	if count == 0:
		return '-'

	return debt

def get_average_sleep_hours(records):
	total = 0
	count = 0
	for record in records[0:len(records)-1]:
		count += 1
		total += record.total_time_asleep()

	if count > 0:
		return decimal.Decimal(total)/count 
	else: 
		return '-'

def get_average_grogginess(records):
	total = 0
	count = 0
	for record in records[0:len(records)-1]:
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
	for record in records[0:len(records)-1]:
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
	all_records = SleepRecord.objects.all_records(user)

	return render(request, 'summary.html', {
		'record_count' : len(all_records) - 1,
		'sleep_debt' : get_sleep_debt(all_records),
		'average_sleep_hours' : get_average_sleep_hours(all_records),
		'average_grog' : get_average_grogginess(all_records),
		#'average_overall' : get_average_overall_feeling(all_records), 				
	})




@login_required
def journal_entry(request, year, month, day):
	user = request.user
	profile = UserProfile.objects.get(user=user)
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
def journal_entry_old(request, record_id):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	
	''' verifies that record exists '''
	record = SleepRecord.objects.get_record(record_id)
	if record is None:
		return HttpResponseNotFound('<h1>Sleep Record not found</h1>')

	''' verifies that record belongs to this user '''
	if record.user != request.user:
		return HttpResponseNotFound('<h1>Access denied</h1>')

	''' find next_id '''
	next_record = record.get_next_record()
	if next_record is None:
		if record.is_last_record:
			next_id = None
		else:
			next_id = 0
	else:
		next_id = next_record.id

	''' find prev_id '''
	prev_record = record.get_prev_record()
	if prev_record is None:
		prev_id = 0
	else:
		prev_id = prev_record.id



	# next_id is None if current record is today's record
	# next_id / prev_id is 0 if it does not exist yet
	return render(request, 'journal_entry.html', {
		'record' : record,
		'next_id' : next_id,
		'prev_id' : prev_id,
	})



@login_required
def update_journal_entry(request, year, month, day):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	try:
		current_date = date(int(year), int(month), int(day))
	except ValueError:
		return HttpResponseNotFound('<h1>Date not valid.</h1>')
	
	if request.method == 'POST':
		form = JournalEntryForm(request.POST)
		if form.is_valid():
			record = form.save(commit=False)
			
			in_bed_time = form.cleaned_data['in_bed']
			fall_asleep_time = form.cleaned_data['fall_asleep']
			wake_up_time = form.cleaned_data['wake_up']
			out_bed_time = form.cleaned_data['out_bed']
			if form.cleaned_data['in_bed_yesterday']:
				yesterday = current_date - timedelta(days=1)
				record.in_bed = datetime.combine(yesterday, in_bed_time)
			else:
				record.in_bed = datetime.combine(current_date, in_bed_time)

			if form.cleaned_data['fall_asleep_yesterday']:
				yesterday = current_date - timedelta(days=1)
				record.fall_asleep = datetime.combine(yesterday, fall_asleep_time)
			else:
				record.fall_asleep = datetime.combine(current_date, fall_asleep_time)

			record.wake_up = datetime.combine(current_date, wake_up_time)
			record.out_bed = datetime.combine(current_date, out_bed_time)

			record.user = user
			record.date = current_date
			record.save()

			return HttpResponseRedirect(reverse('journal_entry', args=(year,month,day)))
	else:
		record = SleepRecord.objects.daily_record(user, current_date)
		if record is None: 
			form = JournalEntryForm()
		else:
			form = JournalEntryForm(instance=record, initial={ 
				'in_bed_time' : record.in_bed.time(),
				'fall_asleep_time' : record.fall_asleep.time(),
				'wake_up_time' : record.wake_up.time(),
				'out_bed_time' : record.out_bed.time(),
				'in_bed_yesterday' : record.in_bed.date() != current_date,
				'fall_asleep_yesterday' : record.fall_asleep.date() != current_date,
			})

	# next_date is None if current record is today's record
	return render(request, 'update_journal_entry.html', {
		'form' : form,
		'date' : current_date,
		'record' : record,
	})

@login_required
def update_alertness(request, year, month, day):
	user = request.user
	profile = UserProfile.objects.get(user=user)
	try:
		current_date = date(int(year), int(month), int(day))
	except ValueError:
		return HttpResponseNotFound('<h1>Date not valid.</h1>')
	
	if request.method == 'POST':
		form = AlertnessEntryForm(request.POST)
		if form.is_valid():
			current_date = date(int(year), int(month), int(day))
			record = SleepRecord.objects.daily_record(user, current_date)
			record.zero_two = form.cleaned_data['zero_two']
			record.two_four = form.cleaned_data['two_four']
			record.four_six = form.cleaned_data['four_six']
			record.six_eight = form.cleaned_data['six_eight']
			record.eight_ten = form.cleaned_data['eight_ten']
			record.ten_twelve = form.cleaned_data['ten_twelve']
			record.twelve_fourteen = form.cleaned_data['twelve_fourteen']
			record.fourteen_sixteen = form.cleaned_data['fourteen_sixteen']
			record.sixteen_eighteen = form.cleaned_data['sixteen_eighteen']
			record.eighteen_twenty = form.cleaned_data['eighteen_twenty']
			record.twenty_twenty_two = form.cleaned_data['twenty_twenty_two']
			record.twenty_two_zero = form.cleaned_data['twenty_two_zero']
			record.overall = form.cleaned_data['overall_feeling']
			opt_time = form.cleaned_data['optimal_time']
			record.optimal_time = datetime.combine(current_date, opt_time)
			record.save()
			return HttpResponseRedirect(reverse('journal_entry', args=(year,month,day)))
	else:
		record = SleepRecord.objects.daily_record(user, current_date)
		form = AlertnessEntryForm()
		# form = AlertnessEntryForm(instance=record, initial={ 

		# 	'zero_two': record.zero_two,
		# 	'two_four':	record.two_four,
		# 	'four_six': record.four_six,
		# 	'six_eight': record.six_eight,
		# 	'eight_ten': record.eight_ten,
		# 	'ten_twelve': record.ten_twelve,
		# 	'twelve_fourteen': record.twelve_fourteen,
		# 	'fourteen_sixteen': record.fourteen_sixteen,
		# 	'sixteen_eighteen': record.sixteen_eighteen,
		# 	'eighteen_twenty': record.eighteen_twenty,
		# 	'twenty_twenty_two': record.twenty_twenty_two,
		# 	'twenty_two_zero': record.twenty_two_zero,
		# 	'optimal_time':record.

		# 	record.two_four = form.cleaned_data['two_four']
		# 	record.four_six = form.cleaned_data['four_six']
		# 	record.six_eight = form.cleaned_data['six_eight']
		# 	record.eight_ten = form.cleaned_data['eight_ten']
		# 	record.ten_twelve = form.cleaned_data['ten_twelve']
		# 	record.twelve_fourteen = form.cleaned_data['twelve_fourteen']
		# 	record.fourteen_sixteen = form.cleaned_data['fourteen_sixteen']
		# 	record.sixteen_eighteen = form.cleaned_data['sixteen_eighteen']
		# 	record.eighteen_twenty = form.cleaned_data['eighteen_twenty']
		# 	record.twenty_twenty_two = form.cleaned_data['twenty_twenty_two']
		# 	record.twenty_two_zero = form.cleaned_data['twenty_two_zero']
		# 	record.overall = form.cleaned_data['overall_feeling']
		# 	opt_time = form.cleaned_data['optimal_time']
		# 	record.optimal_time = datetime.combine(current_date, opt_time)



		# 		'in_bed_time' : record.in_bed.time(),
		# 		'fall_asleep_time' : record.fall_asleep.time(),
		# 		'wake_up_time' : record.wake_up.time(),
		# 		'out_bed_time' : record.out_bed.time(),
		# 		'in_bed_yesterday' : record.in_bed.date() != current_date,
		# 		'fall_asleep_yesterday' : record.fall_asleep.date() != current_date,
		# })

	# next_date is None if current record is today's record
	return render(request, 'update_alertness_entry.html', {
		'form' : form,
		'date' : current_date,
		'record' : record,
	})

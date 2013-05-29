# django imports
from django.db import models
from django.contrib.auth.models import User

# python imports
from datetime import datetime, timedelta
from django.utils.timezone import utc
import sys, decimal

class UserProfile(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	user = models.ForeignKey(User, unique=True)

	# state
	YEAR_IN_SCHOOL_CHOICES = (
	    ('NA', 'Nap'),
	    ('SL', 'Sleep'),
	    ('AW', 'Awake'),
	)
	state = models.CharField(max_length=2, default='AW')
	onset = models.DateTimeField(blank=True, null=True)

	def get_create_today_record(self):
		today = datetime.today().date()
		record = SleepRecord.objects.daily_record(self.user, today)
		if record is None:
			record = SleepRecord(user=self.user, date=today)
			record.save()

		return record

	def is_nap(self):
		return self.state == 'NA'

	def is_sleep(self):
		return self.state == 'SL'

	def nap(self):
		self.state = 'NA'
		self.onset = datetime.utcnow().replace(tzinfo=utc)
		self.save()

	def sleep(self):
		self.state = 'SL'
		self.onset = datetime.utcnow().replace(tzinfo=utc)
		self.save()

	# returns a timedelta object
	def getup(self):
		self.state = 'AW'
		getup = datetime.utcnow().replace(tzinfo=utc)
		inbed = self.onset
		time_slept = getup - inbed
		self.onset = None
		self.save()
		return inbed, getup, time_slept

class SleepRecordManager(models.Manager):
	def all_records(self, user):
		return self.filter(user=user)

	def weekly_records(self, user, date):
		weekday = date.weekday()
		monday = date - timedelta(days=weekday-1)
		sunday = monday + timedelta(days=7)
		return self.filter(user=user, date__gte=monday, date__lte=sunday)

	def daily_record(self, user, date):
		try:
			record = self.get(user=user, date=date)
			return record
		except SleepRecord.DoesNotExist:
			return None

	def get_record(self, id):
		try:
			record = self.get(pk=id)
			return record
		except SleepRecord.DoesNotExist:
			return None

class SleepRecord(models.Model):
	objects = SleepRecordManager()
	# user
	user = models.ForeignKey(User, related_name='sleep_records')
	date = models.DateField()

	# sleep related times
	in_bed = models.DateTimeField(blank=True, null=True)
	fall_asleep = models.DateTimeField(blank=True, null=True)
	wake_up = models.DateTimeField(blank=True, null=True)
	out_bed = models.DateTimeField(blank=True, null=True)
	awake_hours = models.DecimalField(default=0, max_digits=4, decimal_places=2)
	napping_hours = models.DecimalField(default=0, max_digits=4, decimal_places=2)
	grogginess = models.IntegerField(blank=True, null=True)

	# alertness
	ALERTNESS = (
		(1, 'Alert'),
		(2, 'Slowed'),
		(3, 'Tired'),
		(4, 'Exhausted'),
		(5, 'Drowsy'),
		(6, 'Asleep'),
	)
	zero_two = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	two_four = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	four_six = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	six_eight = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	eight_ten = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	ten_twelve = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	twelve_fourteen = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	fourteen_sixteen = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	sixteen_eighteen = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	eighteen_twenty = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	twenty_twenty_two = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	twenty_two_zero = models.IntegerField(blank=True, null=True, choices=ALERTNESS)
	optimal_time = models.DateTimeField(blank=True, null=True)
	overall = models.IntegerField(blank=True, null=True)

	# sleep altering factors
	inducing_factor = models.TextField(blank=True)
	inhibiting_factor = models.TextField(blank=True)

	class Meta:
		ordering = ['user', 'date']
		unique_together = ('user', 'date')

	def __unicode__(self):
		return 'Sleep Record of %s on %s' % (self.user.get_full_name(), self.get_weekday())

	def get_weekday(self):
		weekday = self.date.weekday()
		weekday_strings = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
		return weekday_strings[weekday]

	def get_dreams_count(self):
		return len(self.dream_records)

	def is_last_record(self):
		return self.date == datetime.today().date()

	''' navigation methods '''
	def get_next_record(self):
		next = self.date + timedelta(days=1)
		record = SleepRecord.objects.daily_record(self.user, next)
		return record

	def get_prev_record(self):
		previous = self.date + timedelta(days=1)
		record = SleepRecord.objects.daily_record(self.user, previous)
		return record

	''' these are functions that updates the record '''
	def add_nap_time(self, timedelta):
		napped_hours = decimal.Decimal(timedelta.seconds)/3600
		self.napping_hours += napped_hours
		self.save()

	def record_sleep(self, inbed, outbed):
		self.in_bed = inbed
		self.out_bed = outbed
		self.save()

	def add_sleep_details(self, minutes_to_sleep, minutes_to_getup, hours_awake_in_sleep):
		self.fall_asleep = self.in_bed + timedelta(minutes=minutes_to_sleep)
		self.wake_up = self.out_bed - timedelta(minutes=minutes_to_getup)
		self.awake_hours = hours_awake_in_sleep
		self.save()

	''' these are the calculated fields in the journal '''
	def time_awake_in_bed(self):
		seconds_awake = ((self.fall_asleep - self.in_bed) + (self.out_bed - self.wake_up)).seconds
		return decimal.Decimal(seconds_awake)/3600

	def time_asleep_at_night(self):
		seconds_asleep = (self.wake_up - self.fall_asleep).seconds
		return decimal.Decimal(seconds_asleep)/3600

	def total_time_asleep(self):
		return self.napping_hours + self.time_asleep_at_night()

class DreamRecordManager(models.Manager):
	def all_dreams(self, user):
		return self.filter(sleep_record__user=user)

class DreamRecord(models.Model):
	objects = DreamRecordManager()
	sleep_record = models.ForeignKey(SleepRecord, related_name='dream_records')

	# dream types
	TYPES = (
		('N', 'Nightmare'),
		('L', 'Lucid'),
		('X', 'N/A'),
	)
	type = models.CharField(max_length=1, choices=TYPES)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['sleep_record']
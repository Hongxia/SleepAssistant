# django imports
from django.db import models
from django.contrib.auth.models import User

# python imports
from datetime import datetime, timedelta

class SleepRecordManager(models.Manager):
	def all_records(self, user):
		return self.filter(user=user)

	def weekly_records(self, user, date):
		weekday = date.weekday()
		monday = date - datetime.timedelta(days=weekday-1)
		sunday = monday + datetime.timedelta(days=7)
		return self.filter(user=user, date__gte=monday, date__lte=sunday)

class SleepRecord(models.Model):
	objects = SleepRecordManager()
	# user
	user = models.ForeignKey(User, related_name='sleep_records')
	date = models.DateField(auto_now_add=True)

	# sleep related times
	in_bed = models.TimeField(blank=True, null=True)
	fall_asleep = models.TimeField(blank=True, null=True)
	wake_up = models.TimeField(blank=True, null=True)
	out_bed = models.TimeField(blank=True, null=True)
	awake_hours = models.DecimalField(default=0, max_digits=4, decimal_places=2)
	napping_hours = models.DecimalField(default=0, max_digits=4, decimal_places=2)
	grogginess = models.IntegerField(default=0)

	# alertness
	ALERTNESS = (
		(1, 'Alert'),
		(2, 'Slowed'),
		(3, 'Tired'),
		(4, 'Exhausted'),
		(5, 'Drowsy'),
		(6, 'Asleep'),
	)
	zero_two = models.IntegerField(blank=True, choices=ALERTNESS)
	two_four = models.IntegerField(blank=True, choices=ALERTNESS)
	four_six = models.IntegerField(blank=True, choices=ALERTNESS)
	six_eight = models.IntegerField(blank=True, choices=ALERTNESS)
	eight_ten = models.IntegerField(blank=True, choices=ALERTNESS)
	ten_twelve = models.IntegerField(blank=True, choices=ALERTNESS)
	twelve_fourteen = models.IntegerField(blank=True, choices=ALERTNESS)
	fourteen_sixteen = models.IntegerField(blank=True, choices=ALERTNESS)
	sixteen_eighteen = models.IntegerField(blank=True, choices=ALERTNESS)
	eighteen_twenty = models.IntegerField(blank=True, choices=ALERTNESS)
	twenty_twenty_two = models.IntegerField(blank=True, choices=ALERTNESS)
	twenty_two_zero = models.IntegerField(blank=True, choices=ALERTNESS)
	optimal_time = models.TimeField(blank=True, null=True)
	overall = models.IntegerField(blank=True)

	# sleep altering factors
	inducing_factor = models.TextField(blank=True)
	inhibiting_factor = models.TextField(blank=True)

	class Meta:
		ordering = ['user', 'date']

	def __unicode__(self):
		return 'Sleep Record of %s on %s' % (self.user.get_full_name(), self.get_weekday())

	def get_weekday(self):
		weekday = self.date.weekday()
		weekday_strings = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
		return weekday_strings[weekday]

	def get_dreams_count(self):
		return len(self.dream_records)

class DreamRecordManager(models.Manager):
	def all_dreams(self, user):
		return self.filter(sleep_record__user=user)

class DreamRecord(models.Model):
	objects = DreamRecordManager()
	sleep_record = models.ForeignKey(SleepRecord, related_name='dream_records')

	# dream type
	TYPES = (
		('N', 'Nightmare'),
		('L', 'Lucid'),
		('X', 'N/A'),
	)
	type = models.CharField(max_length=1, choices=TYPES)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ['sleep_record']
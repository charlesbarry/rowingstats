from django.db import models

# commentary on the below
# TODO: Create ProgressionRule - ForeignKey of Race, which specifies how crews progress
# TODO: Possibly create CompetitionInstance - eg Rio Olympics

# HOCR, HRR, HORR, Marlow etc
class Competition(models.Model):
	name = models.CharField(max_length=200)
	
	def __str__(self):
		return self.name

# Event is M2-, W2x, Temple, PA etc, IM14+ - unique to each Competition (M2- of Olympics not M2- of World Cup)
class Event(models.Model):
	name = models.CharField(max_length=100)
	comp = models.ForeignKey(Competition, on_delete=models.PROTECT)
	
	type_choices = (
		('Sweep', 'Sweep'),
		('Sculling', 'Sculling'),
		('Lwt Sweep', 'Lightweight Sweep'),
		('Lwt Sculling', 'Lightweight Sculling'),
		('Para-Sweep', 'Para-Sweep'),
		('Para-Sculling', 'Para-Sculling'),
	)
	type = models.CharField(max_length=20, choices=type_choices, default='Sweep')
	distance = models.CharField(max_length=20, default="2000m")
	
	def __str__(self):
		return str(self.comp.name) +": "+ self.name
		
	def next(self):
		try:
			return Event.objects.get(pk=self.pk+1)
		except:
			return None
			
	def previous(self):
		try:
			return Event.objects.get(pk=self.pk-1)
		except:
			return None
	
	# old stackoverflow tip
	class Meta:
		ordering = ['comp__name', 'name']
	
class Rower(models.Model):
	name = models.CharField(max_length=100)
	
	# to be implemented, left out for now for simplicity
	#lightweight = models.BooleanField() - may be moved to be result attribute
	#u20 = lightweight = models.BooleanField()
	#u23 = lightweight = models.BooleanField()
	#BUCS = lightweight = models.BooleanField()
	#retired = boolean
	gender_choices = (
		('M', 'M'),
		('W', 'W'),
		('U', 'U'),
	)
	gender = models.CharField(max_length=1, choices=gender_choices, default='M')
	nationality = models.CharField(max_length=8, default="GBR")
	#iscox = models.BooleanField(default=False)
	
	# world rowing ID number
	wrid = models.IntegerField(null=True, blank=True, verbose_name='World Rowing ID', unique=True)

	def __str__(self):
		return self.name
		
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)

# Used to define a set of fixtures - e.g. the 2016 Olympics or 2017 HRR
class Edition(models.Model):
	name = models.CharField(max_length=100)
	comp = models.ForeignKey(Competition, on_delete=models.PROTECT)
	
	def __str__(self):
		return self.name

# Also known as Knockout in earlier version of this code (debating to rename this as a Tournament)
# This is the M2- at the Rio Olympics - it's a set of races within a given competition
class Fixture(models.Model):
	event = models.ForeignKey(Event, on_delete=models.PROTECT)
	edition = models.ForeignKey(Edition, null=True, blank=True, on_delete=models.CASCADE)
	rounds = models.PositiveSmallIntegerField(default=1)
	complete = models.BooleanField(default=False)
	
	def __str__(self):
		return (self.event.name + ' - ' + str(self.year))

# M2- FA, Final of PA etc		
class Race(models.Model):
	name = models.CharField(max_length=200)
	date = models.DateField("Race date")
	raceclass = models.CharField("Class", max_length=100, null=True, blank=True)
	event = models.ForeignKey(Event, on_delete=models.PROTECT)
	rnumber = models.IntegerField(null=True, blank=True, verbose_name="Race Number", help_text="If helpful, this can be used to store race numbers.")
	# for separating TTs, Heats, SFs and Fs conducted on the same day
	order_choices = (
		(0, 'TT/Heat/Single race'),
		(1, 'Semi-Final'),
		(2, 'Final'),
	)
	order = models.PositiveSmallIntegerField(default=0, choices=order_choices)
	
	# to be implemented
	# location = 
	
	complete = models.BooleanField(default=True, help_text="If set to True (checked) the Race will be used in calculating scores and displayed publicly. Leave unchecked for incomplete races. Useful for big races that need to be done in chunks.")
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
	
	# progression fields
	progression = models.ManyToManyField('self', through='RaceLink', through_fields=('startrace','endrace'), symmetrical=False)
	
	# perhaps add predecessor and successor fields?

	def __str__(self):
		return self.name
		
	def next(self):
		try:
			return Race.objects.get(pk=self.pk+1)
		except:
			return None
			
	def previous(self):
		try:
			return Race.objects.get(pk=self.pk-1)
		except:
			return None

# used to create a map of races - eg linking semis to final
# creates a directed graph - e.g. positions 1,2,3 from heat to semi
class RaceLink(models.Model):
	startrace = models.ForeignKey(Race, on_delete=models.CASCADE)
	endrace = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='endrace')
	'''type_choices = (
		('Predecessor', 'Predecessor'),
		('Successor', 'Successor'),
	)
	type = models.CharField(max_length=15, choices=type_choices)'''
	
	positions = models.CharField(max_length=15)
	
	def __str__(self):
		return self.startrace.name + " progressing positions " + self.positions + " to " + self.endrace.name

class Club(models.Model):
	name = models.CharField(max_length=200)
	
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
	countrycode = models.CharField(max_length=3, help_text="Used for national crews, provides the nationality code in international races", blank=True, null=True)
	country = models.CharField(max_length=200, default="UK", null=True, blank=True)
	
	def __str__(self):
		return self.name
	
class Result(models.Model):
	race = models.ForeignKey(Race, on_delete=models.CASCADE)
	position = models.IntegerField(null=True, blank=True)
	crew = models.ManyToManyField(Rower, blank=True)
	# Not to store club membership for each rower, but indirectly through the race entry
	clubs = models.ManyToManyField(Club, blank=True)
	# eg A, B crew
	flag = models.CharField(max_length=10, null=True, blank=True)
	
	# to be implemented
	# club = foreignkey
	# time = timefields or perhaps 1toM relationship?
	# cox threw some errors and probably needs to be a M2M relationship too
	cox = models.ForeignKey(Rower, on_delete=models.SET_NULL, null=True, blank=True, related_name='cox')
	# lwt field - can be used for determining whether crew members are lightweight
	
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
	
	def __str__(self):
		return str(self.race)+": #"+str(self.position)
		
class Time(models.Model):
	result = models.ForeignKey(Result, on_delete=models.CASCADE)
	description = models.CharField(max_length=100)
	value = models.TimeField()
	order = models.PositiveSmallIntegerField(default=0)
	
	class Meta:
		unique_together = ['result', 'description']
		ordering = ['order']
		
	def __str__(self):
		return str(self.result.race.name) + ' (' + str(self.result.position) + ') - ' + self.description + ' :- ' + str(self.value) + ' (' + str(self.order) + ')'
		
class Alias(models.Model):
	rower = models.ForeignKey(Rower, on_delete=models.CASCADE)
	value = models.CharField(max_length=200)
	temp = models.BooleanField(default=False)
	
	# used to avoid filling with duplicates
	class Meta:
		unique_together = ['rower', 'value']
		verbose_name_plural = 'aliases'
		
	def __str__(self):
		return str(self.value) + " for " + str(self.rower.name)
		
class ClubAlias(models.Model):
	club = models.ForeignKey(Club, on_delete=models.CASCADE)
	value = models.CharField(max_length=200)
	
	# used to avoid filling with duplicates
	class Meta:
		unique_together = ['club', 'value']
		verbose_name_plural = 'clubAliases'
		
	def __str__(self):
		return str(self.value) + " for " + str(self.club.name)
	
class Score(models.Model):
	''' Not needed as can be pulled through from Event through Race
	type_choices = (
		('Sweep', 'Sweep'),
		('Sculling', 'Sculling'),
	)
	type = models.CharField(max_length=10, choices=type_choices, default='Sweep')'''
	mu = models.FloatField(default=100.0)
	sigma = models.FloatField(default=10)
	#date = models.DateField("Score date")
	rower = models.ForeignKey(Rower, on_delete=models.CASCADE)
	# used to access race name and date - now done via result then race
	#race = models.ForeignKey(Race, on_delete=models.PROTECT)
	result = models.ForeignKey(Result, on_delete=models.CASCADE)
	
	def __str__(self):
		return str(self.rower)+" - "+str(round(self.mu,2))+", "+str(round(self.sigma,2))+" - "+str(self.result.race.event.type)+" - "+str(self.result.race.date)
		
class ScoreRanking(models.Model):
	mu = models.FloatField(default=100.0)
	sigma = models.FloatField(default=10)
	delta_mu_sigma = models.FloatField(default=90.0)
	rower = models.ForeignKey(Rower, on_delete=models.CASCADE)
	date = models.DateField("Score date")
	type = models.CharField(max_length=20, default='Sweep')
	
	sr_choices = (
		('Current', 'Current'),
		('All time', 'All time'),
	)
	sr_type = models.CharField(max_length=20, choices=sr_choices, default='Current')

# KNOCKOUT-ONLY CLASSES
# There are a number of issues with this section of the schema, largely stemming from the rushed nature of their development
# 1) These only work for 1 vs 1 knockouts, with no extension to multilane racing
# 2) The referencing of crews is poor, leading to duplication or extensive error handling
	
class KnockoutRace(models.Model):
	knockout = models.ForeignKey(Fixture, null=True, blank=True, on_delete=models.CASCADE)
	race = models.OneToOneField(Race, null=True, blank=True, on_delete=models.SET_NULL)
	child = models.ForeignKey('self', null=True, blank=True, related_name='parent', on_delete=models.SET_NULL)
	round = models.PositiveSmallIntegerField(default=0)
	slot = models.PositiveSmallIntegerField(default=0)
	selected = models.BooleanField(default=False)
	bye = models.BooleanField(default=False)
	margin = models.CharField(max_length=50, null=True, blank=True)
	
	def __str__(self):
		return str(self.knockout) + ', round=' + str(self.round) + ', slot=' + str(self.slot)
		
class MatchProb(models.Model):
	knockout = models.ForeignKey(Fixture, on_delete=models.CASCADE)
	crewAname = models.CharField(max_length=100)
	crewBname = models.CharField(max_length=100)
	day = models.DateField()
	dayn = models.CharField(max_length=20, null=True)
	winprob = models.FloatField()
	
	def __str__(self):
		return self.crewAname + ' to beat ' + self.crewBname + ' - ' + str(round(self.winprob*100, 2)) + '% probability'
	
class CumlProb(models.Model):
	knockout = models.ForeignKey(Fixture, on_delete=models.CASCADE)
	crewname = models.CharField(max_length=100)
	day = models.DateField()
	dayn = models.CharField(max_length=20, null=True)
	cumlprob = models.FloatField()
	
	def __str__(self):
		return self.crewname + ' to win ' ' - ' + str(round(self.cumlprob*100, 2)) + '% probability'
	
class KnockoutCrew(models.Model):
	knockout = models.ForeignKey(Fixture, on_delete=models.CASCADE)
	crewname = models.CharField(max_length=100)
	startingslot = models.PositiveSmallIntegerField(default=0)
	
	def __str__(self):
		return self.crewname + ' - ' + str(self.knockout)
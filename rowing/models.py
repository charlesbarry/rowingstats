from django.db import models

# commentary on the below
# Race is M2- FA, Final of PA etc
# Event is M2-, W2x, Temple, PA etc, IM14+
# Competition is HOCR, HRR, HORR, Marlow etc
# View for Competition - select each competition, 
# Then filter Events by year, generating page where you can select year
# Then see Events for that year

class Competition(models.Model):
	name = models.CharField(max_length=200)
	
	def __str__(self):
		return self.name

class Event(models.Model):
	name = models.CharField(max_length=100)
	comp = models.ForeignKey(Competition, on_delete=models.PROTECT)
	
	type_choices = (
		('Sweep', 'Sweep'),
		('Sculling', 'Sculling'),
	)
	type = models.CharField(max_length=10, choices=type_choices, default='Sweep')
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

	def __str__(self):
		return self.name
		
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
		
class Race(models.Model):
	name = models.CharField(max_length=100)
	date = models.DateField("Race date")
	raceclass = models.CharField("Class", max_length=100, null=True, blank=True)
	event = models.ForeignKey(Event, on_delete=models.PROTECT)
	# for separating TTs, Heats, SFs and Fs conducted on the same day
	order_choices = (
		(0, 'TT/Heat/Single race'),
		(1, 'Semi-Final'),
		(2, 'Final'),
	)
	order = models.PositiveSmallIntegerField(default=0, choices=order_choices)
	
	# to be implemented
	# location = 
	
	complete = models.BooleanField(default=True, help_text="If set to True (checked) the Race will be published and will be used in calculating scores. Leave unchecked for incomplete races. Useful for big races that need to be done in chunks.")
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)

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
		
class Club(models.Model):
	name = models.CharField(max_length=200)
	
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
	
	def __str__(self):
		return self.name
	
class Result(models.Model):
	race = models.ForeignKey(Race, on_delete=models.PROTECT)
	position = models.IntegerField()
	crew = models.ManyToManyField(Rower)
	# Not to store club membership for each rower, but indirectly through the race entry
	clubs = models.ManyToManyField(Club)
	# eg A, B crew
	flag = models.CharField(max_length=10, null=True, blank=True)
	
	# to be implemented
	# club = foreignkey
	# time = timefields or perhaps 1toM relationship?
	# cox threw some errors and probably needs to be a M2M relationship too
	# cox = models.ForeignKey(Rower, on_delete=models.PROTECT, null=True, blank=True)
	# lwt field - can be used for determining whether crew members are lightweight
	
	last_updated = models.DateTimeField("Last updated", auto_now=True)
	created = models.DateTimeField("Created on", auto_now_add=True)
	
	def __str__(self):
		return str(self.race)+": #"+str(self.position)
	
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
	rower = models.ForeignKey(Rower, on_delete=models.PROTECT)
	date = models.DateField("Score date")
	type = models.CharField(max_length=10, default='Sweep')
# creates one on one probabilities and then updates those accordingly
# for each of the crews in the first round of each knockout, compare against every other crew
# # get crewname from results data
# # get latest mu and sigma for each crew
# # run prob calc on each combination
# # if have beaten them on prior day, need to change prob to 1 or 0 (use a 'have beaten' flag)
# save prob calc and crew names in DB

# run recursive calculation on each 

# crew data structure: [crewname, [crewmembers]]
# matches 

from rowing.models import Event, Race, EventInstance, KnockoutRace, Result, MatchProb, CumlProb, Score, KnockoutCrew
from scipy.stats import norm
from math import floor
import datetime, itertools

def CPcalc(ccrew, knockout, r, slot, day, indent):
	#print("-"*indent, "Starting CPcalc2 with slot=%s, r=%s" % (slot, r))
	if r == 0:
		#print("-"*indent, "Returning 1")
		return 1
	else:
		v = 1 + 2**(r-1) + (2**(r+1))*floor((slot-1)/(2**r)) - (2**(r-1))*floor((slot-1)/(2**(r-1)))
		u = v + 2**(r-1) - 1
		probsum = 0
		for item in range(v, u+1):
			# add p(i,k) * recursive
			try:
				othcrew = KnockoutCrew.objects.get(knockout=knockout, startingslot=item)
			except KnockoutCrew.DoesNotExist:
				raise	
			try:
				mp = MatchProb.objects.get(knockout=knockout, crewAname=ccrew.crewname, crewBname=othcrew.crewname, day=day).winprob
				#print("-"*indent, "MP: %s" % mp)				
			except MatchProb.DoesNotExist:
				#print("Error: No MatchProb for the provided parameters, resorting to default of 0.5")
				#print("Parameters ccrew=%s, knockout=%s, crewA=%s, crewB=%s" % (ccrew, str(knockout), ccrew.crewname, othcrew.crewname))
				mp = 0.5
			probsum += (mp * CPcalc(othcrew, knockout, r-1, othcrew.startingslot, day, indent+1))
			cp2 = CPcalc(ccrew, knockout, r-1, ccrew.startingslot, day, indent+1)
		#print("-"*indent, "Probsum: %s" % probsum)
		#print("-"*indent, "cp2: %s" % cp2)
		#print("-"*indent, "Returning value: %s" % (cp2*probsum))
		return cp2 * probsum


weds_date = ["Wednesday", datetime.date(2018, 7, 4)]
thurs_date = ["Thursday", datetime.date(2018, 7, 5)]
fri_date = ["Friday", datetime.date(2018, 7, 6)]
sat_date = ["Saturday", datetime.date(2018, 7, 7)]
sun_date = ["Sunday", datetime.date(2018, 7, 8)]
days = [weds_date, thurs_date, fri_date, sat_date, sun_date]

## TODO convert to wider loop of all EIs	
## TODO run for all five days
day = weds_date
#EI = EventInstance.objects.get(pk=4)
for EI in EventInstance.objects.filter(year=2018):
	# generate list of crews	
	crews = []
	krs = KnockoutRace.objects.filter(round=1, knockout=EI)
	sslot = 0	
	for kr in krs:
		print(kr.race.name)
		for res in kr.race.result_set.all():
			snames = []
			sslot += 1
			# add crew
			if kr.race.result_set.first().crew.count() <= 2:
				# use surname
				for a in res.crew.order_by('name'):
					snames.append(a.name[a.name.find(" ")+1:])
			else:
				# use club name
				for c in res.clubs.all():
					snames.append(c.name)	
			
			# parse isnames
			if len(snames) == 1:
					#single name
					names2 = snames[0]
			else:
				# pair / composite
				names2 = snames[0] + ' and ' + snames[1]

			# add completed calc to crew
			crews.append([names2, res.crew.all(), sslot])
		# increment sslot again to compensate for lack of bye result
		if kr.bye == True:
			sslot += 1
			crews.append(["Bye-"+str(sslot), None, sslot])

	#save crew names
	for crew in crews:
		try:
			KnockoutCrew.objects.get(knockout=EI, crewname=crew[0])
		except KnockoutCrew.DoesNotExist:
			KnockoutCrew.objects.create(
				knockout=EI,
				crewname=crew[0],
				startingslot = crew[2],
			)
	print("All KCrews created")
			
	#loop through crews and do 1:1 prob calcs
	# TODO add get/except functions to avoid duplication
	for day in days:
		print("Starting on day %s" % day[0])
		for crew1, crew2 in itertools.combinations(crews, 2):
			#print("Trying the following: crew1 = %s, crew2 = %s" % (crew1, crew2))
			if crew1 != crew2:
				try:
					MatchProb.objects.get(knockout=EI, crewAname=crew1[0], crewBname=crew2[0], day=day[1])
					MatchProb.objects.get(knockout=EI, crewAname=crew2[0], crewBname=crew1[0], day=day[1])
					#print("MatchProb found")
				except MatchProb.DoesNotExist:
					print("MatchProb not found")
					c1havelost = False
					c2havelost = False
					print("Trying to see if lost in previous days")
					# Check to see if have lost in previous days
					# get all races in this knockout from previous days
					for kr in KnockoutRace.objects.filter(knockout=EI, race__date__lt=day[1]):
						# don't bother with round 1 races
						if kr.round != 1:
							if kr.race.result_set.filter(position=2, crew=crew1[1].crew.all()).count() > 0:
								c1havelost = True
							elif kr.race.result_set.filter(position=2, crew=crew2[1].crew.all()).count() > 0:
								c2havelost = True
					print("Checking if bye")
					if crew1[0][:4] == "Bye-":
						c1havelost = True
					elif crew2[0][:4] == "Bye-":
						c2havelost = True
					# if have lost in a previous race
					if c1havelost == True:
						MatchProb.objects.create(
							crewAname = crew1[0],
							crewBname = crew2[0],
							winprob = 0,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)
						MatchProb.objects.create(
							crewBname = crew1[0],
							crewAname = crew2[0],
							winprob = 1,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)
					elif c2havelost == True:
						MatchProb.objects.create(
							crewAname = crew1[0],
							crewBname = crew2[0],
							winprob = 1,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)
						MatchProb.objects.create(
							crewBname = crew1[0],
							crewAname = crew2[0],
							winprob = 0,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)
					# if are still in the race
					else:
						print("Running calcs if in race")
						crew1_mu = 0
						crew1_sigma = 0
						crew2_mu = 0
						crew2_sigma = 0
						# crew1[0] is crewname
						for c in crew1[1]:
							try:
								crew1_mu += c.score_set.filter(result__race__date__lt=day[1], result__race__event__type=EI.event.type).latest('result__race__date').mu
								crew1_sigma += c.score_set.filter(result__race__date__lt=day[1], result__race__event__type=EI.event.type).latest('result__race__date').sigma
							except Score.DoesNotExist:
								# add default values
								crew1_mu += 0.0
								crew1_sigma += 10.0
						for c in crew2[1]:
							try:
								crew2_mu += c.score_set.filter(result__race__date__lt=day[1], result__race__event__type=EI.event.type).latest('result__race__date').mu
								crew2_sigma += c.score_set.filter(result__race__date__lt=day[1], result__race__event__type=EI.event.type).latest('result__race__date').sigma
							except Score.DoesNotExist:
								# add default values
								crew1_mu += 0.0
								crew1_sigma += 10.0
						winprob = 1 - norm.cdf( -(crew1_mu - crew2_mu) / (crew1_sigma + crew2_sigma) )
						
						MatchProb.objects.create(
							crewAname = crew1[0],
							crewBname = crew2[0],
							winprob = winprob,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)
						MatchProb.objects.create(
							crewBname = crew1[0],
							crewAname = crew2[0],
							winprob = 1-winprob,
							day = day[1],
							dayn = day[0],
							knockout = EI,
						)

		# create cumulative probs
		print("Starting CProb calcs...")
		for crew in KnockoutCrew.objects.filter(knockout=EI).exclude(crewname__startswith='Bye-'):
			print("Trying crew %s" % crew.crewname)
			'''notincomp = False
			for kr in KnockoutRace.objects.filter(knockout=EI, race__date__lt=day[1]):
				if kr.race.result_set.filter(position=2, crew=.crew.all()).count() > 0:
					notincomp = True
					break
			# skip CP if crew is knocked out
			if notincomp == True
				continue'''
			try:
				CumlProb.objects.get(crewname=crew.crewname, knockout=EI, day=day[1])
			except CumlProb.DoesNotExist:
				cumlp = CPcalc(crew, EI, EI.rounds, crew.startingslot, day[1], 0)
				CumlProb.objects.create(
					crewname = crew.crewname,
					knockout = EI,
					day = day[1],
					dayn = day[0],
					cumlprob = cumlp,
				)
print("Script complete")
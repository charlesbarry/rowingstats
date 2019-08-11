from rowing.models import Event, Race, EventInstance, KnockoutRace, Result, MatchProb, CumlProb, Score, KnockoutCrew
from scipy.stats import norm
from math import floor
import datetime, itertools, logging

logging.basicConfig(filename='./log/cpcalc.log', level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

EI = EventInstance.objects.get(pk=4)
day = ["Wednesday", datetime.date(2018, 7, 4)]
crew3 = KnockoutCrew.objects.filter(knockout=EI)[6]

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
				print("Error: No MatchProb for the provided parameters, resorting to default of 0.5")
				print("Parameters ccrew=%s, knockout=%s, crewA=%s, crewB=%s" % (ccrew, str(knockout), ccrew.crewname, othcrew.crewname))
				mp = 0.5
			probsum += (mp * CPcalc(othcrew, knockout, r-1, othcrew.startingslot, day, indent+1))
			cp2 = CPcalc(ccrew, knockout, r-1, ccrew.startingslot, day, indent+1)
		#print("-"*indent, "Probsum: %s" % probsum)
		#print("-"*indent, "cp2: %s" % cp2)
		#print("-"*indent, "Returning value: %s" % (cp2*probsum))
		return cp2 * probsum
		
print(CPcalc(KnockoutCrew.objects.filter(knockout=EI)[0], EI, 4, crew3.startingslot, day[1], 0))
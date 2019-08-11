# renames the first round races for HRR draws

from rowing.models import Event, Race, EventInstance, KnockoutRace
import datetime
	
#EI = EventInstance.objects.get(pk=4)

for EI in EventInstance.objects.filter(year=2018):	
	krs = KnockoutRace.objects.filter(round=1, knockout=EI)
	for kr in krs:
		if kr.race:
			# think through what happens with byes (ie pos = 1)
			if kr.race.result_set.all().count() > 0:
				# use individual names
				# structure of snames: [[C1 N1, C1 N2],[C2 N1, C2 N2]]
				if kr.race.result_set.first().crew.count() <= 2:
					snames = []
					for res in kr.race.result_set.all():
						isnames = []
						for c in res.crew.order_by('name'):
							isnames.append(c.name[c.name.find(" ")+1:])
						snames.append(isnames)
				# use clubnames
				else:
					snames = []
					for res in kr.race.result_set.all():
						isnames = []
						for c in res.clubs.all():
							isnames.append(c.name)
						snames.append(isnames)
							
				if len(snames) == 1:
					if len(snames[0]) == 1:
						#single bye
						names2 = snames[0][0]
					else:
						# pair bye
						names2 = snames[0][0] + ' and ' + snames[0][1]
				else:
					# single vs
					if len(snames[0]) == 1 and len(snames[0]) == len(snames[1]):
						names2 = snames[0][0] + ' vs ' + snames[1][0]
					# pair vs / two composites
					elif len(snames[0]) == 2 and len(snames[0]) == len(snames[1]):
						names2 = (snames[0][0] + ' and ' + snames[0][1]) + ' vs ' + (snames[1][0] + ' and ' + snames[1][1])
					# l is a composite, r is not
					elif len(snames[0]) == 2 and len(snames[0]) != len(snames[1]):
						names2 = (snames[0][0] + ' and ' + snames[0][1]) + ' vs ' + (snames[1][0])
					# r is a composite, l is not
					elif len(snames[0]) == 1 and len(snames[0]) != len(snames[1]):
						names2 = (snames[0][0]) + ' vs ' + (snames[1][0] + ' and ' + snames[1][1])
					else:
						print("Somehow you are at the end of this tree")
						raise
		
				kr.race.name = names2
				kr.race.save()
				
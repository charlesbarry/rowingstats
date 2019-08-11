# updates the subsequent round by creating results based on parent result positions

from rowing.models import Event, Race, EventInstance, KnockoutRace, Result
import datetime

## TODO convert to wider loop of all EIs	
#EI = EventInstance.objects.get(pk=4)

for EI in EventInstance.objects.filter(year=2018):
	krs = KnockoutRace.objects.filter(round__gt=1, knockout=EI)
	
	for kr in krs:
		# check that both parents have non-null positions
		print(kr.race.name)
		# check that the race has parents with races, and check they have results
		if kr.parent.first().race and kr.parent.last().race and kr.parent.first().race.result_set.all().count() > 0 and kr.parent.last().race.result_set.all().count() > 0: 
			# check that parent results have positions
			if kr.parent.first().race.result_set.first().position and kr.parent.last().race.result_set.first().position:
				# create two new results for the race
				firstres = kr.race.result_set.first()
				lastres = kr.race.result_set.last()
				if firstres is None:
					firstres = Result.objects.create(
						race = kr.race
					)
				if lastres is None:
					lastres = Result.objects.create(
						race = kr.race
					)
				firstres.crew.clear()
				firstres.clubs.clear()
				lastres.crew.clear()
				lastres.clubs.clear()
				
				# add the bucks crew
				for c in kr.parent.first().race.result_set.get(position=1).crew.all():
					firstres.crew.add(c)
					
				# add the bucks clubs
				for c in kr.parent.first().race.result_set.get(position=1).clubs.all():
					firstres.clubs.add(c)
				
				# add the berks crew
				# skip byes for last res
				for c in kr.parent.last().race.result_set.get(position=1).crew.all():
					lastres.crew.add(c)
					
				# add the berks clubs
				for c in kr.parent.last().race.result_set.get(position=1).clubs.all():
					lastres.clubs.add(c)
					
				# update parents to be complete
				for p in kr.parent.all():
					p.race.complete = True
					p.race.save()
			
		# think through what happens with byes (ie pos = 1)
		if kr.race.result_set.all().count() > 0:
			# use individual names
			# structure of snames: [[C1 N1, C1 N2],[C2 N1, C2 N2]]
			if kr.race.result_set.first().clubs.count() == 0:
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

			kr.race.name = names2
			kr.race.save()
				
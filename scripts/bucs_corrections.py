from rowing.models import Race, Result, Event, Competition, Club

bucs = Competition.objects.get(pk=4)

citcam = Club.objects.get(pk=28)
cubc = Club.objects.get(pk=125)
cheltenham = Club.objects.get(pk=391)
chesteru = Club.objects.get(pk=336)
leedsrc = Club.objects.get(pk=119)
leedsu = Club.objects.get(pk=291)
derbyrc = Club.objects.get(pk=120)
derbyu = Club.objects.get(pk=483) 
livvic = Club.objects.get(pk=472)
livu = Club.objects.get(pk=17) 


for res in Result.objects.filter(race__event__comp=bucs):
	'''
	if citcam in res.clubs.all():
		res.clubs.remove(citcam)
		res.clubs.add(cubc)
	elif cheltenham in res.clubs.all():
		res.clubs.remove(cheltenham)
		res.clubs.add(chesteru)
	elif leedsrc in res.clubs.all():
		res.clubs.remove(leedsrc)
		res.clubs.add(leedsu)
	elif derbyrc in res.clubs.all():
		res.clubs.remove(derbyu)
		res.clubs.add(derbyu)
	elif livvic in res.clubs.all():
		res.clubs.remove(livvic)
		res.clubs.add(livu)	
	'''	
	try:
		ftime = res.time_set.get(description="Finish")
		for t in res.time_set.order_by('order'):
			if t != ftime and t.value == ftime.value:
				t.delete()
	except Time.DoesNotExist:
		print("No times for res %s" % res.result.name)
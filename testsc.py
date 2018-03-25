# test py script

from rowing.models import Rower, Club, Result, Race

rower1 = Rower.objects.get(pk=1)
club1 = Club.objects.get(pk=1)
race1 = Race.objects.get(pk=91)

for item in range(275,301):
	foo = Result.objects.create(
		race = race1,
		position = item,
		flag = ''
	)
	foo.crew = [rower1]
	foo.clubs = [club1]
	foo.save()
	print("Entry %s complete" % item)
	
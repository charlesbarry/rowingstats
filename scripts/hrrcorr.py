# generates trees for HRR draws

from rowing.models import Event, Race, EventInstance, KnockoutRace
import datetime
	
##### CONFIG #####	
weds_date = datetime.date(2018, 7, 4)
thurs_date = datetime.date(2018, 7, 5)
fri_date = datetime.date(2018, 7, 6)
sat_date = datetime.date(2018, 7, 7)
sun_date = datetime.date(2018, 7, 8)

makeraces = True
year = 2018

grand = Event.objects.get(pk=51)
stewards = Event.objects.get(pk=67)
queenmum = Event.objects.get(pk=460)
sandg = Event.objects.get(pk=69)
doubles = Event.objects.get(pk=461)
diamondsculls = Event.objects.get(pk=30)
remenham = Event.objects.get(pk=462)
town = Event.objects.get(pk=463)
princessg = Event.objects.get(pk=464)
hambleden = Event.objects.get(pk=465)
stonor = Event.objects.get(pk=466)
princessr = Event.objects.get(pk=467)
ladies = Event.objects.get(pk=468)
visitors = Event.objects.get(pk=68)
pow = Event.objects.get(pk=469)
thames = Event.objects.get(pk=25)
wyfold = Event.objects.get(pk=24)
brit = Event.objects.get(pk=27)
temple = Event.objects.get(pk=31)
pa = Event.objects.get(pk=470)
pe = Event.objects.get(pk=26)
fawley = Event.objects.get(pk=28)
dj = Event.objects.get(pk=29)
##### END CONFIG #####

##### DATA #####
# format is event, rounds, [days]
hrrdata = [
	{'event':grand, 'rounds':2, 'days':[sat_date, sun_date]},
	{'event':stewards, 'rounds':1, 'days':[sun_date]},
	{'event':queenmum, 'rounds':1, 'days':[sun_date]},
	{'event':sandg, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':doubles, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':diamondsculls, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':remenham, 'rounds':4, 'days':[weds_date, fri_date, sat_date, sun_date]},
	{'event':town, 'rounds':3, 'days':[fri_date, sat_date, sun_date]},
	{'event':princessg, 'rounds':3, 'days':[fri_date, sat_date, sun_date]},
	{'event':hambleden, 'rounds':2, 'days':[sat_date, sun_date]},
	{'event':stonor, 'rounds':3, 'days':[fri_date, sat_date, sun_date]},
	{'event':princessr, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':ladies, 'rounds':3, 'days':[fri_date, sat_date, sun_date]},
	{'event':visitors, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':pow, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':thames, 'rounds':5, 'days':[weds_date, thurs_date, fri_date, sat_date, sun_date]},
	{'event':wyfold, 'rounds':5, 'days':[weds_date, thurs_date, fri_date, sat_date, sun_date]},
	{'event':brit, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
	{'event':temple, 'rounds':5, 'days':[weds_date, thurs_date, fri_date, sat_date, sun_date]},
	{'event':pa, 'rounds':4, 'days':[weds_date, fri_date, sat_date, sun_date]},
	{'event':pe, 'rounds':5, 'days':[weds_date, thurs_date, fri_date, sat_date, sun_date]},
	{'event':fawley, 'rounds':5, 'days':[weds_date, thurs_date, fri_date, sat_date, sun_date]},
	{'event':dj, 'rounds':4, 'days':[thurs_date, fri_date, sat_date, sun_date]},
]
##### END DATA #####

##### MAIN FUNCTION ######
for row in hrrdata:
	KEvent = row['event']
	rounds = row['rounds']

	#create the event instance
	try:
		EI = EventInstance.objects.get(event=KEvent, year=year)
		EI.rounds = row['rounds']
		EI.save()
	except EventInstance.DoesNotExist:
		EI = EventInstance.objects.create(event=KEvent, year=year, rounds=row['rounds'])				
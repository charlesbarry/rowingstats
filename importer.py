# script to import the csv data into sqlite

# NB run through the django shell

csvfilepath = "C:/Users/Charles/Dropbox/statistics/rowing/gbdatacsv/results.csv"
djangoproject = "C:/Users/Charles/Dropbox/statistics/rowing/rowingstats/rowingstats" #project of project folder

import sys, os
#sys.path.append(djangoproject)
os.environ['DJANGO_SETTINGS_MODULE'] = 'rowingstats.settings'

from rowing.models import Rower, Race, Result

import csv

# csv reader goes here
with open(csvfilepath) as csvfile:
	reader = csv.DictReader(csvfile)
	data = (list(reader))

for row in data:
	#change to the appropriate model
	#record = Race.objects.create(name=row['name'],r_date=row['date'],r_type=row['type'],r_class=row['class'])
	alt_record = Race.objects.get(pk=row['race'])
	record = Result.objects.create(race=alt_record,position=row['position'])
	for item in row['ID']:
		temp = Rower.objects.get(pk=item)
		record.crew.add(temp)
		
for i, row in enumerate(data):
	record = Result.objects.get(pk=(i+1))
	for item in row['ID']:
		temp = Rower.objects.get(pk=item)
		record.crew.add(temp)
		


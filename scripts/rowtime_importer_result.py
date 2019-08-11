# script to import the 2018 bucs regatta data

#TODO: move to django management command, allow options such as rollback for events

from rowing.models import Rower, Race, Result, Club, Competition, Event, Time, Alias
import json, csv, datetime, logging, os, sys
from django.db.models import Q
from scripts.raceimporter import rowersearch, clubsearch, add_time

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/bucslog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

SATDATE = datetime.date(2019, 5, 4)
SUNDATE = datetime.date(2019, 5, 5)
MONDATE = datetime.date(2019, 5, 6)

DATES = [SATDATE, SUNDATE, MONDATE]

basedir = '../bucs/2019 Regatta/json/'

comp = Competition.objects.get(pk=4)
##### END CONFIG #####

# use this to start the counter manually
try:
	counter = int(sys.argv[2]) # third argument
except IndexError:
	counter = 0
	
# sticking this here to get round weird variable issue
#race = Race.objects.get(pk=1)	
	
logging.info("Counter set as: %s", counter)
logging.info("Config and preparatory tasks completed.")

##### BEGIN MAIN FUNCTION #####
try:
	if counter == 0:
		list_races = Race.objects.filter(event__comp=comp, date__in=DATES)
		#list_races = Race.objects.filter(pk=8321)
	else:
		list_races = Race.objects.filter(event__comp=comp, date__in=DATES)[counter:]

	for race in list_races:
		try_error = 0
		# get the file
		# splits 'event - race (NN)' into NN
		filestr = basedir + 'Race' + str(race.rnumber) + '.json'
		
		# TODO add exception handling here for if json file is not json
		try:
			with open(filestr) as jsonfile2:
				racedata = json.load(jsonfile2)
		except json.decoder.JSONDecodeError:
			logging.error("Failed to load %s. Skipping to next race", filestr)
			continue
		
		logging.info("File %s successfully loaded.", filestr)
		
		#check file has lane data
		try:
			if len(racedata['lanes']) == 0:
				logging.error("File %s lacks lanedata.", filestr)
				counter += 1
				continue
		except KeyError:
			logging.error("File %s lacks lanedata.", filestr)
			counter += 1
			continue
		
		# create the results and operate on them
		for lane in racedata['lanes']:
			# check for flags
			if "(" in lane['CrewCode']:
				flag = lane['CrewCode'][(lane['CrewCode'].find("(")+1):lane['CrewCode'].rfind(")")]
			else:
				flag = ""
			
			# create the base layer result - or check if one exists
			try:
				logging.debug("Result being created with position=%s and flag=%s.", str(lane['Posn']), flag)
				new_res = Result.objects.create(
					race = race,
					position = lane['Posn'],
					flag = flag,
				)
			except ValueError:
				logging.warning("ValueError incurred for lane entry: race=%s, club=%s, position=%s", str(race), lane['ClubName'], lane['Posn'])
				#try_error = 1
				continue
			except Exception as e:
				logging.error("Exception %s incurred when creating Result - race=%s, clubname=%s, crewnames=%s, crewcode=%s", str(e), str(race), lane['ClubName'], lane['CrewNames'], lane['CrewCode'])
				try_error = 1
				continue		
			
			# add times to the result
			if lane['Finish'] != '' and lane['Finish'] != 'DNA':
				add_time("Finish", lane['Finish'], new_res, 3)
			if lane['Split1'] != '' and lane['Split1'] != 'DNA':
				add_time("500m", lane['Split1'], new_res, 0)
			if lane['Split2'] != '' and lane['Split2'] != 'DNA':
				add_time("1000m", lane['Split2'], new_res, 1)			
			if lane['Split3'] != '' and lane['Split3'] != 'DNA':
				add_time("1500m", lane['Split3'], new_res, 2)
				
			# split the crew names
			if '<br>' in lane['CrewNames'] or ' - ' in lane['CrewNames']:
				# format to convert: 1 - T. Broomfield<br>2 - S. Clifford
				crewnames = lane['CrewNames'].split('<br>')
				# trim off the seat position
				crewnames = [name[name.find('-')+2:] for name in crewnames]				
			else:
				# format: S..&nbsp;Williamson , H..&nbsp;Jones
				crewnames = lane['CrewNames'].split(' , ')
				# trim off the nbsp
				crewnames = [(name[0] + ' ' + name[name.find(';')+1:]) for name in crewnames]
				
			# remove irritating bug where '' results are included due to <br><br> doublesplitting
			crewnames = [x for x in crewnames if x != '']
			
			# gender detection
			if "W" in race.name:
				gender = "W"
			else:
				gender = "M"
				
			# irish detection
			if lane['CrewCode'][0] == "Z":
				nationality = "IRE"
			else:
				nationality = "GBR"
			
			logging.debug("Crewnames about to be searched as follows: %s", str(crewnames))
			club_str = lane['ClubName'] + ' - (' + lane['CrewCode'] + ')'
			
			# add club to result - important this goes first as club in res helps rowersearch
			# composite handling
			if "/ " in lane['ClubName']:
				logging.debug("Composite detected: %s", lane['ClubName'])
				cnames = lane['ClubName'].split("/ ")
				for cname in cnames:
					clubsearch(new_res, cname)
			else:
				logging.debug("Search for club: %s", lane['ClubName'])
				if "(IRE)" in lane['ClubName']:
					cname = lane['ClubName'][:lane['ClubName'].find("(")-1]
					clubsearch(new_res, cname, country="Ireland")
				elif nationality == "IRE":
					clubsearch(new_res, lane['ClubName'], country="Ireland")
				elif "(" in lane['ClubName']:
					cname = lane['ClubName'][:lane['ClubName'].find("(")-1]
					clubsearch(new_res, cname)
				else:
					clubsearch(new_res, lane['ClubName'])
			
			# remove the cox (coxed four or eight only)
			if len(crewnames) in (5, 9):
				coxname = crewnames.pop()
				logging.debug("Search for cox: %s", str(coxname))
				if "(" in coxname:
					coxname = coxname[:coxname.find("(")-1]
				rowersearch(res=new_res, name=coxname, gender=gender, nationality=nationality, club_str=club_str, cox=True)
			
			for name in crewnames:
				logging.debug("Search for name: %s", str(name))
				if "(" in name:
					name = name[:name.find("(")-1]
				
				# due to some stupid idea to have <br><br> in some people's names
				if "<br" in name:
					name = name[:name.find("<br")-1]
				
				rowersearch(res=new_res, name=name, gender=gender, nationality=nationality, club_str=club_str)
			
		logging.info("Race %s of %s completed.", counter, Race.objects.filter(event__comp=comp, date__in=DATES).count())
		if try_error == 0:
			race.complete = True
			race.save()
		counter += 1		
except KeyboardInterrupt:
	print("Exiting due to keyboard interrupt.")
	logging.info("Exiting main loop during Race %s (item %s in loop)", race.name, str(counter))
	
	# rollback
	for res in race.result_set.all():
		res.delete()
	
	logging.info("Results for current race rolled back")
	
except Exception:
	logging.exception("Exiting main loop during Race %s (item %s in loop). Exception detected.", race.name, str(counter))
	logging.debug("Vars as follows: %s", str(globals()))
	
	# rollback
	for res in race.result_set.all():
		res.delete()
		
	logging.info("Results for current race rolled back")
else:
	print("All races completed.")	
	if Race.objects.filter(event__comp=comp, date__in=DATES, complete=False).count() > 0:
		logging.info("The following races incurred non-critical errors and should be reviewed manually:")
		for r in Race.objects.filter(event__comp=comp, date__in=DATES, complete=False):
			logging.info("---%s", r.name)
	logging.info("Deleting temporary aliases")
	Alias.objects.filter(temp=True).delete()
	logging.info("All races completed. Exiting...")
finally:
	# save crewtemptest and clubtemptest to file in crashout
	print("Exiting loop on race %s (Loop #: %s). Shutting down..." % (race.name, counter))
	logging.info("####### End of Log ########")	
# script to import the 2018 bucs regatta data

#TODO: move to django management command, allow options such as rollback for events

from rowing.models import Rower, Race, Result, Club, Competition, Event, Time
import json, csv, datetime, logging, os, pickle
from django.db.models import Q
from scripts.raceimporter import crewsearch, clubsearch, add_time

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/bucslog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

SATDATE = datetime.date(2018, 5, 5)
SUNDATE = datetime.date(2018, 5, 6)
MONDATE = datetime.date(2018, 5, 7)

basedir = './data/2018 Regatta/'

bucs = Competition.objects.get(pk=4)

# composite placeholder is 362 on production, 188 on local (laptop), 50 on local (desktop)
composite_placeholder = Club.objects.get(pk=1)

composite = False
##### END CONFIG #####

composite_list = []

if os.path.isfile('./log/bucs_crewtemptest.pickle'):
	with open('./log/bucs_crewtemptest.pickle', 'rb') as fp:
		crewtemptest = pickle.load(fp)
else:
	crewtemptest = []

if os.path.isfile('./log/bucs_clubtemptest.pickle'):
	with open('./log/bucs_clubtemptest.pickle', 'rb') as fp:
		clubtemptest = pickle.load(fp)
else:
	clubtemptest = []
	
if os.path.isfile('./log/bucs_counter.pickle'):
	with open('./log/bucs_counter.pickle', 'rb') as fp:
		counter = pickle.load(fp)
else:
	counter = 0

if os.path.isfile('./log/bucs_allevents.pickle'):
	with open('./log/bucs_allevents.pickle', 'rb') as fp:
		allevents = pickle.load(fp)
else:
	allevents = False
	
if os.path.isfile('./log/bucs_allraces.pickle'):
	with open('./log/bucs_allraces.pickle', 'rb') as fp:
		allraces = pickle.load(fp)
else:
	allraces = False
	
logging.info("Counter set as: %s", counter)
logging.info("Config and preparatory tasks completed.")

##### CREATION OF EVENTS AND RACES ######
if not allevents:
	fname = basedir + 'event_list.csv'
	with open(fname, 'r', encoding='UTF-8-sig', newline='') as csvfile:
		reader = csv.reader(csvfile)
		eventdata = (list(reader))
		
		logging.info("Event data successfully loaded. Starting create_events()")
		print("Starting to create events...")
		
	for ev in eventdata:
		try:
			Event.objects.get(name = ev[0])
		except Event.DoesNotExist:
			try:
				if "x" in ev[0]:
					type = 'Sculling'
				else:
					type = 'Sweep'
			
				new_event = Event.objects.create(
						name = ev[0],
						comp = bucs,
						type = type,
						distance = '2000m',
					)
				logging.debug("Event created with parameters as follows - name=%s, type=%s", ev[0], type)
			except Exception as e:
				logging.error("Exception incurred for Event %s: %s", ev[0], str(e))
				raise e
			
	logging.info("All events added to DB.")
	print("All events added to DB.")
	allevents = True
	
if not allraces:
	fname = basedir + 'race_list.json'
	with open(fname) as jsonfile:
		jdata = json.load(jsonfile)
		racedata = jdata['data']

	logging.info("Race data successfully loaded. Starting createraces()")
	print("Starting to create races...")
	
	for race in racedata:
		#remove html artifacts
		if "&" in race['Round']:
			race['Round'] = race['Round'][:race['Round'].find("&")]
		
		rname = (race['FullName'] + " - " + race['Round'] + " (" + race['Race'] + ")")
		
		if race['Day'] == "Saturday":
			rdate = SATDATE
		elif race['Day'] == "Sunday":
			rdate = SUNDATE
		elif race['Day'] == "Monday":
			rdate = MONDATE
		
		try:
			Race.objects.get(name = rname, date = rdate)
		except Race.DoesNotExist:	
			if race['Round'] == "Time Trial":
				order = 0
			elif 'Rep' in race['Round'] or 'Semi' in race['Round']:
				order = 1
			elif 'Final' in race['Round']:
				order = 2
			
			logging.debug("Trying to add %s to the DB - Event %s.", rname, race['Event'])
			try:
				new_race = Race.objects.create(
						name = rname,
						date = rdate,
						raceclass = "Student",
						event = Event.objects.get(name=race['Event']),
						order = order,
						complete = False,				
					)
			except Exception as e:
				logging.error("Exception incurred for Race %s: %s", ev[0], str(e))
				raise e	
			logging.info("Race %s added to DB." % rname)
	
	logging.info("All races added to DB.")
	print("All races added to DB.")
	allraces = True

##### END RACE/EVENT CREATION #####


##### BEGIN MAIN FUNCTION #####
try:
	if counter == 0:
		list_races = Race.objects.filter(event__comp=bucs, date__in=[SATDATE,SUNDATE,MONDATE])
	else:
		list_races = Race.objects.filter(event__comp=bucs, date__in=[SATDATE,SUNDATE,MONDATE])[counter:]

	for race in list_races:
		try_error = 0
		# get the file
		# splits 'event - race (NN)' into NN
		racenum = race.name[(race.name.find("(") + 1):race.name.rfind(")")]
		filestr = basedir + 'Race' + racenum + '.json'
		with open(filestr) as jsonfile2:
			racedata = json.load(jsonfile2)
		
		logging.debug("File %s successfully loaded.", filestr)
		
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
				# exactcheck
				logging.debug("Result being searched for with position=%s and flag=%s.", str(lane['Posn']), flag)
				new_res = Result.objects.get(race = race, position = lane['Posn'], flag = flag)
			except Result.MultipleObjectsReturned:
				print("!"*20)
				print("Error: multiple objects returned for an exact result check.")
				print("Search database for duplicates of %s." % rname)
				print("!"*20)
				
				logging.error("Multiple objects returned for a search of %s", rname)
				
				# skipping this result due to error
				try_error = 1
				continue
			except Result.DoesNotExist:			
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
			
			# irish detection
			if lane['CrewCode'][0] == "Z":
				nationality = "IRE"
			else:
				nationality = "GBR"
			
			# add times to the result
			if lane['Finish'] != '':
				add_time("Finish", lane['Finish'], new_res, 3)
			if lane['Split1'] != '':
				add_time("500m", lane['Finish'], new_res, 0)
			if lane['Split2'] != '':
				add_time("1000m", lane['Finish'], new_res, 1)			
			if lane['Split3'] != '':
				add_time("1500m", lane['Finish'], new_res, 2)
				
			# split the crew names
			if '<br>' in lane['CrewNames']:
				crewnames = lane['CrewNames'].split('<br>')
			else:
				# create single member list
				crewnames = [lane['CrewNames'],]
			
			# remove the cox (coxed four or eight only)
			if len(crewnames) in (5, 9):
				crewnames.pop()
				
			# gender detection
			if "Women" in race.name:
				gender = "W"
			else:
				gender = "M"
			
			# trim off the seat position
			crewnames = [name[4:] for name in crewnames]
			
			logging.debug("Crewnames about to be searched as follows: %s", str(crewnames))
			
			for name in crewnames:
				logging.debug("Search for name: %s", str(name))
				increwcache = False
				# scan through the crewnames cache
				for t in crewtemptest:
					#print("Comparing %s to %s" %(name, t[0]))
					if name == t[0]:
						increwcache = True
						new_res.crew.add(t[1])
						logging.debug("%s added to the result.", t[1].name)
						break
				
				# if not in the crew cache, call full search
				if not increwcache:
					club_str = lane['ClubName'] + ' - (' + lane['CrewCode'] + ')'
					crewtemptest = crewsearch(new_res, race, name, gender, nationality, club_str, crewtemptest)
				
				'''
				if any(name in i for i in crewtemptest):
					for name_i in crewtemptest:
						if name in name_i[0]:
							new_res.crew.add(name_i[1])
							logging.debug("%s added to the result.", name_i[1].name)
				
				else:
					club_str = lane['ClubName'] + ' - (' + lane['CrewCode'] + ')'
					crewtemptest = crewsearch(new_res, race, name, nationality, club_str, crewtemptest)
				'''
				
			# add club to result
			# clubtemptest used to avoid repetitive idiosycratic corrections eg Molesey BC -> Molesey Boat Club
			# structure is [(Incorrect entry, club object)]
			logging.debug("Search for club: %s", lane['ClubName'])
			inclubcache = False
			# scan through the crewnames cache
			for t in clubtemptest:
				if lane['ClubName'] == t[0]:
					inclubcache = True
					new_res.clubs.add(t[1])
					logging.debug("%s added to the result.", t[1].name)
					break
			
			# if not in the crew cache, call full search
			if not inclubcache:
				clubtemptest = clubsearch(new_res, race, lane['ClubName'], composite, nationality, clubtemptest)
			
			
			'''
			if any(lane['ClubName'] in i for i in clubtemptest):
				for clubt in clubtemptest:
					if lane['ClubName'] in clubt[0]:
						new_res.clubs.add(clubt[1])
						print("%s added to the result." % clubt[1].name)
			else:
				clubtemptest = clubsearch(new_res, race, lane['ClubName'], composite, nationality, clubtemptest)
			'''
			
		logging.info("Race %s of %s completed.", counter, list_races.count())
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
	if len(composite_list) > 0:
		print("The following composite crews need to be resolved manually:")
		logging.info("The following composite crews need to be resolved manually:")
		for item in composite_list:
			print("Club searched: %s, Race name: %s" % (item[0], item[1]))
			logging.info("Club searched: %s, Race name: %s", item[0], item[1])
			
	if Race.objects.filter(event__comp=bucs, date__in=[SATDATE,SUNDATE,MONDATE], complete=False).count() > 0:
		logging.info("The following races incurred non-critical errors and should be reviewed manually:")
		for r in Race.objects.filter(event__comp=bucs, date__in=[SATDATE,SUNDATE,MONDATE], complete=False):
			logging.info("---%s", r.name)
	logging.info("All races completed. Exiting...")
finally:
	# save crewtemptest and clubtemptest to file in crashout
	try:
		with open('./log/bucs_crewtemptest.pickle', 'wb') as fp:
			pickle.dump(crewtemptest, fp)
		with open('./log/bucs_clubtemptest.pickle', 'wb') as fp:
			pickle.dump(clubtemptest, fp)
		with open('./log/bucs_counter.pickle', 'wb') as fp:
			pickle.dump(counter, fp)
		with open('./log/bucs_allevents.pickle', 'wb') as fp:
			pickle.dump(allevents, fp)
		with open('./log/bucs_allraces.pickle', 'wb') as fp:
			pickle.dump(allraces, fp)
	except Exception:
		logging.exception("Failed to pickle core variables because of exception.")
	else:
		logging.info("Successfully pickled core variables.")
	
	print("Exiting loop on race %s (Loop #: %s). Shutting down..." % (race.name, counter))
	logging.info("####### End of Log ########")	
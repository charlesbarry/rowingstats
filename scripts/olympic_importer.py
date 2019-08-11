# script to import the 2018 bucs regatta data

#TODO: move to django management command, allow options such as rollback for events

from rowing.models import Rower, Race, Result, Club, Competition, Event, Time
import json, csv, datetime, logging, os, pickle
from django.db.models import Q
from scripts.raceimporter import crewsearch, clubsearch, add_time

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/worldrowing.log', level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

#fname = './data/worldrowing/wr200013data.csv'
#fname = './data/worldrowing/wr201417data.csv'
fname = './data/worldrowing/wrdatacombined.csv'

olympics = Competition.objects.get(pk=10)
worldchamps = Competition.objects.get(pk=13)
worldcup = Competition.objects.get(pk=16)
euros = Competition.objects.get(pk=17)

composite = False

picklepath_crewtemptest = './log/wr_crewtemptest.pickle'
picklepath_clubtemptest = './log/wr_clubtemptest.pickle'
picklepath_counter = './log/wr_counter.pickle'
picklepath_allraces = './log/wr_allraces.pickle'
picklepath_allevents = './log/wr_allevents.pickle'
picklepath_wrdata = './log/wr_wrdata.pickle'

##### END CONFIG #####

##### PREPARATORY #####
composite_list = []

if os.path.isfile(picklepath_crewtemptest):
	with open(picklepath_crewtemptest, 'rb') as fp:
		crewtemptest = pickle.load(fp)
else:
	crewtemptest = []

if os.path.isfile(picklepath_clubtemptest):
	with open(picklepath_clubtemptest, 'rb') as fp:
		clubtemptest = pickle.load(fp)
else:
	clubtemptest = []
	
if os.path.isfile(picklepath_counter):
	with open(picklepath_counter, 'rb') as fp:
		counter = pickle.load(fp)
else:
	counter = 0

if os.path.isfile(picklepath_allevents):
	with open(picklepath_allevents, 'rb') as fp:
		allevents = pickle.load(fp)
else:
	allevents = False
	
if os.path.isfile(picklepath_allraces):
	with open(picklepath_allraces, 'rb') as fp:
		allraces = pickle.load(fp)
else:
	allraces = False
	
logging.info("Counter set as: %s", counter)
logging.info("Config and preparatory tasks completed.")

if os.path.isfile(picklepath_wrdata):
	with open(picklepath_wrdata, 'rb') as fp:
		wrdata = pickle.load(fp)
else:
	with open(fname, 'r', encoding='UTF-8-sig', newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		wrdata = (list(reader))
	
logging.info("Data read successfully.")
##### END PREPARATORY #####

##### CREATION OF EVENTS AND RACES ######
if not allevents:
	logging.info("Starting to create new events")
	try:
		for row in wrdata[counter:]:
			# skip if django Event already exists for this row
			if not 'dj_event' in row or row['dj_event'] == '':
				if "Cup" in row['competition']:
					comp = worldcup
				elif "European" in row['competition']:
					comp = euros
				elif "World Rowing Championships" in row['competition']:
					comp = worldcup
				elif "Olympic" in row['competition']:
					comp = olympics
				else:
					raise ValueError
			
				try:
					Event.objects.get(name = row['event'], comp=comp)
				except Event.DoesNotExist:
					try:
						# para events
						if "TA" in row['event'] or "AS" in row['event'] or "ID" in row['event'] or "PR" in row['event']:
							if "x" in row['event']:
								type = 'Para-Sculling'
							else:
								type = 'Para-Sweep'
						# lwt events
						elif "L" in row['event']:
							if "x" in row['event']:
								type = 'Lwt Sculling'
							else:
								type = 'Lwt Sweep'
						else:
							if "x" in row['event']:
								type = 'Sculling'
							else:
								type = 'Sweep'
					
						# shorter distance for old para events
						if "TA" in row['event'] or "AS" in row['event'] or "ID" in row['event']:
							dist = '1000m'
						else:
							dist = '2000m'
					
						new_event = Event.objects.create(
								name = row['event'],
								comp = comp,
								type = type,
								distance = dist,
							)
						logging.debug("Event created with parameters as follows - name=%s, type=%s", row['event'], type)
					except Exception:
						logging.exception("Exception incurred for Event %s", (row['competition'] + ' - ' + row['race']))
						raise
					else:
						row['dj_event'] = new_event
				else:
					row['dj_event'] = Event.objects.get(name = row['event'], comp=comp)
			counter += 1
	except Exception:
		# quit, save variables
		logging.exception("Exiting event creation loop during at item %s in loop). Exception detected.", str(counter))
		raise

	else:
		logging.info("All events added to DB.")
		print("All events added to DB.")
		allevents = True
		counter = 0
		# save allevents to preserve the True
		with open(picklepath_allevents, 'wb') as fp:
			pickle.dump(allevents, fp)
	finally:
		# save variables
		with open(picklepath_counter, 'wb') as fp:
			pickle.dump(counter, fp)
		with open(picklepath_wrdata, 'wb') as fp:
			pickle.dump(wrdata, fp)
	
if not allraces:
	logging.info("Starting to create new races")
	try:
		for row in wrdata[counter:]:
			if 'dj_race' not in row or row['dj_race'] == '':
				rname = (row['race'] + " " + row['code'][1:])
				rname = rname.rstrip()
				
				day = row['date'][:row['date'].find('/')]
				month = row['date'][row['date'].find('/')+1:row['date'].rfind('/')]
				year = row['date'][row['date'].rfind('/')+1:]
				rdate = datetime.date(int(year), int(month), int(day))
				
				try:
					Race.objects.get(name = rname, date = rdate)
				except Race.DoesNotExist:	
					if 'Heat' in row['race']:
						order = 0
					elif 'Repech' in row['race'] or 'Semif' in row['race']:
						order = 1
					elif 'Final' in row['race']:
						order = 2
					
					logging.debug("Trying to add %s to the DB - Event %s.", rname, row['event'])
					try:
						new_race = Race.objects.create(
								name = rname,
								date = rdate,
								raceclass = "International",
								event = row['dj_event'],
								order = order,
								complete = False,				
							)
					except Exception:
						logging.exception("Exception incurred for Race %s", ev[0])
						raise	
					else:
						logging.info("Race %s added to DB." % rname)
						row['dj_race'] = new_race
				else:
					row['dj_race'] = Race.objects.get(name = rname, date = rdate)
			counter += 1
	except Exception:
		logging.exception("Exiting race creation loop during at item %s in loop). Exception detected.", str(counter))
		raise
		# quit, save variables
	else:
		logging.info("All races added to DB.")
		print("All races added to DB.")
		allraces = True
		counter = 0
		# pickle allraces to preserve the True
		with open(picklepath_allraces, 'wb') as fp:
			pickle.dump(allraces, fp)
			
	finally:
		# save variables
		with open(picklepath_counter, 'wb') as fp:
			pickle.dump(counter, fp)
		with open(picklepath_wrdata, 'wb') as fp:
			pickle.dump(wrdata, fp)

##### END RACE/EVENT CREATION #####


##### BEGIN MAIN FUNCTION #####
try:
	for row in wrdata[counter:]:
		if int(row['position']) == 0:
			logging.info("Position with zero value skipped - event:%s, race:%s, nat:%s", row['event'], row['race'], row['nationality'])
			continue
		else:
		
			try_error = 0
			
			# create the results and operate on them

			# check for flags
			if len(row['nationality']) > 3:
				flag = row['nationality'][3:]
			else:
				flag = ""
			
			# create the base layer result - or check if one exists
			try:
				# exactcheck
				logging.debug("Result being searched for with position=%s and flag=%s.", row['position'], flag)
				new_res = Result.objects.get(race = row['dj_race'], position = int(row['position']), flag = flag)
			except Result.MultipleObjectsReturned:
				print("!"*20)
				print("Error: multiple objects returned for an exact result check.")
				print("Search database for duplicates of %s." % str(row['dj_race']))
				print("!"*20)
				
				logging.error("Multiple objects returned for a search of %s", str(row['dj_race']))
				
				# skipping this result due to error
				try_error = 1
				continue
			except Result.DoesNotExist:			
				logging.debug("Result being created with position=%s and flag=%s.", row['position'], flag)
				try:
					new_res = Result.objects.create(
						race = row['dj_race'],
						position = row['position'],
						flag = flag,
					)
				except Exception:
					logging.exception("Exception incurred during creation of new result. Parameters: counter=%, race=%s, position=%s, flag=%", str(counter), str(row['dj_race']), row['position'], flag)
					raise
			except ValueError:
				logging.warning("ValueError incurred for result entry: race=%s, club=%s, position=%s", str(row['dj_race']), row['nationality'], row['position'])
				#try_error = 1
				continue
			'''except Exception as e:
				logging.error("Exception %s incurred when finding Result - race=%s, clubname=%s, crewnames=%s, crewcode=%s", str(e), str(race), lane['ClubName'], lane['CrewNames'], lane['CrewCode'])
				try_error = 1
				continue	'''	
			
			# nationality
			nationality = row['nationality'][:3]
			
			# add times to the result
			add_time("Finish", row['time'], new_res, 0)
				
			# check crew exists
			if row['crew'] == "No Crew Recorded":
				try_error = 1
			else:
				# gender
				if "Women's" in row['race']:
					gender = "W"
				elif "Men's" in row['race']:
					gender = "M"
				else:
					gender = "U"
				
				# split names into list
				crewnames = row['crew'].split(";")
		
				# change "SURNAME, Forename" to "Forename Surname"
				# separate list required to avoid python issues with for loops
				newcrewnames = []
				for name in crewnames:
					txt_torep = name[1:name.find(', ')]
					tname = name.replace(txt_torep, txt_torep.lower())
					s_name = tname[:tname.find(', ')]
					f_name = tname[tname.find(', ')+2:]
					newcrewnames.append((f_name + ' ' + s_name))
				crewnames = newcrewnames
				
				def wrname()
				
				# remove the cox
				if "+" in row['event']:
					coxn = crewnames.pop()
					logging.debug("Adding cox: %s", coxn)
					
					try:
						new_res.cox = Rower.objects.get(name=coxn, nationality=nationality)
						new_res.save()
					except Rower.DoesNotExist:
						new_res.cox = Rower.objects.create(
							name = coxn,
							gender = gender,
							nationality = nationality)
						new_res.save()
					
				logging.debug("Crewnames about to be searched as follows: %s", str(crewnames))
				
				for name in crewnames:
					logging.debug("Search for name: %s", str(name))
					
					try:
						if gender != "U":
							r1 = Rower.objects.get(name__iexact=name, nationality=nationality, gender=gender)
						else:
							r1 = Rower.objects.get(name__iexact=name, nationality=nationality)
						new_res.crew.add(r1)
					except Rower.DoesNotExist:
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
							club_str = row['nationality']
							crewtemptest = crewsearch(new_res, row['dj_race'], name, gender, nationality, club_str, crewtemptest)
				
			# add club to result
			# clubtemptest used to avoid repetitive idiosycratic corrections eg Molesey BC -> Molesey Boat Club
			# structure is [(Incorrect entry, club object)]
			logging.debug("Search for club: %s", row['nationality'])
			inclubcache = False
			# scan through the crewnames cache
			'''for t in clubtemptest:
				if lane['ClubName'] == t[0]:
					inclubcache = True
					new_res.clubs.add(t[1])
					logging.debug("%s added to the result.", t[1].name)
					break
			
			# if not in the crew cache, call full search
			if not inclubcache:
				clubtemptest = clubsearch(new_res, race, lane['ClubName'], composite, nationality, clubtemptest)'''
				
			try:
				new_res.clubs.add(Club.objects.get(countrycode=row['nationality'][:3]))
			except Club.DoesNotExist:
				new_club = Club.objects.create(
					name = row['nationality'],
					countrycode = row['nationality']
				)
				new_res.clubs.add(new_club)
				
			logging.info("Result %s of %s completed.", counter, len(wrdata))
			if try_error == 0:
				new_res.race.complete = True
				new_res.save()
			counter += 1		
except KeyboardInterrupt:
	print("Exiting due to keyboard interrupt.")
	logging.info("Exiting main loop during Race %s (item %s in loop)", row['race'], str(counter))
	
	# rollback - needs updating
	#for res in race.result_set.all():
	#	res.delete()
	
	logging.info("Results for current race rolled back")
	
except Exception:
	logging.exception("Exiting main loop during Race %s (item %s in loop). Exception detected.", row['race'], str(counter))
	#logging.debug("Vars as follows: %s", str(globals()))
	
	# rollback
	#for res in race.result_set.all():
	#	res.delete()
		
	#logging.info("Results for current race rolled back")
else:
	print("All races completed.")	
	if len(composite_list) > 0:
		print("The following composite crews need to be resolved manually:")
		logging.info("The following composite crews need to be resolved manually:")
		for item in composite_list:
			print("Club searched: %s, Race name: %s" % (item[0], item[1]))
			logging.info("Club searched: %s, Race name: %s", item[0], item[1])
			
	if Race.objects.filter(event__comp__in=[olympics, worldchamps, worldcup, euros], complete=False).count() > 0:
		logging.info("The following races incurred non-critical errors and should be reviewed manually:")
		for r in Race.objects.filter(event__comp__in=[olympics, worldchamps, worldcup, euros], complete=False):
			logging.info("---%s", r.name)
	logging.info("All races completed. Exiting...")
finally:
	# save crewtemptest and clubtemptest to file in crashout
	try:
		with open(picklepath_crewtemptest, 'wb') as fp:
			pickle.dump(crewtemptest, fp)
		with open(picklepath_clubtemptest, 'wb') as fp:
			pickle.dump(clubtemptest, fp)
		with open(picklepath_counter, 'wb') as fp:
			pickle.dump(counter, fp)
		with open(picklepath_allevents, 'wb') as fp:
			pickle.dump(allevents, fp)
		with open(picklepath_allraces, 'wb') as fp:
			pickle.dump(allraces, fp)
		with open(picklepath_wrdata, 'wb') as fp:
			pickle.dump(wrdata, fp)
	except Exception:
		logging.exception("Failed to pickle core variables because of exception.")
	else:
		logging.info("Successfully pickled core variables.")
	
	print("Exiting loop on race %s (Loop #: %s). Shutting down..." % (row['race'], counter))
	logging.info("####### End of Log ########")	
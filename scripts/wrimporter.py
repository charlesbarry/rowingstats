from rowing.models import Rower, Race, Result, Club, Competition, Event, Time, Alias
import csv, datetime, logging, re, sys
from scripts.raceimporter import clubsearch, rowersearch, add_time

# Will match if a flag is there
# "Thames RC A" will match, "Thames RC" will not
flagmatch = re.compile("[a-zA-Z/\s]+[\s][A-Z]$")

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/worldrowing.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

datafile = '../worldrowing/2019_wrc1and2.csv'

olympics = Competition.objects.get(pk=10)
worldchamps = Competition.objects.get(pk=13)
worldcup = Competition.objects.get(pk=16)
euros = Competition.objects.get(pk=17)
juniors = Competition.objects.get(pk=18)
u23s = Competition.objects.get(pk=19)

# putting this function in the config section due to idiosyncracy
def getrname2(word):
	if word == "TT 1":
		return "Time Trial"
	elif word == "Final":
		return "A Final"
	elif word == "FINAL B":
		return "B Final"
	elif word == "FINAL C":
		return "C Final"
	elif word == "FINAL D":
		return "D Final"
	elif word == "FINAL E":
		return "E Final"
	elif word == "F Final":
		return "F Final"
	else:
		return "Race"

def getnat(cname):
	if "USA" in cname or "United States" in cname or "American" in cname:
		return "USA"
	elif "Canada" in cname:
		return "CAN"
	elif "AUS" in cname or "Australia" in cname or "Queensland" in cname:
		return "AUS" 
	else:
		return "GBR"
		
def getcountry(cname):
	if "USA" in cname or "United States" in cname or "American" in cname:
		return "United States of America"
	elif "Canada" in cname or "CAN" in cname:
		return "Canada"
	elif "AUS" in cname or "Australia" in cname or "Queensland" in cname:
		return "Australia" 
	else:
		return "UK"

def getcomp(compname):
	if "Cup" in compname:
		return worldcup
	elif "Under 23" in compname:
		return u23s
	elif "Junior" in compname:
		return juniors
	elif "European" in compname:
		return euros
	elif "World Rowing Championships" in compname:
		return worldchamps
	elif "Olympic" in compname:
		return olympics
	else:
		raise ValueError
		
def wrname(text):
	if '/' in text:
		# branch including WRID
		text.split('/')
		name, num = text.split('/')
		num = int(num)
	else:
		num = None
		name = text
		
	name = (name[name.find(',')+2:] + " " + name[:name.find(',')]).title()

	return name, num
##### END CONFIG #####
try:
	counter = int(sys.argv[2]) # third argument
except IndexError:
	counter = 0

logging.info("Config and preparatory tasks completed.")

#open datafile
with open(datafile, 'r', encoding='UTF-8-sig', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	data = (list(reader))
	
logging.info("Race data successfully loaded.")
print("Starting to create races...")

try:	
	if counter == 0:
		racedata = data
	else:
		racedata = data[counter:]
	
	for row in racedata:
		# skip DNF entries
		if row['Position'] == "0":
			continue

		comp = getcomp(row['Competition'])
		
		# get event
		try:
			thisevent = Event.objects.get(name=row['Event Name'], comp=comp)
		except Event.DoesNotExist:
			logging.info("Event %s for comp %s does not exist. Creating event...", row['Event Name'], comp.name)
			if "x" in row['Event Name']:
				type = 'Sculling'
			else:
				type = 'Sweep'
			
			# get type
			if "TA" in row['Event Name'] or "AS" in row['Event Name'] or "ID" in row['Event Name'] or "PR" in row['Event Name']:
				if "x" in row['Event Name']:
					type = 'Para-Sculling'
				else:
					type = 'Para-Sweep'
			# lwt events
			elif "L" in row['Event Name']:
				if "x" in row['Event Name']:
					type = 'Lwt Sculling'
				else:
					type = 'Lwt Sweep'
			else:
				if "x" in row['Event Name']:
					type = 'Sculling'
				else:
					type = 'Sweep'
					
			# shorter distance for old para events
			if "TA" in row['Event Name'] or "AS" in row['Event Name'] or "ID" in row['Event Name']:
				dist = '1000m'
			else:
				dist = '2000m'
		
			thisevent = Event.objects.create(
				name = row['Event Name'],
				comp = comp,
				type = type,
				distance = dist,
			)
			logging.debug("Event created with parameters as follows - name=%s, type=%s, comp=%s", row['Event Name'], type, comp.name)
		
		# get race - move sequentially through data
		try:			
			rname = (row['Race'] + " " + row['Race Code'][1:]).rstrip()
			
			day = row['Date'][:row['Date'].find('/')]
			month = row['Date'][row['Date'].find('/')+1:row['Date'].rfind('/')]
			year = row['Date'][row['Date'].rfind('/')+1:]
			rdate = datetime.date(int(year), int(month), int(day))
			
			logging.debug("Trying to get race %s", rname)
			thisrace = Race.objects.get(name = rname, date = rdate, event = thisevent)
		except Race.DoesNotExist:
			logging.debug("Race %s does not exist. Creating race...", rname)
			
			# order handling
			if 'Heat' in row['Race'] or 'Prelim' in row['Race']:
				order = 0
			elif 'Repech' in row['Race'] or 'Semif' in row['Race']:
				order = 1
			elif 'Final' in row['Race']:
				order = 2
				
			if comp != u23s and comp != juniors:
				raceclass = "International"
			else:
				raceclass = "Open"
			
			thisrace = Race.objects.create(
				name = rname,
				date = rdate,
				raceclass = raceclass,
				event = thisevent,
				order = order,
				#rnumber = int(race['Race']),
				complete = True,				
			)
			logging.debug("Race created - name=%s, date=%s, event=%s, order=%s", rname, rdate, thisevent.name, order)
			logging.info("Race %s added to DB." % rname)

		except Race.MultipleObjectsReturned:
			logging.error("Multiple results found found for race in race %s, position %s. Aborting loop", thisrace.name, row['Place'])
			raise
		
		# get result		
		try:			
			logging.debug("Seeking result for race %s, position %s", thisrace.name, row['Position'])
			
			# check for flags
			if len(row['Club']) > 3:
				flag = row['Club'][3:]
			else:
				flag = ""
			
			thisresult = Result.objects.get(
				race=thisrace, 
				position=int(row['Position']),
				flag = flag,
				)
		except Result.DoesNotExist:
			logging.debug("No match found for result in race %s, position %s. Creating new result", thisrace.name, row['Position'])
			
			thisresult = Result.objects.create(
				race=thisrace, 
				position=int(row['Position']),
				flag = flag,
				)
			
		except Result.MultipleObjectsReturned:
			logging.error("Multiple results found found for result in race %s, position %s. Aborting loop", thisrace.name, row['Position'])
			raise
		
		# club search for this result
		clubsearch(res=thisresult, cname=row['Club'][:3], country=row['Club'][:3])
		
		# get crewnames
		crewnames = row['Crew'].split(";")
		crewnames = [wrname(x) for x in crewnames]
		
		if "M" in thisevent.name:
			gender = "M"
		elif "W" in thisevent.name:
			gender = "W"
		else:
			gender = "U"
	
		for name, wrid in crewnames:
			rowersearch(res=thisresult, name=name, gender=gender, nationality=row['Club'][:3], club_str=row['Club'][:3], cox=False, wrid=wrid)
			
		# add cox
		if row['Cox'] != '':
			rowersearch(res=thisresult, name=wrname(row['Cox'])[0], nationality=row['Club'][:3], club_str=row['Club'][:3], cox=True, wrid=wrname(row['Cox'])[1])
			
		# add time to this result if none exists
		try:			
			logging.debug("Checking time for race %s, position %s", thisresult.race.name, thisresult.position)
			thistime = Time.objects.get(
				result=thisresult, 
				description="Finish",
				)
		except Time.DoesNotExist:
			if row['Time'] != '00.00.0':
				logging.debug("No matching time found. Adding time")
				add_time("Finish", row['Time'], thisresult, 0)
			
		counter += 1

except KeyboardInterrupt:
	print("Exiting due to keyboard interrupt.")
	logging.info("Exiting main loop during row %s in loop)", str(counter))
	
except Exception:
	logging.exception("Exiting main loop during row %s in loop. Exception detected.", str(counter))
	logging.debug("Vars as follows: %s", str(globals()))

else:
	print("All races completed.")	
	if Race.objects.filter(event__comp=comp, date__in=[rdate], complete=False).count() > 0:
		logging.info("The following races incurred non-critical errors and should be reviewed manually:")
		for r in Race.objects.filter(event__comp=comp, date__in=[rdate], complete=False):
			logging.info("---%s", r.name)
	logging.info("Deleting temporary aliases")
	Alias.objects.filter(temp=True).delete()
	logging.info("All races completed. Exiting...")
finally:
	print("Exiting loop at place #: %s). Shutting down..." % counter)
	logging.info("####### End of Log ########")	
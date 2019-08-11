from rowing.models import Rower, Race, Result, Club, Competition, Event, Time, Alias
import csv, datetime, logging, re, sys
from scripts.raceimporter import clubsearch, rowersearch, add_time

# Will match if a flag is there
# "Thames RC A" will match, "Thames RC" will not
flagmatch = re.compile("[a-zA-Z/\s]+[\s][A-Z]$")

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/marlowlog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

SATDATE = datetime.date(2019, 6, 1)
SUNDATE = datetime.date(2019, 6, 2)
MONDATE = datetime.date(2019, 6, 3)

datafile = '../marlow/2018_Regatta_Results.csv'

rdate = datetime.date(2018, 6, 23)

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

comp = Competition.objects.get(pk=3)
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
		# skip DNS entries
		if row['Status'] == "DNS":
			continue
		
		# get event
		try:
			thisevent = Event.objects.get(name=row['Event Name'], comp=comp)
		except Event.DoesNotExist:
			logging.debug("Event %s does not exist. Creating race...", row['Event Name'])
			if "x" in row['Event Name']:
				type = 'Sculling'
			else:
				type = 'Sweep'
		
			thisevent = Event.objects.create(
				name = row['Event Name'],
				comp = comp,
				type = type,
				distance = '2000m',
			)
			logging.debug("Event created with parameters as follows - name=%s, type=%s, comp=%s", row['Event Name'], type, comp.name)
		
		# get race - move sequentially through data
		try:			
			rname = row['Event Name'] + ' - ' + getrname2(row['Race Id'])
			logging.debug("Trying to get race %s", rname)
			thisrace = Race.objects.get(name = rname, date = rdate, event = thisevent)
		except Race.DoesNotExist:
			logging.debug("Race %s does not exist. Creating race...", rname)
			
			# order handling
			if row['Race Id'] == "TT 1":
				order = 0
			else:
				order = 2
				
			thisrace = Race.objects.create(
				name = rname,
				date = rdate,
				raceclass = "Open",
				event = Event.objects.get(name=row['Event Name']),
				order = order,
				#rnumber = int(race['Race']),
				complete = True,				
			)
			logging.debug("Race created - name=%s, date=%s, event=%s, order=%s", rname, rdate, Event.objects.get(name=row['Event Name']).name, order)
			logging.info("Race %s added to DB." % rname)

		except Result.MultipleObjectsReturned:
			logging.error("Multiple results found found for race in race %s, position %s. Aborting loop", thisrace.name, row['Place'])
			raise
		
		# get result
		# flag handling
		if flagmatch.match(row['Entry Club']) is not None:
			flag = row['Entry Club'][-1]
			clubname = row['Entry Club'][:-2]
		else:
			flag = ''
			clubname = row['Entry Club']
		
		try:			
			logging.debug("Seeking result for race %s, position %s", thisrace.name, row['Place'])
			thisresult = Result.objects.get(
				race=thisrace, 
				position=int(row['Place']),
				flag = flag,
				)
		except Result.DoesNotExist:
			logging.debug("No match found for result in race %s, position %s. Creating new result", thisrace.name, row['Place'])
			thisresult = Result.objects.create(
				race=thisrace, 
				position=int(row['Place']),
				flag = flag,
				)
			
		except Result.MultipleObjectsReturned:
			logging.error("Multiple results found found for result in race %s, position %s. Aborting loop", thisrace.name, row['Place'])
			raise
		
		# club search for this result
		if '/' in clubname:
			# composites branch
			logging.debug("Composite detected: %s", clubname)
			cnames = clubname.split("/")
			for cname in cnames:
				clubsearch(res=thisresult, cname=cname, country=getcountry(cname))
		else:
			clubsearch(res=thisresult, cname=clubname, country=getcountry(clubname))
		
		# fixing doublespace bug
		if "  " in row['Name']:
			rowername = row['Name'].replace("  ", " ")
		else:
			rowername = row['Name']
			
		# fix "Surname, Forename" format
		if "," in rowername:
			sname = rowername[:rowername.find(',')]
			fname = rowername[rowername.find(',')+1:].lstrip()
			rowername = fname + ' ' + sname
			
		# one athlete per row
		if row['Seat'] == 'Coxswain':
			cox = True
		else:
			cox = False
		rowersearch(res=thisresult, name=rowername, gender="M", nationality=getnat(clubname), club_str=clubname, cox=cox)
			
		# add time to this result if none exists
		try:			
			logging.debug("Checking time for race %s, position %s", thisresult.race.name, thisresult.position)
			thistime = Time.objects.get(
				result=thisresult, 
				description="Finish",
				)
		except Time.DoesNotExist:
			logging.debug("No matching time found. Adding time")
			add_time("Finish", row['Adj. Time'], thisresult, 0)
			
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

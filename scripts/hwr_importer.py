from rowing.models import Rower, Race, Result, Club, Competition, Event, Time, Alias

import csv, logging,datetime

##### BEGIN CONFIG #####
logging.basicConfig(filename='./log/hwrlog.log', level=logging.INFO, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))


comp = Competition.objects.get(pk=12) #HWR primary key

### END CONFIG ###

datafile = './data/hwr2019.csv'

with open(datafile, 'r', encoding='UTF-8-sig', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    data = (list(reader))

logging.info("Race data successfully loaded.")
print("Starting to create races...")


racedata = data
for row in racedata:
    try:
        thisevent = Event.objects.get(name=row['Event'], comp=comp)
    except Event.DoesNotExist:
        logging.debug("Event %s does not exist. Creating race...", row['Event'])
        if "x" in row['Event']:
                type = 'Sculling'
        else:
                type = 'Sweep'

        thisevent = Event.objects.create(
                name = row['Event'],
                comp = comp,
                type = type,
                distance = '2000m',
        )
        logging.debug("Event created with parameters as follows - name=%s, type=%s, comp=%s", row['Event'], type, comp.name)
    
        print(thisevent)


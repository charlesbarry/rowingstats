# custom command to check that no rower exists in the same race

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Result, Rower, Race, Score, Event, ScoreRanking
from trueskill import Rating, rate, setup
from django.db import transaction
from django.db.models import Avg
from itertools import groupby
import datetime, logging

logging.basicConfig(filename='./log/rowercheck.log', level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info("##### START OF LOG ######")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

class Command(BaseCommand):
    help = 'Recalculates the scores of rowers'

    '''def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)'''

    def handle(self, *args, **options):
        duplicates = []
        unusuals = []
        iavgs = []
        counter = 0
        for trace in Race.objects.all():    
            checked = set()
            for tresult in trace.result_set.all():
                for athlete in tresult.crew.all():
                    if athlete in checked:
                        try:
                            #duplicates.append([athlete.name, tresult.position, trace.name, trace.pk])
                            logging.error("Duplicate found: name=%s, race=%s (pk: %s), position=%s", athlete.name, trace.name, trace.pk, tresult.position)
                            trace.complete=False
                        except IndexError:
                            logging.error("IndexError incurred for attempt to add %s, %s and %s to duplicates", athlete.name, tresult.position, trace.name)
                    else:
                        checked.add(athlete)
                    
                if tresult.crew.count() not in [1, 2, 4, 8]:
                    try:
                        #unusuals.append([tresult.crew.count(), trace.name, tresult.clubs.all()[0].name, trace.pk])
                        logging.error("Unusual crew number found: race=%s (pk: %s), club=%s, crewsize=%s", trace.name, trace.pk, tresult.clubs.all()[0].name, tresult.crew.count())
                        trace.complete=False
                    except IndexError:
                        logging.error("IndexError incurred for %s - appears no clubs in result. Race pk: %s", tresult.crew.count(), trace.name, trace.pk)
                        trace.complete=False
                    #print("Unusual crew number (%s) found in %s" % (trace.name, tresult.crew.count()))
        
            # check the average number of people in each crew
            try:
                check_avg = sum([item.crew.count() for item in trace.result_set.all()]) / trace.result_set.count()
                if check_avg not in [1.0, 2.0, 4.0, 8.0]:
                    logging.error("Inconsistent average found: race=%s (pk: %s), average=%s", trace.name, trace.pk, round(check_avg,2))
                    trace.complete=False
                    #iavgs.append([check_avg, trace.name, trace.pk])
            except ZeroDivisionError:
                logging.error("ZeroDivisionError incurred for %s - appears no results. Race pk: %s", trace.name, trace.pk)
                
            if trace.result_set.all().count() < 2:
                logging.warning("Race lacks sufficient results to be ranked: race=%s (pk: %s)", trace.name, trace.pk)
                trace.complete=False
            
            trace.save()
            if counter % 100 == 0:
                print("Race %s of %s checked." % (counter, Race.objects.all().count()))
            counter += 1
        
        '''
        if len(duplicates) > 0:
            print("Duplicates were found. See log")
            for item in duplicates:
                #print(item[0], " - ", item[1], " - ", item[2])
                
                
        else:
            print("No duplicates found")
            logging.info("No duplicates found")

        if len(unusuals) > 0:
            print("Unusual crew numbers were found. See log")
            for item in unusuals:
                #print(item[0], " - ", item[1], " - ", item[2])
                logging.error("Unusual crew number found: race=%s (pk: %s), club=%s, crewsize=%s", item[1], item[3], item[2], item[0])
                
        else:
            print("No unusual crew numbers found")
            logging.info("No duplicates found")
            
        if len(iavgs) > 0:
            print("Inconsistent averages were found. See log")
            for item in iavgs:
                #print(item[1], " - Average: ", item[0])
                
        else:
            print("No inconsistent averages found")
            logging.info("No inconsistent averages")
        '''
        
        logging.info("##### END OF LOG ######")
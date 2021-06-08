# generates trees for HRR draws

from django.core.management.base import BaseCommand, CommandError
from rowing.models import Event, Race, EventInstance, KnockoutRace
import datetime
    
class Command(BaseCommand):
    help = 'Creates the race tree for HRR'
    
    weds_date = datetime.date(2018, 7, 4)
    thurs_date = datetime.date(2018, 7, 5)
    fri_date = datetime.date(2018, 7, 6)
    sat_date = datetime.date(2018, 7, 7)
    sun_date = datetime.date(2018, 7, 8)

    def add_arguments(self, parser):
        parser.add_argument('--event', action='store', help='Event PK this is being created for')
        parser.add_argument('--rounds', action='store', help='Number of rounds')
        parser.add_argument('--makeraces', action='store_true', help='Make the races not just the tree')
        parser.add_argument('--year', action='store', default='2018', help='Year')
        # ideally passes a list of days which the event is happening on
        parser.add_argument('--days', action='store', nargs='*', help='Which days is this event on')

    def handle(self, *args, **options):
        if options['event']:
            KEvent = Event.objects.get(pk=options['event'])
        else:
            raise ValueError
            
        if options['rounds']:
            rounds = int(options['rounds'])
        else:    
            raise ValueError
            
        year = int(options['year'])
        
        # prime the days
        rdays = []
        
        #create the event instance
        try:
            EI = EventInstance.objects.get(event=KEvent, year=year)
        except EventInstance.DoesNotExist:
            EI = EventInstance.objects.create(event=KEvent, year=year)
        
        #create the knockout entries
        # loops from 1 to rounds eg 1 to 4
        for round in range(1, rounds+1):
            # loops from 1 to 2^rounds eg 1 to 16
            # if rounds = 4, round = 1, then slots = 16
            for slot in range(1, 2**(rounds-round+1)+1):
                    nkr = KnockoutRace.objects.create(
                        round = round,
                        slot = slot,
                    )
                if round > 1:
                    # add the parents of the current race 
                    tparent = KnockoutRace.objects.get(knockout=EI, round=(round-1), slot=((2*slot)-1))
                    lparent = KnockoutRace.objects.get(knockout=EI, round=(round-1), slot=(2*slot))
                    tparent.child = nkr
                    tparent.save()
                    lparent.child = nkr
                    lparent.save()
        
        #if makeraces options is specified, add new races for each of the knockout entries
        if options['makeraces']:
            for kr in KnockoutRace.objects.filter(knockout=EI):
                try:
                    ar = Race.objects.get(knockoutrace=kr)
                except Race.DoesNotExist:
                    ar = Race.objects.create(
                        name = (str(EI) + ' - (round=' + str(round) + ', slot=' + str(slot) + ')'),
                        date = date.date(2018, 7, 1),
                        event = KEvent,
                        complete = False,
                    )
                
# script to import the csv data into sqlite

# TODO - take out masters races
## remove rowers with place 0
## check that rfind on race identifiers is fixed

from rowing.models import Rower, Race, Result, Club, Competition, Event
import csv
from django.db.models import Q
import datetime
#from django.core.exceptions import MultipleObjectsReturned 
import sys

if sys.argv[1] == "2013":
	SATDATE = datetime.date(2013, 6, 15)
	SUNDATE = datetime.date(2013, 6, 16)
	SATDATE_str = "6/15/2013"
	SUNDATE_str = "6/16/2013"
	datafile = "data/2013_Marlow.csv"
elif sys.argv[1] == "2014":
	SATDATE = datetime.date(2014, 6, 21)
	SUNDATE = datetime.date(2014, 6, 22)
	SATDATE_str = "6/21/2014"
	SUNDATE_str = "6/22/2014"
	datafile = "data/2014_Marlow.csv"
elif sys.argv[1] == "2015":
	SATDATE = datetime.date(2015, 6, 20)
	SUNDATE = datetime.date(2015, 6, 21)
	SATDATE_str = "6/20/2015"
	SUNDATE_str = "6/21/2015"
	datafile = "data/2015_Marlow.csv"
elif sys.argv[1] == "2016":
	SATDATE = datetime.date(2016, 6, 18)
	SUNDATE = datetime.date(2016, 6, 19)
	SATDATE_str = "18/06/2016"
	SUNDATE_str = "19/06/2016"
	datafile = "data/2016_Marlow.csv"
elif sys.argv[1] == "2017":
	SATDATE = datetime.date(2017, 6, 17)
	SUNDATE = datetime.date(2017, 6, 18)
	SATDATE_str = "6/17/2017"
	SUNDATE_str = "6/18/2017"
	datafile = "data/2017_Marlow.csv"

# pk is 3 on both testing and production
marlow = Competition.objects.get(pk=3)

# composite placeholder - 188 in dev, 362 in production
composite_placeholder = Club.objects.get(pk=188)

composite_list = []
clubtemptest = []
crewtemptest = []

with open(datafile, 'r', encoding='UTF-8-sig', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	data = (list(reader))
	
# initial pass over the data - group the rows, create events for each
if Race.objects.filter(event__comp=marlow, date__in=[SATDATE, SUNDATE]).count() > 0:
	try:
		craces = Race.objects.filter(event__comp=marlow, date__in=[SATDATE,SUNDATE])[sys.argv[2]:]
	except IndexError:
		craces = Race.objects.filter(event__comp=marlow, date__in=[SATDATE,SUNDATE])
else:	
	# create a unique list of races
	events = set()
	for row in data:
		events.add(row['Event Name'])
	
	cevents = []
	ecounter = 0
	for event in events:
		# conveniently, all the sculling races have x on the end of their name.
		if "x" in event:
			type = 'Sculling'
		else:
			type = 'Sweep'
	
		# avoid junior events e.g. J14.8x+
		if event[:1] != "J":
			new_event = Event.objects.create(
				name = event,
				comp = marlow,
				type = type,
				distance = '2000m',
			)
			cevents.append(new_event)
		else:
			pass
			
		print("Event %s of %s entered into DB." % (ecounter, len(events)))
		ecounter += 1
	
	craces = []
	rcounter = 0
	for event in cevents:
		# create a filtered list of all racenames for that event
		fraces = [x for x in data if x['Event Name'] == event.name]
		
		# create a unique list of the race names and event names
		# could have just inherited the name from the event in the for loop above - oh well
		fracenames = set()
		for frace in fraces:
			# tuple has to be used rather than list
			fracenames.add((frace['Race Id'], frace['Event Name'], frace['Date']))
		
		# create a new race from members of the fracenames set
		for f in fracenames:
			if "Final" in f[0]:
					order = 2
			elif "Rep" in f[0]:
				order = 1
			else:
				order = 0
				
			if f[2] == SATDATE_str:
				rdate = SATDATE
			elif f[2] == SUNDATE_str:
				rdate = SUNDATE
			
			new_race = Race.objects.create(
				name = f[1] + " - " + f[0],
				date = rdate,
				raceclass = "Club",
				event = event,
				order = order,
				complete = False,				
			)
			craces.append(new_race)
			
			print("Race %s entered into DB." % rcounter)
			rcounter += 1

# crew is a list of names
def crewsearch(new_res, race, rname, row, irish, club_str):
	if row['Seat'] != 'Coxswain':
		if "W" in race.event.name:
			gender = "W"
		else:
			gender = "M"
		
		# exception to shortcut logic if one exact match found
		try:
			exactcheck = Rower.objects.get(name = rname, gender = gender)
			new_res.crew.add(exactcheck)
			return None
		
		except Rower.MultipleObjectsReturned:
			print("!"*20)
			print("Error: multiple objects returned for an exact name and gender match.")
			print("Search database for duplicates of %s." % rname)
			print("!"*20)
			return None
		
		except Rower.DoesNotExist:
			pass
		
		# commence looser search
		# get the surname - obtains the word after the last space in the name
		if rname.find("(") == -1:
			sname = rname[(rname.rfind(" ") + 1):] 
		else:
			tname = rname[:rname.find("(")].rstrip()
			sname = tname[(tname.rfind(" ") + 1):]
		# Q object used to do an OR query
		choicelist = Rower.objects.filter(Q(name__icontains = rname) | Q(name__icontains = sname), name__startswith = rname[:1], gender = gender)
		
		# branch caused by prior error in the split function above
		if len(choicelist) > 50:
			print("A search for %s has generated a very large choicelist (%s results). Debug info as follows:" % (rname, len(choicelist)))
			print("Surname: %s" % sname)
			print("Shortened rname: %s" % rname[:1])
			print("Full crew information:")
			for item in crewl:
				print(item, ",")
			return None
		elif len(choicelist) > 0:				
			print("#"*20)
			print("Input required for rower %s (of club %s)" % (rname, club_str))
			# print all the choices - the ,1 starts enumeration at 1
			for i, item in enumerate(choicelist, 1):
				print("%s): %s - %s - %s" % (i, item.name, item.gender, item.nationality))
				
				# show all associated clubs
				assoc_clubs = set()
				for res1 in item.result_set.all():
					for club in res1.clubs.all():
						if club is not None:
							assoc_clubs.add(club.name)
				print("Associated clubs - %s" % str(assoc_clubs))
			
			# infinite loop to ensure you input correctly
			print("#"*20)
			print("Enter the number of the result to add to the crew. Or choose 0 to ignore this list and add a new entry to the DB. Make the number negative to modify the name of that rower.")
			while True:
				try:
					choice = int(input("Your choice: "))
				except ValueError:
					print("That wasn't an integer. Try again.")
					continue
				if choice > len(choicelist):
					print("Choice out of range. Try again.")
					continue
				if choice < -len(choicelist):
					print("Choice out of range. Try again.")
					continue
				else:
					break
			
			# the ignore branch
			if choice == 0:
				if irish == True:
					nationality = "IRE"
				else:
					nationality = "GBR"
				new_rower = Rower.objects.create(
					name = rname + " (" + club_str + ")",
					gender = gender,
					nationality = nationality,
				)
				new_res.crew.add(new_rower)
				print("New rower %s added to the DB and the crew." % rname)
				crewtemptest.append((rname, new_rower))
			
			# otherwise, add that rower to the crew. 
			# NB choice is -1 because the list enumerated for entry is +1 to reserve the ignore branch as 0.
			elif choice > 0:
				new_res.crew.add(choicelist[choice - 1])
				print("Rower %s added to the crew." % choicelist[choice - 1].name)
				crewtemptest.append((rname, choicelist[choice - 1]))
			
			# branch to modify the rower name
			elif choice < 0:
				achoice = abs(choice)
				new_res.crew.add(choicelist[achoice-1])
				print("Enter the name that the choice should be updated to.")
				newname = input("Name: ")
				choicelist[achoice - 1].name = newname
				choicelist[achoice - 1].save()
				print("Rower %s added to the crew." % choicelist[achoice - 1].name)
				crewtemptest.append((rname, choicelist[achoice - 1]))
			
		# the branch for when no search results found
		else:
			if irish == True:
				nationality = "IRE"
			else:
				nationality = "GBR"
			new_rower = Rower.objects.create(
				name = rname,
				gender = gender,
				nationality = nationality,
			)
			new_res.crew.add(new_rower)
			print("No rower found under name %s. Added to the database" % rname)

# function to search for club members goes here...
def clubsearch(new_res, race, cname, composite, irish):	
	try:
		exactcheck = Club.objects.get(name = cname)
		new_res.clubs.add(exactcheck)
	
	except Club.MultipleObjectsReturned:
		print("!"*20)
		print("Error: multiple clubs returned for an exact name match.")
		print("Search database for duplicates of %s." % rname)
		print("!"*20)
	
	except Club.DoesNotExist:
		pass
	
	# else search on the basis of the first four letters of the club name
	clubchoice = Club.objects.filter(name__icontains = cname[:4])
	
	if composite == True:
		new_res.clubs.add(composite_placeholder)
		print("%s was flagged as a composite and you will need to resolve this manually - Race: %s" % (cname, race.name))	
		composite_list.append((cname, race.name))
	elif len(clubchoice) > 0:
		print("#"*20)
		print("Input required for club name %s" % cname)
		print("Here are the clubs that matched with this name:")
		for i, item in enumerate(clubchoice, 1):
				print("%s): %s" % (i, item.name))
				
		print("#"*20)
		print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB. Choose -1 to add a new club but with manual name entry. Choose -2 to search for a different string.")
		while True:
			try:
				choice = int(input("Your choice: "))
			except ValueError:
				print("That wasn't an integer. Try again.")
				continue
			if choice > len(clubchoice):
				print("Choice out of range. Try again.")
				continue
			if choice < -2:
				print("Choice out of range. Try again.")
				continue
			else:
				break
		
		if choice == -1:
			choice2 = input("Please type the name of this club: ")
			newclub = Club.objects.create(name=choice2)
			new_res.clubs.add(newclub)
			print("%s added to the DB." % choice2)
		
		# search for different string branch
		elif choice == -2:
			while True:
				choice5 = input("Please type the string you want to search for: ")
				if len(choice5) < 3:
					print("Sorry, you need to enter a string of at least four digits to prevent excessively long results.")
					continue
				else:
					clubchoice2 = Club.objects.filter(name__icontains = choice5)
					if clubchoice2.count() == 0:
						print("Sorry, no matches for that string.")
						while True:
							print("Enter manually (M) or search again (S)?")
							choice6 = input("M/S: ")
							if choice6 == "S":
								break
							elif choice6 == "M":
								while True:
									choice4 = input("Please type the name of this club (non-UK country will be appended automatically): ")
									if len(choice4) < 2:
										print("Sorry but that's not a valid Club name. Try again.")
										continue
									else:
										if irish == True:
											choice4 += ", Ireland"
										newclub = Club.objects.create(name=choice4)
										new_res.clubs.add(newclub)
										print("%s added to the DB." % choice4)
										# append to club temptest to avoid repetition
										clubtemptest.append((cname, newclub))
										break
								break
							else:
								print("Sorry, that wasn't a valid choice.")
						break
					
					else:
						print("Here are the clubs that matched with this name:")
						for i, item in enumerate(clubchoice2, 1):
								print("%s): %s" % (i, item.name))
						print("#"*20)
						print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB. Choose -1 to add a new club but with manual name entry.")
						while True:
							try:
								choice = int(input("Your choice: "))
							except ValueError:
								print("That wasn't an integer. Try again.")
								continue
							if choice > len(clubchoice2):
								print("Choice out of range. Try again.")
								continue
							if choice < -1:
								print("Choice out of range. Try again.")
								continue
							else:
								break
						
						if choice == -1:
							choice2 = input("Please type the name of this club: ")
							newclub = Club.objects.create(name=choice2)
							new_res.clubs.add(newclub)
							print("%s added to the DB." % choice2)
							break
						
						elif choice == 0:
							newclub = Club.objects.create(name=choice5)
							new_res.clubs.add(newclub)
							print("%s added to the DB." % newclub.name)
							break
						
						else:
							new_res.clubs.add(clubchoice2[choice-1])
							print("%s added to the result." % clubchoice2[choice-1])
							# append to clubtemptest to avoid repetition
							clubtemptest.append((cname, clubchoice2[choice-1]))
							break
		
		
		elif choice == 0:
			newclub = Club.objects.create(name=cname)
			new_res.clubs.add(newclub)
			print("%s added to the DB." % newclub.name)
		
		else:
			new_res.clubs.add(clubchoice[choice-1])
			print("%s added to the result." % clubchoice[choice-1])
			# append to clubtemptest to avoid repetition
			clubtemptest.append((cname, clubchoice[choice-1]))
		
	else:
		print("%s was not found in the DB. Enter Club name manually? (Y/N or Z to re-search with different string)" % cname)
		while True:
			choice3 = input("Y/N: ")
			if choice3 == "Y":
				while True:
					choice4 = input("Please type the name of this club (non-UK country will be appended automatically): ")
					if len(choice4) < 2:
						print("Sorry but that's not a valid Club name. Try again.")
						continue
					else:
						if irish == True:
							choice4 += ", Ireland"
						newclub = Club.objects.create(name=choice4)
						new_res.clubs.add(newclub)
						print("%s added to the DB." % choice4)
						# append to club temptest to avoid repetition
						clubtemptest.append((cname, newclub))
						break
				break
			elif choice3 == "N":
				if irish == True:
					cname += ", Ireland"
				newclub = Club.objects.create(name=cname)
				new_res.clubs.add(newclub)
				print("%s didn't match so it has been added to the DB." % newclub.name)
				break
			elif choice3 == "Z":
				while True:
					choice5 = input("Please type the string you want to search for: ")
					if len(choice5) < 3:
						print("Sorry, you need to enter a string of at least four digits to prevent excessively long results.")
						continue
					else:
						clubchoice2 = Club.objects.filter(name__icontains = choice5)
						if clubchoice2.count() == 0:
							print("Sorry, no matches for that string.")
							while True:
								print("Enter manually (M) or search again (S)?")
								choice6 = input("M/S: ")
								if choice6 == "S":
									break
								elif choice6 == "M":
									while True:
										choice4 = input("Please type the name of this club (non-UK country will be appended automatically): ")
										if len(choice4) < 2:
											print("Sorry but that's not a valid Club name. Try again.")
											continue
										else:
											if irish == True:
												choice4 += ", Ireland"
											newclub = Club.objects.create(name=choice4)
											new_res.clubs.add(newclub)
											print("%s added to the DB." % choice4)
											# append to club temptest to avoid repetition
											clubtemptest.append((cname, newclub))
											break
									break
								else:
									print("Sorry, that wasn't a valid choice.")
							break
						
						else:
							print("Here are the clubs that matched with this name:")
							for i, item in enumerate(clubchoice2, 1):
									print("%s): %s" % (i, item.name))
							print("#"*20)
							print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB. Choose -1 to add a new club but with manual name entry.")
							while True:
								try:
									choice = int(input("Your choice: "))
								except ValueError:
									print("That wasn't an integer. Try again.")
									continue
								if choice > len(clubchoice2):
									print("Choice out of range. Try again.")
									continue
								if choice < -1:
									print("Choice out of range. Try again.")
									continue
								else:
									break
							
							if choice == -1:
								choice2 = input("Please type the name of this club: ")
								newclub = Club.objects.create(name=choice2)
								new_res.clubs.add(newclub)
								print("%s added to the DB." % choice2)
								break
							
							elif choice == 0:
								newclub = Club.objects.create(name=choice5)
								new_res.clubs.add(newclub)
								print("%s added to the DB." % newclub.name)
								break
							
							else:
								new_res.clubs.add(clubchoice2[choice-1])
								print("%s added to the result." % clubchoice2[choice-1])
								# append to clubtemptest to avoid repetition
								clubtemptest.append((cname, clubchoice2[choice-1]))
								break
				break
			else:
				print("Sorry, that wasn't a valid Y/N/Z. Try again.")
				continue

# new main loop - loop through the identified races in the sheet
counter = 1
for race in craces:
	# split the race name into the Event and Race Names
	ename = race.name[:(race.name.rfind("-")-1)]
	rname = race.name[(race.name.rfind("-")+2):]
	
	# filter the rows to find only those relating to that race
	fraces2 = [x for x in data if x['Event Name'] == ename and x['Race Id'] == rname]
	
	entries = set()
	# because Marlow has athlete not crew level rows, we need to add a further refine
	for row in fraces2:
		entries.add(row['Place'])
	
	for entry in entries:
		fraces3 = [x for x in fraces2 if x['Place'] == entry]

		new_res = Result.objects.create(
		race = race,
		position = fraces3[0]['Place'],
		flag = '',
		)
		
		for row in fraces3:
			composite = False
			isirish = False
			
			# get the fullname - lstrip/rstrip removes whitespace
			rname = row['Name'].rstrip()
			rname = rname.lstrip()
			
			# splits "Surname, Forename"
			# removes . from "Surname, Initial."
			if "." in rname[-1:]:
				rname = rname[:-1]
			rname1 = rname[:rname.find(",")]
			rname2 = rname[rname.find(",")+2:]
			
			# recombines as "Forename Surname"
			rname = rname2 + " " + rname1
			
			if any(rname in i for i in crewtemptest):
				for name_i in crewtemptest:
					if rname in name_i[0]:
						new_res.crew.add(name_i[1])
						print("%s added to the result." % name_i[1].name)
			else:
				crewsearch(new_res, race, rname, row, isirish, row["Entry Club"])
				
		# clubtemptest used to avoid repetitive idiosycratic corrections eg Molesey BC -> Molesey Boat Club
		# structure is [(Incorrect entry, club object)]
		if any(fraces3[0]["Entry Club"] in i for i in clubtemptest):
			for clubt in clubtemptest:
				if fraces3[0]["Entry Club"] in clubt[0]:
					new_res.clubs.add(clubt[1])
					print("%s added to the result." % clubt[1].name)
		else:
			clubsearch(new_res, race, row["Athlete's Club"], composite, isirish)
		
	print("Race %s of %s completed." % (counter, len(craces)+1))
	counter += 1
	
	# should only be reached when all crew/clubs added. Prevents error accumulating un-noticed
	race.complete = True
	race.save()
	
print("All races completed. The following composite crews need to be resolved manually:")
for item in composite_list:
	print("Club searched: %s, Race name: %s" % (item[0], item[1]))
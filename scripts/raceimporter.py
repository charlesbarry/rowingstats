# library for the other importers in the directory

from rowing.models import Rower, Club, Result, Time
from django.db.models import Q
import logging, datetime

def add_time(desc, ts, result, order):
	# assumes time string (ts) is NN:NN.N e.g. 5:51.23
	logging.debug("add_time() called with parameters as follows: desc=%s, ts=%s, result=%s, order=%s", desc, ts, result, order)
	
	# parse the time string
	try:
		# ie find the '.23' in 5:51.23
		micro = int(ts[ts.find(".")+1:])
		# move tenths to hundredths of second - .2 to .20
		if micro < 10:
			micro *= 10
		
		# standardise to millionths of second
		micro *= 10000
		
	except Exception as e:
		logging.debug("Exception incurred - %s - setting micro as 0", str(e))
		micro = 0
	
	try:
		ttime = datetime.time(
			hour = 0,
			minute = int(ts[:ts.find(":")]),
			second = int(ts[(ts.find(":")+1):ts.find(".")]),
			microsecond = micro
		)
		
		logging.debug("ttime is: %s", str(ttime))
		
		Time.objects.create(
			description = desc,
			result = result,
			order = order,
			value = ttime,
		)
	except ValueError:
		logging.warning("Invalid value when adding time for result %s - value provided: %s", result, ts)
		return None
	except Exception as e:
		logging.error("Exception incurred: %s", str(e))
		# the raise causes an exception in the higher layer (i.e. that invokes the function)
		raise e

# crew is a list of names
def crewsearch(new_res, race, name, nationality, club_str, crewtemptest):
	logging.debug("Crewsearch called with parameters as follows:")
	logging.debug("--new_res: %s", str(new_res))
	logging.debug("--race: %s", str(race))
	logging.debug("--name: %s", name)
	logging.debug("--nationality: %s", nationality)
	logging.debug("--club_str: %s", club_str)
	#logging.debug("--crewtemptest: %s", str(crewtemptest))
	
	# get the fullname - lstrip/rstrip removes whitespace
	rname = name.rstrip()
	rname = rname.lstrip()
	
	if "Women" in race.name:
		gender = "W"
	else:
		gender = "M"
	
	# exception to shortcut logic if one exact match found
	logging.debug("Trying exact match for name=%s and gender=%s", rname, gender)
	try:
		exactcheck = Rower.objects.get(name = rname, gender = gender)
		new_res.crew.add(exactcheck)
		
		# skipping the rest of the function due to success
		crewtemptest.append((rname, exactcheck))
		return crewtemptest
	
	except Rower.MultipleObjectsReturned:
		print("!"*20)
		print("Error: multiple objects returned for an exact name and gender match.")
		print("Search database for duplicates of %s." % rname)
		print("!"*20)
		
		logging.error("Multiple objects returned for a search of %s", rname)
		
		# skipping this person due to error
		return crewtemptest
	
	except Rower.DoesNotExist:
		logging.debug("No such match found")
	
	# commence looser search
	# get the surname - obtains the word after the last space in the name
	if rname.find("(") == -1:
		sname = rname[(rname.rfind(" ") + 1):] 
	else:
		tname = rname[:rname.find("(")].rstrip()
		sname = tname[(tname.rfind(" ") + 1):]
	# Q object used to do an OR query
	choicelist = Rower.objects.filter(Q(name__icontains = rname) | Q(name__icontains = sname), name__startswith = rname[:1], gender = gender)
	logging.debug("Looser search started, parameters as follows: name=%s, surname=%s, initial=%s, gender=%s", rname, sname, rname[:1], gender)
	
	# branch caused by prior error in the split function above
	if len(choicelist) > 250:
		print("A search for %s has generated a very large choicelist (%s results). Debug info as follows:" % (rname, len(choicelist)))
		print("Surname: %s" % sname)
		print("Shortened rname: %s" % rname[:1])
		logging.error("A search for %s and %s has generated a very large choicelist (%s results).", rname, sname, len(choicelist))
		return crewtemptest
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
			new_rower = Rower.objects.create(
				name = rname,
				gender = gender,
				nationality = nationality,
			)
			new_res.crew.add(new_rower)
			logging.debug("New rower added to the DB - name=%s, gender=%s, nationality=%s", rname, gender, nationality)
			print("New rower %s added to the DB and the crew." % rname)
			crewtemptest.append((rname, new_rower))
			return crewtemptest
		
		# otherwise, add that rower to the crew. 
		# NB choice is -1 because the list enumerated for entry is +1 to reserve the ignore branch as 0.
		elif choice > 0:
			new_res.crew.add(choicelist[choice - 1])
			print("Rower %s added to the crew." % choicelist[choice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[choice - 1].name)
			crewtemptest.append((rname, choicelist[choice - 1]))
			return crewtemptest
		
		# branch to modify the rower name
		elif choice < 0:
			achoice = abs(choice)
			new_res.crew.add(choicelist[achoice-1])
			print("Enter the name that the choice should be updated to.")
			newname = input("Name: ")
			choicelist[achoice - 1].name = newname
			choicelist[achoice - 1].save()
			print("Rower %s added to the crew." % choicelist[achoice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[achoice - 1].name)
			crewtemptest.append((rname, choicelist[achoice - 1]))
			return crewtemptest
			
	# the branch for when no search results found
	else:
		new_rower = Rower.objects.create(
			name = rname,
			gender = gender,
			nationality = nationality,
		)
		new_res.crew.add(new_rower)
		logging.debug("No rower found with name=%s. Added to the DB with gender=%s and nationality=%s.", rname, gender, nationality)
		print("No rower found under name %s. Added to the database" % rname)

	return crewtemptest
	
# function to search for club members
def clubsearch(new_res, race, cname, composite, nationality, clubtemptest):	
	logging.debug("Clubsearch called with parameters as follows:")
	logging.debug("--new_res: %s", str(new_res))
	logging.debug("--race: %s", str(race))
	logging.debug("--name: %s", cname)
	logging.debug("--composite: %s", str(composite))
	logging.debug("--nationality: %s", nationality)
	#logging.debug("--clubtemptest: %s", str(clubtemptest))
	
	logging.debug("Trying exact match for name %s", cname)
	try:
		exactcheck = Club.objects.get(name = cname)
		new_res.clubs.add(exactcheck)
		
		clubtemptest.append((cname, exactcheck))
		return clubtemptest
	
	except Club.MultipleObjectsReturned:
		print("!"*20)
		print("Error: multiple clubs returned for an exact name match.")
		print("Search database for duplicates of %s." % cname)
		print("!"*20)
		
		logging.error("Multiple objects returned for a search of %s", cname)
	
		return clubtemptest
		
	except Club.DoesNotExist:
		logging.debug("No such match found")
	
	# else search on the basis of the first four letters of the club name
	clubchoice = Club.objects.filter(name__icontains = cname[:4])
	logging.debug("Searching for matches for %s. (%s matches found)", cname[:4], str(len(clubchoice)))
	
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
			logging.debug("Club %s added to the DB.", newclub.name)
		
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
										if nationality == "IRE":
											choice4 += ", Ireland"
										newclub = Club.objects.create(name=choice4)
										new_res.clubs.add(newclub)
										print("%s added to the DB." % choice4)
										logging.debug("Club %s added to the DB.", choice4)
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
							logging.debug("Club %s added to the DB.", newclub.name)
							break
						
						elif choice == 0:
							newclub = Club.objects.create(name=choice5)
							new_res.clubs.add(newclub)
							print("%s added to the DB." % newclub.name)
							logging.debug("Club %s added to the DB.", newclub.name)
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
			logging.debug("Club %s added to the DB.", newclub.name)
		
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
						if nationality == "IRE":
							choice4 += ", Ireland"
						newclub = Club.objects.create(name=choice4)
						new_res.clubs.add(newclub)
						print("%s added to the DB." % choice4)
						# append to club temptest to avoid repetition
						clubtemptest.append((cname, newclub))
						break
				break
			elif choice3 == "N":
				if nationality == "IRE":
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
											if nationality == "IRE":
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

	return clubtemptest
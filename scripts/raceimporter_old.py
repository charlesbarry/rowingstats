
def rowersearch_bk(new_res=None, race=None, name=None, gender="U", nationality="GBR", club_str=None, crewtemptest=[], add_exact=True, cox=False):
	logging.debug("Crewsearch called with parameters as follows:")
	logging.debug("--new_res: %s", str(new_res))
	logging.debug("--race: %s", str(race))
	logging.debug("--name: %s", name)
	logging.debug("--nationality: %s", nationality)
	logging.debug("--club_str: %s", club_str)
	#logging.debug("--crewtemptest: %s", str(crewtemptest))
	
	# exceptions
	if new_res is None:
		raise Exception("No result specified in search")
	
	if race is None:
		raise Exception("No race specified in search")
	
	if name is None:
		raise Exception("No name specified in search")
	
	# get the fullname - lstrip/rstrip removes whitespace
	rname = name.rstrip()
	rname = rname.lstrip()
	
	# exception to shortcut logic if one exact match found
	logging.debug("Trying exact match for name=%s and gender=%s", rname, gender)
	try:
		exactcheck = Rower.objects.get(name = rname, gender = gender)
		if cox == True:
			new_res.cox.add(exactcheck)
		else:
			new_res.crew.add(exactcheck)
		
		# this if statement (on by default) allows large crewtemptests to avoid adding simple exact matches.
		# Turn off if you have very standardised data that will match the DB
		if add_exact:
			crewtemptest.append((name, exactcheck))
		
		# skipping the rest of the function due to success
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
		sname = rname[rname.rfind(" "):] 
	else:
		tname = rname[:rname.find("(")].rstrip()
		# space before surname to help with v short surnames eg Lo
		sname = tname[tname.rfind(" "):]
	# Q object used to do an OR query
	# TODO shorten choicelist where doesn't end with SNAME
	# EITHER starts with initial or starts with 
	# gender__in used in case search against M or W made when rower has only U as prev race history
	choicelist = Rower.objects.filter(Q(name__icontains = rname) | Q(name__icontains = sname), name__startswith = rname[:1], name__iendswith = sname, gender__in = [gender, "U"])
	logging.debug("Looser search started, parameters as follows: name=%s, surname=%s, initial=%s, gender=%s", rname, sname, rname[:1], gender)
	
	# method shortening choicelist where firstname doesn't match
	# EG Tom Middleton != Tim Middleton
	# if search is not initials or initial.
	# think about multiple initial eg AG Grace or A. G. Grace
	if len(rname[:rname.find(" ")]) > 2:
		for item in choicelist:
			# check if both DB and search have fullnames - 2 includes intal
			if len(item.name[:item.name.find(" ")]) > 2:
				# check for exact case insensitive match
				db_str = item.name[:item.name.find(" ")]
				r_str = rname[:rname.find(" ")]
				# if don't match, remove			
				# exception for Tim, Tom, Oli and Fred - nicknames
				exceptionlist = ['tim', 'tom', 'oli', 'fred']
				if any(db_str.lower() in word for word in exceptionlist) or any(r_str.lower() in word for word in exceptionlist):
					pass
				elif db_str.lower() != r_str.lower():
					choicelist = choicelist.exclude(id=item.id)
			
	
	# branch caused by prior error in the split function above
	if choicelist.count() > 250:
		print("A search for %s has generated a very large choicelist (%s results). Debug info as follows:" % (rname, len(choicelist)))
		print("Surname: %s" % sname)
		print("Shortened rname: %s" % rname[:1])
		logging.error("A search for %s and %s has generated a very large choicelist (%s results).", rname, sname, len(choicelist))
		return crewtemptest
	## TODO if exactly 1 match and the club is the same == that match
	elif choicelist.count() > 0:				
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
			if cox == True:
				new_res.cox.add(new_rower)
			else:
				new_res.crew.add(new_rower)
			logging.debug("New rower added to the DB - name=%s, gender=%s, nationality=%s", rname, gender, nationality)
			print("New rower %s added to the DB and the crew." % rname)
			crewtemptest.append((name, new_rower))
			return crewtemptest
		
		# otherwise, add that rower to the crew. 
		# NB choice is -1 because the list enumerated for entry is +1 to reserve the ignore branch as 0.
		elif choice > 0:
			if cox == True:
				new_res.cox.add(choicelist[choice - 1])
			else:
				new_res.crew.add(choicelist[choice - 1])
			print("Rower %s added to the crew." % choicelist[choice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[choice - 1].name)
			crewtemptest.append((name, choicelist[choice - 1]))
			return crewtemptest
		
		# branch to modify the rower name
		elif choice < 0:
			achoice = abs(choice)
			if cox == True:
				new_res.cox.add(choicelist[achoice - 1])
			else:
				new_res.crew.add(choicelist[achoice - 1])
			print("Enter the name that the choice should be updated to.")
			newname = input("Name: ")
			choicelist[achoice - 1].name = newname
			choicelist[achoice - 1].save()
			print("Rower %s added to the crew." % choicelist[achoice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[achoice - 1].name)
			crewtemptest.append((name, choicelist[achoice - 1]))
			return crewtemptest
			
	# the branch for when no search results found ie len == 0
	else:
		new_rower = Rower.objects.create(
			name = rname,
			gender = gender,
			nationality = nationality,
		)
		if cox == True:
			new_res.cox.add(new_rower)
		else:
			new_res.crew.add(new_rower)
		logging.debug("No rower found with name=%s. Added to the DB with gender=%s and nationality=%s.", rname, gender, nationality)
		print("No rower found under name %s. Added to the database" % rname)

	return crewtemptest

# function to search for club members
def clubsearch_bk(new_res, race, cname, composite, nationality, clubtemptest):	
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
# library for the other importers in the directory

from rowing.models import Rower, Club, Result, Time, Alias, ClubAlias
from django.db.models import Q
from django.db.utils import IntegrityError
import logging, datetime, re

# initials re expression
re_form = re.compile('[a-zA-Z][\s.]+[a-zA-Z-\s]+')

def add_time(desc, ts, result, order):
	# assumes time string (ts) is NN:NN.N e.g. 5:51.23
	logging.debug("add_time() called with parameters as follows: desc=%s, ts=%s, result=%s, order=%s", desc, ts, result, order)
	
	# parse the time string
	try:
		# ie find the '.23' in 5:51.23
		micro = int(ts[ts.find(".")+1:])
		# move tenths to hundredths of second - .2 to .20
		if micro < 10:
			micro *= 100000
		# thousandths of a second
		elif micro >= 100:
			micro *= 1000
		else:
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

# merge different rowers
def rowermerge(primary, *others):
	# rowers can be either a Rower object or their name.
	if not isinstance(primary, Rower):
		try:
			primary = Rower.objects.get(name=str(primary))
		except Rower.DoesNotExist:
			print("No primary rower found matching %s" % str(primary))
			logging.warning("No primary rower found matching %s", str(primary))
			return
		except Rower.MultipleObjectsReturned:
			print("Multiple returns for %s. Use the specific rower object instead" % str(primary))
			logging.warning("Multiple returns for %s. Use the specific rower object instead", str(primary))
			return
			
	others2 = []
	for o in others:
		if isinstance(o, Rower):
			others2.append(o)
		else:
			try:
				others2.append(Rower.objects.get(name=str(o)))
			except Rower.DoesNotExist:
				print("No primary rower found matching %s" % str(primary))
				logging.warning("No primary rower found matching %s", str(primary))
				return
			except Rower.MultipleObjectsReturned:
				print("Multiple returns for %s. Use the specific rower object instead" % str(primary))
				logging.warning("Multiple returns for %s. Use the specific rower object instead", str(primary))
				return
	
	for del_rower in others2:
		# this two loop structure used to avoid changing lists as they are iterated on
		chlist = []
		for res in del_rower.result_set.all():
			chlist.append(res)
		
		for ch in chlist:
			ch.crew.add(primary)
			ch.crew.remove(del_rower)
			
		if re_form.match(del_rower.name) is None:
			try:
				Alias.objects.create(
					rower = primary,
					value = del_rower.name,
					temp = False,
				)
			except IntegrityError:
				pass
		
		# WRID merge
		if del_rower.wrid is not None and primary.wrid is None:
			primary.wrid = del_rower.wrid
			
		del_rower.delete()
		primary.save()

# searches for a string and produces a rower
# TODO - fix "U" gender not matching with existing rowers
def rowersearch(res=None, name=None, gender="U", nationality="GBR", club_str=None, cox=False, wrid=None):
	logging.debug("Crewsearch called with parameters as follows:")
	logging.debug("--res: %s", str(res))
	logging.debug("--name: %s", name)
	logging.debug("--nationality: %s", nationality)
	logging.debug("--club_str: %s", club_str)
	logging.debug("--cox: %s", cox)
	logging.debug("--wrid: %s", wrid)

	# exceptions
	if res is None:
		raise Exception("No result specified in search")
	elif not isinstance(res, Result):
		raise Exception("Res is not a Result")
	
	if name is None or name == '':
		raise Exception("No name specified in search")
	
	# get the fullname - lstrip/rstrip removes whitespace
	rname = name.rstrip()
	rname = rname.lstrip()
	
	def cclist(choicelist, noalias=False, temp=False):
		print("#"*20)
		if cox:
			print("Input required for cox %s (of club %s)" % (rname, club_str))
		else:
			print("Input required for rower %s (of club %s)" % (rname, club_str))
		# print all the choices - the ,1 starts enumeration at 1
		for i, item in enumerate(choicelist, 1):
			print("%s): %s - %s - %s" % (i, item.name, item.gender, item.nationality))
			
			# show all associated clubs
			assoc_clubs = set()
			for res1 in item.result_set.all().union(item.cox.all()):
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
				res.cox = new_rower
				res.save()
			else:
				res.crew.add(new_rower)
			logging.debug("New rower added to the DB - name=%s, gender=%s, nationality=%s", rname, gender, nationality)
			print("New rower %s added to the DB and the crew." % rname)
			if noalias == False:
				Alias.objects.create(value = rname, rower = new_rower, temp=temp)
				
			if wrid is not None:
				new_rower.wrid = wrid
				new_rower.save()
		
		# otherwise, add that rower to the crew. 
		# NB choice is -1 because the list enumerated for entry is +1 to reserve the ignore branch as 0.
		elif choice > 0:
			if cox == True:
				res.cox = choicelist[choice - 1]
				res.save()
			else:
				res.crew.add(choicelist[choice - 1])
			print("Rower %s added to the crew." % choicelist[choice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[choice - 1].name)
			if noalias == False:
				Alias.objects.create(value = rname, rower = choicelist[choice - 1], temp=temp)
				
			if wrid is not None:
				choicelist[choice - 1].wrid = wrid
				choicelist[choice - 1].save()
		
		# branch to modify the rower name
		elif choice < 0:
			achoice = abs(choice)
			if cox == True:
				res.cox = choicelist[achoice - 1]
				res.save()
			else:
				res.crew.add(choicelist[achoice - 1])
			print("Enter the name that the choice should be updated to.")
			newname = input("Name: ")
			oname = choicelist[achoice - 1].name
			choicelist[achoice - 1].name = newname
			choicelist[achoice - 1].save()
			print("Rower %s added to the crew." % choicelist[achoice - 1].name)
			logging.debug("Rower %s added to the crew.", choicelist[achoice - 1].name)
			if noalias == False and choicelist[achoice - 1].name != oname:
				if re_form.match(oname) is not None:
					temp = True
				try:
					Alias.objects.create(value = oname, rower = choicelist[achoice - 1], temp=temp)
				except IntegrityError:
					logging.warning("Alias creation blocked for duplication, parameters: value=%s, rower=%s", oname, choicelist[achoice - 1].name)
					
			if wrid is not None:
				choicelist[achoice - 1].wrid = wrid
				choicelist[achoice - 1].save()
	
	# exception to shortcut logic if one exact match found
	if wrid is not None:
		try:
			exactcheck = Rower.objects.get(wrid=wrid)
			
			if cox == True:
				res.cox = exactcheck
				res.save()
			else:
				res.crew.add(exactcheck)
			
			return
	
		except Rower.DoesNotExist:
			logging.info("No rower found for WRID %s", wrid)
	
	logging.debug("Trying exact match for name=%s and gender=%s", rname, gender)
	try:
		exactcheck = Rower.objects.get(name__iexact = rname, gender = gender)
		if cox == True:
			res.cox = exactcheck
			res.save()
		else:
			res.crew.add(exactcheck)
		
		if wrid is not None:
			exactcheck.wrid = wrid
			exactcheck.save()
			logging.info("WRID %s added to rower %s", wrid, exactcheck.name)
		
		logging.debug("Exact match for name=%s and gender=%s proved successful", rname, gender)
		return
	
	except Rower.MultipleObjectsReturned:
		## TODO rewrite this section - think of Tom James and Tom James!
		
		print("!"*20)
		print("Warning: multiple objects returned for an exact name and gender match.")		
		logging.warning("Multiple objects returned for a search of %s", rname)
		
		choicelist = Rower.objects.filter(name = rname, gender = gender)
		cclist(choicelist)
		return
	
	except Rower.DoesNotExist:
		logging.debug("No exact match found")
		
		# search where gender is relaxed
		if gender == "U":
			choicelist = Rower.objects.filter(name = rname)
			if choicelist.count() > 0:
				cclist(choicelist)
				return
		
		logging.debug("Trying exact alias match for name=%s", rname)
		try:
			aliascheck = Alias.objects.get(value = rname)
			if cox == True:
				res.cox = aliascheck.rower
				res.save()
			else:
				res.crew.add(aliascheck.rower)
				
			logging.debug("Exact alias match for name=%s proved successful", rname)
			
			if wrid is not None:
				aliascheck.rower.wrid = wrid
				aliascheck.rower.save()
				logging.info("WRID %s added to rower %s", wrid, aliascheck.rower.name)
			
			return
			
		except Alias.MultipleObjectsReturned:
			logging.debug("Multiple aliases found for %s", rname)
			
			# some mangling to turn the aliases into rowers for cclist
			alist = list(Alias.objects.filter(value = rname))
			choicelist = [x.rower for x in alist]
			cclist(choicelist, noalias=True)
			return
			
		except Alias.DoesNotExist:
			logging.debug("No aliases found for %s", rname)
	
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
	if gender == "U":
		genderc = ["M", "F", "U"]
	else:
		genderc = [gender, "U"]
	choicelist = Rower.objects.filter(Q(name__icontains = rname) | Q(name__icontains = sname), name__startswith = rname[:1], name__iendswith = sname, gender__in = genderc)
	logging.debug("Looser search started, parameters as follows: name=%s, surname=%s, initial=%s, gender=%s", rname, sname, rname[:1], gender)
	
	# exception to shortcut 'A. Johnson' or A Johnson
	if choicelist.count() == 1:
		assoc_clubs = set()
		for res1 in choicelist[0].result_set.all().union(choicelist[0].cox.all()):
			for club1 in res1.clubs.all():
				if club1 is not None:
					assoc_clubs.add(club1)
		if all([
			re_form.match(rname) is not None, # match the re pattern
			not(set(res.clubs.all()).isdisjoint(assoc_clubs)), # ensures the crew's and the rower's clubs have at least one in common
		]):
			if cox == True:
				res.cox = choicelist[0]
				res.save()
			else:
				res.crew.add(choicelist[0])
			logging.debug("%s added to the crew on the initial/club exemption", rname)
			
			if wrid is not None:
				choicelist[0].wrid = wrid
				choicelist[0].save()
			
			return
			
		elif all([
			re_form.match(choicelist[0].name) is not None, # match the re pattern
			not(set(res.clubs.all()).isdisjoint(assoc_clubs)), # ensures the crew's and the rower's clubs have at least one in common
		]):
			oname = choicelist[0].name
			
			# fixes bizarre bug where won't save if you call choicelist[0] direct
			r1 = choicelist[0]
			r1.name = rname
			r1.save()
			
			if cox == True:
				res.cox = choicelist[0]
				res.save()
			else:
				res.crew.add(choicelist[0])
			logging.info("%s was added to the crew on the single result/club exemption, but name was updated to %s", oname, rname)
			
			return
	
	# TODO check this makes any sense!!!
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
		return
	elif choicelist.count() > 0:				
		# prevents permanent aliases being created for simple initials
		if re_form.match(rname) is not None:
			cclist(choicelist, temp=True)
		else:
			cclist(choicelist)
			
	# the branch for when no search results found ie len == 0
	else:
		new_rower = Rower.objects.create(
			name = rname,
			gender = gender,
			nationality = nationality,
		)
		if cox == True:
			res.cox = new_rower
			res.save()
		else:
			res.crew.add(new_rower)
		logging.debug("No rower found with name=%s. Added to the DB with gender=%s and nationality=%s.", rname, gender, nationality)
		print("No rower found under name %s. Added to the database" % rname)

	return
	
# function to search for club members
# TODO - simplify this bloated function (not urgent!)
def clubsearch(res=None, cname=None, country="UK"):	
	logging.debug("Clubsearch called with parameters as follows:")
	logging.debug("--res: %s", str(res))
	logging.debug("--name: %s", cname)
	logging.debug("--country: %s", country)
	
	# exceptions
	if res is None:
		raise Exception("No result specified in search")
	
	if cname is None:
		raise Exception("No name specified in search")
	
	logging.debug("Trying exact match for name %s", cname)
	try:
		exactcheck = Club.objects.get(name = cname)
		res.clubs.add(exactcheck)
		return
	
	except Club.MultipleObjectsReturned:
		print("!"*20)
		print("Error: multiple clubs returned for an exact name match.")
		print("Search database for duplicates of %s." % cname)
		print("!"*20)
		
		logging.warning("Multiple objects returned for a search of %s", cname)
		
		choicelist = Club.objects.filter(name = cname)
		print("Here are the clubs that matched with this name:")
		for i, item in enumerate(choicelist, 1):
				print("%s): %s" % (i, item.name))
		print("#"*20)
		print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB. Choose -1 to add a new club but with manual name entry.")
		while True:
			try:
				choice = int(input("Your choice: "))
			except ValueError:
				print("That wasn't an integer. Try again.")
				continue
			if choice > len(choicelist):
				print("Choice out of range. Try again.")
				continue
			if choice < -1:
				print("Choice out of range. Try again.")
				continue
			else:
				break
		
		if choice == -1:
			choice2 = input("Please type the name of this club: ")
			newclub = Club.objects.create(name=choice2, country=country)
			res.clubs.add(newclub)
			print("%s added to the DB." % choice2)
		
		elif choice == 0:
			newclub = Club.objects.create(name=choice5, country=country)
			res.clubs.add(newclub)
			print("%s added to the DB." % newclub.name)
		
		else:
			res.clubs.add(choicelist[choice-1])
			print("%s added to the result." % choicelist[choice-1].name)
			# create ClubAlias to avoid repetition
			ClubAlias.objects.create(value = cname,	club = choicelist[choice-1])
		
		return
		
	except Club.DoesNotExist:
		logging.debug("No such match found")
		
		# search on ClubAlias
		try:
			aliascheck = ClubAlias.objects.get(value = cname)
			res.clubs.add(aliascheck.club)
			
			return
			
		except ClubAlias.MultipleObjectsReturned:
			logging.debug("Multiple aliases found for %s", cname)
			
			# some mangling to turn the aliases into rowers for cclist
			alist = list(ClubAlias.objects.filter(value = cname))
			choicelist = [x.club for x in alist]
			
			print("Here are the clubs that matched with this name:")
			for i, item in enumerate(choicelist, 1):
					print("%s): %s" % (i, item.name))
			print("#"*20)
			print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB. Choose -1 to add a new club but with manual name entry.")
			while True:
				try:
					choice = int(input("Your choice: "))
				except ValueError:
					print("That wasn't an integer. Try again.")
					continue
				if choice > len(choicelist):
					print("Choice out of range. Try again.")
					continue
				if choice < -1:
					print("Choice out of range. Try again.")
					continue
				else:
					break
			
			if choice == -1:
				choice2 = input("Please type the name of this club: ")
				newclub = Club.objects.create(name=choice2, country=country)
				res.clubs.add(newclub)
				print("%s added to the DB." % choice2)
			
			elif choice == 0:
				newclub = Club.objects.create(name=choice5, country=country)
				res.clubs.add(newclub)
				print("%s added to the DB." % newclub.name)
			
			else:
				res.clubs.add(choicelist[choice-1])
				print("%s added to the result." % choicelist[choice-1].name)
			
			return
			
		except ClubAlias.DoesNotExist:
			logging.debug("No aliases found for %s", cname)
	
	# else search on the basis of the first four letters of the club name
	clubchoice = Club.objects.filter(name__icontains = cname[:4])
	logging.debug("Searching for matches for %s. (%s matches found)", cname[:4], str(clubchoice.count()))
	
	if len(clubchoice) > 0:
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
			newclub = Club.objects.create(name=choice2, country=country)
			res.clubs.add(newclub)
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
						research = False
						while True:
							print("Enter manually (M) or search again (S)?")
							choice6 = input("M/S: ")
							if choice6 == "S":
								research = True
								break
							elif choice6 == "M":
								while True:
									choice4 = input("Please type the name of this club: ")
									if len(choice4) < 2:
										print("Sorry but that's not a valid Club name. Try again.")
										continue
									else:
										newclub = Club.objects.create(name=choice4, country=country)
										res.clubs.add(newclub)
										print("%s added to the DB." % choice4)
										logging.debug("Club %s added to the DB.", choice4)
										break
								break
							else:
								print("Sorry, that wasn't a valid choice.")
						
						if research:
							continue
						else:
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
							newclub = Club.objects.create(name=choice2, country=country)
							res.clubs.add(newclub)
							print("%s added to the DB." % choice2)
							logging.debug("Club %s added to the DB.", newclub.name)
							break
						
						elif choice == 0:
							newclub = Club.objects.create(name=choice5, country=country)
							res.clubs.add(newclub)
							print("%s added to the DB." % newclub.name)
							logging.debug("Club %s added to the DB.", newclub.name)
							break
						
						else:
							res.clubs.add(clubchoice2[choice-1])
							print("%s added to the result." % clubchoice2[choice-1])
							# create ClubAlias to avoid repetition
							ClubAlias.objects.create(value = cname,	club = clubchoice2[choice-1])
							break
		
		
		elif choice == 0:
			newclub = Club.objects.create(name=cname, country=country)
			res.clubs.add(newclub)
			print("%s added to the DB." % newclub.name)
			logging.debug("Club %s added to the DB.", newclub.name)
		
		else:
			res.clubs.add(clubchoice[choice-1])
			print("%s added to the result." % clubchoice[choice-1])
			# create ClubAlias to avoid repetition
			ClubAlias.objects.create(value = cname,	club = clubchoice[choice-1])
		
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
						newclub = Club.objects.create(name=choice4, country=country)
						res.clubs.add(newclub)
						print("%s added to the DB." % choice4)
						break
				break
			elif choice3 == "N":
				if country != "UK" and country != "GBR":
					cname += (", " + country)
				newclub = Club.objects.create(name=cname, country=country)
				res.clubs.add(newclub)
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
							research = False
							while True:
								print("Enter manually (M) or search again (S)?")
								choice6 = input("M/S: ")
								if choice6 == "S":
									research = True
									break
								elif choice6 == "M":
									while True:
										choice4 = input("Please type the name of this club (non-UK country will be appended automatically): ")
										if len(choice4) < 2:
											print("Sorry but that's not a valid Club name. Try again.")
											continue
										else:
											newclub = Club.objects.create(name=choice4, country=country)
											res.clubs.add(newclub)
											print("%s added to the DB." % choice4)
											break
									break
								else:
									print("Sorry, that wasn't a valid choice.")
							
							if research:
								continue
							else:
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
								newclub = Club.objects.create(name=choice2, country=country)
								res.clubs.add(newclub)
								print("%s added to the DB." % choice2)
								break
							
							elif choice == 0:
								newclub = Club.objects.create(name=choice5, country=country)
								res.clubs.add(newclub)
								print("%s added to the DB." % newclub.name)
								break
							
							else:
								res.clubs.add(clubchoice2[choice-1])
								print("%s added to the result." % clubchoice2[choice-1])
								# create ClubAlias to avoid repetition
								ClubAlias.objects.create(value = cname,	club = clubchoice2[choice-1])
								break
				break
			else:
				print("Sorry, that wasn't a valid Y/N/Z. Try again.")
				continue

	return
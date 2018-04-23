# script to import the csv data into sqlite

from rowing.models import Rower, Race, Result, Club
import csv
from django.db.models import Q
#from django.core.exceptions import MultipleObjectsReturned 

wehorr = Race.objects.get(pk=92)

with open('wehorr crews.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	data = (list(reader))
	
for row in data[39:]:
	new_res = Result.objects.create(
		race = wehorr,
		position = row['FPos'],
		flag = row['Flag']
	)
	
	for r in ("r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"):
		# get the fullname - rstrip removes whitespace
		rname = row[r].rstrip()
		
		# exception to shortcut logic if one exact match found
		try:
			exactcheck = Rower.objects.get(name = rname, gender = "W")
			new_res.crew.add(exactcheck)
			continue
		
		except Rower.MultipleObjectsReturned:
			print("!"*20)
			print("Error: multiple objects returned for an exact name and gender match.")
			print("Search database for duplicates of %s." % rname)
			print("!"*20)
			continue
		
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
		choicelist = Rower.objects.filter(Q(name__icontains = rname) | Q(name__icontains = sname), name__startswith = rname[:1], gender = "W")
		
		
		
		if len(choicelist) > 0:
			print("#"*20)
			print("Input required for rower %s" % rname)
			# print all the choices
			for i, item in enumerate(choicelist, 1):
				print("%s): %s - %s - %s" % (i, item.name, item.gender, item.nationality))
			
			# infinte loop to ensure you input correctly
			print("#"*20)
			print("Enter the number of the result to add to the crew. Or choose 0 to ignore this list and add a new entry to the DB.")
			while True:
				try:
					choice = int(input("Your choice: "))
				except ValueError:
					print("That wasn't an integer. Try again.")
					continue
				if choice > len(choicelist):
					print("Choice out of range. Try again.")
					continue
				else:
					break
			
			# the ignore branch
			if choice == 0:
				new_rower = Rower.objects.create(
					name = rname,
					gender = "W",
					nationality = "GBR",
				)
				new_res.crew.add(new_rower)
				print("New rower %s added to the DB and the crew." % rname)
			
			# otherwise, add that rower to the crew. 
			# NB choice is -1 because the list enumerated for entry is +1 to reserve the ignore branch as 0.
			else:
				new_res.crew.add(choicelist[choice-1])
				print("Rower %s added to the crew." % choicelist[choice-1].name)	

		# the branch for when no search results found
		else:
			new_rower = Rower.objects.create(
				name = rname,
				gender = "W",
				nationality = "GBR",
			)
			new_res.crew.add(new_rower)
			print("No rower found under name %s. Added to the database" % rname)
		
	# add the club name
	if row['composite'] == 'No':
		cname = row['club'].rstrip()	
	else:
		cname = row['composite'].rstrip()
	
	# exception to shortcut logic if one exact match found
	try:
		exactcheck = Club.objects.get(name = cname)
		new_res.clubs.add(exactcheck)
		print("Row %s completed." % row['FPos'])
		continue
	
	except Club.MultipleObjectsReturned:
		print("!"*20)
		print("Error: multiple clubs returned for an exact name match.")
		print("Search database for duplicates of %s." % rname)
		print("!"*20)
		continue
	
	except Club.DoesNotExist:
		pass
	
	# else search on the basis of the first three letters of the club name
	clubchoice = Club.objects.filter(name__icontains = cname[:3])
	
	if len(clubchoice) > 0:
		print("#"*20)
		print("Input required for club name %s" % cname)
		print("Here are the clubs that matched with this name:")
		for i, item in enumerate(clubchoice, 1):
				print("%s): %s" % (i, item.name))
				
		print("#"*20)
		print("Enter the number of the club to add. Or choose 0 to ignore this list and add a new entry to the DB.")
		while True:
			try:
				choice = int(input("Your choice: "))
			except ValueError:
				print("That wasn't an integer. Try again.")
				continue
			if choice > len(clubchoice):
				print("Choice out of range. Try again.")
				continue
			else:
				break
		
		if choice == 0:
			newclub = Club.objects.create(name=cname)
			new_res.clubs.add(newclub)
			print("%s added to the DB." % newclub.name)
		
		else:
			new_res.clubs.add(clubchoice[choice-1])
			print("%s added to the result." % clubchoice[choice-1])
		
	else:
		newclub = Club.objects.create(name=cname)
		new_res.clubs.add(newclub)
		print("%s didn't match so it has been added to the DB." % newclub.name)
		
	print("Row %s completed." % row['FPos'])	


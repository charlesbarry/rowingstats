# script to do parse wr names to
# 1) create list of rowers and their unique ids
# 2) fix duplicates accordingly
# this is part 2 - to affect the db

import csv, logging, datetime
from rowing.models import Rower, Race, Result, Club, Competition, Event

# CONFIG
datafile = './data/output1e.csv'
logging.basicConfig(filename='./log/wrnames.log', level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info("####### Start of Log ########")
logging.info("Timestamp -- %s", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S - %A, %d %B %Y"))

# MAIN FUNCTION
counter1 = 0
counter2 = 0
try:
	'''
	
	# open the data
	with open(datafile, 'r', encoding='UTF-8-sig', newline='') as csvfile:
		reader = csv.reader(csvfile)
		data = (list(reader))

	# loop through and add WR IDs
	for row in data:
		try:
			r = Rower.objects.get(name=row[0])
		except Rower.DoesNotExist:
			logging.debug("No match for %s", row[0])
			row[3] = 'yes'
			continue
		except Rower.MultipleObjectsReturned:
			logging.debug("Attempting to run %s generated multiple results. Suggest manual intervention", row[0])
			row[3] = 'yes'
			continue
		else:
			r.wrid = int(row[1])
			r.save()
			
		counter1 += 1

	with open('output1e2.csv','w',newline='') as csvfile2:
		writer = csv.writer(csvfile2)
		for row in data:
			writer.writerow(row)

	print("Completed loop 1")
	input("Press any key to continue: ")
	'''
	
	with open('./data/output1e2.csv', 'r', encoding='UTF-8-sig', newline='') as csvfile:
		reader = csv.reader(csvfile)
		data = (list(reader))
	duplicates = [x for x in data if x[2] == 'Duplicate']

	toskip = set()
	# loop through and merge duplicates
	for d in duplicates:
		if int(d[1]) not in toskip and Rower.objects.filter(wrid=int(d[1])).count() > 1 and d[3] == 'no':
			choices = []
			# doing this convoluted method so I can use pop below
			for r in Rower.objects.filter(wrid=int(d[1])):
				choices.append(r)
			for i, item in enumerate(choices, 1):
				print("%s): %s - %s - %s" % (i, item.name, item.gender, item.nationality))
						
			print("#"*20)
			print("Enter the choice number to select. Make the number negative to modify the name of that rower.")
			while True:
				try:
					choice = int(input("Your choice: "))
				except ValueError:
					print("That wasn't an integer. Try again.")
					continue
				if choice == 0:
					print("Choice out of range. Try again.")
					continue
				if choice > len(choices):
					print("Choice out of range. Try again.")
					continue
				if choice < -len(choices):
					print("Choice out of range. Try again.")
					continue
				else:
					break
			
			# choice is -1 because the enumeration started at 1
			selected_rower = choices.pop(abs(choice) - 1)
			
			if choice < 0:
				print("Enter the correct name")
				newname = str(input("New name: "))
				selected_rower.name = newname
				selected_rower.save()
			
			print("Rower %s selected." % selected_rower.name)
			# for all the ones NOT chosen, convert all their race results to the one that is chosen
			for del_rower in choices:
				chlist = []
				# double loop to avoid a moving target on the result_set
				for res in del_rower.result_set.all():
					chlist.append(res)
				
				for ch in chlist:
					ch.crew.add(selected_rower)
					ch.crew.remove(del_rower)

				try:
					print("Deleting %s." % del_rower.name)
					del_rower.delete()
				except:
					logging.exception("Failed to delete %s", del_rower.name)
					print("Failed to delete %s." % del_rower.name)
		
		else:
			logging.info("Skipping entry %s", str(d))
		counter2 += 1
		
except KeyboardInterrupt:
	print("Exiting due to keyboard interrupt.")
	logging.debug("Exiting main loop at position %s (loop 1) and %s (loop 2)", str(counter1), str(counter2))
		
except Exception:
	logging.exception("Exiting main loop at position %s (loop 1) and %s (loop 2)", str(counter1), str(counter2))
	print("Exception occurred")

else:
	print("All races completed.")	
	logging.info("All races completed. Exiting...")
finally:	
	print("Exiting loop on race %s (Loop #: %s). Shutting down..." % counter2))
	logging.info("####### End of Log ########")	
# custom command to recalculate scores based on data

from django.core.management.base import BaseCommand, CommandError
import datetime
	
class Command(BaseCommand):
	help = 'Test command to see what happens with optional arguments'

	def add_arguments(self, parser):
		parser.add_argument('--date', action='store', help='Starts from YYYY-MM-DD')

	def handle(self, *args, **options):
		if options['date']:
			print(options['date'])
		else:
			print("No date passed")
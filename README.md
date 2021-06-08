# Rowingstats
This repository provides the codebase for the rowingstats project. This includes the main rowingstats app, plus the blog and other experimental projects.

The website is built using the django python web framework, with of course lots of js on top. The main site is hosted on heroku so there are some specific files designed to manage that.

## Installation
1. You'll need python 3 - probably 3.6 or later (currently being developed on 3.8)
2. Clone the repo into a location of your choice
3. If you care about such things, create a virtual environment (venv) of your choice. If you don't, simply run `pip install -r requirements.txt` in the local repo.
4. Set up a .env file in rowingstats/rowingstats (i.e. alongside `settings.py`). This needs to specify as a minimum the SECRET_KEY (a nice long random string). If you don't specify a DATABASE_URL then it will default to a sqlite file database. (NB: rowingstats is designed with specific features of postgresql in mind, so be aware if you don't do this.) Here you can also turn DEBUG and a few security settings on and off - see `settings.py`.
5. In the folder where you've set things up, run `python manage.py migrate` to initialise your database. If you don't do this, things will crash and burn.
6. Then run `python manage.py runserver` and navigate to `localhost:8000`. If all's gone well, that should do it.
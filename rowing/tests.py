from django.test import TestCase
from rowing.models import Rower, Race, Result, Competition, Event, Score, Club, ScoreRanking, Time, Fixture, KnockoutRace, CumlProb, Edition
from django.urls import reverse
from rowing.forms import CompareForm, RankingForm, RowerForm, CrewCompareForm, CompetitionForm

# a helper suite that creates randomly populated objects
from model_bakery import baker

class RowerTest(TestCase):
    #setUpTestData means don't have to have new baker objects in each test
    
    @classmethod    
    def setUpTestData(cls):
        cls.r = baker.make('rowing.Rower')

    def test_rower_creation(self):
        #r = baker.make('rowing.Rower')
        self.assertTrue(isinstance(self.r, Rower))
        self.assertEqual(self.r.__str__(), self.r.name)

    # views
    def test_rower_list(self):
        url = reverse("rower-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_rowers_detail(self):
        url = reverse("rower-detail", args=[str(self.r.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

class CompTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.c = baker.make('rowing.Competition')   

    def test_comp_creation(self):
        self.assertTrue(isinstance(self.c, Competition))
        self.assertEqual(self.c.__str__(), self.c.name)

    # views
    def test_comp_list(self):
        url = reverse("comp-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_comp_detail(self):
        url = reverse("comp-detail", args=[str(self.c.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)          

class EventTest(TestCase):
    def test_event_creation(self):
        c = baker.make('rowing.Event')
        self.assertTrue(isinstance(c, Event))
        self.assertEqual(c.__str__(), (str(c.comp.name) +": "+ c.name))

class RaceTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.c = baker.make('rowing.Race')   
    
    def test_race_creation(self):
        self.assertTrue(isinstance(self.c, Race))
        self.assertEqual(self.c.__str__(), self.c.name)

    # views
    def test_race_list(self):
        url = reverse("race-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_race_detail(self):
        url = reverse("race-detail", args=[str(self.c.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)  

class ClubTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.c = baker.make('rowing.Club')  
    
    def test_club_creation(self):
        self.assertTrue(isinstance(self.c, Club))
        self.assertEqual(self.c.__str__(), self.c.name)

    # views
    def test_club_list(self):
        url = reverse("club-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_club_detail(self):
        url = reverse("club-detail", args=[str(self.c.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200) 

class EditionTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.c = baker.make('rowing.Edition')  
    
    def test_edition_creation(self):
        self.assertTrue(isinstance(self.c, Edition))
        self.assertEqual(self.c.__str__(), self.c.name)

    # views        
    def test_edition_detail(self):
        url = reverse("edition-detail", args=[str(self.c.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

class FixtureTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.c = baker.make('rowing.Fixture')  
    
    def test_fixture_creation(self):
        self.assertTrue(isinstance(self.c, Fixture))
        self.assertEqual(self.c.__str__(),(self.c.event.name + ' - ' + self.c.edition.name))

    # views        
    def test_fixture_detail(self):
        url = reverse("fixture-detail", args=[str(self.c.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)             

# to just check the damn thing works on the most basic level        
class ViewsBasicTest(TestCase):
    def test_index(self):
        url = reverse("index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_about(self):
        url = reverse("about")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)     

    def test_rower_search(self):
        url = reverse("rower-search")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)         

    def test_compare(self):
        url = reverse("compare2")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)    

    def test_crewcompare(self):
        url = reverse("crewcompare")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

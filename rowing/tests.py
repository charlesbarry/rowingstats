from django.test import TestCase
from rowing.models import Rower, Race, Result, Competition, Event, Score, Club, ScoreRanking, Time, Fixture, KnockoutRace, CumlProb
#from django.utils import timezone
from django.urls import reverse
from rowing.forms import CompareForm, RankingForm, RowerForm, CrewCompareForm, CompetitionForm
from model_bakery import baker

class RowerTest(TestCase):
    #def create_rower(self, name="Test Example", gender="U", nationality="GBR"):
    #    return Rower.objects.create(name=name, gender=gender, nationality=nationality)

    def test_rower_creation(self):
        r = baker.make('rowing.Rower')
        self.assertTrue(isinstance(r, Rower))
        self.assertEqual(r.__str__(), r.name)

    # views
    def test_rower_list(self):
        r = baker.make('rowing.Rower')
        url = reverse("rower-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        #self.assertIn(r.name, resp.content)
        
    def test_rowers_detail(self):
        #r = self.create_rower()
        r = baker.make('rowing.Rower')
        url = reverse("rower-detail", args=[str(r.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(r.name, resp.content)

class CompTest(TestCase):
    def test_comp_creation(self):
        c = baker.make('rowing.Competition')
        self.assertTrue(isinstance(c, Competition))
        self.assertEqual(c.__str__(), c.name)

    # views
    def test_comp_list(self):
        url = reverse("comp-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_comp_detail(self):
        r = baker.make('rowing.Competition')
        url = reverse("comp-detail", args=[str(r.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)          

class EventTest(TestCase):
    def test_event_creation(self):
        c = baker.make('rowing.Event')
        self.assertTrue(isinstance(c, Event))
        self.assertEqual(c.__str__(), (str(self.comp.name) +": "+ self.name))

class RaceTest(TestCase):
    def test_race_creation(self):
        c = baker.make('rowing.Race')
        self.assertTrue(isinstance(c, Race))
        self.assertEqual(c.__str__(), c.name)

    # views
    def test_race_list(self):
        url = reverse("race-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_race_detail(self):
        r = baker.make('rowing.Race')
        url = reverse("race-detail", args=[str(r.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)  

class ClubTest(TestCase):
    def test_club_creation(self):
        c = baker.make('rowing.Club')
        self.assertTrue(isinstance(c, Club))
        self.assertEqual(c.__str__(), c.name)

    # views
    def test_club_list(self):
        url = reverse("club-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_club_detail(self):
        r = baker.make('rowing.Club')
        url = reverse("club-detail", args=[str(r.pk)])
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

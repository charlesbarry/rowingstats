from django.test import TestCase
from blog.models import Article
from django.utils import timezone
from model_bakery import baker
from django.urls import reverse

# Create your tests here.
class ArticleTest(TestCase):
    @classmethod    
    def setUpTestData(cls):
        cls.r = baker.make('blog.Article')

    def test_article_creation(self):
        self.assertTrue(isinstance(self.r, Article))
        self.assertEqual(self.r.__str__(), self.r.title)
        
    # views
    def test_article_list(self):
        url = reverse("blog-index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_article_detail(self):
        url = reverse("blog-detail", args=[str(self.r.pk)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
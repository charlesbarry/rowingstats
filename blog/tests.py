from django.test import TestCase
from blog.models import Article
from django.utils import timezone

# Create your tests here.
class ArticleTest(TestCase):
    def create_article(self, title="Test Example", summary="A summary of the test", content="A very long post about <a>something</a>", published=timezone.now(), public=True, views=100):
        return Article.objects.create(title=title, summary=summary, content=content, published=published, public=public, views=views)

    def test_article_creation(self):
        r = self.create_article()
        self.assertTrue(isinstance(r, Article))
        self.assertEqual(r.__str__(), r.title)
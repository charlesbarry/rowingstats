from django.db import models
from django.utils import timezone

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=250)
    summary = models.CharField(max_length=1000)
    content = models.TextField()
    last_updated = models.DateTimeField("Last updated", auto_now=True)
    created = models.DateTimeField("Created on", auto_now_add=True)
    published = models.DateTimeField("Published on", default=timezone.now)
    public = models.BooleanField(default=False, help_text="If set to True (checked) the Article will be published. Leave unchecked for draft posts")
    views = models.PositiveIntegerField(editable=False, default=0)
    
    def __str__(self):
        return self.title
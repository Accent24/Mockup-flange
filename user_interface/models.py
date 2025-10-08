from django.db import models

# Create your models here.
class MainFunction(models.Model):
    name = models.CharField(blank=False, max_length=200)
    view_name = models.CharField(blank=False, max_length=200)

    def __str__(self):
        return self.name


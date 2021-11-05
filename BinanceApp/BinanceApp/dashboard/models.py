from django.db import models

# Create your models here.
class Log(models.Model):
    symbol = models.CharField(max_length=200)
    timestamp = models.DateTimeField('Timestmap')
    volume = models.FloatField('Volume')
    interval = models.CharField(max_length=200)
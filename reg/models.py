from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Person(models.Model):
    user = models.OneToOneField(User)
    identifier=models.BigIntegerField()

    def __unicode__(self):
        return self.identifier

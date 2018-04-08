from django.db import models
from django_mysql.models import JSONField
from django.contrib.auth.models import User


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, unique=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, null=True)
    title = models.CharField(max_length=100, null=True)
    career = JSONField(null=True)
    training = JSONField(null=True)
    cv_ref = models.CharField(max_length=150, null=True)
    # profile summary
    # core skills

    def __str__(self):
        return "%s" % (self.name)


class Recruter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=15, null=True)
    location = models.CharField(max_length=200, null=True)
    summary = models.TextField(null=True)

    def __str__(self):
        return "%s" % (self.name)


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    working_schedule = models.CharField(max_length=20, null=True)
    salary = models.CharField(max_length=20, null=True)
    niv_etude = models.CharField(max_length=10, null=True)
    experience = models.IntegerField(default=0)
    requirements = JSONField(null=True)
    description = models.TextField(null=True)
    recruter = models.ForeignKey(Recruter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.title)

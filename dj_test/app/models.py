from django.db import models
from django_mysql.models import JSONField
from django.contrib.auth.models import User


class Recruiter(models.Model):
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=15, null=True)
    location = models.CharField(max_length=200, null=True)
    summary = models.TextField(null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.name)


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    schedule = models.CharField(max_length=20, null=True)
    salary = models.CharField(max_length=20, null=True)
    degree = models.CharField(max_length=50, null=True)
    experience = models.IntegerField(default=0)

    # Skills:
    programming_languages = models.CharField(max_length=100, null=True, blank=True)
    programming_frameworks = models.CharField(max_length=100, null=True, blank=True)
    technologies = models.CharField(max_length=100, null=True, blank=True)
    languages = models.CharField(max_length=100, null=True, blank=True)

    description = models.TextField(null=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.title)


class Candidate(models.Model):

    # Contact :
    name = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)

    # Skills :
    programming_languages = models.CharField(max_length=200, null=True, blank=True)
    programming_frameworks = models.CharField(max_length=200, null=True, blank=True)
    technologies = models.CharField(max_length=200, null=True, blank=True)
    languages = models.CharField(max_length=200, null=True, blank=True)

    degree = models.CharField(max_length=50, null=True, blank=True)
    experience = models.IntegerField(default=0)
    career = JSONField(null=True, blank=True)
    training = JSONField(null=True, blank=True)

    cv_ref = models.CharField(max_length=150, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "%s" % (self.name)

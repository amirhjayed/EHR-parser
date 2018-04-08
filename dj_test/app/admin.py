from django.contrib import admin

from .models import Recruter, JobOffer, Candidate


# class QuestionAdmin(admin.ModelAdmin):
#     fields = ['pub_date', 'question_text']


admin.site.register(Recruter)
admin.site.register(JobOffer)
admin.site.register(Candidate)
